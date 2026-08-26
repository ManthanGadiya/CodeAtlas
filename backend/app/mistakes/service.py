"""Deterministic mistake detection over graded submissions (ROADMAP Phase 2.2).

Detection-first slice of docs/Mistake_Taxonomy.md §50: only signals a
compiler/runtime/test-runner already produced — no LLM in this path. The
classifier returns at most one primary category per submission; multi-label
refinement arrives with AST analysis and AI-assisted layers.

Severity/confidence values are explicit initial assumptions, not validated
constants (same policy as the mastery weights).
"""

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.events.service import record_event
from app.execution.runner import RunOutcome
from app.mistakes.models import Mistake, MistakeCategory, MistakePattern
from app.mistakes.taxonomy import TAXONOMY_V1, category_id
from app.problems.models import Problem

# Deterministically detectable statuses: (code, severity, confidence).
# Confidence reflects how directly the observed signal implies the label;
# timeouts stay modest because an infinite loop looks identical to a
# genuinely too-slow algorithm.
CLASSIFIER_RULES = {
    "COMPILE_ERROR": ("M01", "LOW", 0.95),
    "RUNTIME_ERROR": ("M03", "MEDIUM", 0.85),
    "TIMEOUT": ("M07", "MEDIUM", 0.65),
    "MEMORY_LIMIT": ("M07", "MEDIUM", 0.65),
}
EDGE_CASE_RULE = ("M10", "MEDIUM", 0.7)  # visible pass + hidden fail: generalisation gap
LOGIC_ERROR_RULE = ("M04", "MEDIUM", 0.5)  # ambiguous catch-all (taxonomy §2 core principle)
PATTERN_CONFIDENCE_BASE = 0.3
PATTERN_CONFIDENCE_GAIN = 0.15


@dataclass(frozen=True)
class ClassifiedMistake:
    category_code: str
    severity: str
    confidence: float
    evidence_note: str


def seed_categories(db: Session) -> None:
    """Idempotently ensure every taxonomy row exists.

    Normal environments get the categories from migration 0008; this exists
    so create_all-based test databases can match production state.
    """
    existing = set(db.scalars(select(MistakeCategory.code)).all())
    for code, name in TAXONOMY_V1:
        if code not in existing:
            db.add(MistakeCategory(id=category_id(code), code=code, name=name))
    db.commit()


def classify_outcome(
    *,
    status: str,
    visible_passed: int,
    visible_total: int,
    hidden_failed: int,
) -> ClassifiedMistake | None:
    """Pure mapping from execution signals to one primary mistake category."""
    if status in CLASSIFIER_RULES:
        code, severity, confidence = CLASSIFIER_RULES[status]
        return ClassifiedMistake(code, severity, confidence, f"submit ended in {status}")

    if status != "SUCCESS":
        return None  # e.g. SYSTEM_ERROR is infrastructure, not student evidence

    if visible_total > 0 and visible_passed == visible_total and hidden_failed > 0:
        code, severity, confidence = EDGE_CASE_RULE
        return ClassifiedMistake(
            code,
            severity,
            confidence,
            f"all {visible_total} visible cases passed but {hidden_failed} hidden case(s) failed",
        )
    if hidden_failed > 0 or visible_passed < visible_total:
        code, severity, confidence = LOGIC_ERROR_RULE
        return ClassifiedMistake(code, severity, confidence, "visible cases failing")

    return None


