from __future__ import annotations

import logging
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models import AnalyticsTrend
from app.registry import register_job

logger = logging.getLogger(__name__)

LOOKBACK_MONTHS = 12


def _month_key(date_str: str) -> str | None:
    """Extract 'YYYY-MM' from a date string (YYYY-MM-DD or DD-MM-YYYY)."""
    if not date_str:
        return None
    for fmt in ("%Y-%m-%d", "%d-%m-%Y"):
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            return dt.strftime("%Y-%m")
        except ValueError:
            continue
    return None


def _parse_date(date_str: str) -> datetime | None:
    if not date_str:
        return None
    for fmt in ("%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    return None


def _monthly_counts(session: Session) -> list[dict]:
    """Monthly crime counts by district, crime head, and category."""
    rows = session.execute(
        text(
            "SELECT DATE_TRUNC('month', TO_DATE(cm.crime_registered_date, 'YYYY-MM-DD')) AS month, "
            "COALESCE(d.district_name, 'Unknown') AS district, "
            "COALESCE(ch.head_name, 'Unknown') AS crime_type, "
            "COALESCE(cc.category_name, 'Unknown') AS category, "
            "COUNT(*) AS cnt "
            "FROM case_master cm "
            "LEFT JOIN unit u ON u.unit_id = cm.police_station_id "
            "LEFT JOIN district d ON d.district_id = u.district_id "
            "LEFT JOIN crime_head ch ON ch.crime_head_id = cm.crime_major_head_id "
            "LEFT JOIN case_category cc ON cc.case_category_id = cm.case_category_id "
            "WHERE cm.crime_registered_date IS NOT NULL "
            "GROUP BY month, d.district_name, ch.head_name, cc.category_name "
            "ORDER BY month"
        )
    ).fetchall()

    results = []
    for r in rows:
        month, district, crime_type, category, cnt = r[0], r[1], r[2], r[3], r[4]
        for dim, val in [("district", district), ("crime_head", crime_type), ("category", category)]:
            results.append({
                "metric_type": "monthly_count",
                "dimension": dim,
                "dimension_value": val,
                "period_date": month,
                "value": float(cnt),
            })

    return results


def _yoy_comparison(session: Session) -> list[dict]:
    """Year-over-year comparison: same month this year vs last year."""
    rows = session.execute(
        text(
            "WITH monthly AS ("
            "  SELECT DATE_TRUNC('month', TO_DATE(cm.crime_registered_date, 'YYYY-MM-DD')) AS month, "
            "  COALESCE(d.district_name, 'Unknown') AS district, "
            "  COUNT(*) AS cnt "
            "  FROM case_master cm "
            "  LEFT JOIN unit u ON u.unit_id = cm.police_station_id "
            "  LEFT JOIN district d ON d.district_id = u.district_id "
            "  WHERE cm.crime_registered_date IS NOT NULL "
            "  GROUP BY month, d.district_name"
            ") "
            "SELECT curr.month, curr.district, curr.cnt AS this_year, "
            "       prev.cnt AS last_year "
            "FROM monthly curr "
            "LEFT JOIN monthly prev "
            "  ON prev.district = curr.district "
            "  AND prev.month = curr.month - INTERVAL '1 year' "
            "WHERE curr.month IS NOT NULL "
            "ORDER BY curr.month"
        )
    ).fetchall()

    results = []
    for r in rows:
        month, district, this_year, last_year = r[0], r[1], r[2], r[3]
        if last_year and last_year > 0:
            yoy_pct = ((this_year - last_year) / last_year) * 100
        else:
            yoy_pct = 0.0
        results.append({
            "metric_type": "yoy_comparison",
            "dimension": "district",
            "dimension_value": district,
            "period_date": month,
            "value": round(yoy_pct, 2),
        })

    return results


def _moving_averages(session: Session, window: int) -> list[dict]:
    """Compute N-month moving average of total monthly crime counts."""
    rows = session.execute(
        text(
            "SELECT DATE_TRUNC('month', TO_DATE(crime_registered_date, 'YYYY-MM-DD')) AS month, "
            "COUNT(*) AS cnt "
            "FROM case_master "
            "WHERE crime_registered_date IS NOT NULL "
            "GROUP BY month ORDER BY month"
        )
    ).fetchall()

    if len(rows) < window:
        return []

    counts = [float(r[1]) for r in rows]
    months = [r[0] for r in rows]
    metric = f"moving_avg_{window}m"
    results = []

    for i in range(window - 1, len(counts)):
        avg = sum(counts[i - window + 1 : i + 1]) / window
        results.append({
            "metric_type": metric,
            "dimension": "total",
            "dimension_value": "all_crimes",
            "period_date": months[i],
            "value": round(avg, 2),
        })

    return results


def _chargesheet_rates(session: Session) -> list[dict]:
    """Chargesheet completion rate by district per month."""
    rows = session.execute(
        text(
            "SELECT DATE_TRUNC('month', TO_DATE(cm.crime_registered_date, 'YYYY-MM-DD')) AS month, "
            "COALESCE(d.district_name, 'Unknown') AS district, "
            "COUNT(DISTINCT cm.case_id) AS total_cases, "
            "COUNT(DISTINCT CASE WHEN csm.status_name = 'Chargesheet Filed' "
            "  THEN cm.case_id END) AS chargesheet_count "
            "FROM case_master cm "
            "LEFT JOIN unit u ON u.unit_id = cm.police_station_id "
            "LEFT JOIN district d ON d.district_id = u.district_id "
            "LEFT JOIN case_status_master csm ON csm.case_status_id = cm.case_status_id "
            "WHERE cm.crime_registered_date IS NOT NULL "
            "GROUP BY month, d.district_name "
            "HAVING COUNT(DISTINCT cm.case_id) > 0 "
            "ORDER BY month"
        )
    ).fetchall()

    results = []
    for r in rows:
        month, district, total, chargesheet = r[0], r[1], r[2], r[3]
        rate = (chargesheet / total * 100) if total > 0 else 0.0
        results.append({
            "metric_type": "chargesheet_rate",
            "dimension": "district",
            "dimension_value": district,
            "period_date": month,
            "value": round(rate, 2),
        })

    return results


@register_job(
    "trend_analysis",
    schedule="cron",
    description="Compute monthly crime counts, YoY comparisons, moving averages, and chargesheet rates",
    day_of_week="sun",
    hour=3,
    minute=0,
)
class TrendAnalysisPipeline:
    name = "trend_analysis"
    description = "Compute monthly crime counts, YoY comparisons, moving averages, and chargesheet rates"

    def run(self, session: Session) -> dict[str, Any]:
        logger.info("Running crime trend analysis pipeline...")

        all_trends = []

        for name, fn in [
            ("monthly_counts", _monthly_counts),
            ("yoy_comparison", _yoy_comparison),
            ("moving_avg_3m", lambda s: _moving_averages(s, 3)),
            ("moving_avg_6m", lambda s: _moving_averages(s, 6)),
            ("chargesheet_rates", _chargesheet_rates),
        ]:
            try:
                trends = fn(session)
                all_trends.extend(trends)
                logger.info("  %s: generated %d records", name, len(trends))
            except Exception:
                logger.exception("  %s: failed", name)

        for t in all_trends:
            session.add(AnalyticsTrend(**t))

        session.commit()
        logger.info("Total trend records stored: %d", len(all_trends))

        return {
            "rows_processed": len(all_trends),
            "trends_computed": len(all_trends),
        }
