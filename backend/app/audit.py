from __future__ import annotations

import logging

from sqlalchemy import insert

from app.db.session import async_session
from app.models.audit import AuditTrail

logger = logging.getLogger("app.audit")


async def log_audit_step(
    *,
    session_id: str | None,
    user_id: str | None,
    step_number: int,
    step_type: str,
    content: str | None = None,
    tool_name: str | None = None,
    tool_output: str | None = None,
    sql_executed: str | None = None,
    duration_ms: int | None = None,
) -> None:
    try:
        async with async_session() as db:
            await db.execute(
                insert(AuditTrail).values(
                    session_id=session_id,
                    user_id=user_id,
                    step_number=step_number,
                    step_type=step_type,
                    content=content,
                    tool_name=tool_name,
                    tool_output=tool_output,
                    sql_executed=sql_executed,
                    duration_ms=duration_ms,
                )
            )
            await db.commit()
    except Exception:
        logger.exception("Failed to write audit trail entry")
