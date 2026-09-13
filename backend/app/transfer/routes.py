"""Transfer evaluation API — Phase 3.7 (Problem_Generator §49-51)."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.auth.dependencies import CurrentUser, DbSession
from app.execution.runner import DockerPythonRunner, get_runner
from app.transfer import service as xfer_service

Runner = Annotated[DockerPythonRunner, Depends(get_runner)]
router = APIRouter(prefix="/transfer", tags=["transfer"])


class ScheduleBody(BaseModel):
    skill_id: str | None = None  # if omitted, picks most mastery-eligible
    transfer_level: str = "T2"


class CompleteBody(BaseModel):
    result: str  # success|failure|partial
    confidence: float | None = None


@router.get("/due")
def due(db: DbSession, student: CurrentUser):
    return xfer_service.due_for_transfer(db, student.id)


@router.post("/schedule", status_code=status.HTTP_201_CREATED)
def schedule(body: ScheduleBody, db: DbSession, student: CurrentUser, runner: Runner):
    if body.transfer_level not in ("T0", "T1", "T2", "T3", "T4", "T5"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="invalid transfer_level"
        )
    # Resolve skill_id: explicit or first due
    skill_uuid = None
    if body.skill_id:
        try:
            skill_uuid = uuid.UUID(body.skill_id)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="invalid skill_id"
            ) from exc
    else:
        due = xfer_service.due_for_transfer(db, student.id)
        if not due:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="no skill eligible for transfer evaluation",
            )
        skill_uuid = uuid.UUID(due[0]["skill_id"])
    try:
        row = xfer_service.schedule_transfer(
            db, student.id, skill_uuid, transfer_level=body.transfer_level, runner=runner
        )  # type: ignore[arg-type]
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
    return {
        "id": str(row.id),
        "skill_id": str(row.skill_id),
        "source_problem_id": str(row.source_problem_id) if row.source_problem_id else None,
        "transfer_problem_id": str(row.transfer_problem_id),
        "transfer_level": row.transfer_level,
    }


@router.post("/complete/{evaluation_id}")
def complete(evaluation_id: str, body: CompleteBody, db: DbSession, student: CurrentUser):
    try:
        row = xfer_service.complete_transfer(
            db, uuid.UUID(evaluation_id), student.id, result=body.result, confidence=body.confidence
        )
    except ValueError as exc:
        msg = str(exc)
        if "not found" in msg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg) from exc
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=msg) from exc
    return {"id": str(row.id), "result": row.result, "transfer_level": row.transfer_level}


@router.get("/history")
def history(db: DbSession, student: CurrentUser, limit: int = 20):
    limit = max(1, min(limit, 50))
    rows = xfer_service.history_for_student(db, student.id, limit=limit)
    return [
        {
            "id": str(r.id),
            "skill_id": str(r.skill_id),
            "source_problem_id": str(r.source_problem_id) if r.source_problem_id else None,
            "transfer_problem_id": str(r.transfer_problem_id),
            "transfer_level": r.transfer_level,
            "result": r.result,
            "created_at": r.created_at.isoformat(),
            "completed_at": r.completed_at.isoformat() if r.completed_at else None,
        }
        for r in rows
    ]
