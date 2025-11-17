import os
import time
from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from db.init_db import init_database
from routers import debates, moderator, policy_papers, monitoring
from config import settings
from monitoring.metrics import get_metrics_collector

# Load environment variables from .env file
load_dotenv()

# Set up improved logging
try:
    from logging_config import app_logger as logger
    logger.info("Using improved loguru logging")
except Exception as e:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.warning(f"Failed to load loguru logging, using standard logging: {e}")

# Initialize the app with better documentation
app = FastAPI(
    title="AI Parliament Simulator API",
    description="Simulate parliamentary debates on AI policy papers using AI-powered MPs",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Initialize database
init_database()

# Request logging and metrics middleware
@app.middleware("http")
async def log_requests_and_track_metrics(request: Request, call_next):
    """Log all requests and track metrics."""
    start_time = time.time()

    # Log request
    logger.info(f"→ {request.method} {request.url.path}")

    # Process request
    try:
        response = await call_next(request)
        duration = time.time() - start_time

        # Log response
        logger.info(
            f"← {request.method} {request.url.path} "
            f"completed in {duration:.2f}s with status {response.status_code}"
        )

        # Track metrics
        metrics = get_metrics_collector()
        if request.url.path not in metrics.metrics["api_request_times"]:
            metrics.metrics["api_request_times"][request.url.path] = []

        metrics.metrics["api_request_times"][request.url.path].append({
            "duration": duration,
            "status": response.status_code,
            "timestamp": datetime.utcnow()
        })

        return response

    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"✗ {request.method} {request.url.path} failed after {duration:.2f}s: {str(e)}")

        # Track error
        metrics = get_metrics_collector()
        metrics.record_error(
            error_type=type(e).__name__,
            error_message=str(e),
            context={"path": request.url.path, "method": request.method}
        )

        raise

# CORS Configuration (using settings from config)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins if not settings.debug else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(debates.router)
app.include_router(moderator.router)
app.include_router(policy_papers.router)
app.include_router(monitoring.router)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "version": "2.0.0"
    }


@app.get("/metrics")
async def get_metrics(time_window_hours: int = None):
    """
    Get application metrics.

    Args:
        time_window_hours: Optional time window in hours (e.g., 1 for last hour)

    Returns:
        Metrics summary including performance stats and error counts
    """
    from datetime import timedelta

    metrics = get_metrics_collector()

    time_window = timedelta(hours=time_window_hours) if time_window_hours else None
    summary = metrics.get_summary(time_window=time_window)

    return {
        "summary": summary,
        "recent_errors": metrics.get_recent_errors(limit=5),
        "time_window": f"{time_window_hours} hours" if time_window_hours else "all time"
    }


# Startup event
@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info("=" * 80)
    logger.info("AI Parliament Simulator API v2.0.0 Starting Up")
    logger.info(f"Debug Mode: {settings.debug}")
    logger.info(f"Database: {settings.database_url}")
    logger.info(f"OpenAI Model: {settings.openai_model}")
    logger.info("=" * 80)


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info("AI Parliament Simulator API shutting down...")
    metrics = get_metrics_collector()
    summary = metrics.get_summary()
    logger.info(f"Final stats: {summary['total_debates']} debates, "
                f"{summary['total_responses']} responses, "
                f"{summary['total_votes']} votes")
    logger.info("Goodbye!")
