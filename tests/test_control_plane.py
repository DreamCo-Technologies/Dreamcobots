"""
Tests for DreamCo Platform — Unified Command Center Control Plane
=================================================================

Covers:
1.  BotLifecycleState — new lifecycle states in bot registry
2.  BotRegistry       — lifecycle CRUD and find_by_lifecycle
3.  CorrelationChain  — creation, derivation, header injection/extraction
4.  HealthGateway     — snapshot content and CI status injection
5.  MetricsGateway    — bridging TelemetryCollector → snapshot
6.  LearningGateway   — stubbed and loop-attached snapshots
7.  WorkflowGateway   — orchestrator status aggregation
8.  RegistryGateway   — catalog and lifecycle breakdown
9.  RevenueGateway    — ARR/MRR and subscription tracking
10. DashboardAggregator — all section snapshots + master summary
"""

from __future__ import annotations

import os
import sys
import time

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dreamco_platform.registry.bot_registry import (
    BotLifecycleState,
    BotRegistry,
    BotRegistryEntry,
    HealthStatus,
)
from dreamco_platform.control_plane.correlation import CorrelationChain, HEADER_MAP
from dreamco_platform.control_plane.health_gateway import HealthGateway
from dreamco_platform.control_plane.metrics_gateway import MetricsGateway
from dreamco_platform.control_plane.learning_gateway import LearningGateway
from dreamco_platform.control_plane.workflow_gateway import WorkflowGateway
from dreamco_platform.control_plane.registry_gateway import RegistryGateway
from dreamco_platform.control_plane.revenue_gateway import RevenueGateway
from dreamco_platform.control_plane.aggregator import DashboardAggregator
from dreamco_platform.observability.telemetry import TelemetryCollector, TelemetryEvent
from dreamco_platform.observability.metrics import MetricsCollector


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_bot(bot_id: str, **kwargs) -> BotRegistryEntry:
    return BotRegistryEntry(
        bot_id=bot_id,
        display_name=bot_id.replace("_", " ").title(),
        **kwargs,
    )


# ---------------------------------------------------------------------------
# 1. BotLifecycleState
# ---------------------------------------------------------------------------

class TestBotLifecycleState:
    def test_all_states_present(self):
        values = {s.value for s in BotLifecycleState}
        expected = {
            "active", "beta", "deprecated", "maintenance",
            "training", "quarantined", "sandboxed",
            "rolling_back", "failed_validation",
        }
        assert values == expected

    def test_values_are_strings(self):
        for state in BotLifecycleState:
            assert isinstance(state.value, str)


# ---------------------------------------------------------------------------
# 2. BotRegistry — lifecycle integration
# ---------------------------------------------------------------------------

