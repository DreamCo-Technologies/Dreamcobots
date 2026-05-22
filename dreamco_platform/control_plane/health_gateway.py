"""
DreamCo Control Plane — Health Gateway
=======================================

Aggregates system-level health signals:

* per-bot health status breakdown (healthy / degraded / unhealthy / unknown)
* per-bot lifecycle state breakdown
* platform heartbeat timestamp
* CI / deployment status stub (extensible via ``set_ci_status``)
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from dreamco_platform.registry.bot_registry import (
    BotLifecycleState,
    BotRegistry,
    HealthStatus,
)


class HealthGateway:
    """
    Single access point for platform health signals.

    Parameters
    ----------
    registry : BotRegistry
        The canonical bot registry to query.
    """

    def __init__(self, registry: Optional[BotRegistry] = None) -> None:
        self._registry = registry or BotRegistry()
        self._ci_status: Dict[str, Any] = {}
        self._started_at: float = time.time()

    # ------------------------------------------------------------------
    # CI / external status
    # ------------------------------------------------------------------

    def set_ci_status(self, pipeline: str, status: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Record the result of a CI pipeline run."""
        self._ci_status[pipeline] = {
            "pipeline": pipeline,
            "status": status,
            "recorded_at": time.time(),
            "metadata": metadata or {},
        }

    # ------------------------------------------------------------------
    # Aggregation
    # ------------------------------------------------------------------

    def snapshot(self) -> Dict[str, Any]:
        """Return a health snapshot suitable for the dashboard API."""
        bots = self._registry.list_all()
        health_counts: Dict[str, int] = {s.value: 0 for s in HealthStatus}
        lifecycle_counts: Dict[str, int] = {s.value: 0 for s in BotLifecycleState}

        for bot in bots:
            health_counts[bot.health.value] += 1
            lifecycle_counts[bot.lifecycle_state.value] += 1

        return {
            "uptime_seconds": round(time.time() - self._started_at, 2),
            "heartbeat": time.time(),
            "total_bots": len(bots),
            "health_breakdown": health_counts,
            "lifecycle_breakdown": lifecycle_counts,
            "ci_pipelines": list(self._ci_status.values()),
            "unhealthy_bots": [
                b.bot_id for b in bots if b.health == HealthStatus.UNHEALTHY
            ],
            "quarantined_bots": [
                b.bot_id for b in bots
                if b.lifecycle_state == BotLifecycleState.QUARANTINED
            ],
            "snapshot_at": time.time(),
        }
