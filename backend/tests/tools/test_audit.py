import json
import logging

import pytest

from app.tools.audit import log_tool_execution
from app.tools.base import ToolResult


class TestAuditLogging:
    def test_log_tool_execution_success(self, caplog: pytest.LogCaptureFixture):
        result = ToolResult(success=True, data={"count": 5})
        with caplog.at_level(logging.INFO, logger="app.tools.audit"):
            log_tool_execution(
                tool_name="calculator",
                args={"expression": "2+3"},
                result=result,
                session_id="sess-001",
                duration_ms=12.5,
            )
        assert len(caplog.records) == 1
        record = caplog.records[0]
        log_entry = json.loads(record.message)
        assert log_entry["tool"] == "calculator"
        assert log_entry["success"] is True
        assert log_entry["session_id"] == "sess-001"
        assert log_entry["duration_ms"] == 12.5

    def test_log_tool_execution_error(self, caplog: pytest.LogCaptureFixture):
        result = ToolResult(success=False, error="bad input")
        with caplog.at_level(logging.WARNING, logger="app.tools.audit"):
            log_tool_execution(
                tool_name="parser",
                args={},
                result=result,
                session_id="sess-002",
                duration_ms=1.0,
            )
        assert len(caplog.records) == 1
        log_entry = json.loads(caplog.records[0].message)
        assert log_entry["success"] is False
        assert log_entry["error"] == "bad input"

    def test_log_includes_metadata(self, caplog: pytest.LogCaptureFixture):
        result = ToolResult(success=True, data="ok", metadata={"rows": 10})
        with caplog.at_level(logging.INFO, logger="app.tools.audit"):
            log_tool_execution(
                tool_name="query",
                args={"sql": "SELECT 1"},
                result=result,
                session_id="sess-003",
                duration_ms=50.0,
            )
        log_entry = json.loads(caplog.records[0].message)
        assert log_entry["result_metadata"] == {"rows": 10}
