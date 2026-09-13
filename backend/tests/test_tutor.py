"""Tutoring engine tests — Phase 3.1 (docs/Tutoring_Engine.md)."""

import pytest
from fastapi.testclient import TestClient

from app.problems.seed import seed_problems

SLUG = "two-sum"


@pytest.fixture()
def seeded_slug(db_session):
    seed_problems(db_session)
    return SLUG


def _register(client: TestClient, email="tutor@example.com"):
    resp = client.post("/api/auth/register", json={"email": email, "password": "strongPass123!"})
    assert resp.status_code == 201
    return resp.cookies


def _hint(client: TestClient, slug: str, code=None, hint_level=None):
    body = {"problem_slug": slug}
    if code is not None:
        body["code"] = code
    if hint_level is not None:
        body["hint_level"] = hint_level
    return client.post("/api/tutor/hint", json=body)


def test_hint_requires_auth(client: TestClient):
    resp = client.post("/api/tutor/hint", json={"problem_slug": "two-sum"})
    assert resp.status_code == 401


def test_hint_404_for_unknown_problem(client: TestClient, seeded_slug: str):  # noqa: ARG001
    _register(client)
    resp = _hint(client, "no-such-problem")
    assert resp.status_code == 404


def test_hint_auto_escalates(client: TestClient, seeded_slug: str):
    """First hint is level 1, second auto-escalates to 2 (minimal effective help)."""
    _register(client, email="escalate@example.com")
    r1 = _hint(client, seeded_slug, code="def solve(): pass")
    assert r1.status_code == 200
    assert r1.json()["hint_level"] == 1
    assert "content" in r1.json()
    assert r1.json()["provider"] in ("dummy", "system")

    r2 = _hint(client, seeded_slug)
    assert r2.status_code == 200
    assert r2.json()["hint_level"] == 2
    # Content differs because template pool is mistake-aware (or generic ladder)
    # At least ensure second hint still has content
    assert r2.json()["content"]


def test_hint_explicit_level_honored(client: TestClient, seeded_slug: str):
    _register(client, email="explicit@example.com")
    r = _hint(client, seeded_slug, hint_level=4)
    assert r.status_code == 200
    assert r.json()["hint_level"] == 4
    assert r.json()["intervention"] in (
        "HINT",
        "EXPLANATION",
        "SOCRATIC_QUESTION",
        "CONCEPT_REMINDER",
        "DEBUGGING_GUIDANCE",
    )


def test_hint_invalid_level_422(client: TestClient, seeded_slug: str):
    _register(client, email="invalid@example.com")
    resp = _hint(client, seeded_slug, hint_level=99)
    assert resp.status_code == 422


def test_hint_level_zero_is_silent_observation(client: TestClient, seeded_slug: str):
    _register(client, email="silent@example.com")
    r = _hint(client, seeded_slug, hint_level=0)
    assert r.status_code == 200
    assert r.json()["hint_level"] == 0
    assert "observing silently" in r.json()["content"].lower()


def test_history_requires_auth(client: TestClient):
    resp = client.get("/api/tutor/history")
    assert resp.status_code == 401


def test_history_lists_recent_hints(client: TestClient, seeded_slug: str):
    _register(client, email="history@example.com")
    _hint(client, seeded_slug, hint_level=1)
    _hint(client, seeded_slug, hint_level=2)
    resp = client.get("/api/tutor/history")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert data[0]["hint_level"] == 2  # newest first
    assert data[1]["hint_level"] == 1


def test_history_filter_by_problem(client: TestClient, seeded_slug: str):
    _register(client, email="filter@example.com")
    _hint(client, seeded_slug)
    resp = client.get(f"/api/tutor/history?problem_slug={seeded_slug}")
    assert resp.status_code == 200
    assert all(item["problem_slug"] == seeded_slug for item in resp.json())


def test_tutor_gateway_fallback_is_deterministic(client: TestClient, seeded_slug: str):
    """Without Gemini/Groq keys the gateway must degrade to dummy templates, never 500."""
    _register(client, email="fallback@example.com")
    r = _hint(client, seeded_slug, code="x = 1")
    assert r.status_code == 200
    body = r.json()
    assert body["is_fallback"] is True
    assert body["provider"] == "dummy"
