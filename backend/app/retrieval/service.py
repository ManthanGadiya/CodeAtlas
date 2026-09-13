"""Retrieval practice engine — rule-based V1 (Forgetting §20-44).

Uses retention R(t) and stability S to schedule deliberately:
  pending → completed → next interval = S * factor (adaptive §22)
Ladder ramps recall difficulty as stability grows (§34).
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.retention.service import overview_for_student
from app.retrieval.models import RetrievalSchedule

MODEL_VERSION = "retrieval-rule-v1"

LADDER = ["recognition", "explain", "partial", "recall", "application", "transfer"]
LADDER_EFFORT = {
    "recognition": 0.3,
    "explain": 0.45,
    "partial": 0.6,
    "recall": 0.75,
    "application": 0.85,
    "transfer": 1.0,
}
SCHEDULE_FACTOR = 0.8  # same as retention S*0.8


def _next_ladder(current_stability: float) -> str:
    if current_stability < 2:
        return "recognition"
    if current_stability < 5:
        return "explain"
    if current_stability < 10:
        return "partial"
    if current_stability < 20:
        return "recall"
    if current_stability < 35:
        return "application"
    return "transfer"


def due_queue(db: Session, student_id: uuid.UUID, now: datetime | None = None) -> list[dict]:
    now = now or datetime.now(UTC)
    items = overview_for_student(db, student_id, now=now)
    # Filter to due items (§26 priority = importance * forgetting risk)
    due = [i for i in items if i["due"]]
    # Also include weakest 2 even if not yet due to keep retrieval interleaved (§43)
    if len(due) < 2:
        weak = sorted([i for i in items if not i["due"]], key=lambda x: x["retrieval_probability"])[
            : 2 - len(due)
        ]
        due.extend(weak)
    # Enrich with problem recommendation (first problem that exercises the skill)
    return [_enrich_with_problem(db, d) for d in due]


def _enrich_with_problem(db: Session, item: dict) -> dict:
    from app.problems.models import Problem, ProblemSkill

    skill_id = uuid.UUID(item["skill_id"])
    link = db.scalar(select(ProblemSkill).where(ProblemSkill.skill_id == skill_id).limit(1))
    problem_slug = None
    problem_id = None
    if link:
        prob = db.get(Problem, link.problem_id)
        if prob:
            problem_slug = prob.slug
            problem_id = str(prob.id)
    # Next ladder suggestion based on stability
    ladder = _next_ladder(item.get("stability", 2.5))
    return {
        **item,
        "recommended_problem_slug": problem_slug,
        "recommended_problem_id": problem_id,
        "ladder": ladder,
    }


def schedule_for_student(
    db: Session,
    student_id: uuid.UUID,
    skill_id: uuid.UUID | None = None,
    now: datetime | None = None,
) -> RetrievalSchedule:
    now = now or datetime.now(UTC)
    # If skill not specified, pick most due
    if skill_id is None:
        queue = due_queue(db, student_id, now=now)
        if not queue:
            raise ValueError("no skill needs retrieval right now")
        skill_id = uuid.UUID(queue[0]["skill_id"])
        rec_pid = queue[0].get("recommended_problem_id")
        ladder = queue[0].get("ladder", "recall")
    else:
        # Resolve problem for explicit skill
        from app.problems.models import ProblemSkill

        link = db.scalar(select(ProblemSkill).where(ProblemSkill.skill_id == skill_id).limit(1))
        rec_pid = str(link.problem_id) if link else None
        # Ladder from current stability
        from app.retention.models import RetentionState

        state = db.get(RetentionState, (student_id, skill_id))
        ladder = _next_ladder(state.stability if state else 2.5)

    # Due now; next interval derived from retention stability after completion
    schedule = RetrievalSchedule(
        student_id=student_id,
        skill_id=skill_id,
        problem_id=uuid.UUID(rec_pid) if rec_pid else None,
        ladder_level=ladder,
        scheduled_for=now,
        status="pending",
        model_version=MODEL_VERSION,
    )
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    return schedule


def complete_schedule(
    db: Session,
    schedule_id: uuid.UUID,
    student_id: uuid.UUID,
    result: str,
    confidence: float | None = None,
    time_taken_ms: int | None = None,
    now: datetime | None = None,
) -> RetrievalSchedule:
    now = now or datetime.now(UTC)
    sched = db.get(RetrievalSchedule, schedule_id)
    if not sched or sched.student_id != student_id:
        raise ValueError("schedule not found")
    if sched.status != "pending":
        raise ValueError("schedule already completed")
    if result not in ("success", "failure", "partial"):
        raise ValueError("result must be success|failure|partial")
    sched.result = result
    sched.confidence = confidence
    sched.time_taken_ms = time_taken_ms
    sched.status = "completed"
    sched.completed_at = now

    # Update retention stability: success → *2, failure → *0.5, partial → *0.8
    from app.retention.service import get_or_create_state

    success_flag = result == "success"
    db.commit()
    # Delegate to retention record_retrieval for stability math
    from app.retention.service import record_retrieval

    # For partial, treat as success with smaller factor (custom path)
    if result == "partial":
        state = get_or_create_state(db, student_id, sched.skill_id, now=now)
        old = state.stability
        state.stability = max(0.5, min(60.0, old * 0.8))
        state.retrieval_count += 1
        state.retrieval_probability = 0.65
        state.next_recommended_review = now + timedelta(
            days=max(1.0, state.stability * SCHEDULE_FACTOR)
        )
        db.commit()
        db.refresh(state)
    else:
        record_retrieval(
            db, student_id=student_id, skill_id=sched.skill_id, success=success_flag, now=now
        )

    # Emit event
    try:
        from app.events.service import record_event

        record_event(
            db,
            student_id=student_id,
            event_type="RETRIEVAL_ATTEMPTED",
            payload={
                "schedule_id": str(sched.id),
                "skill_id": str(sched.skill_id),
                "result": result,
                "ladder": sched.ladder_level,
                "confidence": confidence,
            },
        )
    except Exception:
        pass

    # Auto-schedule next retrieval based on new stability
    _auto_next(db, student_id, sched.skill_id, now=now)

    db.refresh(sched)
    return sched


def _auto_next(db: Session, student_id: uuid.UUID, skill_id: uuid.UUID, now: datetime) -> None:
    from app.retention.models import RetentionState

    state = db.get(RetentionState, (student_id, skill_id))
    if not state:
        return
    next_due = state.next_recommended_review
    if not next_due:
        next_due = now + timedelta(days=max(1.0, state.stability * SCHEDULE_FACTOR))
    nxt = RetrievalSchedule(
        student_id=student_id,
        skill_id=skill_id,
        problem_id=None,
        ladder_level=_next_ladder(state.stability),
        scheduled_for=next_due,
        status="pending",
        model_version=MODEL_VERSION,
    )
    db.add(nxt)
    db.commit()


def history_for_student(
    db: Session, student_id: uuid.UUID, limit: int = 20
) -> list[RetrievalSchedule]:
    rows = db.scalars(
        select(RetrievalSchedule)
        .where(RetrievalSchedule.student_id == student_id)
        .order_by(RetrievalSchedule.created_at.desc())
        .limit(limit)
    ).all()
    return rows


def pending_count(db: Session, student_id: uuid.UUID) -> int:
    from sqlalchemy import func

    return (
        db.scalar(
            select(func.count())
            .select_from(RetrievalSchedule)
            .where(
                RetrievalSchedule.student_id == student_id, RetrievalSchedule.status == "pending"
            )
        )
        or 0
    )
