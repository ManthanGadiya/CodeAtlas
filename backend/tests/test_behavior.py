"""Behavior model tests: threshold rules, patterns, learner summary API."""

import pytest
from sqlalchemy import select

from app.behavior.models import BehaviorObservation, BehaviorPattern
from app.events.models import LearningEvent
from app.problems.seed import seed_problems

REGISTER = {"email": "student@example.com", "password": "correct-horse-battery"}
SOLUTION = "def first_occurrence(nums, target):\n    return -1\n"
SLUG = "binary-search-first-occurrence"


@pytest.fixture()
def authed_client(client):
    client.post("/api/auth/register", json=REGISTER)
    return client


@pytest.fixture()
def catalog(db_session):
    seed_problems(db_session)


def failing_submits(authed_client, count, *, code_suffix=""):
    for i in range(count):
        code = f"def first_occurrence(nums, target):\n    return None  # {code_suffix}{i}\n"
        response = authed_client.post(f"/api/problems/{SLUG}/submit", json={"code": code})
        assert response.status_code == 200


def observations_of(db_session, behavior_type=None):
    stmt = select(BehaviorObservation)
    if behavior_type is not None:
        stmt = stmt.where(BehaviorObservation.behavior_type == behavior_type)
    return db_session.scalars(stmt).all()


class TestBehaviorRules:
    def test_no_signal_below_threshold(self, authed_client, db_session, runner_fake, catalog):
        runner_fake.status = "RUNTIME_ERROR"
        failing_submits(authed_client, 2)

        assert observations_of(db_session) == []
        assert db_session.scalars(select(BehaviorPattern)).all() == []

    def test_repeated_retry_fires_at_third_failed_submit(
        self, authed_client, db_session, runner_fake, catalog
    ):
        runner_fake.status = "RUNTIME_ERROR"
        failing_submits(authed_client, 3)

        retries = observations_of(db_session, "REPEATED_RETRY")
        assert len(retries) == 1
        assert retries[0].severity == "MEDIUM"

        pattern = db_session.scalar(
            select(BehaviorPattern).where(BehaviorPattern.behavior_type == "REPEATED_RETRY")
        )
        assert pattern.frequency == 1
        assert pattern.confidence >= 0.3

        event = db_session.scalar(
            select(LearningEvent).where(LearningEvent.event_type == "BEHAVIOR_OBSERVED")
        )
        assert event.payload["behavior_type"] == "REPEATED_RETRY"

    def test_repeated_retry_escalates_to_high(
        self, authed_client, db_session, runner_fake, catalog
    ):
        runner_fake.status = "RUNTIME_ERROR"
        failing_submits(authed_client, 5)

        retries = observations_of(db_session, "REPEATED_RETRY")
        assert [obs.severity for obs in retries] == ["MEDIUM", "MEDIUM", "HIGH"]
        pattern = db_session.scalar(
            select(BehaviorPattern).where(BehaviorPattern.behavior_type == "REPEATED_RETRY")
        )
        # Severity holds the worst seen; frequency counts every firing.
        assert (pattern.severity, pattern.frequency) == ("HIGH", 3)

    def test_low_testing_co_fires_without_any_runs(
        self, authed_client, db_session, runner_fake, catalog
    ):
        runner_fake.status = "RUNTIME_ERROR"
        failing_submits(authed_client, 3)

        low_testing = observations_of(db_session, "LOW_TESTING")
        assert len(low_testing) == 1

    def test_random_editing_needs_distinct_revisions(
        self, authed_client, db_session, runner_fake, catalog
    ):
        runner_fake.status = "RUNTIME_ERROR"
        failing_submits(authed_client, 6, code_suffix="variant")

        edits = observations_of(db_session, "RANDOM_EDITING")
        # Six distinct submissions -> six artifacts; fires from the 4th.
        assert len(edits) == 3
        assert edits[0].severity == "MEDIUM"
        assert edits[-1].severity == "HIGH"

    def test_productive_persistence_fires_on_success_after_failures(
        self, authed_client, db_session, runner_fake, catalog
    ):
        runner_fake.status = "RUNTIME_ERROR"
        failing_submits(authed_client, 3)

        runner_fake.status = "SUCCESS"
        response = authed_client.post(f"/api/problems/{SLUG}/submit", json={"code": SOLUTION})
        assert response.status_code == 200

        persistence = observations_of(db_session, "PRODUCTIVE_PERSISTENCE")
        assert len(persistence) == 1
        assert persistence[0].severity == "LOW"
        assert persistence[0].detail["failures_overcome"] == 3

    def test_full_pass_resets_the_streak(self, authed_client, db_session, runner_fake, catalog):
        runner_fake.status = "RUNTIME_ERROR"
        failing_submits(authed_client, 3)

        runner_fake.status = "SUCCESS"
        authed_client.post(f"/api/problems/{SLUG}/submit", json={"code": SOLUTION})

        # One fresh failure after the solve stays below every threshold.
        runner_fake.status = "RUNTIME_ERROR"
        before = len(observations_of(db_session, "REPEATED_RETRY"))
        failing_submits(authed_client, 1)

        assert len(observations_of(db_session, "REPEATED_RETRY")) == before

    def test_run_mode_never_fires_signals(self, authed_client, db_session, runner_fake, catalog):
        runner_fake.status = "RUNTIME_ERROR"
        for _ in range(5):
            response = authed_client.post(
                f"/api/problems/{SLUG}/run", json={"code": "while True:\n    pass\n"}
            )
            assert response.status_code == 200

        assert observations_of(db_session) == []


class TestLearnerSummaryEndpoint:
    def test_requires_authentication(self, client, db_session, catalog):
        assert client.get("/api/analytics/learner").status_code == 401

    def test_empty_state_is_honest_zero(self, authed_client, db_session, runner_fake, catalog):
        response = authed_client.get("/api/analytics/learner")
        assert response.status_code == 200
        body = response.json()
        assert body == {
            "skills": [],
            "open_mistakes": [],
            "mistake_patterns": [],
            "behavior_patterns": [],
        }

    def test_summary_reflects_activity(self, authed_client, db_session, runner_fake, catalog):
        runner_fake.status = "RUNTIME_ERROR"
        failing_submits(authed_client, 3)

        response = authed_client.get("/api/analytics/learner")
        body = response.json()

        # Evidence wiring created skill states, weakest first.
        skills = body["skills"]
        assert skills
        assert skills == sorted(skills, key=lambda s: s["mastery"])
        assert all(state["reliability"] in {"unknown", "estimated"} for state in skills)

        # Open mistakes and both co-fired behavior patterns are surfaced.
        assert {m["category_code"] for m in body["open_mistakes"]} == {"M03"}
        behavior_types = {p["behavior_type"] for p in body["behavior_patterns"]}
        assert {"REPEATED_RETRY", "LOW_TESTING"} <= behavior_types

        mistake_pattern_skills = {p["skill_slug"] for p in body["mistake_patterns"]}
        assert mistake_pattern_skills
