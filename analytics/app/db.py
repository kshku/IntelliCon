from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.config import settings

engine = create_engine(settings.DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)

SCHEMA_NAME = "analytics"


def init_schema() -> None:
    """Create the analytics schema and all tables if they don't exist."""
    with engine.connect() as conn:
        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA_NAME}"))
        conn.commit()

    from app.models import metadata  # noqa: F811

    metadata.schema = SCHEMA_NAME
    metadata.create_all(engine)
