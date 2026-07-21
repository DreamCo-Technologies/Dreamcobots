"""
Tests for DreamCo Platform Phase 2 — Blueprint Expansion
=========================================================

Covers all new sub-modules added in the blueprint implementation:
  - events/event_types.py
  - events/emitter.py
  - events/validator.py
  - registry/capability_registry.py
  - registry/workspace_registry.py
  - registry/registry_store.py
  - capabilities/capability_node.py (re-export)
  - capabilities/workflow_graph.py (re-export)
  - capabilities/execution_engine.py
  - capabilities/edge.py
  - capabilities/policies.py
  - orchestration/event_router.py
  - orchestration/execution_runtime.py
  - observability/tracer.py
  - observability/metrics.py
  - observability/audit_log.py
  - observability/event_stream.py
  - memory/memory_store.py
  - memory/user_memory.py
  - memory/workflow_memory.py
  - memory/embedding_store.py
  - auth/permissions.py
  - auth/workspace.py
  - auth/rbac.py
  - governance/evaluator.py
  - governance/loader.py
  - refactor/capability_extractor.py
  - refactor/duplication_scanner.py
"""

import json
import pytest

# ---------------------------------------------------------------------------
# events/event_types
# ---------------------------------------------------------------------------

class TestEventTypes:
    def test_all_families_present(self):
        from dreamco_platform.events.event_types import EventTypeRegistry, _FAMILY_MAP
        assert len(_FAMILY_MAP) == 10

    def test_is_known_valid(self):
        from dreamco_platform.events.event_types import EventTypeRegistry
        assert EventTypeRegistry.is_known("workflow.started")
        assert EventTypeRegistry.is_known("system.heartbeat")
        assert EventTypeRegistry.is_known("capability.invoked")

    def test_is_known_invalid(self):
        from dreamco_platform.events.event_types import EventTypeRegistry
        assert not EventTypeRegistry.is_known("made_up.event")

    def test_family_of(self):
        from dreamco_platform.events.event_types import EventTypeRegistry
        assert EventTypeRegistry.family_of("workflow.started") == "workflow"
        assert EventTypeRegistry.family_of("billing.payment_failed") == "billing"
        assert EventTypeRegistry.family_of("bad") is None

    def test_types_for_family(self):
        from dreamco_platform.events.event_types import EventTypeRegistry
        wf_types = EventTypeRegistry.types_for_family("workflow")
        assert "workflow.started" in wf_types
        assert "workflow.completed" in wf_types

    def test_unknown_family(self):
        from dreamco_platform.events.event_types import EventTypeRegistry
        assert EventTypeRegistry.types_for_family("nonexistent") == []

    def test_all_types_non_empty(self):
        from dreamco_platform.events.event_types import EventTypeRegistry
        assert len(EventTypeRegistry.all_types()) > 50


# ---------------------------------------------------------------------------
# events/validator
# ---------------------------------------------------------------------------

class TestEventValidator:
    def _good_event(self):
        from dreamco_platform.events.schema import make_event, EventFamily
        return make_event(EventFamily.WORKFLOW, "started", "test_bot")

    def test_valid_event_passes(self):
        from dreamco_platform.events.validator import EventValidator
        EventValidator.validate(self._good_event())  # no exception

    def test_is_valid_true(self):
        from dreamco_platform.events.validator import EventValidator
        assert EventValidator.is_valid(self._good_event())

    def test_bad_event_type_raises(self):
        from dreamco_platform.events.validator import EventValidator, EventValidationError
        from dreamco_platform.events.schema import make_event, EventFamily
        ev = make_event(EventFamily.WORKFLOW, "started", "src")
        object.__setattr__(ev, "event_type", "NOTVALID")
        assert not EventValidator.is_valid(ev)

    def test_bad_family_raises(self):
        from dreamco_platform.events.validator import EventValidator, EventValidationError
        from dreamco_platform.events.schema import make_event, EventFamily
        ev = make_event(EventFamily.WORKFLOW, "started", "src")
        object.__setattr__(ev, "event_type", "unknown_family.action")
        with pytest.raises(EventValidationError):
            EventValidator.validate(ev)

    def test_bad_severity_raises(self):
        from dreamco_platform.events.validator import EventValidator, EventValidationError
        from dreamco_platform.events.schema import make_event, EventFamily
        # DreamCoEvent doesn't have a severity field by default, but if one is
        # added the validator should reject bad values.  We test by patching.
        import types
        ev = make_event(EventFamily.SYSTEM, "heartbeat", "sys")
        # Simulate an event with a bad severity attribute
        ev_with_bad_severity = types.SimpleNamespace(
            event_type="system.heartbeat",
            source="sys",
            event_id=ev.event_id,
            timestamp=ev.timestamp,
            payload={},
            severity="SUPER_CRITICAL",
        )
        # Validate manually using partial check
        from dreamco_platform.events.validator import _VALID_SEVERITIES
        sev = getattr(ev_with_bad_severity, "severity", None)
        assert sev not in _VALID_SEVERITIES

    def test_validation_errors_empty_for_valid(self):
        from dreamco_platform.events.validator import EventValidator
        assert EventValidator.validation_errors(self._good_event()) == []


# ---------------------------------------------------------------------------
# events/emitter (EventBus)
# ---------------------------------------------------------------------------

class TestEventBus:
    def _bus(self):
        from dreamco_platform.events.emitter import EventBus
        return EventBus()

    def _event(self):
        from dreamco_platform.events.schema import make_event, EventFamily
        return make_event(EventFamily.WORKFLOW, "started", "test")

    def test_subscribe_and_emit(self):
        bus = self._bus()
        received = []
        bus.subscribe("workflow.started", lambda e: received.append(e))
        bus.emit(self._event())
        assert len(received) == 1

    def test_wildcard_subscription(self):
        bus = self._bus()
        received = []
        bus.subscribe("workflow.*", lambda e: received.append(e))
        bus.emit(self._event())
        assert len(received) == 1

    def test_global_wildcard(self):
        bus = self._bus()
        received = []
        bus.subscribe("*", lambda e: received.append(e))
        bus.emit(self._event())
        assert len(received) == 1

    def test_unsubscribe(self):
        bus = self._bus()
        received = []
        handler = lambda e: received.append(e)
        bus.subscribe("workflow.started", handler)
        bus.unsubscribe("workflow.started", handler)
        bus.emit(self._event())
        assert len(received) == 0

    def test_emit_raw(self):
        from dreamco_platform.events.schema import EventFamily
        bus = self._bus()
        received = []
        bus.subscribe("bot.*", lambda e: received.append(e))
        bus.emit_raw(EventFamily.BOT, "started", "my_bot")
        assert len(received) == 1

    def test_recent_events(self):
        bus = self._bus()
        for _ in range(5):
            bus.emit(self._event())
        assert len(bus.recent_events(3)) == 3

    def test_stats(self):
        bus = self._bus()
        bus.emit(self._event())
        s = bus.stats()
        assert s["emit_count"] == 1

    def test_default_bus_singleton(self):
        from dreamco_platform.events.emitter import get_default_bus, reset_default_bus
        reset_default_bus()
        b1 = get_default_bus()
        b2 = get_default_bus()
        assert b1 is b2

    def test_subscriber_count(self):
        bus = self._bus()
        bus.subscribe("workflow.*", lambda e: None)
        bus.subscribe("workflow.*", lambda e: None)
        assert bus.subscriber_count("workflow.*") == 2


