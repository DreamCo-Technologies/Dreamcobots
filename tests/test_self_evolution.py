"""
Tests for core/self_evolution.py — DreamCo Self-Evolution Engine.

Validates:
  1. SelfEvolutionEngine instantiation and defaults
  2. Performance tracking (record_run, efficiency)
  3. Strategy mutation under different efficiency conditions
  4. Phase promotion (Phase 1 → 2 → 3) with correct LLM provider switches
  5. LLM provider recommendation (suggest_llm_provider)
  6. Evolution history recording
  7. BaseBot self-evolution wiring (_success / _failure auto-recording,
     evolve(), evolution_status(), set_llm_provider())
  8. LLMProvider and EvolutionPhase enum completeness
"""

from __future__ import annotations

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

from core.self_evolution import (
    LLMProvider,
    EvolutionPhase,
    EvolutionRecord,
    SelfEvolutionEngine,
    CATEGORY_LLM_MAP,
    PHASE_2_MIN_RUNS,
    PHASE_2_MIN_EFFICIENCY,
    PHASE_3_MIN_RUNS,
    PHASE_3_MIN_EFFICIENCY,
)
from core.base_bot import BaseBot


# ===========================================================================
# Helpers
# ===========================================================================

class _DummyBot(BaseBot):
    bot_id = "dummy_bot"
    name = "Dummy Bot"
    category = "ai"

    def run(self, task: dict) -> dict:
        if task.get("fail"):
            return self._failure("forced failure")
        return self._success(data={"ok": True}, metrics={"revenue": task.get("revenue", 0.0)})


def _make_engine(category: str = "general") -> SelfEvolutionEngine:
    return SelfEvolutionEngine(bot_id="test_bot", category=category)


def _run_n(engine: SelfEvolutionEngine, n: int, success: bool = True, revenue: float = 0.0) -> None:
    for _ in range(n):
        engine.record_run(success=success, revenue=revenue)


# ===========================================================================
# LLMProvider enum
# ===========================================================================

class TestLLMProvider:
    def test_phase1_commercial_providers_present(self):
        assert LLMProvider.OPENAI in LLMProvider
        assert LLMProvider.ANTHROPIC in LLMProvider
        assert LLMProvider.GOOGLE in LLMProvider

    def test_phase2_open_source_providers_present(self):
        assert LLMProvider.LLAMA in LLMProvider
        assert LLMProvider.MISTRAL in LLMProvider
        assert LLMProvider.DEEPSEEK in LLMProvider
        assert LLMProvider.QWEN in LLMProvider

    def test_phase2_dreamco_domain_providers_present(self):
        assert LLMProvider.DREAMCO_FINANCE in LLMProvider
        assert LLMProvider.DREAMCO_REAL_ESTATE in LLMProvider
        assert LLMProvider.DREAMCO_CODING in LLMProvider
        assert LLMProvider.DREAMCO_TRADING in LLMProvider

    def test_phase3_proprietary_provider_present(self):
        assert LLMProvider.DREAMCO_PROPRIETARY in LLMProvider

    def test_provider_values_are_strings(self):
        for p in LLMProvider:
            assert isinstance(p.value, str)


# ===========================================================================
# EvolutionPhase enum
# ===========================================================================

class TestEvolutionPhase:
    def test_three_phases_defined(self):
        phases = list(EvolutionPhase)
        assert len(phases) == 3

    def test_phase_values(self):
        assert EvolutionPhase.PHASE_1_AI_OS.value == "phase_1_ai_os"
        assert EvolutionPhase.PHASE_2_FINE_TUNED.value == "phase_2_fine_tuned"
        assert EvolutionPhase.PHASE_3_PROPRIETARY.value == "phase_3_proprietary"


# ===========================================================================
# SelfEvolutionEngine — instantiation and defaults
# ===========================================================================

