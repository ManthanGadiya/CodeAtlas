"""Retention & forgetting engine — deterministic V1 (docs/Forgetting_And_Retention.md §56).

Design choices (rule-based, §56 Version 1):
  - Forgetting curve: R(t) = exp(-t / S)  (§15, §25)
  - Stability S grows on success, shrinks on failure (§54)
  - Scheduling: next_review = now + S * schedule_factor (§22)
  - Encoding strength factors deferred to later (§8-9) — V1 uses mastery + evidence
  - Personalized forgetting rate λ (Level 4.2) estimated from Mastery(t) history
    via exponential fit on mastery snapshots.

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


def fit_forgetting_rate(time_days: list[float], mastery_values: list[float]) -> float | None:
    """Fit exponential decay mastery(t) = a * exp(-λ * t) + c to history.

    Uses linear regression on log(mastery - c) where c = min(mastery) * 0.9
    to estimate λ (forgetting rate in 1/days). Returns λ in 1/days, or None
    if insufficient data or fit fails.

    V1 assumption: mastery decays exponentially between retrievals.
    This is a V1 estimator — uncalibrated, documented as such.
    """
    if len(time_days) < 3 or len(mastery_values) < 3:
        return None
    if len(time_days) != len(mastery_values):
        return None
    # Need at least 2 days span for meaningful exponential fit
    if max(time_days) - min(time_days) < 2.0:
        return None

    # Filter out invalid points
    valid = [(t, m) for t, m in zip(time_days, mastery_values, strict=False) if m > 0]
    if len(valid) < 3:
        return None

    t_vals, m_vals = zip(*valid, strict=True)  # noqa: B905 - transpose, equal-length by construction

    # Estimate asymptote c as 90% of minimum observed mastery
    c = min(m_vals) * 0.9

    # Linear regression on log(m - c) = log(a) - λ * t
    try:
        y_vals = [math.log(m - c) for m in m_vals]
    except ValueError:
        return None

    # Simple linear regression: y = -λ * t + log(a)
    n = len(t_vals)
    sum_t = sum(t_vals)
    sum_y = sum(y_vals)
    sum_ty = sum(t * y for t, y in zip(t_vals, y_vals, strict=True))
    sum_t2 = sum(t * t for t in t_vals)

    denom = n * sum_t2 - sum_t * sum_t
    if abs(denom) < 1e-9:
        return None

    slope = (n * sum_ty - sum_t * sum_y) / denom  # slope = -λ
    lambda_est = -slope

    # Sanity bounds: λ in [0.001, 2.0] 1/days (half-life 0.35–693 days)
    if lambda_est <= 0.001 or lambda_est > 2.0:
        return None

    return round(lambda_est, 6)


def estimate_forgetting_rate(
    db: Session, student_id: uuid.UUID, skill_id: uuid.UUID, now: datetime | None = None
) -> float | None:
    """Estimate personalized forgetting rate λ from MasterySnapshot history.

    Queries MasterySnapshot for the (student, skill), converts to (days_ago, mastery)
    points, and fits exponential decay. Returns λ in 1/days, or None if
    insufficient history (need ≥3 snapshots spanning ≥2 days).

    Uses MasterySnapshot.new_mastery as the mastery signal (Data_Model §31).
    """
    from app.skills.models import MasterySnapshot

    now = now or datetime.now(UTC)
    cutoff = now - timedelta(days=90)  # Only look at last 90 days

    rows = db.scalars(
        select(MasterySnapshot)
        .where(
            MasterySnapshot.student_id == student_id,
            MasterySnapshot.skill_id == skill_id,
            MasterySnapshot.created_at >= cutoff,  # type: ignore
        )
        .order_by(MasterySnapshot.created_at)  # type: ignore
    ).all()

    if len(rows) < 3:
        return None

    # Convert to (elapsed_days, mastery) pairs — t=0 at earliest snapshot,
    # increasing forward in time so decay appears as decreasing mastery.
    stamped = []
    for row in rows:
        created = row.created_at
        if created.tzinfo is None:
            created = created.replace(tzinfo=UTC)
        stamped.append((created, float(row.new_mastery)))
    stamped.sort(key=lambda p: p[0])
    earliest = stamped[0][0]

    time_days = [(c - earliest).total_seconds() / 86400.0 for c, _ in stamped]
    mastery_vals = [m for _, m in stamped]

    # Need at least 2 days span for meaningful fit
    if time_days[-1] - time_days[0] < 2.0:
        return None

    return fit_forgetting_rate(time_days, mastery_vals)


def get_forgetting_curve(
    db: Session,
    student_id: uuid.UUID,
    skill_id: uuid.UUID,
    now: datetime | None = None,
) -> dict | None:
    """Get personalized forgetting curve for a skill.

    Returns dict with:
      - lambda: forgetting rate λ (1/days)
      - half_life_days: ln(2) / λ
      - curve_points: list of {t_days, retention_probability} for t=0..60
      - stability: current stability S (days)
      - model_version

    Returns None if λ not yet estimated.
    """
    now = now or datetime.now(UTC)
    state = db.get(RetentionState, (student_id, skill_id))
    if state is None or state.forgetting_rate is None:
        return None

    lambda_val = state.forgetting_rate
    half_life = math.log(2) / lambda_val if lambda_val > 0 else None

    # Generate curve points for t = 0 to 60 days
    curve_points = []
    for t in range(0, 61, 5):
        retention = math.exp(-lambda_val * t)
        curve_points.append({"t_days": t, "retention": round(retention, 3)})

    return {
        "lambda": lambda_val,
        "half_life_days": round(half_life, 1) if half_life else None,
        "curve_points": curve_points,
        "stability": round(state.stability, 2),
        "model_version": state.model_version,
    }


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
    # Estimate forgetting rate from Mastery(t) history (Level 4.2)
    # Only re-estimate periodically to avoid noisy updates
    try:
        lambda_est = estimate_forgetting_rate(db, student_id, skill_id, now)
        if lambda_est is not None:
            state.forgetting_rate = lambda_est
            state.forgetting_rate_updated_at = now
    except Exception:  # noqa: BLE001
        pass
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
                "forgetting_rate": state.forgetting_rate,
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
