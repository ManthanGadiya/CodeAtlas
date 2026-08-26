"""Tests for the student skill-state models and rule-based mastery engine."""

import uuid

import pytest
from sqlalchemy import select

from app.problems.models import Skill
from app.skills.models import MasterySnapshot, StudentSkillState
from app.skills.service import (
    INITIAL_MASTERY,
    MASTERY_CEILING,
    MASTERY_FLOOR,
    MODEL_VERSION,
    InvalidEvidence,
    apply_evidence,
    compute_update,
)
from app.users.models import Student


@pytest.fixture()
def ids(db_session):
    """A real student + skill pair so FK targets exist like production."""
    student = Student(email=f"{uuid.uuid4()}@example.com", password_hash="x")
    skill = Skill(slug=f"skill-{uuid.uuid4().hex[:12]}", name="Binary Search")
    db_session.add_all([student, skill])
    db_session.commit()
    return student.id, skill.id


def apply(db_session, ids, *, positive, strength, reason="unit-test evidence"):
    return apply_evidence(
        db_session,
        student_id=ids[0],
        skill_id=ids[1],
        positive=positive,
        strength=strength,
        reason=reason,
    )


class TestComputeUpdate:
    def test_positive_evidence_raises_mastery(self):
        mastery, _ = compute_update(0.5, 0.5, positive=True, strength=1.0)
        assert mastery > 0.5

    def test_negative_evidence_lowers_mastery(self):
        mastery, _ = compute_update(0.5, 0.5, positive=False, strength=1.0)
        assert mastery < 0.5

    def test_strength_scales_movement(self):
        weak, _ = compute_update(0.5, 0.0, positive=True, strength=0.2)
        strong, _ = compute_update(0.5, 0.0, positive=True, strength=1.0)
        assert strong - 0.5 > weak - 0.5

    def test_consistent_evidence_reaches_the_top_band(self):
        mastery = 0.3
        for _ in range(100):
            mastery, _ = compute_update(mastery, 1.0, positive=True, strength=1.0)
        # Sustained strong evidence must be able to reach Functional/Strong
        # (docs/Learning_Model.md §9) — the estimate may not stall mid-scale.
        assert mastery == MASTERY_CEILING

    def test_single_failure_cannot_define_a_skill(self):
        mastery, _ = compute_update(0.82, 0.9, positive=False, strength=1.0)
        # One event nudges, it does not redefine (docs/Learning_Model.md §27).
        assert mastery > 0.74

    def test_values_stay_revisable(self):
        top, _ = compute_update(MASTERY_CEILING, 1.0, positive=True, strength=1.0)
        bottom, _ = compute_update(MASTERY_FLOOR, 1.0, positive=False, strength=1.0)
        assert top == MASTERY_CEILING
        assert bottom == MASTERY_FLOOR

    def test_rejects_out_of_range_strength(self):
        with pytest.raises(InvalidEvidence):
            compute_update(0.5, 0.0, positive=True, strength=-0.1)
        with pytest.raises(InvalidEvidence):
            compute_update(0.5, 0.0, positive=True, strength=1.5)

    def test_confidence_rises_on_negative_evidence_too(self):
        _, confidence = compute_update(0.5, 0.4, positive=False, strength=1.0)
        assert confidence > 0.4


class TestApplyEvidence:
    def test_no_state_before_first_evidence(self, db_session, ids):
        state = db_session.get(StudentSkillState, ids)
        assert state is None

    def test_first_evidence_creates_state_and_snapshot(self, db_session, ids):
        state, snapshot = apply(db_session, ids, positive=True, strength=0.8)

        assert state.evidence_count == 1
        assert state.last_practiced_at is not None
        assert state.model_version == MODEL_VERSION
        # First evidence starts from the revisable prior, never from a claim.
        assert state.mastery > INITIAL_MASTERY
        assert snapshot.previous_mastery is None
        assert snapshot.new_mastery == state.mastery
        assert snapshot.reason == "unit-test evidence"

    def test_snapshot_trail_is_chained_and_persisted(self, db_session, ids):
        applied = [
            apply(db_session, ids, positive=bool(p), strength=s)
            for p, s in [(True, 0.9), (False, 0.5), (True, 1.0)]
        ]
        snapshots = [snapshot for _, snapshot in applied]

        assert snapshots[0].previous_mastery is None
        # Each snapshot explains its own change: previous -> new chains across
        # the whole history, ending at the current state value (rules 7, 12).
        for previous, following in zip(snapshots, snapshots[1:], strict=False):
            assert following.previous_mastery == previous.new_mastery

        rows = db_session.scalars(
            select(MasterySnapshot).where(
                MasterySnapshot.student_id == ids[0], MasterySnapshot.skill_id == ids[1]
            )
        ).all()
        assert len(rows) == 3
        assert {row.new_mastery for row in rows} == {s.new_mastery for s in snapshots}

    def test_repeated_evidence_updates_one_row(self, db_session, ids):
        for _ in range(3):
            apply(db_session, ids, positive=True, strength=0.5)

        states = db_session.scalars(select(StudentSkillState)).all()
        assert len(states) == 1
        assert states[0].evidence_count == 3

    def test_many_positives_clamp_at_ceiling(self, db_session, ids):
        for _ in range(200):
            state, _ = apply(db_session, ids, positive=True, strength=1.0)
        assert state.mastery == MASTERY_CEILING

    def test_many_negatives_clamp_at_floor(self, db_session, ids):
        for _ in range(200):
            state, _ = apply(db_session, ids, positive=False, strength=1.0)
        assert state.mastery == MASTERY_FLOOR

    def test_rejects_empty_reason(self, db_session, ids):
        with pytest.raises(InvalidEvidence):
            apply(db_session, ids, positive=True, strength=1.0, reason="   ")

    def test_rejects_overlong_reason(self, db_session, ids):
        with pytest.raises(InvalidEvidence):
            apply(db_session, ids, positive=True, strength=1.0, reason="x" * 121)
