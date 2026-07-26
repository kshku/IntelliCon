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
    from neo4j.exceptions import ServiceUnavailable
    try:
        stats = await sync_all()
        return {"status": "ok", "synced": stats}
    except ServiceUnavailable:
        return {"status": "offline", "synced": {}, "message": "Neo4j is offline"}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/schema")
async def init_schema():
    from neo4j.exceptions import ServiceUnavailable
    try:
        get_driver()
        statements = GRAPH_SCHEMA["constraints"] + GRAPH_SCHEMA["indexes"]
        for statement in statements:
            await async_run_write(statement)
        return {"status": "ok", "applied": len(statements)}
    except ServiceUnavailable:
        return {"status": "offline", "applied": 0, "message": "Neo4j is offline"}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/query")
async def query_graph(request: GraphQueryRequest):
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
                    "message": "Neo4j graph database is offline."
                }
            raise HTTPException(status_code=400, detail=result.error)

        return {
            "status": "ok",
            "data": result.data,
            "metadata": result.metadata,
        }
    except ServiceUnavailable:
        return {
            "status": "offline",
            "data": {"nodes": [], "links": []},
            "message": "Neo4j graph database is offline."
        }
    except HTTPException:
        raise
    except Exception as exc:
        if "ServiceUnavailable" in str(exc) or "connection" in str(exc).lower():
            return {
                "status": "offline",
                "data": {"nodes": [], "links": []},
                "message": "Neo4j graph database is offline."
            }
        raise HTTPException(status_code=500, detail=str(exc))
