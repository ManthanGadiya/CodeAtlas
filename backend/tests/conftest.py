"""Shared pytest fixtures: isolated database and API client per test."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.ratelimit import login_limiter
from app.db.base import Base
from app.db.session import get_db
from app.main import app


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


@pytest.fixture(autouse=True)
def _reset_login_limiter():
    login_limiter.reset()
    yield
    login_limiter.reset()


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
