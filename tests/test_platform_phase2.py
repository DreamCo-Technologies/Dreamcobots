"""
Tests for the DreamCo Platform Phase 2 foundation layer.

Covers all 8 platform modules:
1. platform.events.schema        — canonical event schema
2. platform.registry.bot_registry — unified metadata registry
3. platform.capabilities.models   — CapabilityNode + WorkflowGraph
4. platform.orchestration.base_orchestrator — BaseOrchestrator interface
5. platform.memory.dream_memory    — Dream Memory Layer
6. platform.observability.telemetry — structured telemetry
7. platform.governance.policy_engine — Policy-as-Code engine
8. platform.governance.rbac        — RBAC + workspace isolation
"""

from __future__ import annotations

import os
import sys
import time
from typing import Any, Dict

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ---------------------------------------------------------------------------
# 1. Canonical Event Schema
# ---------------------------------------------------------------------------

from dreamco_platform.events.schema import (
    DreamCoEvent,
    EventFamily,
    EventValidator,
    EVENT_FAMILIES,
    make_event,
)


class TestDreamCoEvent:
    def test_all_families_defined(self):
        expected = {
            "system", "workflow", "bot", "capability", "billing",
            "learning", "marketplace", "security", "governance", "deployment",
        }
        assert set(EVENT_FAMILIES) == expected

    def test_event_creation_defaults(self):
        evt = DreamCoEvent(event_type="bot.started", source="test_bot")
        assert evt.family == "bot"
        assert evt.subtype == "started"
        assert evt.event_id
        assert evt.timestamp > 0
        assert evt.correlation_id

    def test_event_to_dict_roundtrip(self):
        evt = DreamCoEvent(
            event_type="workflow.completed",
            source="buddy_orchestrator",
            payload={"result": "ok"},
        )
        d = evt.to_dict()
        assert d["family"] == "workflow"
        assert d["subtype"] == "completed"
        assert d["payload"] == {"result": "ok"}
        restored = DreamCoEvent.from_dict(d)
        assert restored.event_id == evt.event_id
        assert restored.event_type == evt.event_type

    def test_causation_chain(self):
        root = make_event(EventFamily.WORKFLOW, "started", "orchestrator")
        child = make_event(
            EventFamily.BOT, "started", "lead_gen_bot",
            causation_id=root.event_id,
            correlation_id=root.correlation_id,
        )
        assert child.causation_id == root.event_id
        assert child.correlation_id == root.correlation_id

    def test_make_event_helper(self):
        evt = make_event("capability", "invoked", "lead.enrich", {"input": "x"})
        assert evt.family == "capability"
        assert evt.subtype == "invoked"
        assert evt.source == "lead.enrich"
        assert evt.payload == {"input": "x"}

    def test_event_repr(self):
        evt = DreamCoEvent(event_type="system.heartbeat", source="platform")
        assert "system.heartbeat" in repr(evt)

    def test_event_family_enum_values(self):
        assert EventFamily.SYSTEM.value == "system"
        assert EventFamily.GOVERNANCE.value == "governance"


class TestEventValidator:
    def test_valid_event_passes(self):
        evt = make_event(EventFamily.BOT, "completed", "my_bot")
        assert EventValidator.validate(evt) is True

    def test_missing_dot_raises(self):
        evt = DreamCoEvent(event_type="botstarted", source="x")
        with pytest.raises(ValueError, match="format"):
            EventValidator.validate(evt)

    def test_unknown_family_raises(self):
        evt = DreamCoEvent(event_type="unknown.started", source="x")
        with pytest.raises(ValueError, match="Unknown event family"):
            EventValidator.validate(evt)

    def test_empty_source_raises(self):
        evt = DreamCoEvent(event_type="bot.started", source="")
        with pytest.raises(ValueError, match="source"):
            EventValidator.validate(evt)

    def test_valid_family(self):
        assert EventValidator.validate_family("learning") is True

    def test_invalid_family(self):
        with pytest.raises(ValueError):
            EventValidator.validate_family("nonexistent")

    def test_all_families_pass_validation(self):
        for family in EVENT_FAMILIES:
            evt = make_event(family, "test", "source")
            assert EventValidator.validate(evt) is True


# ---------------------------------------------------------------------------
# 2. Unified Metadata Registry
# ---------------------------------------------------------------------------

from dreamco_platform.registry.bot_registry import BotRegistry, BotRegistryEntry, HealthStatus


