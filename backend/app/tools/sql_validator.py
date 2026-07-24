from __future__ import annotations

import re

import sqlparse
from sqlparse.sql import Identifier, IdentifierList
from sqlparse.tokens import DML, Keyword

ALLOWED_TABLES: set[str] = {
    "case_master",
    "complainant_details",
    "victim",
    "accused",
    "arrest_surrender",
    "act_section_association",
    "chargesheet_details",
    "state",
    "district",
    "unit",
    "court",
    "rank",
    "designation",
    "employee",
    "case_category",
    "gravity_offence",
    "case_status_master",
    "crime_head",
    "crime_sub_head",
    "act",
    "section",
    "crime_head_act_section",
    "caste_master",
    "religion_master",
    "occupation_master",
}

ALLOWED_COLUMNS: dict[str, set[str]] = {
    "case_master": {
        "case_id", "case_no", "crime_no", "crime_registered_date",
        "police_person_id", "police_station_id", "case_category_id",
        "gravity_offence_id", "crime_major_head_id", "crime_minor_head_id",
        "case_status_id", "court_id", "incident_from_date", "incident_to_date",
        "latitude", "longitude", "brief_facts",
    },
    "complainant_details": {
        "complainant_id", "case_id", "name", "age", "gender", "address", "phone",
    },
    "victim": {
        "victim_id", "case_id", "name", "age", "gender", "address",
        "caste_id", "religion_id", "occupation_id",
    },
    "accused": {
        "accused_id", "case_id", "name", "age", "gender", "address",
        "caste_id", "religion_id", "occupation_id",
    },
    "arrest_surrender": {
        "arrest_id", "case_id", "accused_name", "arrest_date",
        "surrender_date", "arrested_by",
    },
    "act_section_association": {"id", "case_id", "act_id", "section_id"},
    "chargesheet_details": {
        "chargesheet_id", "case_id", "chargesheet_date",
        "investigating_officer", "chargesheet_number",
    },
    "state": {"state_id", "state_name"},
    "district": {"district_id", "district_name", "state_id"},
    "unit": {"unit_id", "unit_name", "unit_type", "district_id"},
    "court": {"court_id", "court_name", "court_type"},
    "rank": {"rank_id", "rank_name"},
    "designation": {"designation_id", "designation_name"},
    "employee": {
        "employee_id", "name", "badge_number", "rank_id",
        "designation_id", "unit_id",
    },
    "case_category": {"case_category_id", "category_name"},
    "gravity_offence": {"gravity_offence_id", "gravity_name"},
    "case_status_master": {"case_status_id", "status_name"},
    "crime_head": {"crime_head_id", "head_name"},
    "crime_sub_head": {"crime_sub_head_id", "sub_head_name", "crime_head_id"},
    "act": {"act_id", "act_name"},
    "section": {"section_id", "section_number", "description", "act_id"},
    "crime_head_act_section": {"id", "crime_head_id", "act_id", "section_id"},
    "caste_master": {"caste_id", "caste_name"},
    "religion_master": {"religion_id", "religion_name"},
    "occupation_master": {"occupation_id", "occupation_name"},
}


class SqlValidationError(Exception):
    pass


def _extract_table_names(parsed: sqlparse.sql.Statement) -> set[str]:
    tables: set[str] = set()
    from_seen = False

    for token in parsed.tokens:
        if token.ttype is Keyword and token.normalized in ("FROM", "JOIN"):
            from_seen = True
            continue
        if from_seen:
            if isinstance(token, IdentifierList):
                for identifier in token.get_identifiers():
                    name = identifier.get_real_name()
                    if name:
                        tables.add(name.lower())
                from_seen = False
            elif isinstance(token, Identifier):
                name = token.get_real_name()
                if name:
                    tables.add(name.lower())
                from_seen = False
            elif token.ttype is not sqlparse.tokens.Whitespace:
                from_seen = False

    return tables


def _check_subqueries(sql: str) -> None:
    select_count = 0
    for match in re.finditer(r"SELECT\b", sql, re.IGNORECASE):
        select_count += 1
    if select_count > 1:
        raise SqlValidationError("Multiple SELECT statements not allowed")


def validate_sql(sql: str) -> str:
    if not sql or not sql.strip():
        raise SqlValidationError("Empty SQL query")

    sql = sql.strip().rstrip(";")

    parsed_list = sqlparse.parse(sql)
    if not parsed_list:
        raise SqlValidationError("Could not parse SQL")

    stmt = parsed_list[0]

    stmt_type = stmt.get_type()
    if stmt_type and stmt_type.upper() != "SELECT":
        raise SqlValidationError(
            f"Only SELECT queries are allowed. Got: {stmt_type.upper()}"
        )

    if not stmt_type:
        for token in stmt.tokens:
            if token.ttype is DML and token.normalized.upper() != "SELECT":
                raise SqlValidationError(
                    f"Only SELECT queries are allowed. Got: {token.normalized.upper()}"
                )

    _check_subqueries(sql)

    tables = _extract_table_names(stmt)
    invalid_tables = tables - ALLOWED_TABLES
    if invalid_tables:
        raise SqlValidationError(
            f"Unknown tables: {', '.join(sorted(invalid_tables))}. "
            f"Allowed: {', '.join(sorted(ALLOWED_TABLES))}"
        )

    if re.search(r"--|/\*|\*/", sql):
        raise SqlValidationError("SQL comments are not allowed")

    if ";" in sql:
        raise SqlValidationError("Multiple statements (semicolons) not allowed")

    return sql
