"""Retrieval practice API — Phase 3.5 (Forgetting §20-46)."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.auth.dependencies import CurrentUser, DbSession
from app.retrieval import service as ret_service

router = APIRouter(prefix="/retrieval", tags=["retrieval"])


class ScheduleBody(BaseModel):
    skill_id: str | None = None  # optional: explicit skill UUID; else most due


class CompleteBody(BaseModel):
    result: str  # success|failure|partial
    confidence: float | None = None
    time_taken_ms: int | None = None


@router.get("/due")
def due(db: DbSession, student: CurrentUser):
    return ret_service.due_queue(db, student.id)


@router.post("/schedule", status_code=status.HTTP_201_CREATED)
def schedule(body: ScheduleBody, db: DbSession, student: CurrentUser):
    try:
        skill_uuid = uuid.UUID(body.skill_id) if body.skill_id else None
        sched = ret_service.schedule_for_student(db, student.id, skill_id=skill_uuid)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
    return {
        "id": str(sched.id),
        "skill_id": str(sched.skill_id),
        "problem_id": str(sched.problem_id) if sched.problem_id else None,
        "ladder_level": sched.ladder_level,
        "scheduled_for": sched.scheduled_for.isoformat(),
        "status": sched.status,
    }


@router.post("/complete/{schedule_id}")
def complete(schedule_id: str, body: CompleteBody, db: DbSession, student: CurrentUser):
    try:
        sched = ret_service.complete_schedule(
            db,
            uuid.UUID(schedule_id),
            student.id,
            result=body.result,
            confidence=body.confidence,
            time_taken_ms=body.time_taken_ms,
        )
    except ValueError as exc:
        msg = str(exc)
        if "not found" in msg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg) from exc
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=msg) from exc
    return {
        "id": str(sched.id),
        "skill_id": str(sched.skill_id),
        "result": sched.result,
        "status": sched.status,
        "completed_at": sched.completed_at.isoformat() if sched.completed_at else None,
    }


@router.get("/history")
def history(db: DbSession, student: CurrentUser, limit: int = 20):
    limit = max(1, min(limit, 50))
    rows = ret_service.history_for_student(db, student.id, limit=limit)
    return [
        {
            "id": str(r.id),
            "skill_id": str(r.skill_id),
            "problem_id": str(r.problem_id) if r.problem_id else None,
            "ladder_level": r.ladder_level,
            "scheduled_for": r.scheduled_for.isoformat(),
            "status": r.status,
            "result": r.result,
            "created_at": r.created_at.isoformat(),
        }
        for r in rows
    ]


@router.get("/pending-count")
def pending_count(db: DbSession, student: CurrentUser):
    return {"pending": ret_service.pending_count(db, student.id)}
