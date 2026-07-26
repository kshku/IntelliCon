from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

from app.db.session import get_session
from app.main import app
from app.models import (
    Accused,
    CaseMaster,
    CaseStatusMaster,
    ComplainantDetails,
    CrimeHead,
    Unit,
    Victim,
)


def _make_mock_session(cases=None, case_details=None, is_empty_search=False):
    mock_session = AsyncMock()
    mock_session.add = MagicMock()  # Synchronous session method
    mock_result = MagicMock()

    if cases is not None:
        mock_result.scalars().all.return_value = cases
        mock_session.execute.return_value = mock_result
    elif case_details is not None:
        m_case, m_compl, m_acc, m_vic, m_unit, m_status, m_head = case_details

        r_case = MagicMock()
        r_case.scalar_one_or_none.return_value = m_case

        r_compl = MagicMock()
        r_compl.scalars().all.return_value = m_compl

        r_acc = MagicMock()
        r_acc.scalars().all.return_value = m_acc

        r_vic = MagicMock()
        r_vic.scalars().all.return_value = m_vic

        r_unit = MagicMock()
        r_unit.scalar_one_or_none.return_value = m_unit

        r_status = MagicMock()
        r_status.scalar_one_or_none.return_value = m_status

        r_head = MagicMock()
        r_head.scalar_one_or_none.return_value = m_head

        mock_session.execute.side_effect = [
            r_case,
            r_compl,
            r_acc,
            r_vic,
            r_unit,
            r_status,
            r_head,
        ]
    elif is_empty_search:
        mock_result.scalars().all.return_value = []
        mock_session.execute.return_value = mock_result
    else:
        r_empty = MagicMock()
        r_empty.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = r_empty

    return mock_session


def _get_client(session):
    async def dep():
        yield session

    app.dependency_overrides[get_session] = dep
    return TestClient(app)


def test_search_cases_empty():
    session = _make_mock_session(is_empty_search=True)
    client = _get_client(session)
    response = client.get("/cases/search?q=")
    assert response.status_code == 200
    assert response.json() == []


def test_search_cases_with_results():
    case = CaseMaster(
        case_id=12,
        case_no="FIR-0432/2026",
        crime_no="C-432",
        brief_facts="The accused stole some property.",
        crime_registered_date="2026-07-26",
    )

    session = _make_mock_session(cases=[case])
    client = _get_client(session)
    response = client.get("/cases/search?q=theft")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["case_no"] == "FIR-0432/2026"
    assert "stole some property" in data[0]["brief_facts"]


def test_get_case_details_success():
    case = CaseMaster(
        case_id=12,
        case_no="FIR-0432/2026",
        crime_no="C-432",
        brief_facts="Facts",
        latitude=12.9,
        longitude=77.5,
        police_station_id=1,
        case_status_id=2,
        crime_major_head_id=3,
    )

    compl = ComplainantDetails(name="John Doe", age=40, gender="Male")
    acc = Accused(name="Jane Smith", age=30, gender="Female")
    vic = Victim(name="Victim Name", age=22, gender="Male")
    unit = Unit(unit_name="Koramangala PS")
    status = CaseStatusMaster(status_name="Under Investigation")
    head = CrimeHead(head_name="Theft")

    session = _make_mock_session(case_details=(case, [compl], [acc], [vic], unit, status, head))
    client = _get_client(session)
    response = client.get("/cases/12")
    assert response.status_code == 200
    data = response.json()
    assert data["case_no"] == "FIR-0432/2026"
    assert data["station_name"] == "Koramangala PS"
    assert data["status_name"] == "Under Investigation"
    assert data["crime_type"] == "Theft"
    assert data["complainants"][0]["name"] == "John Doe"
    assert data["accused"][0]["name"] == "Jane Smith"
    assert data["victims"][0]["name"] == "Victim Name"


@patch("app.api.cases.sync_all", new_callable=AsyncMock)
def test_upload_cases_csv(mock_sync):
    session = _make_mock_session()
    client = _get_client(session)

    csv_data = (
        "case_no,crime_no,police_station,status,crime_head,"
        "latitude,longitude,brief_facts,complainant_name,accused_name\n"
        "FIR-9999/2026,C-9999,Indiranagar PS,Under Investigation,"
        "Theft,12.97,77.64,Stolen bike,Complainant Guy,Suspect Guy\n"
    )

    response = client.post(
        "/cases/upload",
        json={"file_content": csv_data, "filename": "data.csv"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["inserted_count"] == 1
    assert mock_sync.called
