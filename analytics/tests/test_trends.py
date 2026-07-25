from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from app.pipelines.trends import (
    TrendAnalysisPipeline,
    _month_key,
    _parse_date,
    _monthly_counts,
    _yoy_comparison,
    _moving_averages,
    _chargesheet_rates,
)


def _make_session(rows):
    session = MagicMock()
    result = MagicMock()
    result.fetchall.return_value = rows
    session.execute.return_value = result
    return session


def test_month_key_yyyy_mm_dd():
    assert _month_key("2026-07-15") == "2026-07"


def test_month_key_dd_mm_yyyy():
    assert _month_key("15-07-2026") == "2026-07"


def test_month_key_none():
    assert _month_key(None) is None


def test_month_key_empty():
    assert _month_key("") is None


def test_month_key_invalid():
    assert _month_key("not-a-date") is None


def test_parse_date_yyyy_mm_dd():
    dt = _parse_date("2026-07-15")
    assert dt == datetime(2026, 7, 15)


def test_parse_date_dd_mm_yyyy():
    dt = _parse_date("15-07-2026")
    assert dt == datetime(2026, 7, 15)


def test_parse_date_none():
    assert _parse_date(None) is None


def test_monthly_counts_empty():
    session = _make_session([])
    assert _monthly_counts(session) == []


def test_monthly_counts_generates_multi_dimension():
    rows = [
        (datetime(2026, 1, 1), "Mangaluru", "Theft", "FIR", 10),
        (datetime(2026, 1, 1), "Mangaluru", "Theft", "FIR", 5),
    ]
    session = _make_session(rows)
    trends = _monthly_counts(session)
    assert len(trends) == 6
    assert all(t["metric_type"] == "monthly_count" for t in trends)
    dims = {t["dimension"] for t in trends}
    assert dims == {"district", "crime_head", "category"}


def test_monthly_counts_values():
    rows = [(datetime(2026, 3, 1), "Bengaluru", "Murder", "Cognizable", 25)]
    session = _make_session(rows)
    trends = _monthly_counts(session)
    assert len(trends) == 3
    assert all(t["value"] == 25.0 for t in trends)


def test_yoy_comparison_empty():
    session = _make_session([])
    assert _yoy_comparison(session) == []


def test_yoy_comparison_with_data():
    rows = [
        (datetime(2026, 6, 1), "Mangaluru", 100, 80),
        (datetime(2026, 6, 1), "Mangaluru", 50, None),
    ]
    session = _make_session(rows)
    trends = _yoy_comparison(session)
    assert len(trends) == 2
    assert all(t["metric_type"] == "yoy_comparison" for t in trends)
    assert trends[0]["value"] == 25.0


def test_yoy_comparison_no_last_year():
    rows = [(datetime(2026, 6, 1), "Mangaluru", 50, None)]
    session = _make_session(rows)
    trends = _yoy_comparison(session)
    assert len(trends) == 1
    assert trends[0]["value"] == 0.0


def test_moving_averages_insufficient_data():
    rows = [(datetime(2026, 1, 1), 10), (datetime(2026, 2, 1), 20)]
    session = _make_session(rows)
    assert _moving_averages(session, 3) == []


def test_moving_averages_generates_results():
    rows = [
        (datetime(2026, 1, 1), 10),
        (datetime(2026, 2, 1), 20),
        (datetime(2026, 3, 1), 30),
        (datetime(2026, 4, 1), 40),
    ]
    session = _make_session(rows)
    trends = _moving_averages(session, 3)
    assert len(trends) == 2
    assert all(t["metric_type"] == "moving_avg_3m" for t in trends)
    assert trends[0]["value"] == 20.0
    assert trends[1]["value"] == 30.0


def test_moving_averages_6m():
    rows = [(datetime(2026, i, 1), i * 10) for i in range(1, 7)]
    session = _make_session(rows)
    trends = _moving_averages(session, 6)
    assert len(trends) == 1
    assert trends[0]["metric_type"] == "moving_avg_6m"
    assert trends[0]["value"] == 35.0


def test_chargesheet_rates_empty():
    session = _make_session([])
    assert _chargesheet_rates(session) == []


def test_chargesheet_rates_calculates_correctly():
    rows = [
        (datetime(2026, 1, 1), "Mangaluru", 100, 75),
        (datetime(2026, 1, 1), "Bengaluru", 200, 160),
    ]
    session = _make_session(rows)
    trends = _chargesheet_rates(session)
    assert len(trends) == 2
    assert all(t["metric_type"] == "chargesheet_rate" for t in trends)
    assert trends[0]["value"] == 75.0
    assert trends[1]["value"] == 80.0


def test_chargesheet_rates_zero_cases():
    rows = [(datetime(2026, 1, 1), "Mangaluru", 0, 0)]
    session = _make_session(rows)
    trends = _chargesheet_rates(session)
    assert len(trends) == 1
    assert trends[0]["value"] == 0.0


def test_pipeline_run():
    session = MagicMock()
    with patch("app.pipelines.trends._monthly_counts", return_value=[
        {"metric_type": "monthly_count", "dimension": "district",
         "dimension_value": "Mangaluru", "period_date": datetime(2026, 1, 1), "value": 100.0}
    ]), patch("app.pipelines.trends._yoy_comparison", return_value=[]), \
         patch("app.pipelines.trends._moving_averages", return_value=[]), \
         patch("app.pipelines.trends._chargesheet_rates", return_value=[]):
        pipeline = TrendAnalysisPipeline()
        result = pipeline.run(session)
        assert result["rows_processed"] == 1
        assert result["trends_computed"] == 1
        assert session.add.call_count == 1
        session.commit.assert_called_once()


def test_pipeline_run_mixed_results():
    session = MagicMock()
    with patch("app.pipelines.trends._monthly_counts", return_value=[
        {"metric_type": "monthly_count", "dimension": "district",
         "dimension_value": "A", "period_date": datetime(2026, 1, 1), "value": 10.0},
        {"metric_type": "monthly_count", "dimension": "crime_head",
         "dimension_value": "B", "period_date": datetime(2026, 1, 1), "value": 20.0},
    ]), patch("app.pipelines.trends._yoy_comparison", return_value=[
        {"metric_type": "yoy_comparison", "dimension": "district",
         "dimension_value": "A", "period_date": datetime(2026, 1, 1), "value": 5.0},
    ]), patch("app.pipelines.trends._moving_averages", return_value=[]), \
         patch("app.pipelines.trends._chargesheet_rates", return_value=[]):
        pipeline = TrendAnalysisPipeline()
        result = pipeline.run(session)
        assert result["rows_processed"] == 3
        assert session.add.call_count == 3
