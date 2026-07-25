from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from app.db.sync import _sync_cases, _sync_persons, sync_all


class TestSyncCases:
    @pytest.mark.asyncio
    async def test_sync_cases_empty(self) -> None:
        with patch("app.db.sync._fetch_all", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = []
            count = await _sync_cases()
            assert count == 0

    @pytest.mark.asyncio
    async def test_sync_cases_with_data(self) -> None:
        with (
            patch("app.db.sync._fetch_all", new_callable=AsyncMock) as mock_fetch,
            patch("app.db.sync.run_write") as mock_write,
        ):
            mock_fetch.return_value = [{"pg_id": 1, "case_no": "KA-001", "status": "Open"}]
            count = await _sync_cases()
            assert count == 1
            mock_write.assert_called_once()


class TestSyncPersons:
    @pytest.mark.asyncio
    async def test_sync_persons_empty(self) -> None:
        with patch("app.db.sync._fetch_all", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = []
            count = await _sync_persons()
            assert count == 0


class TestSyncAll:
    @pytest.mark.asyncio
    async def test_sync_all_calls_all_syncers(self) -> None:
        with patch.multiple(
            "app.db.sync",
            _sync_cases=AsyncMock(return_value=5),
            _sync_persons=AsyncMock(return_value=10),
            _sync_employees=AsyncMock(return_value=3),
            _sync_police_stations=AsyncMock(return_value=2),
            _sync_courts=AsyncMock(return_value=1),
            _sync_case_relationships=AsyncMock(return_value=8),
            _sync_co_accused=AsyncMock(return_value=4),
        ):
            stats = await sync_all()
            assert stats["cases"] == 5
            assert stats["persons"] == 10
            assert stats["employees"] == 3
            assert stats["co_accused"] == 4
