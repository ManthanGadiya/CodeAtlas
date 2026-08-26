"""Mistake detection tests: deterministic classification, events, recurrence."""

import uuid

import pytest
from sqlalchemy import select

from app.events.models import LearningEvent
from app.execution.runner import RunOutcome
from app.mistakes.models import Mistake, MistakePattern
from app.mistakes.service import classify_outcome, observe_execution, seed_categories
from app.problems.models import Skill
from app.problems.seed import seed_problems
from app.skills.models import StudentSkillState
from app.users.models import Student

REGISTER = {"email": "student@example.com", "password": "correct-horse-battery"}
SOLUTION = "def first_occurrence(nums, target):\n    return -1\n"
SLUG = "binary-search-first-occurrence"


@pytest.fixture()
def authed_client(client):
    client.post("/api/auth/register", json=REGISTER)
    return client


@pytest.fixture()
def catalog(db_session):
    """Catalog + taxonomy rows, like a migrated production database."""
    seed_problems(db_session)
    seed_categories(db_session)


def student_id(db_session):
    return db_session.scalar(select(Student).where(Student.email == REGISTER["email"])).id


class TestClassifyOutcome:
    def test_compile_error_maps_to_syntax(self):
        mistake = classify_outcome(
            status="COMPILE_ERROR", visible_passed=0, visible_total=0, hidden_failed=0
        )
        assert mistake.category_code == "M01"
        assert mistake.severity == "LOW"

    def test_runtime_error_maps_to_m03(self):
        mistake = classify_outcome(
            status="RUNTIME_ERROR", visible_passed=0, visible_total=0, hidden_failed=0
        )
        assert mistake.category_code == "M03"

    def test_timeout_and_memory_map_to_complexity(self):
        for status in ("TIMEOUT", "MEMORY_LIMIT"):
            mistake = classify_outcome(
                status=status, visible_passed=0, visible_total=0, hidden_failed=0
            )
            assert mistake.category_code == "M07"

    def test_infrastructure_errors_are_never_classified(self):
        assert (
            classify_outcome(
                status="SYSTEM_ERROR", visible_passed=0, visible_total=3, hidden_failed=0
            )
            is None
        )

    def test_visible_pass_with_hidden_fail_is_edge_case(self):
        mistake = classify_outcome(
            status="SUCCESS", visible_passed=3, visible_total=3, hidden_failed=2
        )
        assert mistake.category_code == "M10"
        assert "hidden" in mistake.evidence_note

    def test_visible_failures_are_logic_errors(self):
        mistake = classify_outcome(
            status="SUCCESS", visible_passed=1, visible_total=3, hidden_failed=2
        )
        assert mistake.category_code == "M04"

    def test_full_pass_classifies_nothing(self):
        assert (
            classify_outcome(status="SUCCESS", visible_passed=3, visible_total=3, hidden_failed=0)
            is None
        )


