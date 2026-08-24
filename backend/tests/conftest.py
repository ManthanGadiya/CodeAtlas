"""Shared pytest fixtures: isolated database, API client, fake sandbox runner."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.ratelimit import execution_limiter, login_limiter
from app.db.base import Base
from app.db.session import get_db
from app.execution.runner import RunOutcome, get_runner
from app.main import app


class FakeRunner:
    """Stand-in for DockerPythonRunner recording what it was asked to run."""

    def __init__(
        self,
        *,
        status: str = "SUCCESS",
        runtime_ms: int = 12,
        results: list[dict] | None = None,
        load_error: dict | None = None,
        error: Exception | None = None,
    ) -> None:
        self.status = status
        self.runtime_ms = runtime_ms
        self.results = results
        self.load_error = load_error
        self.error = error
        self.calls: list[dict] = []

    def run(self, **kwargs) -> RunOutcome:
        self.calls.append(kwargs)
        if self.error is not None:
            raise self.error

        results = self.results
        if results is None and self.load_error is None:
            results = [
                {"name": test["name"], "passed": True, "actual": None, "error": None}
                for test in kwargs["tests"]
            ]
        return RunOutcome(
            status=self.status,
            runtime_ms=self.runtime_ms,
            exit_code=0,
            stdout_tail="",
            stderr_tail="",
            results=results or [],
            load_error=self.load_error,
        )


@pytest.fixture(autouse=True)
def _reset_limiters():
    login_limiter.reset()
    execution_limiter.reset()
    yield
    login_limiter.reset()
    execution_limiter.reset()


@pytest.fixture()
def db_engine():
    """Fresh in-memory SQLite database shared by all connections (StaticPool)."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture()
def db_session(db_engine):
    """A plain session for arranging test state directly."""
    factory = sessionmaker(bind=db_engine, autoflush=False, expire_on_commit=False)
    db = factory()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(db_engine):
    """TestClient wired to the shared in-memory database via dependency override."""
    TestingSession = sessionmaker(bind=db_engine, autoflush=False, expire_on_commit=False)

    def _override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def runner_fake(client):
    """Replace the Docker runner dependency with a controllable fake."""
    fake = FakeRunner()
    app.dependency_overrides[get_runner] = lambda: fake
    return fake
