"""Authentication endpoints."""

from fastapi import APIRouter, HTTPException, Request, Response, status

from app.auth import schemas, service
from app.auth.dependencies import CurrentUser, DbSession
from app.core.config import get_settings
from app.core.ratelimit import login_limiter
from app.users.models import Student

router = APIRouter(prefix="/auth", tags=["auth"])


def _set_session_cookie(response: Response, raw_token: str) -> None:
    settings = get_settings()
    response.set_cookie(
        key=settings.session_cookie_name,
        value=raw_token,
        max_age=settings.session_lifetime_minutes * 60,
        httponly=True,
        samesite="lax",
        # Secure cookies on localhost HTTP would never be sent back.
        secure=settings.environment == "production",
        path="/",
    )


@router.get("/status", response_model=schemas.AccountStatus)
def account_status(db: DbSession) -> schemas.AccountStatus:
    """Public endpoint telling the frontend whether an account exists yet."""
    return schemas.AccountStatus(has_account=service.count_students(db) > 0)


@router.post("/register", response_model=schemas.StudentOut, status_code=status.HTTP_201_CREATED)
def register(payload: schemas.RegisterRequest, response: Response, db: DbSession):
    """Bootstrap the single student account. Returns 409 once one exists."""
    try:
        student = service.register_student(
            db, payload.email, payload.password, payload.display_name
        )
    except service.AccountAlreadyExists as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account already exists. Sign in instead.",
        ) from exc

    _, raw_token = service.create_session(db, student)
    _set_session_cookie(response, raw_token)
    return student


@router.post("/login", response_model=schemas.StudentOut)
def login(payload: schemas.LoginRequest, request: Request, response: Response, db: DbSession):
    client_ip = request.client.host if request.client else "unknown"
    if not login_limiter.allow(f"login:{client_ip}"):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Try again in a minute.",
        )

    try:
        student = service.authenticate(db, payload.email, payload.password)
    except service.InvalidCredentials:
        # Identical response for unknown email and wrong password.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        ) from None

    _, raw_token = service.create_session(db, student)
    _set_session_cookie(response, raw_token)
    return student


@router.get("/me", response_model=schemas.StudentOut)
def me(student: CurrentUser) -> Student:
    return student


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request, response: Response, db: DbSession) -> None:
    settings = get_settings()
    raw_token = request.cookies.get(settings.session_cookie_name)
    if raw_token:
        service.revoke_session(db, raw_token)

    response.delete_cookie(key=settings.session_cookie_name, path="/")
