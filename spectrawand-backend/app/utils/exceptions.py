"""
Custom exception classes and FastAPI exception handlers.
"""

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from loguru import logger


# ── Custom Exceptions ───────────────────────────────────────────────────

class SpectrawandError(Exception):
    """Base exception for SpectraWand."""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ModelLoadError(SpectrawandError):
    """Raised when AI models fail to load."""
    def __init__(self, message: str = "Failed to load AI models"):
        super().__init__(message, status_code=503)


class ImageProcessingError(SpectrawandError):
    """Raised when image processing fails."""
    def __init__(self, message: str = "Image processing failed"):
        super().__init__(message, status_code=422)


class ImageValidationError(SpectrawandError):
    """Raised when uploaded image fails validation."""
    def __init__(self, message: str = "Invalid image"):
        super().__init__(message, status_code=400)


class GPUError(SpectrawandError):
    """Raised when GPU is unavailable or out of memory."""
    def __init__(self, message: str = "GPU error"):
        super().__init__(message, status_code=503)


# ── Exception Handlers (register on FastAPI app) ────────────────────────

async def spectrawand_error_handler(request: Request, exc: SpectrawandError):
    logger.error("SpectrawandError: {} (status={})", exc.message, exc.status_code)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message, "type": type(exc).__name__},
    )


async def generic_error_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception: {}", str(exc))
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "type": "UnhandledException"},
    )


def register_exception_handlers(app):
    """Register all custom exception handlers on the FastAPI app."""
    app.add_exception_handler(SpectrawandError, spectrawand_error_handler)
    app.add_exception_handler(Exception, generic_error_handler)