class TestBotRegistryLifecycle:
    def test_default_lifecycle_state_is_active(self):
        entry = _make_bot("test_bot")
        assert entry.lifecycle_state == BotLifecycleState.ACTIVE

    def test_set_lifecycle_state_in_constructor(self):
        entry = _make_bot("quarantine_bot", lifecycle_state=BotLifecycleState.QUARANTINED)
        assert entry.lifecycle_state == BotLifecycleState.QUARANTINED

    def test_update_lifecycle_state(self):
        reg = BotRegistry()
        reg.register(_make_bot("my_bot"))
        reg.update_lifecycle_state("my_bot", BotLifecycleState.TRAINING)
        assert reg.get("my_bot").lifecycle_state == BotLifecycleState.TRAINING

    def test_update_lifecycle_state_unknown_bot_raises(self):
        reg = BotRegistry()
        with pytest.raises(KeyError):
            reg.update_lifecycle_state("nonexistent", BotLifecycleState.SANDBOXED)

    def test_find_by_lifecycle(self):
        reg = BotRegistry()
        reg.register(_make_bot("active_bot", lifecycle_state=BotLifecycleState.ACTIVE))
        reg.register(_make_bot("training_bot", lifecycle_state=BotLifecycleState.TRAINING))
        reg.register(_make_bot("training_bot2", lifecycle_state=BotLifecycleState.TRAINING))

        training = reg.find_by_lifecycle(BotLifecycleState.TRAINING)
        assert len(training) == 2
        assert all(b.lifecycle_state == BotLifecycleState.TRAINING for b in training)

    def test_to_dict_includes_lifecycle_state(self):
        entry = _make_bot("my_bot", lifecycle_state=BotLifecycleState.SANDBOXED)
        d = entry.to_dict()
        assert d["lifecycle_state"] == "sandboxed"
        assert d["schema"] == "bot_registry_entry.v1"

    def test_from_dict_roundtrip_with_lifecycle(self):
        entry = _make_bot("roundtrip_bot", lifecycle_state=BotLifecycleState.FAILED_VALIDATION)
        restored = BotRegistryEntry.from_dict(entry.to_dict())
        assert restored.lifecycle_state == BotLifecycleState.FAILED_VALIDATION

    def test_from_dict_unknown_lifecycle_falls_back_to_active(self):
        data = _make_bot("fallback_bot").to_dict()
        data["lifecycle_state"] = "invented_state"
        restored = BotRegistryEntry.from_dict(data)
        assert restored.lifecycle_state == BotLifecycleState.ACTIVE

    def test_all_new_lifecycle_states_roundtrip(self):
        new_states = [
            BotLifecycleState.TRAINING,
            BotLifecycleState.QUARANTINED,
            BotLifecycleState.SANDBOXED,
            BotLifecycleState.ROLLING_BACK,
            BotLifecycleState.FAILED_VALIDATION,
        ]
        for state in new_states:
            entry = _make_bot(f"bot_{state.value}", lifecycle_state=state)
            restored = BotRegistryEntry.from_dict(entry.to_dict())
            assert restored.lifecycle_state == state


# ---------------------------------------------------------------------------
# 3. CorrelationChain
# ---------------------------------------------------------------------------

class TestCorrelationChain:
    def test_new_generates_unique_ids(self):
        c1 = CorrelationChain.new()
        c2 = CorrelationChain.new()
        assert c1.request_id != c2.request_id
        assert c1.trace_id != c2.trace_id
        assert c1.execution_id != c2.execution_id

    def test_new_with_optional_ids(self):
        chain = CorrelationChain.new(
            workflow_id="wf_123",
            decision_id="dec_456",
            session_id="ses_789",
        )
        assert chain.workflow_id == "wf_123"
        assert chain.decision_id == "dec_456"
        assert chain.session_id == "ses_789"

    def test_derive_preserves_trace_id(self):
        parent = CorrelationChain.new(workflow_id="wf_parent")
        child = parent.derive(workflow_id="wf_child")
        assert child.trace_id == parent.trace_id
        assert child.workflow_id == "wf_child"
        assert child.request_id != parent.request_id
        assert child.execution_id != parent.execution_id

    def test_derive_inherits_session(self):
        parent = CorrelationChain.new(session_id="ses_abc")
        child = parent.derive()
        assert child.session_id == "ses_abc"

    def test_to_headers_and_back(self):
        chain = CorrelationChain.new(
            workflow_id="wf_42",
            session_id="ses_42",
            decision_id="dec_42",
        )
        headers = chain.to_headers()
        restored = CorrelationChain.from_headers(headers)
        assert restored.trace_id == chain.trace_id
        assert restored.workflow_id == "wf_42"
        assert restored.session_id == "ses_42"
        assert restored.decision_id == "dec_42"

    def test_header_keys_match_map(self):
        chain = CorrelationChain.new(workflow_id="wf_x")
        headers = chain.to_headers()
        for field_name, header_name in HEADER_MAP.items():
            value = getattr(chain, field_name, "")
            if value:
                assert header_name in headers
                assert headers[header_name] == value

    def test_from_headers_fills_missing_mandatory_ids(self):
        chain = CorrelationChain.from_headers({})
        assert chain.request_id
        assert chain.trace_id
        assert chain.execution_id

    def test_to_dict_has_all_fields(self):
        chain = CorrelationChain.new(workflow_id="wf_dict")
        d = chain.to_dict()
        for key in ("request_id", "trace_id", "workflow_id", "decision_id",
                    "execution_id", "session_id"):
            assert key in d

    def test_repr_contains_ids(self):
        chain = CorrelationChain.new()
        r = repr(chain)
        assert "CorrelationChain" in r
        assert chain.request_id[:8] in r

    def test_chain_is_immutable(self):
        chain = CorrelationChain.new()
        with pytest.raises((AttributeError, TypeError)):
            chain.request_id = "hacked"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# 4. HealthGateway
