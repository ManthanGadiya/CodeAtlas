"""Application configuration.

Settings load from environment variables and the repository-root ``.env``
file (see ``.env.example``). Every setting has a safe development default so
the application starts even with no ``.env`` present.
"""

from functools import lru_cache
from pathlib import Path
from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

# backend/app/core/config.py -> repository root
REPO_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=REPO_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "CodeAtlas"
    app_version: str = "0.1.0"
    environment: str = "development"
    log_level: str = "INFO"

    # PostgreSQL is the documented system database (docs/Data_Model.md §67).
    # The URL stays configurable so a locally installed PostgreSQL works too;
    # Docker must not be a hard requirement in development.
    database_url: str = "postgresql+psycopg://codeatlas:codeatlas@localhost:5432/codeatlas"

    # AI provider keys stay optional until the AI gateway milestone.
    # Core functionality must work without external AI (docs/PRD.md NFR-002).
    gemini_api_key: str | None = None
    groq_api_key: str | None = None

    # --- Auth & sessions ---
    session_cookie_name: str = "codeatlas_session"
    session_lifetime_minutes: int = 7 * 24 * 60  # 7 days

    # --- Code execution sandbox ---
    # Student code runs ONLY inside a Docker container with network disabled,
    # capped CPU/memory/processes, and a read-only filesystem. The API answers
    # 503 when the engine is unavailable; everything else works without Docker.
    docker_image: str = "python:3.12-alpine"
    exec_memory_mb: int = 256
    exec_cpus: float = 0.5
    exec_pids_limit: int = 64
    exec_timeout_seconds: int = 10
    exec_output_limit_bytes: int = 65_536

    # Frontend origins allowed to send credentialed requests.
    # NoDecode + validator: accept plain comma-separated env values
    # (pydantic-settings would otherwise demand JSON for list fields).
    cors_origins: Annotated[list[str], NoDecode] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_cors_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
