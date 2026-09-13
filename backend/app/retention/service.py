"""Retention & forgetting engine — deterministic V1 (docs/Forgeting_And_Retention.md §56).

Design choices (rule-based, §56 Version 1):
  - Forgetting curve: R(t) = exp(-t / S)  (§15, §25)
  - Stability S grows on success, shrinks on failure (§54)
  - Scheduling: next_review = now + S * schedule_factor (§22)
  - Encoding strength factors deferred to later (§8-9) — V1 uses mastery + evidence

The engine is pure where possible so tests can pin the math without DB.
"""

from __future__ import annotations

import math
import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.retention.models import RetentionState
from app.skills.models import StudentSkillState

MODEL_VERSION = "retention-rule-v1"

# Initial stability mirrors §54: a fresh skill lasts ~2.5 days before hitting
# 1/e retention.  Small enough to force early retrieval, large enough to avoid
# thrashing the curriculum with hourly reviews.
INITIAL_STABILITY = 2.5  # days
MIN_STABILITY = 0.5
MAX_STABILITY = 60.0  # cap at two months — beyond that the skill is Robust
# Success multiplies stability; failure halves it ( §54: 2→5→12, failure 12→6 )
SUCCESS_FACTOR = 2.0
FAILURE_FACTOR = 0.5
# Next review is scheduled at S * factor so the student is asked slightly
# before retention would fall below ~0.6 (exp(-0.8) ≈ 0.45, exp(-1) ≈ 0.37).
# 1.0 means review when R≈0.37; 0.8 pushes it earlier.
SCHEDULE_FACTOR = 0.8


def compute_retention(stability: float, days_since: float) -> float:
    """R(t) = exp(-t / S), clamped to [0,1]. Pure function."""
    if stability <= 0:
        return 0.0
    if days_since <= 0:
        return 1.0
    return max(0.0, min(1.0, math.exp(-days_since / stability)))