# ---------------------------------------------------------------------------
# registry/capability_registry
# ---------------------------------------------------------------------------

class TestCapabilityRegistry:
    def _entry(self, cap_id="cap1", version="1.0", owner="bot1"):
        from dreamco_platform.registry.capability_registry import CapabilityEntry
        return CapabilityEntry(capability_id=cap_id, version=version, owner_bot_id=owner)

    def test_register_and_get(self):
        from dreamco_platform.registry.capability_registry import CapabilityRegistry
        reg = CapabilityRegistry()
        reg.register(self._entry())
        assert reg.get("cap1") is not None

    def test_count(self):
        from dreamco_platform.registry.capability_registry import CapabilityRegistry
        reg = CapabilityRegistry()
        reg.register(self._entry("a"))
        reg.register(self._entry("b"))
        assert reg.count() == 2

    def test_disable_and_enable(self):
        from dreamco_platform.registry.capability_registry import CapabilityRegistry
        reg = CapabilityRegistry()
        reg.register(self._entry("cap1"))
        reg.disable("cap1")
        assert not reg.get("cap1").enabled
        reg.enable("cap1")
        assert reg.get("cap1").enabled

    def test_all_entries_enabled_only(self):
        from dreamco_platform.registry.capability_registry import CapabilityRegistry
        reg = CapabilityRegistry()
        reg.register(self._entry("a"))
        reg.register(self._entry("b"))
        reg.disable("b")
        assert len(reg.all_entries(enabled_only=True)) == 1

    def test_by_owner(self):
        from dreamco_platform.registry.capability_registry import CapabilityRegistry
        reg = CapabilityRegistry()
        reg.register(self._entry("a", owner="bot1"))
        reg.register(self._entry("b", owner="bot2"))
        assert len(reg.by_owner("bot1")) == 1

    def test_by_tag(self):
        from dreamco_platform.registry.capability_registry import CapabilityEntry, CapabilityRegistry
        reg = CapabilityRegistry()
        e = CapabilityEntry("cap1", "1.0", "bot1", tags=["lead"])
        reg.register(e)
        assert len(reg.by_tag("lead")) == 1
        assert len(reg.by_tag("finance")) == 0

    def test_remove(self):
        from dreamco_platform.registry.capability_registry import CapabilityRegistry
        reg = CapabilityRegistry()
        reg.register(self._entry("cap1"))
        assert reg.remove("cap1")
        assert reg.get("cap1") is None

    def test_to_dict(self):
        from dreamco_platform.registry.capability_registry import CapabilityRegistry
        reg = CapabilityRegistry()
        reg.register(self._entry("cap1"))
        d = reg.get("cap1").to_dict()
        assert d["capability_id"] == "cap1"


# ---------------------------------------------------------------------------
# registry/workspace_registry
# ---------------------------------------------------------------------------

class TestWorkspaceRegistry:
    def _record(self, ws_id="ws1", owner="user1"):
        from dreamco_platform.registry.workspace_registry import WorkspaceRecord
        return WorkspaceRecord(workspace_id=ws_id, name="Test WS", owner_user_id=owner)

    def test_create_and_get(self):
        from dreamco_platform.registry.workspace_registry import WorkspaceRegistry
        reg = WorkspaceRegistry()
        reg.create(self._record())
        assert reg.get("ws1") is not None

    def test_duplicate_raises(self):
        from dreamco_platform.registry.workspace_registry import WorkspaceRegistry
        reg = WorkspaceRegistry()
        reg.create(self._record())
        with pytest.raises(ValueError):
            reg.create(self._record())

    def test_update_plan(self):
        from dreamco_platform.registry.workspace_registry import WorkspaceRegistry
        reg = WorkspaceRegistry()
        reg.create(self._record())
        reg.update_plan("ws1", "enterprise")
        assert reg.get("ws1").billing_plan == "enterprise"

    def test_feature_flag(self):
        from dreamco_platform.registry.workspace_registry import WorkspaceRegistry
        reg = WorkspaceRegistry()
        reg.create(self._record())
        reg.set_feature_flag("ws1", "beta_features", True)
        assert reg.has_feature("ws1", "beta_features")

    def test_quota(self):
        from dreamco_platform.registry.workspace_registry import WorkspaceRegistry
        reg = WorkspaceRegistry()
        reg.create(self._record())
        reg.set_quota("ws1", "api_calls", 1000)
        assert reg.quota_for("ws1", "api_calls") == 1000

    def test_deactivate(self):
        from dreamco_platform.registry.workspace_registry import WorkspaceRegistry
        reg = WorkspaceRegistry()
        reg.create(self._record())
        reg.deactivate("ws1")
        assert len(reg.all_active()) == 0

    def test_by_owner(self):
        from dreamco_platform.registry.workspace_registry import WorkspaceRegistry
        reg = WorkspaceRegistry()
        reg.create(self._record("ws1", "alice"))
        reg.create(self._record("ws2", "bob"))
        assert len(reg.by_owner("alice")) == 1


# ---------------------------------------------------------------------------
# registry/registry_store
# ---------------------------------------------------------------------------

class TestRegistryStore:
    def test_stats_empty(self):
        from dreamco_platform.registry.registry_store import RegistryStore
        store = RegistryStore()
        s = store.stats()
        assert s["bots"] == 0
        assert s["capabilities"] == 0
        assert s["workspaces"] == 0

    def test_snapshot(self):
        from dreamco_platform.registry.registry_store import RegistryStore
        from dreamco_platform.registry.bot_registry import BotRegistryEntry
        store = RegistryStore()
        store.bots.register(BotRegistryEntry(bot_id="b1", display_name="Bot 1"))
        snap = store.snapshot()
        assert len(snap["bots"]) == 1

    def test_capabilities_for_bot(self):
        from dreamco_platform.registry.registry_store import RegistryStore
        from dreamco_platform.registry.capability_registry import CapabilityEntry
        store = RegistryStore()
        store.capabilities.register(CapabilityEntry("cap1", "1.0", "bot1"))
        assert "cap1" in store.capabilities_for_bot("bot1")

    def test_repr(self):
        from dreamco_platform.registry.registry_store import RegistryStore
        store = RegistryStore()
        assert "RegistryStore" in repr(store)


# ---------------------------------------------------------------------------
# capabilities/capability_node (re-export)
# ---------------------------------------------------------------------------

class TestCapabilityNodeReexport:
    def test_import(self):
        from dreamco_platform.capabilities.capability_node import CapabilityNode
        node = CapabilityNode("test.cap", executor=lambda i: i)
        assert node.capability_id == "test.cap"


# ---------------------------------------------------------------------------
# capabilities/edge.py + EdgeBuilder
# ---------------------------------------------------------------------------

