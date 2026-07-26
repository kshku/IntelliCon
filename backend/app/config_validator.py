"""Production configuration validator."""
from app.config import Settings


def validate_production_config(settings: Settings) -> list[str]:
    """Validate configuration for production environment.

    Returns list of error messages. Empty list means all checks passed.
    """
    errors: list[str] = []

    # Skip validation in development/testing
    if settings.ENVIRONMENT != "production":
        return errors

    # Validate JWT secret
    if settings.JWT_SECRET_KEY == "change-me-in-production":
        errors.append("JWT_SECRET_KEY must be changed from default placeholder")
    elif len(settings.JWT_SECRET_KEY) < 32:
        errors.append("JWT_SECRET_KEY must be at least 32 characters")

    # Validate LLM API key
    if not settings.LLM_API_KEY or settings.LLM_API_KEY == "your-api-key-here":
        errors.append("LLM_API_KEY must be set to a valid API key")

    # Validate CORS origins
    has_localhost = any(
        "localhost" in origin or "127.0.0.1" in origin
        for origin in settings.CORS_ORIGINS
    )
    if has_localhost:
        errors.append("CORS_ORIGINS must not contain localhost in production")

    # Validate database credentials
    if "intellicon:intellicon@" in settings.DATABASE_URL:
        errors.append("DATABASE_URL contains default development credentials")

    return errors
