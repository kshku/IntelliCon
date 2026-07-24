from __future__ import annotations

import json
import logging
from typing import Any

from app.tools.base import ToolResult

logger = logging.getLogger("app.tools.audit")


def log_tool_execution(
    tool_name: str,
    args: dict[str, Any],
    result: ToolResult,
    session_id: str,
    duration_ms: float,
) -> None:
    log_entry: dict[str, Any] = {
        "tool": tool_name,
        "success": result.success,
        "session_id": session_id,
        "duration_ms": duration_ms,
        "args": args,
    }
    if result.error is not None:
        log_entry["error"] = result.error
    if result.metadata:
        log_entry["result_metadata"] = result.metadata

    level = logging.INFO if result.success else logging.WARNING
    logger.log(level, json.dumps(log_entry, default=str))