# ---------------------------------------------------------------------------

class TestHealthGateway:
    def _registry_with_bots(self) -> BotRegistry:
        reg = BotRegistry()
        reg.register(_make_bot("bot_a", health=HealthStatus.HEALTHY))
        reg.register(_make_bot("bot_b", health=HealthStatus.DEGRADED))
        reg.register(_make_bot(
            "bot_c",
            health=HealthStatus.UNHEALTHY,
            lifecycle_state=BotLifecycleState.QUARANTINED,
        ))
        return reg

    def test_snapshot_keys_present(self):
        gw = HealthGateway()
        snap = gw.snapshot()
        for key in ("uptime_seconds", "heartbeat", "total_bots",
                    "health_breakdown", "lifecycle_breakdown",
                    "ci_pipelines", "unhealthy_bots", "quarantined_bots"):
            assert key in snap

    def test_health_breakdown_counts(self):
        reg = self._registry_with_bots()
        gw = HealthGateway(registry=reg)
        snap = gw.snapshot()
        assert snap["health_breakdown"]["healthy"] == 1
        assert snap["health_breakdown"]["degraded"] == 1
        assert snap["health_breakdown"]["unhealthy"] == 1
        assert snap["total_bots"] == 3

    def test_unhealthy_bots_listed(self):
        reg = self._registry_with_bots()
        gw = HealthGateway(registry=reg)
        assert "bot_c" in gw.snapshot()["unhealthy_bots"]

    def test_quarantined_bots_listed(self):
        reg = self._registry_with_bots()
        gw = HealthGateway(registry=reg)
        assert "bot_c" in gw.snapshot()["quarantined_bots"]

    def test_ci_status_recorded(self):
        gw = HealthGateway()
        gw.set_ci_status("main_ci", "passing", {"run_id": "42"})
        snap = gw.snapshot()
        assert len(snap["ci_pipelines"]) == 1
        assert snap["ci_pipelines"][0]["pipeline"] == "main_ci"
        assert snap["ci_pipelines"][0]["status"] == "passing"

    def test_uptime_increases(self):
        gw = HealthGateway()
        s1 = gw.snapshot()["uptime_seconds"]
        time.sleep(0.01)
        s2 = gw.snapshot()["uptime_seconds"]
        assert s2 >= s1


# ---------------------------------------------------------------------------
# 5. MetricsGateway
# ---------------------------------------------------------------------------

class TestMetricsGateway:
    def test_snapshot_keys(self):
        gw = MetricsGateway()
        snap = gw.snapshot()
        assert "telemetry" in snap
        assert "metrics" in snap
        assert "recent_errors" in snap
        assert "snapshot_at" in snap

    def test_records_telemetry_events(self):
        tel = TelemetryCollector()
        tel.record_latency("cap.test", "bot_a", 42.0)
        gw = MetricsGateway(telemetry=tel)
        snap = gw.snapshot()
        assert snap["telemetry"]["avg_latency_ms"] == 42.0

    def test_records_errors_in_recent_errors(self):
        tel = TelemetryCollector()
        tel.record_error("cap.test", "bot_b", "something broke")
        gw = MetricsGateway(telemetry=tel)
        snap = gw.snapshot()
        assert len(snap["recent_errors"]) == 1

    def test_metrics_counter_reflected(self):
        met = MetricsCollector()
        met.increment("invocations", labels={"bot": "test_bot"})
        met.increment("invocations", labels={"bot": "test_bot"})
        gw = MetricsGateway(metrics=met)
        snap = gw.snapshot()
        counters = snap["metrics"]["counters"]
        assert any(c["name"] == "invocations" and c["value"] == 2 for c in counters)

    def test_telemetry_and_metrics_accessors(self):
        tel = TelemetryCollector()
        met = MetricsCollector()
        gw = MetricsGateway(telemetry=tel, metrics=met)
        assert gw.telemetry is tel
        assert gw.metrics is met


