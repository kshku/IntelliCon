import pytest

from app.tools.base import ToolResult
from app.tools.sample import CalculatorTool


class TestCalculatorTool:
    def setup_method(self):
        self.tool = CalculatorTool()

    @pytest.mark.asyncio
    async def test_basic_addition(self):
        result = await self.tool.execute(expression="2 + 3")
        assert isinstance(result, ToolResult)
        assert result.success is True
        assert result.data == 5

    @pytest.mark.asyncio
    async def test_basic_multiplication(self):
        result = await self.tool.execute(expression="6 * 7")
        assert result.success is True
        assert result.data == 42

    @pytest.mark.asyncio
    async def test_complex_expression(self):
        result = await self.tool.execute(expression="(2 + 3) * 4")
        assert result.success is True
        assert result.data == 20

    @pytest.mark.asyncio
    async def test_division(self):
        result = await self.tool.execute(expression="10 / 2")
        assert result.success is True
        assert result.data == 5.0

    @pytest.mark.asyncio
    async def test_invalid_expression(self):
        result = await self.tool.execute(expression="import os")
        assert result.success is False
        assert result.error is not None

    @pytest.mark.asyncio
    async def test_empty_expression(self):
        result = await self.tool.execute(expression="")
        assert result.success is False

    def test_tool_metadata(self):
        assert self.tool.name == "calculator"
        assert "expression" in self.tool.input_schema.get("properties", {})

    @pytest.mark.asyncio
    async def test_negative_numbers(self):
        result = await self.tool.execute(expression="-5 + 3")
        assert result.success is True
        assert result.data == -2
