"""
Tests for the DreamCo Quantum Decision Bot.

Covers:
  - SimulationEngine
  - ProbabilityModel
  - DimensionMapper
  - QuantumEngine
  - BotRouter
  - MoneyEngine
  - QuantumDecisionBot (tier-gating, all public methods)
  - Module-level run()
"""

from __future__ import annotations

import os
import sys

import pytest

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)


# ===========================================================================
# SimulationEngine
# ===========================================================================

class TestSimulationEngine:
    def test_returns_list(self):
        from bots.quantum_decision_bot.simulation_engine import run_simulations

        results = run_simulations({"base_profit": 1000, "risk": 5}, runs=10)
        assert isinstance(results, list)

    def test_correct_run_count(self):
        from bots.quantum_decision_bot.simulation_engine import run_simulations

        results = run_simulations({"base_profit": 1000, "risk": 5}, runs=20)
        assert len(results) == 20

    def test_outcome_has_required_keys(self):
        from bots.quantum_decision_bot.simulation_engine import run_simulations

        result = run_simulations({"base_profit": 500, "risk": 3}, runs=5)[0]
        assert "profit" in result
        assert "risk" in result
        assert "run_index" in result

    def test_minimum_runs_clamped_to_one(self):
        from bots.quantum_decision_bot.simulation_engine import run_simulations

        results = run_simulations({"base_profit": 100, "risk": 1}, runs=0)
        assert len(results) == 1

    def test_risk_always_non_negative(self):
        from bots.quantum_decision_bot.simulation_engine import run_simulations

        results = run_simulations({"base_profit": 100, "risk": 2, "volatility": 0.5}, runs=50)
        assert all(r["risk"] >= 0 for r in results)

    def test_summarise_outcomes_keys(self):
        from bots.quantum_decision_bot.simulation_engine import run_simulations, summarise_outcomes

        outcomes = run_simulations({"base_profit": 1000, "risk": 5}, runs=20)
        summary = summarise_outcomes(outcomes)
        for key in ("count", "avg_profit", "min_profit", "max_profit", "avg_risk",
                    "profitable_runs", "profitable_pct"):
            assert key in summary

    def test_summarise_empty_outcomes(self):
        from bots.quantum_decision_bot.simulation_engine import summarise_outcomes

        summary = summarise_outcomes([])
        assert summary["count"] == 0
        assert summary["avg_profit"] == 0.0

    def test_summarise_profitable_pct(self):
        from bots.quantum_decision_bot.simulation_engine import summarise_outcomes

        outcomes = [{"profit": 100, "risk": 2}, {"profit": -50, "risk": 8},
                    {"profit": 200, "risk": 3}, {"profit": 50, "risk": 4}]
        summary = summarise_outcomes(outcomes)
        assert summary["profitable_runs"] == 3
        assert summary["profitable_pct"] == 75.0

    def test_high_base_profit_raises_avg_profit(self):
        from bots.quantum_decision_bot.simulation_engine import run_simulations, summarise_outcomes

        outcomes_low = run_simulations({"base_profit": 100, "risk": 2}, runs=100)
        outcomes_high = run_simulations({"base_profit": 10_000, "risk": 2}, runs=100)
        assert summarise_outcomes(outcomes_high)["avg_profit"] > summarise_outcomes(outcomes_low)["avg_profit"]


# ===========================================================================
# ProbabilityModel
# ===========================================================================

