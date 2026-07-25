from __future__ import annotations

import asyncio
import logging
from collections.abc import Generator
from contextlib import contextmanager

from neo4j import Driver, GraphDatabase

from app.config import settings

logger = logging.getLogger(__name__)

_driver: Driver | None = None


def get_driver() -> Driver:
    global _driver
    if _driver is None:
        _driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
        )
    return _driver


@contextmanager
def get_session() -> Generator:
    driver = get_driver()
    session = driver.session()
    try:
        yield session
    finally:
        session.close()


def close_driver() -> None:
    global _driver
    if _driver is not None:
        _driver.close()
        _driver = None


def run_query(cypher: str, parameters: dict | None = None) -> list[dict]:
    with get_session() as session:
        result = session.run(cypher, parameters or {})
        return [dict(record) for record in result]


def run_write(cypher: str, parameters: dict | None = None) -> list[dict]:
    with get_session() as session:
        result = session.execute_write(lambda tx: tx.run(cypher, parameters or {}).data())
        return result


async def async_run_query(cypher: str, parameters: dict | None = None) -> list[dict]:
    return await asyncio.to_thread(run_query, cypher, parameters)


async def async_run_write(cypher: str, parameters: dict | None = None) -> list[dict]:
    return await asyncio.to_thread(run_write, cypher, parameters)
