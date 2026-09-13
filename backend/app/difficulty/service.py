"""Difficulty engine — rule-based V1 (Problem_Generator §14-18, Data_Model §23).

Uses expert-authored vectors initially (§86) then calibrates from
student signals: mastery gaps drive student-specific difficulty
P(success | student, problem) and the productive-challenge zone
(0.55-0.75 success) per §17.
"""

from __future__ import annotations

import math
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.difficulty.models import DifficultyCalibration, ProblemDifficulty
from app.problems.models import Problem

MODEL_VERSION = "difficulty-rule-v1"

# Expert-authored difficulty vectors for seeded problems (0-1 each dimension)
# Calibrated so overall ≈ DIFFICULTY_NUMERIC but with meaningful spread.
VECTORS: dict[str, dict[str, float]] = {
    "two-sum": {
        "conceptual": 0.3,
        "implementation": 0.3,
        "reasoning": 0.35,
        "debugging": 0.2,
        "constraints": 0.25,
        "transfer": 0.2,
    },
    "valid-palindrome": {
        "conceptual": 0.35,
        "implementation": 0.3,
        "reasoning": 0.3,
        "debugging": 0.25,
        "constraints": 0.2,
        "transfer": 0.3,
    },
    "valid-parentheses": {
        "conceptual": 0.4,
        "implementation": 0.35,
        "reasoning": 0.4,
        "debugging": 0.35,
        "constraints": 0.2,
        "transfer": 0.25,
    },
    "maximum-subarray": {
        "conceptual": 0.6,
        "implementation": 0.5,
        "reasoning": 0.65,
        "debugging": 0.45,
        "constraints": 0.5,
        "transfer": 0.55,
    },
    "binary-search-first-occurrence": {
        "conceptual": 0.6,
        "implementation": 0.55,
        "reasoning": 0.65,
        "debugging": 0.6,
        "constraints": 0.4,
        "transfer": 0.5,
    },
}

DEFAULT_EASY = {
    "conceptual": 0.3,
    "implementation": 0.3,
    "reasoning": 0.35,
    "debugging": 0.25,
    "constraints": 0.2,
    "transfer": 0.2,
}
DEFAULT_MEDIUM = {
    "conceptual": 0.55,
    "implementation": 0.5,
    "reasoning": 0.6,
    "debugging": 0.5,
    "constraints": 0.45,
    "transfer": 0.5,
}
DEFAULT_HARD = {
    "conceptual": 0.8,
    "implementation": 0.75,
    "reasoning": 0.85,
    "debugging": 0.7,
    "constraints": 0.75,
    "transfer": 0.8,
}

LABELS = {"easy": DEFAULT_EASY, "medium": DEFAULT_MEDIUM, "hard": DEFAULT_HARD}


def vector_for_problem(problem: Problem) -> dict[str, float]:
    if problem.slug in VECTORS:
        return VECTORS[problem.slug]
    return LABELS.get(problem.difficulty, DEFAULT_MEDIUM)


def overall_from_vector(vec: dict[str, float]) -> float:
    # Weighted average: reasoning & conceptual count more for learning value
    weights = {
        "conceptual": 0.25,
        "implementation": 0.15,
        "reasoning": 0.25,
        "debugging": 0.1,
        "constraints": 0.1,
        "transfer": 0.15,
    }
    return round(sum(vec[k] * weights[k] for k in weights), 3)


def estimate_success(mastery: float, difficulty_overall: float, k: float = 6.0) -> float:
    """IRT-like logistic P(success) — 0.5 when mastery == difficulty."""
    return 1.0 / (1.0 + math.exp(-k * (mastery - difficulty_overall)))


def student_specific_difficulty(mastery: float, difficulty_overall: float) -> float:
    """Difficulty(problem | student): high when gap large."""
    return round(max(0.0, min(1.0, difficulty_overall - mastery + 0.5)), 3)


def zone_label(p_success: float) -> str:
    if p_success >= 0.85:
        return "comfort"
    if p_success >= 0.55:
        return "productive"
    if p_success >= 0.3:
        return "struggle"
    return "overload"


