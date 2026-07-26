from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field


@dataclass
class JobDefinition:
    name: str
    pipeline_class: type
    schedule: str
    schedule_kwargs: dict = field(default_factory=dict)
    description: str = ""


_registry: dict[str, JobDefinition] = {}


def register_job(
    name: str, schedule: str, description: str = "", **schedule_kwargs: object
) -> Callable:
    """Decorator: registers a pipeline class as a scheduled job."""

    def decorator(pipeline_class: type) -> type:
        _registry[name] = JobDefinition(
            name=name,
            pipeline_class=pipeline_class,
            schedule=schedule,
            schedule_kwargs=schedule_kwargs,
            description=description or getattr(pipeline_class, "description", ""),
        )
        return pipeline_class

    return decorator


def get_registry() -> dict[str, JobDefinition]:
    return _registry.copy()
