import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


def test_startup_fails_with_invalid_production_config():
    """App must fail to start with invalid production config."""
    from app.main import app, lifespan

    mock_settings = MagicMock()
    mock_settings.ENVIRONMENT = "production"
    mock_settings.JWT_SECRET_KEY = "short"
    mock_settings.LLM_API_KEY = ""
    mock_settings.CORS_ORIGINS = ["http://localhost:3000"]
    mock_settings.DATABASE_URL = "postgresql://intellicon:intellicon@localhost:5432/intellicon"

    with (
        patch("app.main.settings", mock_settings),
        patch("app.main.validate_production_config") as mock_validate,
        patch("app.main.wait_for_db"),
        patch("app.main.run_migrations"),
        patch("app.main.get_current_revision", return_value="abc123"),
    ):
        mock_validate.return_value = [
            "JWT_SECRET_KEY must be at least 32 characters",
            "LLM_API_KEY must be set to a valid API key",
            "CORS_ORIGINS must not contain localhost in production",
            "DATABASE_URL contains default development credentials",
        ]

        async def run_test():
            with pytest.raises(RuntimeError, match="Production configuration invalid"):
                async with lifespan(app):
                    pass

        asyncio.run(run_test())


def test_startup_skips_validation_in_development():
    """App must skip production validation in development mode."""
    from app.main import app, lifespan

    mock_settings = MagicMock()
    mock_settings.ENVIRONMENT = "development"
    mock_settings.JWT_SECRET_KEY = "a-valid-secret-key-for-development-mode"
    mock_settings.LLM_API_KEY = ""
    mock_settings.CORS_ORIGINS = ["http://localhost:3000"]
    mock_settings.DATABASE_URL = "postgresql://intellicon:intellicon@localhost:5432/intellicon"

    mock_engine = AsyncMock()

    with (
        patch("app.main.settings", mock_settings),
        patch("app.main.validate_production_config") as mock_validate,
        patch("app.main.wait_for_db"),
        patch("app.main.run_migrations"),
        patch("app.main.get_current_revision", return_value="abc123"),
        patch("app.db.session.engine", mock_engine),
        patch("app.db.neo4j.close_driver"),
    ):
        mock_validate.return_value = []

        async def run_test():
            async with lifespan(app):
                pass

        asyncio.run(run_test())
