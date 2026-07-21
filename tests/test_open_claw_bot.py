"""
Tests for bots/open_claw_bot/

Covers:
  1. Tiers
  2. Strategy Engine
  3. AI Model Hub
  4. Client Manager
  5. OpenClawBot main class (integration + chat)
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------
from bots.open_claw_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
    TIER_CATALOGUE,
    FEATURE_STRATEGY_ENGINE,
    FEATURE_AI_MODELS,
    FEATURE_CLIENT_MANAGER,
    FEATURE_CUSTOM_RULES,
    FEATURE_ML_ENSEMBLE,
    FEATURE_SCENARIO_SIM,
    FEATURE_REALTIME_SIGNALS,
    FEATURE_WHITE_LABEL,
)
from bots.open_claw_bot.strategy_engine import (
    StrategyEngine,
    Strategy,
    StrategyType,
    StrategyStatus,
    RiskLevel,
    DataPoint,
    STRATEGY_RULE_TEMPLATES,
)
from bots.open_claw_bot.ai_models import (
    AIModelHub,
    AIModel,
    ModelFamily,
    InferenceResult,
    DEFAULT_MODELS,
)
from bots.open_claw_bot.client_manager import (
    ClientManager,
    ClientProfile,
    ClientPreferences,
    ClientStatus,
    GoalType,
)
from bots.open_claw_bot.open_claw_bot import OpenClawBot, OpenClawBotError, OpenClawBotTierError


# ===========================================================================
# 1. Tiers
# ===========================================================================

class TestTiers:
    def test_three_tiers_exist(self):
        assert len(list_tiers()) == 3

    def test_free_tier_price(self):
        assert get_tier_config(Tier.FREE).price_usd_monthly == 0.0

    def test_pro_tier_price(self):
        assert get_tier_config(Tier.PRO).price_usd_monthly == 49.0

    def test_enterprise_tier_price(self):
        assert get_tier_config(Tier.ENTERPRISE).price_usd_monthly == 199.0

    def test_enterprise_unlimited_clients(self):
        assert get_tier_config(Tier.ENTERPRISE).is_unlimited_clients()

    def test_free_limited_clients(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.max_clients is not None
        assert cfg.max_clients > 0

    def test_upgrade_path_free_to_pro(self):
        upgrade = get_upgrade_path(Tier.FREE)
        assert upgrade is not None
        assert upgrade.tier == Tier.PRO

    def test_no_upgrade_from_enterprise(self):
        assert get_upgrade_path(Tier.ENTERPRISE) is None

    def test_free_has_strategy_engine(self):
        assert FEATURE_STRATEGY_ENGINE in get_tier_config(Tier.FREE).features

    def test_pro_has_ai_models(self):
        assert FEATURE_AI_MODELS in get_tier_config(Tier.PRO).features

    def test_enterprise_has_white_label(self):
        assert FEATURE_WHITE_LABEL in get_tier_config(Tier.ENTERPRISE).features

    def test_has_feature_method(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.has_feature(FEATURE_STRATEGY_ENGINE)
        assert not cfg.has_feature(FEATURE_WHITE_LABEL)


# ===========================================================================
# 2. Strategy Engine
# ===========================================================================

class TestStrategyEngine:
    def test_generate_balanced_strategy(self):
        engine = StrategyEngine()
        strat = engine.generate_strategy(
            "Test", StrategyType.BALANCED, RiskLevel.MEDIUM
        )
        assert strat.strategy_id.startswith("strat_")
        assert strat.strategy_type == StrategyType.BALANCED

    def test_generate_aggressive_strategy(self):
        engine = StrategyEngine()
        strat = engine.generate_strategy(
            "Aggressive", StrategyType.AGGRESSIVE, RiskLevel.HIGH
        )
        assert strat.risk_level == RiskLevel.HIGH

    def test_strategy_has_rules(self):
        engine = StrategyEngine()
        strat = engine.generate_strategy("S", StrategyType.SCALPING, RiskLevel.MEDIUM)
        assert len(strat.rules) > 0

    def test_expected_roi_positive(self):
        engine = StrategyEngine()
        strat = engine.generate_strategy("S", StrategyType.CONSERVATIVE, RiskLevel.LOW)
        assert strat.expected_roi_pct > 0

    def test_confidence_between_zero_and_one(self):
        engine = StrategyEngine()
        for stype in StrategyType:
            strat = engine.generate_strategy("S", stype, RiskLevel.MEDIUM)
            assert 0.0 <= strat.confidence_score <= 1.0

    def test_ingest_data(self):
        engine = StrategyEngine()
        dp = DataPoint(timestamp="2024-01-01", metric="price", value=100.0)
        engine.ingest_data(dp)
        stats = engine.get_buffer_stats()
        assert stats["count"] == 1

    def test_ingest_batch(self):
        engine = StrategyEngine()
        dps = [DataPoint("t1", "price", float(v)) for v in range(10)]
        count = engine.ingest_batch(dps)
        assert count == 10
        assert engine.get_buffer_stats()["count"] == 10

    def test_buffer_stats_stdev(self):
        engine = StrategyEngine()
        engine.ingest_batch([DataPoint("t", "p", float(v)) for v in range(5)])
        stats = engine.get_buffer_stats()
        assert "stdev" in stats
        assert stats["stdev"] >= 0

    def test_clear_buffer(self):
        engine = StrategyEngine()
        engine.ingest_data(DataPoint("t", "p", 1.0))
        engine.clear_buffer()
        assert engine.get_buffer_stats()["count"] == 0

    def test_rank_strategies_by_value(self):
        engine = StrategyEngine()
        engine.generate_strategy("A", StrategyType.CONSERVATIVE, RiskLevel.LOW)
        engine.generate_strategy("B", StrategyType.AGGRESSIVE, RiskLevel.HIGH)
        ranked = engine.rank_strategies()
        assert len(ranked) == 2
        assert (ranked[0].confidence_score * ranked[0].expected_roi_pct >=
                ranked[1].confidence_score * ranked[1].expected_roi_pct)

    def test_rank_filtered_by_client(self):
        engine = StrategyEngine()
        engine.generate_strategy("A", StrategyType.BALANCED, client_id="c1")
        engine.generate_strategy("B", StrategyType.BALANCED, client_id="c2")
        result = engine.rank_strategies(client_id="c1")
        assert len(result) == 1

    def test_activate_strategy(self):
        engine = StrategyEngine()
        strat = engine.generate_strategy("S", StrategyType.BALANCED)
        engine.activate_strategy(strat.strategy_id)
        assert engine.get_strategy(strat.strategy_id).status == StrategyStatus.ACTIVE

    def test_pause_strategy(self):
        engine = StrategyEngine()
        strat = engine.generate_strategy("S", StrategyType.BALANCED)
        engine.activate_strategy(strat.strategy_id)
        engine.pause_strategy(strat.strategy_id)
        assert engine.get_strategy(strat.strategy_id).status == StrategyStatus.PAUSED

    def test_complete_strategy(self):
        engine = StrategyEngine()
        strat = engine.generate_strategy("S", StrategyType.BALANCED)
        engine.complete_strategy(strat.strategy_id, actual_roi_pct=12.5)
        s = engine.get_strategy(strat.strategy_id)
        assert s.status == StrategyStatus.COMPLETED
        assert s.performance_history[0]["actual_roi_pct"] == 12.5

    def test_archive_strategy(self):
        engine = StrategyEngine()
        strat = engine.generate_strategy("S", StrategyType.BALANCED)
        engine.archive_strategy(strat.strategy_id)
        assert engine.get_strategy(strat.strategy_id).status == StrategyStatus.ARCHIVED

    def test_list_strategies_by_status(self):
        engine = StrategyEngine()
        s1 = engine.generate_strategy("S1", StrategyType.BALANCED)
        s2 = engine.generate_strategy("S2", StrategyType.AGGRESSIVE)
        engine.activate_strategy(s1.strategy_id)
        active = engine.list_strategies(status=StrategyStatus.ACTIVE)
        assert len(active) == 1

    def test_simulate_scenario(self):
        engine = StrategyEngine()
        strat = engine.generate_strategy("S", StrategyType.MOMENTUM)
        sim = engine.simulate_scenario(strat.strategy_id, {"volatility": 0.2, "trend": 0.05})
        assert "simulated_roi_pct" in sim
        assert "win_rate" in sim
        assert "max_drawdown_pct" in sim

    def test_strategy_not_found_raises(self):
        engine = StrategyEngine()
        with pytest.raises(KeyError):
            engine.get_strategy("strat_9999")

    def test_custom_rules_prepended(self):
        engine = StrategyEngine()
        custom = [{"rule": "custom_rule_test", "value": 99}]
        strat = engine.generate_strategy("S", StrategyType.BALANCED, custom_rules=custom)
        assert strat.rules[0] == custom[0]

    def test_strategy_to_dict(self):
        engine = StrategyEngine()
        strat = engine.generate_strategy("S", StrategyType.BALANCED)
        d = strat.to_dict()
        assert d["name"] == "S"
        assert "strategy_id" in d


# ===========================================================================
# 3. AI Model Hub
# ===========================================================================

class TestAIModelHub:
    def test_default_models_loaded(self):
        hub = AIModelHub(load_defaults=True)
        models = hub.list_models()
        assert len(models) == len(DEFAULT_MODELS)

    def test_all_default_models_ready(self):
        hub = AIModelHub(load_defaults=True)
        ready = hub.list_models(ready_only=True)
        assert len(ready) == len(DEFAULT_MODELS)

    def test_register_custom_model(self):
        hub = AIModelHub(load_defaults=False)
        model = hub.register_model("MyModel", ModelFamily.SIGNAL_GENERATOR, accuracy=0.90)
        assert model.name == "MyModel"
        assert model.is_ready()

    def test_predict_trend_up(self):
        hub = AIModelHub()
        result = hub.predict_trend([100.0, 105.0, 110.0])
        assert result.prediction["direction"] == "up"

    def test_predict_trend_down(self):
        hub = AIModelHub()
        result = hub.predict_trend([110.0, 105.0, 100.0])
        assert result.prediction["direction"] == "down"

    def test_predict_trend_neutral(self):
        hub = AIModelHub()
        result = hub.predict_trend([100.0, 100.0])
        assert result.prediction["direction"] == "neutral"

    def test_classify_risk_low(self):
        hub = AIModelHub()
        result = hub.classify_risk({"volatility": 0.05, "leverage": 1.0, "exposure_pct": 5.0})
        assert result.prediction["risk_level"] == "low"

    def test_classify_risk_high(self):
        hub = AIModelHub()
        result = hub.classify_risk({"volatility": 0.8, "leverage": 8.0, "exposure_pct": 60.0})
        assert result.prediction["risk_level"] in ("high", "extreme")

    def test_generate_signals_buy(self):
        hub = AIModelHub()
        result = hub.generate_signals({"price": 115, "moving_avg": 100, "rsi": 60})
        assert result.prediction["signal"] == "buy"

    def test_generate_signals_sell(self):
        hub = AIModelHub()
        result = hub.generate_signals({"price": 90, "moving_avg": 100, "rsi": 40})
        assert result.prediction["signal"] == "sell"

    def test_generate_signals_hold(self):
        hub = AIModelHub()
        result = hub.generate_signals({"price": 100, "moving_avg": 100, "rsi": 50})
        assert result.prediction["signal"] == "hold"

    def test_rank_strategies_ml(self):
        hub = AIModelHub()
        scores = [
            {"strategy_id": "s1", "confidence_score": 0.9, "expected_roi_pct": 10.0},
            {"strategy_id": "s2", "confidence_score": 0.7, "expected_roi_pct": 20.0},
        ]
        result = hub.rank_strategies_ml(scores)
        ranked = result.prediction["ranked_strategies"]
        assert ranked[0]["strategy_id"] in ("s1", "s2")

    def test_nlp_advise_conservative(self):
        hub = AIModelHub()
        result = hub.advise_nlp("I want a safe low risk strategy")
        assert result.prediction["recommended_strategy_type"] == "conservative"

    def test_nlp_advise_aggressive(self):
        hub = AIModelHub()
        result = hub.advise_nlp("I want a fast aggressive high return strategy")
        assert result.prediction["recommended_strategy_type"] == "aggressive"

    def test_nlp_advise_scalping(self):
        hub = AIModelHub()
        result = hub.advise_nlp("I want to scalp quick trades")
        assert result.prediction["recommended_strategy_type"] == "scalping"

    def test_nlp_advise_default_balanced(self):
        hub = AIModelHub()
        result = hub.advise_nlp("I want to trade")
        assert result.prediction["recommended_strategy_type"] == "balanced"

    def test_deprecate_model(self):
        hub = AIModelHub()
        model = hub.register_model("Old", ModelFamily.TREND_PREDICTOR)
        hub.deprecate_model(model.model_id)
        from bots.open_claw_bot.ai_models import ModelStatus
        assert hub.get_model(model.model_id).status == ModelStatus.DEPRECATED

    def test_model_not_found_raises(self):
        hub = AIModelHub()
        with pytest.raises(KeyError):
            hub.get_model("model_9999")

    def test_no_ready_model_raises(self):
        hub = AIModelHub(load_defaults=False)
        with pytest.raises(RuntimeError, match="No ready model"):
            hub.predict_trend([1.0, 2.0])

    def test_inference_result_to_dict(self):
        hub = AIModelHub()
        result = hub.predict_trend([100.0, 110.0])
        d = result.to_dict()
        assert "prediction" in d
        assert "confidence" in d

    def test_list_models_by_family(self):
        hub = AIModelHub()
        trend_models = hub.list_models(family=ModelFamily.TREND_PREDICTOR)
        for m in trend_models:
            assert m.family == ModelFamily.TREND_PREDICTOR


# ===========================================================================
# 4. Client Manager
# ===========================================================================

class TestClientManager:
    def test_add_client(self):
        mgr = ClientManager()
        client = mgr.add_client("Alice", "alice@example.com")
        assert client.name == "Alice"
        assert client.is_active()

    def test_get_client(self):
        mgr = ClientManager()
        c = mgr.add_client("Bob", "bob@example.com")
        fetched = mgr.get_client(c.client_id)
        assert fetched.name == "Bob"

    def test_client_limit(self):
        mgr = ClientManager(max_clients=2)
        mgr.add_client("A", "a@x.com")
        mgr.add_client("B", "b@x.com")
        with pytest.raises(RuntimeError, match="limit"):
            mgr.add_client("C", "c@x.com")

    def test_remove_client(self):
        mgr = ClientManager()
        c = mgr.add_client("Alice", "alice@x.com")
        mgr.remove_client(c.client_id)
        assert len(mgr.list_clients()) == 0

    def test_update_preferences(self):
        mgr = ClientManager()
        c = mgr.add_client("Alice", "alice@x.com")
        prefs = ClientPreferences(max_risk_pct=10.0)
        mgr.update_preferences(c.client_id, prefs)
        assert mgr.get_client(c.client_id).preferences.max_risk_pct == 10.0

    def test_set_status_inactive(self):
        mgr = ClientManager()
        c = mgr.add_client("Alice", "alice@x.com")
        mgr.set_status(c.client_id, ClientStatus.INACTIVE)
        assert not mgr.get_client(c.client_id).is_active()

    def test_assign_strategy(self):
        mgr = ClientManager()
        c = mgr.add_client("Alice", "alice@x.com")
        mgr.assign_strategy(c.client_id, "strat_0001")
        assert "strat_0001" in mgr.get_client(c.client_id).strategy_ids

    def test_assign_strategy_no_duplicate(self):
        mgr = ClientManager()
        c = mgr.add_client("Alice", "alice@x.com")
        mgr.assign_strategy(c.client_id, "strat_0001")
        mgr.assign_strategy(c.client_id, "strat_0001")
        assert mgr.get_client(c.client_id).strategy_ids.count("strat_0001") == 1

    def test_remove_strategy(self):
        mgr = ClientManager()
        c = mgr.add_client("Alice", "alice@x.com")
        mgr.assign_strategy(c.client_id, "strat_0001")
        mgr.remove_strategy(c.client_id, "strat_0001")
        assert "strat_0001" not in mgr.get_client(c.client_id).strategy_ids

    def test_record_roi(self):
        mgr = ClientManager()
        c = mgr.add_client("Alice", "alice@x.com")
        mgr.record_roi(c.client_id, 5.0)
        mgr.record_roi(c.client_id, 3.5)
        assert mgr.get_client(c.client_id).total_roi_pct == 8.5

    def test_list_clients_by_status(self):
        mgr = ClientManager()
        c1 = mgr.add_client("A", "a@x.com")
        c2 = mgr.add_client("B", "b@x.com")
        mgr.set_status(c2.client_id, ClientStatus.INACTIVE)
        active = mgr.list_clients(status=ClientStatus.ACTIVE)
        assert len(active) == 1

    def test_find_clients_by_name(self):
        mgr = ClientManager()
        mgr.add_client("Alice Smith", "alice@x.com")
        mgr.add_client("Bob Jones", "bob@x.com")
        results = mgr.find_clients_by_name("alice")
        assert len(results) == 1

    def test_get_top_clients(self):
        mgr = ClientManager()
        c1 = mgr.add_client("A", "a@x.com")
        c2 = mgr.add_client("B", "b@x.com")
        mgr.record_roi(c1.client_id, 20.0)
        mgr.record_roi(c2.client_id, 5.0)
        top = mgr.get_top_clients(n=1)
        assert top[0].client_id == c1.client_id

    def test_client_not_found_raises(self):
        mgr = ClientManager()
        with pytest.raises(KeyError):
            mgr.get_client("client_9999")

    def test_client_to_dict(self):
        mgr = ClientManager()
        c = mgr.add_client("Alice", "alice@x.com")
        d = c.to_dict()
        assert d["name"] == "Alice"
        assert "status" in d


# ===========================================================================
# 5. OpenClawBot (integration)
# ===========================================================================

class TestOpenClawBot:
    def test_instantiation_free_tier(self):
        bot = OpenClawBot(tier=Tier.FREE)
        assert bot.tier == Tier.FREE

    def test_instantiation_pro_tier(self):
        bot = OpenClawBot(tier=Tier.PRO)
        assert bot.config.price_usd_monthly == 49.0

    def test_dashboard_keys(self):
        bot = OpenClawBot(tier=Tier.PRO)
        dash = bot.dashboard()
        for key in ("tier", "total_strategies", "active_strategies",
                    "total_clients", "ai_models_ready"):
            assert key in dash

    def test_add_client(self):
        bot = OpenClawBot(tier=Tier.PRO)
        client = bot.add_client("Alice", "alice@example.com")
        assert client.name == "Alice"

    def test_generate_strategy_balanced(self):
        bot = OpenClawBot(tier=Tier.PRO)
        strat = bot.generate_strategy("Test", strategy_type="balanced")
        assert strat.strategy_type == StrategyType.BALANCED

    def test_generate_strategy_for_client(self):
        bot = OpenClawBot(tier=Tier.PRO)
        client = bot.add_client("Bob", "bob@x.com")
        strat = bot.generate_strategy("Bob Strat", client_id=client.client_id)
        assert strat.client_id == client.client_id
        assert strat.strategy_id in bot.client_manager.get_client(client.client_id).strategy_ids

    def test_generate_all_strategy_types(self):
        bot = OpenClawBot(tier=Tier.PRO)
        for alias in ("aggressive", "balanced", "conservative", "scalping",
                      "arbitrage", "momentum"):
            strat = bot.generate_strategy(f"Test {alias}", strategy_type=alias)
            assert strat is not None

    def test_custom_rules_require_pro(self):
        bot = OpenClawBot(tier=Tier.FREE)
        with pytest.raises(OpenClawBotTierError):
            bot.generate_strategy("Test", custom_rules=[{"rule": "custom"}])

    def test_rank_strategies(self):
        bot = OpenClawBot(tier=Tier.PRO)
        bot.generate_strategy("A", "aggressive")
        bot.generate_strategy("B", "conservative")
        ranked = bot.rank_strategies()
        assert len(ranked) == 2

    def test_rank_strategies_ml(self):
        bot = OpenClawBot(tier=Tier.PRO)
        bot.generate_strategy("A", "aggressive")
        bot.generate_strategy("B", "conservative")
        ranked = bot.rank_strategies(use_ml=True)
        assert len(ranked) == 2

    def test_analyse_trend(self):
        bot = OpenClawBot(tier=Tier.PRO)
        result = bot.analyse_trend([100.0, 110.0, 120.0])
        assert result.prediction["direction"] == "up"

    def test_assess_risk(self):
        bot = OpenClawBot(tier=Tier.PRO)
        result = bot.assess_risk({"volatility": 0.1, "leverage": 1.0, "exposure_pct": 5.0})
        assert "risk_level" in result.prediction

    def test_get_signals(self):
        bot = OpenClawBot(tier=Tier.PRO)
        result = bot.get_signals({"price": 110, "moving_avg": 100, "rsi": 55})
        assert "signal" in result.prediction

    def test_nlp_advise(self):
        bot = OpenClawBot(tier=Tier.PRO)
        result = bot.nlp_advise("I want a safe strategy")
        assert "recommended_strategy_type" in result.prediction

    def test_simulate_scenario(self):
        bot = OpenClawBot(tier=Tier.PRO)
        strat = bot.generate_strategy("Sim", "momentum")
        sim = bot.simulate_scenario(strat.strategy_id, {"volatility": 0.2, "trend": 0.1})
        assert "simulated_roi_pct" in sim

    def test_ingest_data(self):
        bot = OpenClawBot(tier=Tier.PRO)
        bot.ingest_data("price", 100.0, source="market_feed")
        stats = bot.get_data_stats()
        assert stats["count"] == 1

    def test_describe_tier(self):
        bot = OpenClawBot(tier=Tier.FREE)
        desc = bot.describe_tier()
        assert "Free" in desc

    def test_tier_error_free_feature_blocked(self):
        bot = OpenClawBot(tier=Tier.FREE)
        with pytest.raises(OpenClawBotTierError):
            bot._require_feature(FEATURE_WHITE_LABEL)

    def test_chat_aggressive_generates_strategy(self):
        bot = OpenClawBot(tier=Tier.PRO)
        resp = bot.chat("generate an aggressive strategy")
        assert resp["response"] == "open_claw"
        assert "strategy_id" in resp["data"]

    def test_chat_dashboard(self):
        bot = OpenClawBot(tier=Tier.PRO)
        resp = bot.chat("dashboard overview")
        assert "total_strategies" in resp["data"]

    def test_chat_clients(self):
        bot = OpenClawBot(tier=Tier.PRO)
        bot.add_client("Alice", "a@x.com")
        resp = bot.chat("list clients")
        assert "clients" in resp["data"]

    def test_chat_models(self):
        bot = OpenClawBot(tier=Tier.PRO)
        resp = bot.chat("show ai models")
        assert "models" in resp["data"]

    def test_chat_rank(self):
        bot = OpenClawBot(tier=Tier.PRO)
        bot.generate_strategy("A", "balanced")
        resp = bot.chat("rank best strategies")
        assert "strategies" in resp["data"]

    def test_chat_tier(self):
        bot = OpenClawBot(tier=Tier.FREE)
        resp = bot.chat("upgrade plan")
        assert "Open Claw Bot" in resp["message"]

    def test_chat_default_nlp(self):
        bot = OpenClawBot(tier=Tier.PRO)
        resp = bot.chat("what should I do with my portfolio?")
        assert resp["response"] == "open_claw"

    def test_register_with_buddy(self):
        from BuddyAI.buddy_bot import BuddyBot
        orchestrator = BuddyBot()
        bot = OpenClawBot(tier=Tier.PRO)
        bot.register_with_buddy(orchestrator)
        assert "open_claw" in orchestrator.list_bots()

    def test_route_via_buddy_orchestrator(self):
        from BuddyAI.buddy_bot import BuddyBot
        orchestrator = BuddyBot()
        bot = OpenClawBot(tier=Tier.PRO)
        bot.register_with_buddy(orchestrator)
        result = orchestrator.route_message("open_claw", "dashboard")
        assert result["response"] == "open_claw"
