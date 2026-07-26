import pytest
from app.config import Settings


def test_settings_has_environment_field():
    """Settings must have an ENVIRONMENT field."""
    settings = Settings()
    assert hasattr(settings, "ENVIRONMENT")
    assert settings.ENVIRONMENT in ("development", "production", "testing")


def test_settings_environment_default():
    """ENVIRONMENT defaults to development."""
    settings = Settings()
    assert settings.ENVIRONMENT == "development"


def test_settings_environment_from_env(monkeypatch):
    """ENVIRONMENT can be set via environment variable."""
    monkeypatch.setenv("ENVIRONMENT", "production")
    settings = Settings()
    assert settings.ENVIRONMENT == "production"
