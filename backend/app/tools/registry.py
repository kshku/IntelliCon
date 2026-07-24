from __future__ import annotations

from app.tools.base import ToolRegistry
from app.tools.sample import CalculatorTool
from app.tools.sql_query import SqlQueryTool

tool_registry = ToolRegistry()


def register_default_tools() -> None:
    tool_registry.register(CalculatorTool())
    tool_registry.register(SqlQueryTool())
