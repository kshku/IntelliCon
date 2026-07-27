import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.admin import router as admin_router
from app.api.audit import router as audit_router
from app.api.auth import router as auth_router
from app.api.cases import router as cases_router
from app.api.chat import router as chat_router
from app.api.graph import router as graph_router
from app.api.pdf import router as pdf_router
from app.api.translation import router as translation_router
from app.config import settings
from app.config_validator import validate_production_config
from app.db.migrations import get_current_revision, run_migrations, wait_for_db

logger = logging.getLogger(__name__)

_migrations_completed = False


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Handle application startup and shutdown events."""
    global _migrations_completed
    from app.db.neo4j import close_driver
    from app.db.session import engine

    if settings.JWT_SECRET_KEY == "change-me-in-production":
        if settings.ENVIRONMENT == "production":
            logger.critical(
                "JWT_SECRET_KEY is set to the default placeholder. "
                "Set a strong random value via the JWT_SECRET_KEY env var."
            )
            raise RuntimeError("JWT_SECRET_KEY must be changed from default")
        else:
            logger.warning(
                "JWT_SECRET_KEY is set to the default placeholder. "
                "For production, set a strong random value via the JWT_SECRET_KEY env var."
            )

    # Validate production configuration
    config_errors = validate_production_config(settings)
    if config_errors:
        error_msg = "Production configuration invalid:\n" + "\n".join(
            f"  - {e}" for e in config_errors
        )
        logger.critical(error_msg)
        raise RuntimeError(error_msg)

    logger.info("Starting IntelliCon backend...")

    # Wait for database to be available
    wait_for_db()

    # Run migrations
    run_migrations()
    _migrations_completed = True
    logger.info("Backend startup complete")

    yield

    logger.info("Shutting down IntelliCon backend...")
    await engine.dispose()
    close_driver()


app = FastAPI(
    title="IntelliCon API",
    description="Conversational AI platform for Karnataka State Police Crime Database",
    version="0.1.0",
    lifespan=lifespan,
)


# Catalyst AppSail gateway intercepts CORS preflight (OPTIONS) and strips
# Access-Control-Allow-* headers. PUT and DELETE always trigger preflight.
# This middleware lets the frontend send POST + X-HTTP-Method-Override instead,
# avoiding the preflight entirely. Remove once a proper CORS solution is in place.
class MethodOverrideMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method == "POST":
            override = request.headers.get("x-http-method-override", "").upper()
            if override in ("PUT", "DELETE", "PATCH"):
                request.scope["method"] = override
        return await call_next(request)


app.add_middleware(MethodOverrideMiddleware)

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
app.include_router(admin_router)
app.include_router(chat_router, prefix="/api/chat")
app.include_router(cases_router)


@app.get("/health")
async def health_check() -> dict[str, str | dict[str, str | None]]:
    """Health check endpoint that verifies database migrations are complete."""
    from sqlalchemy import text

    from app.db.session import engine

    if not _migrations_completed:
        return {
            "status": "starting",
            "service": "intellicon-backend",
            "message": "Migrations in progress",
        }

    health: dict[str, str | dict[str, str | None]] = {
        "status": "healthy",
        "service": "intellicon-backend",
        "database_revision": get_current_revision() or "unknown",
        "checks": {},
    }

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        health["checks"]["database"] = "ok"  # type: ignore[index]
    except Exception:
        health["checks"]["database"] = "error"  # type: ignore[index]
        health["status"] = "degraded"

    return health
