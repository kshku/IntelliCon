from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.db.graph_schema import GRAPH_SCHEMA
from app.db.neo4j import get_driver, run_write
from app.db.sync import sync_all

router = APIRouter(prefix="/api/graph", tags=["graph"])


@router.post("/sync")
async def trigger_sync():
    try:
        stats = await sync_all()
        return {"status": "ok", "synced": stats}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/schema")
async def init_schema():
    try:
        get_driver()
        statements = GRAPH_SCHEMA["constraints"] + GRAPH_SCHEMA["indexes"]
        for statement in statements:
            run_write(statement)
        return {"status": "ok", "applied": len(statements)}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
