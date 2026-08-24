"""Domain services for registration, login, and session lifecycle."""

from datetime import UTC, datetime, timedelta
from functools import lru_cache

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth import security
from app.auth.models import AuthSession
from app.core.config import get_settings
from app.users.models import Student


class AuthError(Exception):
    """Base class for expected authentication failures."""


class AccountAlreadyExists(AuthError):
    pass


class InvalidCredentials(AuthError):
    pass


def count_students(db: Session) -> int:
    return db.scalar(select(func.count()).select_from(Student)) or 0


def register_student(db: Session, email: str, password: str, display_name: str | None) -> Student:
    """Create the first and only student account (single-user product decision)."""
    if count_students(db) > 0:
        raise AccountAlreadyExists(email)

    student = Student(
        email=email.lower(),
        password_hash=security.hash_password(password),
        display_name=display_name,
    )
    db.add(student)
    db.commit()
    return student


@lru_cache(maxsize=1)
def _dummy_password_hash() -> str:
    """Constant-cost verification target for unknown emails.

    Without this, unknown-email logins return ~an Argon2 run faster than
    wrong-password logins, letting callers probe which emails have accounts.
    """
    return security.hash_password("timing-equalizer-dummy-password")


def authenticate(db: Session, email: str, password: str) -> Student:
    student = db.scalar(select(Student).where(Student.email == email.lower()))
    password_hash = student.password_hash if student is not None else _dummy_password_hash()
    password_ok = security.verify_password(password_hash, password)

    # Same error and same timing for unknown email and wrong password.
    if student is None or not password_ok:
        raise InvalidCredentials()

    if security.needs_rehash(student.password_hash):
        student.password_hash = security.hash_password(password)
        db.commit()
    return student


def create_session(db: Session, student: Student) -> tuple[AuthSession, str]:
    raw_token = security.generate_session_token()
    lifetime = timedelta(minutes=get_settings().session_lifetime_minutes)
    session_row = AuthSession(
        student_id=student.id,
        token_hash=security.hash_token(raw_token),
        expires_at=datetime.now(UTC) + lifetime,
    )
    db.add(session_row)
    db.commit()
    return session_row, raw_token


def _as_utc(value: datetime) -> datetime:
    """Normalize DB datetimes to aware UTC.

    PostgreSQL returns timezone-aware values; SQLite (the unit-test driver)
    stores and returns naive values even for timezone=True columns.
    """
    return value if value.tzinfo is not None else value.replace(tzinfo=UTC)


def resolve_session(db: Session, raw_token: str) -> Student | None:
    token_hash = security.hash_token(raw_token)
    session_row = db.scalar(select(AuthSession).where(AuthSession.token_hash == token_hash))
    if session_row is None or session_row.revoked_at is not None:
        return None

    if _as_utc(session_row.expires_at) <= datetime.now(UTC):
        return None

    return db.get(Student, session_row.student_id)


def revoke_session(db: Session, raw_token: str) -> bool:
    token_hash = security.hash_token(raw_token)
    session_row = db.scalar(select(AuthSession).where(AuthSession.token_hash == token_hash))
    if session_row is None or session_row.revoked_at is not None:
        return False

    session_row.revoked_at = datetime.now(UTC)
    db.commit()
    return True