class TestBotRegistryEntry:
    def test_default_fields(self):
        entry = BotRegistryEntry(bot_id="test_bot", display_name="Test Bot")
        assert entry.pricing_tier == "free"
        assert entry.health == HealthStatus.UNKNOWN
        assert not entry.learning_enabled
        assert entry.capabilities == []
        assert entry.lifecycle_state == "draft"
        assert entry.swarm_role == "specialist"
        assert entry.memory_nodes == []
        assert entry.permissions == []

    def test_to_dict_roundtrip(self):
        entry = BotRegistryEntry(
            bot_id="lead_gen_bot",
            display_name="Lead Gen Bot",
            capabilities=["lead.scrape", "lead.enrich"],
            events_emitted=["bot.started"],
            pricing_tier="pro",
            learning_enabled=True,
            lifecycle_state="active",
            swarm_role="negotiator",
            memory_nodes=["identity.lead_gen_bot"],
            permissions=["observe:runtime"],
            revenue_attribution={"estimated_monthly_usd": 199.0},
            trust_score=0.84,
        )
        d = entry.to_dict()
        restored = BotRegistryEntry.from_dict(d)
        assert restored.bot_id == "lead_gen_bot"
        assert restored.capabilities == ["lead.scrape", "lead.enrich"]
        assert restored.learning_enabled is True
        assert restored.lifecycle_state == "active"
        assert restored.swarm_role == "negotiator"
        assert restored.memory_nodes == ["identity.lead_gen_bot"]
        assert restored.permissions == ["observe:runtime"]
        assert restored.revenue_attribution["estimated_monthly_usd"] == pytest.approx(199.0)
        assert restored.trust_score == pytest.approx(0.84)

    def test_health_status_enum(self):
        assert HealthStatus.HEALTHY.value == "healthy"
        assert HealthStatus.DEGRADED.value == "degraded"

    def test_invalid_bot_id_raises(self):
        with pytest.raises(ValueError, match="Invalid bot_id"):
            BotRegistryEntry(bot_id="BadName", display_name="x")

    def test_invalid_bot_id_with_spaces(self):
        with pytest.raises(ValueError):
            BotRegistryEntry(bot_id="bad id", display_name="x")

    def test_invalid_bot_id_leading_digit(self):
        with pytest.raises(ValueError):
            BotRegistryEntry(bot_id="1bot", display_name="x")

    def test_to_dict_contains_schema_version(self):
        entry = BotRegistryEntry(bot_id="my_bot", display_name="My Bot")
        d = entry.to_dict()
        assert d["schema"] == "bot_registry_entry.v1"

    def test_frozen_entry_is_immutable(self):
        entry = BotRegistryEntry(bot_id="my_bot", display_name="My Bot")
        with pytest.raises((AttributeError, TypeError)):
            entry.display_name = "Mutated"  # type: ignore[misc]


class TestBotRegistry:
    def _make_registry(self) -> BotRegistry:
        reg = BotRegistry()
        reg.register(BotRegistryEntry(
            bot_id="lead_gen_bot",
            display_name="Lead Gen",
            capabilities=["lead.scrape", "lead.enrich"],
            events_emitted=["bot.started", "bot.completed"],
            pricing_tier="pro",
            learning_enabled=True,
            category="sales",
        ))
        reg.register(BotRegistryEntry(
            bot_id="finance_bot",
            display_name="Finance Bot",
            capabilities=["finance.report"],
            events_emitted=["bot.started"],
            pricing_tier="enterprise",
            category="finance",
        ))
        return reg

    def test_register_and_get(self):
        reg = self._make_registry()
        entry = reg.get("lead_gen_bot")
        assert entry is not None
        assert entry.display_name == "Lead Gen"

    def test_contains(self):
        reg = self._make_registry()
        assert "lead_gen_bot" in reg
        assert "nonexistent" not in reg

    def test_len(self):
        reg = self._make_registry()
        assert len(reg) == 2

    def test_list_all_sorted(self):
        reg = self._make_registry()
        ids = [e.bot_id for e in reg.list_all()]
        assert ids == sorted(ids)

    def test_find_by_capability(self):
        reg = self._make_registry()
        results = reg.find_by_capability("lead.enrich")
        assert len(results) == 1
        assert results[0].bot_id == "lead_gen_bot"

    def test_find_by_event_emitted(self):
        reg = self._make_registry()
        results = reg.find_by_event_emitted("bot.started")
        assert len(results) == 2

    def test_find_by_tier(self):
        reg = self._make_registry()
        results = reg.find_by_tier("enterprise")
        assert len(results) == 1
        assert results[0].bot_id == "finance_bot"

    def test_find_learning_enabled(self):
        reg = self._make_registry()
        results = reg.find_learning_enabled()
        assert len(results) == 1
        assert results[0].bot_id == "lead_gen_bot"

    def test_update_health(self):
        reg = self._make_registry()
        reg.update_health("finance_bot", HealthStatus.HEALTHY)
        assert reg.get("finance_bot").health == HealthStatus.HEALTHY

    def test_remove(self):
        reg = self._make_registry()
        removed = reg.remove("finance_bot")
        assert removed is not None
        assert "finance_bot" not in reg

    def test_manifest_summary_includes_runtime_dimensions(self):
        reg = self._make_registry()
        reg.register(BotRegistryEntry(
            bot_id="swarm_bot",
            display_name="Swarm Bot",
            lifecycle_state="active",
            swarm_role="observer_modulator",
            memory_nodes=["identity.swarm_bot", "trust.swarm_bot"],
            permissions=["observe:runtime", "write:memory"],
            revenue_attribution={"estimated_monthly_usd": 50.0, "realized_usd": 25.0},
            trust_score=0.9,
        ))
        summary = reg.manifest_summary()
        assert summary["total_bots"] == 3
        assert summary["lifecycle_states"]["draft"] >= 2
        assert summary["lifecycle_states"]["active"] == 1
        assert "observer_modulator" in summary["swarm_roles"]
        assert "observe:runtime" in summary["permissions"]
        assert "identity.swarm_bot" in summary["memory_nodes"]
        assert summary["revenue"]["estimated_monthly_usd"] == pytest.approx(50.0)

    def test_to_dict(self):
        reg = self._make_registry()
        d = reg.to_dict()
        assert "lead_gen_bot" in d
        assert "finance_bot" in d

    def test_health_requires_key(self):
        reg = self._make_registry()
        with pytest.raises(KeyError):
            reg.update_health("nonexistent", HealthStatus.HEALTHY)

    def test_find_by_category(self):
        reg = self._make_registry()
        results = reg.find_by_category("finance")
        assert len(results) == 1

    def test_find_by_coordination_mode(self):
        reg = self._make_registry()
        reg.register(BotRegistryEntry(
            bot_id="swarm_bot",
            display_name="Swarm Bot",
            metadata={"coordination_mode": "decentralized", "marl_enabled": True},
        ))
        results = reg.find_by_coordination_mode("decentralized")
        assert [entry.bot_id for entry in results] == ["swarm_bot"]

    def test_find_swarm_enabled(self):
        reg = self._make_registry()
        reg.register(BotRegistryEntry(
            bot_id="stigmergy_bot",
            display_name="Stigmergy Bot",
            metadata={"stigmergic_channels": ["shared_board"]},
        ))
        results = reg.find_swarm_enabled()
        assert [entry.bot_id for entry in results] == ["stigmergy_bot"]

    def test_swarm_summary(self):
        reg = self._make_registry()
        reg.register(BotRegistryEntry(
            bot_id="marl_bot",
            display_name="MARL Bot",
            metadata={"coordination_mode": "hybrid", "marl_enabled": True},
        ))
        summary = reg.swarm_summary()
        assert summary["total_bots"] == 3
        assert summary["swarm_enabled"] == 1
        assert summary["marl_enabled"] == 1
        assert summary["coordination_modes"]["hybrid"] == 1


