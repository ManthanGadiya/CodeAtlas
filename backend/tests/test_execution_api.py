"""Execution API tests using a fake runner (no Docker anywhere near CI)."""

import pytest

from app.execution.runner import RunnerUnavailableError, RunOutcome
from app.problems.seed import seed_problems

SLUG = "binary-search-first-occurrence"
REGISTER = {"email": "student@example.com", "password": "correct-horse-battery"}
SOLUTION = "def first_occurrence(nums, target):\n    return -1\n"


@pytest.fixture()
def authed_client(client):
    client.post("/api/auth/register", json=REGISTER)
    return client


def test_run_requires_authentication(client, db_session):
    response = client.post(f"/api/problems/{SLUG}/run", json={"code": SOLUTION})
    assert response.status_code == 401


def test_unknown_problem_404(authed_client, db_session):
    seed_problems(db_session)
    response = authed_client.post("/api/problems/nope/run", json={"code": SOLUTION})
    assert response.status_code == 404


def test_run_uses_only_visible_tests(authed_client, db_session, runner_fake):
    seed_problems(db_session)
    response = authed_client.post(f"/api/problems/{SLUG}/run", json={"code": SOLUTION})

    assert response.status_code == 200
    assert len(runner_fake.calls) == 1
    sent_names = [test["name"] for test in runner_fake.calls[0]["tests"]]
    assert sent_names == ["simple-present", "duplicates-first-index", "absent"]
    body = response.json()
    assert body["mode"] == "run"
    assert body["status"] == "SUCCESS"


def test_submit_uses_all_tests_including_hidden(authed_client, db_session, runner_fake):
    seed_problems(db_session)
    response = authed_client.post(f"/api/problems/{SLUG}/submit", json={"code": SOLUTION})

    body = response.json()
    assert response.status_code == 200
    assert body["mode"] == "submit"
    assert body["summary"]["total"] == 6


def test_successful_submission_is_persisted(authed_client, db_session, runner_fake):
    from app.execution.models import Execution, TestCaseExecution

    seed_problems(db_session)
    authed_client.post(f"/api/problems/{SLUG}/submit", json={"code": SOLUTION})

    rows = db_session.query(Execution).all()
    assert len(rows) == 1
    row = rows[0]
    assert row.mode == "submit"
    assert row.status == "SUCCESS"
    case_rows = db_session.query(TestCaseExecution).all()
    assert len(case_rows) == 6
    assert all(case.passed for case in case_rows)


def test_docker_unavailable_maps_to_503(authed_client, db_session, runner_fake):
    seed_problems(db_session)
    runner_fake.error = RunnerUnavailableError("The Docker engine does not appear to be running.")

    response = authed_client.post(f"/api/problems/{SLUG}/run", json={"code": SOLUTION})

    assert response.status_code == 503
    assert "Docker" in response.json()["detail"]


def test_timeout_status_is_surfaced(authed_client, db_session, runner_fake):
    seed_problems(db_session)
    runner_fake.status = "TIMEOUT"

    response = authed_client.post(
        f"/api/problems/{SLUG}/run", json={"code": "while True:\n    pass\n"}
    )
    assert response.json()["status"] == "TIMEOUT"
    assert response.json()["summary"]["total"] == 3


def test_compile_error_surfaces_message_without_case_results(
    authed_client, db_session, runner_fake
):
    seed_problems(db_session)
    runner_fake.load_error = {
        "kind": "syntax",
        "message": "SyntaxError: invalid syntax (line 1)",
    }
    runner_fake.status = "COMPILE_ERROR"

    response = authed_client.post(f"/api/problems/{SLUG}/run", json={"code": "def broken(:\n"})

    body = response.json()
    assert body["status"] == "COMPILE_ERROR"
    assert body["summary"]["total"] == 0
    assert "SyntaxError" in body["message"]


def test_execution_rate_limit_returns_429(authed_client, db_session, runner_fake):
    seed_problems(db_session)
    for _ in range(10):
        response = authed_client.post(f"/api/problems/{SLUG}/run", json={"code": SOLUTION})
        assert response.status_code == 200

    eleventh = authed_client.post(f"/api/problems/{SLUG}/run", json={"code": SOLUTION})
    assert eleventh.status_code == 429


def test_failed_submit_masks_hidden_case_details(authed_client, db_session, runner_fake):
    """Hidden cases report anonymous pass/fail only — no names or expected outputs."""
    from app.problems.models import TestCase

    seed_problems(db_session)
    hidden = db_session.query(TestCase).filter(TestCase.visibility == "hidden").first()
    assert hidden is not None

    # Make every case fail except we verify masking on the hidden ones.
    runner_fake.results = None
    runner_fake.load_error = None

    def failing_run(self, **kwargs):
        self.calls.append(kwargs)
        return RunOutcome(
            status="SUCCESS",
            runtime_ms=5,
            exit_code=0,
            stdout_tail="",
            stderr_tail="",
            results=[
                {"name": test["name"], "passed": False, "actual": "x", "error": "AssertionError"}
                for test in kwargs["tests"]
            ],
        )

    runner_fake.run = failing_run.__get__(runner_fake)

    response = authed_client.post(f"/api/problems/{SLUG}/submit", json={"code": SOLUTION})

    body = response.json()
    assert body["status"] == "SUCCESS"
    hidden_results = [r for r in body["results"] if r["visibility"] == "hidden"]
    visible_results = [r for r in body["results"] if r["visibility"] == "visible"]
    assert len(hidden_results) == 3
    for entry in hidden_results:
        assert entry["name"] is None
        assert entry["expected_output"] is None
        assert entry["passed"] is False
    # Visible cases keep full feedback.
    assert all(entry["name"] for entry in visible_results)
    assert all("expected_output" in entry for entry in visible_results)
    assert "hidden case(s) failed" in body["message"]
