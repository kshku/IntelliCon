from __future__ import annotations

GRAPH_SCHEMA = {
    "constraints": [
        "CREATE CONSTRAINT IF NOT EXISTS FOR (p:Person) REQUIRE p.pg_id IS UNIQUE",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (c:Case) REQUIRE c.pg_id IS UNIQUE",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (ps:PoliceStation) REQUIRE ps.pg_id IS UNIQUE",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (ct:Court) REQUIRE ct.pg_id IS UNIQUE",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (e:Employee) REQUIRE e.pg_id IS UNIQUE",
    ],
    "indexes": [
        "CREATE INDEX IF NOT EXISTS FOR (p:Person) ON (p.name)",
        "CREATE INDEX IF NOT EXISTS FOR (c:Case) ON (c.case_no)",
        "CREATE INDEX IF NOT EXISTS FOR (c:Case) ON (c.crime_no)",
        "CREATE INDEX IF NOT EXISTS FOR (p:Person) ON (p.role)",
    ],
}

NODE_LABELS = {
    "Person": {
        "properties": ["pg_id", "name", "age", "gender", "role"],
        "roles": ["ACCUSED", "VICTIM", "COMPLAINANT"],
    },
    "Case": {
        "properties": [
            "pg_id",
            "case_no",
            "crime_no",
            "crime_registered_date",
            "incident_from_date",
            "incident_to_date",
            "latitude",
            "longitude",
            "brief_facts",
            "status",
        ],
    },
    "PoliceStation": {
        "properties": ["pg_id", "name", "district"],
    },
    "Court": {
        "properties": ["pg_id", "name", "type"],
    },
    "Employee": {
        "properties": ["pg_id", "name", "badge_number"],
    },
}

RELATIONSHIPS = [
    "IMPLICATED_IN",  # Accused → Case
    "VICTIM_OF",  # Victim → Case
    "FILED_BY",  # Complainant → Case
    "INVESTIGATED_BY",  # Case → Employee (IO)
    "ARRESTED_IN",  # Accused → Case (with arrest_date)
    "TRIED_AT",  # Case → Court
    "REGISTERED_AT",  # Case → PoliceStation
    "CO_ACCUSED",  # Accused ↔ Accused (via shared case)
]