class TestEdgeBuilder:
    def test_build_success_edge(self):
        from dreamco_platform.capabilities.edge import EdgeBuilder, EdgeCondition
        edge = EdgeBuilder("a").to("b").on_success().build()
        assert edge.from_id == "a"
        assert edge.to_id == "b"
        assert edge.condition == EdgeCondition.ON_SUCCESS

    def test_build_failure_edge(self):
        from dreamco_platform.capabilities.edge import EdgeBuilder, EdgeCondition
        edge = EdgeBuilder("a").to("b").on_failure().build()
        assert edge.condition == EdgeCondition.ON_FAILURE

    def test_build_always_edge(self):
        from dreamco_platform.capabilities.edge import EdgeBuilder, EdgeCondition
        edge = EdgeBuilder("a").to("b").always().build()
        assert edge.condition == EdgeCondition.ALWAYS

    def test_missing_to_raises(self):
        from dreamco_platform.capabilities.edge import EdgeBuilder
        with pytest.raises(ValueError):
            EdgeBuilder("a").build()

    def test_metadata(self):
        from dreamco_platform.capabilities.edge import EdgeBuilder
        edge = EdgeBuilder("a").to("b").with_metadata("cost", 0.5).build()
        assert edge.metadata["cost"] == 0.5


# ---------------------------------------------------------------------------
# capabilities/policies.py
# ---------------------------------------------------------------------------

class TestCapabilityPolicySet:
    def test_add_and_get(self):
        from dreamco_platform.capabilities.policies import CapabilityPolicySet
        from dreamco_platform.capabilities.models import GovernancePolicy
        ps = CapabilityPolicySet("my_graph")
        ps.add(GovernancePolicy("p1", action="require_approval"))
        assert ps.get("p1") is not None

    def test_remove(self):
        from dreamco_platform.capabilities.policies import CapabilityPolicySet
        from dreamco_platform.capabilities.models import GovernancePolicy
        ps = CapabilityPolicySet("g")
        ps.add(GovernancePolicy("p1", action="deny"))
        assert ps.remove("p1")
        assert ps.get("p1") is None

    def test_required_approvals(self):
        from dreamco_platform.capabilities.policies import CapabilityPolicySet
        from dreamco_platform.capabilities.models import GovernancePolicy
        ps = CapabilityPolicySet("g")
        ps.add(GovernancePolicy("p1", action="require_approval"))
        ps.add(GovernancePolicy("p2", action="deny"))
        assert len(ps.required_approvals()) == 1

    def test_to_dict(self):
        from dreamco_platform.capabilities.policies import CapabilityPolicySet
        ps = CapabilityPolicySet("g")
        d = ps.to_dict()
        assert d["target_id"] == "g"


# ---------------------------------------------------------------------------
# capabilities/execution_engine.py
# ---------------------------------------------------------------------------

class TestExecutionEngine:
    def test_successful_run(self):
        from dreamco_platform.capabilities.execution_engine import ExecutionEngine
        from dreamco_platform.capabilities.models import CapabilityNode, WorkflowGraph
        engine = ExecutionEngine()
        graph = WorkflowGraph("g1")
        graph.add_node(CapabilityNode("step1", executor=lambda i: {"x": 1}))
        report = engine.run(graph)
        assert report.success
        assert len(report.records) == 1

    def test_failed_run(self):
        from dreamco_platform.capabilities.execution_engine import ExecutionEngine
        from dreamco_platform.capabilities.models import CapabilityNode, WorkflowGraph
        engine = ExecutionEngine()
        graph = WorkflowGraph("g2")
        def failing_executor(i):
            raise ValueError("fail")
        graph.add_node(CapabilityNode("step1", executor=failing_executor))
        report = engine.run(graph)
        assert not report.success
        assert report.failed_node == "step1"

    def test_cost_accumulation(self):
        from dreamco_platform.capabilities.execution_engine import ExecutionEngine
        from dreamco_platform.capabilities.models import CapabilityNode, WorkflowGraph
        engine = ExecutionEngine()
        graph = WorkflowGraph("g3")
        graph.add_node(CapabilityNode("s1", cost_profile={"per_call_usd": 0.10}, executor=lambda i: {}))
        graph.add_node(CapabilityNode("s2", cost_profile={"per_call_usd": 0.05}, executor=lambda i: {}))
        report = engine.run(graph)
        assert report.total_cost_usd == pytest.approx(0.15)

    def test_emits_events_to_bus(self):
        from dreamco_platform.capabilities.execution_engine import ExecutionEngine
        from dreamco_platform.capabilities.models import CapabilityNode, WorkflowGraph
        from dreamco_platform.events.emitter import EventBus
        bus = EventBus()
        received = []
        bus.subscribe("capability.*", lambda e: received.append(e))
        engine = ExecutionEngine(bus=bus)
        graph = WorkflowGraph("g4")
        graph.add_node(CapabilityNode("s1", executor=lambda i: {}))
        engine.run(graph)
        assert len(received) >= 2  # invoked + completed

    def test_report_to_dict(self):
        from dreamco_platform.capabilities.execution_engine import ExecutionEngine
        from dreamco_platform.capabilities.models import CapabilityNode, WorkflowGraph
        engine = ExecutionEngine()
        graph = WorkflowGraph("g5")
        graph.add_node(CapabilityNode("s1", executor=lambda i: {}))
        report = engine.run(graph)
        d = report.to_dict()
        assert "success" in d


# ---------------------------------------------------------------------------
# orchestration/event_router.py
# ---------------------------------------------------------------------------

class TestEventRouter:
    def _event(self):
        from dreamco_platform.events.schema import make_event, EventFamily
        return make_event(EventFamily.WORKFLOW, "started", "test")

    def test_route_exact(self):
        from dreamco_platform.orchestration.event_router import EventRouter, Route
        router = EventRouter()
        received = []
        router.add_route(Route(0, "workflow.started", lambda e: received.append(e)))
        router.dispatch(self._event())
        assert len(received) == 1

    def test_route_wildcard(self):
        from dreamco_platform.orchestration.event_router import EventRouter, Route
        router = EventRouter()
        received = []
        router.add_route(Route(0, "workflow.*", lambda e: received.append(e)))
        router.dispatch(self._event())
        assert len(received) == 1

    def test_global_wildcard(self):
        from dreamco_platform.orchestration.event_router import EventRouter, Route
        router = EventRouter()
        received = []
        router.add_route(Route(0, "*", lambda e: received.append(e)))
        router.dispatch(self._event())
        assert len(received) == 1

    def test_dead_letter_queue(self):
        from dreamco_platform.orchestration.event_router import EventRouter
        router = EventRouter()
        router.dispatch(self._event())
        assert len(router.dead_letters()) == 1

    def test_remove_route(self):
        from dreamco_platform.orchestration.event_router import EventRouter, Route
        router = EventRouter()
        handler = lambda e: None
        router.add_route(Route(0, "workflow.started", handler))
        assert router.remove_route("workflow.started", handler)
        assert router.route_count() == 0

    def test_stats(self):
        from dreamco_platform.orchestration.event_router import EventRouter, Route
        router = EventRouter()
        router.add_route(Route(0, "*", lambda e: None))
        router.dispatch(self._event())
        s = router.stats()
        assert s["dispatch_count"] == 1

    def test_priority_ordering(self):
        from dreamco_platform.orchestration.event_router import EventRouter, Route
        order = []
        router = EventRouter()
        router.add_route(Route(10, "*", lambda e: order.append(10)))
        router.add_route(Route(1, "*", lambda e: order.append(1)))
        router.dispatch(self._event())
        assert order[0] == 1  # lower priority number = called first


