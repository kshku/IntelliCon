from __future__ import annotations

from app.tools.base import ToolRegistry
from app.tools.graph_query import GraphQueryTool
from app.tools.pdf_export import PdfExportTool
from app.tools.sample import CalculatorTool
from app.tools.sql_query import SqlQueryTool

tool_registry = ToolRegistry()


def register_default_tools() -> None:
    if not tool_registry.list_tools():
        tool_registry.register(CalculatorTool())
        tool_registry.register(SqlQueryTool())
        tool_registry.register(GraphQueryTool())
        tool_registry.register(PdfExportTool())


register_default_tools()
