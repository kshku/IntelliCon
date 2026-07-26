import asyncio
from unittest.mock import patch

import pytest

from app.tools.graph_query import CYPHER_TEMPLATES, QUERY_TIMEOUT, GraphQueryTool


@pytest.fixture
def tool():
    return GraphQueryTool()


def test_tool_metadata(tool):
    assert tool.name == "graph_query"
    assert "Cypher" not in tool.description
    assert "query_type" in tool.input_schema["properties"]


def test_tool_has_all_query_types(tool):
    expected = {
        "neighbors_1hop",
        "network_2hop",
        "shortest_path",
        "degree_centrality",
        "shared_cases",
    }
    actual = set(tool.input_schema["properties"]["query_type"]["enum"])
    assert actual == expected


def test_invalid_query_type(tool):
    result = asyncio.run(tool.execute(query_type="nonexistent"))
    assert not result.success
    assert "Unknown query_type" in result.error


def test_neighbors_missing_name(tool):
    result = asyncio.run(tool.execute(query_type="neighbors_1hop"))
    assert not result.success
    assert "name_a is required" in result.error


def test_shortest_path_missing_names(tool):
    result = asyncio.run(
        tool.execute(query_type="shortest_path", name_a="Alice")
    )
    assert not result.success
    assert "Both name_a and name_b" in result.error


def test_shared_cases_missing_names(tool):
    result = asyncio.run(
        tool.execute(query_type="shared_cases", name_a="Alice")
    )
    assert not result.success
    assert "Both name_a and name_b" in result.error


def test_neighbors_1hop_empty_results(tool):
    async def mock_run(cypher, params):
        return []

    with patch("app.db.neo4j.async_run_query", mock_run):
        result = asyncio.run(
            tool.execute(query_type="neighbors_1hop", name_a="Ravi")
        )
    assert result.success
    assert "No results found" in result.data
    assert result.metadata["row_count"] == 0
    assert result.metadata["query_type"] == "neighbors_1hop"


def test_neighbors_1hop_with_results(tool):
    async def mock_run(cypher, params):
        return [
            {
                "person": "Ravi Kumar",
                "person_role": "ACCUSED",
                "relationship": "IMPLICATED_IN",
                "neighbor_type": "Case",
                "neighbor_name": None,
                "neighbor_id": 101,
            },
            {
                "person": "Ravi Kumar",
                "person_role": "ACCUSED",
                "relationship": "CO_ACCUSED",
                "neighbor_type": "Person",
                "neighbor_name": "Suresh",
                "neighbor_id": 202,
            },
        ]

    with patch("app.db.neo4j.async_run_query", mock_run):
        result = asyncio.run(
            tool.execute(query_type="neighbors_1hop", name_a="Ravi")
        )
    assert result.success
    assert "Ravi" in result.data
    assert "Suresh" in result.data
    assert result.metadata["row_count"] == 2
    assert result.metadata["structured"][0]["relationship"] == "IMPLICATED_IN"


def test_shortest_path_found(tool):
    async def mock_run(cypher, params):
        return [
            {
                "person_a": "Ravi",
                "person_b": "Suresh",
                "hops": 3,
                "relationships": ["IMPLICATED_IN", "CO_ACCUSED"],
                "path_nodes": ["Ravi", "Case KA-001", "Suresh"],
            },
        ]

    with patch("app.db.neo4j.async_run_query", mock_run):
        result = asyncio.run(
            tool.execute(query_type="shortest_path", name_a="Ravi", name_b="Suresh")
        )
    assert result.success
    assert "3 hops" in result.data
    assert "Ravi" in result.data
    assert "Suresh" in result.data


def test_shortest_path_not_found(tool):
    async def mock_run(cypher, params):
        return []

    with patch("app.db.neo4j.async_run_query", mock_run):
        result = asyncio.run(
            tool.execute(query_type="shortest_path", name_a="Alice", name_b="Bob")
        )
    assert result.success
    assert "No results found" in result.data


def test_degree_centrality(tool):
    async def mock_run(cypher, params):
        return [
            {"name": "Ravi", "pg_id": 1, "degree": 12},
            {"name": "Suresh", "pg_id": 2, "degree": 8},
            {"name": "Manoj", "pg_id": 3, "degree": 5},
        ]

    with patch("app.db.neo4j.async_run_query", mock_run):
        result = asyncio.run(
            tool.execute(query_type="degree_centrality", district="Mangaluru")
        )
    assert result.success
    assert "Ravi" in result.data
    assert "12 connections" in result.data
    assert result.metadata["row_count"] == 3


def test_shared_cases(tool):
    async def mock_run(cypher, params):
        return [
            {
                "person_a": "Ravi",
                "person_b": "Suresh",
                "case_no": "KA-2024-001",
                "crime_no": "Cr.No.123/2024",
                "date": "2024-06-15",
                "status": "Under Investigation",
            },
            {
                "person_a": "Ravi",
                "person_b": "Suresh",
                "case_no": "KA-2024-005",
                "crime_no": "Cr.No.045/2024",
                "date": "2024-08-20",
                "status": "Chargesheet Filed",
            },
        ]

    with patch("app.db.neo4j.async_run_query", mock_run):
        result = asyncio.run(
            tool.execute(query_type="shared_cases", name_a="Ravi", name_b="Suresh")
        )
    assert result.success
    assert "Ravi" in result.data
    assert "Suresh" in result.data
    assert "KA-2024-001" in result.data
    assert "KA-2024-005" in result.data
    assert result.metadata["row_count"] == 2


def test_network_2hop(tool):
    async def mock_run(cypher, params):
        return [
            {
                "source": "Ravi",
                "rel_path": ["IMPLICATED_IN", "CO_ACCUSED"],
                "node_path": ["Ravi", "Case KA-001", "Suresh"],
                "node_types": ["Person", "Case", "Person"],
            },
        ]

    with patch("app.db.neo4j.async_run_query", mock_run):
        result = asyncio.run(
            tool.execute(query_type="network_2hop", name_a="Ravi")
        )
    assert result.success
    assert "Ravi" in result.data
    assert "1 paths found" in result.data


def test_timeout_error(tool):
    async def slow_run(cypher, params):
        await asyncio.sleep(60)
        return []

    with patch("app.db.neo4j.async_run_query", slow_run):
        result = asyncio.run(
            tool.execute(query_type="neighbors_1hop", name_a="Ravi")
        )
    assert not result.success
    assert "timed out" in result.error


def test_query_timeout_constant():
    assert QUERY_TIMEOUT == 30


def test_cypher_templates_complete():
    assert len(CYPHER_TEMPLATES) == 5
    for name, cypher in CYPHER_TEMPLATES.items():
        assert "MATCH" in cypher
        assert cypher.strip().endswith("LIMIT $limit") or name == "shortest_path"