# ---------------------------------------------------------------------------
# 3. CapabilityNode + WorkflowGraph
# ---------------------------------------------------------------------------

from dreamco_platform.capabilities.models import (
    CapabilityNode,
    EdgeCondition,
    ExecutionEdge,
    ExecutionResult,
    GovernancePolicy,
    WorkflowGraph,
)


class TestCapabilityNode:
    def test_defaults(self):
        node = CapabilityNode(capability_id="lead.scrape")
        assert node.version == "1.0.0"
        assert node.retry_policy["max_attempts"] == 1
        assert node.observability_hooks["trace"] is True

    def test_to_dict(self):
        node = CapabilityNode(
            capability_id="lead.enrich",
            permissions=["lead:read"],
            cost_profile={"per_call_usd": 0.01},
        )
        d = node.to_dict()
        assert d["capability_id"] == "lead.enrich"
        assert d["cost_profile"] == {"per_call_usd": 0.01}

    def test_repr(self):
        node = CapabilityNode(capability_id="x.y")
        assert "x.y" in repr(node)


class TestExecutionEdge:
    def _make_results(self, success: bool) -> ExecutionResult:
        return ExecutionResult(capability_id="a", success=success)

    def test_always_traverses(self):
        edge = ExecutionEdge(from_id="a", to_id="b")
        assert edge.should_traverse(self._make_results(True)) is True
        assert edge.should_traverse(self._make_results(False)) is True

    def test_on_success_condition(self):
        edge = ExecutionEdge(from_id="a", to_id="b", condition=EdgeCondition.ON_SUCCESS)
        assert edge.should_traverse(self._make_results(True)) is True
        assert edge.should_traverse(self._make_results(False)) is False

    def test_on_failure_condition(self):
        edge = ExecutionEdge(from_id="a", to_id="b", condition=EdgeCondition.ON_FAILURE)
        assert edge.should_traverse(self._make_results(False)) is True
        assert edge.should_traverse(self._make_results(True)) is False

    def test_conditional_with_predicate(self):
        edge = ExecutionEdge(
            from_id="a", to_id="b",
            condition=EdgeCondition.CONDITIONAL,
            predicate=lambda r: r.output.get("score", 0) > 50,
        )
        assert edge.should_traverse(ExecutionResult("a", output={"score": 80})) is True
        assert edge.should_traverse(ExecutionResult("a", output={"score": 30})) is False

    def test_to_dict(self):
        edge = ExecutionEdge(from_id="a", to_id="b", label="main path")
        d = edge.to_dict()
        assert d["from_id"] == "a"
        assert d["label"] == "main path"


class TestWorkflowGraph:
    def _build_linear(self) -> WorkflowGraph:
        g = WorkflowGraph(graph_id="linear", description="A → B → C")
        for cid in ("A", "B", "C"):
            g.add_node(CapabilityNode(capability_id=cid))
        g.add_edge(ExecutionEdge("A", "B"))
        g.add_edge(ExecutionEdge("B", "C"))
        return g

    def test_add_node_chaining(self):
        g = WorkflowGraph()
        result = g.add_node(CapabilityNode("x"))
        assert result is g  # chaining

    def test_topological_sort_linear(self):
        g = self._build_linear()
        order = g.topological_sort()
        assert order.index("A") < order.index("B")
        assert order.index("B") < order.index("C")

    def test_topological_sort_cycle_raises(self):
        g = WorkflowGraph()
        g.add_node(CapabilityNode("X"))
        g.add_node(CapabilityNode("Y"))
        g.edges.append(ExecutionEdge("X", "Y"))
        g.edges.append(ExecutionEdge("Y", "X"))  # bypass add_edge validation
        with pytest.raises(ValueError, match="cycle"):
            g.topological_sort()

    def test_add_edge_validates_nodes(self):
        g = WorkflowGraph()
        g.add_node(CapabilityNode("A"))
        with pytest.raises(ValueError, match="not a registered node"):
            g.add_edge(ExecutionEdge("A", "Z"))

    def test_validate_empty_raises(self):
        g = WorkflowGraph()
        with pytest.raises(ValueError, match="at least one node"):
            g.validate()

    def test_validate_linear_passes(self):
        g = self._build_linear()
        assert g.validate() is True

    def test_execute_with_executors(self):
        g = WorkflowGraph()
        g.add_node(CapabilityNode(
            capability_id="step1",
            executor=lambda inp: {"x": inp.get("x", 0) + 1},
        ))
        g.add_node(CapabilityNode(
            capability_id="step2",
            executor=lambda inp: {"x": inp.get("x", 0) * 2},
        ))
        g.add_edge(ExecutionEdge("step1", "step2"))
        results = g.execute({"x": 5})
        assert results["step1"].success is True
        assert results["step2"].success is True
        # step1: x = 5+1 = 6; step2: x = 6*2 = 12
        assert results["step2"].output["x"] == 12

    def test_execute_no_executor_skips(self):
        g = WorkflowGraph()
        g.add_node(CapabilityNode(capability_id="declarative"))
        results = g.execute()
        assert results["declarative"].output.get("skipped") is True

    def test_execute_retry_on_failure(self):
        attempts = []

        def flaky(inp: dict) -> dict:
            attempts.append(1)
            if len(attempts) < 3:
                raise RuntimeError("flaky")
            return {"done": True}

        g = WorkflowGraph()
        g.add_node(CapabilityNode(
            capability_id="flaky_step",
            retry_policy={"max_attempts": 3, "backoff_seconds": 0, "strategy": "none"},
            executor=flaky,
        ))
        results = g.execute()
        assert results["flaky_step"].success is True
        assert results["flaky_step"].attempts == 3

    def test_execute_conditional_edge(self):
        g = WorkflowGraph()
        g.add_node(CapabilityNode("root", executor=lambda _: {"ok": True}))
        g.add_node(CapabilityNode("success_path", executor=lambda _: {"path": "success"}))
        g.add_node(CapabilityNode("failure_path", executor=lambda _: {"path": "failure"}))
        g.add_edge(ExecutionEdge("root", "success_path", condition=EdgeCondition.ON_SUCCESS))
        g.add_edge(ExecutionEdge("root", "failure_path", condition=EdgeCondition.ON_FAILURE))
        results = g.execute()
        assert "success_path" in results
        assert results["success_path"].output.get("path") == "success"

    def test_to_dict(self):
        g = self._build_linear()
        g.add_policy(GovernancePolicy("p1", condition="cost > 100", action="approve"))
        d = g.to_dict()
        assert len(d["nodes"]) == 3
        assert len(d["edges"]) == 2
        assert len(d["policies"]) == 1

    def test_repr(self):
        g = self._build_linear()
        assert "WorkflowGraph" in repr(g)
        assert "nodes=3" in repr(g)

    def test_get_outgoing_edges(self):
        g = self._build_linear()
        edges = g.get_outgoing_edges("A")
        assert len(edges) == 1
        assert edges[0].to_id == "B"


