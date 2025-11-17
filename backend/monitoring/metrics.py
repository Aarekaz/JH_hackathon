"""
Monitoring and metrics collection for AI Parliament.
Tracks API performance, debate generation times, and system health.
"""
from typing import Dict, Optional
from datetime import datetime, timedelta
import time
from functools import wraps
import logging

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Collect and track application metrics."""

    def __init__(self):
        """Initialize metrics collector."""
        self.metrics: Dict[str, list] = {
            "debate_generation_times": [],
            "response_generation_times": [],
            "vote_generation_times": [],
            "api_request_times": {},
            "errors": [],
            "debates_created": 0,
            "responses_generated": 0,
            "votes_cast": 0,
        }
        self.start_time = datetime.utcnow()

    def record_duration(self, metric_name: str, duration: float):
        """Record a duration metric."""
        if metric_name not in self.metrics:
            self.metrics[metric_name] = []

        self.metrics[metric_name].append({
            "duration": duration,
            "timestamp": datetime.utcnow()
        })

        # Keep only last 1000 entries
        if len(self.metrics[metric_name]) > 1000:
            self.metrics[metric_name] = self.metrics[metric_name][-1000:]

    def record_counter(self, metric_name: str, increment: int = 1):
        """Increment a counter metric."""
        if metric_name not in self.metrics:
            self.metrics[metric_name] = 0

        self.metrics[metric_name] += increment

    def record_error(self, error_type: str, error_message: str, context: Optional[Dict] = None):
        """Record an error occurrence."""
        self.metrics["errors"].append({
            "type": error_type,
            "message": error_message,
            "context": context or {},
            "timestamp": datetime.utcnow()
        })

        # Keep only last 500 errors
        if len(self.metrics["errors"]) > 500:
            self.metrics["errors"] = self.metrics["errors"][-500:]

    def get_summary(self, time_window: Optional[timedelta] = None) -> Dict:
        """
        Get metrics summary.

        Args:
            time_window: Optional time window to filter metrics (e.g., last hour)

        Returns:
            Dict containing metrics summary
        """
        cutoff_time = datetime.utcnow() - time_window if time_window else None

        def filter_by_time(items):
            if not cutoff_time:
                return items
            return [item for item in items if item.get("timestamp", datetime.utcnow()) >= cutoff_time]

        # Calculate average durations
        debate_times = filter_by_time(self.metrics.get("debate_generation_times", []))
        response_times = filter_by_time(self.metrics.get("response_generation_times", []))
        vote_times = filter_by_time(self.metrics.get("vote_generation_times", []))

        summary = {
            "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds(),
            "debate_generation": {
                "count": len(debate_times),
                "avg_duration": sum(d["duration"] for d in debate_times) / len(debate_times) if debate_times else 0,
                "max_duration": max((d["duration"] for d in debate_times), default=0),
                "min_duration": min((d["duration"] for d in debate_times), default=0),
            },
            "response_generation": {
                "count": len(response_times),
                "avg_duration": sum(d["duration"] for d in response_times) / len(response_times) if response_times else 0,
            },
            "vote_generation": {
                "count": len(vote_times),
                "avg_duration": sum(d["duration"] for d in vote_times) / len(vote_times) if vote_times else 0,
            },
            "total_debates": self.metrics.get("debates_created", 0),
            "total_responses": self.metrics.get("responses_generated", 0),
            "total_votes": self.metrics.get("votes_cast", 0),
            "errors": len(filter_by_time(self.metrics.get("errors", []))),
        }

        return summary

    def get_recent_errors(self, limit: int = 10) -> list:
        """Get most recent errors."""
        errors = sorted(
            self.metrics.get("errors", []),
            key=lambda x: x["timestamp"],
            reverse=True
        )
        return errors[:limit]


# Singleton instance
_metrics_collector = None


def get_metrics_collector() -> MetricsCollector:
    """Get or create singleton metrics collector."""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


def track_duration(metric_name: str):
    """
    Decorator to track function execution duration.

    Usage:
        @track_duration("debate_generation_times")
        async def create_debate(...):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                collector = get_metrics_collector()
                collector.record_duration(metric_name, duration)
                logger.debug(f"{metric_name}: {duration:.2f}s")

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                collector = get_metrics_collector()
                collector.record_duration(metric_name, duration)
                logger.debug(f"{metric_name}: {duration:.2f}s")

        # Return appropriate wrapper based on whether function is async
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
