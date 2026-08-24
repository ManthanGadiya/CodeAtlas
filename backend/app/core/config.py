"""Application configuration.

Settings load from environment variables and the repository-root ``.env``
file (see ``.env.example``). Every setting has a safe development default so
the application starts even with no ``.env`` present.
"""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

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


@lru_cache
def get_settings() -> Settings:
    return Settings()
