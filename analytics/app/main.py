import logging
import traceback
from datetime import datetime

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

import app.pipelines  # noqa: F401  — triggers @register_job decorators
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


class JobResponse(BaseModel):
    name: str
    description: str
    schedule: str
    schedule_kwargs: dict


class ExecutionResponse(BaseModel):
    id: int
    job_name: str
    status: str
    started_at: datetime
    completed_at: datetime | None
    rows_processed: int
    error_message: str | None
    metadata: dict | None


class TriggerResponse(BaseModel):
    execution_id: int
    status: str


@app.get("/jobs", response_model=list[JobResponse])
def list_jobs() -> list[JobResponse]:
    registry = get_registry()
    return [
        JobResponse(
            name=job_def.name,
            description=job_def.description,
            schedule=job_def.schedule,
            schedule_kwargs=job_def.schedule_kwargs,
        )
        for job_def in registry.values()
    ]


@app.get("/jobs/{job_name}", response_model=JobResponse)
def get_job(job_name: str) -> JobResponse:
    registry = get_registry()
    if job_name not in registry:
        raise HTTPException(status_code=404, detail=f"Job '{job_name}' not found")
    job_def = registry[job_name]
    return JobResponse(
        name=job_def.name,
        description=job_def.description,
        schedule=job_def.schedule,
        schedule_kwargs=job_def.schedule_kwargs,
    )


@app.post("/jobs/{job_name}/trigger", response_model=TriggerResponse)
def trigger_job(job_name: str) -> TriggerResponse:
    registry = get_registry()
    if job_name not in registry:
        raise HTTPException(status_code=404, detail=f"Job '{job_name}' not found")

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
    session.close()

    scheduler.add_job(
        run_job,
        id=f"{job_name}_manual_{execution_id}",
        name=f"{job_name}_manual",
        kwargs={"job_name": job_name},
        trigger="date",
        run_date=datetime.utcnow(),
        replace_existing=False,
    )

    return TriggerResponse(execution_id=execution_id, status="running")


@app.get("/jobs/{job_name}/status", response_model=ExecutionResponse)
def get_job_status(job_name: str) -> ExecutionResponse:
    session = SessionLocal()
    execution = (
        session.query(JobExecutionLog)
        .filter(JobExecutionLog.job_name == job_name)
        .order_by(JobExecutionLog.started_at.desc())
        .first()
    )
    session.close()

    if not execution:
        raise HTTPException(
            status_code=404, detail=f"No executions found for job '{job_name}'"
        )

    return ExecutionResponse(
        id=execution.id,
        job_name=execution.job_name,
        status=execution.status,
        started_at=execution.started_at,
        completed_at=execution.completed_at,
        rows_processed=execution.rows_processed,
        error_message=execution.error_message,
        metadata=execution.metadata_,
    )


@app.get("/executions", response_model=list[ExecutionResponse])
def list_executions(
    job_name: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
) -> list[ExecutionResponse]:
    session = SessionLocal()
    query = session.query(JobExecutionLog)
    if job_name:
        query = query.filter(JobExecutionLog.job_name == job_name)
    executions = query.order_by(JobExecutionLog.started_at.desc()).limit(limit).all()
    session.close()

    return [
        ExecutionResponse(
            id=ex.id,
            job_name=ex.job_name,
            status=ex.status,
            started_at=ex.started_at,
            completed_at=ex.completed_at,
            rows_processed=ex.rows_processed,
            error_message=ex.error_message,
            metadata=ex.metadata_,
        )
        for ex in executions
    ]


@app.get("/executions/{execution_id}", response_model=ExecutionResponse)
def get_execution(execution_id: int) -> ExecutionResponse:
    session = SessionLocal()
    execution = (
        session.query(JobExecutionLog)
        .filter(JobExecutionLog.id == execution_id)
        .first()
    )
    session.close()

    if not execution:
        raise HTTPException(
            status_code=404, detail=f"Execution {execution_id} not found"
        )

    return ExecutionResponse(
        id=execution.id,
        job_name=execution.job_name,
        status=execution.status,
        started_at=execution.started_at,
        completed_at=execution.completed_at,
        rows_processed=execution.rows_processed,
        error_message=execution.error_message,
        metadata=execution.metadata_,
    )
