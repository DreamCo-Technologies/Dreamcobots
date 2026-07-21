"""
DreamOps Bot — Tier-aware AI Operations Automation Suite.

Integrates anomaly detection, auto-scaling, ops command, bottleneck
detection, auto-failover, cost reduction, throughput maximization,
resilience scoring, and intelligent task delegation.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.

Usage
-----
    from bots.dreamops import DreamOpsBot, Tier

    bot = DreamOpsBot(tier=Tier.PRO)
    print(bot.dashboard())
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ai-models-integration"))

from tiers import Tier, get_tier_config, get_upgrade_path  # noqa: F401
from framework import GlobalAISourcesFlow  # noqa: F401

from bots.dreamops.tiers import BOT_FEATURES, WORKFLOW_LIMITS, BOT_LIMITS, get_bot_tier_info
from bots.dreamops.anomaly_detection import AnomalyDetector, WorkflowMetrics, AnomalyAlert
from bots.dreamops.auto_scaling import ScalingEngine, LoadMetrics, ScalingAction
from bots.dreamops.ops_commander import OpsCommander
from bots.dreamops.bottleneck_detector import BottleneckDetector, WorkflowStage
from bots.dreamops.auto_failover import AutoFailover
from bots.dreamops.cost_reduction import CostReductionEngine, CostData
from bots.dreamops.throughput_maximizer import ThroughputMaximizer, FlowStage
from bots.dreamops.resilience_scorer import ResilienceScorer, ResilienceMetrics
from bots.dreamops.task_delegation import TaskDelegationAI, Task
from bots.dreamops.dashboard import render_full_dashboard


class DreamOpsTierError(Exception):
    """Raised when a feature is not available on the current tier."""


class DreamOpsBot:
    """
    DreamOps AI Automation Suite bot.

    Provides a unified interface to all DreamOps operational tools,
    gated by the active subscription tier.
    """

    def __init__(self, tier: Tier = Tier.FREE) -> None:
        self._tier = tier
        self._anomaly_detector = AnomalyDetector()
        self._scaling_engine = ScalingEngine()
        self._ops_commander = OpsCommander()
        self._bottleneck_detector = BottleneckDetector()
        self._auto_failover = AutoFailover()
        self._cost_engine = CostReductionEngine()
        self._throughput_maximizer = ThroughputMaximizer()
        self._resilience_scorer = ResilienceScorer()
        self._task_delegation = TaskDelegationAI()

    # ------------------------------------------------------------------
    # Tier property
    # ------------------------------------------------------------------

    @property
    def tier(self) -> Tier:
        return self._tier

    # ------------------------------------------------------------------
    # Sub-module properties
    # ------------------------------------------------------------------

    @property
    def anomaly_detector(self) -> AnomalyDetector:
        return self._anomaly_detector

    @property
    def scaling_engine(self) -> ScalingEngine:
        return self._scaling_engine

    @property
    def ops_commander(self) -> OpsCommander:
        return self._ops_commander

    @property
    def bottleneck_detector(self) -> BottleneckDetector:
        return self._bottleneck_detector

    @property
    def auto_failover(self) -> AutoFailover:
        return self._auto_failover

    @property
    def cost_engine(self) -> CostReductionEngine:
        return self._cost_engine

    @property
    def throughput_maximizer(self) -> ThroughputMaximizer:
        return self._throughput_maximizer

    @property
    def resilience_scorer(self) -> ResilienceScorer:
        return self._resilience_scorer

    @property
    def task_delegation(self) -> TaskDelegationAI:
        return self._task_delegation

    # ------------------------------------------------------------------
    # Tier guards
    # ------------------------------------------------------------------

    def _require_pro(self, feature: str) -> None:
        if self._tier == Tier.FREE:
            raise DreamOpsTierError(
                f"'{feature}' requires PRO or ENTERPRISE tier. "
                f"Upgrade path: {get_upgrade_path(self._tier)}"
            )

    def _require_enterprise(self, feature: str) -> None:
        if self._tier in (Tier.FREE, Tier.PRO):
            raise DreamOpsTierError(
                f"'{feature}' requires ENTERPRISE tier. "
                f"Upgrade path: {get_upgrade_path(self._tier)}"
            )

    # ------------------------------------------------------------------
    # Tier-gated operations
    # ------------------------------------------------------------------

    def run_anomaly_detection(self, workflow_id: str, metrics: WorkflowMetrics):
        """Run anomaly detection on workflow metrics. Requires PRO+."""
        self._require_pro("anomaly_detection")
        return self._anomaly_detector.analyze_workflow(workflow_id, metrics)

    def auto_scale(self, task_id: str, load_metrics: LoadMetrics):
        """Analyze and trigger auto-scaling for a task. Requires PRO+."""
        self._require_pro("auto_scaling")
        action = self._scaling_engine.analyze_demand(task_id, load_metrics)
        if action == ScalingAction.SCALE_UP:
            return self._scaling_engine.trigger_scale_up(task_id)
        if action == ScalingAction.SCALE_DOWN:
            return self._scaling_engine.trigger_scale_down(task_id)
        return self._scaling_engine.get_resource_allocation(task_id)

    def monitor_operations(self):
        """Monitor all registered systems. Requires PRO+."""
        self._require_pro("monitor_operations")
        return self._ops_commander.monitor_systems()

    def detect_bottlenecks(self, workflow_id: str, stages: list):
        """Detect bottlenecks in a workflow. Requires PRO+."""
        self._require_pro("bottleneck_detection")
        return self._bottleneck_detector.analyze_workflow(workflow_id, stages)

    def manage_failover(self, primary_id: str, backup_id: str, config: dict = None):
        """Configure auto-failover for a system pair. Requires ENTERPRISE."""
        self._require_enterprise("auto_failover")
        return self._auto_failover.configure_failover(primary_id, backup_id, config or {})

    def analyze_costs(self, dept_id: str, cost_data: CostData):
        """Analyze departmental costs and identify waste. Requires ENTERPRISE."""
        self._require_enterprise("cost_reduction")
        self._cost_engine.analyze_costs(dept_id, cost_data)
        return self._cost_engine.identify_waste(dept_id)

    def maximize_throughput(self, flow_id: str, stages: list):
        """Maximize throughput for a flow. Requires ENTERPRISE."""
        self._require_enterprise("throughput_maximizer")
        self._throughput_maximizer.analyze_flow(flow_id, stages)
        self._throughput_maximizer.identify_constraints(flow_id)
        return self._throughput_maximizer.optimize_flow(flow_id)

    def score_resilience(self, system_id: str, metrics: ResilienceMetrics):
        """Score system resilience. Requires ENTERPRISE."""
        self._require_enterprise("resilience_scorer")
        self._resilience_scorer.score_system(system_id, metrics)
        return self._resilience_scorer.generate_resilience_report(system_id)

    # ------------------------------------------------------------------
    # Free-tier operations
    # ------------------------------------------------------------------

    def dashboard(self) -> str:
        """Render the DreamOps dashboard (available on all tiers)."""
        return render_full_dashboard(self)

    def get_tier_info(self) -> dict:
        """Return information about the current tier and its features."""
        return get_bot_tier_info(self._tier)
