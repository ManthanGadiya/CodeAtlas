"""Problem catalog queries."""

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.problems.models import Problem, ProblemSkill


def get_problem_by_slug(db: Session, slug: str) -> Problem | None:
    return db.scalar(
        select(Problem)
        .where(Problem.slug == slug)
        .options(
            selectinload(Problem.skill_links).selectinload(ProblemSkill.skill),
            selectinload(Problem.test_cases),
        )
    )


def list_problems(db: Session) -> list[Problem]:
    return list(
        db.scalars(
            select(Problem)
            .order_by(Problem.difficulty, Problem.title)
            .options(selectinload(Problem.skill_links).selectinload(ProblemSkill.skill))
        )
    )
