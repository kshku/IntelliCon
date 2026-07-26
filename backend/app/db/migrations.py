"""Run Alembic migrations at application startup."""

import logging
import time

from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from alembic import command
from app.config import settings

logger = logging.getLogger(__name__)

ALEMBIC_CFG = Config("alembic.ini")


def wait_for_db(max_retries: int = 30, retry_interval: float = 1.0) -> None:
    """Wait for the database to become available."""
    from sqlalchemy import create_engine

    engine = create_engine(settings.DATABASE_URL)

    for attempt in range(max_retries):
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            logger.info("Database is available")
            return
        except OperationalError:
            if attempt < max_retries - 1:
                logger.info(
                    "Waiting for database... (attempt %d/%d)",
                    attempt + 1,
                    max_retries,
                )
                time.sleep(retry_interval)
            else:
                raise RuntimeError("Database not available after maximum retries")


def run_migrations() -> None:
    """Run Alembic migrations to upgrade the database to the latest version."""
    logger.info("Running database migrations...")
    try:
        command.upgrade(ALEMBIC_CFG, "head")
        logger.info("Database migrations completed successfully")
    except Exception:
        logger.exception("Failed to run database migrations")
        raise


def get_current_revision() -> str | None:
    """Get the current Alembic revision."""
    try:
        heads: str = command.heads(ALEMBIC_CFG, resolve_dependencies=True)  # type: ignore[func-returns-value]
        return heads or None
    except Exception:
        logger.exception("Failed to get current revision")
        return None
