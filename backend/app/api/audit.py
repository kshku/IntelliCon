from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.db.session import get_session
from app.models.audit import AuditTrail
from app.models.user import User

router = APIRouter(prefix="/audit", tags=["audit"])


class AuditStepResponse(BaseModel):
    id: int
    session_id: str | None
    user_id: str | None
    step_number: int
    step_type: str
    content: str | None
    tool_name: str | None
    tool_output: str | None
    sql_executed: str | None
    duration_ms: int | None
    created_at: str

    model_config = {"from_attributes": True}


@router.get("/trail/{session_id}", response_model=list[AuditStepResponse])
async def get_audit_trail(
    session_id: str,
    limit: int = Query(50, ge=1, le=500),
    _user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(AuditTrail)
        .where(AuditTrail.session_id == session_id)
        .order_by(AuditTrail.step_number)
        .limit(limit)
    )
    rows = result.scalars().all()
    if not rows:
        raise HTTPException(status_code=404, detail="No audit trail found for this session")
    return [
        AuditStepResponse(
            id=row.id,
            session_id=row.session_id,
            user_id=row.user_id,
            step_number=row.step_number,
            step_type=row.step_type,
            content=row.content,
            tool_name=row.tool_name,
            tool_output=row.tool_output,
            sql_executed=row.sql_executed,
            duration_ms=row.duration_ms,
            created_at=row.created_at.isoformat() if row.created_at else "",
        )
        for row in rows
    ]
