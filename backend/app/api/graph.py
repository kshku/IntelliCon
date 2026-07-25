from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.db.graph_schema import GRAPH_SCHEMA
from app.db.neo4j import async_run_write, get_driver
from app.db.sync import sync_all

router = APIRouter(prefix="/api/graph", tags=["graph"])


class GraphQueryRequest(BaseModel):
    query_type: str
    name_a: str | None = None
    name_b: str | None = None
    district: str | None = None


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
            await async_run_write(statement)
        return {"status": "ok", "applied": len(statements)}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/query")
async def query_graph(request: GraphQueryRequest):
    try:
        from app.tools.graph_query import GraphQueryTool

        tool = GraphQueryTool()
        kwargs = {"query_type": request.query_type}
        if request.name_a:
            kwargs["name_a"] = request.name_a
        if request.name_b:
            kwargs["name_b"] = request.name_b
        if request.district:
            kwargs["district"] = request.district

        result = await tool.execute(**kwargs)
        if not result.success:
            raise HTTPException(status_code=400, detail=result.error)

        return {
            "status": "ok",
            "data": result.data,
            "metadata": result.metadata,
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
