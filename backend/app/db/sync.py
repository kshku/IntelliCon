from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import text

from app.db.neo4j import async_run_write

logger = logging.getLogger(__name__)

BATCH_SIZE = 500


async def sync_all() -> dict[str, int]:
    from neo4j.exceptions import ServiceUnavailable
    stats: dict[str, int] = {}
    try:
        stats["cases"] = await _sync_cases()
        stats["persons"] = await _sync_persons()
        stats["employees"] = await _sync_employees()
        stats["police_stations"] = await _sync_police_stations()
        stats["courts"] = await _sync_courts()
        stats["case_relationships"] = await _sync_case_relationships()
        stats["co_accused"] = await _sync_co_accused()
        logger.info("Sync complete: %s", stats)
    except ServiceUnavailable as exc:
        logger.warning("Neo4j database is offline. Skipping graph sync: %s", exc)
    except Exception as exc:
        logger.error("Failed to sync data to Neo4j: %s", exc)
    return stats


async def _fetch_all(query: str) -> list[dict[str, Any]]:
    from app.db.session import async_session

    async with async_session() as session:
        result = await session.execute(text(query))
        return [dict(row._mapping) for row in result.fetchall()]


async def _sync_cases() -> int:
    rows = await _fetch_all("""
        SELECT
            cm.case_id AS pg_id,
            cm.case_no,
            cm.crime_no,
            cm.crime_registered_date,
            cm.incident_from_date,
            cm.incident_to_date,
            cm.latitude,
            cm.longitude,
            cm.brief_facts,
            csm.status_name AS status
        FROM case_master cm
        LEFT JOIN case_status_master csm ON cm.case_status_id = csm.case_status_id
    """)
    if not rows:
        return 0

    await async_run_write(
        """
        UNWIND $batch AS row
        MERGE (c:Case {pg_id: row.pg_id})
        SET c.case_no = row.case_no,
            c.crime_no = row.crime_no,
            c.crime_registered_date = row.crime_registered_date,
            c.incident_from_date = row.incident_from_date,
            c.incident_to_date = row.incident_to_date,
            c.latitude = row.latitude,
            c.longitude = row.longitude,
            c.brief_facts = row.brief_facts,
            c.status = row.status
    """,
        {"batch": rows},
    )
    return len(rows)


async def _sync_persons() -> int:
    total = 0
    total += await _sync_persons_by_role("accused", "ACCUSED")
    total += await _sync_persons_by_role("victim", "VICTIM")
    total += await _sync_persons_by_role("complainant_details", "COMPLAINANT")
    return total


async def _sync_persons_by_role(table: str, role: str) -> int:
    id_col = f"{table.split('_')[0]}_id"
    rows = await _fetch_all(f"""
        SELECT
            {id_col} AS pg_id,
            case_id,
            name,
            age,
            gender
        FROM {table}
    """)
    if not rows:
        return 0

    for row in rows:
        row["role"] = role

    await async_run_write(
        """
        UNWIND $batch AS row
        MERGE (p:Person {pg_id: row.pg_id, role: row.role})
        SET p.name = row.name,
            p.age = row.age,
            p.gender = row.gender
    """,
        {"batch": rows},
    )
    return len(rows)


async def _sync_employees() -> int:
    rows = await _fetch_all("""
        SELECT
            employee_id AS pg_id,
            name,
            badge_number
        FROM employee
    """)
    if not rows:
        return 0

    await async_run_write(
        """
        UNWIND $batch AS row
        MERGE (e:Employee {pg_id: row.pg_id})
        SET e.name = row.name,
            e.badge_number = row.badge_number
    """,
        {"batch": rows},
    )
    return len(rows)


async def _sync_police_stations() -> int:
    rows = await _fetch_all("""
        SELECT
            u.unit_id AS pg_id,
            u.unit_name AS name,
            d.district_name AS district
        FROM unit u
        JOIN district d ON u.district_id = d.district_id
    """)
    if not rows:
        return 0

    await async_run_write(
        """
        UNWIND $batch AS row
        MERGE (ps:PoliceStation {pg_id: row.pg_id})
        SET ps.name = row.name,
            ps.district = row.district
    """,
        {"batch": rows},
    )
    return len(rows)