# ---------------------------------------------------------------------------
# 6. LearningGateway
# ---------------------------------------------------------------------------

class TestLearningGateway:
    def test_snapshot_without_loop(self):
        gw = LearningGateway()
        snap = gw.snapshot()
        assert "recent_decisions" in snap
        assert "reward_stats" in snap
        assert "top_strategies" in snap
        assert "retraining_status" in snap
        assert snap["reward_stats"]["count"] == 0

    def test_set_retraining_status(self):
        gw = LearningGateway()
        gw.set_retraining_status("model_v2", "training", {"epoch": 5})
        snap = gw.snapshot()
        assert len(snap["retraining_status"]) == 1
        assert snap["retraining_status"][0]["model_id"] == "model_v2"
        assert snap["retraining_status"][0]["status"] == "training"

    def test_multiple_retraining_statuses(self):
        gw = LearningGateway()
        gw.set_retraining_status("model_a", "idle")
        gw.set_retraining_status("model_b", "training")
        snap = gw.snapshot()
        assert len(snap["retraining_status"]) == 2

    def test_attach_loop_called(self):
        """attach_loop should store the loop without crashing."""
        gw = LearningGateway()
        gw.attach_loop(object())  # arbitrary object; no real loop methods called
        assert gw._loop is not None

    def test_snapshot_with_stub_loop(self):
        """A loop that raises on every method should not crash the gateway."""
        class BrokenLoop:
            def get_recent_decisions(self, limit=20):
                raise RuntimeError("db error")

            def get_top_strategies(self, limit=10):
                raise RuntimeError("db error")

        gw = LearningGateway()
        gw.attach_loop(BrokenLoop())
        snap = gw.snapshot()  # should not raise
        assert snap["reward_stats"]["count"] == 0

    def test_snapshot_with_working_stub_loop(self):
        from dataclasses import dataclass
        from typing import Optional

        @dataclass
        class FakeDecision:
            decision_id: str
            bot_name: str
            action_type: str
            prediction: float
            reward: Optional[float]
            timestamp: str

        @dataclass
        class FakeStrategy:
            strategy_id: str
            bot_name: str
            action_type: str
            avg_reward: float
            success_count: int

        class FakeLoop:
            def get_recent_decisions(self, limit=20):
                return [
                    FakeDecision("d1", "bot_a", "buy", 0.8, 10.0, "2024-01-01"),
                    FakeDecision("d2", "bot_b", "sell", 0.5, 5.0, "2024-01-02"),
                ]

            def get_top_strategies(self, limit=10):
                return [FakeStrategy("s1", "bot_a", "buy", 10.0, 5)]

        gw = LearningGateway()
        gw.attach_loop(FakeLoop())
        snap = gw.snapshot()
        assert snap["reward_stats"]["count"] == 2
        assert snap["reward_stats"]["mean"] == 7.5
        assert snap["reward_stats"]["total"] == 15.0
        assert len(snap["top_strategies"]) == 1
        assert len(snap["recent_decisions"]) == 2


# ---------------------------------------------------------------------------
# 7. WorkflowGateway
# ---------------------------------------------------------------------------

class TestWorkflowGateway:
    def test_snapshot_empty_registry(self):
        gw = WorkflowGateway()
        snap = gw.snapshot()
        assert snap["active_orchestrators"] == 0
        assert isinstance(snap["orchestrators"], list)
        assert snap["pipeline_health"] == []

    def test_pipeline_health_injection(self):
        gw = WorkflowGateway()
        gw.set_pipeline_health("ci_main", "passing", {"branch": "main"})
        snap = gw.snapshot()
        assert len(snap["pipeline_health"]) == 1
        assert snap["pipeline_health"][0]["status"] == "passing"

    def test_multiple_pipelines(self):
        gw = WorkflowGateway()
        gw.set_pipeline_health("ci_main", "passing")
        gw.set_pipeline_health("ci_staging", "failing")
        snap = gw.snapshot()
        assert len(snap["pipeline_health"]) == 2

    def test_snapshot_has_required_keys(self):
        gw = WorkflowGateway()
        snap = gw.snapshot()
        for key in ("active_orchestrators", "orchestrator_status_breakdown",
                    "orchestrators", "pipeline_health", "snapshot_at"):
            assert key in snap