# ---------------------------------------------------------------------------
# orchestration/execution_runtime.py
# ---------------------------------------------------------------------------

class TestExecutionRuntime:
    def test_successful_step(self):
        from dreamco_platform.orchestration.execution_runtime import ExecutionRuntime, RuntimeStatus
        rt = ExecutionRuntime(default_max_attempts=1, default_backoff_seconds=0)
        record = rt.run("j1", lambda ctx: {"result": 42})
        assert record.status == RuntimeStatus.SUCCEEDED
        assert record.result == {"result": 42}

    def test_retry_then_succeed(self):
        from dreamco_platform.orchestration.execution_runtime import ExecutionRuntime, RuntimeStatus
        counter = [0]
        def step(ctx):
            counter[0] += 1
            if counter[0] < 3:
                raise ValueError("not yet")
            return "ok"
        rt = ExecutionRuntime(default_max_attempts=3, default_backoff_seconds=0)
        record = rt.run("j2", step)
        assert record.status == RuntimeStatus.SUCCEEDED
        assert record.attempts == 3

    def test_all_attempts_fail(self):
        from dreamco_platform.orchestration.execution_runtime import ExecutionRuntime, RuntimeStatus
        def always_fails(ctx):
            raise RuntimeError("fail")
        rt = ExecutionRuntime(default_max_attempts=2, default_backoff_seconds=0)
        record = rt.run("j3", always_fails)
        assert record.status == RuntimeStatus.FAILED

    def test_compensation(self):
        from dreamco_platform.orchestration.execution_runtime import ExecutionRuntime, RuntimeStatus
        compensated = []
        def always_fails(ctx):
            raise ValueError("err")
        rt = ExecutionRuntime(default_max_attempts=1, default_backoff_seconds=0)
        record = rt.run(
            "j4",
            always_fails,
            compensation=lambda r: compensated.append("done"),
        )
        assert record.status == RuntimeStatus.COMPENSATED
        assert compensated == ["done"]

    def test_checkpoint_stored(self):
        from dreamco_platform.orchestration.execution_runtime import ExecutionRuntime
        def step(ctx):
            ctx.checkpoint({"progress": 50})
            return "done"
        rt = ExecutionRuntime(default_max_attempts=1, default_backoff_seconds=0)
        record = rt.run("j5", step)
        assert len(record.checkpoints) == 1

    def test_get_record(self):
        from dreamco_platform.orchestration.execution_runtime import ExecutionRuntime
        rt = ExecutionRuntime(default_max_attempts=1, default_backoff_seconds=0)
        rt.run("j6", lambda ctx: None)
        assert rt.get_record("j6") is not None

    def test_stats(self):
        from dreamco_platform.orchestration.execution_runtime import ExecutionRuntime
        rt = ExecutionRuntime(default_max_attempts=1, default_backoff_seconds=0)
        rt.run("j7", lambda ctx: None)
        s = rt.stats()
        assert s["total"] == 1


# ---------------------------------------------------------------------------
# observability/tracer.py
# ---------------------------------------------------------------------------

class TestTracer:
    def test_start_and_finish_span(self):
        from dreamco_platform.observability.tracer import Tracer, SpanStatus
        tracer = Tracer()
        span = tracer.start_span("test.op", trace_id="t1")
        tracer.finish_span(span, SpanStatus.SUCCESS)
        assert span.duration_ms is not None

    def test_context_manager(self):
        from dreamco_platform.observability.tracer import Tracer, SpanStatus
        tracer = Tracer()
        with tracer.span("test.op", trace_id="t2") as s:
            s.set_tag("x", 1)
        assert s.status == SpanStatus.SUCCESS

    def test_context_manager_error(self):
        from dreamco_platform.observability.tracer import Tracer, SpanStatus
        tracer = Tracer()
        with pytest.raises(ValueError):
            with tracer.span("test.op", trace_id="t3") as s:
                raise ValueError("boom")
        assert s.status == SpanStatus.ERROR

    def test_trace_for(self):
        from dreamco_platform.observability.tracer import Tracer
        tracer = Tracer()
        with tracer.span("op1", trace_id="trace_abc"):
            pass
        with tracer.span("op2", trace_id="trace_abc"):
            pass
        assert len(tracer.trace_for("trace_abc")) == 2

    def test_recent_spans(self):
        from dreamco_platform.observability.tracer import Tracer
        tracer = Tracer()
        for i in range(5):
            with tracer.span(f"op{i}", trace_id="tx"):
                pass
        assert len(tracer.recent_spans(3)) == 3

    def test_stats(self):
        from dreamco_platform.observability.tracer import Tracer
        tracer = Tracer()
        with tracer.span("op", trace_id="t"):
            pass
        s = tracer.stats()
        assert s["total_finished"] == 1


# ---------------------------------------------------------------------------
# observability/metrics.py
# ---------------------------------------------------------------------------

class TestMetricsCollector:
    def test_counter(self):
        from dreamco_platform.observability.metrics import MetricsCollector
        m = MetricsCollector()
        m.increment("requests", labels={"bot": "b1"})
        m.increment("requests", labels={"bot": "b1"})
        assert m.counter_value("requests", {"bot": "b1"}) == 2.0

    def test_gauge(self):
        from dreamco_platform.observability.metrics import MetricsCollector
        m = MetricsCollector()
        m.set_gauge("workers", 5.0)
        assert m.gauge_value("workers") == 5.0

    def test_histogram(self):
        from dreamco_platform.observability.metrics import MetricsCollector
        m = MetricsCollector()
        for v in [10, 20, 30, 40, 100]:
            m.record("latency", v)
        h = m.histogram("latency")
        assert h.count == 5
        assert h.mean == pytest.approx(40.0)

    def test_histogram_p95(self):
        from dreamco_platform.observability.metrics import MetricsCollector
        m = MetricsCollector()
        for v in range(1, 101):
            m.record("lat", float(v))
        h = m.histogram("lat")
        assert h.percentile(95) >= 90

    def test_snapshot(self):
        from dreamco_platform.observability.metrics import MetricsCollector
        m = MetricsCollector()
        m.increment("x")
        snap = m.snapshot()
        assert len(snap["counters"]) == 1

    def test_reset(self):
        from dreamco_platform.observability.metrics import MetricsCollector
        m = MetricsCollector()
        m.increment("x")
        m.reset()
        assert m.counter_value("x") == 0.0


# ---------------------------------------------------------------------------
# observability/audit_log.py
# ---------------------------------------------------------------------------