class TestProbabilityModel:
    def test_score_returns_float(self):
        from bots.quantum_decision_bot.probability_model import ProbabilityModel

        model = ProbabilityModel()
        score = model.score_outcomes([{"profit": 100, "risk": 3}])
        assert isinstance(score, float)

    def test_score_empty_outcomes(self):
        from bots.quantum_decision_bot.probability_model import ProbabilityModel

        model = ProbabilityModel()
        assert model.score_outcomes([]) == 0.0

    def test_higher_profit_higher_score(self):
        from bots.quantum_decision_bot.probability_model import ProbabilityModel

        model = ProbabilityModel()
        low_score = model.score_outcomes([{"profit": 100, "risk": 2}])
        high_score = model.score_outcomes([{"profit": 10_000, "risk": 2}])
        assert high_score > low_score

    def test_higher_risk_lower_score(self):
        from bots.quantum_decision_bot.probability_model import ProbabilityModel

        model = ProbabilityModel()
        safe_score = model.score_outcomes([{"profit": 1000, "risk": 1}])
        risky_score = model.score_outcomes([{"profit": 1000, "risk": 9}])
        assert safe_score > risky_score

    def test_probability_of_profit_all_positive(self):
        from bots.quantum_decision_bot.probability_model import ProbabilityModel

        model = ProbabilityModel()
        outcomes = [{"profit": 100, "risk": 2}, {"profit": 200, "risk": 3}]
        assert model.probability_of_profit(outcomes) == 1.0

    def test_probability_of_profit_none_positive(self):
        from bots.quantum_decision_bot.probability_model import ProbabilityModel

        model = ProbabilityModel()
        outcomes = [{"profit": -10, "risk": 2}, {"profit": -5, "risk": 3}]
        assert model.probability_of_profit(outcomes) == 0.0

    def test_probability_of_profit_half(self):
        from bots.quantum_decision_bot.probability_model import ProbabilityModel

        model = ProbabilityModel()
        outcomes = [{"profit": 100, "risk": 2}, {"profit": -50, "risk": 8}]
        assert model.probability_of_profit(outcomes) == 0.5

    def test_learn_returns_dict(self):
        from bots.quantum_decision_bot.probability_model import ProbabilityModel

        model = ProbabilityModel()
        result = model.learn("test_scenario", 5000.0, 6000.0)
        assert isinstance(result, dict)
        assert "scenario" in result

    def test_learn_increments_history(self):
        from bots.quantum_decision_bot.probability_model import ProbabilityModel

        model = ProbabilityModel()
        assert model.get_history_count() == 0
        model.learn("s1", 1000.0, 1200.0)
        assert model.get_history_count() == 1

    def test_learn_adjusts_weights(self):
        from bots.quantum_decision_bot.probability_model import ProbabilityModel

        model = ProbabilityModel()
        original_profit_weight = model.profit_weight
        model.learn("s1", 1000.0, 5000.0)  # under-estimated → increase profit weight
        assert model.profit_weight > original_profit_weight

    def test_reset_weights(self):
        from bots.quantum_decision_bot.probability_model import ProbabilityModel

        model = ProbabilityModel()
        model.learn("s1", 1000.0, 5000.0)
        model.reset_weights()
        assert model.profit_weight == ProbabilityModel.DEFAULT_PROFIT_WEIGHT
        assert model.risk_weight == ProbabilityModel.DEFAULT_RISK_WEIGHT

    def test_get_weights_keys(self):
        from bots.quantum_decision_bot.probability_model import ProbabilityModel

        model = ProbabilityModel()
        weights = model.get_weights()
        assert "profit_weight" in weights
        assert "risk_weight" in weights


# ===========================================================================
# DimensionMapper
# ===========================================================================

