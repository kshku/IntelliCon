import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.admin import router as admin_router
from app.api.audit import router as audit_router
from app.api.auth import router as auth_router
from app.api.cases import router as cases_router
from app.api.chat import router as chat_router
from app.api.graph import router as graph_router
from app.api.pdf import router as pdf_router
from app.api.translation import router as translation_router
from app.config import settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    from app.db.neo4j import close_driver
    from app.db.session import engine

    if settings.JWT_SECRET_KEY == "change-me-in-production":
        logger.critical(
            "JWT_SECRET_KEY is set to the default placeholder. "
            "Set a strong random value via the JWT_SECRET_KEY env var."
        )
        raise RuntimeError("JWT_SECRET_KEY must be changed from default")

    logger.info("Starting IntelliCon backend...")
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
async def health_check():
    from sqlalchemy import text

    from app.db.session import engine

    health = {"status": "healthy", "service": "intellicon-backend", "checks": {}}

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        health["checks"]["database"] = "ok"
    except Exception:
        health["checks"]["database"] = "error"
        health["status"] = "degraded"

    return health