# ---------------------------------------------------------------------------
# 4. Base Orchestrator
# ---------------------------------------------------------------------------

from dreamco_platform.orchestration.base_orchestrator import (
    BaseOrchestrator,
    ExecutionContext,
    OrchestratorRegistry,
    OrchestratorStatus,
)


class _EchoOrchestrator(BaseOrchestrator):
    """Minimal concrete orchestrator for testing."""

    def execute(self, context: ExecutionContext) -> ExecutionContext:
        context.mark_started()
        context.mark_completed({"echo": context.inputs})
        return context

    def status(self):
        return {
            "orchestrator_id": self.orchestrator_id,
            "name": self.name,
            "status": self._status.value,
            "uptime_s": self.uptime_seconds(),
        }

    def shutdown(self):
        self._status = OrchestratorStatus.SHUTDOWN


class TestExecutionContext:
    def test_initial_state(self):
        ctx = ExecutionContext(workflow_id="wf1")
        assert ctx.status == "pending"
        assert ctx.attempts == 0

    def test_mark_started(self):
        ctx = ExecutionContext()
        ctx.mark_started()
        assert ctx.status == "running"
        assert ctx.attempts == 1

    def test_mark_completed(self):
        ctx = ExecutionContext()
        ctx.mark_started()
        ctx.mark_completed({"result": "ok"})
        assert ctx.status == "completed"
        assert ctx.outputs == {"result": "ok"}
        assert ctx.completed_at is not None

    def test_mark_failed_with_retries_remaining(self):
        ctx = ExecutionContext(max_attempts=3)
        ctx.mark_started()
        ctx.mark_failed("boom")
        assert ctx.status == "retrying"
        assert ctx.can_retry() is True

    def test_mark_failed_exhausted(self):
        ctx = ExecutionContext(max_attempts=1)
        ctx.mark_started()
        ctx.mark_failed("boom")
        assert ctx.status == "failed"
        assert ctx.can_retry() is False

    def test_checkpoint(self):
        ctx = ExecutionContext()
        ctx.save_checkpoint({"step": 2, "data": [1, 2, 3]})
        assert ctx.checkpoint["step"] == 2

    def test_to_dict(self):
        ctx = ExecutionContext(workflow_id="w1")
        d = ctx.to_dict()
        assert d["workflow_id"] == "w1"
        assert "execution_id" in d


class TestBaseOrchestrator:
    def test_execute_and_status(self):
        orch = _EchoOrchestrator(name="Echo")
        ctx = orch.create_context("my_workflow", inputs={"x": 42})
        result = orch.execute(ctx)
        assert result.status == "completed"
        assert result.outputs["echo"]["x"] == 42

    def test_shutdown(self):
        orch = _EchoOrchestrator()
        orch.shutdown()
        assert orch._status == OrchestratorStatus.SHUTDOWN

    def test_list_contexts(self):
        orch = _EchoOrchestrator()
        ctx = orch.create_context("wf1")
        orch.execute(ctx)
        completed = orch.list_contexts(status_filter="completed")
        assert len(completed) == 1

    def test_uptime(self):
        orch = _EchoOrchestrator()
        assert orch.uptime_seconds() >= 0

    def test_status_dict(self):
        orch = _EchoOrchestrator(name="TestOrch")
        s = orch.status()
        assert s["name"] == "TestOrch"
        assert "uptime_s" in s

    def test_repr(self):
        orch = _EchoOrchestrator(name="MyOrch")
        assert "MyOrch" in repr(orch)


