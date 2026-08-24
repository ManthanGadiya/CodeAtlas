"""Problem catalog tests: auth guarding, listing, detail, hidden-test exclusion."""

import pytest

from app.problems.seed import seed_problems

PROBLEMS_URL = "/api/problems"


@pytest.fixture()
def authed_client(client):
    client.post(
        "/api/auth/register",
        json={"email": "student@example.com", "password": "correct-horse-battery"},
    )
    return client


def test_listing_requires_authentication(client):
    response = client.get(PROBLEMS_URL)

    assert response.status_code == 401


def test_detail_requires_authentication(client):
    response = client.get(f"{PROBLEMS_URL}/two-sum")

    assert response.status_code == 401


DETAIL_KEYS = {
    "slug",
    "title",
    "difficulty",
    "language",
    "estimated_minutes",
    "description",
    "starter_code",
    "function_name",
    "skills",
    "examples",
}


def test_seeded_problems_are_listed(authed_client, db_session):
    seed_problems(db_session)

    response = authed_client.get(PROBLEMS_URL)

    assert response.status_code == 200
    problems = {p["slug"]: p for p in response.json()}
    assert len(problems) == 5
    assert problems["two-sum"]["difficulty"] == "easy"
    assert problems["binary-search-first-occurrence"]["title"].startswith("Binary Search")


def test_detail_returns_statement_and_visible_examples_only(authed_client, db_session):
    seed_problems(db_session)

    response = authed_client.get(f"{PROBLEMS_URL}/binary-search-first-occurrence")

    assert response.status_code == 200
    body = response.json()
    assert body["function_name"] == "first_occurrence"
    assert "sorted" in body["description"]
    assert set(body["skills"]) >= {"binary-search", "boundary-handling"}
    # 3 visible examples; the 3 hidden edge/boundary cases must not leak.
    names = [example["name"] for example in body["examples"]]
    assert names == ["simple-present", "duplicates-first-index", "absent"]
    # Leakage guards: exact schema shape, no hidden-case names anywhere in
    # the raw payload, and no internal fields (visibility/test_type) exposed.
    assert set(body.keys()) == DETAIL_KEYS
    assert all(
        set(example.keys()) == {"name", "input_args", "expected_output"}
        for example in body["examples"]
    )
    assert "empty-array" not in response.text
    assert "all-duplicates" not in response.text
    assert "target-at-ends" not in response.text


def test_detail_404_for_unknown_slug(authed_client):
    response = authed_client.get(f"{PROBLEMS_URL}/does-not-exist")

    assert response.status_code == 404


def test_seeding_is_idempotent(db_session):
    first = seed_problems(db_session)
    second = seed_problems(db_session)

    assert first == 5
    assert second == 0


def test_reseeding_refreshes_test_case_content(db_session):
    """Content fixes to seed data must propagate on re-run."""
    seed_problems(db_session)

    from app.problems import models as problem_models

    stale = (
        db_session.query(problem_models.TestCase)
        .filter_by(name="large-input", visibility="hidden")
        .one()
    )
    stale.expected_output = [0, 0]
    db_session.commit()

    created = seed_problems(db_session)

    assert created == 0
    refreshed = (
        db_session.query(problem_models.TestCase)
        .filter_by(name="large-input", visibility="hidden")
        .one()
    )
    assert refreshed.expected_output == [98, 99]
