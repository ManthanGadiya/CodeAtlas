"""Temporal Mastery(t) tests — Level 4.1b (ROADMAP §33, Data_Model §31)."""

from datetime import UTC, datetime, timedelta

from app.problems.seed import seed_problems
from app.unified.history import (
    TREND_DECLINING,
    TREND_IMPROVING,
    TREND_STABLE,
    TREND_STRONGLY_DECLINING,
    TREND_STRONGLY_IMPROVING,
    TREND_UNKNOWN,
    bucket_overall_history,
    classify_trend,
    compute_velocity_from_points,
    downsample,
    parse_days,
    to_mastery_points,
)


class TestPure:
    def test_classify_trend_thresholds(self):
        assert classify_trend(0.06, 3) == TREND_STRONGLY_IMPROVING
        assert classify_trend(0.03, 3) == TREND_IMPROVING
        assert classify_trend(0.0, 3) == TREND_STABLE
        assert classify_trend(-0.03, 3) == TREND_DECLINING
        assert classify_trend(-0.06, 3) == TREND_STRONGLY_DECLINING

    def test_classify_trend_needs_two_points(self):
        assert classify_trend(0.5, 0) == TREND_UNKNOWN
        assert classify_trend(0.5, 1) == TREND_UNKNOWN

    def test_parse_days_clamp(self):
        assert parse_days(None) == 30
        assert parse_days("abc") == 30
        assert parse_days(0) == 1
        assert parse_days(500) == 90
        assert parse_days(7) == 7

    def test_downsample_caps_and_keeps_last(self):
        pts = [{"t": f"{i}", "mastery": 0.5} for i in range(250)]
        out = downsample(pts, 100)
        assert len(out) <= 100
        assert out[-1] == pts[-1]
        assert out[0] == pts[0]

    def test_downsample_small_unchanged(self):
        pts = [{"t": f"{i}", "mastery": 0.5} for i in range(10)]
        assert downsample(pts, 100) == pts

    def test_to_mastery_points_passthrough(self):
        class S:
            new_mastery = 0.42
            confidence = None
            reason = "submit:two-sum"

            def __init__(self, t):
                self.created_at = t

        now = datetime(2026, 9, 22, tzinfo=UTC)
        pts = to_mastery_points([S(now)])
        assert pts[0]["mastery"] == 0.42
        assert pts[0]["confidence"] is None
        assert pts[0]["reason"] == "submit:two-sum"

    def test_velocity_and_bucket(self):
        assert compute_velocity_from_points([]) == 0.0
        assert compute_velocity_from_points([0.3]) == 0.0
        v = compute_velocity_from_points([0.3, 0.5, 0.7])
        assert v > 0
        merged = bucket_overall_history(
            {
                "a": [{"t": "2026-09-20T00:00:00Z", "mastery": 0.4}],
                "b": [{"t": "2026-09-20T00:00:00Z", "mastery": 0.6}],
            }
        )
        assert merged[0]["overall_mastery"] == 0.5


