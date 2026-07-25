from __future__ import annotations

import asyncio
import logging
from typing import Any

from app.tools.base import ToolResult

logger = logging.getLogger(__name__)

QUERY_TIMEOUT = 30
MAX_RESULTS = 50

CYPHER_TEMPLATES = {
    "neighbors_1hop": (
        "MATCH (p:Person)-[r]-(n) "
        "WHERE p.name CONTAINS $name "
        "RETURN p.name AS person, p.role AS person_role, "
        "       type(r) AS relationship, labels(n)[0] AS neighbor_type, "
        "       n.name AS neighbor_name, n.pg_id AS neighbor_id "
        "LIMIT $limit"
    ),
    "network_2hop": (
        "MATCH path = (p:Person)-[*1..2]-(n) "
        "WHERE p.name CONTAINS $name "
        "RETURN p.name AS source, "
        "       [r IN relationships(path) | type(r)] AS rel_path, "
        "       [n IN nodes(path) | n.name] AS node_path, "
        "       [n IN nodes(path) | labels(n)[0]] AS node_types "
        "LIMIT $limit"
    ),
    "shortest_path": (
        "MATCH path = shortestPath((a:Person)-[*]-(b:Person)) "
        "WHERE a.name CONTAINS $name_a AND b.name CONTAINS $name_b "
        "RETURN a.name AS person_a, b.name AS person_b, "
        "       length(path) AS hops, "
        "       [r IN relationships(path) | type(r)] AS relationships, "
        "       [n IN nodes(path) | n.name] AS path_nodes "
        "LIMIT 1"
    ),
    "degree_centrality": (
        "MATCH (p:Person)-[r]-(n) "
        "WHERE p.role = 'ACCUSED' "
        "OPTIONAL MATCH (p)-[:REGISTERED_AT]->(:Case)-[:REGISTERED_AT]->(ps:PoliceStation) "
        "WHERE ps.district CONTAINS $district "
        "WITH p, COUNT(DISTINCT n) AS degree "
        "RETURN p.name AS name, p.pg_id AS pg_id, degree "
        "ORDER BY degree DESC "
        "LIMIT $limit"
    ),
    "shared_cases": (
        "MATCH (a:Person)-[:IMPLICATED_IN]->(c:Case)<-[:IMPLICATED_IN]-(b:Person) "
        "WHERE a.name CONTAINS $name_a AND b.name CONTAINS $name_b "
        "RETURN a.name AS person_a, b.name AS person_b, "
        "       c.case_no AS case_no, c.crime_no AS crime_no, "
        "       c.crime_registered_date AS date, c.status AS status "
        "LIMIT $limit"
    ),
}

QUERY_DESCRIPTIONS = {
    "neighbors_1hop": "Find all entities directly connected to a person (1-hop neighbors)",
    "network_2hop": "Traverse up to 2 hops from a person to find their network",
    "shortest_path": "Find the shortest path between two persons",
    "degree_centrality": "Rank accused persons by number of connections (repeat offenders)",
    "shared_cases": "Find cases shared between two persons",
}


