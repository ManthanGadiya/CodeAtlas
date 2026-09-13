# ruff: noqa: E501
"""Retrieval practice tests — Phase 3.5 (Forgetting §20-34)."""

from app.problems.seed import seed_problems


def _register(client, email="retr@example.com"):
    resp = client.post("/api/auth/register", json={"email": email, "password": "strongPass123!"})
    assert resp.status_code == 201
    return resp


def test_due_requires_auth(client):
    assert client.get("/api/retrieval/due").status_code == 401


def test_due_empty_before_evidence(client, db_session):
    seed_problems(db_session)
    _register(client, email="dueEmpty@example.com")
    resp = client.get("/api/retrieval/due")
    assert resp.status_code == 200
    # No skills yet → empty due queue (honest, not fabricated)
    assert resp.json() == []


def test_schedule_and_complete_success(client, db_session, runner_fake):
    seed_problems(db_session)
    _register(client, email="sched@example.com")
    client.post(
        "/api/problems/two-sum/submit", json={"code": "def two_sum(nums, target): return [0,1]"}
    )
    # There should now be due/weak items (interleaved 2)
    due = client.get("/api/retrieval/due").json()
    assert len(due) >= 1
    # Schedule retrieval for most due
    resp = client.post("/api/retrieval/schedule", json={})
    assert resp.status_code == 201, resp.text
    sid = resp.json()["id"]
    assert resp.json()["status"] == "pending"
    assert resp.json()["ladder_level"] in (
        "recognition",
        "explain",
        "partial",
        "recall",
        "application",
        "transfer",
    )
    # Complete successfully
    comp = client.post(
        f"/api/retrieval/complete/{sid}", json={"result": "success", "confidence": 0.8}
    )
    assert comp.status_code == 200
    assert comp.json()["result"] == "success"
    # Completing same schedule again → 422
    again = client.post(f"/api/retrieval/complete/{sid}", json={"result": "success"})
    assert again.status_code == 422
    # History should contain completed
    hist = client.get("/api/retrieval/history").json()
    assert any(h["id"] == sid and h["result"] == "success" for h in hist)
    # Auto-scheduled next pending
    pend = client.get("/api/retrieval/pending-count").json()
    assert pend["pending"] >= 1


def test_schedule_explicit_skill(client, db_session, runner_fake):
    seed_problems(db_session)
    _register(client, email="explicit@example.com")
    client.post(
        "/api/problems/two-sum/submit", json={"code": "def two_sum(nums, target): return [0,1]"}
    )
    # Fetch a skill_id from retention overview
    ov = client.get("/api/retention/overview").json()
    assert len(ov) >= 1
    skill_id = ov[0]["skill_id"]
    resp = client.post("/api/retrieval/schedule", json={"skill_id": skill_id})
    assert resp.status_code == 201
    assert resp.json()["skill_id"] == skill_id


def test_complete_failure_decreases_stability(client, db_session, runner_fake):
    seed_problems(db_session)
    _register(client, email="failRet@example.com")
    client.post(
        "/api/problems/two-sum/submit", json={"code": "def two_sum(nums, target): return [0,1]"}
    )
    sched = client.post("/api/retrieval/schedule", json={}).json()
    before = client.get("/api/retention/overview").json()
    before_stab = {r["skill_id"]: r["stability"] for r in before}[sched["skill_id"]]
    # Fail retrieval
    client.post(f"/api/retrieval/complete/{sched['id']}", json={"result": "failure"})
    after = client.get("/api/retention/overview").json()
    after_stab = {r["skill_id"]: r["stability"] for r in after}[sched["skill_id"]]
    assert after_stab <= before_stab


def test_complete_partial(client, db_session, runner_fake):
    seed_problems(db_session)
    _register(client, email="partial@example.com")
    client.post(
        "/api/problems/valid-palindrome/submit", json={"code": "def is_palindrome(s): return True"}
    )
    sched = client.post("/api/retrieval/schedule", json={}).json()
    comp = client.post(
        f"/api/retrieval/complete/{sched['id']}", json={"result": "partial", "confidence": 0.5}
    )
    assert comp.status_code == 200
    assert comp.json()["result"] == "partial"


def test_history_and_pending_count(client, db_session, runner_fake):
    seed_problems(db_session)
    _register(client, email="hist@example.com")
    client.post(
        "/api/problems/valid-parentheses/submit", json={"code": "def is_valid(s): return True"}
    )
    s1 = client.post("/api/retrieval/schedule", json={}).json()
    client.post("/api/retrieval/schedule", json={}).json()
    hist = client.get("/api/retrieval/history").json()
    assert len(hist) >= 2
    pend = client.get("/api/retrieval/pending-count").json()
    assert pend["pending"] >= 2
    client.post(f"/api/retrieval/complete/{s1['id']}", json={"result": "success"})
    pend2 = client.get("/api/retrieval/pending-count").json()
    # One completed, but auto-next adds one, so pending may stay >=2 (allow >=1)
    assert pend2["pending"] >= 1


def test_schedule_no_skill_422(client, db_session):
    seed_problems(db_session)
    _register(client, email="noskill@example.com")
    # No evidence → due_queue empty → schedule without skill should 422
    resp = client.post("/api/retrieval/schedule", json={})
    assert resp.status_code == 422


def test_complete_invalid_result(client, db_session, runner_fake):
    seed_problems(db_session)
    _register(client, email="badresult@example.com")
    client.post(
        "/api/problems/two-sum/submit", json={"code": "def two_sum(nums, target): return [0,1]"}
    )
    sched = client.post("/api/retrieval/schedule", json={}).json()
    resp = client.post(f"/api/retrieval/complete/{sched['id']}", json={"result": "bogus"})
    assert resp.status_code == 422


def test_complete_404(client, db_session, runner_fake):
    seed_problems(db_session)
    _register(client, email="c404@example.com")
    import uuid

    fake = str(uuid.uuid4())
    resp = client.post(f"/api/retrieval/complete/{fake}", json={"result": "success"})
    assert resp.status_code == 404 or resp.status_code == 422