async def _sync_courts() -> int:
    rows = await _fetch_all("""
        SELECT
            court_id AS pg_id,
            court_name AS name,
            court_type AS type
        FROM court
    """)
    if not rows:
        return 0

    await async_run_write(
        """
        UNWIND $batch AS row
        MERGE (ct:Court {pg_id: row.pg_id})
        SET ct.name = row.name,
            ct.type = row.type
    """,
        {"batch": rows},
    )
    return len(rows)


async def _sync_case_relationships() -> int:
    count = 0
    count += await _link_persons_to_cases("accused", "accused_id", "IMPLICATED_IN")
    count += await _link_persons_to_cases("victim", "victim_id", "VICTIM_OF")
    count += await _link_persons_to_cases("complainant_details", "complainant_id", "FILED_BY")
    count += await _link_arrests()
    count += await _link_case_io()
    count += await _link_case_court()
    count += await _link_case_station()
    return count


async def _link_persons_to_cases(table: str, id_col: str, rel_type: str) -> int:
    rows = await _fetch_all(f"""
        SELECT {id_col} AS person_id, case_id
        FROM {table}
    """)
    if not rows:
        return 0

    role = table.upper()
    if table == "complainant_details":
        role = "COMPLAINANT"

    await async_run_write(
        f"""
        UNWIND $batch AS row
        MATCH (p:Person {{pg_id: row.person_id, role: '{role}'}})
        MATCH (c:Case {{pg_id: row.case_id}})
        MERGE (p)-[r:{rel_type}]->(c)
    """,
        {"batch": rows},
    )
    return len(rows)


async def _link_arrests() -> int:
    rows = await _fetch_all("""
        SELECT a.accused_name AS name, a.case_id, a.arrest_date
        FROM arrest_surrender a
        WHERE a.arrest_date IS NOT NULL
    """)
    if not rows:
        return 0

    await async_run_write(
        """
        UNWIND $batch AS row
        MATCH (p:Person {name: row.name, role: 'ACCUSED'})
        MATCH (c:Case {pg_id: row.case_id})
        MERGE (p)-[r:ARRESTED_IN]->(c)
        SET r.arrest_date = row.arrest_date
    """,
        {"batch": rows},
    )
    return len(rows)


async def _link_case_io() -> int:
    rows = await _fetch_all("""
        SELECT cm.case_id, cm.police_person_id
        FROM case_master cm
        WHERE cm.police_person_id IS NOT NULL
    """)
    if not rows:
        return 0

    await async_run_write(
        """
        UNWIND $batch AS row
        MATCH (e:Employee {pg_id: row.police_person_id})
        MATCH (c:Case {pg_id: row.case_id})
        MERGE (c)-[:INVESTIGATED_BY]->(e)
    """,
        {"batch": rows},
    )
    return len(rows)


async def _link_case_court() -> int:
    rows = await _fetch_all("""
        SELECT cm.case_id, cm.court_id
        FROM case_master cm
        WHERE cm.court_id IS NOT NULL
    """)
    if not rows:
        return 0

    await async_run_write(
        """
        UNWIND $batch AS row
        MATCH (c:Case {pg_id: row.case_id})
        MATCH (ct:Court {pg_id: row.court_id})
        MERGE (c)-[:TRIED_AT]->(ct)
    """,
        {"batch": rows},
    )
    return len(rows)


async def _link_case_station() -> int:
    rows = await _fetch_all("""
        SELECT cm.case_id, cm.police_station_id
        FROM case_master cm
        WHERE cm.police_station_id IS NOT NULL
    """)
    if not rows:
        return 0

    await async_run_write(
        """
        UNWIND $batch AS row
        MATCH (c:Case {pg_id: row.case_id})
        MATCH (ps:PoliceStation {pg_id: row.police_station_id})
        MERGE (c)-[:REGISTERED_AT]->(ps)
    """,
        {"batch": rows},
    )
    return len(rows)


async def _sync_co_accused() -> int:
    rows = await _fetch_all("""
        SELECT DISTINCT
            a1.accused_id AS person1_id,
            a2.accused_id AS person2_id
        FROM accused a1
        JOIN accused a2
            ON a1.case_id = a2.case_id
            AND a1.accused_id < a2.accused_id
    """)
    if not rows:
        return 0

    await async_run_write(
        """
        UNWIND $batch AS row
        MATCH (p1:Person {pg_id: row.person1_id, role: 'ACCUSED'})
        MATCH (p2:Person {pg_id: row.person2_id, role: 'ACCUSED'})
        MERGE (p1)-[:CO_ACCUSED]-(p2)
    """,
        {"batch": rows},
    )
    return len(rows)
