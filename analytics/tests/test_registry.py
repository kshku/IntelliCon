from app.registry import JobDefinition, get_registry, register_job


def test_register_job_adds_to_registry():
    @register_job("test_job", schedule="cron", hour=10, minute=0, description="Test job")
    class TestPipeline:
        name = "test_job"
        description = "Test job"

        def run(self, session):
            return {"rows_processed": 1}

    registry = get_registry()
    assert "test_job" in registry
    assert isinstance(registry["test_job"], JobDefinition)
    assert registry["test_job"].name == "test_job"
    assert registry["test_job"].schedule == "cron"
    assert registry["test_job"].schedule_kwargs == {"hour": 10, "minute": 0}
    assert registry["test_job"].description == "Test job"
    assert registry["test_job"].pipeline_class is TestPipeline


def test_get_registry_returns_copy():
    registry1 = get_registry()
    registry2 = get_registry()
    assert registry1 is not registry2


def test_register_job_uses_class_description_if_none():
    @register_job("test_job_2", schedule="cron", hour=11)
    class TestPipeline2:
        name = "test_job_2"
        description = "From class"

        def run(self, session):
            return {}

    registry = get_registry()
    assert registry["test_job_2"].description == "From class"
