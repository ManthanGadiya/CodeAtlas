"""Curriculum scorer — rule-based V1 (docs/Adaptive_Curriculum.md §55-59).

The scoring is deliberately transparent so a student can ask
“Why did you give me this problem?” and get an evidence-grounded answer
(§75-76).  Every weight is an initial assumption, not a validated constant
— same policy as mastery weights (Evaluation_Framework).
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.curriculum.models import CurriculumDecision, DecisionCandidate
from app.problems.models import Problem, SkillRelationship

MODEL_VERSION = "curriculum-rule-v1"

# Difficulty mapping for “appropriate challenge” (§18-22, §66)
DIFFICULTY_NUMERIC = {"easy": 0.3, "medium": 0.55, "hard": 0.8}
# Decision types (§11)
REINFORCE = "REINFORCE"
REPAIR = "REPAIR"
EXTEND = "EXTEND"
RETRIEVE = "RETRIEVE"
TRANSFER = "TRANSFER"


def _skill_mastery_map(  # noqa: E501
    db: Session, student_id: uuid.UUID
) -> dict[uuid.UUID, tuple[float, float, int]]:
    """Map skill_id → (mastery, confidence, evidence_count)."""
    from app.skills.models import StudentSkillState

    rows = (
        db.execute(select(StudentSkillState).where(StudentSkillState.student_id == student_id))
        .scalars()
        .all()
    )
    return {r.skill_id: (r.mastery, r.confidence, r.evidence_count) for r in rows}


def _retention_map(db: Session, student_id: uuid.UUID) -> dict[uuid.UUID, tuple[float, bool]]:
    """Map skill_id → (retrieval_probability, due). Uses live R(t)."""
    from app.retention.service import overview_for_student

    try:
        items = overview_for_student(db, student_id)
        return {uuid.UUID(i["skill_id"]): (i["retrieval_probability"], i["due"]) for i in items}
    except Exception:  # noqa: BLE001 — retention is additive, never block
        return {}


def _mistake_recurrence_map(db: Session, student_id: uuid.UUID) -> dict[uuid.UUID, int]:
    """Map skill_id → max occurrence_count among its mistake patterns."""
    from app.mistakes.models import MistakePattern

    rows = db.execute(
        select(MistakePattern.skill_id, MistakePattern.occurrence_count).where(
            MistakePattern.student_id == student_id
        )
    ).all()
    # Keep max per skill (a skill may have multiple categories)
    result: dict[uuid.UUID, int] = {}
    for skill_id, count in rows:
        result[skill_id] = max(result.get(skill_id, 0), count)
    return result


def _recent_problem_ids(db: Session, student_id: uuid.UUID, limit: int = 5) -> set[uuid.UUID]:
    from app.execution.models import Execution

    rows = (
        db.execute(
            select(Execution.problem_id)
            .where(Execution.student_id == student_id)
            .order_by(Execution.created_at.desc())
            .limit(limit)
        )
        .scalars()
        .all()
    )
    return set(rows)


def _prerequisite_target(
    db: Session, skill_id: uuid.UUID, mastery_map: dict[uuid.UUID, tuple[float, float, int]]
) -> uuid.UUID | None:
    """If a PREREQUISITE of skill_id is weaker, target the prerequisite (§8, §17)."""
    rows = (
        db.execute(
            select(SkillRelationship).where(
                SkillRelationship.target_skill_id == skill_id,
                SkillRelationship.relationship_type == "PREREQUISITE",
            )
        )
        .scalars()
        .all()
    )
    weakest = None
    weakest_mastery = None
    cur_mastery = mastery_map.get(skill_id, (0.5, 0.0, 0))[0]
    for rel in rows:
        m = mastery_map.get(rel.source_skill_id)
        if m is None:
            # No evidence for prerequisite → treat as weak via cold-start (§62-63)
            return rel.source_skill_id
        mastery = m[0]
        if mastery < cur_mastery and (weakest_mastery is None or mastery < weakest_mastery):
            weakest = rel.source_skill_id
            weakest_mastery = mastery
    return weakest


def _score_problem(
    db: Session,
    problem: Problem,
    mastery_map: dict[uuid.UUID, tuple[float, float, int]],
    retention_map: dict[uuid.UUID, tuple[float, bool]],
    recurrence_map: dict[uuid.UUID, int],
    recent_ids: set[uuid.UUID],
) -> tuple[float, str, uuid.UUID | None, str, float]:
    """Score one candidate problem. Returns (score, decision_type, target_skill_id, reason)."""
    # Aggregate across the problem's skills (primary weighted higher)
    best_skill: uuid.UUID | None = None
    best_need = 0.0
    best_reason = ""
    best_type = REINFORCE
    total_relevance = 0.0

    for link in problem.skill_links:
        sid = link.skill_id
        mastery, confidence, evidence = mastery_map.get(sid, (0.5, 0.0, 0))
        retention_prob, due = retention_map.get(sid, (0.8, False))
        recurrence = recurrence_map.get(sid, 0)

        # Learning need: (1 - mastery) weighted by confidence + recurrence bonus
        need = (1.0 - mastery) * (0.5 + confidence * 0.5)
        if recurrence >= 2:
            need += 0.25
        if recurrence >= 3:
            need += 0.15
        # Retention value: due skills get a strong bump (§25, §44-45)
        retention_bonus = 0.4 if due else 0.0
        if retention_prob < 0.5:
            retention_bonus += 0.2
        need += retention_bonus

        # Appropriate difficulty: best when problem difficulty ≈ mastery
        prob_diff = DIFFICULTY_NUMERIC.get(problem.difficulty, 0.5)
        diff_fit = 1.0 - abs(prob_diff - mastery)  # 1 = perfect match

        # Decision type for this skill (§11)
        if recurrence >= 2 and mastery < 0.6:
            dtype = REPAIR
        elif due and mastery > 0.4:
            dtype = RETRIEVE
        elif mastery > 0.75 and not due:
            dtype = EXTEND
        elif mastery < 0.4:
            dtype = REPAIR if recurrence >= 1 else REINFORCE
        else:
            dtype = REINFORCE

        # Weight by role (Data_Model §28): primary ×1.0, supporting ×0.5
        role_w = 1.0 if link.role == "primary" else 0.5
        skill_score = (need * 0.6 + diff_fit * 0.25 + retention_bonus * 0.15) * role_w

        if skill_score > best_need or best_skill is None:
            best_need = skill_score
            best_skill = sid
            best_type = dtype
            if due:
                best_reason = f"retention due (R={retention_prob:.2f})"
            elif recurrence >= 2:
                best_reason = f"recurring mistakes ×{recurrence} on this skill"
            elif mastery < 0.4:
                best_reason = f"low mastery {mastery:.2f}"
            else:
                best_reason = f"skill gap {1 - mastery:.2f}"

        total_relevance += skill_score

    # Cold-start: problem with no skill links still gets a neutral score
    if best_skill is None:
        total_relevance = 0.1
        best_reason = "cold-start exploration"
        best_type = REINFORCE

    # Repetition penalty (§65): recent problems get docked
    if problem.id in recent_ids:
        total_relevance -= 0.35

    # Confidence of the recommendation: higher when the gap is large
    confidence = min(0.95, max(0.45, 0.5 + best_need * 0.3))

    # Prerequisite pivot (§8): if the best skill depends on a weaker one, retarget
    if best_skill is not None:
        prereq = _prerequisite_target(db, best_skill, mastery_map)
        if prereq is not None:
            best_skill = prereq
            best_reason = f"prerequisite of {best_reason}"
            best_type = REPAIR

    return (  # noqa: E501
        total_relevance,
        best_type,
        best_skill,
        f"{best_reason} (score {total_relevance:.2f})",
        confidence,
    )


def recommend_next(
    db: Session, student_id: uuid.UUID, now: datetime | None = None
) -> tuple[Problem, dict]:
    """Pick the next problem for the student. Pure scoring + audit.

    Returns (selected_problem, decision_dict) where decision_dict contains
    target_skill_id, decision_type, reason, confidence, and ranked
    candidates for persistence.
    """
    now = now or datetime.now(UTC)
    problems = (
        db.execute(
            select(Problem).options(
                selectinload(Problem.skill_links),
                selectinload(Problem.test_cases),
            )
        )
        .scalars()
        .all()
    )
    if not problems:
        from fastapi import HTTPException, status

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No problems available")

    mastery_map = _skill_mastery_map(db, student_id)
    retention_map = _retention_map(db, student_id)
    recurrence_map = _mistake_recurrence_map(db, student_id)
    recent_ids = _recent_problem_ids(db, student_id)

    # Cold-start: no evidence yet → recommend easiest unseen problem
    if not mastery_map and not recurrence_map:
        easiest = sorted(problems, key=lambda p: DIFFICULTY_NUMERIC.get(p.difficulty, 0.5))
        for p in easiest:
            if p.id not in recent_ids:
                selected = p
                break
        else:
            selected = easiest[0]
        # Build ranked for transparency (§54) — selected first, others by difficulty
        ranked_cold: list[  # noqa: E501
            tuple[Problem, float, str, uuid.UUID | None, str, float]
        ] = []
        for p in problems:
            score = (  # noqa: E501
                1.0
                if p.id == selected.id
                else 0.5 - DIFFICULTY_NUMERIC.get(p.difficulty, 0.5) * 0.1
            )
            ranked_cold.append(
                (
                    p,
                    score,
                    REINFORCE,
                    selected.skill_links[0].skill_id if selected.skill_links else None,
                    "cold-start: easiest unseen problem",
                    0.55,
                )
            )
        ranked_cold.sort(key=lambda x: x[1], reverse=True)
        return selected, {
            "target_skill_id": selected.skill_links[0].skill_id if selected.skill_links else None,
            "decision_type": REINFORCE,
            "reason": "cold-start: easiest unseen problem",
            "confidence": 0.55,
            "candidates": [(p.id, s) for p, s, *_ in ranked_cold],
            "ranked": ranked_cold,
        }

    ranked: list[tuple[Problem, float, str, uuid.UUID | None, str, float]] = []
    for prob in problems:
        score, dtype, sid, reason, conf = _score_problem(
            db, prob, mastery_map, retention_map, recurrence_map, recent_ids
        )
        ranked.append((prob, score, dtype, sid, reason, conf))
    ranked.sort(key=lambda x: x[1], reverse=True)

    top_prob, top_score, top_dtype, top_sid, top_reason, top_conf = ranked[0]

    candidates = [(p.id, s) for p, s, *_ in ranked]
    return top_prob, {
        "target_skill_id": top_sid,
        "decision_type": top_dtype,
        "reason": top_reason,
        "confidence": top_conf,
        "candidates": candidates,
        "ranked": ranked,
    }


def persist_decision(
    db: Session, student_id: uuid.UUID, problem: Problem, decision: dict
) -> CurriculumDecision:
    row = CurriculumDecision(
        student_id=student_id,
        selected_problem_id=problem.id,
        target_skill_id=decision["target_skill_id"],
        decision_type=decision["decision_type"],
        reason=decision["reason"],
        confidence=decision["confidence"],
        model_version=MODEL_VERSION,
    )
    db.add(row)
    db.flush()
    # Store ranked candidates for explainability (§54)
    for pid, score in decision.get("candidates", []):
        # Skip the selected problem itself from alternatives? Keep it for completeness.
        cand = DecisionCandidate(
            decision_id=row.id,
            candidate_problem_id=pid,
            score=round(score, 3),
            expected_learning_gain=round(max(0.0, score), 3),
            expected_success=None,
            retention_value=None,
        )
        db.add(cand)
    # Emit event for evaluation (§53)
    try:
        from app.events.service import record_event

        record_event(
            db,
            student_id=student_id,
            event_type="CURRICULUM_DECISION",
            payload={
                "decision_id": str(row.id),
                "problem_slug": problem.slug,
                "decision_type": row.decision_type,
                "target_skill_id": str(row.target_skill_id) if row.target_skill_id else None,
                "reason": row.reason,
                "confidence": row.confidence,
            },
        )
    except Exception:  # noqa: BLE001
        pass
    db.commit()
    db.refresh(row)
    return row