def _ensure_aware(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt


def days_since(last: datetime | None, now: datetime) -> float | None:
    """Days between last retrieval and now, or None if never practiced."""
    if last is None:
        return None
    last = _ensure_aware(last)
    now = _ensure_aware(now)
    delta = now - last
    return delta.total_seconds() / 86400.0


def _schedule_next(stability: float, now: datetime) -> datetime:
    interval_days = max(1.0, stability * SCHEDULE_FACTOR)
    return now + timedelta(days=interval_days)


def get_or_create_state(
    db: Session, student_id: uuid.UUID, skill_id: uuid.UUID, now: datetime | None = None
) -> RetentionState:
    now = now or datetime.now(UTC)
    state = db.get(RetentionState, (student_id, skill_id))
    if state is None:
        state = RetentionState(
            student_id=student_id,
            skill_id=skill_id,
            stability=INITIAL_STABILITY,
            retrieval_probability=1.0,
            last_successful_retrieval=None,
            next_recommended_review=now + timedelta(days=INITIAL_STABILITY * SCHEDULE_FACTOR),
            retrieval_count=0,
            successful_retrievals=0,
            model_version=MODEL_VERSION,
        )
        db.add(state)
        db.flush()
    return state


def refresh_retention(
    db: Session,
    student_id: uuid.UUID,
    skill_id: uuid.UUID,
    now: datetime | None = None,
) -> RetentionState:
    """Recompute R(t) for one skill based on elapsed time.

    Called on read paths so dashboards show live decay without a cron job.
    Updates `retrieval_probability` and mirrors it onto
    `StudentSkillState.retention` for the learner summary (the single
    source the frontend already consumes).
    """
    now = now or datetime.now(UTC)
    state = get_or_create_state(db, student_id, skill_id, now=now)
    # Prefer the skill's last_practiced_at over last_successful_retrieval
    # if the former is more recent — any practice is a learning event (§7).
    skill_state = db.get(StudentSkillState, (student_id, skill_id))
    last = state.last_successful_retrieval
    if skill_state and skill_state.last_practiced_at:
        cand = skill_state.last_practiced_at
        if last is None or _ensure_aware(cand) > _ensure_aware(last):
            last = cand
    ds = days_since(last, now)
    if ds is None:
        state.retrieval_probability = 1.0
    else:
        state.retrieval_probability = compute_retention(state.stability, ds)
    # Mirror onto the mastery table for GET /api/analytics/learner
    if skill_state is not None:
        skill_state.retention = state.retrieval_probability
    db.commit()
    return state


def record_retrieval(
    db: Session,
    *,
    student_id: uuid.UUID,
    skill_id: uuid.UUID,
    success: bool,
    now: datetime | None = None,
) -> RetentionState:
    """Update stability after a retrieval attempt ( §54 ).

    Success → stability *= SUCCESS_FACTOR (capped), next review pushed out.
    Failure → stability *= FAILURE_FACTOR (floored), next review pulled in.
    Also updates StudentSkillState.retention to the post-retrieval probability
    (1.0 on success, decayed value on failure) so the learner summary flips
    immediately.
    """
    now = now or datetime.now(UTC)
    state = get_or_create_state(db, student_id, skill_id, now=now)
    state.retrieval_count += 1
    if success:
        state.successful_retrievals += 1
        state.stability = min(MAX_STABILITY, state.stability * SUCCESS_FACTOR)
        state.last_successful_retrieval = now
        state.retrieval_probability = 1.0
        state.next_recommended_review = _schedule_next(state.stability, now)
    else:
        state.stability = max(MIN_STABILITY, state.stability * FAILURE_FACTOR)
        # Failed retrieval drops confidence immediately — even if the last
        # success was moments ago, the student demonstrated they cannot
        # retrieve right now.  Force probability below the 0.6 due threshold
        # (§31) and make the skill due immediately for curriculum.
        state.retrieval_probability = 0.45
        state.next_recommended_review = now  # due now — retry today
    state.model_version = MODEL_VERSION
    # Mirror
    skill_state = db.get(StudentSkillState, (student_id, skill_id))
    if skill_state is not None:
        skill_state.retention = state.retrieval_probability
    # Emit learning event for analytics (§53) — best-effort, never block
    try:
        from app.events.service import record_event

        record_event(
            db,
            student_id=student_id,
            event_type="RETRIEVAL_ATTEMPTED",
            payload={
                "skill_id": str(skill_id),
                "success": success,
                "stability": round(state.stability, 2),
                "retrieval_probability": round(state.retrieval_probability, 3),
            },
        )
    except Exception:  # noqa: BLE001
        pass
    db.commit()
    return state


def overview_for_student(  # noqa: E501
    db: Session, student_id: uuid.UUID, now: datetime | None = None
) -> list[dict]:
    """Per-skill retention snapshot for the dashboard / curriculum.

    Refreshes every skill the student has ever touched so R(t) is live.
    Skills are returned weakest-retention-first so the curriculum can pick
    the most at-risk ones (Adaptive_Curriculum §17 hierarchy).
    """
    now = now or datetime.now(UTC)
    from app.problems.models import Skill

    states = db.execute(
        select(StudentSkillState, Skill)
        .join(Skill, Skill.id == StudentSkillState.skill_id)
        .where(StudentSkillState.student_id == student_id)
    ).all()
    result: list[dict] = []
    for skill_state, skill in states:
        r_state = refresh_retention(db, student_id, skill.id, now=now)
        due = False
        if r_state.next_recommended_review is not None:
            nxt = _ensure_aware(r_state.next_recommended_review)
            if nxt <= _ensure_aware(now):
                due = True
        # Also due if retention has fallen below 0.6 (exp(-0.5) ≈ 0.6)
        if r_state.retrieval_probability < 0.6:
            due = True
        result.append(
            {
                "skill_id": str(skill.id),
                "skill_slug": skill.slug,
                "skill_name": skill.name,
                "mastery": round(skill_state.mastery, 3),
                "stability": round(r_state.stability, 2),
                "retrieval_probability": round(r_state.retrieval_probability, 3),
                "last_successful_retrieval": (
                    r_state.last_successful_retrieval.isoformat()
                    if r_state.last_successful_retrieval
                    else None
                ),
                "next_recommended_review": (
                    r_state.next_recommended_review.isoformat()
                    if r_state.next_recommended_review
                    else None
                ),
                "retrieval_count": r_state.retrieval_count,
                "due": due,
            }
        )
    # Weakest retention first; never-practiced last
    result.sort(
        key=lambda r: (  # noqa: E501
            r["retrieval_probability"] if r["retrieval_probability"] is not None else 1.5  # noqa: E501
        )
    )
    return result
