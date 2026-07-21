"""
DreamCo Platform — Structured Telemetry and Observability
==========================================================

Every ``CapabilityNode`` execution, every orchestrator lifecycle event,
and every workflow transition writes a structured ``TelemetryEvent`` to
a ``TelemetryCollector``.

The collector provides:
* Per-capability latency, cost, and success-rate metrics
* Export snapshot for Dream Brain ingestion
* Anomaly surface via P95 / P99 latency detection
* Audit trail for governance / compliance

Design
------
The ``TelemetryCollector`` is intentionally in-memory.  In production,
wire the ``record()`` method to push events to Prometheus, OpenTelemetry,
or your chosen observability backend.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Telemetry level
# ---------------------------------------------------------------------------

class TelemetryLevel(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


# ---------------------------------------------------------------------------
# Telemetry event
# ---------------------------------------------------------------------------

@dataclass
class TelemetryEvent:
    """
    A single structured telemetry record.

    Attributes
    ----------
    telemetry_id : str
        Unique identifier.
    capability_id : str
        Which capability this measurement belongs to.
    source : str
        Emitting component (bot_id, orchestrator, etc.).
    level : TelemetryLevel
        Severity / verbosity level.
    metric_name : str
        The specific measurement (e.g. ``"latency_ms"``, ``"cost_usd"``).
    metric_value : float
        Numeric value of the measurement.
    unit : str
        Measurement unit (e.g. ``"ms"``, ``"usd"``, ``"count"``).
    success : bool | None
        Whether the associated operation succeeded.
    correlation_id : str | None
        Links this telemetry event to a larger operation trace.
    timestamp : float
        Unix timestamp.
    tags : dict
        Arbitrary key-value labels (e.g. ``{"env": "prod"}``).
    message : str
        Optional human-readable annotation.
    metadata : dict
        Arbitrary extra metadata.
    """

    capability_id: str
    source: str
    metric_name: str
    metric_value: float
    level: TelemetryLevel = TelemetryLevel.INFO
    unit: str = ""
    success: Optional[bool] = None
    correlation_id: Optional[str] = None
    telemetry_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)
    tags: Dict[str, str] = field(default_factory=dict)
    message: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "telemetry_id": self.telemetry_id,
            "capability_id": self.capability_id,
            "source": self.source,
            "level": self.level.value,
            "metric_name": self.metric_name,
            "metric_value": self.metric_value,
            "unit": self.unit,
            "success": self.success,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp,
            "tags": dict(self.tags),
            "message": self.message,
            "metadata": dict(self.metadata),
        }

    def __repr__(self) -> str:
        return (
            f"TelemetryEvent({self.capability_id!r}, "
            f"{self.metric_name}={self.metric_value} {self.unit})"
        )


# ---------------------------------------------------------------------------
# Telemetry collector
# ---------------------------------------------------------------------------

class TelemetryCollector:
    """
    In-memory structured telemetry collector.

    Every ``CapabilityNode`` execution should write at minimum a
    ``latency_ms`` and ``cost_usd`` event via ``record()``.

    Parameters
    ----------
    max_events : int
        Maximum number of raw events to retain (FIFO eviction).
        Set to 0 for unlimited. Default: 50_000.
    """

    def __init__(self, max_events: int = 50_000) -> None:
        self._events: List[TelemetryEvent] = []
        self._max_events = max_events

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def record(self, event: TelemetryEvent) -> TelemetryEvent:
        """Store *event* and apply FIFO eviction if max_events is set."""
        self._events.append(event)
        if self._max_events > 0 and len(self._events) > self._max_events:
            self._events.pop(0)
        return event

    def record_latency(
        self,
        capability_id: str,
        source: str,
        latency_ms: float,
        *,
        success: bool = True,
        correlation_id: str | None = None,
    ) -> TelemetryEvent:
        """Convenience helper: record a latency measurement."""
        return self.record(TelemetryEvent(
            capability_id=capability_id,
            source=source,
            metric_name="latency_ms",
            metric_value=latency_ms,
            unit="ms",
            success=success,
            correlation_id=correlation_id,
            level=TelemetryLevel.INFO,
        ))

    def record_cost(
        self,
        capability_id: str,
        source: str,
        cost_usd: float,
        *,
        correlation_id: str | None = None,
    ) -> TelemetryEvent:
        """Convenience helper: record a cost measurement."""
        return self.record(TelemetryEvent(
            capability_id=capability_id,
            source=source,
            metric_name="cost_usd",
            metric_value=cost_usd,
            unit="usd",
            correlation_id=correlation_id,
            level=TelemetryLevel.INFO,
        ))

    def record_error(
        self,
        capability_id: str,
        source: str,
        message: str,
        *,
        correlation_id: str | None = None,
    ) -> TelemetryEvent:
        """Convenience helper: record an error event."""
        return self.record(TelemetryEvent(
            capability_id=capability_id,
            source=source,
            metric_name="error_count",
            metric_value=1.0,
            unit="count",
            success=False,
            correlation_id=correlation_id,
            level=TelemetryLevel.ERROR,
            message=message,
        ))

    # ------------------------------------------------------------------
    # Read / query
    # ------------------------------------------------------------------

    def get_events(
        self,
        capability_id: str | None = None,
        source: str | None = None,
        metric_name: str | None = None,
        level: TelemetryLevel | None = None,
        since: float | None = None,
        limit: int | None = None,
    ) -> List[TelemetryEvent]:
        """
        Return stored events matching all supplied filters (AND logic).

        Results are newest-first.
        """
        results = list(self._events)
        if capability_id is not None:
            results = [e for e in results if e.capability_id == capability_id]
        if source is not None:
            results = [e for e in results if e.source == source]
        if metric_name is not None:
            results = [e for e in results if e.metric_name == metric_name]
        if level is not None:
            results = [e for e in results if e.level == level]
        if since is not None:
            results = [e for e in results if e.timestamp >= since]
        results.sort(key=lambda e: e.timestamp, reverse=True)
        if limit is not None:
            results = results[:limit]
        return results

    # ------------------------------------------------------------------
    # Summarisation / metrics
    # ------------------------------------------------------------------

    def summarize(self, capability_id: str | None = None) -> Dict[str, Any]:
        """
        Return aggregate metrics, optionally scoped to *capability_id*.

        Returns
        -------
        dict with keys:
        ``total_events``, ``by_metric``, ``error_rate``,
        ``avg_latency_ms``, ``total_cost_usd``, ``p95_latency_ms``.
        """
        events = self.get_events(capability_id=capability_id)
        if not events:
            return {
                "total_events": 0,
                "by_metric": {},
                "error_rate": 0.0,
                "avg_latency_ms": 0.0,
                "total_cost_usd": 0.0,
                "p95_latency_ms": 0.0,
            }

        by_metric: Dict[str, int] = {}
        latencies: List[float] = []
        total_cost = 0.0
        error_count = 0
        total_with_success = 0

        for evt in events:
            by_metric[evt.metric_name] = by_metric.get(evt.metric_name, 0) + 1
            if evt.metric_name == "latency_ms":
                latencies.append(evt.metric_value)
            if evt.metric_name == "cost_usd":
                total_cost += evt.metric_value
            if evt.success is not None:
                total_with_success += 1
                if not evt.success:
                    error_count += 1

        avg_latency = sum(latencies) / len(latencies) if latencies else 0.0
        p95_latency = 0.0
        if latencies:
            sorted_l = sorted(latencies)
            idx = int(len(sorted_l) * 0.95)
            p95_latency = sorted_l[min(idx, len(sorted_l) - 1)]

        error_rate = (
            error_count / total_with_success if total_with_success > 0 else 0.0
        )

        return {
            "total_events": len(events),
            "by_metric": by_metric,
            "error_rate": round(error_rate, 4),
            "avg_latency_ms": round(avg_latency, 2),
            "total_cost_usd": round(total_cost, 4),
            "p95_latency_ms": round(p95_latency, 2),
        }

    def export(self) -> List[Dict[str, Any]]:
        """Return all events serialised as a list of dicts."""
        return [e.to_dict() for e in self._events]

    # ------------------------------------------------------------------
    # Maintenance
    # ------------------------------------------------------------------

    def clear(self) -> None:
        """Remove all stored events."""
        self._events.clear()

    def __len__(self) -> int:
        return len(self._events)

    def __repr__(self) -> str:
        return f"TelemetryCollector({len(self._events)} events)"
