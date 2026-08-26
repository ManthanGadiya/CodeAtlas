"""Translate graded submissions into mastery evidence (ROADMAP Phase 2.4).

Only Submit results update mastery: Run grades visible examples the
student has already seen, so success there cannot separate knowledge from
familiarity (docs/Learning_Model.md §12.4 — ambiguous evidence must not
trigger aggressive updates). Every weight below is an explicit initial
assumption pending baseline evaluation, kept in one place so it can be
tuned and audited (docs/Evaluation_Framework.md).
"""

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.execution.models import Execution
from app.problems.models import Problem
from app.skills.service import apply_evidence

# docs/Learning_Model.md §28: repeated attempts weaken positive evidence —
# a solve that took many tries demonstrates less than a first-try solve.
FIRST_ATTEMPT_STRENGTH = 1.0
RETRY_STRENGTH = 0.7  # attempts 2-3
LATE_RETRY_STRENGTH = 0.5  # attempt 4+
# docs/Learning_Model.md §12.4: a failed submit is ambiguous (conceptual
# weakness vs carelessness vs misread requirements), so it moves the
# estimate less than an unambiguous success.
FAILED_SUBMIT_STRENGTH = 0.4
LOAD_ERROR_STRENGTH = 0.3  # code never loaded: noisy attribution to knowledge
SUPPORTING_ROLE_FACTOR = 0.5  # primary skills carry full weight (Data_Model §28)


@dataclass(frozen=True)
class EvidenceObservation:
    positive: bool
    strength: float
    reason: str


def derive_submission_evidence(
    *, status: str, passed: int, total: int, attempt_number: int
) -> EvidenceObservation | None:
    """Pure mapping from one graded Submit outcome to evidence.

    ``attempt_number`` counts the current submission; returns None when the
    outcome carries no mastery signal at all.
    """
    if total == 0:
        return None

    if status == "SUCCESS":
        if passed == total:
            if attempt_number <= 1:
                strength = FIRST_ATTEMPT_STRENGTH
            elif attempt_number <= 3:
                strength = RETRY_STRENGTH
            else:
                strength = LATE_RETRY_STRENGTH
            return EvidenceObservation(True, strength, f"solved on attempt {attempt_number}")
        return EvidenceObservation(
            False,
            FAILED_SUBMIT_STRENGTH,
            f"failed {total - passed} of {total} cases on attempt {attempt_number}",
        )

    # Compile errors, runtime errors, timeouts: evidence about knowledge
    # specifically is noisy here, so the move is deliberately small.
    return EvidenceObservation(False, LOAD_ERROR_STRENGTH, f"submit ended in {status}")


def record_submission_evidence(
    db: Session,
    *,
    student_id: UUID,
    problem: Problem,
    mode: str,
    status: str,
    passed: int,
    total: int,
) -> int:
    """Apply mastery updates for one graded execution; returns skills updated.

    Call after persist_execution has committed so the submit-history count
    includes the attempt being recorded. Run-mode executions never touch
    mastery. A problem with no skill links simply produces no evidence.
    """
    links = list(problem.skill_links)
    if mode != "submit" or not links:
        return 0

    attempt_number = db.scalar(
        select(func.count())
        .select_from(Execution)
        .where(
            Execution.student_id == student_id,
            Execution.problem_id == problem.id,
            Execution.mode == "submit",
        )
    )
    observation = derive_submission_evidence(
        status=status,
        passed=passed,
        total=total,
        attempt_number=attempt_number or 0,
    )
    if observation is None:
        return 0

    for link in links:
        role_factor = 1.0 if link.role == "primary" else SUPPORTING_ROLE_FACTOR
        reason = f"{observation.reason} [{problem.slug}]"[:120]  # fits String(120)
        apply_evidence(
            db,
            student_id=student_id,
            skill_id=link.skill_id,
            positive=observation.positive,
            strength=observation.strength * role_factor,
            reason=reason,
        )
    return len(links)