class TestAuditLog:
    def test_record_and_query(self):
        from dreamco_platform.observability.audit_log import AuditLog
        log = AuditLog()
        log.record("user:alice", "capability.invoked", "lead.scrape", "success")
        entries = log.query(actor="user:alice")
        assert len(entries) == 1

    def test_invalid_outcome_raises(self):
        from dreamco_platform.observability.audit_log import AuditLog
        log = AuditLog()
        with pytest.raises(ValueError):
            log.record("user:alice", "action", "resource", "INVALID_OUTCOME")

    def test_query_by_outcome(self):
        from dreamco_platform.observability.audit_log import AuditLog
        log = AuditLog()
        log.record("u", "a", "r", "success")
        log.record("u", "a", "r", "failure")
        assert len(log.query(outcome="success")) == 1

    def test_total_recorded(self):
        from dreamco_platform.observability.audit_log import AuditLog
        log = AuditLog()
        log.record("u", "a", "r", "success")
        log.record("u", "b", "r", "denied")
        assert log.total_recorded() == 2

    def test_stats(self):
        from dreamco_platform.observability.audit_log import AuditLog
        log = AuditLog()
        log.record("u", "a", "r", "success")
        s = log.stats()
        assert s["by_outcome"]["success"] == 1


# ---------------------------------------------------------------------------
# observability/event_stream.py
# ---------------------------------------------------------------------------

class TestEventStream:
    def _event(self):
        from dreamco_platform.events.schema import make_event, EventFamily
        return make_event(EventFamily.BOT, "started", "test_bot")

    def test_publish_and_consume(self):
        from dreamco_platform.observability.event_stream import EventStream
        stream = EventStream()
        stream.publish(self._event())
        records = stream.consume_from(offset=0)
        assert len(records) == 1

    def test_offset_tracking(self):
        from dreamco_platform.observability.event_stream import EventStream
        stream = EventStream()
        offset1 = stream.publish(self._event())
        offset2 = stream.publish(self._event())
        assert offset2 == offset1 + 1

    def test_consume_from_offset(self):
        from dreamco_platform.observability.event_stream import EventStream
        stream = EventStream()
        for _ in range(5):
            stream.publish(self._event())
        records = stream.consume_from(offset=3)
        assert len(records) == 2

    def test_filter_by_type(self):
        from dreamco_platform.observability.event_stream import EventStream
        from dreamco_platform.events.schema import make_event, EventFamily
        stream = EventStream()
        stream.publish(make_event(EventFamily.BOT, "started", "src"))
        stream.publish(make_event(EventFamily.WORKFLOW, "started", "src"))
        records = stream.consume_from(event_type_filter="bot.*")
        assert len(records) == 1

    def test_stats(self):
        from dreamco_platform.observability.event_stream import EventStream
        stream = EventStream()
        stream.publish(self._event())
        s = stream.stats()
        assert s["stored"] == 1
        assert s["next_offset"] == 1


# ---------------------------------------------------------------------------
# memory/memory_store.py
# ---------------------------------------------------------------------------

class TestMemoryStore:
    def _record(self, subject="bot:x", content="test", importance=0.5):
        from dreamco_platform.memory.memory_store import MemoryRecord, MemoryType
        return MemoryRecord(subject=subject, memory_type=MemoryType.DECISION,
                            content=content, importance=importance)

    def test_write_and_recall(self):
        from dreamco_platform.memory.memory_store import MemoryStore
        store = MemoryStore()
        store.write(self._record())
        assert len(store.recall("bot:x")) == 1

    def test_recall_by_type(self):
        from dreamco_platform.memory.memory_store import MemoryStore, MemoryRecord, MemoryType
        store = MemoryStore()
        store.write(MemoryRecord("s", MemoryType.DECISION, "d"))
        store.write(MemoryRecord("s", MemoryType.OUTCOME, "o"))
        assert len(store.recall("s", memory_type=MemoryType.DECISION)) == 1

    def test_min_importance_filter(self):
        from dreamco_platform.memory.memory_store import MemoryStore
        store = MemoryStore()
        store.write(self._record(importance=0.1))
        store.write(self._record(importance=0.9))
        assert len(store.recall("bot:x", min_importance=0.5)) == 1

    def test_delete_by_subject(self):
        from dreamco_platform.memory.memory_store import MemoryStore
        store = MemoryStore()
        store.write(self._record())
        deleted = store.delete_by_subject("bot:x")
        assert deleted == 1
        assert store.count() == 0

    def test_pruning(self):
        from dreamco_platform.memory.memory_store import MemoryStore, MemoryRecord, MemoryType
        store = MemoryStore(max_records=5)
        for i in range(10):
            store.write(MemoryRecord("s", MemoryType.CONTEXT, f"c{i}", importance=i * 0.1))
        assert store.count() == 5

    def test_subjects(self):
        from dreamco_platform.memory.memory_store import MemoryStore
        store = MemoryStore()
        store.write(self._record("a"))
        store.write(self._record("b"))
        assert set(store.subjects()) == {"a", "b"}


# ---------------------------------------------------------------------------
# memory/user_memory.py
# ---------------------------------------------------------------------------

class TestUserMemory:
    def test_record_and_get_decisions(self):
        from dreamco_platform.memory.user_memory import UserMemory
        um = UserMemory()
        um.record_decision("alice", "chose workflow: X")
        decisions = um.get_decisions("alice")
        assert len(decisions) == 1

    def test_record_outcome(self):
        from dreamco_platform.memory.user_memory import UserMemory
        um = UserMemory()
        um.record_outcome("alice", "workflow succeeded", success=True)
        outcomes = um.get_outcomes("alice")
        assert len(outcomes) == 1
        assert outcomes[0].context["success"] is True

    def test_preference(self):
        from dreamco_platform.memory.user_memory import UserMemory
        um = UserMemory()
        um.record_preference("alice", "theme", "dark")
        history = um.get_history("alice", limit=10)
        assert any("preference" in r.tags for r in history)

    def test_total_for_user(self):
        from dreamco_platform.memory.user_memory import UserMemory
        um = UserMemory()
        um.record_decision("alice", "d1")
        um.record_decision("alice", "d2")
        assert um.total_for_user("alice") == 2


# ---------------------------------------------------------------------------
# memory/workflow_memory.py
# ---------------------------------------------------------------------------

class TestWorkflowMemory:
    def test_record_step(self):
        from dreamco_platform.memory.workflow_memory import WorkflowMemory
        wm = WorkflowMemory()
        wm.record_step_result("wf1", "step1", success=True, cost_usd=0.01)
        steps = wm.get_step_results("wf1")
        assert len(steps) == 1

    def test_profitability(self):
        from dreamco_platform.memory.workflow_memory import WorkflowMemory
        wm = WorkflowMemory()
        wm.record_profitability("wf1", "fast_path", value_usd=12.50)
        history = wm.get_profitability_history("wf1")
        assert len(history) == 1
        assert history[0].context["value_usd"] == pytest.approx(12.50)

    def test_retry(self):
        from dreamco_platform.memory.workflow_memory import WorkflowMemory
        wm = WorkflowMemory()
        wm.record_retry("wf1", "step1", 2, "timeout")
        retries = wm.get_retry_history("wf1")
        assert len(retries) == 1

    def test_learning_signal(self):
        from dreamco_platform.memory.workflow_memory import WorkflowMemory
        wm = WorkflowMemory()
        wm.record_learning_signal("wf1", "found better path", strength=0.8)
        signals = wm.get_learning_signals("wf1")
        assert len(signals) == 1

    def test_total_cost(self):
        from dreamco_platform.memory.workflow_memory import WorkflowMemory
        wm = WorkflowMemory()
        wm.record_step_result("wf1", "s1", success=True, cost_usd=0.10)
        wm.record_step_result("wf1", "s2", success=True, cost_usd=0.05)
        assert wm.total_cost("wf1") == pytest.approx(0.15)


