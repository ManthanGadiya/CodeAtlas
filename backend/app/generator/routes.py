"""Generator API — Phase 3.2 (Problem_Generator §59-64)."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field

from app.auth.dependencies import CurrentUser, DbSession
from app.core.ratelimit import execution_limiter
from app.execution.runner import DockerPythonRunner, get_runner
from app.generator import service as gen_service

Runner = Annotated[DockerPythonRunner, Depends(get_runner)]

router = APIRouter(prefix="/generator", tags=["generator"])


class MutateBody(BaseModel):
    source_slug: str = Field(min_length=1)
    mutation_type: str = Field(
        min_length=1, description="boundary_variant | constraint_tighten | context_shift"
    )


class GenerateBody(BaseModel):
    """Skill-targeted generation (alias for mutate when no source given)."""

    skill_slug: str | None = None
    source_slug: str | None = None
    mutation_type: str = Field(default="boundary_variant")
    difficulty: str | None = None


class ValidateDraftBody(BaseModel):
    title: str
    description: str
    function_name: str
    difficulty: str
    starter_code: str
    tests: list[dict]
    reference_code: str | None = None


def _check_budget(request: Request) -> None:
    ip = request.client.host if request.client else "unknown"
    if not execution_limiter.allow(f"generator:{ip}"):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many generation requests"
        )


@router.post("/mutate", status_code=status.HTTP_201_CREATED)
def mutate(
    body: MutateBody,
    request: Request,
    db: DbSession,
    student: CurrentUser,
    runner: Runner,
):
    _check_budget(request)
    if body.mutation_type not in gen_service.MUTATION_TYPES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"unknown mutation_type {body.mutation_type}",
        )
    try:
        problem = gen_service.mutate_problem(
            db,
            source_slug=body.source_slug,
            mutation_type=body.mutation_type,
            student_id=student.id,
            runner=runner,
        )
    except gen_service.GenerationError as exc:
        msg = str(exc)
        if "source problem not found" in msg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg) from exc
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=msg) from exc
    return {
        "slug": problem.slug,
        "title": problem.title,
        "difficulty": problem.difficulty,
        "fingerprint": problem.fingerprint,
        "quality_score": problem.quality_score,
        "parent_slug": body.source_slug,
    }


@router.post("/generate", status_code=status.HTTP_201_CREATED)
def generate(
    body: GenerateBody,
    request: Request,
    db: DbSession,
    student: CurrentUser,
    runner: Runner,
):
    _check_budget(request)
    source_slug = body.source_slug
    if not source_slug and body.skill_slug:
        from sqlalchemy import select

        from app.problems.models import Problem, ProblemSkill, Skill

        skill = db.scalar(select(Skill).where(Skill.slug == body.skill_slug))
        if not skill:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="skill not found")
        link = db.scalar(
            select(ProblemSkill)
            .where(ProblemSkill.skill_id == skill.id)
            .order_by(ProblemSkill.importance.desc())
        )
        if link:
            src = db.get(Problem, link.problem_id)
            source_slug = src.slug if src else None
        if not source_slug:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="no curated problem for skill"
            )
    if not source_slug:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="source_slug or skill_slug required",
        )
    if body.mutation_type not in gen_service.MUTATION_TYPES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"unknown mutation_type {body.mutation_type}",
        )
    try:
        problem = gen_service.mutate_problem(
            db,
            source_slug=source_slug,
            mutation_type=body.mutation_type,
            student_id=student.id,
            runner=runner,
        )
    except gen_service.GenerationError as exc:
        msg = str(exc)
        if "source problem not found" in msg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg) from exc
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=msg) from exc
    return {
        "slug": problem.slug,
        "title": problem.title,
        "difficulty": problem.difficulty,
        "fingerprint": problem.fingerprint,
        "quality_score": problem.quality_score,
        "parent_slug": source_slug,
    }


@router.post("/validate-draft")
def validate_draft(
    body: ValidateDraftBody,
    request: Request,  # noqa: ARG001
    db: DbSession,
    student: CurrentUser,  # noqa: ARG001
    runner: Runner,
):
    errors = gen_service.validate_draft(
        title=body.title,
        description=body.description,
        function_name=body.function_name,
        difficulty=body.difficulty,
        starter_code=body.starter_code,
        tests=body.tests,
        db=db,
        runner=runner,
        reference_code=body.reference_code,
    )
    q = gen_service.estimate_quality(body.description, body.tests)
    fp = gen_service.fingerprint_for(
        body.title, body.description, body.function_name, body.difficulty
    )
    return {"valid": len(errors) == 0, "errors": errors, "quality_score": q, "fingerprint": fp}


@router.get("/problems")
def list_generated(db: DbSession, student: CurrentUser, limit: int = 20):  # noqa: ARG001
    from sqlalchemy import select

    from app.problems.models import Problem

    limit = max(1, min(limit, 50))
    rows = db.scalars(
        select(Problem)
        .where(Problem.source_type == "generated")
        .order_by(Problem.created_at.desc())
        .limit(limit)
    ).all()
    return [
        {
            "slug": p.slug,
            "title": p.title,
            "difficulty": p.difficulty,
            "fingerprint": p.fingerprint,
            "quality_score": p.quality_score,
            "parent_problem_id": str(p.parent_problem_id) if p.parent_problem_id else None,
        }
        for p in rows
    ]
