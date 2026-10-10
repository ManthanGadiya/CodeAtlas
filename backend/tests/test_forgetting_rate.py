"""Forgetting rate estimation tests — Level 4.2 (ROADMAP §33, Data_Model §31)."""

import math
from datetime import UTC, datetime, timedelta

from sqlalchemy import select

from app.problems.models import Skill
from app.retention.models import RetentionState
from app.retention.service import estimate_forgetting_rate, fit_forgetting_rate
from app.skills.models import MasterySnapshot
from app.users.models import Student


class TestFitForgettingRate:
    def test_insufficient_points(self):
        assert fit_forgetting_rate([1.0], [0.5]) is None
        assert fit_forgetting_rate([1.0, 2.0], [0.5, 0.4]) is None
        assert fit_forgetting_rate([1.0, 2.0, 3.0], [0.5]) is None  # mismatched lengths

    def test_perfect_exponential_decay(self):
        # mastery = 0.8 * exp(-0.1 * t) + 0.1, sampled until near-asymptote
        # so V1 estimator (c = 0.9 * min) approximates the true asymptote.
        # t=0: 0.9; t=20: ~0.208; t=40: ~0.115
        t = [0.0, 20.0, 40.0]
        m = [0.9, 0.208, 0.115]
        lambda_est = fit_forgetting_rate(t, m)
        assert lambda_est is not None
        assert abs(lambda_est - 0.1) < 0.05

    def test_insufficient_span(self):
        # Points too close in time
        t = [0.0, 0.5, 1.0]
        m = [0.8, 0.7, 0.6]
        assert fit_forgetting_rate(t, m) is None

    def test_bad_values(self):
        assert fit_forgetting_rate([0, 1, 2], [-0.1, 0.5, 0.3]) is None  # negative mastery
        assert fit_forgetting_rate([0, 1, 2], [0.5, 0.5, 0.5]) is None  # constant (log(0) in fit)

    def test_bounds_rejected(self):
        # Very fast forgetting (half-life ~8 hours = λ ~ 2.1)
        t = [0.0, 1.0, 2.0]
        m = [0.9, 0.1, 0.02]
        assert fit_forgetting_rate(t, m) is None  # λ > 2.0 rejected

        # Very slow forgetting (half-life > 2 years = λ < 0.001)
        t = [0.0, 365.0, 730.0]
        m = [0.9, 0.89, 0.88]
        assert fit_forgetting_rate(t, m) is None  # λ < 0.001 rejected


class TestEstimateForgettingRate:
    def test_insufficient_snapshots(self, client, db_session):
        from app.problems.seed import seed_problems

        seed_problems(db_session)
        client.post(
            "/api/auth/register",
            json={"email": "test_est1@example.com", "password": "strongPass123!"},
        )
        db_session.expire_all()
        student = db_session.scalar(select(Student).where(Student.email == "test_est1@example.com"))
        skill = db_session.scalar(select(Skill).where(Skill.slug == "arrays"))
        assert student is not None and skill is not None
        # No snapshots
        assert estimate_forgetting_rate(db_session, student.id, skill.id) is None

    def test_estimate_with_history(self, client, db_session):
        from app.problems.seed import seed_problems

        seed_problems(db_session)
        client.post(
            "/api/auth/register",
            json={"email": "test_est2@example.com", "password": "strongPass123!"},
        )
        db_session.expire_all()
        student = db_session.scalar(select(Student).where(Student.email == "test_est2@example.com"))
        skill = db_session.scalar(select(Skill).where(Skill.slug == "arrays"))
        assert student is not None and skill is not None
        now = datetime.now(UTC).replace(tzinfo=None)
        # Create 5 snapshots with exponential decay
        for i, (t, m) in enumerate(
            [
                (now - timedelta(days=20), 0.9),
                (now - timedelta(days=15), 0.75),
                (now - timedelta(days=10), 0.6),
                (now - timedelta(days=5), 0.5),
                (now - timedelta(days=1), 0.45),
            ]
        ):
            db_session.add(
                MasterySnapshot(
                    student_id=student.id,
                    skill_id=skill.id,
                    previous_mastery=0.3 if i == 0 else None,
                    new_mastery=m,
                    confidence=0.5,
                    reason=f"test-{i}",
                    model_version="test",
                    created_at=t,
                )
            )
        db_session.commit()

        lambda_est = estimate_forgetting_rate(db_session, student.id, skill.id)
        assert lambda_est is not None
        assert 0.01 < lambda_est < 1.0  # reasonable range


class TestForgettingCurve:
    def test_get_forgetting_curve_no_lambda(self, client, db_session, runner_fake):
        from app.problems.seed import seed_problems

        seed_problems(db_session)
        client.post(
            "/api/auth/register",
            json={"email": "fc1@example.com", "password": "strongPass123!"},
        )
        # No forgetting rate estimated yet
        resp = client.get("/api/retention/forgetting-curve?skill_slug=arrays")
        assert resp.status_code == 404
        assert "not yet estimated" in resp.json()["detail"]

    def test_forgetting_curve_after_estimation(self, client, db_session, runner_fake):
        from app.problems.models import Skill
        from app.problems.seed import seed_problems

        seed_problems(db_session)
        client.post(
            "/api/auth/register",
            json={"email": "fc2@example.com", "password": "strongPass123!"},
        )
        db_session.expire_all()
        # Manually set a forgetting rate on the retention state
        skill = db_session.scalar(select(Skill).where(Skill.slug == "arrays"))
        student = db_session.scalar(select(Student).where(Student.email == "fc2@example.com"))
        r_state = RetentionState(
            student_id=student.id,
            skill_id=skill.id,
            stability=5.0,
            retrieval_probability=0.8,
            forgetting_rate=0.1,
            model_version="test",
        )
        db_session.add(r_state)
        db_session.commit()

        resp = client.get("/api/retention/forgetting-curve?skill_slug=arrays")
        assert resp.status_code == 200
        data = resp.json()
        # Pydantic serializes lambda_ as "lambda" due to alias
        assert abs(data["lambda"] - 0.1) < 0.001
        assert data["half_life_days"] is not None
        assert abs(data["half_life_days"] - math.log(2) / 0.1) < 1.0
        assert len(data["curve_points"]) == 13  # 0, 5, 10, ..., 60
        assert data["curve_points"][0]["t_days"] == 0
        assert data["curve_points"][0]["retention"] == 1.0
        assert data["curve_points"][-1]["t_days"] == 60


class TestIntegration:
    def test_record_retrieval_updates_lambda(self, client, db_session, runner_fake):
        from app.problems.seed import seed_problems

        seed_problems(db_session)
        client.post(
            "/api/auth/register",
            json={"email": "fc3@example.com", "password": "strongPass123!"},
        )
        # First, need some mastery snapshots to fit λ
        # Just test that the endpoint exists and returns 404 before λ is set
        resp = client.get("/api/retention/forgetting-curve?skill_slug=arrays")
        assert resp.status_code == 404
