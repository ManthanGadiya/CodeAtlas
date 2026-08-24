"""Problem catalog endpoints (read-only in Phase 1.2)."""

from fastapi import APIRouter, HTTPException, status

from app.auth.dependencies import CurrentUser, DbSession
from app.problems import schemas, service

router = APIRouter(prefix="/problems", tags=["problems"])


def _skill_slugs(problem) -> list[str]:
    ordered = sorted(problem.skill_links, key=lambda link: link.role != "primary")
    return [link.skill.slug for link in ordered]


def _to_summary(problem) -> schemas.ProblemSummary:
    return schemas.ProblemSummary(
        slug=problem.slug,
        title=problem.title,
        difficulty=problem.difficulty,
        language=problem.language,
        estimated_minutes=problem.estimated_minutes,
    )


@router.get("", response_model=list[schemas.ProblemSummary])
def list_problems(db: DbSession, student: CurrentUser) -> list[schemas.ProblemSummary]:
    return [_to_summary(problem) for problem in service.list_problems(db)]


@router.get("/{slug}", response_model=schemas.ProblemDetail)
def get_problem(slug: str, db: DbSession, student: CurrentUser) -> schemas.ProblemDetail:
    problem = service.get_problem_by_slug(db, slug)
    if problem is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found")

    visible_tests = [t for t in problem.test_cases if t.visibility == "visible"]
    return schemas.ProblemDetail(
        **_to_summary(problem).model_dump(),
        description=problem.description,
        starter_code=problem.starter_code,
        function_name=problem.function_name,
        skills=_skill_slugs(problem),
        examples=[
            schemas.VisibleTestCase(
                name=t.name,
                input_args=t.input_args,
                expected_output=t.expected_output,
            )
            for t in visible_tests
        ],
    )