class TestOrchestratorRegistry:
    def test_register_and_get(self):
        reg = OrchestratorRegistry()
        orch = _EchoOrchestrator(name="A")
        reg.register(orch)
        assert reg.get(orch.orchestrator_id) is orch

    def test_contains(self):
        reg = OrchestratorRegistry()
        orch = _EchoOrchestrator()
        reg.register(orch)
        assert orch.orchestrator_id in reg

    def test_len(self):
        reg = OrchestratorRegistry()
        reg.register(_EchoOrchestrator())
        reg.register(_EchoOrchestrator())
        assert len(reg) == 2

    def test_unregister(self):
        reg = OrchestratorRegistry()
        orch = _EchoOrchestrator()
        reg.register(orch)
        reg.unregister(orch.orchestrator_id)
        assert orch.orchestrator_id not in reg

    def test_status_summary(self):
        reg = OrchestratorRegistry()
        reg.register(_EchoOrchestrator(name="A"))
        summaries = reg.status_summary()
        assert len(summaries) == 1
        assert "name" in summaries[0]

    def test_list_all_sorted(self):
        reg = OrchestratorRegistry()
        reg.register(_EchoOrchestrator(name="Zeta"))
        reg.register(_EchoOrchestrator(name="Alpha"))
        names = [o.name for o in reg.list_all()]
        assert names == sorted(names)


# ---------------------------------------------------------------------------
# 5. Dream Memory Layer
# ---------------------------------------------------------------------------

from dreamco_platform.memory.dream_memory import DreamMemory, MemoryEntry, MemoryType


class TestMemoryEntry:
    def test_defaults(self):
        entry = MemoryEntry(
            memory_type=MemoryType.DECISION,
            source="bot_a",
            subject="workflow_1",
        )
        assert entry.importance == 0.5
        assert entry.memory_id
        assert entry.timestamp > 0

    def test_to_dict(self):
        entry = MemoryEntry(
            memory_type=MemoryType.OUTCOME,
            source="bot_a",
            subject="workflow_1",
            data={"success": True},
            profitability_usd=100.0,
        )
        d = entry.to_dict()
        assert d["memory_type"] == "outcome"
        assert d["profitability_usd"] == 100.0

    def test_repr(self):
        entry = MemoryEntry(memory_type=MemoryType.RETRY, source="x", subject="y")
        assert "retry" in repr(entry)


class TestDreamMemory:
    def _make_memory(self) -> DreamMemory:
        mem = DreamMemory()
        mem.record_decision("bot_a", "wf_1", "go_left", importance=0.8)
        mem.record_outcome("bot_a", "wf_1", success=True, profitability_usd=50.0)
        mem.record_retry("bot_b", "wf_2", attempt=2, reason="timeout")
        mem.record(MemoryEntry(
            memory_type=MemoryType.LEARNING_SIGNAL,
            source="learning_system",
            subject="bot_a",
            importance=0.9,
        ))
        return mem

    def test_len(self):
        mem = self._make_memory()
        assert len(mem) == 4

    def test_get_by_id(self):
        mem = self._make_memory()
        entries = mem.query(memory_type=MemoryType.DECISION)
        entry = mem.get(entries[0].memory_id)
        assert entry is not None
        assert entry.memory_type == MemoryType.DECISION

    def test_query_by_source(self):
        mem = self._make_memory()
        results = mem.query(source="bot_a")
        assert all(e.source == "bot_a" for e in results)

    def test_query_by_type(self):
        mem = self._make_memory()
        results = mem.query(memory_type=MemoryType.RETRY)
        assert len(results) == 1
        assert results[0].data["attempt"] == 2

    def test_query_by_subject(self):
        mem = self._make_memory()
        results = mem.query(subject="wf_1")
        assert all(e.subject == "wf_1" for e in results)

    def test_query_by_bot(self):
        mem = self._make_memory()
        results = mem.query_by_bot("bot_a")
        # source == "bot_a" entries + subject == "bot_a" entries
        assert len(results) >= 2

    def test_query_since(self):
        mem = DreamMemory()
        early = MemoryEntry(memory_type=MemoryType.TELEMETRY, source="s", subject="x")
        early.timestamp = time.time() - 1000
        mem.record(early)
        recent = MemoryEntry(memory_type=MemoryType.TELEMETRY, source="s", subject="y")
        mem.record(recent)
        results = mem.query(since=time.time() - 100)
        assert all(e.memory_id == recent.memory_id for e in results)

    def test_query_newest_first(self):
        mem = self._make_memory()
        results = mem.query()
        for i in range(len(results) - 1):
            assert results[i].timestamp >= results[i + 1].timestamp

    def test_summarize(self):
        mem = self._make_memory()
        summary = mem.summarize()
        assert summary["total_entries"] == 4
        assert summary["total_profitability_usd"] == 50.0
        assert "decision" in summary["by_type"]

    def test_summarize_empty(self):
        mem = DreamMemory()
        summary = mem.summarize()
        assert summary["total_entries"] == 0

    def test_clear(self):
        mem = self._make_memory()
        mem.clear()
        assert len(mem) == 0

    def test_pruning_on_max_entries(self):
        mem = DreamMemory(max_entries=3)
        for i in range(5):
            mem.record(MemoryEntry(
                memory_type=MemoryType.TELEMETRY,
                source="s",
                subject=f"x{i}",
                importance=float(i) / 5,
            ))
        assert len(mem) == 3

    def test_repr(self):
        mem = self._make_memory()
        assert "DreamMemory" in repr(mem)


# ---------------------------------------------------------------------------
# 6. Telemetry and Observability
# ---------------------------------------------------------------------------

from dreamco_platform.observability.telemetry import (
    TelemetryCollector,
    TelemetryEvent,
    TelemetryLevel,
)


