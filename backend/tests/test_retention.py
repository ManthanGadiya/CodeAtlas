"""Retention & forgetting tests — Phase 3.6 (docs/Forgetting_And_Retention.md)."""

import math
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select

from app.problems.seed import seed_problems
from app.retention.service import (
    INITIAL_STABILITY,
    MAX_STABILITY,
    compute_retention,
    days_since,
)

SLUG = "two-sum"


@pytest.fixture()
def seeded_skill(db_session):
    seed_problems(db_session)
    from app.problems.models import Skill

    skill = db_session.scalar(select(Skill).where(Skill.slug == "arrays"))
    assert skill is not None
    return skill


class TestRetentionMath:
    def test_retention_at_zero_days_is_one(self):
        assert compute_retention(INITIAL_STABILITY, 0) == 1.0

    def test_retention_decays_exponentially(self):
        # R(t) = exp(-t/S) — at t=S, R≈0.3679
        assert math.isclose(compute_retention(2.5, 2.5), math.exp(-1), rel_tol=1e-6)
        assert compute_retention(5.0, 2.5) > compute_retention(2.5, 2.5)

    def test_retention_long_time_near_zero(self):
        assert compute_retention(2.5, 100) < 0.01

    def test_days_since_none_is_none(self):
        assert days_since(None, datetime.now(UTC)) is None

    def test_days_since_computes_fractional(self):
        now = datetime(2026, 9, 10, tzinfo=UTC)
        last = now - timedelta(hours=12)
        assert days_since(last, now) == pytest.approx(0.5)


class TestRetentionAPI:
    def test_overview_requires_auth(self, client):
        assert client.get("/api/retention/overview").status_code == 401

    def test_overview_empty_before_any_evidence(self, client):
        client.post(
            "/api/auth/register",
            json={"email": "ret1@example.com", "password": "strongPass123!"},
        )
        resp = client.get("/api/retention/overview")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_overview_after_one_submit_shows_stability(self, client, seeded_skill, runner_fake):
        client.post(
            "/api/auth/register",
            json={"email": "ret2@example.com", "password": "strongPass123!"},
        )
        client.post(
            f"/api/problems/{SLUG}/submit",
            json={"code": "def two_sum(nums, target): return [0,1]"},
        )
        resp = client.get("/api/retention/overview")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) > 0
        first = data[0]
        assert "stability" in first and "retrieval_probability" in first
        assert first["stability"] >= INITIAL_STABILITY
        assert 0 <= first["retrieval_probability"] <= 1

    def test_review_success_increases_stability(self, client, seeded_skill, runner_fake):
        client.post(
            "/api/auth/register",
            json={"email": "ret3@example.com", "password": "strongPass123!"},
        )
        client.post(
            f"/api/problems/{SLUG}/submit",
            json={"code": "def two_sum(nums, target): return [0,1]"},
        )
        resp = client.post("/api/retention/review", json={"skill_slug": "arrays", "success": True})
        assert resp.status_code == 200
        assert resp.json()["stability"] > INITIAL_STABILITY
        assert resp.json()["retrieval_probability"] == 1.0
        resp2 = client.post("/api/retention/review", json={"skill_slug": "arrays", "success": True})
        assert resp2.json()["stability"] > resp.json()["stability"]

    def test_review_failure_decreases_stability(self, client, seeded_skill, runner_fake):
        client.post(
            "/api/auth/register",
            json={"email": "ret4@example.com", "password": "strongPass123!"},
        )
        client.post(
            f"/api/problems/{SLUG}/submit",
            json={"code": "def two_sum(nums, target): return [0,1]"},
        )
        client.post("/api/retention/review", json={"skill_slug": "arrays", "success": True})
        before = client.post(
            "/api/retention/review", json={"skill_slug": "arrays", "success": True}
        ).json()
        after_fail = client.post(
            "/api/retention/review", json={"skill_slug": "arrays", "success": False}
        ).json()
        assert after_fail["stability"] < before["stability"]
        assert after_fail["retrieval_probability"] < 1.0

    def test_review_unknown_skill_404(self, client):
        client.post(
            "/api/auth/register",
            json={"email": "ret5@example.com", "password": "strongPass123!"},
        )
        resp = client.post("/api/retention/review", json={"skill_slug": "nope", "success": True})
        assert resp.status_code == 404

    def test_stability_capped(self, client, seeded_skill, runner_fake):
        client.post(
            "/api/auth/register",
            json={"email": "ret6@example.com", "password": "strongPass123!"},
        )
        client.post(
            f"/api/problems/{SLUG}/submit",
            json={"code": "def two_sum(nums, target): return [0,1]"},
        )
        for _ in range(10):
            client.post("/api/retention/review", json={"skill_slug": "arrays", "success": True})
        resp = client.get("/api/retention/overview").json()
        assert all(item["stability"] <= MAX_STABILITY for item in resp)

    def test_overview_due_flag(self, client, seeded_skill, runner_fake):
        client.post(
            "/api/auth/register",
            json={"email": "ret7@example.com", "password": "strongPass123!"},
        )
        client.post(
            f"/api/problems/{SLUG}/submit",
            json={"code": "def two_sum(nums, target): return [0,1]"},
        )
        for _ in range(3):
            client.post("/api/retention/review", json={"skill_slug": "arrays", "success": False})
        data = client.get("/api/retention/overview").json()
        due_items = [d for d in data if d["due"]]
        assert len(due_items) >= 1