class TestSelfEvolutionEngineInit:
    def test_default_phase_is_phase1(self):
        engine = _make_engine()
        assert engine.phase == EvolutionPhase.PHASE_1_AI_OS

    def test_default_llm_is_llama_for_unknown_category(self):
        engine = _make_engine(category="unknown_xyz")
        assert engine.llm_provider == LLMProvider.LLAMA

    def test_finance_category_gets_dreamco_finance_provider(self):
        engine = _make_engine(category="finance")
        assert engine.llm_provider == LLMProvider.DREAMCO_FINANCE

    def test_real_estate_category_provider(self):
        engine = _make_engine(category="real_estate")
        assert engine.llm_provider == LLMProvider.DREAMCO_REAL_ESTATE

    def test_explicit_provider_override(self):
        engine = SelfEvolutionEngine(
            bot_id="b", category="finance", llm_provider=LLMProvider.OPENAI
        )
        assert engine.llm_provider == LLMProvider.OPENAI

    def test_zero_runs_on_init(self):
        engine = _make_engine()
        assert engine._total_runs == 0
        assert engine._successful_runs == 0
        assert engine._total_revenue == 0.0

    def test_zero_evolution_cycles_on_init(self):
        engine = _make_engine()
        assert engine._evolution_cycle == 0

    def test_empty_history_on_init(self):
        engine = _make_engine()
        assert engine.get_evolution_history() == []


# ===========================================================================
# SelfEvolutionEngine — performance tracking
# ===========================================================================

class TestPerformanceTracking:
    def test_efficiency_with_no_runs_is_one(self):
        engine = _make_engine()
        assert engine.efficiency == 1.0

    def test_efficiency_all_successes(self):
        engine = _make_engine()
        _run_n(engine, 10, success=True)
        assert engine.efficiency == 1.0

    def test_efficiency_all_failures(self):
        engine = _make_engine()
        _run_n(engine, 10, success=False)
        assert engine.efficiency == 0.0

    def test_efficiency_mixed_runs(self):
        engine = _make_engine()
        _run_n(engine, 7, success=True)
        _run_n(engine, 3, success=False)
        assert round(engine.efficiency, 2) == 0.70

    def test_revenue_accumulates(self):
        engine = _make_engine()
        engine.record_run(success=True, revenue=100.0)
        engine.record_run(success=True, revenue=200.0)
        assert engine._total_revenue == 300.0

    def test_total_runs_increments(self):
        engine = _make_engine()
        _run_n(engine, 5)
        assert engine._total_runs == 5

    def test_performance_snapshot_keys(self):
        engine = _make_engine()
        _run_n(engine, 3, success=True, revenue=10.0)
        snap = engine._performance_snapshot()
        for key in ("efficiency", "total_runs", "successful_runs",
                    "success_rate_pct", "total_revenue_usd", "evolution_cycle"):
            assert key in snap


# ===========================================================================
# SelfEvolutionEngine — phase promotion
# ===========================================================================

class TestPhasePromotion:
    def test_no_promotion_below_threshold(self):
        engine = _make_engine()
        _run_n(engine, PHASE_2_MIN_RUNS - 1, success=True)
        engine.evolve()
        assert engine.phase == EvolutionPhase.PHASE_1_AI_OS

    def test_phase1_to_phase2_promotion(self):
        engine = _make_engine(category="sales")
        _run_n(engine, PHASE_2_MIN_RUNS, success=True)
        engine.evolve()
        assert engine.phase == EvolutionPhase.PHASE_2_FINE_TUNED

    def test_phase2_llm_matches_category(self):
        engine = _make_engine(category="sales")
        _run_n(engine, PHASE_2_MIN_RUNS, success=True)
        engine.evolve()
        assert engine.llm_provider == LLMProvider.MISTRAL

    def test_phase2_to_phase3_promotion(self):
        engine = _make_engine()
        # Force into Phase 2 first
        _run_n(engine, PHASE_2_MIN_RUNS, success=True)
        engine.evolve()
        assert engine.phase == EvolutionPhase.PHASE_2_FINE_TUNED
        # Now accumulate enough for Phase 3
        _run_n(engine, PHASE_3_MIN_RUNS - PHASE_2_MIN_RUNS, success=True)
        engine.evolve()
        assert engine.phase == EvolutionPhase.PHASE_3_PROPRIETARY

    def test_phase3_llm_is_dreamco_proprietary(self):
        engine = _make_engine()
        _run_n(engine, PHASE_3_MIN_RUNS, success=True)
        engine.evolve()
        engine.evolve()  # second cycle to confirm stability
        assert engine.llm_provider == LLMProvider.DREAMCO_PROPRIETARY

    def test_no_promotion_with_low_efficiency(self):
        engine = _make_engine()
        # Run many times but with low success rate
        _run_n(engine, PHASE_2_MIN_RUNS, success=False)
        engine.evolve()
        assert engine.phase == EvolutionPhase.PHASE_1_AI_OS

    def test_phase_transition_flag_in_record(self):
        engine = _make_engine()
        _run_n(engine, PHASE_2_MIN_RUNS, success=True)
        record = engine.evolve()
        assert record.metadata.get("phase_transition") is True

    def test_no_phase_transition_flag_when_stable(self):
        engine = _make_engine()
        _run_n(engine, 5, success=True)
        record = engine.evolve()
        assert record.metadata.get("phase_transition") is False


