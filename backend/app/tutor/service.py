"""Tutoring engine — deterministic-first intervention selection (docs/Tutoring_Engine.md).

Phase 3.1 implements the tutoring loop:
  Student → Attempt → Observe (mistake/behavior/skill) → Diagnose → Hint → Observe Again

Decision matrix is rule-based (DESIGN §34, Adaptive_Curriculum §55):
  - Minimal effective help (§9)
  - Escalation only when prior hint did not lead to progress (§8, §53)
  - Provider abstraction via app.ai.gateway — LLM output is untrusted (§29)

Every hint is persisted as a TutorInteraction and emits a HINT_REQUESTED
/ HINT_SHOWN learning event so future analytics can measure intervention
effectiveness (Tutoring_Engine.md §48, Evaluation_Framework.md).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.gateway import HintRequest, get_gateway, hash_context
from app.problems.models import Problem
from app.tutor.models import TutorInteraction

# Hint ladder 0..7 inclusive (ROADMAP §22, Tutoring_Engine.md §7)
MAX_HINT_LEVEL = 7
MIN_HINT_LEVEL = 0

# Intervention labels (Tutoring_Engine.md §5, §22, §68 decision matrix)
INTERVENTION_SOCRATIC = "SOCRATIC_QUESTION"
INTERVENTION_HINT = "HINT"
INTERVENTION_EXPLANATION = "EXPLANATION"
INTERVENTION_DEBUG = "DEBUGGING_GUIDANCE"
INTERVENTION_CONCEPT = "CONCEPT_REMINDER"


@dataclass(frozen=True)
class TutorDecision:
    hint_level: int
    intervention: str
    skill_hint: str | None
    reason: str


def _clamp_level(level: int | None, *, fallback: int = 1) -> int:
    if level is None:
        return fallback
    return max(MIN_HINT_LEVEL, min(MAX_HINT_LEVEL, level))


def select_intervention(
    *,
    mistake_code: str | None,
    skill_mastery: float | None,
    skill_confidence: float | None,
    behavior_severity: str | None,
    prior_hints_for_problem: int,
    requested_level: int | None,
) -> TutorDecision:
    """Rule-based selector — cheapest correct intervention first.

    Priority hierarchy (Tutoring_Engine.md §68 + Adaptive_Curriculum §17):
      1. Explicit caller request wins if within bounds (student pressed "need more help").
      2. Otherwise escalation = prior_hints + 1 (capped), so repeated requests
         naturally walk the ladder instead of trapping the student (docs §53).
      3. Intervention label chosen by mistake/signal, not by LLM.
    """
    # 1) Caller explicitly asked for a level — honour it.
    if requested_level is not None:
        level = _clamp_level(requested_level)
        intervention = _intervention_for_level(level, mistake_code)
        reason = f"explicit level {level} requested"
        return TutorDecision(level, intervention, None, reason)

    # 2) Escalation ladder: each prior hint pushes the next hint one step up.
    escalated = _clamp_level(prior_hints_for_problem + 1, fallback=1)
    # Low mastery + low confidence → stay Socratic before giving away the answer
    if skill_mastery is not None and skill_confidence is not None:
        if skill_mastery < 0.4 and skill_confidence < 0.5:
            # Unknown/weak state — diagnose before prescribing (§46)
            intervention = INTERVENTION_SOCRATIC
            return TutorDecision(  # noqa: E501
                escalated, intervention, None, "low mastery + low confidence → diagnose first"
            )

    # Behavior-aware nudge: random editing → debugging guidance
    if behavior_severity in ("HIGH", "CRITICAL"):
        return TutorDecision(  # noqa: E501
            escalated, INTERVENTION_DEBUG, None, "high-severity behavior → debugging guidance"
        )

    # Mistake-aware mapping (Mistake_Taxonomy.md §43 table)
    intervention = _intervention_for_mistake(mistake_code, escalated)
    skill_hint = _skill_hint_for_mistake(mistake_code)
    return TutorDecision(
        escalated,
        intervention,
        skill_hint,
        f"mistake {mistake_code or 'UNKNOWN'} at level {escalated}",
    )


def _intervention_for_mistake(code: str | None, level: int) -> str:
    if code in ("M01",):
        return INTERVENTION_HINT if level <= 2 else INTERVENTION_EXPLANATION
    if code in ("M03",):
        return INTERVENTION_DEBUG if level <= 3 else INTERVENTION_EXPLANATION
    if code in ("M04",):
        return INTERVENTION_SOCRATIC if level <= 2 else INTERVENTION_HINT
    if code in ("M07",):
        return INTERVENTION_CONCEPT if level <= 2 else INTERVENTION_HINT
    if code in ("M10",):
        return INTERVENTION_DEBUG if level <= 2 else INTERVENTION_HINT
    # Generic fallback uses the level ladder directly
    return _intervention_for_level(level, code)


def _intervention_for_level(level: int, _code: str | None) -> str:
    if level == 0:
        return INTERVENTION_SOCRATIC  # observe silently is handled by not calling the tutor
    if level <= 2:
        return INTERVENTION_SOCRATIC
    if level <= 4:
        return INTERVENTION_HINT
    if level <= 5:
        return INTERVENTION_EXPLANATION
    return INTERVENTION_CONCEPT


def _skill_hint_for_mistake(code: str | None) -> str | None:
    mapping = {
        "M01": "syntax",
        "M03": "runtime error handling",
        "M04": "logic",
        "M07": "complexity",
        "M10": "edge cases",
    }
    return mapping.get(code or "")


def _count_prior_hints(db: Session, student_id: uuid.UUID, problem_id: uuid.UUID) -> int:
    return (
        db.execute(
            select(TutorInteraction).where(
                TutorInteraction.student_id == student_id,
                TutorInteraction.problem_id == problem_id,
            )
        )
        .scalars()
        .all()
    ).__len__()


def _recent_mistake_for_problem(db: Session, student_id: uuid.UUID, problem_id: uuid.UUID):
    """Return the most recent UNRESOLVED mistake for this problem, if any."""
    from app.mistakes.models import Mistake, MistakeCategory

    row = db.execute(
        select(Mistake, MistakeCategory)
        .join(MistakeCategory, MistakeCategory.id == Mistake.category_id)
        .where(
            Mistake.student_id == student_id,
            Mistake.problem_id == problem_id,
            Mistake.resolution_status == "UNRESOLVED",
        )
        .order_by(Mistake.detected_at.desc())
        .limit(1)
    ).first()
    if row is None:
        return None, None
    mistake, category = row
    return mistake, category


def _skill_context(db: Session, student_id: uuid.UUID, problem: Problem):
    """Pick the weakest linked skill for this problem as the tutor's focus."""
    from app.skills.models import StudentSkillState

    if not problem.skill_links:
        return None, None
    # Prefer the skill with lowest mastery among the problem's links
    best = None
    best_state = None
    for link in problem.skill_links:
        state = db.get(StudentSkillState, (student_id, link.skill_id))
        if state is None:
            continue
        if best_state is None or state.mastery < best_state.mastery:
            best = link.skill
            best_state = state
    if best is None and problem.skill_links:
        # No state yet → use the first linked skill
        best = problem.skill_links[0].skill
    return best, best_state


