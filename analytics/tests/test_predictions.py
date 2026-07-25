from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import numpy as np

from app.pipelines.predictions import (
    PredictiveAnalyticsPipeline,
    _crime_forecast,
    _recidivism_scoring,
    _resolution_time,
    _seasonal_patterns,
)


def _make_session(rows):
    session = MagicMock()
    result = MagicMock()
    result.fetchall.return_value = rows
    session.execute.return_value = result
    return session


def test_crime_forecast_insufficient_data():
    session = _make_session([(datetime(2024, 1, 1), 10)])
    assert _crime_forecast(session) == []


def test_crime_forecast_generates_predictions():
    months = [
        (datetime(2024, 1, 1), 50),
        (datetime(2024, 2, 1), 55),
        (datetime(2024, 3, 1), 60),
        (datetime(2024, 4, 1), 65),
        (datetime(2024, 5, 1), 70),
    ]
    session = _make_session(months)
    preds = _crime_forecast(session)
    assert len(preds) == 3
    assert all(p["prediction_type"] == "crime_forecast" for p in preds)
    assert all(p["entity_type"] == "district" for p in preds)
    assert all(0 <= p["confidence"] <= 1 for p in preds)
    assert all(p["prediction_value"] >= 0 for p in preds)


def test_crime_forecast_trending_up():
    months = [(datetime(2024, i, 1), i * 10) for i in range(1, 13)]
    session = _make_session(months)
    preds = _crime_forecast(session)
    assert len(preds) == 3
    assert preds[0]["prediction_value"] > months[-1][1]


def test_recidivism_scoring_no_records():
    session = _make_session([])
    assert _recidivism_scoring(session) == []


def test_recidivism_scoring_single_case():
    session = _make_session([(1, "John", 1)])
    preds = _recidivism_scoring(session)
    assert len(preds) == 1
    assert preds[0]["prediction_value"] == 0.1
    assert preds[0]["entity_type"] == "person"
    assert preds[0]["entity_id"] == 1


def test_recidivism_scoring_high_risk():
    session = _make_session([(1, "John", 10)])
    preds = _recidivism_scoring(session)
    assert len(preds) == 1
    assert preds[0]["prediction_value"] > 0.8


def test_resolution_time_no_data():
    session = _make_session([])
    assert _resolution_time(session) == []


def test_resolution_time_generates_predictions():
    rows = [
        (1, "Theft", 45.5, 20),
        (2, "Assault", 120.3, 15),
        (3, "Fraud", 30.0, 5),
    ]
    session = _make_session(rows)
    preds = _resolution_time(session)
    assert len(preds) == 3
    assert all(p["prediction_type"] == "resolution_time" for p in preds)
    assert all(p["entity_type"] == "case" for p in preds)
    assert preds[0]["prediction_value"] == 45.5
    assert preds[0]["entity_id"] == 1


def test_seasonal_patterns_no_data():
    session = _make_session([])
    assert _seasonal_patterns(session) == []


def test_seasonal_patterns_all_months():
    rows = [(i, i * 100) for i in range(1, 13)]
    session = _make_session(rows)
    preds = _seasonal_patterns(session)
    assert len(preds) == 12
    assert all(p["prediction_type"] == "seasonal_pattern" for p in preds)
    assert all(p["entity_type"] == "district" for p in preds)
    assert all(p["entity_id"] == i for i, p in enumerate(preds, 1))


def test_seasonal_patterns_spike_detection():
    rows = [(1, 10), (2, 10), (3, 10), (4, 10), (5, 10), (6, 100),
            (7, 10), (8, 10), (9, 10), (10, 10), (11, 10), (12, 10)]
    session = _make_session(rows)
    preds = _seasonal_patterns(session)
    june = next(p for p in preds if p["entity_id"] == 6)
    january = next(p for p in preds if p["entity_id"] == 1)
    assert june["prediction_value"] > january["prediction_value"]


def test_pipeline_run():
    session = MagicMock()
    with patch("app.pipelines.predictions._crime_forecast", return_value=[
        {"prediction_type": "crime_forecast", "entity_type": "district",
         "entity_id": None, "prediction_value": 100.0, "confidence": 0.8,
         "period_date": datetime.now(timezone.utc), "model_version": "v1.0"}
    ]), patch("app.pipelines.predictions._recidivism_scoring", return_value=[]), \
         patch("app.pipelines.predictions._resolution_time", return_value=[]), \
         patch("app.pipelines.predictions._seasonal_patterns", return_value=[]):
        pipeline = PredictiveAnalyticsPipeline()
        result = pipeline.run(session)
        assert result["rows_processed"] == 1
        assert result["predictions_generated"] == 1
        assert session.add.call_count == 1
        assert session.commit.call_count == 1
