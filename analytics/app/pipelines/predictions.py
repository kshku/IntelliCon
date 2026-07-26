from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

import numpy as np
from dateutil.relativedelta import relativedelta
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models import AnalyticsPrediction
from app.registry import register_job

logger = logging.getLogger(__name__)

MODEL_VERSION = "v1.0"


def _crime_forecast(session: Session) -> list[dict]:
    """Forecast monthly crime counts for next 3 months using linear regression."""
    rows = session.execute(
        text(
            "SELECT DATE_TRUNC('month', TO_DATE(crime_registered_date, 'YYYY-MM-DD')) AS month, "
            "COUNT(*) AS cnt "
            "FROM case_master "
            "WHERE crime_registered_date IS NOT NULL "
            "GROUP BY month ORDER BY month"
        )
    ).fetchall()

    if len(rows) < 3:
        logger.warning("Not enough historical data for crime forecast (need >= 3 months)")
        return []

    months = np.arange(len(rows), dtype=float)
    counts = np.array([r[1] for r in rows], dtype=float)

    coeffs = np.polyfit(months, counts, 1)
    predictions = []
    last_month = rows[-1][0]
    if isinstance(last_month, datetime):
        base_date = last_month.replace(tzinfo=UTC)
    else:
        base_date = datetime(last_month.year, last_month.month, 1, tzinfo=UTC)

    for i in range(1, 4):
        next_month = base_date + relativedelta(months=i)
        predicted = max(0, float(np.polyval(coeffs, len(rows) - 1 + i)))
        residuals = counts - np.polyval(coeffs, months)
        rmse = float(np.sqrt(np.mean(residuals**2)))
        confidence = max(0.0, 1.0 - (rmse / max(predicted, 1.0)))

        predictions.append(
            {
                "prediction_type": "crime_forecast",
                "entity_type": "district",
                "entity_id": None,
                "prediction_value": round(predicted, 2),
                "confidence": round(min(confidence, 0.99), 4),
                "period_date": next_month,
                "model_version": MODEL_VERSION,
            }
        )

    return predictions


def _recidivism_scoring(session: Session) -> list[dict]:
    """Score accused persons based on prior record."""
    rows = session.execute(
        text(
            "SELECT a.accused_id, a.name, COUNT(DISTINCT cm.case_id) AS case_count "
            "FROM accused a "
            "JOIN case_master cm ON cm.case_id = a.case_id "
            "GROUP BY a.accused_id, a.name"
        )
    ).fetchall()

    predictions = []
    for row in rows:
        accused_id, _, case_count = row[0], row[1], row[2]
        if case_count <= 1:
            risk = 0.1
        elif case_count <= 3:
            risk = 0.3 + (case_count - 1) * 0.15
        else:
            risk = min(0.9, 0.6 + (case_count - 3) * 0.1)

        predictions.append(
            {
                "prediction_type": "recidivism_risk",
                "entity_type": "person",
                "entity_id": accused_id,
                "prediction_value": round(risk, 4),
                "confidence": round(min(0.95, 0.5 + case_count * 0.05), 4),
                "period_date": datetime.now(UTC),
                "model_version": MODEL_VERSION,
            }
        )

    return predictions


def _resolution_time(session: Session) -> list[dict]:
    """Estimate resolution time per case category based on historical averages."""
    rows = session.execute(
        text(
            "SELECT cc.case_category_id, cc.category_name, "
            "AVG(EXTRACT(EPOCH FROM (NOW()::date - "
            "TO_DATE(cm.crime_registered_date, 'YYYY-MM-DD'))) / 86400) "
            "AS avg_days, "
            "COUNT(*) AS sample_size "
            "FROM case_master cm "
            "JOIN case_category cc ON cc.case_category_id = cm.case_category_id "
            "WHERE cm.crime_registered_date IS NOT NULL "
            "GROUP BY cc.case_category_id, cc.category_name "
            "HAVING COUNT(*) >= 3"
        )
    ).fetchall()

    predictions = []
    for row in rows:
        cat_id, _, avg_days, sample_size = row[0], row[1], row[2] or 0, row[3]
        confidence = min(0.95, sample_size / (sample_size + 10))

        predictions.append(
            {
                "prediction_type": "resolution_time",
                "entity_type": "case",
                "entity_id": cat_id,
                "prediction_value": round(float(avg_days), 2),
                "confidence": round(confidence, 4),
                "period_date": datetime.now(UTC),
                "model_version": MODEL_VERSION,
            }
        )

    return predictions


def _seasonal_patterns(session: Session) -> list[dict]:
    """Detect seasonal spikes in crime by month."""
    rows = session.execute(
        text(
            "SELECT EXTRACT(MONTH FROM TO_DATE(crime_registered_date, 'YYYY-MM-DD')) AS month_num, "
            "COUNT(*) AS cnt "
            "FROM case_master "
            "WHERE crime_registered_date IS NOT NULL "
            "GROUP BY month_num ORDER BY month_num"
        )
    ).fetchall()

    if not rows:
        return []

    counts = {int(r[0]): r[1] for r in rows}
    total = sum(counts.values())
    if total == 0:
        return []

    avg_per_month = total / 12
    predictions = []

    for month_num in range(1, 13):
        count = counts.get(month_num, 0)
        seasonal_index = count / avg_per_month if avg_per_month > 0 else 1.0

        predictions.append(
            {
                "prediction_type": "seasonal_pattern",
                "entity_type": "district",
                "entity_id": month_num,
                "prediction_value": round(seasonal_index, 4),
                "confidence": round(min(0.95, count / max(avg_per_month, 1)), 4),
                "period_date": datetime.now(UTC),
                "model_version": MODEL_VERSION,
            }
        )

    return predictions


@register_job(
    "predictive_analytics",
    schedule="cron",
    description=(
        "Generate crime forecasts, recidivism scores, "
        "resolution estimates, and seasonal patterns"
    ),
    day_of_week="sun",
    hour=4,
    minute=0,
)
class PredictiveAnalyticsPipeline:
    name = "predictive_analytics"
    description = (
        "Generate crime forecasts, recidivism scores, "
        "resolution estimates, and seasonal patterns"
    )

    def run(self, session: Session) -> dict[str, Any]:
        logger.info("Running predictive analytics pipeline...")

        all_predictions = []

        for name, fn in [
            ("crime_forecast", _crime_forecast),
            ("recidivism_risk", _recidivism_scoring),
            ("resolution_time", _resolution_time),
            ("seasonal_pattern", _seasonal_patterns),
        ]:
            try:
                preds = fn(session)
                all_predictions.extend(preds)
                logger.info(f"  {name}: generated {len(preds)} predictions")
            except Exception:
                logger.exception(f"  {name}: failed")

        for p in all_predictions:
            session.add(AnalyticsPrediction(**p))

        session.commit()
        logger.info(f"Total predictions stored: {len(all_predictions)}")

        return {
            "rows_processed": len(all_predictions),
            "predictions_generated": len(all_predictions),
        }
