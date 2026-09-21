"""
backend/main.py — GAIA API entry point.
Mounts all route modules. Initializes DB on startup.
API keys loaded from .env via db.py and settings routes.
"""
import os
import structlog
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()
log = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize DB tables and Graphiti indices on startup."""
    log.info("gaia.starting")
    try:
        from backend.db import init_db
        await init_db()
        log.info("gaia.db_initialized")
    except Exception as e:
        log.warning("gaia.db_init_failed", error=str(e), hint="Check DATABASE_URL and NEO4J_* in .env")
    yield
    log.info("gaia.shutdown")


app = FastAPI(
    title="GAIA Command Center API",
    description="Growth AI Agent — Backend",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS for Vite dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Mount all route modules ───────────────────────────────────────────────────
from backend.routes.chat import router as chat_router
from backend.routes.settings import router as settings_router
from backend.routes.memory import router as memory_router
from backend.routes.approvals import router as approvals_router
from backend.routes.workflows import router as workflows_router
from backend.routes.content import router as content_router
from backend.routes.tasks import router as tasks_router
from backend.routes.intelligence import router as intelligence_router
from backend.routes.costs import router as costs_router

app.include_router(chat_router)
app.include_router(settings_router)
app.include_router(memory_router)
app.include_router(approvals_router)
app.include_router(workflows_router)
app.include_router(content_router)
app.include_router(tasks_router)
app.include_router(intelligence_router)
app.include_router(costs_router)


@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "agent": "GAIA",
        "version": "2.0.0",
        "llm": os.getenv("GEMINI_MODEL", "gemini-2.5-pro"),
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("GAIA_API_PORT", 8001))
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=True)
