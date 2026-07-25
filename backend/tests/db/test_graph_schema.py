from app.db.graph_schema import GRAPH_SCHEMA, NODE_LABELS, RELATIONSHIPS


class TestGraphSchema:
    def test_has_constraints(self) -> None:
        assert "constraints" in GRAPH_SCHEMA
        assert len(GRAPH_SCHEMA["constraints"]) > 0

    def test_has_indexes(self) -> None:
        assert "indexes" in GRAPH_SCHEMA
        assert len(GRAPH_SCHEMA["indexes"]) > 0

    def test_constraints_are_cypher(self) -> None:
        for constraint in GRAPH_SCHEMA["constraints"]:
            assert "CREATE CONSTRAINT" in constraint
            assert "IS UNIQUE" in constraint

    def test_indexes_are_cypher(self) -> None:
        for idx in GRAPH_SCHEMA["indexes"]:
            assert "CREATE INDEX" in idx


class TestNodeLabels:
    def test_person_label(self) -> None:
        assert "Person" in NODE_LABELS
        assert "pg_id" in NODE_LABELS["Person"]["properties"]
        assert "name" in NODE_LABELS["Person"]["properties"]
        assert "role" in NODE_LABELS["Person"]["properties"]

    def test_case_label(self) -> None:
        assert "Case" in NODE_LABELS
        assert "pg_id" in NODE_LABELS["Case"]["properties"]
        assert "case_no" in NODE_LABELS["Case"]["properties"]

    def test_person_roles(self) -> None:
        roles = NODE_LABELS["Person"]["roles"]
        assert "ACCUSED" in roles
        assert "VICTIM" in roles
        assert "COMPLAINANT" in roles


class TestRelationships:
    def test_required_relationships(self) -> None:
        required = {
            "IMPLICATED_IN",
            "VICTIM_OF",
            "FILED_BY",
            "INVESTIGATED_BY",
            "ARRESTED_IN",
            "TRIED_AT",
            "REGISTERED_AT",
            "CO_ACCUSED",
        }
        assert required.issubset(set(RELATIONSHIPS))
