"""Difficulty API — Phase 3.3 (Problem_Generator §14-18)."""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.auth.dependencies import CurrentUser, DbSession
from app.difficulty import service as diff_service
from app.problems import service as problem_service

router = APIRouter(prefix="/difficulty", tags=["difficulty"])


class EstimateResponse(BaseModel):
    slug: str
    overall: float
    vector: dict[str, float]
    confidence: float
    model_version: str
    student_mastery: float
    p_success: float
    student_specific_difficulty: float
    zone: str


@router.get("/overview")
def overview(db: DbSession, student: CurrentUser):  # noqa: ARG001
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    from app.problems.models import Problem

    problems = db.scalars(select(Problem).options(selectinload(Problem.skill_links))).all()
    result = []
    for p in problems:
        vec = diff_service.get_or_create_vector(db, p)
        result.append(
            {
                "slug": p.slug,
                "title": p.title,
                "difficulty": p.difficulty,
                "overall": vec.overall,
                "vector": {
                    "conceptual": vec.conceptual,
                    "implementation": vec.implementation,
                    "reasoning": vec.reasoning,
                    "debugging": vec.debugging,
                    "constraints": vec.constraints,
                    "transfer": vec.transfer,
                },
                "confidence": vec.confidence,
            }
        )
    return result


@router.get("/estimate/{slug}", response_model=EstimateResponse)
def estimate(slug: str, db: DbSession, student: CurrentUser):
    problem = problem_service.get_problem_by_slug(db, slug)
    if not problem:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found")
    return diff_service.estimate_for_student(db, student.id, problem)


@router.get("/recommend")
def recommend(db: DbSession, student: CurrentUser):
    return diff_service.recommend_difficulty_target(db, student.id)


@router.post("/calibrate/{slug}")
def calibrate(
    slug: str, db: DbSession, student: CurrentUser, success_rate: float = 0.7, n: int = 10
):  # noqa: ARG001
    problem = problem_service.get_problem_by_slug(db, slug)
    if not problem:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found")
    if not 0 <= success_rate <= 1:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="success_rate 0-1"
        )
    vec = diff_service.calibrate_from_signals(db, problem, success_rate=success_rate, n=n)
    return {"slug": slug, "overall": vec.overall, "confidence": vec.confidence}