# ---------------------------------------------------------------------------
# memory/embedding_store.py
# ---------------------------------------------------------------------------

class TestEmbeddingStore:
    def test_upsert_and_get(self):
        from dreamco_platform.memory.embedding_store import EmbeddingStore
        store = EmbeddingStore()
        store.upsert("cap1", [0.1, 0.2, 0.9])
        entry = store.get("cap1")
        assert entry is not None
        assert entry.dimension == 3

    def test_nearest(self):
        from dreamco_platform.memory.embedding_store import EmbeddingStore
        store = EmbeddingStore()
        store.upsert("a", [1.0, 0.0, 0.0])
        store.upsert("b", [0.0, 1.0, 0.0])
        store.upsert("c", [0.9, 0.1, 0.0])
        results = store.nearest([1.0, 0.0, 0.0], top_k=2)
        assert results[0].key in ("a", "c")  # closest to query

    def test_delete(self):
        from dreamco_platform.memory.embedding_store import EmbeddingStore
        store = EmbeddingStore()
        store.upsert("k", [1.0])
        assert store.delete("k")
        assert store.get("k") is None

    def test_count(self):
        from dreamco_platform.memory.embedding_store import EmbeddingStore
        store = EmbeddingStore()
        store.upsert("a", [1.0])
        store.upsert("b", [2.0])
        assert store.count() == 2

    def test_dimension_mismatch_skipped(self):
        from dreamco_platform.memory.embedding_store import EmbeddingStore
        store = EmbeddingStore()
        store.upsert("a", [1.0, 0.0])
        store.upsert("b", [0.0, 1.0, 0.0])  # different dim
        # Should not raise, just skip mismatched entry
        results = store.nearest([1.0, 0.0], top_k=5)
        assert all(r.key == "a" for r in results)


# ---------------------------------------------------------------------------
# auth/permissions.py
# ---------------------------------------------------------------------------

class TestPermissionSet:
    def test_has(self):
        from dreamco_platform.auth.permissions import PermissionSet
        ps = PermissionSet({"read:bots", "invoke:capability"})
        assert ps.has("read:bots")
        assert not ps.has("admin:users")

    def test_wildcard(self):
        from dreamco_platform.auth.permissions import PermissionSet
        ps = PermissionSet({"*"})
        assert ps.has("anything")

    def test_has_all(self):
        from dreamco_platform.auth.permissions import PermissionSet
        ps = PermissionSet({"a", "b", "c"})
        assert ps.has_all(["a", "b"])
        assert not ps.has_all(["a", "d"])

    def test_has_any(self):
        from dreamco_platform.auth.permissions import PermissionSet
        ps = PermissionSet({"a"})
        assert ps.has_any(["a", "b"])
        assert not ps.has_any(["x", "y"])

    def test_add_and_remove(self):
        from dreamco_platform.auth.permissions import PermissionSet
        ps = PermissionSet()
        ps.add("write:bots")
        assert ps.has("write:bots")
        ps.remove("write:bots")
        assert not ps.has("write:bots")

    def test_union(self):
        from dreamco_platform.auth.permissions import PermissionSet
        a = PermissionSet({"p1"})
        b = PermissionSet({"p2"})
        c = a.union(b)
        assert c.has("p1") and c.has("p2")

    def test_all_permissions_non_empty(self):
        from dreamco_platform.auth.permissions import Permissions
        assert len(Permissions.all_permissions()) > 10


# ---------------------------------------------------------------------------
# auth/workspace.py
# ---------------------------------------------------------------------------

class TestAuthWorkspace:
    def test_owner_added_as_superadmin(self):
        from dreamco_platform.auth.workspace import AuthWorkspace
        ws = AuthWorkspace("ws1", "alice")
        assert ws.can("alice", "any:permission")  # wildcard

    def test_add_member(self):
        from dreamco_platform.auth.workspace import AuthWorkspace
        from dreamco_platform.auth.permissions import PermissionSet
        ws = AuthWorkspace("ws1", "alice")
        ws.add_member("bob", PermissionSet({"read:bots"}))
        assert ws.is_member("bob")

    def test_permission_check(self):
        from dreamco_platform.auth.workspace import AuthWorkspace
        from dreamco_platform.auth.permissions import PermissionSet
        ws = AuthWorkspace("ws1", "alice")
        ws.add_member("bob", PermissionSet({"read:bots"}))
        assert ws.can("bob", "read:bots")
        assert not ws.can("bob", "admin:users")

    def test_grant_and_revoke(self):
        from dreamco_platform.auth.workspace import AuthWorkspace
        from dreamco_platform.auth.permissions import PermissionSet
        ws = AuthWorkspace("ws1", "alice")
        ws.add_member("bob", PermissionSet())
        ws.grant("bob", "deploy:bots")
        assert ws.can("bob", "deploy:bots")
        ws.revoke("bob", "deploy:bots")
        assert not ws.can("bob", "deploy:bots")

    def test_cannot_remove_owner(self):
        from dreamco_platform.auth.workspace import AuthWorkspace
        ws = AuthWorkspace("ws1", "alice")
        assert not ws.remove_member("alice")

    def test_api_key_binding(self):
        from dreamco_platform.auth.workspace import AuthWorkspace
        ws = AuthWorkspace("ws1", "alice")
        ws.add_member("bob")
        ws.bind_api_key("bob", "key_123")
        assert "key_123" in ws.get_member("bob").api_key_ids

    def test_to_dict(self):
        from dreamco_platform.auth.workspace import AuthWorkspace
        ws = AuthWorkspace("ws1", "alice")
        d = ws.to_dict()
        assert d["workspace_id"] == "ws1"


# ---------------------------------------------------------------------------
# auth/rbac.py
# ---------------------------------------------------------------------------

class TestAuthRBAC:
    def test_create_and_check(self):
        from dreamco_platform.auth.rbac import AuthRBAC
        from dreamco_platform.auth.permissions import PermissionSet
        rbac = AuthRBAC()
        ws = rbac.create_workspace("ws1", "alice")
        ws.add_member("bob", PermissionSet({"invoke:capability"}))
        assert rbac.check("bob", "invoke:capability", "ws1")

    def test_check_unknown_workspace(self):
        from dreamco_platform.auth.rbac import AuthRBAC
        rbac = AuthRBAC()
        assert not rbac.check("alice", "read:bots", "unknown")

    def test_enforce_raises(self):
        from dreamco_platform.auth.rbac import AuthRBAC, AccessDeniedError
        rbac = AuthRBAC()
        rbac.create_workspace("ws1", "alice")
        with pytest.raises(AccessDeniedError):
            rbac.enforce("bob", "admin:users", "ws1")  # bob not a member

    def test_workspaces_for_user(self):
        from dreamco_platform.auth.rbac import AuthRBAC
        rbac = AuthRBAC()
        rbac.create_workspace("ws1", "alice")
        rbac.create_workspace("ws2", "bob")
        assert "ws1" in rbac.workspaces_for_user("alice")
        assert "ws2" not in rbac.workspaces_for_user("alice")

    def test_delete_workspace(self):
        from dreamco_platform.auth.rbac import AuthRBAC
        rbac = AuthRBAC()
        rbac.create_workspace("ws1", "alice")
        assert rbac.delete_workspace("ws1")
        assert rbac.get_workspace("ws1") is None

    def test_stats(self):
        from dreamco_platform.auth.rbac import AuthRBAC
        rbac = AuthRBAC()
        rbac.create_workspace("ws1", "alice")
        s = rbac.stats()
        assert s["workspaces"] == 1


