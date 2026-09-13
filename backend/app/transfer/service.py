"""Transfer evaluation engine — rule-based V1 (Problem_Generator §49-51).

Transfer = same underlying reasoning, different surface. V1 picks a
skill where mastery >0.35, generates a T2 context_shift variant, and
records whether the student recognizes the technique.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Literal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.problems.models import Problem, ProblemSkill
from app.transfer.models import TransferEvaluation

MODEL_VERSION = "transfer-rule-v1"
TransferLevel = Literal["T0", "T1", "T2", "T3", "T4", "T5"]

LEVEL_META = {
    "T0": "Same structure",
    "T1": "Slight variation",
    "T2": "Different context",
    "T3": "Different representation",
    "T4": "Hidden technique",
    "T5": "Multi-concept transfer",
}


def due_for_transfer(db: Session, student_id: uuid.UUID) -> list[dict]:
    from app.skills.models import StudentSkillState

    rows = db.scalars(
        select(StudentSkillState).where(StudentSkillState.student_id == student_id)
    ).all()
    out = []
    for r in rows:
        if r.mastery >= 0.35 and r.evidence_count >= 1:
            from app.problems.models import Skill

            skill = db.get(Skill, r.skill_id)
            if not skill:
                continue
            # Check if transfer already succeeded recently → skip
            recent_success = db.scalars(
                select(TransferEvaluation).where(
                    TransferEvaluation.student_id == student_id,
                    TransferEvaluation.skill_id == r.skill_id,
                    TransferEvaluation.result == "success",
                )
            ).first()
            # If already succeeded, V1 surfaces once
            if recent_success:
                continue
            # Find a source problem for this skill
            link = db.scalar(
                select(ProblemSkill).where(ProblemSkill.skill_id == r.skill_id).limit(1)
            )
            source_slug = None
            if link:
                prob = db.get(Problem, link.problem_id)
                source_slug = prob.slug if prob else None
            out.append(
                {
                    "skill_id": str(r.skill_id),
                    "skill_slug": skill.slug,
                    "skill_name": skill.name,
                    "mastery": round(r.mastery, 3),
                    "evidence_count": r.evidence_count,
                    "source_problem_slug": source_slug,
                    "suggested_level": "T2",
                    "level_desc": LEVEL_META["T2"],
                }
            )
    # Sort strongest mastery first (transfer is evaluative, not remedial)
    out.sort(key=lambda x: x["mastery"], reverse=True)
    return out


def schedule_transfer(
    db: Session,
    student_id: uuid.UUID,
    skill_id: uuid.UUID,
    transfer_level: TransferLevel = "T2",
    runner=None,
) -> TransferEvaluation:
    from sqlalchemy import select

    from app.problems.models import Skill

    skill = db.get(Skill, skill_id)
    if not skill:
        raise ValueError("skill not found")
    # Find source problem
    link = db.scalar(select(ProblemSkill).where(ProblemSkill.skill_id == skill_id).limit(1))
    if not link:
        raise ValueError("no problem for skill")
    source_prob = db.get(Problem, link.problem_id)
    if not source_prob:
        raise ValueError("source problem missing")
    # Generate transfer variant via generator
    from app.generator.service import mutate_problem

    # Mutate to create transfer problem
    # Use context_shift for T2, boundary_variant for T1, constraint_tighten for T3, etc.
    mut_map = {
        "T0": "boundary_variant",
        "T1": "boundary_variant",
        "T2": "context_shift",
        "T3": "context_shift",
        "T4": "constraint_tighten",
        "T5": "constraint_tighten",
    }
    mutation = mut_map.get(transfer_level, "context_shift")
    # Delegate to generator mutate (creates a new problem)
    new_prob = mutate_problem(
        db,
        source_slug=source_prob.slug,
        mutation_type=mutation,
        student_id=student_id,
        runner=runner,
    )
    # Tweak title to reflect transfer level
    eval_row = TransferEvaluation(
        student_id=student_id,
        skill_id=skill_id,
        source_problem_id=source_prob.id,
        transfer_problem_id=new_prob.id,
        transfer_level=transfer_level,
        model_version=MODEL_VERSION,
    )
    db.add(eval_row)
    db.commit()
    db.refresh(eval_row)
    return eval_row


def complete_transfer(
    db: Session,
    evaluation_id: uuid.UUID,
    student_id: uuid.UUID,
    result: str,
    confidence: float | None = None,
) -> TransferEvaluation:
    row = db.get(TransferEvaluation, evaluation_id)
    if not row or row.student_id != student_id:
        raise ValueError("evaluation not found")
    if row.result is not None:
        raise ValueError("evaluation already completed")
    if result not in ("success", "failure", "partial"):
        raise ValueError("result must be success|failure|partial")
    row.result = result
    row.confidence = confidence
    row.completed_at = datetime.now(UTC)
    db.commit()
    # Emit event
    try:
        from app.events.service import record_event

        record_event(
            db,
            student_id=student_id,
            event_type="TRANSFER_ATTEMPTED",
            payload={
                "evaluation_id": str(row.id),
                "skill_id": str(row.skill_id),
                "transfer_level": row.transfer_level,
                "result": result,
            },
        )
    except Exception:
        pass
    db.refresh(row)
    return row


def history_for_student(
    db: Session, student_id: uuid.UUID, limit: int = 20
) -> list[TransferEvaluation]:
    return list(
        db.scalars(
            select(TransferEvaluation)
            .where(TransferEvaluation.student_id == student_id)
            .order_by(TransferEvaluation.created_at.desc())
            .limit(limit)
        ).all()
    )
