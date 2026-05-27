import time

import pytest

from dreamco_platform.swarm.stigmergy import (
    FileDurableEventStore,
    GovernancePolicy,
    PersistentStigmergyEnvironment,
    PheromoneTrace,
    SafetyViolation,
    StigmergicBot,
    StigmergyGovernance,
    StigmergyReplayer,
    SwarmSafetyControls,
)


class _RedisStore:
    def __init__(self):
        self.traces = []

    def put_active_trace(self, trace):
        self.traces.append(trace)

    def get_active_traces(self):
        return list(self.traces)


class _DurableStore:
    def __init__(self):
        self.events = []
        self.traces = []

    def append_trace_event(self, event):
        self.events.append(event)

    def load_active_traces(self):
        return list(self.traces)


class _ArchiveStore:
    def __init__(self):
        self.snapshots = []

    def snapshot(self, traces):
        self.snapshots.append(list(traces))


class _FailingDurableStore:
    def append_trace_event(self, event):
        raise RuntimeError("durable-store-down")

    def load_active_traces(self):
        return []


def test_observer_and_metrics_capture_deposit():
    env = PersistentStigmergyEnvironment()
    decision = env.deposit(PheromoneTrace("routing", 0.5, (1, 2), "bot_1"))
    assert decision.allowed is True
    metrics = env.metrics()
    assert metrics["active_trace_count"] == 1
    assert metrics["heatmap"]["1:2"] == 0.5
    assert "anomalies" in metrics
    assert "stigmergy_deposits_total" in metrics["prometheus"]


def test_governance_blocks_unapproved_high_impact_trace():
    governance = StigmergyGovernance(
        GovernancePolicy(
            max_strength=1.0,
            allowed_trace_types={"high_value_trade"},
            require_approval={"high_value_trade"},
            bot_role_permissions={"trader": {"high_value_trade"}},
        )
    )
    env = PersistentStigmergyEnvironment(governance=governance)
    with pytest.raises(SafetyViolation):
        env.deposit(
            PheromoneTrace("high_value_trade", 0.95, (0, 0), "bot_7"),
            bot_role="trader",
            approval=False,
        )


def test_replay_reconstructs_trace_state():
    env = PersistentStigmergyEnvironment()
    t0 = time.time()
    env.deposit(PheromoneTrace("search", 0.2, (1, 1), "bot_a"))
    env.deposit(PheromoneTrace("search", 0.4, (1, 1), "bot_b"))
    replay = StigmergyReplayer(env.event_store)
    replay_state = replay.replay_from(t0, filters={"trace_type": "search"})
    assert replay_state["events_replayed"] >= 2
    assert replay_state["rejected_events"] == 0
    assert len(replay_state["active_traces"]) == 2
    assert replay_state["total_strength"] == pytest.approx(0.6)


def test_reinforcement_uses_economic_feedback():
    bot = StigmergicBot()
    trace = PheromoneTrace("pricing", 0.5, (3, 3), "bot_x", risk=0.2)
    strengthened = bot.reinforce_trace(trace, {"profit": 4000, "risk": 0.1})
    weakened = bot.reinforce_trace(trace, {"profit": -1000, "risk": 0.8})
    assert strengthened.strength > trace.strength
    assert weakened.strength < trace.strength


def test_persistence_writes_to_all_layers_and_recovers():
    redis_store = _RedisStore()
    durable_store = _DurableStore()
    archive_store = _ArchiveStore()
    env = PersistentStigmergyEnvironment(
        redis_store=redis_store,
        durable_store=durable_store,
        archive_store=archive_store,
    )
    trace = PheromoneTrace("supply", 0.7, (2, 4), "bot_supply")
    env.deposit(trace, approval=True)
    durable_store.traces = [trace]
    recovered = env.reload_from_durable_storage()
    assert redis_store.traces == [trace]
    assert len(durable_store.events) == 1
    assert len(archive_store.snapshots) == 1
    assert recovered == [trace]


