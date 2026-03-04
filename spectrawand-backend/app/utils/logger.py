"""
Structured logging powered by Loguru.

Replaces Python's default logging with structured, colorized output.
"""

import sys
from loguru import logger


def setup_logging(debug: bool = False) -> None:
    """Configure Loguru for the application."""
    logger.remove()

    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> — "
        "<level>{message}</level>"
    )

    logger.add(
        sys.stderr,
        format=log_format,
        level="DEBUG" if debug else "INFO",
        colorize=True,
        backtrace=True,
        diagnose=debug,
    )

    # File logging — rotated daily, kept 7 days
    logger.add(
        "logs/spectrawand_{time:YYYY-MM-DD}.log",
        format=log_format,
        level="DEBUG",
        rotation="00:00",
        retention="7 days",
        compression="gz",
        enqueue=True,  # Thread-safe
    )

    logger.info("Logging initialized (debug={})", debug)
