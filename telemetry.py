"""
Telemetry and Monitoring Module for SAP Datasphere MCP Server

Tracks performance metrics, tool usage, errors, and system health.
Provides insights for optimization and troubleshooting.
"""

import time
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics tracked"""
    TOOL_CALL = "tool_call"
    ERROR = "error"
    VALIDATION_FAILURE = "validation_failure"
    AUTHORIZATION_CHECK = "authorization_check"
    CACHE_HIT = "cache_hit"
    CACHE_MISS = "cache_miss"
    CACHE_EVENT = "cache_event"


@dataclass
class ToolMetric:
    """Metrics for a single tool invocation"""
    tool_name: str
    start_time: float
    end_time: float
    duration_ms: float
    success: bool
    error_message: Optional[str] = None
    cached: bool = False
    validation_passed: bool = True
    authorization_passed: bool = True


@dataclass
class TelemetryStats:
    """Aggregated telemetry statistics"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_duration_ms: float = 0.0
    avg_duration_ms: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0
    validation_failures: int = 0
    authorization_denials: int = 0
    tool_usage: Dict[str, int] = field(default_factory=dict)
    error_counts: Dict[str, int] = field(default_factory=dict)


class TelemetryManager:
    """
    Telemetry and monitoring manager

    Features:
    - Request tracking and timing
    - Tool usage statistics
    - Error tracking
    - Performance metrics
    - Cache effectiveness
    - Sliding window for recent metrics
    """

    def __init__(self, max_history: int = 1000):
        """
        Initialize telemetry manager

        Args:
            max_history: Maximum number of recent metrics to keep
        """
        self.max_history = max_history
        self._metrics: deque[ToolMetric] = deque(maxlen=max_history)
        self._tool_usage = defaultdict(int)
        self._tool_errors = defaultdict(int)
        self._error_messages = defaultdict(int)
        self._start_time = time.time()
        self._cache_hits = 0
        self._cache_misses = 0
        self._validation_failures = 0
        self._authorization_denials = 0
        self._cache_events = defaultdict(lambda: defaultdict(int))  # {category: {event_type: count}}

        logger.info(f"Telemetry manager initialized (max_history={max_history})")

    def record_tool_call(
        self,
        tool_name: str,
        duration_ms: float,
        success: bool,
        error_message: Optional[str] = None,
        cached: bool = False,
        validation_passed: bool = True,
        authorization_passed: bool = True
    ):
        """
        Record a tool invocation

        Args:
            tool_name: Name of the tool
            duration_ms: Execution duration in milliseconds
            success: Whether the call succeeded
            error_message: Error message if failed
            cached: Whether result was from cache
            validation_passed: Whether validation passed
            authorization_passed: Whether authorization passed
        """
        now = time.time()
        metric = ToolMetric(
            tool_name=tool_name,
            start_time=now - (duration_ms / 1000.0),
            end_time=now,
            duration_ms=duration_ms,
            success=success,
            error_message=error_message,
            cached=cached,
            validation_passed=validation_passed,
            authorization_passed=authorization_passed
        )

        self._metrics.append(metric)
        self._tool_usage[tool_name] += 1

        if not success:
            self._tool_errors[tool_name] += 1
            if error_message:
                self._error_messages[error_message] += 1

        if cached:
            self._cache_hits += 1
        else:
            self._cache_misses += 1

        if not validation_passed:
            self._validation_failures += 1

        if not authorization_passed:
            self._authorization_denials += 1

        logger.debug(
            f"Metric recorded: {tool_name} "
            f"({duration_ms:.2f}ms, success={success}, cached={cached})"
        )

    def record_cache_event(self, event_type: str, category: str, details: str = ""):
        """
        Record a cache event (hit/miss)

        Args:
            event_type: Type of event ("hit" or "miss")
            category: Cache category (e.g., "catalog_assets", "spaces")
            details: Optional details about the event
        """
        self._cache_events[category][event_type] += 1

        if event_type == "hit":
            self._cache_hits += 1
        elif event_type == "miss":
            self._cache_misses += 1

        logger.debug(f"Cache {event_type}: {category} ({details})")

    def get_stats(self, window_minutes: Optional[int] = None) -> TelemetryStats:
        """
        Get aggregated statistics

        Args:
            window_minutes: Optional time window for recent stats

        Returns:
            Aggregated telemetry statistics
        """
        metrics = self._get_metrics_in_window(window_minutes) if window_minutes else list(self._metrics)

        if not metrics:
            return TelemetryStats()

        total_requests = len(metrics)
        successful = sum(1 for m in metrics if m.success)
        failed = total_requests - successful
        total_duration = sum(m.duration_ms for m in metrics)
        avg_duration = total_duration / total_requests if total_requests > 0 else 0.0

        cache_hits = sum(1 for m in metrics if m.cached)
        cache_misses = total_requests - cache_hits

        validation_failures = sum(1 for m in metrics if not m.validation_passed)
        auth_denials = sum(1 for m in metrics if not m.authorization_passed)

        tool_usage = defaultdict(int)
        for m in metrics:
            tool_usage[m.tool_name] += 1

        error_counts = defaultdict(int)
        for m in metrics:
            if m.error_message:
                error_counts[m.error_message] += 1

        return TelemetryStats(
            total_requests=total_requests,
            successful_requests=successful,
            failed_requests=failed,
            total_duration_ms=total_duration,
            avg_duration_ms=avg_duration,
            cache_hits=cache_hits,
            cache_misses=cache_misses,
            validation_failures=validation_failures,
            authorization_denials=auth_denials,
            tool_usage=dict(tool_usage),
            error_counts=dict(error_counts)
        )

    def get_tool_performance(self, tool_name: str) -> Dict[str, Any]:
        """Get performance metrics for a specific tool"""
        tool_metrics = [m for m in self._metrics if m.tool_name == tool_name]

        if not tool_metrics:
            return {
                "tool_name": tool_name,
                "total_calls": 0,
                "message": "No metrics available"
            }

        total_calls = len(tool_metrics)
        successful = sum(1 for m in tool_metrics if m.success)
        failed = total_calls - successful
        durations = [m.duration_ms for m in tool_metrics]

        return {
            "tool_name": tool_name,
            "total_calls": total_calls,
            "successful": successful,
            "failed": failed,
            "success_rate_percent": round((successful / total_calls * 100), 2),
            "avg_duration_ms": round(sum(durations) / len(durations), 2),
            "min_duration_ms": round(min(durations), 2),
            "max_duration_ms": round(max(durations), 2),
            "cache_hit_rate": round(sum(1 for m in tool_metrics if m.cached) / total_calls * 100, 2)
        }

    def get_error_summary(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get summary of most common errors"""
        error_list = []

        for error_msg, count in sorted(
            self._error_messages.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]:
            error_list.append({
                "error_message": error_msg,
                "count": count,
                "percentage": round(count / len(self._metrics) * 100, 2) if self._metrics else 0
            })

        return error_list

    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health metrics"""
        uptime_seconds = time.time() - self._start_time
        stats = self.get_stats()

        success_rate = (
            (stats.successful_requests / stats.total_requests * 100)
            if stats.total_requests > 0
            else 100.0
        )

        cache_hit_rate = (
            (stats.cache_hits / (stats.cache_hits + stats.cache_misses) * 100)
            if (stats.cache_hits + stats.cache_misses) > 0
            else 0.0
        )

        return {
            "status": "healthy" if success_rate > 90 else "degraded" if success_rate > 75 else "unhealthy",
            "uptime_seconds": round(uptime_seconds, 2),
            "uptime_hours": round(uptime_seconds / 3600, 2),
            "total_requests": stats.total_requests,
            "success_rate_percent": round(success_rate, 2),
            "avg_response_time_ms": round(stats.avg_duration_ms, 2),
            "cache_hit_rate_percent": round(cache_hit_rate, 2),
            "validation_failure_rate": round(
                (stats.validation_failures / stats.total_requests * 100)
                if stats.total_requests > 0
                else 0.0,
                2
            ),
            "most_used_tools": self._get_top_tools(5),
            "recent_errors": len([m for m in list(self._metrics)[-100:] if not m.success])
        }

    def get_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data"""
        stats = self.get_stats()
        recent_stats = self.get_stats(window_minutes=5)

        return {
            "overview": {
                "total_requests": stats.total_requests,
                "successful": stats.successful_requests,
                "failed": stats.failed_requests,
                "success_rate_percent": round(
                    (stats.successful_requests / stats.total_requests * 100)
                    if stats.total_requests > 0
                    else 0.0,
                    2
                )
            },
            "performance": {
                "avg_duration_ms": round(stats.avg_duration_ms, 2),
                "total_duration_ms": round(stats.total_duration_ms, 2),
                "recent_avg_ms": round(recent_stats.avg_duration_ms, 2)
            },
            "caching": {
                "cache_hits": stats.cache_hits,
                "cache_misses": stats.cache_misses,
                "cache_hit_rate_percent": round(
                    (stats.cache_hits / (stats.cache_hits + stats.cache_misses) * 100)
                    if (stats.cache_hits + stats.cache_misses) > 0
                    else 0.0,
                    2
                ),
                "by_category": dict(self._cache_events)
            },
            "security": {
                "validation_failures": stats.validation_failures,
                "authorization_denials": stats.authorization_denials
            },
            "tool_usage": dict(sorted(
                stats.tool_usage.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]),
            "top_errors": self.get_error_summary(5),
            "system_health": self.get_system_health()
        }

    def _get_metrics_in_window(self, window_minutes: int) -> List[ToolMetric]:
        """Get metrics within a time window"""
        cutoff_time = time.time() - (window_minutes * 60)
        return [m for m in self._metrics if m.end_time >= cutoff_time]

    def _get_top_tools(self, limit: int) -> List[Dict[str, Any]]:
        """Get top N most used tools"""
        return [
            {"tool": tool, "count": count}
            for tool, count in sorted(
                self._tool_usage.items(),
                key=lambda x: x[1],
                reverse=True
            )[:limit]
        ]

    def reset_stats(self):
        """Reset all statistics"""
        self._metrics.clear()
        self._tool_usage.clear()
        self._tool_errors.clear()
        self._error_messages.clear()
        self._cache_hits = 0
        self._cache_misses = 0
        self._validation_failures = 0
        self._authorization_denials = 0
        self._start_time = time.time()
        logger.info("Telemetry statistics reset")


# Global telemetry instance
_telemetry_manager: Optional[TelemetryManager] = None


def get_telemetry_manager() -> TelemetryManager:
    """Get or create global telemetry manager instance"""
    global _telemetry_manager
    if _telemetry_manager is None:
        _telemetry_manager = TelemetryManager(max_history=1000)
    return _telemetry_manager


def record_tool_call(
    tool_name: str,
    duration_ms: float,
    success: bool,
    error_message: Optional[str] = None,
    cached: bool = False
):
    """Convenience function to record tool call"""
    get_telemetry_manager().record_tool_call(
        tool_name, duration_ms, success, error_message, cached
    )


def get_stats() -> TelemetryStats:
    """Convenience function to get statistics"""
    return get_telemetry_manager().get_stats()


def get_dashboard() -> Dict[str, Any]:
    """Convenience function to get dashboard"""
    return get_telemetry_manager().get_dashboard()
