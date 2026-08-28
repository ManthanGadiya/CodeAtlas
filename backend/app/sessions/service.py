"""Session lifecycle service."""

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session as DbSession

from app.sessions.models import SESSION_TYPES, Session

# An open session younger than this is reused for consecutive
# executions so a burst of Run → Submit stays in the same session.
# Older open sessions are closed lazily and a new one is created.
SESSION_TTL_MINUTES = 30


def _now_utc() -> datetime:
    return datetime.now(UTC)


def get_open_session(db: DbSession, *, student_id: uuid.UUID) -> Session | None:
    return db.scalar(
        select(Session)
        .where(Session.student_id == student_id, Session.ended_at.is_(None))
        .order_by(Session.started_at.desc())
        .limit(1)
    )


def get_or_create_open_session(
    db: DbSession,
    *,
    student_id: uuid.UUID,
    session_type: str = "practice",
    device_context: dict | None = None,
) -> Session:
    if session_type not in SESSION_TYPES:
        session_type = "practice"
    open_session = get_open_session(db, student_id=student_id)
    if open_session is not None:
        started = open_session.started_at
        if started.tzinfo is None:
            started = started.replace(tzinfo=UTC)
        age = _now_utc() - started
        if age < timedelta(minutes=SESSION_TTL_MINUTES):
            return open_session
        # Stale open session: close it and fall through to create.
        open_session.ended_at = _now_utc()
        db.commit()

    session = Session(
        student_id=student_id,
        session_type=session_type,
        device_context=device_context or {},
    )
    db.add(session)
    db.commit()
    return session


def create_session(
    db: DbSession,
    *,
    student_id: uuid.UUID,
    session_type: str = "practice",
    device_context: dict | None = None,
) -> Session:
    if session_type not in SESSION_TYPES:
        session_type = "practice"
    session = Session(
        student_id=student_id,
        session_type=session_type,
        device_context=device_context or {},
    )
    db.add(session)
    db.commit()
    return session


def end_session(db: DbSession, *, student_id: uuid.UUID, session_id: uuid.UUID) -> Session | None:
    session = db.scalar(
        select(Session).where(Session.id == session_id, Session.student_id == student_id)
    )
    if session is None or session.ended_at is not None:
        return session
    session.ended_at = _now_utc()
    db.commit()
    return session
