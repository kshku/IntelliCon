import pytest

from app.tools.base import ToolRegistry, ToolResult


class TestToolResult:
    def test_success_result(self):
        result = ToolResult(success=True, data={"key": "value"})
        assert result.success is True
        assert result.data == {"key": "value"}
        assert result.error is None
        assert result.metadata == {}

    def test_error_result(self):
        result = ToolResult(success=False, error="something went wrong")
        assert result.success is False
        assert result.error == "something went wrong"
        assert result.data is None

    def test_result_with_metadata(self):
        metadata = {"duration_ms": 42, "source": "test"}
        result = ToolResult(success=True, data=123, metadata=metadata)
        assert result.metadata == metadata

    def test_result_defaults(self):
        result = ToolResult(success=True)
        assert result.data is None
        assert result.error is None
        assert result.metadata == {}


class TestToolRegistry:
    def test_register_and_get(self):
        registry = ToolRegistry()

        class FakeTool:
            name = "fake"
            description = "A fake tool"
            input_schema: dict = {}

            async def execute(self, **kwargs: object) -> ToolResult:
                return ToolResult(success=True)

        tool = FakeTool()
        registry.register(tool)
        assert registry.get("fake") is tool

    def test_get_nonexistent_returns_none(self):
        registry = ToolRegistry()
        assert registry.get("nope") is None

    def test_list_tools(self):
        registry = ToolRegistry()

        class ToolA:
            name = "a"
            description = "Tool A"
            input_schema: dict = {}

            async def execute(self, **kwargs: object) -> ToolResult:
                return ToolResult(success=True)

        class ToolB:
            name = "b"
            description = "Tool B"
            input_schema: dict = {}

            async def execute(self, **kwargs: object) -> ToolResult:
                return ToolResult(success=True)

        registry.register(ToolA())
        registry.register(ToolB())
        tools = registry.list_tools()
        assert len(tools) == 2
        names = {t.name for t in tools}
        assert names == {"a", "b"}

    def test_duplicate_name_raises(self):
        registry = ToolRegistry()

        class ToolX:
            name = "x"
            description = "First"
            input_schema: dict = {}

            async def execute(self, **kwargs: object) -> ToolResult:
                return ToolResult(success=True)

        class ToolX2:
            name = "x"
            description = "Duplicate"
            input_schema: dict = {}

            async def execute(self, **kwargs: object) -> ToolResult:
                return ToolResult(success=True)

        registry.register(ToolX())
        with pytest.raises(ValueError, match="already registered"):
            registry.register(ToolX2())

    def test_get_langchain_tools(self):
        registry = ToolRegistry()

        class CalcTool:
            name = "calculator"
            description = "Evaluates math expressions"
            input_schema = {"type": "object", "properties": {"expression": {"type": "string"}}}

            async def execute(self, **kwargs: object) -> ToolResult:
                return ToolResult(success=True, data=42)

        registry.register(CalcTool())
        lc_tools = registry.get_langchain_tools()
        assert len(lc_tools) == 1
        assert lc_tools[0].name == "calculator"
