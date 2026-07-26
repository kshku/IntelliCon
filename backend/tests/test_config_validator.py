import pytest
from app.config import Settings
from app.config_validator import validate_production_config


def test_validate_returns_list():
    """Validator must return a list of errors."""
    settings = Settings()
    errors = validate_production_config(settings)
    assert isinstance(errors, list)


def test_validate_rejects_default_jwt_secret():
    """Must reject default JWT secret in production."""
    settings = Settings(
        ENVIRONMENT="production",
        JWT_SECRET_KEY="change-me-in-production",
    )
    errors = validate_production_config(settings)
    assert any("JWT_SECRET_KEY" in e for e in errors)


def test_validate_rejects_weak_jwt_secret():
    """Must reject JWT secrets shorter than 32 characters."""
    settings = Settings(
        ENVIRONMENT="production",
        JWT_SECRET_KEY="short",
    )
    errors = validate_production_config(settings)
    assert any("JWT_SECRET_KEY" in e for e in errors)


def test_validate_accepts_strong_jwt_secret():
    """Must accept JWT secrets >= 32 characters."""
    settings = Settings(
        ENVIRONMENT="production",
        JWT_SECRET_KEY="a" * 32,
    )
    errors = validate_production_config(settings)
    assert not any("JWT_SECRET_KEY" in e for e in errors)


def test_validate_rejects_default_llm_key():
    """Must reject default/empty LLM API key in production."""
    settings = Settings(
        ENVIRONMENT="production",
        LLM_API_KEY="",
    )
    errors = validate_production_config(settings)
    assert any("LLM_API_KEY" in e for e in errors)


def test_validate_rejects_placeholder_llm_key():
    """Must reject placeholder LLM API key in production."""
    settings = Settings(
        ENVIRONMENT="production",
        LLM_API_KEY="your-api-key-here",
    )
    errors = validate_production_config(settings)
    assert any("LLM_API_KEY" in e for e in errors)


def test_validate_accepts_real_llm_key():
    """Must accept real LLM API key in production."""
    settings = Settings(
        ENVIRONMENT="production",
        LLM_API_KEY="sk-1234567890abcdef",
    )
    errors = validate_production_config(settings)
    assert not any("LLM_API_KEY" in e for e in errors)


def test_validate_rejects_localhost_cors():
    """Must reject localhost CORS origins in production."""
    settings = Settings(
        ENVIRONMENT="production",
        CORS_ORIGINS=["http://localhost:3000"],
    )
    errors = validate_production_config(settings)
    assert any("CORS_ORIGINS" in e for e in errors)


def test_validate_rejects_127_cors():
    """Must reject 127.0.0.1 CORS origins in production."""
    settings = Settings(
        ENVIRONMENT="production",
        CORS_ORIGINS=["http://127.0.0.1:3000"],
    )
    errors = validate_production_config(settings)
    assert any("CORS_ORIGINS" in e for e in errors)


def test_validate_accepts_production_cors():
    """Must accept non-localhost CORS origins in production."""
    settings = Settings(
        ENVIRONMENT="production",
        CORS_ORIGINS=["https://app.example.com"],
    )
    errors = validate_production_config(settings)
    assert not any("CORS_ORIGINS" in e for e in errors)


def test_validate_rejects_default_postgres_password():
    """Must reject default Postgres password in production."""
    settings = Settings(
        ENVIRONMENT="production",
        DATABASE_URL="postgresql://intellicon:intellicon@localhost:5432/intellicon",
    )
    errors = validate_production_config(settings)
    assert any("DATABASE_URL" in e for e in errors)


def test_validate_accepts_custom_postgres_password():
    """Must accept non-default Postgres password in production."""
    settings = Settings(
        ENVIRONMENT="production",
        DATABASE_URL="postgresql://intellicon:s3cur3p@ss@db.example.com:5432/intellicon",
    )
    errors = validate_production_config(settings)
    assert not any("DATABASE_URL" in e for e in errors)


def test_validate_skips_checks_in_development():
    """Must skip validation in development mode."""
    settings = Settings(
        ENVIRONMENT="development",
        JWT_SECRET_KEY="change-me-in-production",
        LLM_API_KEY="",
        CORS_ORIGINS=["http://localhost:3000"],
    )
    errors = validate_production_config(settings)
    assert errors == []


def test_validate_skips_checks_in_testing():
    """Must skip validation in testing mode."""
    settings = Settings(
        ENVIRONMENT="testing",
        JWT_SECRET_KEY="change-me-in-production",
        LLM_API_KEY="",
        CORS_ORIGINS=["http://localhost:3000"],
    )
    errors = validate_production_config(settings)
    assert errors == []


def test_validate_rejects_all_defaults():
    """Must catch all default values at once."""
    settings = Settings(
        ENVIRONMENT="production",
        JWT_SECRET_KEY="change-me-in-production",
        LLM_API_KEY="",
        CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:5173"],
        DATABASE_URL="postgresql://intellicon:intellicon@localhost:5432/intellicon",
    )
    errors = validate_production_config(settings)
    assert len(errors) >= 4  # JWT, LLM, CORS, DATABASE
