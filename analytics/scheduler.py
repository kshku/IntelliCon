from __future__ import annotations

import logging

from apscheduler.schedulers.blocking import BlockingScheduler

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

scheduler = BlockingScheduler()


@scheduler.scheduled_job("cron", hour=2, minute=0)
def run_hotspot_detection() -> None:
    logger.info("Running hotspot detection pipeline...")


@scheduler.scheduled_job("cron", day_of_week="sun", hour=3, minute=0)
def run_trend_analysis() -> None:
    logger.info("Running crime trend analysis pipeline...")


@scheduler.scheduled_job("cron", day_of_week="sun", hour=4, minute=0)
def run_predictive_analytics() -> None:
    logger.info("Running predictive analytics pipeline...")


if __name__ == "__main__":
    logger.info("Starting analytics scheduler...")
    scheduler.start()
