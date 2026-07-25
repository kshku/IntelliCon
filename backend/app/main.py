from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.audit import router as audit_router
from app.api.auth import router as auth_router
from app.api.graph import router as graph_router
from app.api.translation import router as translation_router
from app.config import settings

app = FastAPI(
    title="IntelliCon API",
    description="Conversational AI platform for Karnataka State Police Crime Database",
    version="0.1.0",
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
app.include_router(translation_router, prefix="/api")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "intellicon-backend"}
