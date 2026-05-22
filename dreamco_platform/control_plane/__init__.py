"""
DreamCo Platform — Unified Command Center Control Plane
=======================================================

The control plane is the single source of truth for all operational
dashboards, live telemetry, and cross-system observability.

Sub-modules
-----------
correlation     — Universal CorrelationChain propagated across every subsystem
aggregator      — Top-level DashboardAggregator that fans-out to all gateways
health_gateway  — System-health: uptime, heartbeat, CI status
metrics_gateway — Telemetry / Prometheus metrics snapshot
learning_gateway — Rewards, drift detection, retraining status
workflow_gateway — Actions pipeline health, active workflow counts
registry_gateway — Bot catalog, lifecycle state summary
revenue_gateway — ARR/MRR, billing tier distribution
"""

from dreamco_platform.control_plane.correlation import CorrelationChain
from dreamco_platform.control_plane.aggregator import DashboardAggregator

__all__ = ["CorrelationChain", "DashboardAggregator"]