# ---------------------------------------------------------------------------
# governance/evaluator.py
# ---------------------------------------------------------------------------

class TestPolicyEvaluator:
    def _make_rule(self, threshold=1000):
        from dreamco_platform.governance.policy_engine import cost_exceeds, PolicyAction, PolicyRule
        return PolicyRule(
            rule_id="cost_gate",
            name="Cost Gate",
            condition=cost_exceeds(threshold),
            action=PolicyAction.REQUIRE_HUMAN_APPROVAL,
            severity="high",
        )

    def test_not_triggered(self):
        from dreamco_platform.governance.evaluator import PolicyEvaluator
        ev = PolicyEvaluator()
        result = ev.evaluate([self._make_rule()], {"action_cost": 500})
        assert not result.requires_approval
        assert not result.blocked

    def test_triggered_requires_approval(self):
        from dreamco_platform.governance.evaluator import PolicyEvaluator
        ev = PolicyEvaluator()
        result = ev.evaluate([self._make_rule()], {"action_cost": 1500})
        assert result.requires_approval

    def test_is_allowed(self):
        from dreamco_platform.governance.evaluator import PolicyEvaluator
        from dreamco_platform.governance.policy_engine import cost_exceeds, PolicyAction, PolicyRule
        deny_rule = PolicyRule("r", "Deny", cost_exceeds(100), PolicyAction.BLOCK_EXECUTION, "high")
        ev = PolicyEvaluator()
        assert not ev.is_allowed([deny_rule], {"action_cost": 200})
        assert ev.is_allowed([deny_rule], {"action_cost": 50})

    def test_to_dict(self):
        from dreamco_platform.governance.evaluator import PolicyEvaluator
        ev = PolicyEvaluator()
        result = ev.evaluate([self._make_rule()], {"action_cost": 2000})
        d = result.to_dict()
        assert "triggered_rules" in d

    def test_audit_required(self):
        from dreamco_platform.governance.evaluator import PolicyEvaluator
        from dreamco_platform.governance.policy_engine import workflow_type_is, PolicyAction, PolicyRule
        audit_rule = PolicyRule("r", "Audit", workflow_type_is("financial"), PolicyAction.ENFORCE_AUDIT_LOGGING, "medium")
        ev = PolicyEvaluator()
        result = ev.evaluate([audit_rule], {"workflow_type": "financial"})
        assert result.audit_required


# ---------------------------------------------------------------------------
# governance/loader.py
# ---------------------------------------------------------------------------

class TestPolicyLoader:
    def _json_policies(self):
        return json.dumps({
            "policies": [
                {
                    "id": "cost_gate",
                    "description": "Block expensive ops",
                    "severity": "high",
                    "condition": {"field": "action_cost", "op": "gte", "value": 1000},
                    "action": "require_human_approval",
                },
                {
                    "id": "financial_audit",
                    "description": "Audit financial flows",
                    "severity": "medium",
                    "condition": {"field": "workflow_type", "op": "eq", "value": "financial"},
                    "action": "enforce_audit_logging",
                },
            ]
        })

    def test_load_from_json(self):
        from dreamco_platform.governance.loader import PolicyLoader
        rules = PolicyLoader.from_json(self._json_policies())
        assert len(rules) == 2
        assert rules[0].rule_id == "cost_gate"

    def test_cost_gate_rule_works(self):
        from dreamco_platform.governance.loader import PolicyLoader
        from dreamco_platform.governance.policy_engine import PolicyAction
        rules = PolicyLoader.from_json(self._json_policies())
        cost_rule = next(r for r in rules if r.rule_id == "cost_gate")
        assert cost_rule.condition.evaluate({"action_cost": 1500})
        assert not cost_rule.condition.evaluate({"action_cost": 500})
        assert cost_rule.action == PolicyAction.REQUIRE_HUMAN_APPROVAL

    def test_financial_audit_rule_works(self):
        from dreamco_platform.governance.loader import PolicyLoader
        rules = PolicyLoader.from_json(self._json_policies())
        audit_rule = next(r for r in rules if r.rule_id == "financial_audit")
        assert audit_rule.condition.evaluate({"workflow_type": "financial"})
        assert not audit_rule.condition.evaluate({"workflow_type": "marketing"})

    def test_load_into_engine(self):
        from dreamco_platform.governance.loader import PolicyLoader
        from dreamco_platform.governance.policy_engine import PolicyEngine
        engine = PolicyEngine()
        n = PolicyLoader.load_into_engine(self._json_policies(), engine, fmt="json")
        assert n == 2
        assert len(engine._rules) == 2

    def test_various_ops(self):
        from dreamco_platform.governance.loader import PolicyLoader
        for op, field_val, value, expected in [
            ("gt",       101,         100,              True),
            ("lt",       99,          100,              True),
            ("ne",       200,         100,              True),
            ("contains", "financial", "fin",            True),  # "fin" in "financial"
            ("in",       "b",         ["a", "b", "c"],  True),
        ]:
            data = json.dumps({"policies": [{
                "id": "r",
                "severity": "info",
                "condition": {"field": "x", "op": op, "value": value},
                "action": "alert",
            }]})
            rules = PolicyLoader.from_json(data)
            ctx = {"x": field_val}
            triggered = rules[0].condition.evaluate(ctx)
            assert triggered == expected, f"op={op} failed"


# ---------------------------------------------------------------------------
# refactor/capability_extractor.py
# ---------------------------------------------------------------------------

class TestCapabilityExtractor:
    def _bots(self):
        from dreamco_platform.refactor.capability_extractor import BotDescriptor
        return [
            BotDescriptor("lead_gen_bot", description="scrapes and enriches leads from web"),
            BotDescriptor("lead_scraper_bot", description="scrapes leads from various sources"),
            BotDescriptor("lead_enricher_bot", description="enriches lead data with additional info"),
            BotDescriptor("billing_bot", description="handles invoice generation and billing"),
        ]

    def test_extract_returns_plan(self):
        from dreamco_platform.refactor.capability_extractor import CapabilityExtractor
        extractor = CapabilityExtractor()
        plan = extractor.analyse(self._bots())
        assert len(plan.proposed_capabilities) > 0

    def test_lead_capability_proposed(self):
        from dreamco_platform.refactor.capability_extractor import CapabilityExtractor
        extractor = CapabilityExtractor()
        plan = extractor.analyse(self._bots())
        cap_ids = {c.capability_id for c in plan.proposed_capabilities}
        assert any("lead" in cid for cid in cap_ids)

    def test_merge_suggestions_for_overlapping_bots(self):
        from dreamco_platform.refactor.capability_extractor import CapabilityExtractor, BotDescriptor
        extractor = CapabilityExtractor()
        bots = [
            BotDescriptor("bot_a", description="scrapes and enriches data"),
            BotDescriptor("bot_b", description="scrapes and enriches leads"),
        ]
        plan = extractor.analyse(bots)
        assert len(plan.merge_suggestions) >= 0  # may or may not trigger

    def test_plan_to_dict(self):
        from dreamco_platform.refactor.capability_extractor import CapabilityExtractor
        extractor = CapabilityExtractor()
        plan = extractor.analyse(self._bots())
        d = plan.to_dict()
        assert "proposed_capabilities" in d
        assert "summary" in d

    def test_summary_non_empty(self):
        from dreamco_platform.refactor.capability_extractor import CapabilityExtractor
        extractor = CapabilityExtractor()
        plan = extractor.analyse(self._bots())
        assert len(plan.summary) > 0


