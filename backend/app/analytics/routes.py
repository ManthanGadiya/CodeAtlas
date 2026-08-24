"""Analytics endpoints."""

from fastapi import APIRouter

from app.analytics import service
from app.auth.dependencies import CurrentUser, DbSession

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary")
def summary(db: DbSession, student: CurrentUser) -> dict:
    """Activity observations for the dashboard (Phase 1.6: not intelligence)."""
    return service.build_summary(db, student.id)