def test_safety_controls_support_kill_switch_and_rate_limit():
    safety = SwarmSafetyControls(max_actions_per_window=1, window_seconds=60)
    safety.enforce(action="deposit", bot_id="bot_1")
    try:
        safety.enforce(action="deposit", bot_id="bot_1")
        assert False
    except Exception as exc:  # noqa: BLE001
        assert "rate limit exceeded" in str(exc)
    safety.activate_kill_switch()
    try:
        safety.enforce(action="deposit", bot_id="bot_2")
        assert False
    except Exception as exc:  # noqa: BLE001
        assert "kill switch" in str(exc)


def test_governance_policy_loads_from_yaml():
    governance = StigmergyGovernance.from_yaml("config/stigmergy_governance.yaml")
    assert governance.policy.max_strength == pytest.approx(1.0)
    assert "high_value_trade" in governance.policy.require_approval
    assert "pricing" in governance.policy.bot_role_permissions["trader"]
    assert governance.required_approvals_for("high_value_trade") == 2


def test_file_durable_event_store_replays_and_prunes(tmp_path):
    event_log = tmp_path / "stigmergy_events.jsonl"
    durable_store = FileDurableEventStore(str(event_log))
    env = PersistentStigmergyEnvironment(durable_store=durable_store)
    trace = PheromoneTrace("search", 0.3, (2, 2), "bot_file")
    env.deposit(trace, approval=True)

    loaded = durable_store.load_active_traces()
    assert loaded == [trace]

    removed = durable_store.prune_before(time.time() + 1.0)
    assert removed >= 1
    assert durable_store.load_active_traces() == []


def test_distributed_safety_allows_threshold_approvals_without_boolean_override():
    policy = GovernancePolicy(
        allowed_trace_types={"high_value_trade"},
        bot_role_permissions={"trader": {"high_value_trade"}},
        min_approvals_by_trace_type={"high_value_trade": 2},
    )
    env = PersistentStigmergyEnvironment(governance=StigmergyGovernance(policy))
    trace = PheromoneTrace(
        "high_value_trade",
        0.95,
        (9, 9),
        "bot_trader",
        metadata={"approved_by": ["buddy", "safetybot"]},
    )
    decision = env.deposit(trace, bot_role="trader", approval=False)
    assert decision.allowed is True


def test_persistence_failure_rolls_back_active_trace_and_replays_failure():
    env = PersistentStigmergyEnvironment(durable_store=_FailingDurableStore())
    trace = PheromoneTrace("search", 0.4, (7, 7), "bot_failure")
    decision = env.deposit(trace, approval=True)
    assert decision.allowed is False
    assert env.active_traces() == []
    replay = StigmergyReplayer(env.event_store).replay_from(0.0)
    assert replay["rejected_events"] >= 1


def test_economic_guardrail_blocks_high_volatility_spikes():
    env = PersistentStigmergyEnvironment(max_strength_volatility=0.2)
    assert env.deposit(PheromoneTrace("search", 0.2, (1, 1), "bot_a"), approval=True).allowed
    assert env.deposit(PheromoneTrace("search", 0.22, (1, 1), "bot_b"), approval=True).allowed
    blocked = env.deposit(PheromoneTrace("search", 1.0, (1, 1), "bot_c"), approval=True)
    assert blocked.allowed is False
    assert "volatility" in blocked.reason


def test_semantic_pheromone_feedback_and_adaptive_decay():
    trace = PheromoneTrace(
        "semantic_search",
        0.8,
        (4, 4),
        "bot_semantic",
        semantic_category="lead_generation",
        trust_score=0.7,
        profitability_signal=3_000,
        volatility_signal=0.1,
    )
    updated = trace.with_semantic_feedback(trust_score=0.9, economic_score=1200.0)
    assert updated.semantic_category == "lead_generation"
    assert updated.trust_score == pytest.approx(0.9)
    assert updated.economic_score == pytest.approx(1200.0)
    decayed = updated.adaptive_decay(base_decay_rate=0.05)
    assert decayed.strength > 0.0
