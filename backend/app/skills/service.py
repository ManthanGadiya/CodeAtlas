"""Rule-based mastery update engine (docs/Learning_Model.md §48, Stage 1).

Each evidence observation moves mastery an exponential-moving-average step
toward what it implies (1.0 or 0.0), scaled by its strength, so early and
weak observations move the estimate little and no single event can dominate
(docs/Learning_Model.md §27). Mastery and confidence stay separate numbers
(rule 3): confidence records how much consistent signal has accumulated,
it does not gate further learning. Every change is written to the snapshot
trail with a reason (rules 6, 12), and values are clamped to [0.02, 0.98]
so any belief stays revisable.

Weights are explicit initial design assumptions, not validated constants —
they live here so they can be tuned and evaluated against baselines
(docs/Evaluation_Framework.md).
"""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.skills.models import MasterySnapshot, StudentSkillState

MODEL_VERSION = "mastery-rule-v1"

# Prior for a skill's first observation; confidence starts at 0, so this is
# a revisable guess rather than a claim about the student.
INITIAL_MASTERY = 0.3
# Revisability bounds: never certain knowledge, never certain failure.
MASTERY_FLOOR = 0.02
MASTERY_CEILING = 0.98
BASE_STEP = 0.08  # mastery movement fraction for unit-strength evidence
CONFIDENCE_GAIN = 0.15  # confidence approach rate toward 1.0 per unit-strength evidence


class InvalidEvidence(ValueError):
    pass


def compute_update(
    mastery: float, confidence: float, *, positive: bool, strength: float
) -> tuple[float, float]:
    """One evidence observation -> new (mastery, confidence). Pure function.

    ``strength`` weights the observation in [0, 1] (docs/Learning_Model.md
    §11): an independent correct solution should arrive near 1.0, a heavily
    assisted one much lower. Confidence rises on consistent evidence of
    either direction (§36) — quantity of signal sharpens the estimate even
    when the news is bad — but does not gate mastery movement.
    """
    if not 0.0 <= strength <= 1.0:
        raise InvalidEvidence(f"strength must be within [0, 1], got {strength}")

    target = 1.0 if positive else 0.0
    step = BASE_STEP * strength
    new_mastery = min(max(mastery + step * (target - mastery), MASTERY_FLOOR), MASTERY_CEILING)
    new_confidence = min(confidence + CONFIDENCE_GAIN * strength * (1.0 - confidence), 1.0)
    return new_mastery, new_confidence


def apply_evidence(
    db: Session,
    *,
    student_id: UUID,
    skill_id: UUID,
    positive: bool,
    strength: float,
    reason: str,
) -> tuple[StudentSkillState, MasterySnapshot]:
    """Record one evidence observation for a (student, skill) pair.

    Creates the state row on first evidence, updates it in place afterwards
    (one row per pair), and always appends a snapshot capturing the previous
    value (NULL on first evidence). Commits before returning.
    """
    if not reason.strip():
        raise InvalidEvidence("reason must describe why mastery changed")
    if len(reason) > 120:
        raise InvalidEvidence("reason must fit String(120)")

    state = db.get(StudentSkillState, (student_id, skill_id))
    first_evidence = state is None or state.evidence_count == 0
    base_mastery = INITIAL_MASTERY if first_evidence else state.mastery
    base_confidence = 0.0 if first_evidence else state.confidence
    previous_mastery = None if first_evidence else base_mastery

    new_mastery, new_confidence = compute_update(
        base_mastery, base_confidence, positive=positive, strength=strength
    )

    if state is None:
        state = StudentSkillState(
            student_id=student_id,
            skill_id=skill_id,
            mastery=INITIAL_MASTERY,
            confidence=0.0,
            evidence_count=0,
            model_version=MODEL_VERSION,
        )
        db.add(state)

    now = datetime.now(UTC)
    state.mastery = new_mastery
    state.confidence = new_confidence
    state.evidence_count += 1
    state.last_practiced_at = now
    state.model_version = MODEL_VERSION

    snapshot = MasterySnapshot(
        student_id=student_id,
        skill_id=skill_id,
        previous_mastery=previous_mastery,
        new_mastery=new_mastery,
        reason=reason,
        model_version=MODEL_VERSION,
    )
    db.add(snapshot)
    db.commit()
    return state, snapshot