class TestTemporalAPI:
    def test_requires_auth(self, client):
        assert client.get("/api/learner/mastery-history?skill_slug=arrays").status_code == 401
        assert client.get("/api/learner/unified-history").status_code == 401

    def test_empty_before_evidence(self, client, db_session):
        seed_problems(db_session)
        client.post(
            "/api/auth/register",
            json={"email": "tmp1@example.com", "password": "strongPass123!"},
        )
        resp = client.get("/api/learner/mastery-history?skill_slug=arrays&days=30")
        assert resp.status_code == 200
        assert resp.json()["points"] == []
        assert resp.json()["trend"] == TREND_UNKNOWN

    def test_empty_with_seed(self, client, db_session):
        seed_problems(db_session)
        client.post(
            "/api/auth/register",
            json={"email": "tmp2@example.com", "password": "strongPass123!"},
        )
        resp = client.get("/api/learner/mastery-history?skill_slug=arrays&days=30")
        assert resp.status_code == 200
        data = resp.json()
        assert data["points"] == []
        assert data["trend"] == TREND_UNKNOWN
        assert data["velocity"] == 0.0
        resp2 = client.get("/api/learner/unified-history?days=30")
        assert resp2.status_code == 200
        assert resp2.json()["points"] == []

    def test_happy_path_per_skill(self, client, db_session, runner_fake):
        seed_problems(db_session)
        client.post(
            "/api/auth/register",
            json={"email": "tmp3@example.com", "password": "strongPass123!"},
        )
        client.post(
            "/api/problems/two-sum/submit",
            json={"code": "def two_sum(nums, target): return [0,1]"},
        )
        client.post(
            "/api/problems/two-sum/submit",
            json={"code": "def two_sum(nums, target): return [0,1]"},
        )
        # two-sum links to arrays + other skills; arrays must have >=2 points
        resp = client.get("/api/learner/mastery-history?skill_slug=arrays&days=30")
        assert resp.status_code == 200
        data = resp.json()
        assert data["skill_slug"] == "arrays"
        assert len(data["points"]) >= 2
        assert set(data["points"][0].keys()) == {"t", "mastery", "confidence", "reason"}
        # ascending by event timestamp
        ts = [p["t"] for p in data["points"]]
        assert ts == sorted(ts)
        assert data["trend"] in (
            TREND_STRONGLY_IMPROVING,
            TREND_IMPROVING,
            TREND_STABLE,
            TREND_DECLINING,
            TREND_STRONGLY_DECLINING,
            TREND_UNKNOWN,
        )

    def test_invalid_skill_404(self, client):
        client.post(
            "/api/auth/register",
            json={"email": "tmp4@example.com", "password": "strongPass123!"},
        )
        resp = client.get("/api/learner/mastery-history?skill_slug=does-not-exist")
        assert resp.status_code == 404
        assert "does-not-exist" in resp.json()["detail"]

    def test_days_clamp(self, client, db_session):
        seed_problems(db_session)
        client.post(
            "/api/auth/register",
            json={"email": "tmp5@example.com", "password": "strongPass123!"},
        )
        assert (
            client.get("/api/learner/mastery-history?skill_slug=arrays&days=9999").json()["days"]
            == 90
        )
        assert (
            client.get("/api/learner/mastery-history?skill_slug=arrays&days=0").json()["days"] == 1
        )
        assert (
            client.get("/api/learner/mastery-history?skill_slug=arrays&days=abc").json()["days"]
            == 30
        )

    def test_ordering_by_event_timestamp(self, client, db_session, runner_fake):
        from sqlalchemy import select

        from app.problems.models import Skill
        from app.skills.models import MasterySnapshot
        from app.users.models import Student

        seed_problems(db_session)
        client.post(
            "/api/auth/register",
            json={"email": "tmp6@example.com", "password": "strongPass123!"},
        )
        student = db_session.scalar(select(Student).where(Student.email == "tmp6@example.com"))
        skill = db_session.scalar(select(Skill).where(Skill.slug == "arrays"))
        now = datetime.now(UTC).replace(tzinfo=None)
        # Insert out-of-order created_at deliberately
        for i, delta in [(0, 2), (1, 0), (2, 1)]:
            _ = i
            db_session.add(
                MasterySnapshot(
                    student_id=student.id,
                    skill_id=skill.id,
                    previous_mastery=0.3,
                    new_mastery=0.3 + delta * 0.05,
                    confidence=0.5,
                    reason=f"manual-{delta}",
                    model_version="test",
                    created_at=now - timedelta(days=delta),
                )
            )
        db_session.commit()
        resp = client.get("/api/learner/mastery-history?skill_slug=arrays&days=30")
        assert resp.status_code == 200
        ts = [p["t"] for p in resp.json()["points"]]
        assert ts == sorted(ts)

    def test_overall_history(self, client, db_session, runner_fake):
        seed_problems(db_session)
        client.post(
            "/api/auth/register",
            json={"email": "tmp7@example.com", "password": "strongPass123!"},
        )
        client.post(
            "/api/problems/two-sum/submit",
            json={"code": "def two_sum(nums, target): return [0,1]"},
        )
        client.post(
            "/api/problems/valid-palindrome/submit",
            json={"code": "def is_palindrome(s): return True"},
        )
        resp = client.get("/api/learner/unified-history?days=30")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["points"]) >= 1
        for pt in data["points"]:
            assert 0.02 <= pt["overall_mastery"] <= 0.98
        ts = [p["t"] for p in data["points"]]
        assert ts == sorted(ts)

    def test_single_snapshot_unknown(self, client, db_session, runner_fake):
        from sqlalchemy import select

        from app.problems.models import Skill
        from app.skills.models import MasterySnapshot
        from app.users.models import Student

        seed_problems(db_session)
        client.post(
            "/api/auth/register",
            json={"email": "tmp8@example.com", "password": "strongPass123!"},
        )
        student = db_session.scalar(select(Student).where(Student.email == "tmp8@example.com"))
        skill = db_session.scalar(select(Skill).where(Skill.slug == "arrays"))
        db_session.add(
            MasterySnapshot(
                student_id=student.id,
                skill_id=skill.id,
                previous_mastery=None,
                new_mastery=0.35,
                confidence=0.2,
                reason="single evidence",
                model_version="test",
            )
        )
        db_session.commit()
        resp = client.get("/api/learner/mastery-history?skill_slug=arrays&days=30")
        assert resp.status_code == 200
        assert len(resp.json()["points"]) == 1
        assert resp.json()["trend"] == TREND_UNKNOWN

    def test_cross_student_isolation(self, client, db_session, runner_fake):
        # Single-user bootstrap allows one account via API, so isolation is
        # verified at the service layer: history for student B (created
        # directly in DB) must be empty while student A has evidence.

        from sqlalchemy import select

        from app.problems.models import Skill
        from app.unified.service import get_mastery_history, get_overall_history
        from app.users.models import Student

        seed_problems(db_session)
        client.post(
            "/api/auth/register",
            json={"email": "iso-a@example.com", "password": "strongPass123!"},
        )
        client.post(
            "/api/problems/two-sum/submit",
            json={"code": "def two_sum(nums, target): return [0,1]"},
        )
        resp_a = client.get("/api/learner/mastery-history?skill_slug=arrays&days=30")
        assert resp_a.status_code == 200
        assert len(resp_a.json()["points"]) >= 1
        # Second student created directly (API bootstrap forbids second register).
        student_b = Student(
            email="iso-b@example.com",
            password_hash="dummy",
            display_name=None,
        )
        db_session.add(student_b)
        db_session.commit()
        skill = db_session.scalar(select(Skill).where(Skill.slug == "arrays"))
        hist_b = get_mastery_history(db_session, student_b.id, skill.id, days=30)
        assert hist_b["points"] == []
        assert hist_b["trend"] == TREND_UNKNOWN
        overall_b = get_overall_history(db_session, student_b.id, days=30)
        assert overall_b["points"] == []

    def test_downsample_cap_via_api(self, client, db_session):
        from sqlalchemy import select

        from app.problems.models import Skill
        from app.skills.models import MasterySnapshot
        from app.users.models import Student

        seed_problems(db_session)
        client.post(
            "/api/auth/register",
            json={"email": "tmp9@example.com", "password": "strongPass123!"},
        )
        student = db_session.scalar(select(Student).where(Student.email == "tmp9@example.com"))
        skill = db_session.scalar(select(Skill).where(Skill.slug == "arrays"))
        for i in range(150):
            db_session.add(
                MasterySnapshot(
                    student_id=student.id,
                    skill_id=skill.id,
                    previous_mastery=0.3,
                    new_mastery=0.3 + (i % 10) * 0.01,
                    confidence=0.5,
                    reason=f"bulk-{i}",
                    model_version="test",
                )
            )
        db_session.commit()
        resp = client.get("/api/learner/mastery-history?skill_slug=arrays&days=90")
        assert resp.status_code == 200
        pts = resp.json()["points"]
        assert len(pts) <= 100
        assert pts[-1]["reason"] == "bulk-149"
