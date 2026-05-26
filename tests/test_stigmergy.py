from __future__ import annotations

from datetime import datetime, timedelta, timezone

from dreamco_platform.swarm.runtime import DreamCoRuntime
from dreamco_platform.swarm.stigmergy.pheromone import SemanticPheromone
from dreamco_platform.swarm.stigmergy.stigmergic_bot import ForagingRole, StigmergicBot


def test_semantic_pheromone_adaptive_decay_prefers_profitable_paths():
    now = datetime.now(timezone.utc)
    profitable = SemanticPheromone(
        trace_type="lead",
        semantic_category="real_estate",
        strength=1.0,
        economic_score=0.9,
        reinforcement_count=4,
        created_at=now - timedelta(hours=6),
    )
    failed = SemanticPheromone(
        trace_type="lead",
        semantic_category="real_estate",
        strength=1.0,
        execution_outcome="failed",
        volatility_score=0.8,
        created_at=now - timedelta(hours=6),
    )
    assert profitable.current_strength(now=now) > failed.current_strength(now=now)


def test_runtime_stigmergy_semantic_search_and_reinforcement():
    runtime = DreamCoRuntime()
    pheromone = SemanticPheromone(
        trace_type="lead_opportunity",
        semantic_category="distress",
        strength=0.6,
        embedding=[0.1, 0.9, 0.2],
        context={"vertical": "real_estate"},
    )
    runtime.stigmergy.deposit(pheromone)

    traces = runtime.stigmergy.read_traces(
        context={"vertical": "real_estate"},
        trace_types=["lead_opportunity"],
        embedding=[0.1, 0.88, 0.2],
    )
    assert traces
    assert traces[0].id == pheromone.id

    assert runtime.reinforce_trace(pheromone.id, profit_delta=0.4, success=True)
    assert runtime.stigmergy.read_traces(trace_types=["lead_opportunity"])[0].reinforcement_count == 1


def test_foraging_roles_cover_explorer_exploiter_guardian_and_synthesizer():
    runtime = DreamCoRuntime()
    env = runtime.stigmergy
    bot = StigmergicBot(name="seed", environment=env)
    bot.deposit_trace(
        trace_type="market_signal",
        semantic_category="distress",
        context={"market": "A"},
        strength=0.8,
    )
    bot.deposit_trace(
        trace_type="market_signal",
        semantic_category="risk",
        context={"market": "A"},
        strength=0.7,
        metadata={"anomaly": True},
    )
    risk_trace = env.read_traces(trace_types=["market_signal"])[1]
    risk_trace.volatility_score = 0.9
    risk_trace.trust_score = 0.2

    explorer = StigmergicBot(name="exp", environment=env, role=ForagingRole.EXPLORER)
    exploiter = StigmergicBot(name="xpt", environment=env, role=ForagingRole.EXPLOITER)
    guardian = StigmergicBot(name="guard", environment=env, role=ForagingRole.GUARDIAN)
    synth = StigmergicBot(name="syn", environment=env, role=ForagingRole.SYNTHESIZER)

    assert explorer.forage(trace_types=["market_signal"])["mode"] == "explore"
    assert exploiter.forage(trace_types=["market_signal"])["selected"] is not None
    assert guardian.forage(trace_types=["market_signal"])["selected"]
    assert synth.forage(trace_types=["market_signal"])["selected"]["distress"] >= 1