def get_or_create_vector(db: Session, problem: Problem) -> ProblemDifficulty:
    row = db.get(ProblemDifficulty, problem.id)
    if row:
        return row
    vec = vector_for_problem(problem)
    row = ProblemDifficulty(
        problem_id=problem.id,
        overall=overall_from_vector(vec),
        conceptual=vec["conceptual"],
        implementation=vec["implementation"],
        reasoning=vec["reasoning"],
        debugging=vec["debugging"],
        constraints=vec["constraints"],
        transfer=vec["transfer"],
        confidence=0.65,
        model_version=MODEL_VERSION,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def calibrate_from_signals(
    db: Session,
    problem: Problem,
    success_rate: float,
    n: int = 10,
    reason: str = "observed success_rate",
) -> ProblemDifficulty:
    """Adjust overall toward observed success_rate (1 - success_rate) with dampening."""
    vec = get_or_create_vector(db, problem)
    old = vec.overall
    # If students succeed >0.8, problem is easier than thought; push overall down
    target = 1.0 - success_rate
    # Dampening: small step (0.15) per calibration to avoid thrash
    new_overall = round(max(0.1, min(0.95, old + (target - old) * 0.15)), 3)
    if abs(new_overall - old) >= 0.02:
        vec.overall = new_overall
        hist = DifficultyCalibration(
            problem_id=problem.id,
            old_overall=old,
            new_overall=new_overall,
            reason=reason,
            model_version=MODEL_VERSION,
        )
        db.add(hist)
        db.commit()
        db.refresh(vec)
    return vec


def student_mastery_for_problem(db: Session, student_id: uuid.UUID, problem: Problem) -> float:
    """Average mastery across problem's skills."""
    from app.skills.models import StudentSkillState

    if not problem.skill_links:
        return 0.5
    scores = []
    for link in problem.skill_links:
        state = db.get(StudentSkillState, (student_id, link.skill_id))
        if state:
            scores.append(state.mastery)
        else:
            scores.append(0.5)
    return round(sum(scores) / len(scores), 3) if scores else 0.5


def estimate_for_student(db: Session, student_id: uuid.UUID, problem: Problem) -> dict:
    vec = get_or_create_vector(db, problem)
    mastery = student_mastery_for_problem(db, student_id, problem)
    p = round(estimate_success(mastery, vec.overall), 3)
    return {
        "slug": problem.slug,
        "overall": vec.overall,
        "vector": {
            "conceptual": vec.conceptual,
            "implementation": vec.implementation,
            "reasoning": vec.reasoning,
            "debugging": vec.debugging,
            "constraints": vec.constraints,
            "transfer": vec.transfer,
        },
        "confidence": vec.confidence,
        "model_version": vec.model_version,
        "student_mastery": mastery,
        "p_success": p,
        "student_specific_difficulty": student_specific_difficulty(mastery, vec.overall),
        "zone": zone_label(p),
    }


def recommend_difficulty_target(db: Session, student_id: uuid.UUID) -> dict:
    """Pick difficulty band where student is in productive zone."""

    from sqlalchemy.orm import selectinload

    from app.problems.models import Problem

    problems = db.scalars(select(Problem).options(selectinload(Problem.skill_links))).all()
    if not problems:
        return {"target_overall": 0.5, "band": "medium", "reason": "no problems"}
    # Average student mastery
    from app.skills.models import StudentSkillState

    rows = db.scalars(
        select(StudentSkillState).where(StudentSkillState.student_id == student_id)
    ).all()
    if not rows:
        return {"target_overall": 0.45, "band": "easy", "reason": "cold-start — ease in"}
    avg_mastery = sum(r.mastery for r in rows) / len(rows)
    # Productive zone wants difficulty ~ mastery + 0.1
    target = round(max(0.2, min(0.85, avg_mastery + 0.1)), 3)
    if target < 0.4:
        band = "easy"
    elif target < 0.65:
        band = "medium"
    else:
        band = "hard"
    # Count how many problems are already in productive zone
    productive = 0
    for p in problems:
        est = estimate_for_student(db, student_id, p)
        if est["zone"] == "productive":
            productive += 1
    return {
        "target_overall": target,
        "band": band,
        "avg_mastery": round(avg_mastery, 3),
        "productive_problems": productive,
        "total_problems": len(problems),
        "reason": (  # noqa: E501
            f"avg mastery {avg_mastery:.2f} → target {target:.2f} ({band}) keeps p_success ~0.65"
        ),
    }
