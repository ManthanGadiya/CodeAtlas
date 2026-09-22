"""CodeAtlas FastAPI application factory."""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.exc import OperationalError, ProgrammingError

from app.analytics.routes import router as analytics_router
from app.api.routes import health
from app.auth.routes import router as auth_router
from app.core.config import get_settings
from app.curriculum.routes import router as curriculum_router
from app.difficulty.routes import router as difficulty_router
from app.events.routes import router as events_router
from app.execution.routes import router as execution_router
from app.generator.routes import router as generator_router
from app.problems.routes import router as problems_router
from app.retention.routes import router as retention_router
from app.retrieval.routes import router as retrieval_router
from app.sessions.routes import router as sessions_router
from app.transfer.routes import router as transfer_router
from app.tutor.routes import router as tutor_router


def create_app() -> FastAPI:
    settings = get_settings()
    logging.basicConfig(level=settings.log_level.upper())

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Bring schema up to date before seeding. Without this a stale
        # checkout (e.g. after pulling Level-3 migrations) boots with
        # 500s like "column problems.fingerprint does not exist" /
        # "relation retention_states does not exist" until the operator
        # remembers `alembic upgrade head`. Auto-migrate is safe — Alembic
        # is idempotent when already at head — and degrades to a warning
        # when the DB is unreachable.
        import os
        import sys

        # Tests use an in-memory SQLite override (see backend/tests/conftest.py)
        # and must not block on a real PostgreSQL connection. The same applies
        # in CI where the DB may not be started yet.
        if "PYTEST_CURRENT_TEST" not in os.environ and "pytest" not in sys.modules:
            try:
                from alembic import command
                from alembic.config import Config

                alembic_ini = Path(__file__).resolve().parents[1] / "alembic.ini"
                migrations_dir = Path(__file__).resolve().parents[1] / "migrations"
                if alembic_ini.exists() and migrations_dir.exists():
                    # Fail fast when DB is down — psycopg defaults to a long
                    # TCP timeout; 2 s is enough for local/docker and keeps
                    # pytest and host-only `uvicorn --reload` snappy.
                    db_url = settings.database_url
                    if "connect_timeout" not in db_url:
                        sep = "&" if "?" in db_url else "?"
                        db_url = f"{db_url}{sep}connect_timeout=2"
                    cfg = Config(str(alembic_ini))
                    cfg.set_main_option("sqlalchemy.url", db_url)
                    # Ensure Alembic finds migrations/env.py via script_location
                    cfg.set_main_option("script_location", str(migrations_dir))
                    command.upgrade(cfg, "head")
                    logging.info("Database schema is at head")
            except OperationalError:
                logging.warning(
                    "Database unavailable at startup — schema migration skipped; "
                    "will retry when DB is reachable"
                )
            except Exception as exc:  # noqa: BLE001
                logging.warning("Automatic schema migration failed: %s", exc)

        # Catalog is reference data — it must exist before any student
        # browses problems. The seed is idempotent and also refreshes
        # problem metadata so content fixes propagate on restart.
        # Skip when running under pytest — the fixture provisions an
        # in-memory SQLite DB and a real PostgreSQL is not available.
        if "PYTEST_CURRENT_TEST" not in os.environ and "pytest" not in sys.modules:
            try:
                from app.db.session import SessionLocal
                from app.problems.seed import seed_problems

                db = SessionLocal()
                try:
                    created = seed_problems(db)
                    if created:
                        logging.info("Catalog auto-seeded: %s problem(s) created", created)
                    else:
                        logging.info("Catalog already seeded")
                finally:
                    db.close()
            except OperationalError:
                logging.warning(
                    "Database unavailable at startup — catalog will be seeded when DB is reachable"
                )
            except ProgrammingError as exc:
                # Stale schema — most commonly after pulling new migrations
                # without running `alembic upgrade head`. Surface an actionable
                # hint instead of a raw UndefinedColumn/UndefinedTable traceback.
                orig = getattr(exc, "orig", None)
                detail = str(orig) if orig is not None else str(exc)
                logging.warning(
                    "Database schema out of date (ProgrammingError): %s — "
                    "fix with: cd backend && alembic upgrade head",
                    detail,
                )
            except Exception as exc:  # noqa: BLE001
                logging.warning("Catalog auto-seed failed: %s", exc)
        yield

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )

    # Credentialed browser access from the Next.js frontend.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        allow_headers=["Content-Type"],
    )

    @app.exception_handler(OperationalError)
    async def database_unavailable(request: Request, exc: OperationalError):
        """Unreachable database answers a clean 503 instead of a traceback."""
        logging.error("Database unavailable on %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=503,
            content={"detail": ("Database unavailable. Start it with: docker compose up -d db")},
        )

    @app.exception_handler(ProgrammingError)
    async def schema_out_of_date(request: Request, exc: ProgrammingError):
        """Stale schema (e.g. missing column/table) answers 503 with a fix hint."""
        orig = getattr(exc, "orig", None)
        detail = str(orig) if orig is not None else str(exc)
        logging.error("Schema out of date on %s %s: %s", request.method, request.url.path, detail)
        return JSONResponse(
            status_code=503,
            content={
                "detail": (
                    "Database schema out of date — run: cd backend && alembic upgrade head. "
                    f"Detail: {detail}"
                )
            },
        )

    @app.get("/", include_in_schema=False)
    def root() -> RedirectResponse:
        return RedirectResponse(url="/api/docs")

    app.include_router(health.router, prefix="/api")
    app.include_router(auth_router, prefix="/api")
    app.include_router(problems_router, prefix="/api")
    app.include_router(execution_router, prefix="/api")
    app.include_router(events_router, prefix="/api")
    app.include_router(analytics_router, prefix="/api")
    app.include_router(sessions_router, prefix="/api")
    app.include_router(tutor_router, prefix="/api")
    app.include_router(retention_router, prefix="/api")
    app.include_router(curriculum_router, prefix="/api")
    app.include_router(generator_router, prefix="/api")
    app.include_router(difficulty_router, prefix="/api")
    app.include_router(retrieval_router, prefix="/api")
    app.include_router(transfer_router, prefix="/api")
    return app


app = create_app()
