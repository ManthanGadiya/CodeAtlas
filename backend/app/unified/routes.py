"""Unified student state API — Level 4.1 (ROADMAP §32, Data_Model §8).

The single read surface for the learner model's combined intelligence
(Knowledge + Mistakes + Behavior + Retention + Performance + Preferences).
Deterministic aggregation — no LLM in this path (AI Architecture Rule §28).
"""

from fastapi import APIRouter

from app.auth.dependencies import CurrentUser, DbSession
from app.unified.service import build_unified_state

router = APIRouter(prefix="/learner", tags=["learner"])


@router.get("/unified-state")
def unified_state(db: DbSession, student: CurrentUser) -> dict:
    """Return the unified student state projection for the current student."""
    return build_unified_state(db, student.id)


@router.get("/unified-state/health")
def unified_health() -> dict:
    return {"status": "ok", "module": "unified-state", "version": "v1-unified-rule"}
