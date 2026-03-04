"""
SpectraWand API — FastAPI Application Entry Point.

Manages application lifespan (model loading/unloading),
CORS middleware, exception handlers, and routing.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.config import settings
from app.api.router import router
from app.core.pipeline import pipeline
from app.utils.logger import setup_logging
from app.utils.exceptions import register_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan — load models on startup, cleanup on shutdown.

    Using the modern lifespan context manager instead of deprecated
    on_event("startup") / on_event("shutdown").
    """
    # ── Startup ─────────────────────────────────────────────────────────
    setup_logging(debug=settings.DEBUG)
    logger.info("Starting {} v{}", settings.APP_NAME, settings.APP_VERSION)
    settings.ensure_dirs()

    try:
        await pipeline.initialize()
        logger.info("✓ {} is ready to serve requests", settings.APP_NAME)
    except Exception as e:
        logger.error("Failed to initialize pipeline: {}", e)
        logger.warning("Server starting WITHOUT AI models — health check will show 'loading'")

    yield

    # ── Shutdown ────────────────────────────────────────────────────────
    logger.info("Shutting down {}...", settings.APP_NAME)
    await pipeline.shutdown()
    logger.info("✓ Shutdown complete")


# ── Create FastAPI app ──────────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "AI-powered professional color grading API. "
        "Uses Stable Diffusion XL with ControlNet for structure-preserving "
        "color grading and Real-ESRGAN for 4K enhancement."
    ),
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Exception Handlers ─────────────────────────────────────────────────
register_exception_handlers(app)

# ── Routes ──────────────────────────────────────────────────────────────
app.include_router(router)


# ── Root redirect ───────────────────────────────────────────────────────
@app.get("/", include_in_schema=False)
async def root():
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/api/v1/health",
    }


# ── Uvicorn runner ──────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info",
        workers=1,  # Single worker for GPU (models are not fork-safe)
    )
