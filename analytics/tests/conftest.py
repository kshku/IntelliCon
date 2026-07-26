import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.config import settings


@pytest.fixture(scope="session")
def engine():
    """Create a test engine using the same DATABASE_URL."""
    test_url = settings.DATABASE_URL
    eng = create_engine(test_url, echo=False)
    yield eng
    eng.dispose()


@pytest.fixture(scope="session")
def schema(engine):
    """Create a test schema, yield it, then drop it."""
    schema_name = "analytics_test"
    with engine.connect() as conn:
        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}"))
        conn.commit()
    yield schema_name
    with engine.connect() as conn:
        conn.execute(text(f"DROP SCHEMA IF EXISTS {schema_name} CASCADE"))
        conn.commit()


@pytest.fixture()
def session(engine, schema):
    """Provide a transactional session that rolls back after each test."""
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    sess = Session()
    yield sess
    sess.close()
    transaction.rollback()
    connection.close()
