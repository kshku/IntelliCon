import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.audit import router as audit_router
from app.api.auth import router as auth_router
from app.api.graph import router as graph_router
from app.api.pdf import router as pdf_router
from app.api.translation import router as translation_router
from app.config import settings
from app.db.migrations import get_current_revision, run_migrations, wait_for_db

logger = logging.getLogger(__name__)

_migrations_completed = False


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Handle application startup and shutdown events."""
    global _migrations_completed
    logger.info("Starting IntelliCon backend...")

    # Wait for database to be available
    wait_for_db()

    # Run migrations
    run_migrations()
    _migrations_completed = True
    logger.info("Backend startup complete")

    yield

    logger.info("Shutting down IntelliCon backend...")


app = FastAPI(
    title="IntelliCon API",
    description="Conversational AI platform for Karnataka State Police Crime Database",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(audit_router)
app.include_router(auth_router)
app.include_router(graph_router)
app.include_router(pdf_router)
app.include_router(translation_router, prefix="/api")


@app.get("/health")
async def health_check() -> dict[str, str | dict[str, str | None]]:
    """Health check endpoint that verifies database migrations are complete."""
    if not _migrations_completed:
        return {
            "status": "starting",
            "service": "intellicon-backend",
            "message": "Migrations in progress",
        }

    revision = get_current_revision()
    return {
        "status": "healthy",
        "service": "intellicon-backend",
        "database_revision": revision or "unknown",
    }
