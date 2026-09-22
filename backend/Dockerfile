# CodeAtlas backend — FastAPI + Alembic + sandboxed runner
# Built from repository root via docker-compose (context: ./backend).

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# curl is needed for the HEALTHCHECK; keep the image slim.
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies first for better layer caching.
COPY pyproject.toml alembic.ini ./
COPY migrations ./migrations
COPY app ./app
COPY sandbox ./sandbox
COPY scripts ./scripts

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -e .

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=5s --start-period=20s --retries=10 \
    CMD curl -f http://localhost:8000/api/healthz || exit 1

# Auto-migration + seed lives in app.main lifespan (alembic upgrade head
# + seed_problems), so the container boots cleanly on a stale checkout.
# No entrypoint wrapper is required; the app self-heals. Mounting the Docker
# socket is only needed for Run/Submit execution — everything else works
# without it.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