class TestSubmissionFlow:
    def test_compile_error_submit_records_mistake_event_and_negative_evidence(
        self, authed_client, db_session, runner_fake, catalog
    ):
        runner_fake.load_error = {"kind": "syntax", "message": "SyntaxError: invalid syntax"}
        runner_fake.status = "COMPILE_ERROR"

        response = authed_client.post(
            f"/api/problems/{SLUG}/submit", json={"code": "def broken(:\n"}
        )
        assert response.status_code == 200

        # One mistake per detected submission, regardless of linked-skill count.
        mistakes = db_session.scalars(select(Mistake)).all()
        assert len(mistakes) == 1
        assert mistakes[0].severity == "LOW"

        event = db_session.scalar(
            select(LearningEvent).where(LearningEvent.event_type == "MISTAKE_DETECTED")
        )
        assert event.payload["category_code"] == "M01"
        assert event.payload["mistake_id"] == str(mistakes[0].id)

        # Phase 2.4 gap closed: compile errors now carry weak negative evidence.
        states = db_session.scalars(select(StudentSkillState)).all()
        assert states
        assert all(state.mastery < 0.3 for state in states)

    def test_hidden_failures_after_visible_pass_are_edge_case_mistakes(
        self, authed_client, db_session, runner_fake, catalog
    ):
        from app.problems.service import get_problem_by_slug

        problem = get_problem_by_slug(db_session, SLUG)
        passes = {case.name: case.visibility == "visible" for case in problem.test_cases}

        def edge_failure_run(self, **kwargs):
            self.calls.append(kwargs)
            return RunOutcome(
                status="SUCCESS",
                runtime_ms=5,
                exit_code=0,
                stdout_tail="",
                stderr_tail="",
                results=[
                    {
                        "name": case["name"],
                        "passed": passes[case["name"]],
                        "actual": None,
                        "error": None if passes[case["name"]] else "AssertionError",
                    }
                    for case in kwargs["tests"]
                ],
            )

        runner_fake.run = edge_failure_run.__get__(runner_fake)
        response = authed_client.post(f"/api/problems/{SLUG}/submit", json={"code": SOLUTION})
        assert response.status_code == 200

        mistakes = db_session.scalars(select(Mistake)).all()
        assert len(mistakes) == 1
        assert mistakes[0].evidence_note.startswith("all ")
        assert mistakes[0].resolution_status == "UNRESOLVED"

    def test_successful_submit_resolves_open_mistakes(
        self, authed_client, db_session, runner_fake, catalog
    ):
        runner_fake.status = "RUNTIME_ERROR"
        authed_client.post(f"/api/problems/{SLUG}/submit", json={"code": SOLUTION})
        assert db_session.scalar(select(Mistake)).resolution_status == "UNRESOLVED"

        # Default FakeRunner behaviour: SUCCESS with every case passing.
        runner_fake.status = "SUCCESS"
        authed_client.post(f"/api/problems/{SLUG}/submit", json={"code": SOLUTION})

        mistakes = db_session.scalars(select(Mistake)).all()
        assert mistakes
        assert all(m.resolution_status == "RESOLVED" for m in mistakes)

    def test_run_mode_is_never_classified(self, authed_client, db_session, runner_fake, catalog):
        runner_fake.status = "RUNTIME_ERROR"
        response = authed_client.post(
            f"/api/problems/{SLUG}/run", json={"code": "while True:\n    pass\n"}
        )
        assert response.status_code == 200
        assert db_session.scalars(select(Mistake)).all() == []

    def test_recurrence_aggregates_across_problems_via_shared_skill(
        self, authed_client, db_session, runner_fake, catalog
    ):
        from app.mistakes.taxonomy import category_id

        runner_fake.status = "RUNTIME_ERROR"
        # two-sum and maximum-subarray both map the "arrays" skill (supporting).
        authed_client.post("/api/problems/two-sum/submit", json={"code": "x = (\n"})
        authed_client.post("/api/problems/maximum-subarray/submit", json={"code": "x = (\n"})

        arrays_skill = db_session.scalar(select(Skill).where(Skill.slug == "arrays"))
        pattern = db_session.get(
            MistakePattern, (student_id(db_session), category_id("M03"), arrays_skill.id)
        )
        assert pattern is not None
        assert pattern.occurrence_count == 2
        assert pattern.confidence > 0.3

        # Each submission produced its own mistake row.
        assert len(db_session.scalars(select(Mistake)).all()) == 2


class TestDirectObservation:
    def test_observe_requires_submit_mode(self, db_session, catalog):
        from app.problems.service import get_problem_by_slug

        problem = get_problem_by_slug(db_session, "two-sum")
        outcome = RunOutcome(
            status="COMPILE_ERROR",
            runtime_ms=1,
            exit_code=1,
            stdout_tail="",
            stderr_tail="",
            results=[],
        )
        # The mode guard fires before any DB work, so an unregistered
        # student id never touches a foreign key here.
        result = observe_execution(
            db_session,
            student_id=uuid.uuid4(),
            problem=problem,
            mode="run",
            outcome=outcome,
            executed_cases=[],
        )
        assert result is None