class TestDimensionMapper:
    def test_map_returns_dict_with_keys(self):
        from bots.quantum_decision_bot.dimension_mapper import DimensionMapper

        mapper = DimensionMapper()
        profile = mapper.map({})
        for key in ("time", "capital", "risk", "scale"):
            assert key in profile

    def test_map_string_time_horizon(self):
        from bots.quantum_decision_bot.dimension_mapper import DimensionMapper

        mapper = DimensionMapper()
        p = mapper.map({"time_horizon": "short"})
        assert p["time"] == 3.0

    def test_map_numeric_time_horizon(self):
        from bots.quantum_decision_bot.dimension_mapper import DimensionMapper

        mapper = DimensionMapper()
        p = mapper.map({"time_horizon": 7.0})
        assert p["time"] == 7.0

    def test_map_budget_zero(self):
        from bots.quantum_decision_bot.dimension_mapper import DimensionMapper

        mapper = DimensionMapper()
        p = mapper.map({"budget": 0})
        assert p["capital"] == 0.0

    def test_map_budget_high(self):
        from bots.quantum_decision_bot.dimension_mapper import DimensionMapper

        mapper = DimensionMapper()
        p = mapper.map({"budget": 500_000})
        assert p["capital"] == 10.0

    def test_map_risk_string(self):
        from bots.quantum_decision_bot.dimension_mapper import DimensionMapper

        mapper = DimensionMapper()
        p = mapper.map({"risk_level": "extreme"})
        assert p["risk"] == 10.0

    def test_map_scale_string(self):
        from bots.quantum_decision_bot.dimension_mapper import DimensionMapper

        mapper = DimensionMapper()
        p = mapper.map({"scale_goal": "global"})
        assert p["scale"] == 10.0

    def test_optimality_score_returns_float(self):
        from bots.quantum_decision_bot.dimension_mapper import DimensionMapper

        mapper = DimensionMapper()
        profile = {"time": 5.0, "capital": 2.0, "risk": 3.0, "scale": 7.0}
        score = mapper.optimality_score(profile)
        assert isinstance(score, float)

    def test_optimality_score_range(self):
        from bots.quantum_decision_bot.dimension_mapper import DimensionMapper

        mapper = DimensionMapper()
        profile = {"time": 5.0, "capital": 0.0, "risk": 0.0, "scale": 10.0}
        score = mapper.optimality_score(profile)
        assert 0.0 <= score <= 100.0

    def test_optimal_profile_higher_than_bad_profile(self):
        from bots.quantum_decision_bot.dimension_mapper import DimensionMapper

        mapper = DimensionMapper()
        good = mapper.optimality_score({"time": 5.0, "capital": 0.0, "risk": 1.0, "scale": 10.0})
        bad = mapper.optimality_score({"time": 10.0, "capital": 10.0, "risk": 10.0, "scale": 1.0})
        assert good > bad

    def test_find_optimal_intersection_sorted(self):
        from bots.quantum_decision_bot.dimension_mapper import DimensionMapper

        mapper = DimensionMapper()
        paths = [
            {"profile": {"time": 9.0, "capital": 9.0, "risk": 9.0, "scale": 1.0}, "score": 100},
            {"profile": {"time": 5.0, "capital": 2.0, "risk": 3.0, "scale": 7.0}, "score": 80},
        ]
        result = mapper.find_optimal_intersection(paths)
        # Closer to ideal should come first
        assert result[0]["score"] == 80


# ===========================================================================
# QuantumEngine
# ===========================================================================

class TestQuantumEngine:
    def test_decide_returns_dict(self):
        from bots.quantum_decision_bot.quantum_engine import QuantumEngine

        engine = QuantumEngine(simulation_runs=5)
        result = engine.decide({"base_profit": 5000, "risk": 4.0})
        assert isinstance(result, dict)

    def test_decide_has_best_path(self):
        from bots.quantum_decision_bot.quantum_engine import QuantumEngine

        engine = QuantumEngine(simulation_runs=5)
        result = engine.decide({})
        assert "best_path" in result

    def test_decide_has_worst_case(self):
        from bots.quantum_decision_bot.quantum_engine import QuantumEngine

        engine = QuantumEngine(simulation_runs=5)
        result = engine.decide({})
        assert "worst_case" in result

    def test_decide_has_alternatives(self):
        from bots.quantum_decision_bot.quantum_engine import QuantumEngine

        engine = QuantumEngine(simulation_runs=5)
        result = engine.decide({})
        assert "alternatives" in result
        assert isinstance(result["alternatives"], list)

    def test_decide_best_path_score_gte_worst(self):
        from bots.quantum_decision_bot.quantum_engine import QuantumEngine

        engine = QuantumEngine(simulation_runs=10)
        result = engine.decide({"base_profit": 10_000, "risk": 5})
        assert result["best_path"]["score"] >= result["worst_case"]["score"]

    def test_decide_custom_scenarios(self):
        from bots.quantum_decision_bot.quantum_engine import QuantumEngine

        engine = QuantumEngine(simulation_runs=5)
        custom = [{"name": "test", "base_profit": 1000, "risk": 2, "volatility": 0.1}]
        result = engine.decide({"scenarios": custom})
        assert result["best_path"]["scenario"] == "test"

    def test_path_history_grows(self):
        from bots.quantum_decision_bot.quantum_engine import QuantumEngine

        engine = QuantumEngine(simulation_runs=5)
        engine.decide({})
        assert len(engine.get_path_history()) > 0

    def test_clear_history(self):
        from bots.quantum_decision_bot.quantum_engine import QuantumEngine

        engine = QuantumEngine(simulation_runs=5)
        engine.decide({})
        engine.clear_history()
        assert len(engine.get_path_history()) == 0

    def test_all_paths_in_result(self):
        from bots.quantum_decision_bot.quantum_engine import QuantumEngine

        engine = QuantumEngine(simulation_runs=5)
        result = engine.decide({})
        assert "all_paths" in result
        assert len(result["all_paths"]) == 3  # conservative/moderate/aggressive