class TestTelemetryEvent:
    def test_defaults(self):
        evt = TelemetryEvent(
            capability_id="lead.enrich",
            source="bot_a",
            metric_name="latency_ms",
            metric_value=42.5,
        )
        assert evt.level == TelemetryLevel.INFO
        assert evt.telemetry_id
        assert evt.timestamp > 0

    def test_to_dict(self):
        evt = TelemetryEvent(
            capability_id="x",
            source="y",
            metric_name="cost_usd",
            metric_value=0.05,
            unit="usd",
        )
        d = evt.to_dict()
        assert d["metric_name"] == "cost_usd"
        assert d["unit"] == "usd"

    def test_repr(self):
        evt = TelemetryEvent(capability_id="a", source="b", metric_name="lat", metric_value=10)
        assert "lat" in repr(evt)


class TestTelemetryCollector:
    def _make_collector(self) -> TelemetryCollector:
        col = TelemetryCollector()
        col.record_latency("cap.a", "bot_a", 100.0, success=True)
        col.record_latency("cap.a", "bot_a", 200.0, success=True)
        col.record_latency("cap.a", "bot_a", 300.0, success=False)
        col.record_cost("cap.a", "bot_a", 0.03)
        col.record_error("cap.b", "bot_b", "connection refused")
        return col

    def test_len(self):
        col = self._make_collector()
        assert len(col) == 5

    def test_get_events_by_capability(self):
        col = self._make_collector()
        results = col.get_events(capability_id="cap.a")
        assert all(e.capability_id == "cap.a" for e in results)
        assert len(results) == 4

    def test_get_events_by_level(self):
        col = self._make_collector()
        errors = col.get_events(level=TelemetryLevel.ERROR)
        assert len(errors) == 1
        assert errors[0].capability_id == "cap.b"

    def test_get_events_newest_first(self):
        col = self._make_collector()
        events = col.get_events()
        for i in range(len(events) - 1):
            assert events[i].timestamp >= events[i + 1].timestamp

    def test_summarize(self):
        col = self._make_collector()
        s = col.summarize(capability_id="cap.a")
        assert s["total_events"] == 4
        assert s["avg_latency_ms"] == 200.0
        assert s["total_cost_usd"] == 0.03
        assert s["error_rate"] > 0

    def test_summarize_empty(self):
        col = TelemetryCollector()
        s = col.summarize()
        assert s["total_events"] == 0

    def test_p95_latency(self):
        col = TelemetryCollector()
        for ms in range(1, 101):
            col.record_latency("cap", "src", float(ms))
        s = col.summarize(capability_id="cap")
        assert s["p95_latency_ms"] >= 95.0

    def test_export(self):
        col = self._make_collector()
        exported = col.export()
        assert len(exported) == 5
        assert all(isinstance(e, dict) for e in exported)

    def test_fifo_eviction(self):
        col = TelemetryCollector(max_events=3)
        for i in range(5):
            col.record_latency("cap", "src", float(i))
        assert len(col) == 3

    def test_clear(self):
        col = self._make_collector()
        col.clear()
        assert len(col) == 0

    def test_repr(self):
        col = self._make_collector()
        assert "TelemetryCollector" in repr(col)


# ---------------------------------------------------------------------------
# 7. Policy-as-Code Engine
# ---------------------------------------------------------------------------

from dreamco_platform.governance.policy_engine import (
    PolicyAction,
    PolicyCondition,
    PolicyEngine,
    PolicyResult,
    PolicyRule,
    cost_exceeds,
    custom,
    field_equals,
    field_gte,
    field_lte,
    workflow_type_is,
)


class TestPolicyCondition:
    def test_cost_exceeds(self):
        cond = cost_exceeds(1000)
        assert cond.evaluate({"action_cost": 1500}) is True
        assert cond.evaluate({"action_cost": 500}) is False

    def test_workflow_type_is(self):
        cond = workflow_type_is("financial")
        assert cond.evaluate({"workflow_type": "financial"}) is True
        assert cond.evaluate({"workflow_type": "marketing"}) is False

    def test_field_equals(self):
        cond = field_equals("env", "prod")
        assert cond.evaluate({"env": "prod"}) is True
        assert cond.evaluate({"env": "dev"}) is False

    def test_field_gte(self):
        cond = field_gte("risk_score", 0.8)
        assert cond.evaluate({"risk_score": 0.9}) is True
        assert cond.evaluate({"risk_score": 0.5}) is False

    def test_field_lte(self):
        cond = field_lte("budget", 100)
        assert cond.evaluate({"budget": 50}) is True
        assert cond.evaluate({"budget": 150}) is False

    def test_and_composition(self):
        cond = cost_exceeds(100) & workflow_type_is("financial")
        assert cond.evaluate({"action_cost": 200, "workflow_type": "financial"}) is True
        assert cond.evaluate({"action_cost": 50, "workflow_type": "financial"}) is False

    def test_or_composition(self):
        cond = cost_exceeds(1000) | workflow_type_is("financial")
        assert cond.evaluate({"action_cost": 200, "workflow_type": "financial"}) is True
        assert cond.evaluate({"action_cost": 1500}) is True
        assert cond.evaluate({"action_cost": 50, "workflow_type": "marketing"}) is False

    def test_not_composition(self):
        cond = ~workflow_type_is("financial")
        assert cond.evaluate({"workflow_type": "marketing"}) is True
        assert cond.evaluate({"workflow_type": "financial"}) is False

    def test_custom_condition(self):
        cond = custom(lambda ctx: ctx.get("x", 0) > 10, "x > 10")
        assert cond.evaluate({"x": 20}) is True
        assert cond.evaluate({"x": 5}) is False


