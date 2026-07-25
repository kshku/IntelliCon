from sqlalchemy import inspect, text

from app.db import engine, init_schema


def test_init_schema_creates_analytics_schema():
    """Verify init_schema creates the analytics schema and tables."""
    init_schema()
    with engine.connect() as conn:
        result = conn.execute(
            text(
                "SELECT schema_name FROM information_schema.schemata "
                "WHERE schema_name = 'analytics'"
            )
        )
        assert result.fetchone() is not None


def test_init_schema_creates_job_execution_log():
    """Verify job_execution_log table exists in analytics schema."""
    init_schema()
    inspector = inspect(engine)
    tables = inspector.get_table_names(schema="analytics")
    assert "job_execution_log" in tables


def test_init_schema_creates_result_tables():
    """Verify all result tables exist in analytics schema."""
    init_schema()
    inspector = inspect(engine)
    tables = inspector.get_table_names(schema="analytics")
    assert "hotspot_results" in tables
    assert "trend_results" in tables
    assert "prediction_results" in tables