# ===========================================================================
# BotRouter
# ===========================================================================

class TestBotRouter:
    def test_route_returns_dict(self):
        from bots.quantum_decision_bot.bot_router import BotRouter

        router = BotRouter()
        # Override engine with low-run engine for speed
        from bots.quantum_decision_bot.quantum_engine import QuantumEngine
        router.engine = QuantumEngine(simulation_runs=5)
        result = router.route("real_estate_bot", {"base_profit": 40_000, "risk": 7})
        assert isinstance(result, dict)

    def test_route_has_bot_name(self):
        from bots.quantum_decision_bot.bot_router import BotRouter
        from bots.quantum_decision_bot.quantum_engine import QuantumEngine

        router = BotRouter(engine=QuantumEngine(simulation_runs=5))
        result = router.route("trade_bot", {})
        assert result["bot"] == "trade_bot"

    def test_route_has_next_actions(self):
        from bots.quantum_decision_bot.bot_router import BotRouter
        from bots.quantum_decision_bot.quantum_engine import QuantumEngine

        router = BotRouter(engine=QuantumEngine(simulation_runs=5))
        result = router.route("hustle_bot", {})
        assert "next_actions" in result
        assert len(result["next_actions"]) > 0

    def test_route_unknown_bot_uses_default_actions(self):
        from bots.quantum_decision_bot.bot_router import BotRouter
        from bots.quantum_decision_bot.quantum_engine import QuantumEngine

        router = BotRouter(engine=QuantumEngine(simulation_runs=5))
        result = router.route("unknown_xyz_bot", {})
        assert len(result["next_actions"]) > 0

    def test_route_all(self):
        from bots.quantum_decision_bot.bot_router import BotRouter
        from bots.quantum_decision_bot.quantum_engine import QuantumEngine

        router = BotRouter(engine=QuantumEngine(simulation_runs=5))
        results = router.route_all({
            "real_estate_bot": {},
            "trade_bot": {},
        })
        assert len(results) == 2
        bots = {r["bot"] for r in results}
        assert "real_estate_bot" in bots
        assert "trade_bot" in bots

    def test_routing_log_grows(self):
        from bots.quantum_decision_bot.bot_router import BotRouter
        from bots.quantum_decision_bot.quantum_engine import QuantumEngine

        router = BotRouter(engine=QuantumEngine(simulation_runs=5))
        router.route("test_bot", {})
        assert len(router.get_routing_log()) == 1

    def test_network_status_keys(self):
        from bots.quantum_decision_bot.bot_router import BotRouter
        from bots.quantum_decision_bot.quantum_engine import QuantumEngine

        router = BotRouter(engine=QuantumEngine(simulation_runs=5))
        router.route("bot_a", {})
        router.route("bot_b", {})
        status = router.network_status()
        assert "total_routing_calls" in status
        assert "unique_bots" in status
        assert status["total_routing_calls"] == 2
        assert status["unique_bots"] == 2

    def test_network_status_empty(self):
        from bots.quantum_decision_bot.bot_router import BotRouter

        router = BotRouter()
        status = router.network_status()
        assert status["total_routing_calls"] == 0
        assert status["avg_decision_score"] == 0.0


# ===========================================================================
# MoneyEngine
# ===========================================================================

