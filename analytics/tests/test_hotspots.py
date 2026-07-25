from unittest.mock import MagicMock, patch

from app.pipelines.hotspots import (
    HotspotDetectionPipeline,
    _haversine_km,
    _classify_severity,
    _cluster_cases,
    _compute_radius_km,
    _dominant_crime_type,
    _fetch_cases,
)


def test_haversine_km_same_point():
    assert _haversine_km(12.97, 77.59, 12.97, 77.59) == 0.0


def test_haversine_km_known_distance():
    d = _haversine_km(12.97, 77.59, 13.0, 77.6)
    assert 1.0 < d < 5.0


def test_haversine_km_far_apart():
    d = _haversine_km(12.97, 77.59, 28.61, 77.23)
    assert 1500 < d < 1900


def test_classify_severity_heinous():
    assert _classify_severity("Murder") == "heinous"
    assert _classify_severity("Rape and sexual assault") == "heinous"
    assert _classify_severity("Kidnapping for ransom") == "heinous"
    assert _classify_severity("Arson and property damage") == "heinous"


def test_classify_severity_non_heinous():
    assert _classify_severity("Theft") == "non-heinous"
    assert _classify_severity("Fraud") == "non-heinous"
    assert _classify_severity("Assault") == "non-heinous"


def test_classify_severity_none():
    assert _classify_severity(None) == "non-heinous"
    assert _classify_severity("") == "non-heinous"


def test_cluster_cases_empty():
    assert _cluster_cases([]) == {}


def test_cluster_cases_single_point():
    cases = [{"case_id": 1, "latitude": 12.97, "longitude": 77.59,
              "crime_type": "Theft", "crime_registered_date": "2026-07-01"}]
    clusters = _cluster_cases(cases)
    assert len(clusters) == 0


def test_cluster_cases_dense_cluster():
    cases = [
        {"case_id": 1, "latitude": 12.9700, "longitude": 77.5900, "crime_type": "Theft", "crime_registered_date": "2026-07-01"},
        {"case_id": 2, "latitude": 12.9701, "longitude": 77.5901, "crime_type": "Theft", "crime_registered_date": "2026-07-01"},
        {"case_id": 3, "latitude": 12.9702, "longitude": 77.5902, "crime_type": "Theft", "crime_registered_date": "2026-07-01"},
        {"case_id": 4, "latitude": 12.9703, "longitude": 77.5903, "crime_type": "Theft", "crime_registered_date": "2026-07-01"},
        {"case_id": 5, "latitude": 12.9704, "longitude": 77.5904, "crime_type": "Theft", "crime_registered_date": "2026-07-01"},
    ]
    clusters = _cluster_cases(cases)
    assert len(clusters) >= 1
    total_in_clusters = sum(len(v) for v in clusters.values())
    assert total_in_clusters == 5


def test_cluster_cases_two_separate_groups():
    cases = [
        {"case_id": 1, "latitude": 12.97, "longitude": 77.59, "crime_type": "Theft", "crime_registered_date": "2026-07-01"},
        {"case_id": 2, "latitude": 12.9701, "longitude": 77.5901, "crime_type": "Theft", "crime_registered_date": "2026-07-01"},
        {"case_id": 3, "latitude": 12.9702, "longitude": 77.5902, "crime_type": "Theft", "crime_registered_date": "2026-07-01"},
        {"case_id": 4, "latitude": 13.50, "longitude": 78.50, "crime_type": "Fraud", "crime_registered_date": "2026-07-01"},
        {"case_id": 5, "latitude": 13.5001, "longitude": 78.5001, "crime_type": "Fraud", "crime_registered_date": "2026-07-01"},
        {"case_id": 6, "latitude": 13.5002, "longitude": 78.5002, "crime_type": "Fraud", "crime_registered_date": "2026-07-01"},
    ]
    clusters = _cluster_cases(cases)
    assert len(clusters) >= 2


def test_compute_radius_km_small_cluster():
    cases = [
        {"latitude": 12.970, "longitude": 77.590},
        {"latitude": 12.980, "longitude": 77.600},
    ]
    r = _compute_radius_km(cases)
    assert 0.5 < r < 1.5


def test_compute_radius_km_single_point():
    cases = [{"latitude": 12.97, "longitude": 77.59}]
    assert _compute_radius_km(cases) == 0.0


def test_dominant_crime_type():
    cases = [
        {"crime_type": "Theft"},
        {"crime_type": "Theft"},
        {"crime_type": "Theft"},
        {"crime_type": "Fraud"},
    ]
    assert _dominant_crime_type(cases) == "Theft"


def test_dominant_crime_type_no_types():
    cases = [{"crime_type": None}, {"crime_type": None}]
    assert _dominant_crime_type(cases) == "unknown"


def test_fetch_cases_empty():
    session = MagicMock()
    result = MagicMock()
    result.fetchall.return_value = []
    session.execute.return_value = result
    assert _fetch_cases(session, 30) == []


def test_fetch_cases_with_data():
    session = MagicMock()
    result = MagicMock()
    result.fetchall.return_value = [
        (1, 12.97, 77.59, 1, "Theft", "2026-07-01"),
        (2, 13.0, 77.6, 2, "Fraud", "2026-07-10"),
    ]
    session.execute.return_value = result
    cases = _fetch_cases(session, 30)
    assert len(cases) == 2
    assert cases[0]["latitude"] == 12.97
    assert cases[0]["crime_type"] == "Theft"


def test_pipeline_run_no_cases():
    session = MagicMock()
    with patch("app.pipelines.hotspots._fetch_cases", return_value=[]):
        pipeline = HotspotDetectionPipeline()
        result = pipeline.run(session)
        assert result["rows_processed"] == 0
        assert result["clusters_found"] == 0
        session.commit.assert_not_called()


def test_pipeline_run_with_clusters():
    cases = [
        {"case_id": 1, "latitude": 12.9700, "longitude": 77.5900, "crime_type": "Theft", "crime_registered_date": "2026-07-01"},
        {"case_id": 2, "latitude": 12.9701, "longitude": 77.5901, "crime_type": "Theft", "crime_registered_date": "2026-07-01"},
        {"case_id": 3, "latitude": 12.9702, "longitude": 77.5902, "crime_type": "Theft", "crime_registered_date": "2026-07-01"},
        {"case_id": 4, "latitude": 12.9703, "longitude": 77.5903, "crime_type": "Theft", "crime_registered_date": "2026-07-01"},
        {"case_id": 5, "latitude": 12.9704, "longitude": 77.5904, "crime_type": "Theft", "crime_registered_date": "2026-07-01"},
    ]
    session = MagicMock()
    with patch("app.pipelines.hotspots._fetch_cases", return_value=cases):
        pipeline = HotspotDetectionPipeline()
        result = pipeline.run(session)
        assert result["rows_processed"] == 5
        assert result["clusters_found"] >= 1
        assert result["hotspots_stored"] >= 1
        assert session.add.call_count >= 1
        session.commit.assert_called_once()
