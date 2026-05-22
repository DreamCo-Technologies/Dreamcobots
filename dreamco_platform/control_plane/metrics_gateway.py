"""
DreamCo Control Plane — Metrics Gateway
=========================================

Bridges the platform ``TelemetryCollector`` and ``MetricsCollector`` into a
single normalised snapshot consumed by the dashboard and Prometheus exporters.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from dreamco_platform.observability.telemetry import TelemetryCollector
from dreamco_platform.observability.metrics import MetricsCollector


class MetricsGateway:
    """
    Aggregates telemetry and metrics into a normalised dashboard payload.

    Parameters
    ----------
    telemetry : TelemetryCollector | None
        Platform telemetry collector.  A fresh empty collector is used if
        ``None`` is supplied.
    metrics : MetricsCollector | None
        Platform metrics collector.  A fresh empty collector is used if
        ``None`` is supplied.
    """

    def __init__(
        self,
        telemetry: Optional[TelemetryCollector] = None,
        metrics: Optional[MetricsCollector] = None,
    ) -> None:
        self._telemetry = telemetry if telemetry is not None else TelemetryCollector()
        self._metrics = metrics if metrics is not None else MetricsCollector()

    # ------------------------------------------------------------------
    # Public accessors
    # ------------------------------------------------------------------

    @property
    def telemetry(self) -> TelemetryCollector:
        return self._telemetry

    @property
    def metrics(self) -> MetricsCollector:
        return self._metrics

    # ------------------------------------------------------------------
    # Snapshot
    # ------------------------------------------------------------------

    def snapshot(self) -> Dict[str, Any]:
        """Return a combined observability snapshot for the dashboard."""
        tel_summary = self._telemetry.summarize()
        metrics_snap = self._metrics.snapshot()

        recent_errors: List[Dict[str, Any]] = [
            e.to_dict()
            for e in self._telemetry.get_events(metric_name="error_count", limit=10)
        ]

        return {
            "telemetry": tel_summary,
            "metrics": metrics_snap,
            "recent_errors": recent_errors,
            "snapshot_at": time.time(),
        }
