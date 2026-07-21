import time

import pytest

from dreamco_platform.swarm.stigmergy import (
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


def test_observer_and_metrics_capture_deposit():
    env = PersistentStigmergyEnvironment()
    decision = env.deposit(PheromoneTrace("routing", 0.5, (1, 2), "bot_1"))
    assert decision.allowed is True
    metrics = env.metrics()
    assert metrics["active_trace_count"] == 1
    assert metrics["heatmap"]["1:2"] == 0.5
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
