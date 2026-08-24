"""Tests for application configuration."""

import pytest

from app.core.config import Settings

_ENV_KEYS_THAT_AFFECT_SETTINGS = (
    "APP_NAME",
    "APP_VERSION",
    "ENVIRONMENT",
    "LOG_LEVEL",
    "DATABASE_URL",
    "GEMINI_API_KEY",
    "GROQ_API_KEY",
)


@pytest.fixture(autouse=True)
def _clean_settings_env(monkeypatch):
    """Keep tests deterministic even if a developer exports these vars."""
    for key in _ENV_KEYS_THAT_AFFECT_SETTINGS:
        monkeypatch.delenv(key, raising=False)


def test_ai_keys_optional_by_default():
    settings = Settings(_env_file=None)
    assert settings.gemini_api_key is None
    assert settings.groq_api_key is None


def test_safe_defaults_without_env_file():
    settings = Settings(_env_file=None)
    assert settings.environment == "development"
    assert settings.database_url.startswith("postgresql+psycopg://")