class TestPolicyEngine:
    def _make_engine(self) -> PolicyEngine:
        engine = PolicyEngine()
        engine.add_rule(PolicyRule(
            rule_id="cost_gate",
            name="High-cost gate",
            condition=cost_exceeds(1000),
            action=PolicyAction.REQUIRE_HUMAN_APPROVAL,
            severity="high",
        ))
        engine.add_rule(PolicyRule(
            rule_id="financial_audit",
            name="Financial audit",
            condition=workflow_type_is("financial"),
            action=PolicyAction.ENFORCE_AUDIT_LOGGING,
            severity="medium",
        ))
        engine.add_rule(PolicyRule(
            rule_id="block_rule",
            name="Block high risk",
            condition=field_gte("risk_score", 0.95),
            action=PolicyAction.BLOCK_EXECUTION,
            severity="critical",
        ))
        return engine

    def test_len(self):
        engine = self._make_engine()
        assert len(engine) == 3

    def test_evaluate_triggered(self):
        engine = self._make_engine()
        result = engine.evaluate("cost_gate", {"action_cost": 2000})
        assert result.triggered is True
        assert result.action == PolicyAction.REQUIRE_HUMAN_APPROVAL

    def test_evaluate_not_triggered(self):
        engine = self._make_engine()
        result = engine.evaluate("cost_gate", {"action_cost": 500})
        assert result.triggered is False
        assert result.action is None

    def test_evaluate_all(self):
        engine = self._make_engine()
        ctx = {"action_cost": 2000, "workflow_type": "financial", "risk_score": 0.5}
        results = engine.evaluate_all(ctx)
        triggered = [r for r in results if r.triggered]
        assert len(triggered) == 2

    def test_requires_approval(self):
        engine = self._make_engine()
        assert engine.requires_approval({"action_cost": 5000}) is True
        assert engine.requires_approval({"action_cost": 10}) is False

    def test_has_blocking_violation(self):
        engine = self._make_engine()
        assert engine.has_blocking_violation({"risk_score": 0.99}) is True
        assert engine.has_blocking_violation({"risk_score": 0.5}) is False

    def test_disabled_rule_not_evaluated(self):
        engine = self._make_engine()
        engine.get_rule("cost_gate").enabled = False
        results = engine.evaluate_all({"action_cost": 9999})
        triggered = [r for r in results if r.rule_id == "cost_gate" and r.triggered]
        assert len(triggered) == 0

    def test_audit_log(self):
        engine = self._make_engine()
        engine.evaluate("cost_gate", {"action_cost": 2000})
        log = engine.audit_log()
        assert len(log) == 1

    def test_audit_log_triggered_only(self):
        engine = self._make_engine()
        engine.evaluate("cost_gate", {"action_cost": 2000})
        engine.evaluate("cost_gate", {"action_cost": 10})
        triggered = engine.audit_log(triggered_only=True)
        assert all(r.triggered for r in triggered)

    def test_remove_rule(self):
        engine = self._make_engine()
        removed = engine.remove_rule("cost_gate")
        assert removed is not None
        assert engine.get_rule("cost_gate") is None

    def test_unknown_rule_raises(self):
        engine = PolicyEngine()
        with pytest.raises(KeyError):
            engine.evaluate("nonexistent", {})

    def test_policy_result_to_dict(self):
        engine = self._make_engine()
        result = engine.evaluate("cost_gate", {"action_cost": 5000})
        d = result.to_dict()
        assert d["rule_id"] == "cost_gate"
        assert d["triggered"] is True

    def test_rule_to_dict(self):
        rule = PolicyRule(
            rule_id="r1",
            name="Test",
            condition=cost_exceeds(100),
            action=PolicyAction.LOG_ONLY,
        )
        d = rule.to_dict()
        assert d["action"] == "log_only"


# ---------------------------------------------------------------------------
# 8. RBAC + Workspace Isolation
# ---------------------------------------------------------------------------

from dreamco_platform.governance.rbac import (
    Permission,
    RBACRegistry,
    Role,
    Workspace,
)


class TestRole:
    def test_built_in_roles(self):
        assert Role.read_only().role_id == "read_only"
        assert Role.developer().role_id == "developer"
        assert Role.operator().role_id == "operator"
        assert Role.admin().role_id == "admin"

    def test_admin_has_all_permissions(self):
        admin = Role.admin()
        for perm in Permission:
            assert admin.has_permission(perm) is True

    def test_read_only_no_write(self):
        ro = Role.read_only()
        assert ro.has_permission(Permission.BOT_DEPLOY) is False
        assert ro.has_permission(Permission.BOT_READ) is True

    def test_superadmin_grants_all(self):
        role = Role(role_id="x", name="X", permissions={Permission.SUPERADMIN})
        assert role.has_permission(Permission.BILLING_ADMIN) is True

    def test_to_dict(self):
        role = Role.developer()
        d = role.to_dict()
        assert d["role_id"] == "developer"
        assert isinstance(d["permissions"], list)


class TestWorkspace:
    def test_add_and_remove_member(self):
        ws = Workspace(name="Alpha", owner_id="user_1")
        ws.add_member("user_2", "developer")
        assert ws.get_member_role("user_2") == "developer"
        ws.remove_member("user_2")
        assert ws.get_member_role("user_2") is None

    def test_to_dict(self):
        ws = Workspace(name="Beta", owner_id="u1")
        ws.add_member("u2", "read_only")
        d = ws.to_dict()
        assert d["name"] == "Beta"
        assert "u2" in d["members"]

    def test_repr(self):
        ws = Workspace(name="TestWS", owner_id="u1")
        assert "TestWS" in repr(ws)


