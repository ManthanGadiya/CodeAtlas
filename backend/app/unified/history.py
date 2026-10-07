"""Temporal helpers — Level 4.1b Mastery(t) (ROADMAP §33, Data_Model §31).

Pure functions so tests pin thresholds without DB (AGENTS.md §37).
No new tables — reuses append-only MasterySnapshot (Data_Model §31, §65).

Trend labels follow Learning_Model §32 six-way scale:
STRONGLY_IMPROVING / IMPROVING / STABLE / DECLINING / STRONGLY_DECLINING / UNKNOWN.
"""

from __future__ import annotations

TREND_STRONGLY_IMPROVING = "STRONGLY_IMPROVING"
TREND_IMPROVING = "IMPROVING"
TREND_STABLE = "STABLE"
TREND_DECLINING = "DECLINING"
TREND_STRONGLY_DECLINING = "STRONGLY_DECLINING"
TREND_UNKNOWN = "UNKNOWN"

DEFAULT_DAYS = 30
MIN_DAYS = 1
MAX_DAYS = 90
MAX_POINTS = 100


def classify_trend(velocity: float, n_points: int) -> str:
    """Map numeric velocity to Learning_Model §32 six-way trend.

    V1 assumption, uncalibrated: cutoffs 0.05/0.02 per-snapshot slope are
    initial guesses, not validated constants. Velocity is per-snapshot, not
    per-day — dense practice inflates trend vs sparse practice. Kept separate
    from build_unified_state's legacy 4-way lowercase scale for backwards
    compat (test_unified.py pins old labels); align the two in 4.2.
    """
    if n_points < 2:
        return TREND_UNKNOWN
    if velocity > 0.05:
        return TREND_STRONGLY_IMPROVING
    if velocity > 0.02:
        return TREND_IMPROVING
    if velocity < -0.05:
        return TREND_STRONGLY_DECLINING
    if velocity < -0.02:
        return TREND_DECLINING
    return TREND_STABLE


def parse_days(raw: str | int | None, default: int = DEFAULT_DAYS) -> int:
    """Parse days query param, clamp to [1, 90]. Never raises."""
    try:
        if raw is None:
            return default
        value = int(raw)  # type: ignore[arg-type]
    except (ValueError, TypeError):
        return default
    if value < MIN_DAYS:
        return MIN_DAYS
    if value > MAX_DAYS:
        return MAX_DAYS
    return value


def to_mastery_points(snapshots: list) -> list[dict]:
    """Snapshot rows (pre-sorted ASC) -> {t, mastery, confidence, reason}."""
    points: list[dict] = []
    for snap in snapshots:
        created = snap.created_at
        # SQLite returns naive, Postgres aware — emit UTC ISO with Z.
        t = created.isoformat() if hasattr(created, "isoformat") else str(created)
        if not t.endswith("Z") and "+" not in t:
            t = f"{t}Z"
        points.append(
            {
                "t": t,
                "mastery": round(float(snap.new_mastery), 3),
                "confidence": (
                    round(float(snap.confidence), 3) if snap.confidence is not None else None
                ),
                "reason": snap.reason,
            }
        )
    return points


def downsample(points: list[dict], max_points: int = MAX_POINTS) -> list[dict]:
    """Evenly stride to cap payload. Always keeps last point."""
    if max_points <= 0 or len(points) <= max_points:
        return points
    if max_points == 1:
        return [points[-1]]
    # Stride to keep first, evenly spaced middles, and last.
    step = (len(points) - 1) / (max_points - 1)
    indices = [round(i * step) for i in range(max_points - 1)]
    indices.append(len(points) - 1)
    # Dedupe while preserving order (rounding can collide on small lists).
    seen: list[int] = []
    for idx in indices:
        if not seen or seen[-1] != idx:
            seen.append(idx)
    return [points[i] for i in seen]


def compute_velocity_from_points(masteries: list[float]) -> float:
    """Slope over last-5 mastery values (float twin of compute_learning_velocity)."""
    if len(masteries) < 2:
        return 0.0
    window = masteries[-5:]
    slope = (window[-1] - window[0]) / max(len(window) - 1, 1)
    return round(max(-1.0, min(1.0, slope)), 4)


def bucket_overall_history(points_by_skill: dict[str, list[dict]]) -> list[dict]:
    """Merge per-skill streams into overall_mastery(t) = mean at each timestamp.

    V1 naive mean — no interpolation. Groups by exact timestamp string.
    Documented assumption, not calibrated cohort mean.
    """
    buckets: dict[str, list[float]] = {}
    for points in points_by_skill.values():
        for pt in points:
            buckets.setdefault(pt["t"], []).append(float(pt["mastery"]))
    merged = [
        {"t": t, "overall_mastery": round(sum(vals) / len(vals), 3)} for t, vals in buckets.items()
    ]
    merged.sort(key=lambda p: p["t"])
    return merged
