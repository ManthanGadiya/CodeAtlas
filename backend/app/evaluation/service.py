"""Evaluation service — wires metrics to CodeAtlas evidence.

Computes mastery-prediction calibration from real student history so the
hardening claim "mastery predicts success" can be measured rather than
asserted (docs/Evaluation_Framework.md §27-29, §46-48).
"""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.difficulty.service import estimate_success, get_or_create_vector
from app.execution.models import Execution
from app.problems.models import Problem


def collect_mastery_predictions(
    db: Session, student_id: uuid.UUID, limit: int = 200
) -> tuple[list[float], list[int]]:
    """Collect (predicted P(success), observed outcome) pairs from history.

    Uses current mastery estimate + difficulty IRT as the prediction and the
    submit's actual SUCCESS/FAIL as outcome.  Limited to the most recent
    `limit` submits.  V1 uses current mastery (not time-travel) — honest
    about hindsight bias and documented as such; future V2 can time-travel
    via MasterySnapshot.
    """
    from app.skills.models import StudentSkillState

    executions = db.scalars(
        select(Execution)
        .where(Execution.student_id == student_id, Execution.mode == "submit")
        .order_by(Execution.created_at.desc())
        .limit(limit)
    ).all()

    if not executions:
        return [], []

    predictions: list[float] = []
    outcomes: list[int] = []

    for execution in executions:
        problem = db.get(Problem, execution.problem_id)
        if problem is None:
            continue
        vec = get_or_create_vector(db, problem)
        # Current mastery for the problem's skills
        mastery_vals: list[float] = []
        for link in problem.skill_links:
            state = db.get(StudentSkillState, (student_id, link.skill_id))
            mastery_vals.append(state.mastery if state else 0.5)
        mastery_at_time = sum(mastery_vals) / len(mastery_vals) if mastery_vals else 0.5
        p = estimate_success(mastery_at_time, vec.overall)
        predictions.append(round(p, 3))
        passed = execution.status == "SUCCESS"
        if passed and execution.test_executions:
            passed = all(t.passed for t in execution.test_executions)
        outcomes.append(1 if passed else 0)

    return predictions, outcomes


def build_evaluation_report(db: Session, student_id: uuid.UUID) -> dict:
    """Build the full evaluation report for GET /api/evaluation/report."""
    from app.evaluation.baselines import baseline_static, compare_brier
    from app.evaluation.metrics import brier_baseline_naive, brier_score, calibration_bins, ece

    predictions, outcomes = collect_mastery_predictions(db, student_id)

    if not predictions:
        return {
            "n": 0,
            "message": "Not enough evidence — submit a few problems first.",
            "brier": None,
            "baseline_brier": None,
            "ece": None,
            "calibration": [],
            "comparison": None,
        }

    brier = round(brier_score(predictions, outcomes), 4)
    baseline_brier = round(brier_baseline_naive(outcomes), 4)
    ece_val = ece(predictions, outcomes)
    bins = calibration_bins(predictions, outcomes)
    # Static 0.5 baseline comparison
    comp = compare_brier(predictions, baseline_static(0.5, len(predictions)), outcomes)

    return {
        "n": len(predictions),
        "brier": brier,
        "baseline_brier": baseline_brier,
        "ece": ece_val,
        "calibration": bins,
        "comparison": comp,
    }