def _behavior_severity(db: Session, student_id: uuid.UUID) -> str | None:
    from app.behavior.models import BehaviorPattern

    row = (
        db.execute(
            select(BehaviorPattern)
            .where(BehaviorPattern.student_id == student_id)
            .order_by(BehaviorPattern.last_observed_at.desc())
            .limit(1)
        )
        .scalars()
        .first()
    )
    return row.severity if row else None


def request_hint(
    db: Session,
    *,
    student_id: uuid.UUID,
    session_id: uuid.UUID | None,
    problem: Problem,
    student_code: str | None = None,
    requested_level: int | None = None,
) -> TutorInteraction:
    """Generate, persist, and return one tutor hint.

    Steps (System_Architecture.md §23 event flow):
      1. Observe current diagnosis (mistake + skill + behavior).
      2. Select intervention (rule-based).
      3. Build AI context and generate hint (via gateway, validated).
      4. Persist TutorInteraction + emit HINT_REQUESTED/HINT_SHOWN events.
    """
    prior_count = _count_prior_hints(db, student_id, problem.id)
    mistake, category = _recent_mistake_for_problem(db, student_id, problem.id)
    skill, skill_state = _skill_context(db, student_id, problem)
    behavior_severity = _behavior_severity(db, student_id)

    # Validate requested level before selection
    if requested_level is not None and not (MIN_HINT_LEVEL <= requested_level <= MAX_HINT_LEVEL):
        raise ValueError(f"hint_level must be between {MIN_HINT_LEVEL} and {MAX_HINT_LEVEL}")

    decision = select_intervention(
        mistake_code=category.code if category else None,
        skill_mastery=skill_state.mastery if skill_state else None,
        skill_confidence=skill_state.confidence if skill_state else None,
        behavior_severity=behavior_severity,
        prior_hints_for_problem=prior_count,
        requested_level=requested_level,
    )

    # If level is 0, the tutor stays silent (DESIGN.md §34) — still record it
    # so the escalation ladder advances honestly.
    gateway = get_gateway()
    hint_req = HintRequest(
        problem_title=problem.title,
        problem_slug=problem.slug,
        problem_statement=problem.description or "",
        student_code=student_code,
        mistake_code=category.code if category else None,
        mistake_name=category.name if category else None,
        hint_level=decision.hint_level,
        intervention=decision.intervention,
        skill_hint=skill.name if skill else decision.skill_hint,
    )

    if decision.hint_level == 0:
        content = (
            "Keep exploring — the tutor is observing silently. Ask for a hint when you want one."
        )
        provider = "system"
        model = "silence-v1"
        latency_ms = 0
        is_fallback = True
        ctx_hash = hash_context(hint_req)
    else:
        ctx_hash = hash_context(hint_req)
        resp = gateway.generate(hint_req)
        # Validation: LLM output is untrusted (docs/AI_And_ML_Strategy §76)
        content = (resp.content or "").strip()
        if not content:
            raise ValueError("Tutor provider returned empty hint")
        if len(content) > 4000:
            content = content[:4000]
        provider = resp.provider
        model = resp.model
        latency_ms = resp.latency_ms
        is_fallback = resp.is_fallback

    # Persist interaction (append-only)
    interaction = TutorInteraction(
        student_id=student_id,
        session_id=session_id,
        problem_id=problem.id,
        interaction_type=decision.intervention,
        hint_level=decision.hint_level,
        intervention=decision.intervention,
        model_provider=provider,
        model_name=model,
        model_version="v1",
        prompt_context_hash=ctx_hash,
        response=content,
        latency_ms=latency_ms,
    )
    db.add(interaction)

    # Emit learning events for analytics (Tutoring_Engine.md §48)
    from app.events.service import record_event

    # HINT_REQUESTED always, HINT_SHOWN when content was actually delivered
    record_event(
        db,
        student_id=student_id,
        session_id=session_id,
        event_type="HINT_REQUESTED",
        payload={
            "problem_slug": problem.slug,
            "hint_level": decision.hint_level,
            "intervention": decision.intervention,
            "mistake_code": category.code if category else None,
            "reason": decision.reason,
            "provider": provider,
            "is_fallback": is_fallback,
        },
    )
    if decision.hint_level > 0:
        record_event(
            db,
            student_id=student_id,
            session_id=session_id,
            event_type="HINT_SHOWN",
            payload={
                "problem_slug": problem.slug,
                "hint_level": decision.hint_level,
                "intervention": decision.intervention,
                "prompt_hash": ctx_hash,
                "provider": provider,
            },
        )
    db.commit()
    db.refresh(interaction)
    return interaction
