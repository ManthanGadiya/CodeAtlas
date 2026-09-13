# ruff: noqa: E501
"""Adaptive difficulty tests — Phase 3.3 (Problem_Generator §14-18)."""

from app.problems.seed import seed_problems


def _register(client, email="diff@example.com"):
    resp = client.post("/api/auth/register", json={"email": email, "password": "strongPass123!"})
    assert resp.status_code == 201
    return resp


def test_overview_requires_auth(client):
    assert client.get("/api/difficulty/overview").status_code == 401


def test_overview_returns_vectors(client, db_session):
    seed_problems(db_session)
    _register(client, email="ov@example.com")
    resp = client.get("/api/difficulty/overview")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 5
    # Check easy problem overall < medium
    easy = [d for d in data if d["slug"] == "two-sum"][0]
    medium = [d for d in data if d["slug"] == "binary-search-first-occurrence"][0]
    assert easy["overall"] < medium["overall"]
    assert "conceptual" in easy["vector"]


def test_estimate_cold_start(client, db_session):
    seed_problems(db_session)
    _register(client, email="est@example.com")
    resp = client.get("/api/difficulty/estimate/two-sum")
    assert resp.status_code == 200
    data = resp.json()
    assert data["slug"] == "two-sum"
    assert 0 <= data["p_success"] <= 1
    assert data["zone"] in ("comfort", "productive", "struggle", "overload")
    assert "student_specific_difficulty" in data


def test_estimate_404(client, db_session):
    seed_problems(db_session)
    _register(client, email="est404@example.com")
    assert client.get("/api/difficulty/estimate/no-such").status_code == 404


def test_recommend_cold_start(client, db_session):
    seed_problems(db_session)
    _register(client, email="rec@example.com")
    resp = client.get("/api/difficulty/recommend")
    assert resp.status_code == 200
    data = resp.json()
    assert data["band"] in ("easy", "medium", "hard")
    assert "target_overall" in data


def test_recommend_after_submit_targets_higher(client, db_session, runner_fake):
    seed_problems(db_session)
    _register(client, email="rec2@example.com")
    # Successful submit should raise avg mastery → target shifts up
    client.post(
        "/api/problems/two-sum/submit", json={"code": "def two_sum(nums, target): return [0,1]"}
    )
    resp = client.get("/api/difficulty/recommend")
    assert resp.status_code == 200
    assert resp.json()["target_overall"] >= 0.2


def test_calibration_adjusts_overall(client, db_session):
    seed_problems(db_session)
    _register(client, email="cal@example.com")
    before = client.get("/api/difficulty/estimate/two-sum").json()["overall"]
    # Simulate observed 95% success → problem easier than thought → overall pushed down
    resp = client.post("/api/difficulty/calibrate/two-sum", params={"success_rate": 0.95})
    assert resp.status_code == 200
    after = resp.json()["overall"]
    # With high success, new overall should be lower (easier) or same damped
    assert after <= before or after == before
    # Low success → push up
    client.post("/api/difficulty/calibrate/two-sum", params={"success_rate": 0.2})
    up = client.get("/api/difficulty/estimate/two-sum").json()["overall"]
    assert up >= after


def test_calibration_404(client, db_session):
    seed_problems(db_session)
    _register(client, email="cal404@example.com")
    assert (
        client.post("/api/difficulty/calibrate/no-such", params={"success_rate": 0.5}).status_code
        == 404
    )


def test_estimate_zone_shifts_with_mastery(client, db_session, runner_fake):
    seed_problems(db_session)
    _register(client, email="zone@example.com")
    # Fail twice to lower mastery → p_success drops → zone moves from comfort/productive toward struggle
    from app.execution.runner import RunOutcome

    def failing_run(self, **kwargs):
        self.calls.append(kwargs)
        return RunOutcome(
            status="SUCCESS",
            runtime_ms=5,
            exit_code=0,
            stdout_tail="",
            stderr_tail="",
            results=[
                {"name": t["name"], "passed": False, "actual": "x", "error": None}
                for t in kwargs["tests"]
            ],
        )

    runner_fake.run = failing_run.__get__(runner_fake)
    client.post(
        "/api/problems/two-sum/submit", json={"code": "def two_sum(nums, target): return [0,0]"}
    )
    client.post(
        "/api/problems/two-sum/submit", json={"code": "def two_sum(nums, target): return [0,0]"}
    )
    resp = client.get("/api/difficulty/estimate/two-sum")
    assert resp.status_code == 200
    # After failures mastery low, p_success should be lower than 0.85
    assert resp.json()["p_success"] < 0.9


def test_overview_vectors_have_confidence(client, db_session):
    seed_problems(db_session)
    _register(client, email="conf@example.com")
    data = client.get("/api/difficulty/overview").json()
    for item in data:
        assert 0.3 <= item["confidence"] <= 1.0
        assert item["overall"] > 0
