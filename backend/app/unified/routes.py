"""Unified student state API — Level 4.1 (ROADMAP §32, Data_Model §8).

The single read surface for the learner model's combined intelligence
(Knowledge + Mistakes + Behavior + Retention + Performance + Preferences).
Deterministic aggregation — no LLM in this path (AI Architecture Rule §28).
"""

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select

from app.auth.dependencies import CurrentUser, DbSession
from app.problems.models import Skill
from app.unified.service import (
    build_unified_state,
    get_mastery_history,
    get_overall_history,
)

router = APIRouter(prefix="/learner", tags=["learner"])


@router.get("/unified-state")
def unified_state(db: DbSession, student: CurrentUser) -> dict:
    """Return the unified student state projection for the current student."""
    return build_unified_state(db, student.id)


@router.get("/unified-state/health")
def unified_health() -> dict:
    return {"status": "ok", "module": "unified-state", "version": "v1-unified-rule"}


@router.get("/mastery-history")
def mastery_history(
    db: DbSession,
    student: CurrentUser,
    skill_slug: str = Query(min_length=1, description="Skill slug, e.g. arrays"),
    days: str = Query(default="30", description="Lookback window in days, clamped 1-90"),
) -> dict:
    """Per-skill Mastery(t) — Level 4.1b temporal history (ROADMAP §33).

    Replays append-only MasterySnapshot ordered by event timestamp (§79).
    No new tables; `days` never 422s — clamped via parse_days.
    """
    skill = db.scalar(select(Skill).where(Skill.slug == skill_slug))
    if skill is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Skill not found: {skill_slug}",
        )
    result = get_mastery_history(db, student.id, skill.id, days=days)
    return {"skill_slug": skill_slug, **result}


@router.get("/unified-history")
def unified_history(
    db: DbSession,
    student: CurrentUser,
    days: str = Query(default="30", description="Lookback window in days, clamped 1-90"),
) -> dict:
    """Overall Mastery(t) — mean across skills at each snapshot timestamp."""
    return get_overall_history(db, student.id, days=days)
