"""Tests for system endpoints."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_healthz_returns_ok():
    response = client.get("/api/healthz")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "CodeAtlas"


def test_healthz_reports_identity_fields():
    response = client.get("/api/healthz")

    body = response.json()
    assert body["version"]
    assert body["environment"]