class GraphQueryTool:
    name = "graph_query"
    description = (
        "Queries the criminal network graph database (Neo4j). "
        "Use this to answer questions about connections between accused persons, "
        "criminal networks, shared cases, shortest paths, and repeat offenders."
    )
    input_schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "query_type": {
                "type": "string",
                "description": "Type of graph query to execute",
                "enum": [
                    "neighbors_1hop",
                    "network_2hop",
                    "shortest_path",
                    "degree_centrality",
                    "shared_cases",
                ],
            },
            "name_a": {
                "type": "string",
                "description": "Name of the first person (for neighbors, network, shortest_path, shared_cases)",
            },
            "name_b": {
                "type": "string",
                "description": "Name of the second person (for shortest_path and shared_cases only)",
            },
            "district": {
                "type": "string",
                "description": "District name filter (for degree_centrality only)",
            },
        },
        "required": ["query_type"],
    }

    async def execute(self, **kwargs: Any) -> ToolResult:
        query_type = kwargs.get("query_type", "")
        if query_type not in CYPHER_TEMPLATES:
            return ToolResult(
                success=False,
                error=f"Unknown query_type '{query_type}'. Valid types: {list(CYPHER_TEMPLATES.keys())}",
            )

        params = self._build_params(query_type, kwargs)
        if isinstance(params, str):
            return ToolResult(success=False, error=params)

        cypher = CYPHER_TEMPLATES[query_type]

        try:
            rows = await asyncio.wait_for(
                self._run_query(cypher, params),
                timeout=QUERY_TIMEOUT,
            )
        except TimeoutError:
            return ToolResult(
                success=False,
                error=f"Graph query timed out after {QUERY_TIMEOUT}s",
            )
        except Exception as exc:
            return ToolResult(success=False, error=f"Graph query failed: {exc}")

        summary = self._format_summary(query_type, rows, kwargs)
        structured = [dict(r) for r in rows]

        return ToolResult(
            success=True,
            data=summary,
            metadata={
                "cypher": cypher,
                "parameters": params,
                "row_count": len(rows),
                "query_type": query_type,
                "structured": structured,
            },
        )

    def _build_params(self, query_type: str, kwargs: dict) -> dict | str:
        limit = MAX_RESULTS
        if query_type in ("neighbors_1hop", "network_2hop"):
            name = kwargs.get("name_a", "")
            if not name:
                return "name_a is required for this query type"
            return {"name": name, "limit": limit}
        if query_type == "shortest_path":
            name_a = kwargs.get("name_a", "")
            name_b = kwargs.get("name_b", "")
            if not name_a or not name_b:
                return "Both name_a and name_b are required for shortest_path"
            return {"name_a": name_a, "name_b": name_b}
        if query_type == "degree_centrality":
            district = kwargs.get("district", "")
            return {"district": district, "limit": limit}
        if query_type == "shared_cases":
            name_a = kwargs.get("name_a", "")
            name_b = kwargs.get("name_b", "")
            if not name_a or not name_b:
                return "Both name_a and name_b are required for shared_cases"
            return {"name_a": name_a, "name_b": name_b, "limit": limit}
        return "Invalid query_type"

    async def _run_query(self, cypher: str, params: dict) -> list[dict]:
        from app.db.neo4j import async_run_query as _async_run_query
        return await _async_run_query(cypher, params)

    def _format_summary(self, query_type: str, rows: list[dict], kwargs: dict) -> str:
        if not rows:
            return "No results found in the graph database."

        if query_type == "neighbors_1hop":
            person = kwargs.get("name_a", "Unknown")
            connections = []
            for r in rows:
                connections.append(
                    f"- {r.get('neighbor_name', 'Unknown')} ({r.get('neighbor_type', '?')}) "
                    f"via {r.get('relationship', '?')}"
                )
            return f"Connections for '{person}':\n" + "\n".join(connections)

        if query_type == "network_2hop":
            person = kwargs.get("name_a", "Unknown")
            return f"Network for '{person}': {len(rows)} paths found.\n" + "\n".join(
                f"- Path: {' -> '.join(str(n) for n in r.get('node_path', []))}"
                for r in rows[:20]
            )

        if query_type == "shortest_path":
            r = rows[0]
            hops = r.get("hops", "?")
            path = " -> ".join(str(n) for n in r.get("path_nodes", []))
            rels = ", ".join(r.get("relationships", []))
            return (
                f"Shortest path between '{r.get('person_a')}' and '{r.get('person_b')}':\n"
                f"  {hops} hops: {path}\n"
                f"  Relationships: {rels}"
            )

        if query_type == "degree_centrality":
            lines = []
            for r in rows:
                lines.append(f"- {r.get('name', '?')} (ID: {r.get('pg_id', '?')}): {r.get('degree', 0)} connections")
            return f"Top repeat offenders:\n" + "\n".join(lines)

        if query_type == "shared_cases":
            lines = []
            for r in rows:
                lines.append(
                    f"- Case {r.get('case_no', '?')} ({r.get('crime_no', '?')}): "
                    f"{r.get('date', '?')}, Status: {r.get('status', '?')}"
                )
            a = rows[0].get("person_a", "?") if rows else "?"
            b = rows[0].get("person_b", "?") if rows else "?"
            return f"Cases linking '{a}' and '{b}':\n" + "\n".join(lines)

        return f"Query returned {len(rows)} results."
