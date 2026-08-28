"""Session API — create / list / current / end."""

import uuid

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.auth.dependencies import CurrentUser, DbSession
from app.sessions.models import Session
from app.sessions.service import create_session, end_session, get_open_session

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.get("/current")
def get_current_session(db: DbSession, student: CurrentUser):
    session = get_open_session(db, student_id=student.id)
    if session is None:
        return {"session": None}
    return {
        "session": {
            "id": str(session.id),
            "session_type": session.session_type,
            "started_at": session.started_at.isoformat() if session.started_at else None,
            "ended_at": session.ended_at.isoformat() if session.ended_at else None,
            "device_context": session.device_context,
        }
    }


@router.get("")
def list_sessions(db: DbSession, student: CurrentUser):
    rows = db.scalars(
        select(Session)
        .where(Session.student_id == student.id)
        .order_by(Session.started_at.desc())
        .limit(50)
    ).all()
    return {
        "sessions": [
            {
                "id": str(s.id),
                "session_type": s.session_type,
                "started_at": s.started_at.isoformat() if s.started_at else None,
                "ended_at": s.ended_at.isoformat() if s.ended_at else None,
            }
            for s in rows
        ]
    }


@router.post("", status_code=201)
def create_session_endpoint(
    payload: dict | None,
    db: DbSession,
    student: CurrentUser,
):
    body = payload or {}
    session_type = body.get("session_type", "practice")
    device_context = body.get("device_context")
    session = create_session(
        db,
        student_id=student.id,
        session_type=session_type,
        device_context=device_context,
    )
    return {
        "id": str(session.id),
        "session_type": session.session_type,
        "started_at": session.started_at.isoformat() if session.started_at else None,
    }


@router.patch("/{session_id}/end")
def end_session_endpoint(session_id: uuid.UUID, db: DbSession, student: CurrentUser):
    session = end_session(db, student_id=student.id, session_id=session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return {
        "id": str(session.id),
        "ended_at": session.ended_at.isoformat() if session.ended_at else None,
    }
