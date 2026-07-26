from __future__ import annotations

import asyncio
import logging
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from app.config import settings
from app.tools.base import ToolResult
from app.tools.schema_context import SCHEMA_DESCRIPTION
from app.tools.sql_validator import SqlValidationError, validate_sql

logger = logging.getLogger("app.tools.sql_query")

SQL_GENERATION_SYSTEM_PROMPT = """\
You are a PostgreSQL query generator for a Karnataka Police FIR database.

Given the user's natural language question, generate a single SQL SELECT query.

{schema}

Rules:
- Generate ONLY a SELECT query. No INSERT, UPDATE, DELETE, or DDL.
- Use standard SQL syntax compatible with PostgreSQL.
- For date comparisons, dates are stored as VARCHAR. Use LIKE or string comparison.
  Example: crime_registered_date LIKE '2024-07%' for July 2024.
- Always JOIN tables using foreign keys when you need data from related tables.
- Use aggregate functions (COUNT, SUM, AVG) when the question asks for summaries.
- Use GROUP BY for breakdowns by category.
- Order results logically (e.g., by date, by count descending).
- Return ONLY the SQL query, no explanation, no markdown code blocks.
"""


class SqlQueryTool:
    name = "sql_query"
    description = (
        "Queries the Karnataka Police FIR database using natural language. "
        "Converts questions to SQL, validates, executes, and returns results."
    )
    input_schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": (
                    "Natural language question about FIR data, "
                    "e.g. 'How many theft cases were registered in Mangaluru last month?'"
                ),
            }
        },
        "required": ["question"],
    }

    async def execute(self, **kwargs: Any) -> ToolResult:
        question = kwargs.get("question", "")
        if not question or not isinstance(question, str):
            return ToolResult(success=False, error="A non-empty question string is required")

        try:
            sql = await self._generate_sql(question)
        except Exception as exc:
            return ToolResult(success=False, error=f"SQL generation failed: {exc}")

        try:
            validated_sql = validate_sql(sql)
        except SqlValidationError as exc:
            return ToolResult(success=False, error=f"SQL validation failed: {exc}")

        try:
            result = await self._execute_query(validated_sql)
        except TimeoutError:
            return ToolResult(
                success=False,
                error=f"Query timed out after {settings.SQL_QUERY_TIMEOUT}s",
            )
        except Exception as exc:
            return ToolResult(success=False, error=f"Query execution failed: {exc}")

        return result

    async def _generate_sql(self, question: str) -> str:
        from app.agent.llm_factory import get_llm

        llm = get_llm()
        messages = [
            SystemMessage(content=SQL_GENERATION_SYSTEM_PROMPT.format(schema=SCHEMA_DESCRIPTION)),
            HumanMessage(content=question),
        ]
        response = await llm.ainvoke(messages)
        sql = response.content if isinstance(response.content, str) else str(response.content)
        sql = sql.strip()
        sql = sql.removeprefix("```sql").removesuffix("```").strip()
        return sql

    async def _execute_query(self, sql: str) -> ToolResult:
        from sqlalchemy import text

        from app.db.session import async_session

        max_rows = settings.SQL_MAX_ROWS
        timeout = settings.SQL_QUERY_TIMEOUT

        needs_limit = "LIMIT" not in sql.upper()
        if needs_limit:
            sql = f"{sql} LIMIT {max_rows}"

        logger.info("Executing SQL: %s", sql)

        async with async_session() as session:
            result = await asyncio.wait_for(
                session.execute(text(sql)),
                timeout=timeout,
            )
            rows = result.fetchall()
            columns = list(result.keys())

        truncated = len(rows) >= max_rows and needs_limit
        formatted = self._format_results(columns, list(rows))

        return ToolResult(
            success=True,
            data=formatted,
            metadata={
                "sql": sql,
                "row_count": len(rows),
                "truncated": truncated,
                "columns": columns,
            },
        )

    def _format_results(self, columns: list[str], rows: list[tuple[Any, ...]]) -> str:
        if not rows:
            return "No results found."

        lines: list[str] = []
        lines.append(" | ".join(columns))
        lines.append("-" * len(lines[0]))
        for row in rows:
            lines.append(" | ".join(str(v) if v is not None else "NULL" for v in row))
        return "\n".join(lines)
