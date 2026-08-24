"""Request-scoped authentication dependencies."""

from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.auth.service import resolve_session
from app.core.config import get_settings
from app.db.session import get_db
from app.users.models import Student

# Shared dependency annotations (FastAPI's recommended Annotated style).
DbSession = Annotated[Session, Depends(get_db)]


def _cookie_token(request: Request) -> str | None:
    return request.cookies.get(get_settings().session_cookie_name)


def get_current_student(request: Request, db: DbSession) -> Student:
    """Resolve the session cookie to a Student, or answer 401."""
    raw_token = _cookie_token(request)
    if not raw_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    student = resolve_session(db, raw_token)
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired session"
        )
    return student


CurrentUser = Annotated[Student, Depends(get_current_student)]
