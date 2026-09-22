"""Evaluation API — Option A hardening (Evaluation_Framework.md §71-72).

Golden-dataset–free V1: evaluates mastery → success calibration from the
student's own history.  No LLM in this path; purely deterministic metrics.
"""

from fastapi import APIRouter

from app.auth.dependencies import CurrentUser, DbSession
from app.evaluation.service import build_evaluation_report

router = APIRouter(prefix="/evaluation", tags=["evaluation"])


@router.get("/report")
def evaluation_report(db: DbSession, student: CurrentUser) -> dict:
    """Calibration + Brier report from the student's submit history."""
    return build_evaluation_report(db, student.id)


@router.get("/health")
def evaluation_health() -> dict:
    return {"status": "ok", "module": "evaluation", "version": "v1-baseline"}
