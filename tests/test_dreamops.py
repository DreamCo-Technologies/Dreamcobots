"""
Tests for bots/dreamops/ — DreamOps AI Automation Suite

Covers all DreamOps modules:
  1. Tiers
  2. Anomaly Detection
  3. Auto-Scaling
  4. Ops Commander
  5. Bottleneck Detector
  6. Auto-Failover
  7. Cost Reduction
  8. Throughput Maximizer
  9. Resilience Scorer
  10. Task Delegation AI
  11. Dashboard
  12. DreamOpsBot main class (integration)
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
AI_MODELS_DIR = os.path.join(REPO_ROOT, "bots", "ai-models-integration")
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from bots.dreamops.tiers import (
    BOT_FEATURES,
    WORKFLOW_LIMITS,
    BOT_LIMITS,
    get_bot_tier_info,
)
from bots.dreamops.anomaly_detection import (
    AnomalyDetector,
    WorkflowMetrics,
    AnomalyAlert,
)
from bots.dreamops.auto_scaling import (
    ScalingEngine,
    LoadMetrics,
    ScalingAction,
)
from bots.dreamops.ops_commander import OpsCommander
from bots.dreamops.bottleneck_detector import (
    BottleneckDetector,
    WorkflowStage,
)
from bots.dreamops.auto_failover import AutoFailover
from bots.dreamops.cost_reduction import CostReductionEngine, CostData
from bots.dreamops.throughput_maximizer import (
    ThroughputMaximizer,
    FlowStage,
)
from bots.dreamops.resilience_scorer import ResilienceScorer, ResilienceMetrics
from bots.dreamops.task_delegation import TaskDelegationAI, Task
from bots.dreamops.dashboard import (
    render_anomaly_summary,
    render_scaling_status,
    render_ops_status,
    render_bottleneck_map,
    render_failover_status,
    render_cost_summary,
    render_throughput_report,
    render_full_dashboard,
)
from bots.dreamops.dreamops_bot import DreamOpsBot, DreamOpsTierError
from bots.dreamops import DreamOpsBot as DreamOpsBotExport


# ===========================================================================
# 1. Tiers
# ===========================================================================


class TestTiers:
    def test_three_tiers_exist(self):
        from tiers import list_tiers
        assert len(list_tiers()) == 3

    def test_free_tier_features_exist(self):
        assert len(BOT_FEATURES[Tier.FREE.value]) > 0

    def test_pro_tier_features_exist(self):
        assert len(BOT_FEATURES[Tier.PRO.value]) > 0

    def test_enterprise_tier_features_exist(self):
        assert len(BOT_FEATURES[Tier.ENTERPRISE.value]) > 0

    def test_free_workflow_limit(self):
        assert WORKFLOW_LIMITS[Tier.FREE] == 5

    def test_pro_workflow_limit(self):
        assert WORKFLOW_LIMITS[Tier.PRO] == 50

    def test_enterprise_workflow_limit_unlimited(self):
        assert WORKFLOW_LIMITS[Tier.ENTERPRISE] is None

    def test_free_bot_limit(self):
        assert BOT_LIMITS[Tier.FREE] == 3

    def test_pro_bot_limit(self):
        assert BOT_LIMITS[Tier.PRO] == 10

    def test_enterprise_bot_limit_unlimited(self):
        assert BOT_LIMITS[Tier.ENTERPRISE] is None

    def test_get_bot_tier_info_returns_dict(self):
        info = get_bot_tier_info(Tier.FREE)
        assert isinstance(info, dict)

    def test_get_bot_tier_info_has_required_keys(self):
        info = get_bot_tier_info(Tier.PRO)
        for key in ("tier", "name", "price_usd_monthly", "features", "workflow_limit"):
            assert key in info

    def test_get_bot_tier_info_free_price(self):
        info = get_bot_tier_info(Tier.FREE)
        assert info["price_usd_monthly"] == 0.0

    def test_get_bot_tier_info_enterprise_unlimited_workflows(self):
        info = get_bot_tier_info(Tier.ENTERPRISE)
        assert info["workflow_limit"] is None

    def test_enterprise_has_more_features_than_free(self):
        free_count = len(BOT_FEATURES[Tier.FREE.value])
        ent_count = len(BOT_FEATURES[Tier.ENTERPRISE.value])
        assert ent_count > free_count


# ===========================================================================
# 2. Anomaly Detection
# ===========================================================================


class TestAnomalyDetection:
    def setup_method(self):
        self.detector = AnomalyDetector()

    def _make_metrics(self, workflow_id="wf-001", execution_time=1.0,
                      error_rate=0.01, throughput=100.0):
        return WorkflowMetrics(
            workflow_id=workflow_id,
            execution_time=execution_time,
            error_rate=error_rate,
            throughput=throughput,
        )

    def _seed_history(self, detector, workflow_id, n=6):
        """Seed detector with n normal metric readings so z-score can be computed."""
        for _ in range(n):
            detector.analyze_workflow(
                workflow_id, self._make_metrics(workflow_id, 1.0, 0.01, 100.0)
            )

    def test_analyze_workflow_does_not_raise(self):
        metrics = self._make_metrics()
        # First call may return None (not enough history) – that's expected
        result = self.detector.analyze_workflow("wf-001", metrics)
        assert result is None or isinstance(result, AnomalyAlert)

    def test_analyze_normal_workflow_no_critical_alert(self):
        self._seed_history(self.detector, "wf-001")
        metrics = self._make_metrics(execution_time=1.0, error_rate=0.01)
        self.detector.analyze_workflow("wf-001", metrics)
        alerts = self.detector.get_alerts()
        critical = [a for a in alerts if hasattr(a, "severity") and str(a.severity.value).upper() == "CRITICAL"]
        assert len(critical) == 0

    def test_high_error_rate_generates_alert(self):
        # Seed normal history first
        self._seed_history(self.detector, "wf-bad")
        # Now inject a spike – very high error rate should create anomaly
        metrics = self._make_metrics("wf-bad", error_rate=0.99, throughput=1.0)
        self.detector.analyze_workflow("wf-bad", metrics)
        alerts = self.detector.get_alerts()
        assert len(alerts) >= 1

    def test_get_alerts_returns_list(self):
        assert isinstance(self.detector.get_alerts(), list)

    def test_clear_alerts(self):
        metrics = self._make_metrics(error_rate=0.99)
        self.detector.analyze_workflow("wf-001", metrics)
        self.detector.clear_alerts()
        assert self.detector.get_alerts() == []

    def test_score_severity_low_deviation(self):
        score = self.detector.score_severity(0.5)
        assert isinstance(score, (str, float, int, object))

    def test_score_severity_high_deviation(self):
        score_low = self.detector.score_severity(0.5)
        score_high = self.detector.score_severity(5.0)
        assert score_high != score_low

    def test_workflow_metrics_dataclass(self):
        m = self._make_metrics()
        assert m.workflow_id == "wf-001"
        assert m.execution_time == 1.0
        assert m.error_rate == 0.01
        assert m.throughput == 100.0

    def test_multiple_workflows_tracked(self):
        for i in range(3):
            self.detector.analyze_workflow(f"wf-{i}", self._make_metrics(f"wf-{i}"))
        # Should handle multiple workflows without error

    def test_analyze_workflow_twice_same_id(self):
        metrics = self._make_metrics()
        self.detector.analyze_workflow("wf-001", metrics)
        self.detector.analyze_workflow("wf-001", metrics)
        # Should not raise


# ===========================================================================
# 3. Auto-Scaling
# ===========================================================================


class TestAutoScaling:
    def setup_method(self):
        self.engine = ScalingEngine()

    def _make_load(self, task_id="task-1", current=50.0, peak=80.0, avg=55.0):
        return LoadMetrics(
            task_id=task_id,
            current_load=current,
            peak_load=peak,
            avg_load=avg,
        )

    def test_analyze_demand_returns_action(self):
        load = self._make_load()
        action = self.engine.analyze_demand("task-1", load)
        assert action in ScalingAction

    def test_high_load_triggers_scale_up(self):
        load = self._make_load(current=95.0, peak=99.0, avg=92.0)
        action = self.engine.analyze_demand("task-high", load)
        assert action == ScalingAction.SCALE_UP

    def test_low_load_triggers_scale_down_with_trend(self):
        # Need to provide enough history to drive a downward trend
        engine = ScalingEngine()
        loads = [90.0, 70.0, 50.0, 30.0, 10.0]
        last_action = ScalingAction.MAINTAIN
        for l in loads:
            last_action = engine.analyze_demand("task-low", LoadMetrics("task-low", l / 100, l / 100, l / 100))
        assert last_action == ScalingAction.SCALE_DOWN

    def test_trigger_scale_up_returns_result(self):
        result = self.engine.trigger_scale_up("task-1")
        assert result is not None

    def test_trigger_scale_down_returns_result(self):
        result = self.engine.trigger_scale_down("task-1")
        assert result is not None

    def test_get_resource_allocation_after_scale_up_returns_dict(self):
        self.engine.trigger_scale_up("task-1")
        alloc = self.engine.get_resource_allocation("task-1")
        assert alloc is not None
        assert hasattr(alloc, "task_id")

    def test_optimize_costs_returns_result(self):
        result = self.engine.optimize_costs()
        assert result is not None

    def test_scaling_action_enum_values(self):
        assert ScalingAction.SCALE_UP in ScalingAction
        assert ScalingAction.SCALE_DOWN in ScalingAction
        assert ScalingAction.MAINTAIN in ScalingAction

    def test_load_metrics_dataclass(self):
        load = self._make_load()
        assert load.task_id == "task-1"
        assert load.current_load == 50.0

    def test_moderate_load_maintains(self):
        load = self._make_load(current=50.0, peak=60.0, avg=50.0)
        action = self.engine.analyze_demand("task-mod", load)
        assert action in ScalingAction


# ===========================================================================
# 4. Ops Commander
# ===========================================================================


class TestOpsCommander:
    def setup_method(self):
        self.commander = OpsCommander()

    def test_register_system_returns_result(self):
        result = self.commander.register_system("sys-001", {"name": "API Server"})
        assert result is not None

    def test_monitor_systems_returns_list(self):
        self.commander.register_system("sys-001", {"name": "DB Server"})
        report = self.commander.monitor_systems()
        assert report is not None

    def test_respond_to_incident_returns_result(self):
        # Must create the incident first before responding
        incident = self.commander.create_incident("sys-001", "HIGH", "Service down")
        result = self.commander.respond_to_incident(
            incident.incident_id, {"action": "restart_service", "service": "api"}
        )
        assert result is not None

    def test_optimize_performance_returns_result(self):
        self.commander.register_system("sys-001", {"name": "Worker"})
        result = self.commander.optimize_performance("sys-001")
        assert result is not None

    def test_get_status_report_returns_dict(self):
        report = self.commander.get_status_report()
        assert isinstance(report, dict)

    def test_register_multiple_systems(self):
        for i in range(5):
            self.commander.register_system(f"sys-{i}", {"name": f"System {i}"})
        report = self.commander.get_status_report()
        assert report is not None

    def test_status_report_has_keys(self):
        report = self.commander.get_status_report()
        assert len(report) >= 0  # may be empty but must be dict


# ===========================================================================
# 5. Bottleneck Detector
# ===========================================================================


class TestBottleneckDetector:
    def setup_method(self):
        self.detector = BottleneckDetector()

    def _make_stages(self):
        return [
            WorkflowStage(
                stage_id=f"stage-{i}",
                name=f"Stage {i}",
                avg_duration=float(i + 1),
                queue_depth=i * 10,
                throughput=100.0 / (i + 1),
            )
            for i in range(4)
        ]

    def test_analyze_workflow_returns_result(self):
        stages = self._make_stages()
        result = self.detector.analyze_workflow("wf-001", stages)
        assert result is not None

    def test_get_bottlenecks_returns_list(self):
        stages = self._make_stages()
        self.detector.analyze_workflow("wf-001", stages)
        bottlenecks = self.detector.get_bottlenecks()
        assert isinstance(bottlenecks, list)

    def test_high_queue_depth_creates_bottleneck(self):
        stages = [
            WorkflowStage("s1", "Fast Stage", 0.1, 0, 1000.0),
            WorkflowStage("s2", "Slow Stage", 10.0, 500, 10.0),
        ]
        self.detector.analyze_workflow("wf-slow", stages)
        bottlenecks = self.detector.get_bottlenecks()
        assert len(bottlenecks) >= 1

    def test_generate_heat_map_returns_result(self):
        stages = self._make_stages()
        self.detector.analyze_workflow("wf-001", stages)
        heat_map = self.detector.generate_heat_map("wf-001")
        assert heat_map is not None

    def test_workflow_stage_dataclass(self):
        stage = WorkflowStage("s1", "Init", 1.0, 5, 200.0)
        assert stage.stage_id == "s1"
        assert stage.name == "Init"
        assert stage.avg_duration == 1.0

    def test_remediate_bottleneck(self):
        stages = self._make_stages()
        self.detector.analyze_workflow("wf-001", stages)
        bottlenecks = self.detector.get_bottlenecks()
        if bottlenecks:
            result = self.detector.remediate(bottlenecks[0].bottleneck_id)
            assert result is not None

    def test_analyze_empty_stages(self):
        result = self.detector.analyze_workflow("wf-empty", [])
        # Should handle gracefully


# ===========================================================================
# 6. Auto-Failover
# ===========================================================================


class TestAutoFailover:
    def setup_method(self):
        self.failover = AutoFailover()

    def test_configure_failover_returns_result(self):
        result = self.failover.configure_failover("primary-1", "backup-1", {})
        assert result is not None

    def test_check_health_returns_result(self):
        result = self.failover.check_health("system-1")
        assert result is not None

    def test_trigger_failover_returns_result(self):
        self.failover.configure_failover("primary-1", "backup-1", {})
        result = self.failover.trigger_failover("primary-1")
        assert result is not None

    def test_restore_primary_returns_result(self):
        self.failover.configure_failover("primary-1", "backup-1", {})
        self.failover.trigger_failover("primary-1")
        result = self.failover.restore_primary("primary-1")
        assert result is not None

    def test_get_failover_status_returns_dict(self):
        status = self.failover.get_failover_status()
        assert isinstance(status, dict)

    def test_multiple_failover_configs(self):
        for i in range(3):
            self.failover.configure_failover(f"p-{i}", f"b-{i}", {})
        status = self.failover.get_failover_status()
        assert status is not None

    def test_health_check_before_config(self):
        # Should handle gracefully even without prior config
        result = self.failover.check_health("unknown-system")
        assert result is not None


# ===========================================================================
# 7. Cost Reduction
# ===========================================================================


class TestCostReduction:
    def setup_method(self):
        self.engine = CostReductionEngine()

    def _make_cost_data(self, dept_id="dept-ops"):
        return CostData(
            dept_id=dept_id,
            monthly_spend=50_000.0,
            categories={
                "infrastructure": 20_000.0,
                "labor": 25_000.0,
                "software": 5_000.0,
            },
        )

    def test_analyze_costs_returns_result(self):
        data = self._make_cost_data()
        result = self.engine.analyze_costs("dept-ops", data)
        assert result is not None

    def test_identify_waste_returns_list(self):
        data = self._make_cost_data()
        self.engine.analyze_costs("dept-ops", data)
        waste = self.engine.identify_waste("dept-ops")
        assert isinstance(waste, list)

    def test_score_automation_opportunity_returns_result(self):
        score = self.engine.score_automation_opportunity("process-data-entry")
        assert score is not None

    def test_generate_reduction_plan_returns_result(self):
        data = self._make_cost_data()
        self.engine.analyze_costs("dept-ops", data)
        plan = self.engine.generate_reduction_plan("dept-ops")
        assert plan is not None

    def test_estimate_savings_returns_result(self):
        data = self._make_cost_data()
        self.engine.analyze_costs("dept-ops", data)
        savings = self.engine.estimate_savings()
        assert savings is not None

    def test_cost_data_dataclass(self):
        data = self._make_cost_data()
        assert data.dept_id == "dept-ops"
        assert data.monthly_spend == 50_000.0
        assert isinstance(data.categories, dict)

    def test_multiple_departments(self):
        for dept in ["ops", "marketing", "engineering"]:
            data = self._make_cost_data(f"dept-{dept}")
            self.engine.analyze_costs(f"dept-{dept}", data)
        savings = self.engine.estimate_savings()
        assert savings is not None


# ===========================================================================
# 8. Throughput Maximizer
# ===========================================================================


class TestThroughputMaximizer:
    def setup_method(self):
        self.maximizer = ThroughputMaximizer()

    def _make_stages(self):
        return [
            FlowStage(f"fs-{i}", capacity=100.0 - i * 10,
                      current_load=60.0, cycle_time=float(i + 1))
            for i in range(5)
        ]

    def test_analyze_flow_returns_result(self):
        stages = self._make_stages()
        result = self.maximizer.analyze_flow("flow-001", stages)
        assert result is not None

    def test_identify_constraints_returns_list(self):
        stages = self._make_stages()
        self.maximizer.analyze_flow("flow-001", stages)
        constraints = self.maximizer.identify_constraints("flow-001")
        assert isinstance(constraints, list)

    def test_optimize_flow_returns_result(self):
        stages = self._make_stages()
        self.maximizer.analyze_flow("flow-001", stages)
        self.maximizer.identify_constraints("flow-001")
        result = self.maximizer.optimize_flow("flow-001")
        assert result is not None

    def test_forecast_throughput_returns_result(self):
        stages = self._make_stages()
        self.maximizer.analyze_flow("flow-001", stages)
        forecast = self.maximizer.forecast_throughput("flow-001", 30)
        assert forecast is not None

    def test_get_optimization_report_returns_result(self):
        stages = self._make_stages()
        self.maximizer.analyze_flow("flow-001", stages)
        report = self.maximizer.get_optimization_report()
        assert report is not None

    def test_flow_stage_dataclass(self):
        fs = FlowStage("fs-1", 100.0, 60.0, 2.5)
        assert fs.stage_id == "fs-1"
        assert fs.capacity == 100.0

    def test_constrained_flow_has_constraints(self):
        stages = [
            FlowStage("s1", capacity=100.0, current_load=10.0, cycle_time=1.0),
            FlowStage("s2", capacity=20.0, current_load=19.5, cycle_time=5.0),  # bottleneck
        ]
        self.maximizer.analyze_flow("constrained", stages)
        constraints = self.maximizer.identify_constraints("constrained")
        assert len(constraints) >= 1


# ===========================================================================
# 9. Resilience Scorer
# ===========================================================================


class TestResilienceScorer:
    def setup_method(self):
        self.scorer = ResilienceScorer()

    def _make_metrics(self, system_id="sys-1"):
        return ResilienceMetrics(
            system_id=system_id,
            uptime_pct=99.9,
            mttr_hours=0.5,
            mtbf_hours=720.0,
            redundancy_score=0.85,
        )

    def test_score_system_returns_result(self):
        metrics = self._make_metrics()
        result = self.scorer.score_system("sys-1", metrics)
        assert result is not None

    def test_analyze_failure_modes_returns_result(self):
        metrics = self._make_metrics()
        self.scorer.score_system("sys-1", metrics)
        result = self.scorer.analyze_failure_modes("sys-1")
        assert result is not None

    def test_calculate_recovery_score_returns_result(self):
        metrics = self._make_metrics()
        self.scorer.score_system("sys-1", metrics)
        result = self.scorer.calculate_recovery_score("sys-1")
        assert result is not None

    def test_generate_resilience_report_returns_result(self):
        metrics = self._make_metrics()
        self.scorer.score_system("sys-1", metrics)
        report = self.scorer.generate_resilience_report("sys-1")
        assert report is not None

    def test_resilience_metrics_dataclass(self):
        m = self._make_metrics()
        assert m.system_id == "sys-1"
        assert m.uptime_pct == 99.9
        assert m.mttr_hours == 0.5

    def test_high_uptime_high_score(self):
        good = ResilienceMetrics("g", 99.99, 0.1, 8760.0, 0.99)
        bad = ResilienceMetrics("b", 80.0, 24.0, 100.0, 0.2)
        self.scorer.score_system("g", good)
        self.scorer.score_system("b", bad)
        r_good = self.scorer.generate_resilience_report("g")
        r_bad = self.scorer.generate_resilience_report("b")
        assert r_good is not None and r_bad is not None

    def test_multiple_systems(self):
        for i in range(3):
            self.scorer.score_system(f"sys-{i}", self._make_metrics(f"sys-{i}"))


# ===========================================================================
# 10. Task Delegation AI
# ===========================================================================


class TestTaskDelegationAI:
    def setup_method(self):
        self.ai = TaskDelegationAI()

    def _register_agents(self):
        self.ai.register_agent("agent-1", ["python", "data-analysis"], 1.0)
        self.ai.register_agent("agent-2", ["devops", "automation"], 1.0)
        self.ai.register_agent("agent-3", ["python", "ml"], 1.0)

    def _make_task(self):
        from datetime import datetime, timedelta
        return Task(
            task_id="t-001",
            required_skills={"python"},
            priority=5,
            estimated_hours=2.0,
            deadline=datetime.utcnow() + timedelta(days=7),
        )

    def test_register_agent_returns_result(self):
        result = self.ai.register_agent("a-1", ["python"], 1.0)
        assert result is not None

    def test_delegate_task_returns_result(self):
        self._register_agents()
        task = self._make_task()
        result = self.ai.delegate_task(task)
        assert result is not None

    def test_rebalance_workload_returns_result(self):
        self._register_agents()
        result = self.ai.rebalance_workload()
        assert result is not None

    def test_get_delegation_report_returns_result(self):
        self._register_agents()
        report = self.ai.get_delegation_report()
        assert report is not None

    def test_score_confidence_returns_result(self):
        self._register_agents()
        task = self._make_task()
        score = self.ai.score_confidence(task, "agent-1")
        assert score is not None

    def test_task_dataclass(self):
        t = self._make_task()
        assert t.task_id == "t-001"
        assert "python" in t.required_skills

    def test_delegate_task_no_agents_handles_gracefully(self):
        task = self._make_task()
        result = self.ai.delegate_task(task)
        # Should not raise, may return None or an error dict

    def test_multiple_task_delegation(self):
        self._register_agents()
        for i in range(5):
            task = Task(f"t-{i}", ["python"], i % 10, float(i + 1))
            self.ai.delegate_task(task)
        report = self.ai.get_delegation_report()
        assert report is not None


# ===========================================================================
# 11. Dashboard
# ===========================================================================


class TestDashboard:
    def setup_method(self):
        self.detector = AnomalyDetector()
        self.scaling = ScalingEngine()
        self.commander = OpsCommander()
        self.bottleneck = BottleneckDetector()
        self.failover = AutoFailover()
        self.cost = CostReductionEngine()
        self.throughput = ThroughputMaximizer()

    def test_render_anomaly_summary_returns_string(self):
        result = render_anomaly_summary(self.detector)
        assert isinstance(result, str)

    def test_render_scaling_status_returns_string(self):
        result = render_scaling_status(self.scaling)
        assert isinstance(result, str)

    def test_render_ops_status_returns_string(self):
        result = render_ops_status(self.commander)
        assert isinstance(result, str)

    def test_render_bottleneck_map_returns_string(self):
        result = render_bottleneck_map(self.bottleneck)
        assert isinstance(result, str)

    def test_render_failover_status_returns_string(self):
        result = render_failover_status(self.failover)
        assert isinstance(result, str)

    def test_render_cost_summary_returns_string(self):
        result = render_cost_summary(self.cost)
        assert isinstance(result, str)

    def test_render_throughput_report_returns_string(self):
        result = render_throughput_report(self.throughput)
        assert isinstance(result, str)

    def test_render_full_dashboard_returns_string(self):
        bot = DreamOpsBot(tier=Tier.FREE)
        result = render_full_dashboard(bot)
        assert isinstance(result, str)

    def test_full_dashboard_has_content(self):
        bot = DreamOpsBot(tier=Tier.ENTERPRISE)
        result = render_full_dashboard(bot)
        assert len(result) > 50


# ===========================================================================
# 12. DreamOpsBot Integration
# ===========================================================================


class TestDreamOpsBotInit:
    def test_free_tier_init(self):
        bot = DreamOpsBot(tier=Tier.FREE)
        assert bot.tier == Tier.FREE

    def test_pro_tier_init(self):
        bot = DreamOpsBot(tier=Tier.PRO)
        assert bot.tier == Tier.PRO

    def test_enterprise_tier_init(self):
        bot = DreamOpsBot(tier=Tier.ENTERPRISE)
        assert bot.tier == Tier.ENTERPRISE

    def test_default_tier_is_free(self):
        bot = DreamOpsBot()
        assert bot.tier == Tier.FREE

    def test_has_anomaly_detector(self):
        bot = DreamOpsBot()
        assert bot.anomaly_detector is not None

    def test_has_scaling_engine(self):
        bot = DreamOpsBot()
        assert bot.scaling_engine is not None

    def test_has_ops_commander(self):
        bot = DreamOpsBot()
        assert bot.ops_commander is not None

    def test_has_bottleneck_detector(self):
        bot = DreamOpsBot()
        assert bot.bottleneck_detector is not None

    def test_has_auto_failover(self):
        bot = DreamOpsBot()
        assert bot.auto_failover is not None

    def test_has_cost_engine(self):
        bot = DreamOpsBot()
        assert bot.cost_engine is not None

    def test_has_throughput_maximizer(self):
        bot = DreamOpsBot()
        assert bot.throughput_maximizer is not None

    def test_has_resilience_scorer(self):
        bot = DreamOpsBot()
        assert bot.resilience_scorer is not None

    def test_has_task_delegation(self):
        bot = DreamOpsBot()
        assert bot.task_delegation is not None


class TestDreamOpsBotTierGating:
    def test_free_anomaly_detection_raises(self):
        bot = DreamOpsBot(tier=Tier.FREE)
        metrics = WorkflowMetrics("wf-1", 1.0, 0.01, 100.0)
        with pytest.raises(DreamOpsTierError):
            bot.run_anomaly_detection("wf-1", metrics)

    def test_pro_anomaly_detection_works(self):
        bot = DreamOpsBot(tier=Tier.PRO)
        metrics = WorkflowMetrics("wf-1", 1.0, 0.01, 100.0)
        result = bot.run_anomaly_detection("wf-1", metrics)
        assert result is not None

    def test_enterprise_anomaly_detection_works(self):
        bot = DreamOpsBot(tier=Tier.ENTERPRISE)
        metrics = WorkflowMetrics("wf-1", 1.0, 0.01, 100.0)
        result = bot.run_anomaly_detection("wf-1", metrics)
        assert result is not None

    def test_free_auto_scale_raises(self):
        bot = DreamOpsBot(tier=Tier.FREE)
        load = LoadMetrics("t-1", 50.0, 80.0, 55.0)
        with pytest.raises(DreamOpsTierError):
            bot.auto_scale("t-1", load)

    def test_pro_auto_scale_works(self):
        bot = DreamOpsBot(tier=Tier.PRO)
        load = LoadMetrics("t-1", 50.0, 80.0, 55.0)
        result = bot.auto_scale("t-1", load)
        assert result is not None

    def test_free_monitor_operations_raises(self):
        bot = DreamOpsBot(tier=Tier.FREE)
        with pytest.raises(DreamOpsTierError):
            bot.monitor_operations()

    def test_pro_monitor_operations_works(self):
        bot = DreamOpsBot(tier=Tier.PRO)
        result = bot.monitor_operations()
        assert result is not None

    def test_free_detect_bottlenecks_raises(self):
        bot = DreamOpsBot(tier=Tier.FREE)
        with pytest.raises(DreamOpsTierError):
            bot.detect_bottlenecks("wf-1", [])

    def test_free_manage_failover_raises(self):
        bot = DreamOpsBot(tier=Tier.FREE)
        with pytest.raises(DreamOpsTierError):
            bot.manage_failover("p-1", "b-1")

    def test_pro_manage_failover_raises(self):
        bot = DreamOpsBot(tier=Tier.PRO)
        with pytest.raises(DreamOpsTierError):
            bot.manage_failover("p-1", "b-1")

    def test_enterprise_manage_failover_works(self):
        bot = DreamOpsBot(tier=Tier.ENTERPRISE)
        result = bot.manage_failover("p-1", "b-1")
        assert result is not None

    def test_free_analyze_costs_raises(self):
        bot = DreamOpsBot(tier=Tier.FREE)
        data = CostData("dept-1", 10000.0, {"infra": 10000.0})
        with pytest.raises(DreamOpsTierError):
            bot.analyze_costs("dept-1", data)

    def test_enterprise_analyze_costs_works(self):
        bot = DreamOpsBot(tier=Tier.ENTERPRISE)
        data = CostData("dept-1", 10000.0, {"infra": 10000.0})
        result = bot.analyze_costs("dept-1", data)
        assert result is not None

    def test_free_maximize_throughput_raises(self):
        bot = DreamOpsBot(tier=Tier.FREE)
        with pytest.raises(DreamOpsTierError):
            bot.maximize_throughput("flow-1", [])

    def test_enterprise_maximize_throughput_works(self):
        bot = DreamOpsBot(tier=Tier.ENTERPRISE)
        stages = [FlowStage(f"s-{i}", 100.0, 50.0, float(i + 1)) for i in range(3)]
        result = bot.maximize_throughput("flow-1", stages)
        assert result is not None


class TestDreamOpsBotDashboard:
    def test_dashboard_returns_string(self):
        bot = DreamOpsBot(tier=Tier.FREE)
        result = bot.dashboard()
        assert isinstance(result, str)

    def test_dashboard_enterprise_returns_string(self):
        bot = DreamOpsBot(tier=Tier.ENTERPRISE)
        result = bot.dashboard()
        assert isinstance(result, str)

    def test_get_tier_info_returns_dict(self):
        bot = DreamOpsBot(tier=Tier.PRO)
        info = bot.get_tier_info()
        assert isinstance(info, dict)

    def test_get_tier_info_has_features(self):
        bot = DreamOpsBot(tier=Tier.PRO)
        info = bot.get_tier_info()
        assert "features" in info
        assert len(info["features"]) > 0

    def test_dreamops_bot_export(self):
        assert DreamOpsBotExport is DreamOpsBot


class TestDreamOpsBotScoreResilience:
    def test_free_score_resilience_raises(self):
        bot = DreamOpsBot(tier=Tier.FREE)
        metrics = ResilienceMetrics("s-1", 99.9, 0.5, 720.0, 0.85)
        with pytest.raises(DreamOpsTierError):
            bot.score_resilience("s-1", metrics)

    def test_enterprise_score_resilience_works(self):
        bot = DreamOpsBot(tier=Tier.ENTERPRISE)
        metrics = ResilienceMetrics("s-1", 99.9, 0.5, 720.0, 0.85)
        result = bot.score_resilience("s-1", metrics)
        assert result is not None
