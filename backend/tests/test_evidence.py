"""Evidence-layer tests: artifacts, version chains, events, analytics."""

import pytest

from app.events.models import LearningEvent
from app.events.service import UnknownEventType, record_event
from app.execution.models import CodeArtifact, Execution
from app.execution.service import record_artifact
from app.problems.models import Problem
from app.problems.seed import seed_problems

REGISTER = {"email": "student@example.com", "password": "correct-horse-battery"}


@pytest.fixture()
def authed_client(client):
    client.post("/api/auth/register", json=REGISTER)
    return client


@pytest.fixture()
def seeded_db(db_session):
    seed_problems(db_session)
    return db_session


def _two_sum_problem(db):
    return db.query(Problem).filter_by(slug="two-sum").one()


def _register_student(db):
    """Create the single student directly (no HTTP needed)."""
    from app.auth.service import register_student

    return register_student(db, "student@example.com", "correct-horse-battery", None)


def test_artifact_chain_with_diff_and_dedup(seeded_db):
    db = seeded_db
    problem = _two_sum_problem(db)
    student = _register_student(db)
    v1 = record_artifact(
        db,
        student_id=student.id,
        problem=problem,
        code="def two_sum(nums, t):\n    return []\n",
    )
    v2 = record_artifact(
        db,
        student_id=student.id,
        problem=problem,
        code="def two_sum(nums, t):\n    seen = {}\n    return []\n",
    )
    v2_again = record_artifact(
        db,
        student_id=student.id,
        problem=problem,
        code="def two_sum(nums, t):\n    seen = {}\n    return []\n",
    )

    assert v1.parent_artifact_id is None
    assert v1.diff_text is None
    assert v2.parent_artifact_id == v1.id
    assert "+    seen = {}" in v2.diff_text
    # Identical resubmission deduplicates to the same artifact.
    assert v2_again.id == v2.id
    # A later distinct version parents to the deduplicated artifact,
    # not to some forked twin.
    v3 = record_artifact(
        db,
        student_id=student.id,
        problem=problem,
        code="def two_sum(nums, t):\n    seen = {}\n    return [0]\n",
    )
    assert v3.parent_artifact_id == v2.id
    assert db.query(CodeArtifact).count() == 3


def test_unknown_event_type_is_rejected(seeded_db):
    student = _register_student(seeded_db)
    with pytest.raises(UnknownEventType):
        record_event(seeded_db, student_id=student.id, event_type="NOT_A_THING", payload={})


def test_events_are_recorded_immutable_shape(seeded_db):
    db = seeded_db
    student = _register_student(db)
    event = record_event(
        db, student_id=student.id, event_type="PROBLEM_OPENED", payload={"slug": "two-sum"}
    )

    row = db.query(LearningEvent).one()
    assert row.id == event.id
    assert row.event_type == "PROBLEM_OPENED"
    assert row.schema_version == 1
    assert row.payload == {"slug": "two-sum"}


def test_run_records_artifact_execution_and_events(authed_client, seeded_db, runner_fake):
    db = seeded_db

    response = authed_client.post(
        "/api/problems/two-sum/run",
        json={"code": "def two_sum(nums, target):\n    return [0, 1]\n"},
    )

    assert response.status_code == 200
    execution = db.query(Execution).one()
    assert execution.code_artifact_id is not None
    events = {e.event_type for e in db.query(LearningEvent).all()}
    assert "CODE_RUN" in events


def test_completed_submit_emits_problem_completed(authed_client, seeded_db, runner_fake):
    db = seeded_db

    authed_client.post(
        "/api/problems/two-sum/submit",
        json={"code": "def two_sum(nums, target):\n    return [0, 1]\n"},
    )

    events = {e.event_type for e in db.query(LearningEvent).all()}
    assert "PROBLEM_COMPLETED" in events


def test_analytics_summary_counts(authed_client, seeded_db, runner_fake):
    authed_client.post(
        "/api/problems/two-sum/run", json={"code": "def two_sum(a, b):\n    return [0, 1]\n"}
    )
    authed_client.post(
        "/api/problems/two-sum/submit", json={"code": "def two_sum(a, b):\n    return [0, 1]\n"}
    )

    response = authed_client.get("/api/analytics/summary")

    assert response.status_code == 200
    body = response.json()
    assert body["totals"]["runs"] == 1
    assert body["totals"]["submits"] == 1
    assert body["totals"]["success_rate"] == 1.0
    assert body["problems"]["attempted"] == 1
    assert body["problems"]["completed"] == 1
    assert len(body["recent_activity"]) == 2
    per = {p["problem_slug"]: p for p in body["per_problem"]}
    assert per["two-sum"]["completed"] is True


def test_analytics_requires_authentication(client):
    assert client.get("/api/analytics/summary").status_code == 401


def test_event_ingestion_endpoint(authed_client, seeded_db):
    response = authed_client.post(
        "/api/events",
        json={"event_type": "PROBLEM_OPENED", "payload": {"slug": "two-sum"}},
    )
    assert response.status_code == 201
    assert "id" in response.json()


def test_event_ingestion_requires_authentication(client):
    response = client.post("/api/events", json={"event_type": "PROBLEM_OPENED"})
    assert response.status_code == 401


def test_ingestion_cannot_forge_server_emitted_evidence(authed_client):
    """Grading/completion events are server-reserved — no client forgery."""
    for forged in ("PROBLEM_COMPLETED", "TEST_PASSED", "CODE_RUN"):
        response = authed_client.post(
            "/api/events", json={"event_type": forged, "payload": {"problem_slug": "two-sum"}}
        )
        assert response.status_code == 422, forged


def test_completed_submit_emits_faithful_event_trail(authed_client, seeded_db, runner_fake):
    """Submit grading records the documented per-case + completion events."""
    db = seeded_db

    authed_client.post(
        "/api/problems/two-sum/submit",
        json={"code": "def two_sum(nums, target):\n    return [0, 1]\n"},
    )

    events = [e.event_type for e in db.query(LearningEvent).all()]
    assert events.count("TEST_PASSED") == 5
    assert events.count("TEST_FAILED") == 0
    assert events.count("PROBLEM_COMPLETED") == 1
    assert events.count("CODE_RUN") == 1


def test_event_ingestion_rejects_unknown_types(authed_client):
    response = authed_client.post("/api/events", json={"event_type": "HAX"})
    assert response.status_code == 422
