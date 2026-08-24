"""Database engine and session management (SQLAlchemy 2.x, synchronous).

Synchronous sessions keep the first milestones simple and easy to test;
the execution and analysis paths that need concurrency will be evaluated
when they arrive rather than assumed now.
"""

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings


def _create_engine():
    settings = get_settings()
    if settings.database_url.startswith("sqlite"):
        return create_engine(settings.database_url, connect_args={"check_same_thread": False})
    # Short connect timeout: an unreachable database should fail in ~3s with a
    # clean 503, not hang each request for the driver's default (~30s).
    return create_engine(
        settings.database_url,
        pool_pre_ping=True,
        connect_args={"connect_timeout": 3},
    )


engine = _create_engine()

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Iterator[Session]:
    """FastAPI dependency yielding a request-scoped database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
