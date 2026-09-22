"""Evaluation package — Option A hardening (Evaluation_Framework.md).

Provides the first measurable baseline and calibration harness for
CodeAtlas learning claims (Phase 4.10 starter, §27-29, §71-72).
"""

from app.evaluation.baselines import baseline_random, baseline_static
from app.evaluation.metrics import brier_score, calibration_bins, ece

__all__ = ["brier_score", "calibration_bins", "ece", "baseline_random", "baseline_static"]
