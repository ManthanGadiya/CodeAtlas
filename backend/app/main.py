"""CodeAtlas FastAPI application factory."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.exc import OperationalError

from app.analytics.routes import router as analytics_router
from app.api.routes import health
from app.auth.routes import router as auth_router
from app.core.config import get_settings
from app.events.routes import router as events_router
from app.execution.routes import router as execution_router
from app.problems.routes import router as problems_router
from app.sessions.routes import router as sessions_router


def create_app() -> FastAPI:
    settings = get_settings()
    logging.basicConfig(level=settings.log_level.upper())

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Catalog is reference data — it must exist before any student
        # browses problems. The seed is idempotent and also refreshes
        # problem metadata so content fixes propagate on restart.
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
    return app


app = create_app()