class TestMoneyEngine:
    def _fast_engine(self):
        from bots.quantum_decision_bot.quantum_engine import QuantumEngine
        return QuantumEngine(simulation_runs=5)

    def test_scan_returns_dict(self):
        from bots.quantum_decision_bot.money_engine import MoneyEngine

        engine = MoneyEngine(engine=self._fast_engine())
        result = engine.scan(top_n=3)
        assert isinstance(result, dict)

    def test_scan_has_ranked_opportunities(self):
        from bots.quantum_decision_bot.money_engine import MoneyEngine

        engine = MoneyEngine(engine=self._fast_engine())
        result = engine.scan(top_n=3)
        assert "ranked_opportunities" in result
        assert len(result["ranked_opportunities"]) <= 3

    def test_scan_has_top_opportunity(self):
        from bots.quantum_decision_bot.money_engine import MoneyEngine

        engine = MoneyEngine(engine=self._fast_engine())
        result = engine.scan()
        assert result["top_opportunity"] is not None

    def test_scan_ranked_by_score(self):
        from bots.quantum_decision_bot.money_engine import MoneyEngine

        engine = MoneyEngine(engine=self._fast_engine())
        result = engine.scan(top_n=5)
        scores = [o["quantum_score"] for o in result["ranked_opportunities"]]
        assert scores == sorted(scores, reverse=True)

    def test_scan_filter_by_type(self):
        from bots.quantum_decision_bot.money_engine import MoneyEngine

        engine = MoneyEngine(engine=self._fast_engine())
        result = engine.scan(filter_type="service", top_n=10)
        for opp in result["ranked_opportunities"]:
            assert opp["type"] == "service"

    def test_scan_total_scanned(self):
        from bots.quantum_decision_bot.money_engine import MoneyEngine

        engine = MoneyEngine(engine=self._fast_engine())
        result = engine.scan()
        assert result["total_scanned"] > 0

    def test_add_custom_opportunity(self):
        from bots.quantum_decision_bot.money_engine import MoneyEngine

        engine = MoneyEngine(engine=self._fast_engine())
        custom = {
            "id": "test_opp", "type": "service", "name": "Test Service",
            "description": "Test", "base_profit": 999, "risk": 2.0
        }
        engine.add_opportunity(custom)
        result = engine.scan(top_n=20)
        names = [o["name"] for o in result["ranked_opportunities"]]
        assert "Test Service" in names

    def test_execute_plan_returns_steps(self):
        from bots.quantum_decision_bot.money_engine import MoneyEngine

        engine = MoneyEngine(engine=self._fast_engine())
        opp = {"type": "service", "name": "Test", "base_profit": 1000, "risk": 3.0}
        plan = engine.execute_plan(opp)
        assert "execution_steps" in plan
        assert len(plan["execution_steps"]) > 0

    def test_execute_plan_all_types(self):
        from bots.quantum_decision_bot.money_engine import MoneyEngine

        engine = MoneyEngine(engine=self._fast_engine())
        for opp_type in ("service", "saas", "real_estate", "affiliate", "trading", "digital"):
            plan = engine.execute_plan({"type": opp_type, "name": "X", "base_profit": 1000, "risk": 3})
            assert plan["type"] == opp_type

    def test_probability_of_profit_in_opportunity(self):
        from bots.quantum_decision_bot.money_engine import MoneyEngine

        engine = MoneyEngine(engine=self._fast_engine())
        result = engine.scan(top_n=1)
        top = result["top_opportunity"]
        assert "probability_of_profit" in top
        assert 0.0 <= top["probability_of_profit"] <= 1.0


# ===========================================================================
# QuantumDecisionBot — Tier gating
# ===========================================================================

