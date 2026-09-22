"""Unified student state tests — Level 4.1 (ROADMAP §32, Data_Model §8)."""

from sqlalchemy import select

from app.problems.seed import seed_problems
from app.unified.service import (
    compute_confidence,
    compute_independence_score,
    compute_learning_velocity,
    compute_overall_mastery,
    compute_retention_score,
)


class TestUnifiedPure:
    def test_overall_mastery_empty_is_prior(self):
        assert compute_overall_mastery([]) == 0.3

    def test_overall_mastery_avg(self):
        assert compute_overall_mastery([0.2, 0.8]) == 0.5

    def test_confidence_empty_zero(self):
        assert compute_confidence([]) == 0.0

    def test_retention_empty_prior(self):
        assert compute_retention_score([]) == 0.5

    def test_independence_no_submits(self):
        assert compute_independence_score(0) == 0.5

    def test_velocity_needs_two(self):
        assert compute_learning_velocity([]) == 0.0

    def test_velocity_improving(self):
        class S:
            def __init__(self, v):
                self.new_mastery = v

        snaps = [S(0.3), S(0.5), S(0.7)]
        assert compute_learning_velocity(snaps) > 0

    def test_velocity_clamped(self):
        class S:
            def __init__(self, v):
                self.new_mastery = v

        snaps = [S(0.0), S(1.0)]
        v = compute_learning_velocity(snaps)
        assert -1.0 <= v <= 1.0


class TestUnifiedAPI:
    def test_requires_auth(self, client):
        assert client.get("/api/learner/unified-state").status_code == 401

    def test_health(self, client):
        resp = client.get("/api/learner/unified-state/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    def test_empty_before_evidence(self, client):
        client.post(
            "/api/auth/register",
            json={"email": "uni1@example.com", "password": "strongPass123!"},
        )
        resp = client.get("/api/learner/unified-state")
        assert resp.status_code == 200
        data = resp.json()
        assert "knowledge" in data
        assert "misconceptions" in data
        assert "behavior" in data
        assert "retention" in data
        assert "performance" in data
        assert "preferences" in data
        assert "summary" in data
        assert data["model_version"] == "unified-rule-v1"
        assert data["knowledge"]["overall_mastery"] == 0.3
        assert data["summary"]["trend"] in ("unknown", "stable", "improving", "declining")

    def test_after_one_submit(self, client, db_session, runner_fake):
        seed_problems(db_session)
        client.post(
            "/api/auth/register",
            json={"email": "uni2@example.com", "password": "strongPass123!"},
        )
        client.post(
            "/api/problems/two-sum/submit",
            json={"code": "def two_sum(nums, target): return [0,1]"},
        )
        resp = client.get("/api/learner/unified-state")
        assert resp.status_code == 200
        data = resp.json()
        # Knowledge should now have skills
        assert data["knowledge"]["skill_count"] > 0
        assert data["knowledge"]["overall_mastery"] > 0.3
        assert data["performance"]["totals"]["submits"] >= 1
        # Retention should have at least one skill
        assert data["retention"]["retention_score"] >= 0
        # Summary mirrors derived scores
        assert 0 <= data["summary"]["overall_mastery"] <= 1

    def test_mirrors_to_student_learning_states(self, client, db_session, runner_fake):
        seed_problems(db_session)
        client.post(
            "/api/auth/register",
            json={"email": "uni3@example.com", "password": "strongPass123!"},
        )
        client.post(
            "/api/problems/two-sum/submit",
            json={"code": "def two_sum(nums, target): return [0,1]"},
        )
        client.get("/api/learner/unified-state")
        # Verify persistence
        from app.users.models import StudentLearningState

        rows = db_session.execute(select(StudentLearningState)).scalars().all()
        # There is exactly one student in this isolated test DB
        assert len(rows) == 1
        state = rows[0]
        assert 0 <= state.overall_mastery <= 1
        assert state.retention_score is not None
