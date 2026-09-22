"""Pure evaluation metrics — Option A hardening.

Implements the minimum viable evaluation from docs/Evaluation_Framework.md:
- Brier score (§29): calibration of mastery → success predictions
- Calibration bins (§27-28): predicted vs observed per bucket
- Expected Calibration Error (ECE)
- Learning gain (§7, §87): pre vs post delta

All functions are pure so they can be unit-tested without DB and explained
to a student without leaking model internals (§77-78).
"""

from __future__ import annotations


def brier_score(predictions: list[float], outcomes: list[int]) -> float:
    """Mean squared error between predicted probability and binary outcome.

    Args:
        predictions: P(success) in [0,1] per attempt.
        outcomes: 0 or 1 per attempt, aligned with predictions.

    Returns:
        Brier in [0,1], lower is better. 0 is perfect, 0.25 is random at 0.5.
    """
    if not predictions:
        raise ValueError("predictions must be non-empty")
    if len(predictions) != len(outcomes):
        raise ValueError("predictions and outcomes must be same length")
    for p in predictions:
        if not 0.0 <= p <= 1.0:
            raise ValueError(f"prediction {p} not in [0,1]")
    for o in outcomes:
        if o not in (0, 1):
            raise ValueError(f"outcome {o} must be 0 or 1")
    n = len(predictions)
    return sum((p - o) ** 2 for p, o in zip(predictions, outcomes, strict=True)) / n


def calibration_bins(predictions: list[float], outcomes: list[int], n_bins: int = 10) -> list[dict]:
    """Bucket predictions into n_bins and report per-bucket calibration.

    Each bin: {bin_low, bin_high, count, avg_predicted, avg_observed, gap}.
    Empty bins are omitted so callers can plot only populated buckets.
    """
    if n_bins <= 0:
        raise ValueError("n_bins must be positive")
    if not predictions:
        return []
    bins: list[list[tuple[float, int]]] = [[] for _ in range(n_bins)]
    for p, o in zip(predictions, outcomes, strict=True):
        idx = min(int(p * n_bins), n_bins - 1)
        bins[idx].append((p, o))
    result: list[dict] = []
    for i, bucket in enumerate(bins):
        if not bucket:
            continue
        avg_pred = sum(p for p, _ in bucket) / len(bucket)
        avg_obs = sum(o for _, o in bucket) / len(bucket)
        result.append(
            {
                "bin_low": round(i / n_bins, 3),
                "bin_high": round((i + 1) / n_bins, 3),
                "count": len(bucket),
                "avg_predicted": round(avg_pred, 3),
                "avg_observed": round(avg_obs, 3),
                "gap": round(abs(avg_pred - avg_obs), 3),
            }
        )
    return result


def ece(predictions: list[float], outcomes: list[int], n_bins: int = 10) -> float:
    """Expected Calibration Error — weighted mean gap across bins."""
    bins = calibration_bins(predictions, outcomes, n_bins=n_bins)
    n = len(predictions)
    if n == 0 or not bins:
        return 0.0
    return round(sum(b["gap"] * b["count"] for b in bins) / n, 4)


def learning_gain(pre: float, post: float) -> dict:
    """Simple pre/post gain with normalized variants.

    Returns {absolute, relative, normalized} where normalized rescales by
    headroom (1 - pre) so a student near ceiling is not penalized.
    """
    for v in (pre, post):
        if not 0.0 <= v <= 1.0:
            raise ValueError(f"mastery {v} not in [0,1]")
    absolute = round(post - pre, 4)
    relative = round((post - pre) / pre, 4) if pre > 0 else (absolute if absolute > 0 else 0.0)
    headroom = 1.0 - pre
    normalized = round(absolute / headroom, 4) if headroom > 1e-9 else 0.0
    return {"absolute": absolute, "relative": relative, "normalized": normalized}


def mastery_trend(evidence_masteries: list[float]) -> str:
    """Classify a short mastery trajectory as improving/stable/declining."""
    if len(evidence_masteries) < 2:
        return "unknown"
    # Simple slope over last min(5, n) points
    window = evidence_masteries[-5:]
    slope = (window[-1] - window[0]) / max(len(window) - 1, 1)
    if slope > 0.02:
        return "improving"
    if slope < -0.02:
        return "declining"
    return "stable"


def brier_baseline_naive(outcomes: list[int]) -> float:
    """Brier of a naive predictor that always predicts the base rate."""
    if not outcomes:
        raise ValueError("outcomes must be non-empty")
    base_rate = sum(outcomes) / len(outcomes)
    return brier_score([base_rate] * len(outcomes), outcomes)


def auc_approx(predictions: list[float], outcomes: list[int]) -> float:
    """Approximate AUC via pairwise ranking (Mann-Whitney)."""
    if not predictions:
        raise ValueError("predictions must be non-empty")
    pos = [p for p, o in zip(predictions, outcomes, strict=True) if o == 1]
    neg = [p for p, o in zip(predictions, outcomes, strict=True) if o == 0]
    if not pos or not neg:
        return 0.5  # undefined — return random
    wins = 0
    ties = 0
    for p in pos:
        for n in neg:
            if p > n:
                wins += 1
            elif p == n:
                ties += 1
    total = len(pos) * len(neg)
    return round((wins + 0.5 * ties) / total, 4)
