"""Idempotent seeding of curated skills and problems.

Upsert semantics: missing problems are inserted; existing problems get
their metadata refreshed and their test cases replaced, so content fixes
propagate when the seed is re-run. Skill links are additive.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.problems.models import Problem, ProblemSkill, Skill, TestCase
from app.problems.seed_data import PROBLEMS, SKILLS


def seed_skills(db: Session) -> None:
    for spec in SKILLS:
        skill = db.scalar(select(Skill).where(Skill.slug == spec["slug"]))
        if skill is None:
            db.add(Skill(slug=spec["slug"], name=spec["name"]))
    db.commit()


def _get_skill(db: Session, slug: str) -> Skill:
    skill = db.scalar(select(Skill).where(Skill.slug == slug))
    if skill is None:
        raise LookupError(f"missing seed skill: {slug}")
    return skill


def seed_problems(db: Session) -> int:
    """Upsert curated problems by slug. Returns number of problems created."""
    seed_skills(db)
    created = 0

    for spec in PROBLEMS:
        problem = db.scalar(select(Problem).where(Problem.slug == spec["slug"]))
        if problem is None:
            problem = Problem(slug=spec["slug"])
            db.add(problem)
            created += 1

        problem.title = spec["title"]
        problem.description = spec["description"]
        problem.difficulty = spec["difficulty"]
        problem.function_name = spec["function_name"]
        problem.estimated_minutes = spec["estimated_minutes"]

        # Replace evaluation data wholesale so fixes always propagate.
        problem.test_cases.clear()
        for order, case in enumerate(spec["test_cases"]):
            problem.test_cases.append(
                TestCase(
                    name=case["name"],
                    input_args=case["input_args"],
                    expected_output=case["expected_output"],
                    visibility=case["visibility"],
                    test_type=case["test_type"],
                    order_index=order,
                )
            )
        db.flush()

        existing_links = {
            link.skill_id: link
            for link in db.scalars(
                select(ProblemSkill).where(ProblemSkill.problem_id == problem.id)
            )
        }
        for skill_slug, role in spec["skills"]:
            skill = _get_skill(db, skill_slug)
            link = existing_links.get(skill.id)
            if link is None:
                db.add(ProblemSkill(problem_id=problem.id, skill_id=skill.id, role=role))
            elif link.role != role:
                link.role = role

    db.commit()
    return created