# ===========================================================================
# SelfEvolutionEngine — strategy mutation
# ===========================================================================

class TestStrategyMutation:
    def test_underperforming_increases_exploration(self):
        engine = _make_engine()
        _run_n(engine, 10, success=False)  # 0% efficiency
        before = engine._strategy["exploration_rate"]
        engine.evolve()
        assert engine._strategy["exploration_rate"] > before

    def test_underperforming_increases_learning_rate(self):
        engine = _make_engine()
        _run_n(engine, 10, success=False)
        before = engine._strategy["learning_rate"]
        engine.evolve()
        assert engine._strategy["learning_rate"] > before

    def test_high_performer_reduces_exploration(self):
        engine = _make_engine()
        _run_n(engine, 100, success=True)  # 100% efficiency
        before = engine._strategy["exploration_rate"]
        engine.evolve()
        assert engine._strategy["exploration_rate"] < before

    def test_high_performer_reduces_learning_rate(self):
        engine = _make_engine()
        _run_n(engine, 100, success=True)
        before = engine._strategy["learning_rate"]
        engine.evolve()
        assert engine._strategy["learning_rate"] < before

    def test_strategy_delta_recorded(self):
        engine = _make_engine()
        _run_n(engine, 10, success=False)
        record = engine.evolve()
        assert isinstance(record.strategy_delta, dict)
        assert "exploration_rate" in record.strategy_delta

    def test_strategy_exploration_rate_stays_bounded(self):
        engine = _make_engine()
        for _ in range(20):
            _run_n(engine, 5, success=False)
            engine.evolve()
        assert 0.0 <= engine._strategy["exploration_rate"] <= 1.0

    def test_strategy_confidence_threshold_stays_bounded(self):
        engine = _make_engine()
        for _ in range(20):
            _run_n(engine, 5, success=True)
            engine.evolve()
        assert 0.0 <= engine._strategy["confidence_threshold"] <= 1.0


# ===========================================================================
# SelfEvolutionEngine — suggest_llm_provider
# ===========================================================================

class TestSuggestLLMProvider:
    def test_phase1_suggests_llama(self):
        engine = _make_engine(category="general")
        assert engine.suggest_llm_provider() == LLMProvider.LLAMA

    def test_phase2_suggests_category_model(self):
        engine = _make_engine(category="finance")
        engine.phase = EvolutionPhase.PHASE_2_FINE_TUNED
        assert engine.suggest_llm_provider() == LLMProvider.DREAMCO_FINANCE

    def test_phase3_always_suggests_proprietary(self):
        engine = _make_engine(category="finance")
        engine.phase = EvolutionPhase.PHASE_3_PROPRIETARY
        assert engine.suggest_llm_provider() == LLMProvider.DREAMCO_PROPRIETARY


# ===========================================================================
# SelfEvolutionEngine — evolution history
# ===========================================================================

class TestEvolutionHistory:
    def test_history_grows_with_each_cycle(self):
        engine = _make_engine()
        assert len(engine.get_evolution_history()) == 0
        engine.evolve()
        assert len(engine.get_evolution_history()) == 1
        engine.evolve()
        assert len(engine.get_evolution_history()) == 2

    def test_history_record_keys(self):
        engine = _make_engine()
        engine.evolve()
        record = engine.get_evolution_history()[0]
        for key in ("cycle", "timestamp", "phase", "llm_provider",
                    "performance_before", "performance_after",
                    "strategy_delta", "fitness_improvement", "metadata"):
            assert key in record

    def test_cycle_numbers_are_sequential(self):
        engine = _make_engine()
        for _ in range(5):
            engine.evolve()
        cycles = [r["cycle"] for r in engine.get_evolution_history()]
        assert cycles == [1, 2, 3, 4, 5]

    def test_evolution_record_phase_value_is_string(self):
        engine = _make_engine()
        engine.evolve()
        record = engine.get_evolution_history()[0]
        assert isinstance(record["phase"], str)

    def test_evolution_record_llm_value_is_string(self):
        engine = _make_engine()
        engine.evolve()
        record = engine.get_evolution_history()[0]
        assert isinstance(record["llm_provider"], str)


