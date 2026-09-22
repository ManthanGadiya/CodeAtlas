"""Unified student state builder — Level 4.1 (ROADMAP §32, Data_Model §8).

V1 is a deterministic aggregation of the six evidence halves CodeAtlas
already tracks.  No new ML, no extra tables — just a single read
projection that replaces the scattered `learnerSummary + retentionOverview +
analyticsSummary` dance the dashboard previously did.

The shape mirrors Data_Model §8 + ROADMAP §32:

    StudentState {
        knowledge, misconceptions, behavior, retention,
        preferences, confidence, learning_velocity
    }

plus top-level `overall_mastery` / `independence_score` / `retention_score`
that get mirrored to `student_learning_states` for persistence (§64 DERIVED).

All helpers are pure where possible so tests can pin the math without DB.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.users.models import StudentLearningState, StudentPreferences

MODEL_VERSION = "unified-rule-v1"


def compute_overall_mastery(masteries: list[float]) -> float:
    """Average mastery across skills, 0.3 prior when empty (matches mastery-rule-v1)."""
    if not masteries:
        return 0.3
    return round(sum(masteries) / len(masteries), 3)


def compute_confidence(confidences: list[float]) -> float:
    """Average confidence, 0.0 when no evidence yet."""
    if not confidences:
        return 0.0
    return round(sum(confidences) / len(confidences), 3)


def compute_learning_velocity(snapshots: list) -> float:
    """Slope of mastery over last 5 snapshots (mastery delta per snapshot).

    Returns a signed velocity in [-1, 1] range; 0 means stable.
    Mirrors app/evaluation/metrics.py:mastery_trend but as numeric slope
    so it can be persisted and trended.
    """
    if len(snapshots) < 2:
        return 0.0
    window = snapshots[-5:]
    first = window[0].new_mastery if hasattr(window[0], "new_mastery") else window[0]
    last = window[-1].new_mastery if hasattr(window[-1], "new_mastery") else window[-1]
    # Normalize by window length
    slope = (last - first) / max(len(window) - 1, 1)
    # Clamp to [-1, 1] for safety
    return round(max(-1.0, min(1.0, slope)), 4)


def compute_retention_score(retention_probs: list[float]) -> float:
    """Average retrieval_probability across skills, 0.5 prior when empty."""
    if not retention_probs:
        return 0.5
    return round(sum(retention_probs) / len(retention_probs), 3)


def compute_independence_score(submits: int, hinted_submits: int | None = None) -> float:
    """Proportion of submits without heavy hinting.

    V1 heuristic: if hint data unavailable, estimate from overall success
    pattern.  When hint counts are available, 1.0 means fully independent.
    """
    if submits == 0:
        return 0.5
    if hinted_submits is None:
        return 0.5  # neutral prior until we wire tutor hint counts
    hinted = max(0, min(hinted_submits, submits))
    return round(1.0 - hinted / submits, 3)


def build_unified_state(db: Session, student_id: uuid.UUID) -> dict:
    """Build the unified student state from existing evidence tables.

    This is the Level 4.1 projection (Data_Model §8, ROADMAP §32).  It pulls
    from the six halves: Knowledge (skills), Misconceptions (mistakes),
    Behavior (patterns), Retention (R(t)), Performance (executions), and
    Preferences (profile).  Raw evidence is never overwritten — this is a
    derived view (Data_Model §64 RAW vs DERIVED).

    The result is also mirrored to `student_learning_states` so that table
    becomes live instead of a stale placeholder (STATUS.md M14).
    """
    from app.analytics.service import build_learner_summary
    from app.analytics.service import build_summary as build_analytics_summary
    from app.retention.service import overview_for_student

    # Layer 1: raw evidence aggregates (existing services, already tested)
    learner = build_learner_summary(db, student_id)
    analytics = build_analytics_summary(db, student_id)

    # Retention needs explicit overview (live R(t) refresh)
    try:
        retention_overview = overview_for_student(db, student_id)
    except Exception:
        retention_overview = []

    # Preferences + existing learning state
    prefs = db.get(StudentPreferences, student_id)
    existing_state = db.get(StudentLearningState, student_id)

    # Knowledge slice
    skills = learner.get("skills", [])
    masteries = [s["mastery"] for s in skills]
    confidences = [s["confidence"] for s in skills]
    overall_mastery = compute_overall_mastery(masteries)
    confidence = compute_confidence(confidences)

    # Identify gaps: skills with mastery < 0.4 (Developing/Unknown threshold)
    gaps = [s for s in skills if s["mastery"] < 0.4]
    strong = [s for s in skills if s["mastery"] >= 0.75]

    # Misconceptions slice (top recurring patterns)
    misconceptions = learner.get("mistake_patterns", [])[:5]
    open_mistakes = learner.get("open_mistakes", [])

    # Behavior slice
    behaviors = learner.get("behavior_patterns", [])

    # Retention slice
    retention_probs = [r["retrieval_probability"] for r in retention_overview]
    retention_score = compute_retention_score(retention_probs)
    due_skills = [r for r in retention_overview if r.get("due")]

    # Performance slice
    totals = analytics.get("totals", {})
    problems = analytics.get("problems", {})
    success_rate = totals.get("success_rate")

    # Independence: V1 uses hint-unavailable prior (0.5) until we count
    # tutor hints per submit.  Future wiring will pass hinted_submits.
    submits = totals.get("submits", 0)
    independence_score = compute_independence_score(submits)

    # Learning velocity: slope over recent mastery snapshots
    velocity = 0.0
    trend_label = "unknown"
    try:
        from app.skills.models import MasterySnapshot

        snapshots = db.scalars(
            select(MasterySnapshot)
            .where(MasterySnapshot.student_id == student_id)
            .order_by(MasterySnapshot.created_at)
        ).all()
        velocity = compute_learning_velocity(snapshots)
        # Map numeric velocity to label
        if velocity > 0.02:
            trend_label = "improving"
        elif velocity < -0.02:
            trend_label = "declining"
        elif len(snapshots) >= 2:
            trend_label = "stable"
    except Exception:
        velocity = 0.0

    # Preferences slice (raw profile, not derived ability)
    pref_dict = {}
    if prefs:
        pref_dict = {
            "preferred_language": prefs.preferred_language,
            "preferred_difficulty": prefs.preferred_difficulty,
            "explanation_style": prefs.explanation_style,
            "hint_style": prefs.hint_style,
            "session_length": prefs.session_length,
        }

    # Build unified projection
    unified = {
        "student_id": str(student_id),
        "model_version": MODEL_VERSION,
        "generated_at": datetime.now(UTC).isoformat(),
        "knowledge": {
            "overall_mastery": overall_mastery,
            "confidence": confidence,
            "skills": skills,
            "gaps": gaps,
            "strengths": strong,
            "skill_count": len(skills),
        },
        "misconceptions": {
            "open_mistakes": open_mistakes,
            "recurring": misconceptions,
            "open_count": len(open_mistakes),
            "recurring_count": len(misconceptions),
        },
        "behavior": {
            "patterns": behaviors,
            "pattern_count": len(behaviors),
        },
        "retention": {
            "overview": retention_overview,
            "due": due_skills,
            "retention_score": retention_score,
            "due_count": len(due_skills),
        },
        "performance": {
            "totals": totals,
            "problems": problems,
            "success_rate": success_rate,
            "recent_activity": analytics.get("recent_activity", [])[:5],
        },
        "preferences": pref_dict,
        "learning_velocity": velocity,
        "trend": trend_label,
        "summary": {
            "overall_mastery": overall_mastery,
            "confidence": confidence,
            "retention_score": retention_score,
            "independence_score": independence_score,
            "learning_velocity": velocity,
            "trend": trend_label,
        },
    }

    # Mirror aggregate scores to student_learning_states (Data_Model §8).
    # This table was a placeholder; now it carries live values.
    try:
        if existing_state is None:
            existing_state = StudentLearningState(
                student_id=student_id,
                overall_mastery=overall_mastery,
                learning_velocity=velocity,
                independence_score=independence_score,
                retention_score=retention_score,
            )
            db.add(existing_state)
        else:
            existing_state.overall_mastery = overall_mastery
            existing_state.learning_velocity = velocity
            existing_state.independence_score = independence_score
            existing_state.retention_score = retention_score
        db.commit()
    except Exception:
        db.rollback()

    return unified