class TestQuantumDecisionBotTiers:
    def test_free_tier_decide(self):
        from bots.quantum_decision_bot.quantum_decision_bot import QuantumDecisionBot, Tier

        bot = QuantumDecisionBot(tier=Tier.FREE)
        bot.quantum_engine.simulation_runs = 5
        result = bot.decide({})
        assert "best_path" in result

    def test_free_tier_simulate(self):
        from bots.quantum_decision_bot.quantum_decision_bot import QuantumDecisionBot, Tier

        bot = QuantumDecisionBot(tier=Tier.FREE)
        result = bot.simulate({"base_profit": 1000, "risk": 3})
        assert "count" in result

    def test_free_tier_cannot_access_dimension_mapper(self):
        from bots.quantum_decision_bot.quantum_decision_bot import QuantumDecisionBot, Tier, QuantumTierError

        bot = QuantumDecisionBot(tier=Tier.FREE)
        with pytest.raises(QuantumTierError):
            bot.map_dimensions({})

    def test_free_tier_cannot_access_bot_router(self):
        from bots.quantum_decision_bot.quantum_decision_bot import QuantumDecisionBot, Tier, QuantumTierError

        bot = QuantumDecisionBot(tier=Tier.FREE)
        with pytest.raises(QuantumTierError):
            bot.route_bot("real_estate_bot", {})

    def test_free_tier_cannot_scan_opportunities(self):
        from bots.quantum_decision_bot.quantum_decision_bot import QuantumDecisionBot, Tier, QuantumTierError

        bot = QuantumDecisionBot(tier=Tier.FREE)
        with pytest.raises(QuantumTierError):
            bot.scan_opportunities()

    def test_pro_tier_can_access_dimension_mapper(self):
        from bots.quantum_decision_bot.quantum_decision_bot import QuantumDecisionBot, Tier

        bot = QuantumDecisionBot(tier=Tier.PRO)
        bot.quantum_engine.simulation_runs = 5
        result = bot.map_dimensions({"time_horizon": "medium", "risk_level": "moderate"})
        assert "dimensions" in result

    def test_pro_tier_can_route_bot(self):
        from bots.quantum_decision_bot.quantum_decision_bot import QuantumDecisionBot, Tier

        bot = QuantumDecisionBot(tier=Tier.PRO)
        bot.quantum_engine.simulation_runs = 5
        result = bot.route_bot("trade_bot", {})
        assert result["bot"] == "trade_bot"

    def test_pro_tier_can_scan_opportunities(self):
        from bots.quantum_decision_bot.quantum_decision_bot import QuantumDecisionBot, Tier

        bot = QuantumDecisionBot(tier=Tier.PRO)
        bot.quantum_engine.simulation_runs = 5
        result = bot.scan_opportunities(top_n=3)
        assert "ranked_opportunities" in result

    def test_pro_tier_cannot_learn(self):
        from bots.quantum_decision_bot.quantum_decision_bot import QuantumDecisionBot, Tier, QuantumTierError

        bot = QuantumDecisionBot(tier=Tier.PRO)
        with pytest.raises(QuantumTierError):
            bot.learn("test", 1000.0, 1200.0)

    def test_enterprise_tier_can_learn(self):
        from bots.quantum_decision_bot.quantum_decision_bot import QuantumDecisionBot, Tier

        bot = QuantumDecisionBot(tier=Tier.ENTERPRISE)
        bot.quantum_engine.simulation_runs = 5
        result = bot.learn("test_scenario", 1000.0, 1500.0)
        assert "scenario" in result

    def test_enterprise_tier_get_model_weights(self):
        from bots.quantum_decision_bot.quantum_decision_bot import QuantumDecisionBot, Tier

        bot = QuantumDecisionBot(tier=Tier.ENTERPRISE)
        weights = bot.get_model_weights()
        assert "profit_weight" in weights


# ===========================================================================
# QuantumDecisionBot — Active paths
# ===========================================================================

class TestQuantumDecisionBotActivePaths:
    def test_free_tier_no_active_paths(self):
        from bots.quantum_decision_bot.quantum_decision_bot import QuantumDecisionBot, Tier, QuantumTierError

        bot = QuantumDecisionBot(tier=Tier.FREE)
        with pytest.raises(QuantumTierError):
            bot.get_active_paths()

    def test_pro_tier_active_paths_grow(self):
        from bots.quantum_decision_bot.quantum_decision_bot import QuantumDecisionBot, Tier

        bot = QuantumDecisionBot(tier=Tier.PRO)
        bot.quantum_engine.simulation_runs = 5
        bot.decide({})
        bot.decide({})
        paths = bot.get_active_paths()
        assert len(paths) == 2

    def test_active_paths_capped_at_max(self):
        from bots.quantum_decision_bot.quantum_decision_bot import QuantumDecisionBot, Tier

        bot = QuantumDecisionBot(tier=Tier.PRO)
        bot.quantum_engine.simulation_runs = 5
        max_paths = bot._config.max_active_paths
        for _ in range(max_paths + 5):
            bot.decide({})
        assert len(bot.get_active_paths()) <= max_paths


