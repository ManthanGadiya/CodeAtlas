"""Simple baselines for evaluation (docs/Evaluation_Framework.md §61, AGENTS.md §61).

Complexity does not prove superiority — every CodeAtlas decision mechanic
must be compared to a trivial alternative.  These baselines are deliberately
dumb so that beating them is meaningful and losing to them is instructive.
"""

from __future__ import annotations

import random
from collections.abc import Sequence


def baseline_random(n: int, seed: int = 42, low: float = 0.0, high: float = 1.0) -> list[float]:
    """Return n uniform random predictions in [low, high]."""
    rng = random.Random(seed)
    return [rng.uniform(low, high) for _ in range(n)]


def baseline_static(value: float, n: int) -> list[float]:
    """Return n copies of a static prediction (e.g. base-rate or 0.5)."""
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"value {value} not in [0,1]")
    return [value] * n


def baseline_majority(outcomes: Sequence[int]) -> list[int]:
    """Predict the majority class for every outcome (accuracy baseline)."""
    if not outcomes:
        raise ValueError("outcomes must be non-empty")
    majority = 1 if sum(outcomes) / len(outcomes) >= 0.5 else 0
    return [majority] * len(outcomes)


def compare_brier(
    model_preds: list[float], baseline_preds: list[float], outcomes: list[int]
) -> dict:
    """Compare model Brier vs baseline Brier."""
    from app.evaluation.metrics import brier_score

    model = brier_score(model_preds, outcomes)
    baseline = brier_score(baseline_preds, outcomes)
    # Positive delta means model is better (lower Brier)
    delta = round(baseline - model, 4)
    improvement_pct = round(delta / baseline * 100, 1) if baseline > 0 else 0.0
    return {
        "model_brier": round(model, 4),
        "baseline_brier": round(baseline, 4),
        "delta": delta,
        "improvement_pct": improvement_pct,
        "model_better": delta > 0,
    }
