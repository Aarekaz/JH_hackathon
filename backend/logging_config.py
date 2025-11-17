"""
Logging configuration for AI Parliament application.
Uses loguru for better structured logging.
"""
import sys
from pathlib import Path
from loguru import logger
from config import settings


def setup_logging():
    """Configure logging for the application."""

    # Remove default logger
    logger.remove()

    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Console logging (stdout)
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.log_level,
        colorize=True,
    )

    # File logging (with rotation)
    logger.add(
        settings.log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=settings.log_level,
        rotation="500 MB",  # Rotate when file reaches 500 MB
        retention="10 days",  # Keep logs for 10 days
        compression="zip",  # Compress rotated logs
        enqueue=True,  # Thread-safe
    )

    # Error logging (separate file for errors)
    logger.add(
        "logs/errors.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR",
        rotation="100 MB",
        retention="30 days",
        compression="zip",
        enqueue=True,
    )

    logger.info("Logging configured successfully")

    return logger


# Initialize logging
app_logger = setup_logging()
