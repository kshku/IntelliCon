from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

from langchain_core.tools import StructuredTool


@dataclass
class ToolResult:
    success: bool
    data: Any = None
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@runtime_checkable
class BaseTool(Protocol):
    name: str
    description: str
    input_schema: dict[str, Any]

    async def execute(self, **kwargs: Any) -> ToolResult: ...


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        if tool.name in self._tools:
            raise ValueError(f"Tool '{tool.name}' is already registered")
        self._tools[tool.name] = tool

    def get(self, name: str) -> BaseTool | None:
        return self._tools.get(name)

    def list_tools(self) -> list[BaseTool]:
        return list(self._tools.values())

    def get_langchain_tools(self) -> list[StructuredTool]:
        tools: list[StructuredTool] = []
        for tool in self._tools.values():
            lc_tool = StructuredTool(
                name=tool.name,
                description=tool.description,
                args_schema=tool.input_schema,
                coroutine=tool.execute,
            )
            tools.append(lc_tool)
        return tools
