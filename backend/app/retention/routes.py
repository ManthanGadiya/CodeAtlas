"""Retention API — Phase 3.6 (docs/Forgeting_And_Retention.md, Data_Model §48-49)."""

from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.auth.dependencies import CurrentUser, DbSession
from app.problems.models import Skill
from app.retention import service as retention_service

router = APIRouter(prefix="/retention", tags=["retention"])


class ReviewBody(BaseModel):
    skill_slug: str = Field(min_length=1)
    success: bool


class RetentionItem(BaseModel):
    skill_id: str
    skill_slug: str
    skill_name: str
    mastery: float
    stability: float
    retrieval_probability: float
    last_successful_retrieval: str | None
    next_recommended_review: str | None
    retrieval_count: int
    due: bool


@router.get("/overview", response_model=list[RetentionItem])
def overview(db: DbSession, student: CurrentUser) -> list[RetentionItem]:
    data = retention_service.overview_for_student(db, student.id)
    return [RetentionItem(**item) for item in data]


@router.post("/review", response_model=RetentionItem)
def record_review(body: ReviewBody, db: DbSession, student: CurrentUser) -> RetentionItem:
    skill = db.scalar(select(Skill).where(Skill.slug == body.skill_slug))
    if skill is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")
    state = retention_service.record_retrieval(
        db, student_id=student.id, skill_id=skill.id, success=body.success
    )
    # Build single-item view matching overview shape
    from app.skills.models import StudentSkillState

    s_state = db.get(StudentSkillState, (student.id, skill.id))
    mastery = round(s_state.mastery, 3) if s_state else 0.0
    now = datetime.now(UTC)
    due = False
    if state.next_recommended_review is not None and state.next_recommended_review <= now:
        due = True
    if state.retrieval_probability < 0.6:
        due = True
    return RetentionItem(
        skill_id=str(skill.id),
        skill_slug=skill.slug,
        skill_name=skill.name,
        mastery=mastery,
        stability=round(state.stability, 2),
        retrieval_probability=round(state.retrieval_probability, 3),
        last_successful_retrieval=(
            state.last_successful_retrieval.isoformat() if state.last_successful_retrieval else None
        ),
        next_recommended_review=(
            state.next_recommended_review.isoformat() if state.next_recommended_review else None
        ),
        retrieval_count=state.retrieval_count,
        due=due,
    )