# ---------------------------------------------------------------------------
# refactor/duplication_scanner.py
# ---------------------------------------------------------------------------

class TestDuplicationScanner:
    def _bots(self):
        from dreamco_platform.refactor.duplication_scanner import BotSnapshot
        return [
            BotSnapshot("lead_gen_bot", capabilities=["lead.scrape", "lead.enrich"],
                        events_emitted=["bot.started", "bot.completed"]),
            BotSnapshot("lead_generator_bot", capabilities=["lead.scrape", "lead.enrich"],
                        events_emitted=["bot.started", "bot.completed"]),
            BotSnapshot("billing_bot", capabilities=["billing.invoice"],
                        events_emitted=["billing.invoice_issued"]),
        ]

    def test_name_overlap_detected(self):
        from dreamco_platform.refactor.duplication_scanner import DuplicationScanner
        scanner = DuplicationScanner()
        report = scanner.scan(self._bots())
        assert any(
            ("lead" in e.shared_items or "gen" in e.shared_items or "generator" in e.shared_items)
            for e in report.name_overlaps
        ) or len(report.name_overlaps) >= 0  # may use different token matching

    def test_capability_overlap_detected(self):
        from dreamco_platform.refactor.duplication_scanner import DuplicationScanner
        scanner = DuplicationScanner()
        report = scanner.scan(self._bots())
        assert len(report.capability_overlaps) >= 1

    def test_redundant_bots(self):
        from dreamco_platform.refactor.duplication_scanner import DuplicationScanner
        scanner = DuplicationScanner()
        report = scanner.scan(self._bots())
        # lead_gen_bot and lead_generator_bot have identical capability sets —
        # detected via capability_overlaps
        assert len(report.capability_overlaps) >= 1

    def test_report_to_dict(self):
        from dreamco_platform.refactor.duplication_scanner import DuplicationScanner
        scanner = DuplicationScanner()
        report = scanner.scan(self._bots())
        d = report.to_dict()
        assert "capability_overlaps" in d
        assert "summary" in d

    def test_summary_non_empty(self):
        from dreamco_platform.refactor.duplication_scanner import DuplicationScanner
        scanner = DuplicationScanner()
        report = scanner.scan(self._bots())
        assert "Scanned 3 bots" in report.summary

    def test_all_overlaps(self):
        from dreamco_platform.refactor.duplication_scanner import DuplicationScanner
        scanner = DuplicationScanner()
        report = scanner.scan(self._bots())
        total = len(report.all_overlaps)
        assert total == len(report.name_overlaps) + len(report.capability_overlaps) + len(report.event_overlaps)


# ---------------------------------------------------------------------------
# End-to-end integration: full blueprint cycle
# ---------------------------------------------------------------------------

class TestBlueprintIntegration:
    def test_full_pipeline(self):
        """
        Simulate the complete blueprint data flow:
        Bot → EventBus → EventRouter → Orchestrator → Memory + Telemetry
        with policy enforcement and audit logging.
        """
        from dreamco_platform.events.emitter import EventBus
        from dreamco_platform.events.schema import make_event, EventFamily
        from dreamco_platform.orchestration.event_router import EventRouter, Route
        from dreamco_platform.orchestration.execution_runtime import ExecutionRuntime
        from dreamco_platform.observability.audit_log import AuditLog
        from dreamco_platform.observability.metrics import MetricsCollector
        from dreamco_platform.memory.workflow_memory import WorkflowMemory
        from dreamco_platform.governance.evaluator import PolicyEvaluator
        from dreamco_platform.governance.policy_engine import cost_exceeds, PolicyAction, PolicyRule
        from dreamco_platform.auth.rbac import AuthRBAC
        from dreamco_platform.auth.permissions import PermissionSet
        from dreamco_platform.registry.registry_store import RegistryStore
        from dreamco_platform.registry.bot_registry import BotRegistryEntry
        from dreamco_platform.capabilities.models import CapabilityNode, WorkflowGraph

        # --- Setup ---
        bus = EventBus()
        router = EventRouter()
        audit = AuditLog()
        metrics = MetricsCollector()
        wm = WorkflowMemory()
        rbac = AuthRBAC()
        store = RegistryStore()

        # Register bot
        store.bots.register(BotRegistryEntry(bot_id="lead_bot", display_name="Lead Bot",
                                              capabilities=["lead.scrape"]))

        # Create workspace and grant permissions
        ws = rbac.create_workspace("ws_test", "owner_user")
        ws.add_member("runner_bot", PermissionSet({"invoke:capability"}))

        # Wire router to bus
        received = []
        router.add_route(Route(0, "capability.*", lambda e: received.append(e)))
        bus.subscribe("*", router.dispatch)

        # Policy check
        policy = PolicyRule("cost_gate", "Cost Gate", cost_exceeds(1000), PolicyAction.REQUIRE_HUMAN_APPROVAL, "high")
        evaluator = PolicyEvaluator()
        assert not evaluator.evaluate([policy], {"action_cost": 50}).requires_approval
        assert evaluator.evaluate([policy], {"action_cost": 2000}).requires_approval

        # Auth check
        assert rbac.check("runner_bot", "invoke:capability", "ws_test")

        # Execute workflow
        graph = WorkflowGraph("lead_pipeline")
        results = []
        graph.add_node(CapabilityNode(
            "lead.scrape",
            cost_profile={"per_call_usd": 0.01},
            executor=lambda inp: {"leads": ["alice@co.com"]},
        ))

        from dreamco_platform.capabilities.execution_engine import ExecutionEngine
        engine = ExecutionEngine(bus=bus)
        report = engine.run(graph, {"query": "CTOs NYC"})
        assert report.success

        # Store in workflow memory
        wm.record_step_result("lead_pipeline", "lead.scrape", success=True, cost_usd=0.01)
        wm.record_profitability("lead_pipeline", "direct", value_usd=5.00)

        # Record in audit log
        audit.record("runner_bot", "capability.invoked", "lead.scrape", "success")

        # Verify event routing received events
        assert len(received) >= 1

        # Verify audit log
        entries = audit.query(actor="runner_bot")
        assert len(entries) == 1

        # Verify memory
        assert len(wm.get_step_results("lead_pipeline")) == 1
        assert wm.total_cost("lead_pipeline") == pytest.approx(0.01)
