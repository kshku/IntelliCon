from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from app.tools.base import ToolResult
from app.tools.sql_query import SqlQueryTool


class TestSqlQueryTool:
    def setup_method(self):
        self.tool = SqlQueryTool()

    def test_tool_metadata(self):
        assert self.tool.name == "sql_query"
        assert "question" in self.tool.input_schema.get("properties", {})

    @pytest.mark.asyncio
    async def test_empty_question(self):
        result = await self.tool.execute(question="")
        assert result.success is False
        assert "required" in result.error

    @pytest.mark.asyncio
    async def test_missing_question(self):
        result = await self.tool.execute()
        assert result.success is False

    @pytest.mark.asyncio
    async def test_invalid_sql_generation(self):
        with patch.object(
            self.tool, "_generate_sql", new_callable=AsyncMock
        ) as mock_gen:
            mock_gen.return_value = "INSERT INTO case_master VALUES (1)"
            result = await self.tool.execute(question="Add a case")
            assert result.success is False
            assert "validation failed" in result.error

    @pytest.mark.asyncio
    async def test_valid_query_execution(self):
        with (
            patch.object(
                self.tool, "_generate_sql", new_callable=AsyncMock
            ) as mock_gen,
            patch.object(
                self.tool, "_execute_query", new_callable=AsyncMock
            ) as mock_exec,
        ):
            mock_gen.return_value = "SELECT COUNT(*) FROM case_master"
            mock_exec.return_value = ToolResult(
                success=True, data="count\n5", metadata={"row_count": 1}
            )
            result = await self.tool.execute(question="How many cases?")
            assert result.success is True
            assert "5" in result.data

    @pytest.mark.asyncio
    async def test_query_timeout(self):
        with (
            patch.object(
                self.tool, "_generate_sql", new_callable=AsyncMock
            ) as mock_gen,
            patch.object(
                self.tool, "_execute_query", new_callable=AsyncMock
            ) as mock_exec,
        ):
            mock_gen.return_value = "SELECT * FROM case_master"
            mock_exec.side_effect = TimeoutError()
            result = await self.tool.execute(question="Show all cases")
            assert result.success is False
            assert "timed out" in result.error

    def test_format_results_empty(self):
        formatted = self.tool._format_results([], [])
        assert formatted == "No results found."

    def test_format_results_with_data(self):
        formatted = self.tool._format_results(
            ["case_no", "crime_no"],
            [("KA-001", "Cr.No.1/2024"), ("KA-002", "Cr.No.2/2024")],
        )
        assert "case_no" in formatted
        assert "KA-001" in formatted
        assert "KA-002" in formatted

    def test_format_results_null_values(self):
        formatted = self.tool._format_results(
            ["col1"], [(None,)]
        )
        assert "NULL" in formatted
