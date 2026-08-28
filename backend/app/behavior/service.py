"""Deterministic behavior signals over execution history (ROADMAP Phase 2.5).

V1 rules read only what is already persisted — artifact revision counts
and submit/run outcomes. Every rule is a conservative threshold crossing:
a single event never produces a pattern (docs/Behavior_Model.md §2 core
principle: observed error is not inferred cause). Thresholds and severity
cut-offs are explicit initial assumptions, not validated constants.

Known V1 simplifications, recorded honestly:
- "random editing" is proxied by many distinct revisions while still
  unresolved; distinguishing healthy iterative refinement (§25) needs
  diff-content analysis that arrives later.
- persistence quality ignores time-on-problem entirely (§26).
"""

from datetime import UTC, datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.behavior.models import BehaviorObservation, BehaviorPattern
from app.events.service import record_event
from app.execution.models import CodeArtifact, Execution

MODEL_VERSION = "behavior-rules-v1"

# Controlled vocabulary (subset of docs/Data_Model.md §39 detectable now).
REPEATED_RETRY = "REPEATED_RETRY"
RANDOM_EDITING = "RANDOM_EDITING"
LOW_TESTING = "LOW_TESTING"
PRODUCTIVE_PERSISTENCE = "PRODUCTIVE_PERSISTENCE"

SEVERITY_RANK = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}
PATTERN_CONFIDENCE_BASE = 0.3
PATTERN_CONFIDENCE_GAIN = 0.15

# Rule thresholds (initial assumptions).
RETRY_THRESHOLD = 3  # failed submits since last full pass before the signal fires
RETRY_HIGH_THRESHOLD = 5
RANDOM_EDIT_REVISIONS = 4  # distinct revisions in an unresolved streak
RANDOM_EDIT_HIGH_REVISIONS = 6
LOW_TESTING_SUBMITS = 3  # failing submits with zero Run attempts at all
PERSISTENCE_PRIOR_FAILURES = 2  # failures overcome before PRODUCTIVE_PERSISTENCE fires


def _full_pass(execution: Execution) -> bool:
    return (
        execution.status == "SUCCESS"
        and bool(execution.test_executions)
        and all(te.passed for te in execution.test_executions)
    )


def _streak_stats(
    db: Session, *, student_id: UUID, problem_id: UUID, exclude_execution_id: UUID | None = None
) -> dict:
    """Counts relative to the last full pass on this problem.

    The streak resets when a submit passes everything; everything the
    student did before that belongs to a solved chapter.
    """
    stmt = (
        select(Execution)
        .where(
            Execution.student_id == student_id,
            Execution.problem_id == problem_id,
            Execution.mode == "submit",
        )
        .options(selectinload(Execution.test_executions))
        .order_by(Execution.created_at)
    )
    if exclude_execution_id is not None:
        stmt = stmt.where(Execution.id != exclude_execution_id)
    submits = list(db.scalars(stmt))
    runs = db.scalar(
        select(sa.func.count())
        .select_from(Execution)
        .where(
            Execution.student_id == student_id,
            Execution.problem_id == problem_id,
            Execution.mode == "run",
        )
    )

    last_pass_index = None
    for index, execution in enumerate(submits):
        if _full_pass(execution):
            last_pass_index = index
    streak_submits = submits[last_pass_index + 1 :] if last_pass_index is not None else submits

    solved_at = submits[last_pass_index].created_at if last_pass_index is not None else None
    revisions_since = db.scalar(
        select(sa.func.count())
        .select_from(CodeArtifact)
        .where(
            CodeArtifact.student_id == student_id,
            CodeArtifact.problem_id == problem_id,
            *([CodeArtifact.created_at > solved_at] if solved_at is not None else []),
        )
    )

    return {
        "failed_submits_in_streak": len(streak_submits),
        "revisions_in_streak": revisions_since or 0,
        "runs_ever": runs or 0,
        "total_submits": len(submits),
        # failures overcome before the current submit within this streak
        # (what the productive-persistence rule looks at on a passing submit)
        "prior_failures_in_streak": len(streak_submits),
    }