# ===========================================================================
# SelfEvolutionEngine — evolution_status
# ===========================================================================

class TestEvolutionStatus:
    def test_status_contains_required_keys(self):
        engine = _make_engine()
        status = engine.evolution_status()
        for key in ("bot_id", "category", "phase", "llm_provider",
                    "suggested_llm", "evolution_cycle", "performance",
                    "strategy", "history_count"):
            assert key in status

    def test_status_bot_id(self):
        engine = SelfEvolutionEngine(bot_id="my_bot", category="ai")
        assert engine.evolution_status()["bot_id"] == "my_bot"

    def test_status_phase_matches_engine_phase(self):
        engine = _make_engine()
        assert engine.evolution_status()["phase"] == engine.phase.value

    def test_status_history_count_increments(self):
        engine = _make_engine()
        assert engine.evolution_status()["history_count"] == 0
        engine.evolve()
        assert engine.evolution_status()["history_count"] == 1


# ===========================================================================
# BaseBot — self-evolution wiring
# ===========================================================================

class TestBaseBotSelfEvolution:
    def test_bot_has_self_evolution_attribute(self):
        bot = _DummyBot()
        assert hasattr(bot, "self_evolution")
        assert isinstance(bot.self_evolution, SelfEvolutionEngine)

    def test_success_auto_records_run(self):
        bot = _DummyBot()
        bot.run({"fail": False})
        assert bot.self_evolution._total_runs == 1
        assert bot.self_evolution._successful_runs == 1

    def test_failure_auto_records_run(self):
        bot = _DummyBot()
        bot.run({"fail": True})
        assert bot.self_evolution._total_runs == 1
        assert bot.self_evolution._successful_runs == 0

    def test_multiple_runs_tracked(self):
        bot = _DummyBot()
        for _ in range(5):
            bot.run({"fail": False})
        bot.run({"fail": True})
        assert bot.self_evolution._total_runs == 6
        assert bot.self_evolution._successful_runs == 5

    def test_revenue_recorded_from_metrics(self):
        bot = _DummyBot()
        bot.run({"revenue": 50.0})
        assert bot.self_evolution._total_revenue == 50.0

    def test_evolve_returns_dict(self):
        bot = _DummyBot()
        result = bot.evolve()
        assert isinstance(result, dict)
        for key in ("cycle", "phase", "llm_provider", "fitness_improvement",
                    "strategy_delta", "metadata"):
            assert key in result

    def test_evolve_increments_cycle(self):
        bot = _DummyBot()
        bot.evolve()
        assert bot.self_evolution._evolution_cycle == 1

    def test_evolution_status_returns_dict(self):
        bot = _DummyBot()
        status = bot.evolution_status()
        assert isinstance(status, dict)
        assert status["bot_id"] == "dummy_bot"

    def test_set_llm_provider_updates_engine(self):
        bot = _DummyBot()
        bot.set_llm_provider(LLMProvider.OPENAI)
        assert bot.self_evolution.llm_provider == LLMProvider.OPENAI

    def test_bot_category_propagated_to_engine(self):
        bot = _DummyBot()
        assert bot.self_evolution.category == "ai"

    def test_bot_id_propagated_to_engine(self):
        bot = _DummyBot()
        assert bot.self_evolution.bot_id == "dummy_bot"

    def test_phase1_is_initial_phase(self):
        bot = _DummyBot()
        status = bot.evolution_status()
        assert status["phase"] == EvolutionPhase.PHASE_1_AI_OS.value


# ===========================================================================
# Category LLM map
# ===========================================================================

class TestCategoryLLMMap:
    def test_finance_maps_to_dreamco_finance(self):
        assert CATEGORY_LLM_MAP["finance"] == LLMProvider.DREAMCO_FINANCE

    def test_real_estate_maps_to_dreamco_real_estate(self):
        assert CATEGORY_LLM_MAP["real_estate"] == LLMProvider.DREAMCO_REAL_ESTATE

    def test_trading_maps_to_dreamco_trading(self):
        assert CATEGORY_LLM_MAP["trading"] == LLMProvider.DREAMCO_TRADING

    def test_coding_maps_to_dreamco_coding(self):
        assert CATEGORY_LLM_MAP["coding"] == LLMProvider.DREAMCO_CODING

    def test_all_values_are_llm_providers(self):
        for v in CATEGORY_LLM_MAP.values():
            assert isinstance(v, LLMProvider)
