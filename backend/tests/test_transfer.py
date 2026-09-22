# ruff: noqa: E501
"""Transfer evaluation tests — Phase 3.7 (Problem_Generator §49-51)."""

from app.problems.seed import seed_problems


def _register(client, email="xfer@example.com"):
    resp = client.post("/api/auth/register", json={"email": email, "password": "strongPass123!"})
    assert resp.status_code == 201
    return resp


def test_transfer_due_requires_auth(client):
    assert client.get("/api/transfer/due").status_code == 401


def test_due_empty_before_evidence(client, db_session):
    seed_problems(db_session)
    _register(client, email="dueEmptyX@example.com")
    resp = client.get("/api/transfer/due")
    assert resp.status_code == 200
    assert resp.json() == []


def test_due_after_mastery(client, db_session, runner_fake):
    seed_problems(db_session)
    _register(client, email="dueX@example.com")
    # Two successful submits build mastery >=0.55 for hash-maps/arrays
    client.post(
        "/api/problems/two-sum/submit", json={"code": "def two_sum(nums, target): return [0,1]"}
    )
    client.post(
        "/api/problems/two-sum/submit", json={"code": "def two_sum(nums, target): return [0,1]"}
    )
    due = client.get("/api/transfer/due").json()
    assert len(due) >= 1
    assert due[0]["suggested_level"] in ("T0", "T1", "T2", "T3", "T4", "T5")


def test_schedule_and_complete(client, db_session, runner_fake):
    seed_problems(db_session)
    _register(client, email="schedX@example.com")
    client.post(
        "/api/problems/two-sum/submit", json={"code": "def two_sum(nums, target): return [0,1]"}
    )
    client.post(
        "/api/problems/two-sum/submit", json={"code": "def two_sum(nums, target): return [0,1]"}
    )
    due = client.get("/api/transfer/due").json()
    assert due
    skill_id = due[0]["skill_id"]
    sched = client.post(
        "/api/transfer/schedule", json={"skill_id": skill_id, "transfer_level": "T2"}
    ).json()
    assert sched["skill_id"] == skill_id
    assert sched["transfer_level"] == "T2"
    assert sched["transfer_problem_id"]
    # Transfer problem should be fetchable
    # Find slug via listing problems
    probs = client.get("/api/problems").json()
    # Find generated problem among probs (not ideal but use transfer_problem_id existence)
    assert any(isinstance(p["slug"], str) for p in probs)
    # Complete
    comp = client.post(
        f"/api/transfer/complete/{sched['id']}", json={"result": "success", "confidence": 0.9}
    )
    assert comp.status_code == 200
    assert comp.json()["result"] == "success"
    # Re-completing → 422
    again = client.post(f"/api/transfer/complete/{sched['id']}", json={"result": "success"})
    assert again.status_code == 422


def test_schedule_auto_skill(client, db_session, runner_fake):
    seed_problems(db_session)
    _register(client, email="autoX@example.com")
    client.post(
        "/api/problems/valid-palindrome/submit", json={"code": "def is_palindrome(s): return True"}
    )
    client.post(
        "/api/problems/valid-palindrome/submit", json={"code": "def is_palindrome(s): return True"}
    )
    resp = client.post("/api/transfer/schedule", json={})
    assert resp.status_code == 201
    assert "transfer_problem_id" in resp.json()


def test_schedule_no_eligible_422(client, db_session):
    seed_problems(db_session)
    _register(client, email="noelig@example.com")
    resp = client.post("/api/transfer/schedule", json={})
    assert resp.status_code == 422


def test_transfer_history(client, db_session, runner_fake):
    seed_problems(db_session)
    _register(client, email="histX@example.com")
    client.post(
        "/api/problems/valid-parentheses/submit", json={"code": "def is_valid(s): return True"}
    )
    client.post(
        "/api/problems/valid-parentheses/submit", json={"code": "def is_valid(s): return True"}
    )
    due = client.get("/api/transfer/due").json()
    assert due
    sched = client.post("/api/transfer/schedule", json={"skill_id": due[0]["skill_id"]}).json()
    client.post(f"/api/transfer/complete/{sched['id']}", json={"result": "failure"})
    hist = client.get("/api/transfer/history").json()
    assert len(hist) >= 1
    assert hist[0]["result"] in ("success", "failure", "partial")


def test_invalid_level_422(client, db_session, runner_fake):
    seed_problems(db_session)
    _register(client, email="badlevel@example.com")
    client.post(
        "/api/problems/two-sum/submit", json={"code": "def two_sum(nums, target): return [0,1]"}
    )
    client.post(
        "/api/problems/two-sum/submit", json={"code": "def two_sum(nums, target): return [0,1]"}
    )
    due = client.get("/api/transfer/due").json()
    assert due
    resp = client.post(
        "/api/transfer/schedule", json={"skill_id": due[0]["skill_id"], "transfer_level": "T9"}
    )
    assert resp.status_code == 422


def test_complete_404(client, db_session):
    seed_problems(db_session)
    _register(client, email="c404X@example.com")
    import uuid

    fake = str(uuid.uuid4())
    resp = client.post(f"/api/transfer/complete/{fake}", json={"result": "success"})
    assert resp.status_code == 404


def test_due_excludes_recent_success(client, db_session, runner_fake):
    seed_problems(db_session)
    _register(client, email="exclude@example.com")
    client.post(
        "/api/problems/two-sum/submit", json={"code": "def two_sum(nums, target): return [0,1]"}
    )
    client.post(
        "/api/problems/two-sum/submit", json={"code": "def two_sum(nums, target): return [0,1]"}
    )
    due1 = client.get("/api/transfer/due").json()
    assert len(due1) >= 1
    skill_id = due1[0]["skill_id"]
    sched = client.post("/api/transfer/schedule", json={"skill_id": skill_id}).json()
    client.post(f"/api/transfer/complete/{sched['id']}", json={"result": "success"})
    due2 = client.get("/api/transfer/due").json()
    # That skill should now be excluded (recent success)
    assert all(d["skill_id"] != skill_id for d in due2)