class TestRBACRegistry:
    def _make_registry(self) -> RBACRegistry:
        reg = RBACRegistry()
        ws = reg.create_workspace("Acme Corp", "admin_user")
        ws.add_member("dev_user", "developer")
        ws.add_member("read_user", "read_only")
        return reg

    def test_seeded_roles(self):
        reg = RBACRegistry()
        assert reg.get_role("read_only") is not None
        assert reg.get_role("developer") is not None
        assert reg.get_role("operator") is not None
        assert reg.get_role("admin") is not None

    def test_create_workspace_auto_adds_owner(self):
        reg = RBACRegistry()
        ws = reg.create_workspace("My WS", "alice")
        assert ws.get_member_role("alice") == "admin"

    def test_user_has_permission_true(self):
        reg = self._make_registry()
        ws = reg.list_workspaces()[0]
        assert reg.user_has_permission("dev_user", ws.workspace_id, Permission.BOT_RUN)

    def test_user_has_permission_false(self):
        reg = self._make_registry()
        ws = reg.list_workspaces()[0]
        assert not reg.user_has_permission("read_user", ws.workspace_id, Permission.BOT_DEPLOY)

    def test_non_member_has_no_permissions(self):
        reg = self._make_registry()
        ws = reg.list_workspaces()[0]
        assert not reg.user_has_permission("stranger", ws.workspace_id, Permission.BOT_READ)

    def test_effective_permissions_inheritance(self):
        reg = RBACRegistry()
        effective = reg.effective_permissions("developer")
        # Developer inherits from read_only
        assert Permission.BOT_READ in effective
        assert Permission.BOT_RUN in effective

    def test_effective_permissions_operator(self):
        reg = RBACRegistry()
        effective = reg.effective_permissions("operator")
        # Operator > developer > read_only
        assert Permission.BOT_DEPLOY in effective
        assert Permission.BOT_READ in effective

    def test_admin_effective_permissions(self):
        reg = RBACRegistry()
        effective = reg.effective_permissions("admin")
        assert Permission.SUPERADMIN in effective

    def test_get_user_permissions(self):
        reg = self._make_registry()
        ws = reg.list_workspaces()[0]
        perms = reg.get_user_permissions("dev_user", ws.workspace_id)
        assert Permission.BOT_RUN in perms

    def test_workspace_isolation(self):
        reg = RBACRegistry()
        ws_a = reg.create_workspace("WS A", "alice")
        ws_b = reg.create_workspace("WS B", "bob")
        ws_a.add_member("charlie", "developer")
        # charlie has no role in ws_b
        assert not reg.user_has_permission("charlie", ws_b.workspace_id, Permission.BOT_READ)

    def test_add_custom_role(self):
        reg = RBACRegistry()
        custom_role = Role(
            role_id="analyst",
            name="Analyst",
            permissions={Permission.ANALYTICS_READ, Permission.BILLING_READ},
        )
        reg.add_role(custom_role)
        assert reg.get_role("analyst") is not None

    def test_delete_workspace(self):
        reg = self._make_registry()
        ws = reg.list_workspaces()[0]
        removed = reg.delete_workspace(ws.workspace_id)
        assert removed is not None
        assert reg.get_workspace(ws.workspace_id) is None

    def test_repr(self):
        reg = RBACRegistry()
        assert "RBACRegistry" in repr(reg)


# ---------------------------------------------------------------------------
# Integration: Event → Registry → Capability → Memory → Telemetry → Policy
# ---------------------------------------------------------------------------

class TestPlatformIntegration:
    """
    End-to-end integration test: simulate a full capability execution cycle
    across the platform layer.
    """

    def test_full_capability_execution_cycle(self):
        # 1. Register a bot
        registry = BotRegistry()
        registry.register(BotRegistryEntry(
            bot_id="integration_bot",
            display_name="Integration Bot",
            capabilities=["integration.run"],
            events_emitted=["capability.invoked", "capability.completed"],
            pricing_tier="pro",
            learning_enabled=True,
        ))
        assert "integration_bot" in registry

        # 2. Create and execute a workflow graph
        graph = WorkflowGraph(graph_id="integration_wf")
        graph.add_node(CapabilityNode(
            capability_id="integration.run",
            cost_profile={"per_call_usd": 0.05},
            executor=lambda inp: {"processed": True, "count": inp.get("count", 0) + 1},
        ))
        results = graph.execute({"count": 10})
        assert results["integration.run"].success is True
        assert results["integration.run"].output["count"] == 11

        # 3. Emit canonical events
        correlation_id = str(__import__("uuid").uuid4())
        event = make_event(
            EventFamily.CAPABILITY, "completed", "integration_bot",
            payload={"workflow_id": "integration_wf", "success": True},
            correlation_id=correlation_id,
        )
        assert EventValidator.validate(event) is True

        # 4. Record to Dream Memory
        memory = DreamMemory()
        memory.record_outcome(
            source="integration_bot",
            subject="integration_wf",
            success=True,
            profitability_usd=0.05,
            correlation_id=correlation_id,
        )
        assert len(memory) == 1

        # 5. Record telemetry
        telemetry = TelemetryCollector()
        telemetry.record_latency(
            "integration.run", "integration_bot",
            results["integration.run"].latency_ms,
            success=True,
            correlation_id=correlation_id,
        )
        telemetry.record_cost(
            "integration.run", "integration_bot",
            results["integration.run"].cost_usd,
            correlation_id=correlation_id,
        )
        assert len(telemetry) == 2

        # 6. Policy check
        engine = PolicyEngine()
        engine.add_rule(PolicyRule(
            rule_id="cost_gate",
            name="Cost gate",
            condition=cost_exceeds(1000),
            action=PolicyAction.REQUIRE_HUMAN_APPROVAL,
        ))
        # Cost 0.05 should not trigger
        assert not engine.requires_approval({"action_cost": 0.05})

        # 7. RBAC check
        rbac = RBACRegistry()
        ws = rbac.create_workspace("Test WS", "admin")
        ws.add_member("operator_user", "operator")
        assert rbac.user_has_permission("operator_user", ws.workspace_id, Permission.BOT_RUN)

        summary = memory.summarize()
        assert summary["total_profitability_usd"] == 0.05
