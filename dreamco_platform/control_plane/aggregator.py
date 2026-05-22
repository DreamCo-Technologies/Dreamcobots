"""
DreamCo Control Plane — Dashboard Aggregator
=============================================

``DashboardAggregator`` is the single entry point for all dashboard API
handlers.  It fans out to the seven specialised gateways and merges their
snapshots into the payloads served by the REST endpoints.

Architecture
------------
::

    DashboardAggregator
    ├── HealthGateway      (/api/dashboard/health)
    ├── MetricsGateway     (/api/dashboard/observability)
    ├── LearningGateway    (/api/dashboard/learning)
    ├── WorkflowGateway    (/api/dashboard/workflows)
    ├── RegistryGateway    (/api/dashboard/marketplace)
    ├── RevenueGateway     (/api/dashboard/revenue)
    └── (security signals) (/api/dashboard/security)

Usage
-----
::

    from dreamco_platform.control_plane import DashboardAggregator

    agg = DashboardAggregator()
    summary = agg.summary()           # /api/dashboard/summary
    health  = agg.health_snapshot()   # /api/dashboard/health
"""

from __future__ import annotations

import time
from typing import Any, Dict, Optional

from dreamco_platform.control_plane.health_gateway import HealthGateway
from dreamco_platform.control_plane.learning_gateway import LearningGateway
from dreamco_platform.control_plane.metrics_gateway import MetricsGateway
from dreamco_platform.control_plane.registry_gateway import RegistryGateway
from dreamco_platform.control_plane.revenue_gateway import RevenueGateway
from dreamco_platform.control_plane.workflow_gateway import WorkflowGateway
from dreamco_platform.observability.audit_log import AuditLog


class DashboardAggregator:
    """
    Unified Command Center aggregation layer.

    All gateway instances are created internally with sane defaults.
    Pass pre-configured instances to wire up production data sources.

    Parameters
    ----------
    health_gateway : HealthGateway | None
    metrics_gateway : MetricsGateway | None
    learning_gateway : LearningGateway | None
    workflow_gateway : WorkflowGateway | None
    registry_gateway : RegistryGateway | None
    revenue_gateway : RevenueGateway | None
    audit_log : AuditLog | None
    """

    def __init__(
        self,
        health_gateway: Optional[HealthGateway] = None,
        metrics_gateway: Optional[MetricsGateway] = None,
        learning_gateway: Optional[LearningGateway] = None,
        workflow_gateway: Optional[WorkflowGateway] = None,
        registry_gateway: Optional[RegistryGateway] = None,
        revenue_gateway: Optional[RevenueGateway] = None,
        audit_log: Optional[AuditLog] = None,
    ) -> None:
        self.health = health_gateway or HealthGateway()
        self.metrics = metrics_gateway or MetricsGateway()
        self.learning = learning_gateway or LearningGateway()
        self.workflows = workflow_gateway or WorkflowGateway()
        self.registry = registry_gateway or RegistryGateway()
        self.revenue = revenue_gateway or RevenueGateway()
        self._audit_log = audit_log or AuditLog()

    # ------------------------------------------------------------------
    # Per-section snapshots  (mapped 1-to-1 onto REST endpoints)
    # ------------------------------------------------------------------

    def health_snapshot(self) -> Dict[str, Any]:
        """/api/dashboard/health"""
        return self.health.snapshot()

    def observability_snapshot(self) -> Dict[str, Any]:
        """/api/dashboard/observability"""
        return self.metrics.snapshot()

    def learning_snapshot(self) -> Dict[str, Any]:
        """/api/dashboard/learning"""
        return self.learning.snapshot()

    def workflows_snapshot(self) -> Dict[str, Any]:
        """/api/dashboard/workflows"""
        return self.workflows.snapshot()

    def marketplace_snapshot(self) -> Dict[str, Any]:
        """/api/dashboard/marketplace"""
        return self.registry.snapshot()

    def revenue_snapshot(self) -> Dict[str, Any]:
        """/api/dashboard/revenue"""
        return self.revenue.snapshot()

    def security_snapshot(self) -> Dict[str, Any]:
        """/api/dashboard/security"""
        recent_entries = self._audit_log.query(limit=20)
        security_events = [
            e.to_dict()
            for e in self._audit_log.query(limit=50)
            if e.action.startswith("security.") or e.outcome == "denied"
        ]
        return {
            "recent_audit_entries": [e.to_dict() for e in recent_entries],
            "security_events": security_events,
            "total_audit_entries": self._audit_log.total_recorded(),
            "snapshot_at": time.time(),
        }

    # ------------------------------------------------------------------
    # Master summary — /api/dashboard/summary
    # ------------------------------------------------------------------

    def summary(self) -> Dict[str, Any]:
        """/api/dashboard/summary — top-level aggregation of all sections."""
        h = self.health.snapshot()
        r = self.revenue.snapshot()
        reg = self.registry.snapshot()
        wf = self.workflows.snapshot()
        learn = self.learning.snapshot()

        return {
            "system_health": {
                "total_bots": h["total_bots"],
                "unhealthy_bots": len(h["unhealthy_bots"]),
                "quarantined_bots": len(h["quarantined_bots"]),
                "uptime_seconds": h["uptime_seconds"],
                "heartbeat": h["heartbeat"],
            },
            "learning_intelligence": {
                "reward_mean": learn["reward_stats"]["mean"],
                "reward_total": learn["reward_stats"]["total"],
                "drift_indicator": learn["reward_stats"]["drift_indicator"],
                "top_strategy_count": len(learn["top_strategies"]),
            },
            "revenue_operations": {
                "arr": r["arr"],
                "mrr": r["mrr"],
                "total_customers": r["total_customers"],
                "datasets_sold": r["datasets_sold"],
            },
            "bot_network": {
                "total_bots": reg["total_bots"],
                "lifecycle_breakdown": reg["lifecycle_breakdown"],
                "category_count": len(reg["category_breakdown"]),
            },
            "workflow_operations": {
                "active_orchestrators": wf["active_orchestrators"],
                "pipeline_count": len(wf["pipeline_health"]),
            },
            "snapshot_at": time.time(),
        }
