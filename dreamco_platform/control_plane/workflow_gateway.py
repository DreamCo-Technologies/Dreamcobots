"""
DreamCo Control Plane — Workflow Gateway
==========================================

Aggregates active workflow counts, pipeline health, and orchestrator status
from the platform's ``OrchestratorRegistry``.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from dreamco_platform.orchestration.base_orchestrator import OrchestratorRegistry


class WorkflowGateway:
    """
    Dashboard gateway for workflow / pipeline operations.

    Parameters
    ----------
    registry : OrchestratorRegistry | None
        Shared orchestrator registry.  A fresh empty registry is created if
        ``None`` is supplied.
    """

    def __init__(self, registry: Optional[OrchestratorRegistry] = None) -> None:
        self._registry = registry or OrchestratorRegistry()
        self._pipeline_health: Dict[str, Any] = {}

    # ------------------------------------------------------------------
    # Pipeline health stubs (injected by CI / deployment hooks)
    # ------------------------------------------------------------------

    def set_pipeline_health(
        self,
        pipeline: str,
        status: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Record Actions pipeline health for *pipeline*."""
        self._pipeline_health[pipeline] = {
            "pipeline": pipeline,
            "status": status,
            "recorded_at": time.time(),
            "metadata": metadata or {},
        }

    # ------------------------------------------------------------------
    # Snapshot
    # ------------------------------------------------------------------

    def snapshot(self) -> Dict[str, Any]:
        """Return a workflow operations snapshot for the dashboard."""
        all_orchestrators = self._registry.list_all()
        status_counts: Dict[str, int] = {}
        orchestrator_summaries: List[Dict[str, Any]] = []

        for orch in all_orchestrators:
            st = orch.status()
            status_val = st.get("status", "unknown") if isinstance(st, dict) else str(st)
            status_counts[status_val] = status_counts.get(status_val, 0) + 1
            orchestrator_summaries.append(
                {
                    "orchestrator_id": orch.orchestrator_id,
                    "name": orch.name,
                    "status": status_val,
                }
            )

        running_count = status_counts.get("running", 0)

        return {
            "active_orchestrators": running_count,
            "orchestrator_status_breakdown": status_counts,
            "orchestrators": orchestrator_summaries,
            "pipeline_health": list(self._pipeline_health.values()),
            "snapshot_at": time.time(),
        }