# ===========================================================================
# QuantumDecisionBot — Dashboard
# ===========================================================================

class TestQuantumDecisionBotDashboard:
    def test_dashboard_returns_dict(self):
        from bots.quantum_decision_bot.quantum_decision_bot import QuantumDecisionBot, Tier

        bot = QuantumDecisionBot(tier=Tier.FREE)
        result = bot.dashboard()
        assert isinstance(result, dict)

    def test_dashboard_has_title(self):
        from bots.quantum_decision_bot.quantum_decision_bot import QuantumDecisionBot, Tier

        bot = QuantumDecisionBot(tier=Tier.FREE)
        assert bot.dashboard()["title"] == "DreamCo QuantumOS"

    def test_dashboard_reflects_tier(self):
        from bots.quantum_decision_bot.quantum_decision_bot import QuantumDecisionBot, Tier

        bot = QuantumDecisionBot(tier=Tier.PRO)
        assert bot.dashboard()["tier"] == "pro"

    def test_dashboard_has_model_weights(self):
        from bots.quantum_decision_bot.quantum_decision_bot import QuantumDecisionBot, Tier

        bot = QuantumDecisionBot(tier=Tier.FREE)
        assert "model_weights" in bot.dashboard()

    def test_dashboard_paths_evaluated_increases(self):
        from bots.quantum_decision_bot.quantum_decision_bot import QuantumDecisionBot, Tier

        bot = QuantumDecisionBot(tier=Tier.FREE)
        bot.quantum_engine.simulation_runs = 5
        before = bot.dashboard()["paths_evaluated"]
        bot.decide({})
        after = bot.dashboard()["paths_evaluated"]
        assert after > before


# ===========================================================================
# QuantumDecisionBot — Chat interface
# ===========================================================================

class TestQuantumDecisionBotChat:
    def test_chat_default_response(self):
        from bots.quantum_decision_bot.quantum_decision_bot import QuantumDecisionBot, Tier

        bot = QuantumDecisionBot(tier=Tier.FREE)
        result = bot.chat("hello")
        assert "message" in result

    def test_chat_dashboard_command(self):
        from bots.quantum_decision_bot.quantum_decision_bot import QuantumDecisionBot, Tier

        bot = QuantumDecisionBot(tier=Tier.FREE)
        result = bot.chat("show dashboard")
        assert "data" in result

    def test_chat_tier_command(self):
        from bots.quantum_decision_bot.quantum_decision_bot import QuantumDecisionBot, Tier

        bot = QuantumDecisionBot(tier=Tier.PRO)
        result = bot.chat("what is my tier plan")
        assert "data" in result

    def test_chat_opportunities_pro_tier(self):
        from bots.quantum_decision_bot.quantum_decision_bot import QuantumDecisionBot, Tier

        bot = QuantumDecisionBot(tier=Tier.PRO)
        bot.quantum_engine.simulation_runs = 5
        result = bot.chat("scan for money opportunities")
        assert "data" in result

    def test_chat_opportunities_free_tier_blocked(self):
        from bots.quantum_decision_bot.quantum_decision_bot import QuantumDecisionBot, Tier

        bot = QuantumDecisionBot(tier=Tier.FREE)
        result = bot.chat("scan for money opportunities")
        assert "message" in result
        assert "not available" in result["message"].lower()

    def test_process_delegates_to_chat(self):
        from bots.quantum_decision_bot.quantum_decision_bot import QuantumDecisionBot, Tier

        bot = QuantumDecisionBot(tier=Tier.FREE)
        result = bot.process({"command": "status"})
        assert "data" in result


# ===========================================================================
# QuantumDecisionBot — Tier info
# ===========================================================================

