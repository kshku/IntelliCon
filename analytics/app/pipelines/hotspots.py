from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

import numpy as np
from sklearn.cluster import DBSCAN
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models import AnalyticsHotspot
from app.registry import register_job

logger = logging.getLogger(__name__)

HEINOUS_CRIME_KEYWORDS = [
    "murder",
    "homicide",
    "rape",
    "kidnap",
    "robbery",
    "dacoity",
    "extortion",
    "arson",
    "acid attack",
]

LOOKBACK_DAYS = 30
DBSCAN_EPS_KM = 1.0
DBSCAN_MIN_SAMPLES = 3


def _haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Great-circle distance between two points in km."""
    R = 6371.0
    dlat = np.radians(lat2 - lat1)
    dlng = np.radians(lng2 - lng1)
    a = (
        np.sin(dlat / 2) ** 2
        + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlng / 2) ** 2
    )
    return R * 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))


def _classify_severity(crime_type: str | None) -> str:
    if not crime_type:
        return "non-heinous"
    lower = crime_type.lower()
    for kw in HEINOUS_CRIME_KEYWORDS:
        if kw in lower:
            return "heinous"
    return "non-heinous"


def _fetch_cases(session: Session, lookback_days: int) -> list[dict]:
    cutoff = (datetime.now(timezone.utc) - timedelta(days=lookback_days)).strftime(
        "%Y-%m-%d"
    )
    rows = session.execute(
        text(
            "SELECT cm.case_id, cm.latitude, cm.longitude, "
            "cm.crime_major_head_id, ch.head_name AS crime_type, "
            "cm.crime_registered_date "
            "FROM case_master cm "
            "LEFT JOIN crime_head ch ON ch.crime_head_id = cm.crime_major_head_id "
            "WHERE cm.latitude IS NOT NULL AND cm.longitude IS NOT NULL "
            "AND cm.crime_registered_date >= :cutoff "
            "ORDER BY cm.case_id"
        ),
        {"cutoff": cutoff},
    ).fetchall()
    return [
        {
            "case_id": r[0],
            "latitude": float(r[1]),
            "longitude": float(r[2]),
            "crime_major_head_id": r[3],
            "crime_type": r[4],
            "crime_registered_date": r[5],
        }
        for r in rows
    ]


def _cluster_cases(cases: list[dict]) -> dict[int, list[dict]]:
    if not cases:
        return {}

    coords = np.array([[c["latitude"], c["longitude"]] for c in cases])

    eps_rad = DBSCAN_EPS_KM / 6371.0
    db = DBSCAN(
        eps=eps_rad,
        min_samples=DBSCAN_MIN_SAMPLES,
        metric="haversine",
        algorithm="ball_tree",
    )
    labels = db.fit_predict(coords)

    clusters: dict[int, list[dict]] = {}
    for label, case in zip(labels, cases):
        if label == -1:
            continue
        clusters.setdefault(int(label), []).append(case)

    return clusters


def _compute_radius_km(cluster_cases: list[dict]) -> float:
    if len(cluster_cases) < 2:
        return 0.0
    lats = [c["latitude"] for c in cluster_cases]
    lngs = [c["longitude"] for c in cluster_cases]
    center_lat = float(np.mean(lats))
    center_lng = float(np.mean(lngs))
    max_dist = max(
        _haversine_km(center_lat, center_lng, lat, lng) for lat, lng in zip(lats, lngs)
    )
    return round(max_dist, 3)


def _dominant_crime_type(cluster_cases: list[dict]) -> str:
    from collections import Counter

    types = [c["crime_type"] for c in cluster_cases if c["crime_type"]]
    if not types:
        return "unknown"
    return Counter(types).most_common(1)[0][0]


@register_job(
    "hotspot_detection",
    schedule="cron",
    description="Detect crime hotspots using DBSCAN clustering on location data",
    hour=2,
    minute=0,
)
class HotspotDetectionPipeline:
    name = "hotspot_detection"
    description = "Detect crime hotspots using DBSCAN clustering on location data"

    def run(self, session: Session) -> dict[str, Any]:
        logger.info(
            "Running hotspot detection pipeline (lookback=%d days)...", LOOKBACK_DAYS
        )

        cases = _fetch_cases(session, LOOKBACK_DAYS)
        logger.info("Fetched %d cases with location data", len(cases))

        if not cases:
            logger.info("No cases with coordinates found — skipping")
            return {"rows_processed": 0, "clusters_found": 0}

        clusters = _cluster_cases(cases)
        logger.info("DBSCAN found %d clusters", len(clusters))

        now = datetime.now(timezone.utc)
        period_start = now - timedelta(days=LOOKBACK_DAYS)
        stored = 0

        for cluster_id, cluster_cases in clusters.items():
            center_lat = float(np.mean([c["latitude"] for c in cluster_cases]))
            center_lng = float(np.mean([c["longitude"] for c in cluster_cases]))
            radius_km = _compute_radius_km(cluster_cases)
            crime_type = _dominant_crime_type(cluster_cases)
            severity = _classify_severity(crime_type)

            session.add(
                AnalyticsHotspot(
                    cluster_id=cluster_id,
                    center_lat=round(center_lat, 6),
                    center_lng=round(center_lng, 6),
                    crime_type=crime_type,
                    case_count=len(cluster_cases),
                    severity=severity,
                    period_start=period_start,
                    period_end=now,
                    radius_km=radius_km,
                    computed_at=now,
                )
            )
            stored += 1

        session.commit()
        logger.info("Stored %d hotspot records", stored)

        return {
            "rows_processed": len(cases),
            "clusters_found": len(clusters),
            "hotspots_stored": stored,
        }