# ---------------------------------------------------------------------------
# 8. RegistryGateway
# ---------------------------------------------------------------------------

class TestRegistryGateway:
    def _populated_registry(self) -> BotRegistry:
        reg = BotRegistry()
        reg.register(_make_bot("bot_free", pricing_tier="free", category="lead_gen"))
        reg.register(_make_bot("bot_pro", pricing_tier="pro", category="finance",
                               lifecycle_state=BotLifecycleState.BETA))
        reg.register(_make_bot("bot_ent", pricing_tier="enterprise", category="lead_gen",
                               lifecycle_state=BotLifecycleState.TRAINING))
        return reg

    def test_snapshot_keys(self):
        gw = RegistryGateway()
        snap = gw.snapshot()
        for key in ("total_bots", "tier_breakdown", "category_breakdown",
                    "lifecycle_breakdown", "catalog", "snapshot_at"):
            assert key in snap

    def test_tier_breakdown(self):
        reg = self._populated_registry()
        gw = RegistryGateway(registry=reg)
        snap = gw.snapshot()
        assert snap["tier_breakdown"]["free"] == 1
        assert snap["tier_breakdown"]["pro"] == 1
        assert snap["tier_breakdown"]["enterprise"] == 1

    def test_category_breakdown(self):
        reg = self._populated_registry()
        gw = RegistryGateway(registry=reg)
        snap = gw.snapshot()
        assert snap["category_breakdown"]["lead_gen"] == 2
        assert snap["category_breakdown"]["finance"] == 1

    def test_lifecycle_breakdown(self):
        reg = self._populated_registry()
        gw = RegistryGateway(registry=reg)
        snap = gw.snapshot()
        assert snap["lifecycle_breakdown"]["active"] == 1
        assert snap["lifecycle_breakdown"]["beta"] == 1
        assert snap["lifecycle_breakdown"]["training"] == 1

    def test_catalog_entries_have_required_fields(self):
        reg = self._populated_registry()
        gw = RegistryGateway(registry=reg)
        snap = gw.snapshot()
        for entry in snap["catalog"]:
            for field in ("bot_id", "display_name", "category", "pricing_tier",
                          "version", "health", "lifecycle_state", "learning_enabled"):
                assert field in entry

    def test_registry_property(self):
        reg = BotRegistry()
        gw = RegistryGateway(registry=reg)
        assert gw.registry is reg


# ---------------------------------------------------------------------------
# 9. RevenueGateway
# ---------------------------------------------------------------------------

class TestRevenueGateway:
    def test_initial_snapshot_zeroed(self):
        gw = RevenueGateway()
        snap = gw.snapshot()
        assert snap["arr"] == 0.0
        assert snap["total_customers"] == 0

    def test_set_arr_mrr(self):
        gw = RevenueGateway()
        gw.set_arr(120_000.0)
        gw.set_mrr(10_000.0)
        snap = gw.snapshot()
        assert snap["arr"] == 120_000.0
        assert snap["mrr"] == 10_000.0

    def test_record_subscription(self):
        gw = RevenueGateway()
        gw.record_subscription("cust_001", "pro", 99.0)
        gw.record_subscription("cust_002", "enterprise", 499.0)
        snap = gw.snapshot()
        assert snap["total_customers"] == 2
        assert snap["tier_distribution"]["pro"] == 1
        assert snap["tier_distribution"]["enterprise"] == 1

    def test_mrr_computed_from_subscriptions(self):
        gw = RevenueGateway()
        gw.record_subscription("c1", "pro", 99.0)
        gw.record_subscription("c2", "pro", 99.0)
        snap = gw.snapshot()
        assert snap["mrr"] == 198.0

    def test_datasets_sold(self):
        gw = RevenueGateway()
        gw.increment_datasets_sold(3)
        gw.increment_datasets_sold(2)
        snap = gw.snapshot()
        assert snap["datasets_sold"] == 5

    def test_tier_mrr_totals(self):
        gw = RevenueGateway()
        gw.record_subscription("c1", "pro", 99.0)
        gw.record_subscription("c2", "pro", 99.0)
        snap = gw.snapshot()
        assert snap["tier_mrr"]["pro"] == 198.0

    def test_snapshot_has_required_keys(self):
        gw = RevenueGateway()
        snap = gw.snapshot()
        for key in ("arr", "mrr", "total_customers", "tier_distribution",
                    "tier_mrr", "datasets_sold", "updated_at", "snapshot_at"):
            assert key in snap


