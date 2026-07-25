import logging
import traceback
from datetime import datetime

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI

from app.config import settings
from app.db import SessionLocal, init_schema
from app.models import JobExecutionLog
from app.registry import get_registry

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="IntelliCon Analytics Scheduler",
    description="Cron job infrastructure for batch analytics pipelines",
    version="0.1.0",
)

jobstores = {
    "default": SQLAlchemyJobStore(url=settings.DATABASE_URL)
}
scheduler = BackgroundScheduler(jobstores=jobstores)


def run_job(job_name: str) -> None:
    """Execute a registered job and log the result."""
    registry = get_registry()
    if job_name not in registry:
        logger.error(f"Job '{job_name}' not found in registry")
        return

    job_def = registry[job_name]
    session = SessionLocal()

    execution = JobExecutionLog(
        job_name=job_name,
        status="running",
        started_at=datetime.utcnow(),
    )
    session.add(execution)
    session.commit()
    session.refresh(execution)
    execution_id = execution.id

    logger.info(f"Starting job '{job_name}' (execution_id={execution_id})")

    try:
        pipeline = job_def.pipeline_class()
        result = pipeline.run(session)

        execution.status = "completed"
        execution.completed_at = datetime.utcnow()
        execution.rows_processed = result.get("rows_processed", 0)
        execution.metadata_ = result

        session.commit()
        logger.info(
            f"Job '{job_name}' completed (execution_id={execution_id}, "
            f"rows={execution.rows_processed})"
        )
    except Exception as e:
        execution.status = "failed"
        execution.completed_at = datetime.utcnow()
        execution.error_message = traceback.format_exc()
        session.commit()
        logger.error(f"Job '{job_name}' failed (execution_id={execution_id}): {e}")

        if settings.ANALYTICS_WEBHOOK_URL:
            _send_error_webhook(job_name, execution_id, str(e))
    finally:
        session.close()


def _send_error_webhook(job_name: str, execution_id: int, error: str) -> None:
    """Send error notification to webhook URL."""
    import json
    import urllib.request

    try:
        payload = json.dumps(
            {
                "job_name": job_name,
                "execution_id": execution_id,
                "error": error,
            }
        ).encode()
        req = urllib.request.Request(
            settings.ANALYTICS_WEBHOOK_URL,
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        urllib.request.urlopen(req, timeout=10)
        logger.info(f"Error webhook sent for job '{job_name}'")
    except Exception as webhook_err:
        logger.error(f"Failed to send error webhook: {webhook_err}")


@app.on_event("startup")
def startup() -> None:
    logger.info("Initializing analytics schema...")
    init_schema()

    registry = get_registry()
    for name, job_def in registry.items():
        trigger_kwargs = {"trigger": job_def.schedule, **job_def.schedule_kwargs}
        scheduler.add_job(
            run_job,
            id=name,
            name=name,
            kwargs={"job_name": name},
            replace_existing=True,
            **trigger_kwargs,
        )
        logger.info(
            f"Registered job '{name}' with schedule: {job_def.schedule} {job_def.schedule_kwargs}"
        )

    scheduler.start()
    logger.info(f"Scheduler started with {len(registry)} jobs")


@app.on_event("shutdown")
def shutdown() -> None:
    scheduler.shutdown(wait=False)
    logger.info("Scheduler shut down")


@app.get("/health")
def health_check() -> dict:
    return {"status": "healthy", "service": "intellicon-analytics"}
