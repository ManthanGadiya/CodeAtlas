"""Authentication flow tests: bootstrap, login, session lifecycle, guardrails."""

from fastapi.testclient import TestClient

REGISTER_URL = "/api/auth/register"
LOGIN_URL = "/api/auth/login"
ME_URL = "/api/auth/me"
STATUS_URL = "/api/auth/status"
LOGOUT_URL = "/api/auth/logout"

ACCOUNT = {"email": "student@example.com", "password": "correct-horse-battery"}


def _register(client, email=ACCOUNT["email"], password=ACCOUNT["password"]):
    return client.post(REGISTER_URL, json={"email": email, "password": password})


def test_status_reports_no_account_initially(client):
    response = client.get(STATUS_URL)

    assert response.status_code == 200
    assert response.json() == {"has_account": False}


def test_register_creates_account_and_session(client):
    response = _register(client)

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == ACCOUNT["email"]
    assert "codeatlas_session" in client.cookies

    me = client.get(ME_URL)
    assert me.status_code == 200
    assert me.json()["email"] == ACCOUNT["email"]


def test_register_rejects_second_account(client):
    first = _register(client)
    second = _register(client, email="other@example.com")

    assert first.status_code == 201
    assert second.status_code == 409


def test_register_validates_password_length_and_email(client):
    weak = _register(client, password="short")
    bad_email = client.post(
        REGISTER_URL, json={"email": "not-an-email", "password": "long-enough-pass"}
    )

    assert weak.status_code == 422
    assert bad_email.status_code == 422


def test_login_rejects_wrong_password_without_leaking_information(client):
    _register(client)

    wrong = client.post(LOGIN_URL, json={"email": ACCOUNT["email"], "password": "wrong-password"})
    unknown = client.post(LOGIN_URL, json={"email": "ghost@example.com", "password": "whatever-x"})

    assert wrong.status_code == 401
    assert unknown.status_code == 401
    assert wrong.json()["detail"] == unknown.json()["detail"]


def test_logout_revokes_the_session(client):
    _register(client)
    assert client.get(ME_URL).status_code == 200

    logout = client.post(LOGOUT_URL)
    after = client.get(ME_URL)

    assert logout.status_code == 204
    assert after.status_code == 401


def test_me_requires_authentication(client):
    # A brand-new client shares no cookie jar with `client`.
    fresh = TestClient(client.app)
    response = fresh.get(ME_URL)
    assert response.status_code == 401


def test_status_flips_after_registration(client):
    assert client.get(STATUS_URL).json() == {"has_account": False}
    _register(client)
    assert client.get(STATUS_URL).json() == {"has_account": True}


def test_email_case_is_normalized_for_login(client):
    client.post(
        REGISTER_URL,
        json={"email": "Student@Example.com", "password": ACCOUNT["password"]},
    )

    response = client.post(LOGIN_URL, json=ACCOUNT)  # lowercase email

    assert response.status_code == 200


def test_tampered_session_cookie_is_rejected(client):
    _register(client)
    client.cookies.set("codeatlas_session", "forged-token-value")

    response = client.get(ME_URL)

    assert response.status_code == 401
    client.cookies.clear()


def test_expired_session_is_rejected(db_session, client):
    from datetime import UTC, datetime, timedelta

    from app.auth import service as auth_service

    _register(client)
    raw_token = client.cookies.get("codeatlas_session")
    token_hash = auth_service.security.hash_token(raw_token)
    session_row = db_session.query(auth_service.AuthSession).filter_by(token_hash=token_hash).one()
    session_row.expires_at = datetime.now(UTC) - timedelta(minutes=1)
    db_session.commit()

    response = client.get(ME_URL)

    assert response.status_code == 401


def test_logout_without_cookie_is_idempotent(client):
    response = client.post(LOGOUT_URL)

    assert response.status_code == 204


def test_sixth_login_attempt_within_a_minute_is_rate_limited(client):
    _register(client)
    for _ in range(5):
        client.cookies.clear()
        client.post(LOGIN_URL, json={"email": ACCOUNT["email"], "password": "wrong-pass"})

    sixth = client.post(LOGIN_URL, json=dict(ACCOUNT, password="wrong-pass"))

    assert sixth.status_code == 429