# ---------------------------------------------------------------------------
# 10. DashboardAggregator
# ---------------------------------------------------------------------------

class TestDashboardAggregator:
    def _agg(self) -> DashboardAggregator:
        reg = BotRegistry()
        reg.register(_make_bot("agg_bot_a", health=HealthStatus.HEALTHY,
                               category="finance", pricing_tier="pro"))
        reg.register(_make_bot("agg_bot_b", health=HealthStatus.DEGRADED,
                               lifecycle_state=BotLifecycleState.QUARANTINED,
                               category="lead_gen", pricing_tier="free"))
        health_gw = HealthGateway(registry=reg)
        registry_gw = RegistryGateway(registry=reg)

        revenue_gw = RevenueGateway()
        revenue_gw.set_arr(60_000.0)
        revenue_gw.set_mrr(5_000.0)

        return DashboardAggregator(
            health_gateway=health_gw,
            registry_gateway=registry_gw,
            revenue_gateway=revenue_gw,
        )

    def test_summary_keys(self):
        agg = self._agg()
        s = agg.summary()
        for section in ("system_health", "learning_intelligence",
                        "revenue_operations", "bot_network",
                        "workflow_operations", "snapshot_at"):
            assert section in s

    def test_summary_system_health(self):
        agg = self._agg()
        s = agg.summary()
        assert s["system_health"]["total_bots"] == 2
        assert s["system_health"]["quarantined_bots"] == 1

    def test_summary_revenue(self):
        agg = self._agg()
        s = agg.summary()
        assert s["revenue_operations"]["arr"] == 60_000.0
        assert s["revenue_operations"]["mrr"] == 5_000.0

    def test_health_snapshot(self):
        agg = self._agg()
        snap = agg.health_snapshot()
        assert "health_breakdown" in snap

    def test_observability_snapshot(self):
        agg = DashboardAggregator()
        snap = agg.observability_snapshot()
        assert "telemetry" in snap
        assert "metrics" in snap

    def test_learning_snapshot(self):
        agg = DashboardAggregator()
        snap = agg.learning_snapshot()
        assert "reward_stats" in snap

    def test_workflows_snapshot(self):
        agg = DashboardAggregator()
        snap = agg.workflows_snapshot()
        assert "active_orchestrators" in snap

    def test_marketplace_snapshot(self):
        agg = self._agg()
        snap = agg.marketplace_snapshot()
        assert snap["total_bots"] == 2
        assert "catalog" in snap

    def test_revenue_snapshot(self):
        agg = self._agg()
        snap = agg.revenue_snapshot()
        assert snap["arr"] == 60_000.0

    def test_security_snapshot(self):
        agg = DashboardAggregator()
        snap = agg.security_snapshot()
        assert "recent_audit_entries" in snap
        assert "security_events" in snap
        assert "total_audit_entries" in snap

    def test_all_snapshots_have_snapshot_at(self):
        agg = DashboardAggregator()
        for method in (
            agg.health_snapshot,
            agg.observability_snapshot,
            agg.learning_snapshot,
            agg.workflows_snapshot,
            agg.marketplace_snapshot,
            agg.revenue_snapshot,
            agg.security_snapshot,
        ):
            snap = method()
            assert "snapshot_at" in snap, f"{method.__name__} missing snapshot_at"

    def test_gateways_accessible(self):
        agg = DashboardAggregator()
        assert agg.health is not None
        assert agg.metrics is not None
        assert agg.learning is not None
        assert agg.workflows is not None
        assert agg.registry is not None
        assert agg.revenue is not None
