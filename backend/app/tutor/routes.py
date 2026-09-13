"""Tutoring engine API — Phase 3.1 (docs/Tutoring_Engine.md §18, PRD FR-013/014)."""

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.auth.dependencies import CurrentUser, DbSession
from app.core.ratelimit import execution_limiter
from app.problems import service as problem_service
from app.sessions.service import get_or_create_open_session
from app.tutor import service as tutor_service
from app.tutor.models import TutorInteraction

router = APIRouter(prefix="/tutor", tags=["tutor"])


class HintRequestBody(BaseModel):
    problem_slug: str = Field(min_length=1, description="Problem to get a hint for")
    code: str | None = Field(default=None, description="Current student code (optional context)")
    hint_level: int | None = Field(
        default=None, ge=0, le=7, description="Explicit ladder level 0-7; omit to auto-escalate"
    )


class HintResponseBody(BaseModel):
    interaction_id: str
    problem_slug: str
    hint_level: int
    intervention: str
    content: str
    provider: str
    is_fallback: bool


class TutorHistoryItem(BaseModel):
    id: str
    problem_slug: str | None
    hint_level: int
    intervention: str
    provider: str
    response: str
    created_at: str


def _hint_budget(request: Request) -> None:
    client_ip = request.client.host if request.client else "unknown"
    if not execution_limiter.allow(f"tutor:{client_ip}"):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many hint requests. Pause and think before asking again.",
        )


@router.post("/hint", response_model=HintResponseBody)
def request_hint(
    payload: HintRequestBody,
    request: Request,
    db: DbSession,
    student: CurrentUser,
) -> HintResponseBody:
    _hint_budget(request)
    problem = problem_service.get_problem_by_slug(db, payload.problem_slug)
    if problem is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found")

    session = get_or_create_open_session(db, student_id=student.id)

    try:
        interaction = tutor_service.request_hint(
            db,
            student_id=student.id,
            session_id=session.id,
            problem=problem,
            student_code=payload.code,
            requested_level=payload.hint_level,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc

    return HintResponseBody(
        interaction_id=str(interaction.id),
        problem_slug=problem.slug,
        hint_level=interaction.hint_level,
        intervention=interaction.intervention,
        content=interaction.response,
        provider=interaction.model_provider,
        is_fallback=interaction.model_provider in ("dummy", "system"),
    )


@router.get("/history", response_model=list[TutorHistoryItem])
def get_history(
    db: DbSession,
    student: CurrentUser,
    problem_slug: str | None = None,
    limit: int = 20,
) -> list[TutorHistoryItem]:
    limit = max(1, min(limit, 50))
    query = (
        select(TutorInteraction)
        .where(TutorInteraction.student_id == student.id)
        .order_by(TutorInteraction.created_at.desc())
    )
    if problem_slug:
        problem = problem_service.get_problem_by_slug(db, problem_slug)
        if problem is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found")
        query = query.where(TutorInteraction.problem_id == problem.id)
    rows = db.execute(query.limit(limit)).scalars().all()
    return [
        TutorHistoryItem(
            id=str(r.id),
            problem_slug=problem_slug if problem_slug else None,
            hint_level=r.hint_level,
            intervention=r.intervention,
            provider=r.model_provider,
            response=r.response,
            created_at=r.created_at.isoformat(),
        )
        for r in rows
    ]
