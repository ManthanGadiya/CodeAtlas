"""Evidence wiring tests: graded submissions must move skill mastery.

Integration tests drive the real submit/run endpoints with the fake runner
and assert on the resulting StudentSkillState/MasterySnapshot rows; pure
tests pin the derivation rules (strength scaling, ambiguity discounts).
"""

import uuid

import pytest
from sqlalchemy import select

from app.execution.models import Execution
from app.execution.runner import RunOutcome
from app.problems.models import Problem
from app.problems.seed import seed_problems
from app.skills.evidence import (
    FAILED_SUBMIT_STRENGTH,
    FIRST_ATTEMPT_STRENGTH,
    LATE_RETRY_STRENGTH,
    LOAD_ERROR_STRENGTH,
    RETRY_STRENGTH,
    derive_submission_evidence,
    record_submission_evidence,
)
from app.skills.models import MasterySnapshot, StudentSkillState
from app.skills.service import INITIAL_MASTERY
from app.users.models import Student

SLUG = "binary-search-first-occurrence"
REGISTER = {"email": "student@example.com", "password": "correct-horse-battery"}
SOLUTION = "def first_occurrence(nums, target):\n    return -1\n"


@pytest.fixture()
def authed_client(client):
    client.post("/api/auth/register", json=REGISTER)
    return client


@pytest.fixture()
def seeded_student_problem(db_session):
    """Seed the catalog and return (student_id, problem_id, role_by_skill_id)."""
    seed_problems(db_session)
    from app.problems.service import get_problem_by_slug

    student = db_session.scalar(select(Student).where(Student.email == REGISTER["email"]))
    problem = get_problem_by_slug(db_session, SLUG)
    roles = {link.skill_id: link.role for link in problem.skill_links}
    assert roles, "seeded problem must have skill links for these tests"
    return student.id, problem.id, roles


class TestSubmissionToMastery:
    def test_first_successful_submit_creates_mastery_states(
        self, authed_client, db_session, runner_fake, seeded_student_problem
    ):
        student_id, problem_id, roles = seeded_student_problem

        response = authed_client.post(f"/api/problems/{SLUG}/submit", json={"code": SOLUTION})
        assert response.status_code == 200

        states = {
            state.skill_id: state for state in db_session.scalars(select(StudentSkillState)).all()
        }
        assert set(states) == set(roles)
        primary = states[next(sid for sid, role in roles.items() if role == "primary")]
        supporting = states[next(sid for sid, role in roles.items() if role == "supporting")]

        # First-try full pass: positive evidence above the revisable prior.
        assert primary.mastery > INITIAL_MASTERY
        # Primary skills carry more weight than supporting ones (Data_Model §28).
        assert primary.mastery - INITIAL_MASTERY > supporting.mastery - INITIAL_MASTERY
        assert primary.evidence_count == 1

        snapshot = db_session.scalar(
            select(MasterySnapshot).where(MasterySnapshot.student_id == student_id)
        )
        assert snapshot.previous_mastery is None
        assert "attempt 1" in snapshot.reason
        assert SLUG in snapshot.reason

    def test_run_mode_never_updates_mastery(
        self, authed_client, db_session, runner_fake, seeded_student_problem
    ):
        response = authed_client.post(f"/api/problems/{SLUG}/run", json={"code": SOLUTION})
        assert response.status_code == 200
        assert response.json()["status"] == "SUCCESS"

        assert db_session.scalars(select(StudentSkillState)).all() == []
        assert db_session.scalars(select(MasterySnapshot)).all() == []

    def test_failed_submit_moves_mastery_down(
        self, authed_client, db_session, runner_fake, seeded_student_problem
    ):
        def failing_run(self, **kwargs):
            self.calls.append(kwargs)
            return RunOutcome(
                status="SUCCESS",
                runtime_ms=5,
                exit_code=0,
                stdout_tail="",
                stderr_tail="",
                results=[
                    {"name": t["name"], "passed": False, "actual": "x", "error": "AssertionError"}
                    for t in kwargs["tests"]
                ],
            )

        runner_fake.run = failing_run.__get__(runner_fake)
        response = authed_client.post(f"/api/problems/{SLUG}/submit", json={"code": SOLUTION})
        assert response.status_code == 200

        states = db_session.scalars(select(StudentSkillState)).all()
        assert states
        assert all(state.mastery < INITIAL_MASTERY for state in states)

    def test_runs_do_not_count_as_attempts(
        self, authed_client, db_session, runner_fake, seeded_student_problem
    ):
        student_id, problem_id, roles = seeded_student_problem
        # A prior run plus a prior failed submit: only the submit counts.
        db_session.add_all(
            [
                Execution(
                    student_id=student_id, problem_id=problem_id, mode="run", status="SUCCESS"
                ),
                Execution(
                    student_id=student_id,
                    problem_id=problem_id,
                    mode="submit",
                    status="RUNTIME_ERROR",
                ),
            ]
        )
        db_session.commit()

        authed_client.post(f"/api/problems/{SLUG}/submit", json={"code": SOLUTION})

        snapshots = db_session.scalars(
            select(MasterySnapshot).where(MasterySnapshot.student_id == student_id)
        ).all()
        assert len(snapshots) == len(roles)
        assert all("attempt 2" in snapshot.reason for snapshot in snapshots)


class TestDerivationRules:
    def test_attempt_scaling_weakens_repeated_success(self):
        first = derive_submission_evidence(status="SUCCESS", passed=5, total=5, attempt_number=1)
        second = derive_submission_evidence(status="SUCCESS", passed=5, total=5, attempt_number=2)
        fourth = derive_submission_evidence(status="SUCCESS", passed=5, total=5, attempt_number=4)

        assert first.strength == FIRST_ATTEMPT_STRENGTH
        assert second.strength == RETRY_STRENGTH < first.strength
        assert fourth.strength == LATE_RETRY_STRENGTH < second.strength
        assert all(obs.positive for obs in (first, second, fourth))

    def test_failed_submit_is_ambiguous_negative(self):
        observation = derive_submission_evidence(
            status="SUCCESS", passed=3, total=6, attempt_number=1
        )
        assert not observation.positive
        assert observation.strength == FAILED_SUBMIT_STRENGTH < FIRST_ATTEMPT_STRENGTH
        assert "failed" in observation.reason

    def test_non_success_status_maps_to_weakest_negative(self):
        for status in ("COMPILE_ERROR", "RUNTIME_ERROR", "TIMEOUT", "MEMORY_LIMIT"):
            observation = derive_submission_evidence(
                status=status, passed=0, total=4, attempt_number=1
            )
            assert not observation.positive
            assert observation.strength == LOAD_ERROR_STRENGTH <= FAILED_SUBMIT_STRENGTH

    def test_zero_graded_cases_carries_no_signal(self):
        assert (
            derive_submission_evidence(status="SYSTEM_ERROR", passed=0, total=0, attempt_number=1)
            is None
        )

    def test_reason_never_exceeds_column_limit(self, db_session):
        problem = Problem(
            id=uuid.uuid4(),
            slug="x" * 120,
            title="Long slug stress",
            description="d",
            difficulty="easy",
            function_name="f",
        )
        applied = record_submission_evidence(
            db_session,
            student_id=uuid.uuid4(),
            problem=problem,
            mode="submit",
            status="SUCCESS",
            passed=1,
            total=1,
        )
        # No linked skills -> nothing recorded; the point is that constructing
        # and truncating reasons never raises before that check.
        assert applied == 0
