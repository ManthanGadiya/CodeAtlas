"""Curriculum API — Phase 3.4 (docs/Adaptive_Curriculum.md, Data_Model §52-54)."""

from fastapi import APIRouter
from pydantic import BaseModel

from app.auth.dependencies import CurrentUser, DbSession
from app.curriculum import service as curriculum_service

router = APIRouter(prefix="/curriculum", tags=["curriculum"])


class NextResponse(BaseModel):
    problem_slug: str
    problem_title: str
    difficulty: str
    decision_type: str
    target_skill_slug: str | None
    reason: str
    confidence: float
    alternatives: list[dict]


class DecisionHistoryItem(BaseModel):
    id: str
    problem_slug: str
    decision_type: str
    reason: str
    confidence: float
    created_at: str


@router.get("/next", response_model=NextResponse)
def get_next(db: DbSession, student: CurrentUser) -> NextResponse:
    problem, decision = curriculum_service.recommend_next(db, student.id)
    # Persist the decision for audit and future evaluation (§53-54)
    row = curriculum_service.persist_decision(db, student.id, problem, decision)

    target_slug = None
    if row.target_skill_id is not None:
        from sqlalchemy import select

        from app.problems.models import Skill

        skill = db.scalar(select(Skill).where(Skill.id == row.target_skill_id))
        target_slug = skill.slug if skill else None

    # Build alternatives for transparency (top 3 after selected)
    alts: list[dict] = []
    ranked = decision.get("ranked", [])
    for prob, score, dtype, _, reason, _ in ranked[1:4]:
        alts.append(
            {
                "problem_slug": prob.slug,
                "problem_title": prob.title,
                "score": round(score, 3),
                "decision_type": dtype,
                "reason": reason,
            }
        )

    return NextResponse(
        problem_slug=problem.slug,
        problem_title=problem.title,
        difficulty=problem.difficulty,
        decision_type=row.decision_type,
        target_skill_slug=target_slug,
        reason=row.reason,
        confidence=round(row.confidence, 3),
        alternatives=alts,
    )


@router.get("/decisions", response_model=list[DecisionHistoryItem])
def list_decisions(db: DbSession, student: CurrentUser) -> list[DecisionHistoryItem]:
    from sqlalchemy import select

    from app.curriculum.models import CurriculumDecision
    from app.problems.models import Problem

    rows = db.execute(
        select(CurriculumDecision, Problem)
        .join(Problem, Problem.id == CurriculumDecision.selected_problem_id)
        .where(CurriculumDecision.student_id == student.id)
        .order_by(CurriculumDecision.created_at.desc())
        .limit(20)
    ).all()
    return [
        DecisionHistoryItem(
            id=str(dec.id),
            problem_slug=prob.slug,
            decision_type=dec.decision_type,
            reason=dec.reason,
            confidence=dec.confidence,
            created_at=dec.created_at.isoformat(),
        )
        for dec, prob in rows
    ]