class TestQuantumDecisionBotTierInfo:
    def test_free_tier_info(self):
        from bots.quantum_decision_bot.quantum_decision_bot import QuantumDecisionBot, Tier

        bot = QuantumDecisionBot(tier=Tier.FREE)
        info = bot.get_tier_info()
        assert info["tier"] == "free"
        assert info["price_usd_monthly"] == 0.0

    def test_pro_tier_info(self):
        from bots.quantum_decision_bot.quantum_decision_bot import QuantumDecisionBot, Tier

        bot = QuantumDecisionBot(tier=Tier.PRO)
        info = bot.get_tier_info()
        assert info["tier"] == "pro"
        assert info["price_usd_monthly"] == 49.0

    def test_enterprise_tier_info(self):
        from bots.quantum_decision_bot.quantum_decision_bot import QuantumDecisionBot, Tier

        bot = QuantumDecisionBot(tier=Tier.ENTERPRISE)
        info = bot.get_tier_info()
        assert info["tier"] == "enterprise"
        assert info["price_usd_monthly"] == 199.0

    def test_can_access_returns_bool(self):
        from bots.quantum_decision_bot.quantum_decision_bot import QuantumDecisionBot, Tier

        bot = QuantumDecisionBot(tier=Tier.FREE)
        assert bot.can_access("simulation") is True
        assert bot.can_access("god_mode") is False


# ===========================================================================
# QuantumDecisionBot — route_all_bots & network_status
# ===========================================================================

class TestQuantumDecisionBotNetwork:
    def test_route_all_bots(self):
        from bots.quantum_decision_bot.quantum_decision_bot import QuantumDecisionBot, Tier

        bot = QuantumDecisionBot(tier=Tier.PRO)
        bot.quantum_engine.simulation_runs = 5
        results = bot.route_all_bots({
            "real_estate_bot": {},
            "trade_bot": {},
            "hustle_bot": {},
        })
        assert len(results) == 3

    def test_network_status_returns_dict(self):
        from bots.quantum_decision_bot.quantum_decision_bot import QuantumDecisionBot, Tier

        bot = QuantumDecisionBot(tier=Tier.PRO)
        bot.quantum_engine.simulation_runs = 5
        bot.route_bot("real_estate_bot", {})
        status = bot.network_status()
        assert "total_routing_calls" in status


# ===========================================================================
# Module-level run()
# ===========================================================================

class TestModuleLevelRun:
    def test_run_returns_dict(self):
        from bots.quantum_decision_bot.quantum_decision_bot import run

        result = run()
        assert isinstance(result, dict)

    def test_run_status_success(self):
        from bots.quantum_decision_bot.quantum_decision_bot import run

        assert run()["status"] == "success"

    def test_run_has_leads(self):
        from bots.quantum_decision_bot.quantum_decision_bot import run

        result = run()
        assert "leads" in result
        assert result["leads"] > 0

    def test_run_has_revenue(self):
        from bots.quantum_decision_bot.quantum_decision_bot import run

        result = run()
        assert "revenue" in result
        assert isinstance(result["revenue"], int)

    def test_run_has_quantum_score(self):
        from bots.quantum_decision_bot.quantum_decision_bot import run

        result = run()
        assert "quantum_score" in result

    def test_run_has_ranked_opportunities(self):
        from bots.quantum_decision_bot.quantum_decision_bot import run

        result = run()
        assert "ranked_opportunities" in result
        assert isinstance(result["ranked_opportunities"], list)


# ===========================================================================
# BotLibrary registration
# ===========================================================================

class TestBotLibraryRegistration:
    def test_quantum_bot_in_library(self):
        from bots.global_bot_network.bot_library import BotLibrary

        lib = BotLibrary()
        lib.populate_dreamco_bots()
        entry = lib.get_bot("quantum_decision_bot")
        assert entry.display_name == "Quantum Decision Bot"

    def test_quantum_bot_capabilities(self):
        from bots.global_bot_network.bot_library import BotLibrary

        lib = BotLibrary()
        lib.populate_dreamco_bots()
        entry = lib.get_bot("quantum_decision_bot")
        assert "quantum_decision_engine" in entry.capabilities
        assert "monte_carlo_simulation" in entry.capabilities
        assert "entangled_bot_router" in entry.capabilities

    def test_quantum_bot_category(self):
        from bots.global_bot_network.bot_library import BotLibrary, BotCategory

        lib = BotLibrary()
        lib.populate_dreamco_bots()
        entry = lib.get_bot("quantum_decision_bot")
        assert entry.category == BotCategory.AI