def observe_execution(
    db: Session,
    *,
    student_id: UUID,
    session_id: UUID | None = None,
    problem,  # Problem
    mode: str,
    outcome,  # RunOutcome
    execution_id: UUID | None = None,
) -> list[BehaviorObservation]:
    """Evaluate all rules for one graded execution; persist any firings.

    Called after persist_execution commits, so counts include the current
    attempt. Commits when observations are written; returns them.
    """
    if mode != "submit":
        return []

    fully_passed = (
        outcome.status == "SUCCESS"
        and bool(outcome.results)
        and all(bool(result.get("passed")) for result in outcome.results)
    )
    # For a passing submit the current execution would otherwise be counted
    # as the "last full pass" itself, erasing the streak that the
    # productive-persistence rule needs to see.
    stats = _streak_stats(
        db,
        student_id=student_id,
        problem_id=problem.id,
        exclude_execution_id=execution_id if fully_passed else None,
    )

    firings: list[tuple[str, str, dict]] = []
    if not fully_passed:
        if stats["failed_submits_in_streak"] >= RETRY_THRESHOLD:
            severity = (
                "HIGH" if stats["failed_submits_in_streak"] >= RETRY_HIGH_THRESHOLD else "MEDIUM"
            )
            firings.append(
                (
                    REPEATED_RETRY,
                    severity,
                    {"failed_submits_in_streak": stats["failed_submits_in_streak"]},
                )
            )
        if stats["revisions_in_streak"] >= RANDOM_EDIT_REVISIONS:
            severity = (
                "HIGH" if stats["revisions_in_streak"] >= RANDOM_EDIT_HIGH_REVISIONS else "MEDIUM"
            )
            firings.append(
                (
                    RANDOM_EDITING,
                    severity,
                    {"revisions_in_streak": stats["revisions_in_streak"]},
                )
            )
        if stats["runs_ever"] == 0 and stats["total_submits"] >= LOW_TESTING_SUBMITS:
            firings.append((LOW_TESTING, "MEDIUM", {"runs_ever": 0}))
    elif stats["prior_failures_in_streak"] >= PERSISTENCE_PRIOR_FAILURES:
        firings.append(
            (
                PRODUCTIVE_PERSISTENCE,
                "LOW",  # positive signal: failures overcome with eventual success
                {"failures_overcome": stats["prior_failures_in_streak"]},
            )
        )

    if not firings:
        return []

    observations: list[BehaviorObservation] = []
    now = datetime.now(UTC)
    for behavior_type, severity, detail in firings:
        observation = BehaviorObservation(
            student_id=student_id,
            session_id=session_id,
            problem_id=problem.id,
            behavior_type=behavior_type,
            severity=severity,
            detail=detail,
            model_version=MODEL_VERSION,
        )
        db.add(observation)
        observations.append(observation)

        record_event(
            db,
            student_id=student_id,
            session_id=session_id,
            event_type="BEHAVIOR_OBSERVED",
            payload={
                "behavior_type": behavior_type,
                "severity": severity,
                "problem_slug": problem.slug,
                **detail,
            },
        )
        _upsert_pattern(
            db, student_id=student_id, behavior_type=behavior_type, severity=severity, now=now
        )

    db.commit()
    return observations


def _upsert_pattern(
    db: Session, *, student_id: UUID, behavior_type: str, severity: str, now: datetime
) -> None:
    pattern = db.get(BehaviorPattern, (student_id, behavior_type))
    if pattern is None:
        pattern = BehaviorPattern(
            student_id=student_id,
            behavior_type=behavior_type,
            frequency=1,
            severity=severity,
            confidence=PATTERN_CONFIDENCE_BASE,
            last_observed_at=now,
        )
        db.add(pattern)
        return
    pattern.frequency += 1
    if SEVERITY_RANK.get(severity, 0) > SEVERITY_RANK.get(pattern.severity, 0):
        pattern.severity = severity
    pattern.confidence = min(
        0.99, PATTERN_CONFIDENCE_BASE + PATTERN_CONFIDENCE_GAIN * pattern.frequency
    )
    pattern.last_observed_at = now