def observe_execution(
    db: Session,
    *,
    student_id: UUID,
    problem: Problem,
    mode: str,
    outcome: RunOutcome,
    executed_cases: list,
    execution_id: UUID | None = None,
    code_artifact_id: UUID | None = None,
) -> Mistake | None:
    """Detect, persist, announce, and pattern-track one submission's mistakes.

    Call after persist_execution has committed so the execution row exists.
    Run-mode attempts are exploratory practice — observed but not classified
    in V1. A fully passing submit resolves the problem's earlier open
    mistakes instead of recording anything new (taxonomy §45-46 lifecycle).
    Commits when a mistake is recorded or resolved; returns the mistake.
    """
    if mode != "submit":
        return None

    results_by_name = {result["name"]: result for result in outcome.results}
    visible_passed = visible_total = hidden_failed = 0
    for case in executed_cases:
        result = results_by_name.get(case.name)
        passed = bool(result.get("passed")) if result is not None else False
        if case.visibility == "visible":
            visible_total += 1
            visible_passed += int(passed)
        elif not passed:
            hidden_failed += 1

    classified = classify_outcome(
        status=outcome.status,
        visible_passed=visible_passed,
        visible_total=visible_total,
        hidden_failed=hidden_failed,
    )
    if classified is not None:
        return _record_mistake(
            db,
            student_id=student_id,
            problem=problem,
            classified=classified,
            execution_id=execution_id,
            code_artifact_id=code_artifact_id,
        )

    fully_passed = (
        outcome.status == "SUCCESS"
        and bool(executed_cases)
        and all(bool(results_by_name.get(case.name, {}).get("passed")) for case in executed_cases)
    )
    if fully_passed:
        _resolve_open_mistakes(db, student_id=student_id, problem_id=problem.id)
    return None


def _record_mistake(
    db: Session,
    *,
    student_id: UUID,
    problem: Problem,
    classified: ClassifiedMistake,
    execution_id: UUID | None,
    code_artifact_id: UUID | None,
) -> Mistake:
    category = db.scalar(
        select(MistakeCategory).where(MistakeCategory.code == classified.category_code)
    )
    mistake = Mistake(
        student_id=student_id,
        problem_id=problem.id,
        execution_id=execution_id,
        code_artifact_id=code_artifact_id,
        category_id=category.id,
        severity=classified.severity,
        confidence=classified.confidence,
        evidence_note=classified.evidence_note,
    )
    db.add(mistake)
    db.flush()  # assign mistake.id before referencing it in the event payload

    record_event(
        db,
        student_id=student_id,
        event_type="MISTAKE_DETECTED",
        payload={
            "mistake_id": str(mistake.id),
            "problem_slug": problem.slug,
            "category_code": classified.category_code,
            "severity": classified.severity,
            "confidence": classified.confidence,
        },
    )

    _update_patterns(db, student_id=student_id, problem=problem, category_id=category.id)
    db.commit()
    return mistake


def _resolve_open_mistakes(db: Session, *, student_id: UUID, problem_id: UUID) -> int:
    """A full pass closes earlier unresolved mistakes on the same problem."""
    mistakes = db.scalars(
        select(Mistake).where(
            Mistake.student_id == student_id,
            Mistake.problem_id == problem_id,
            Mistake.resolution_status == "UNRESOLVED",
        )
    ).all()
    for mistake in mistakes:
        mistake.resolution_status = "RESOLVED"
    db.commit()
    return len(mistakes)


def _update_patterns(db: Session, *, student_id: UUID, problem: Problem, category_id: UUID) -> None:
    """Upsert recurrence counters for every skill linked to the problem.

    Patterns are skill-keyed precisely so the same category recurring on
    different problems aggregates into one signal (taxonomy §38).
    """
    now = datetime.now(UTC)
    for link in problem.skill_links:
        pattern = db.get(MistakePattern, (student_id, category_id, link.skill_id))
        if pattern is None:
            pattern = MistakePattern(
                student_id=student_id,
                category_id=category_id,
                skill_id=link.skill_id,
                occurrence_count=1,
                first_seen_at=now,
                last_seen_at=now,
                confidence=PATTERN_CONFIDENCE_BASE,
            )
            db.add(pattern)
        else:
            pattern.occurrence_count += 1
            pattern.last_seen_at = now
            pattern.confidence = min(
                0.99,
                PATTERN_CONFIDENCE_BASE + PATTERN_CONFIDENCE_GAIN * (pattern.occurrence_count - 1),
            )
