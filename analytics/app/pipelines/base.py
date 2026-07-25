from __future__ import annotations

from typing import Any, Protocol

from sqlalchemy.orm import Session


class BasePipeline(Protocol):
    name: str
    description: str

    def run(self, session: Session) -> dict[str, Any]: ...
