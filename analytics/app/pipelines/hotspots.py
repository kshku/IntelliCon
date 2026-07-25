from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.orm import Session

from app.registry import register_job

logger = logging.getLogger(__name__)


@register_job(
    "hotspot_detection",
    schedule="cron",
    description="Detect crime hotspots using DBSCAN clustering",
    hour=2,
    minute=0,
)
class HotspotDetectionPipeline:
    name = "hotspot_detection"
    description = "Detect crime hotspots using DBSCAN clustering"

    def run(self, session: Session) -> dict[str, Any]:
        logger.info("Running hotspot detection pipeline...")
        # TODO: Implement DBSCAN clustering on case lat/lng data
        # For now, return stub results
        return {"rows_processed": 0, "clusters_found": 0}
