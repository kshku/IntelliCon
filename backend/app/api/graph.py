from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.auth import get_current_user
from app.db.graph_schema import GRAPH_SCHEMA
from app.db.neo4j import async_run_write, get_driver
from app.db.sync import sync_all
from app.models.user import User

router = APIRouter(prefix="/api/graph", tags=["graph"])


class GraphQueryRequest(BaseModel):
    query_type: str
    name_a: str | None = None
    name_b: str | None = None
    district: str | None = None


@router.post("/sync")
async def trigger_sync(
    _user: User = Depends(get_current_user),
):
    from neo4j.exceptions import ServiceUnavailable

    try:
        stats = await sync_all()
        return {"status": "ok", "synced": stats}
    except ServiceUnavailable:
        return {
            "status": "offline",
            "synced": {},
            "message": "Neo4j is offline",
        }
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/schema")
async def init_schema(
    _user: User = Depends(get_current_user),
):
    from neo4j.exceptions import ServiceUnavailable

    try:
        get_driver()
        statements = GRAPH_SCHEMA["constraints"] + GRAPH_SCHEMA["indexes"]
        for statement in statements:
            await async_run_write(statement)
        return {"status": "ok", "applied": len(statements)}
    except ServiceUnavailable:
        return {
            "status": "offline",
            "applied": 0,
            "message": "Neo4j is offline",
        }
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/query")
async def query_graph(
    request: GraphQueryRequest,
    _user: User = Depends(get_current_user),
):
    from neo4j.exceptions import ServiceUnavailable

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
            err_str = str(result.error)
            if "ServiceUnavailable" in err_str or "connection" in err_str.lower():
                return {
                    "status": "offline",
                    "data": {"nodes": [], "links": []},
                    "message": ("Neo4j graph database is offline."),
                }
            raise HTTPException(status_code=400, detail="Graph query failed")

        return {
            "status": "ok",
            "data": result.data,
            "metadata": result.metadata,
        }
    except ServiceUnavailable:
        return {
            "status": "offline",
            "data": {"nodes": [], "links": []},
            "message": "Neo4j graph database is offline.",
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")
