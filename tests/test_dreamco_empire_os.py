"""
Tests for bots/dreamco_empire_os/

Covers all Empire OS modules:
  1. Tiers
  2. Empire HQ
  3. Bot Fleet
  4. Deal Analyzer
  5. Formula Vault
  6. Learning Matrix
  7. AI Leaders
  8. Orchestration
  9. Marketplace
  10. Revenue Tracker
  11. Cost Tracking
  12. Modules (Divisions, AIModelsHub, AIEcosystem, CryptoTracker, PaymentsHub,
               BizLaunch, CodeLab, LoansDeals, DebugIntel, PricingEngine,
               Connections, TimeCapsule, AutonomyControl)
  13. DreamCoEmpireOS main class (integration)
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------
from bots.dreamco_empire_os.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
    TIER_CATALOGUE,
    FEATURE_EMPIRE_HQ,
    FEATURE_BOT_FLEET,
    FEATURE_LEARNING_MATRIX,
    FEATURE_ORCHESTRATION,
    FEATURE_WHITE_LABEL,
)
from bots.dreamco_empire_os.empire_hq import EmpireHQ
from bots.dreamco_empire_os.bot_fleet import BotFleet, BotSpeed, BotStatus
from bots.dreamco_empire_os.deal_analyzer import DealAnalyzer, DealType, RiskLevel
from bots.dreamco_empire_os.formula_vault import FormulaVault, FormulaCategory
from bots.dreamco_empire_os.learning_matrix import LearningMatrix, LearningDomain
from bots.dreamco_empire_os.ai_leaders import AILeaders, LeaderRole, LeaderStatus
from bots.dreamco_empire_os.orchestration import Orchestration, PipelineStatus
from bots.dreamco_empire_os.marketplace import Marketplace, ListingCategory, ListingStatus
from bots.dreamco_empire_os.revenue_tracker import RevenueTracker
from bots.dreamco_empire_os.cost_tracking import CostTracking, CostCategory
from bots.dreamco_empire_os.modules import (
    Divisions,
    AIModelsHub,
    AIEcosystem,
    CryptoTracker,
    PaymentsHub,
    PaymentStatus,
    BizLaunch,
    CodeLab,
    LoansDeals,
    DebugIntel,
    DebugLevel,
    PricingEngine,
    Connections,
    TimeCapsule,
    AutonomyControl,
    AutonomyMode,
)
from bots.dreamco_empire_os.empire_os import DreamCoEmpireOS, DreamCoTierError


# ===========================================================================
# 1. Tiers
# ===========================================================================

class TestTiers:
    def test_three_tiers_exist(self):
        tiers = list_tiers()
        assert len(tiers) == 3

    def test_free_tier_price(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.price_usd_monthly == 0.0

    def test_pro_tier_price(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.price_usd_monthly == 49.0

    def test_enterprise_tier_price(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.price_usd_monthly == 199.0

    def test_enterprise_unlimited_bots(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.is_unlimited_bots()

    def test_free_has_empire_hq(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.has_feature(FEATURE_EMPIRE_HQ)

    def test_free_lacks_white_label(self):
        cfg = get_tier_config(Tier.FREE)
        assert not cfg.has_feature(FEATURE_WHITE_LABEL)

    def test_enterprise_has_white_label(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.has_feature(FEATURE_WHITE_LABEL)

    def test_upgrade_path_free_to_pro(self):
        upgrade = get_upgrade_path(Tier.FREE)
        assert upgrade.tier == Tier.PRO

    def test_upgrade_path_enterprise_is_none(self):
        assert get_upgrade_path(Tier.ENTERPRISE) is None

    def test_tier_config_has_feature_method(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.has_feature(FEATURE_BOT_FLEET)


# ===========================================================================
# 2. Empire HQ
# ===========================================================================

class TestEmpireHQ:
    def setup_method(self):
        self.hq = EmpireHQ()

    def test_instantiation(self):
        assert self.hq is not None

    def test_initial_revenue_zero(self):
        snap = self.hq.snapshot()
        assert snap["revenue_usd"] == 0.0

    def test_record_revenue(self):
        self.hq.record_revenue(1000.0)
        snap = self.hq.snapshot()
        assert snap["revenue_usd"] == 1000.0

    def test_record_cost(self):
        self.hq.record_cost(300.0)
        snap = self.hq.snapshot()
        assert snap["cost_usd"] == 300.0

    def test_profit_calculation(self):
        self.hq.record_revenue(1000.0)
        self.hq.record_cost(400.0)
        snap = self.hq.snapshot()
        assert snap["profit_usd"] == 600.0

    def test_set_active_bots(self):
        self.hq.set_active_bots(877)
        snap = self.hq.snapshot()
        assert snap["active_bots"] == 877

    def test_empire_level_street_hustler(self):
        level = self.hq.get_empire_level()
        assert level["level_name"] == "Street Hustler"

    def test_empire_level_advances_with_revenue(self):
        self.hq.record_revenue(10_000.0)
        level = self.hq.get_empire_level()
        assert level["level_name"] != "Street Hustler"

    def test_add_and_get_alerts(self):
        self.hq.add_alert("Bot offline: Lead Scraper")
        alerts = self.hq.get_alerts()
        assert len(alerts) == 1

    def test_update_stat(self):
        self.hq.update_stat("custom_metric", 42.0, "units", "up")
        snap = self.hq.snapshot()
        assert "custom_metric" in snap["stats"]
        assert snap["stats"]["custom_metric"]["value"] == 42.0

    def test_empire_xp_increases_with_revenue(self):
        self.hq.record_revenue(200.0)
        level = self.hq.get_empire_level()
        assert level["empire_xp"] > 0

    def test_snapshot_has_required_keys(self):
        snap = self.hq.snapshot()
        for key in ("module", "timestamp", "active_bots", "revenue_usd", "cost_usd", "profit_usd", "empire_level"):
            assert key in snap


# ===========================================================================
# 3. Bot Fleet
# ===========================================================================

class TestBotFleet:
    def setup_method(self):
        self.fleet = BotFleet()

    def test_register_bot(self):
        bot = self.fleet.register_bot("Lead Scraper", category="marketing", profit_per_day_usd=180)
        assert bot.name == "Lead Scraper"

    def test_register_multiple_bots(self):
        for i in range(5):
            self.fleet.register_bot(f"bot_{i}")
        assert len(self.fleet.list_bots()) == 5

    def test_activate_bot(self):
        self.fleet.register_bot("bot_a")
        result = self.fleet.activate_bot("bot_a")
        assert result["status"] == BotStatus.RUNNING.value

    def test_pause_bot(self):
        self.fleet.register_bot("bot_b")
        self.fleet.activate_bot("bot_b")
        result = self.fleet.pause_bot("bot_b")
        assert result["status"] == BotStatus.PAUSED.value

    def test_set_speed(self):
        self.fleet.register_bot("bot_c")
        result = self.fleet.set_speed("bot_c", BotSpeed.AGGRESSIVE)
        assert result["speed"] == BotSpeed.AGGRESSIVE.value

    def test_fleet_speed_applies_to_all(self):
        for i in range(3):
            self.fleet.register_bot(f"fb_{i}")
        result = self.fleet.set_fleet_speed(BotSpeed.SLOW)
        assert result["bots_updated"] == 3

    def test_toggle_autonomy(self):
        self.fleet.register_bot("auto_bot")
        result = self.fleet.toggle_autonomy("auto_bot", True)
        assert result["autonomous"] is True

    def test_record_run_success(self):
        self.fleet.register_bot("runner")
        self.fleet.record_run("runner", success=True)
        bot = self.fleet.get_bot("runner")
        assert bot["total_runs"] == 1
        assert bot["success_rate"] == 100.0

    def test_record_run_failure(self):
        self.fleet.register_bot("failer")
        self.fleet.record_run("failer", success=False)
        bot = self.fleet.get_bot("failer")
        assert bot["total_runs"] == 1
        assert bot["success_rate"] == 0.0

    def test_get_top_bots_by_profit(self):
        self.fleet.register_bot("rich_bot", profit_per_day_usd=500)
        self.fleet.register_bot("poor_bot", profit_per_day_usd=10)
        top = self.fleet.get_top_bots(n=1, sort_by="profit")
        assert top[0]["name"] == "rich_bot"

    def test_fleet_stats(self):
        self.fleet.register_bot("s1")
        self.fleet.activate_bot("s1")
        stats = self.fleet.get_fleet_stats()
        assert stats["running"] == 1
        assert stats["total_bots"] == 1

    def test_unregister_bot(self):
        self.fleet.register_bot("temp_bot")
        removed = self.fleet.unregister_bot("temp_bot")
        assert removed is True
        assert len(self.fleet.list_bots()) == 0

    def test_unregister_nonexistent_returns_false(self):
        assert self.fleet.unregister_bot("ghost") is False

    def test_get_unknown_bot_raises(self):
        with pytest.raises(KeyError):
            self.fleet.get_bot("unknown_bot")


# ===========================================================================
# 4. Deal Analyzer
# ===========================================================================

class TestDealAnalyzer:
    def setup_method(self):
        self.analyzer = DealAnalyzer()

    def _add_deal(self, deal_id="d001"):
        return self.analyzer.add_deal(
            deal_id=deal_id,
            name="SaaS Partnership",
            deal_type=DealType.PARTNERSHIP,
            upfront_cost_usd=5000.0,
            projected_monthly_revenue_usd=2000.0,
            risk_level=RiskLevel.LOW,
        )

    def test_add_deal(self):
        deal = self._add_deal()
        assert deal.deal_id == "d001"

    def test_analyze_deal_returns_score(self):
        self._add_deal()
        result = self.analyzer.analyze_deal("d001")
        assert "score" in result
        assert result["score"] >= 0

    def test_analyze_deal_verdict(self):
        self._add_deal()
        result = self.analyzer.analyze_deal("d001")
        assert result["verdict"] in ("Strong Buy", "Good Opportunity", "Proceed with Caution", "Pass")

    def test_rank_deals(self):
        self._add_deal("d1")
        self.analyzer.add_deal("d2", "Risky Deal", DealType.INVESTMENT,
                               50000, 100, RiskLevel.CRITICAL)
        ranked = self.analyzer.rank_deals()
        assert len(ranked) == 2
        assert ranked[0]["score"] >= ranked[1]["score"]

    def test_get_summary(self):
        self._add_deal()
        summary = self.analyzer.get_summary()
        assert summary["total_deals"] == 1

    def test_monthly_roi_calculation(self):
        deal = self._add_deal()
        assert deal.monthly_roi_pct == 40.0

    def test_payback_months(self):
        deal = self._add_deal()
        assert deal.payback_months == 2.5

    def test_unknown_deal_raises(self):
        with pytest.raises(KeyError):
            self.analyzer.analyze_deal("nonexistent")


# ===========================================================================
# 5. Formula Vault
# ===========================================================================

class TestFormulaVault:
    def setup_method(self):
        self.vault = FormulaVault()

    def test_builtins_loaded(self):
        formulas = self.vault.list_formulas()
        assert len(formulas) >= 7

    def test_execute_roi_monthly(self):
        result = self.vault.execute("roi_monthly", {"revenue": 1500.0, "cost": 1000.0})
        assert result["result"] == 50.0

    def test_execute_profit_margin(self):
        result = self.vault.execute("profit_margin", {"revenue": 5000.0, "expenses": 3500.0})
        assert result["result"] == 30.0

    def test_execute_compound_growth(self):
        result = self.vault.execute("compound_growth", {"principal": 1000.0, "rate": 0.0, "periods": 12})
        assert result["result"] == 1000.0

    def test_execute_missing_variable_raises(self):
        with pytest.raises(ValueError):
            self.vault.execute("roi_monthly", {"revenue": 1000.0})

    def test_execute_nonnumeric_raises(self):
        with pytest.raises(TypeError):
            self.vault.execute("roi_monthly", {"revenue": "big", "cost": 1000.0})

    def test_add_custom_formula(self):
        self.vault.add_formula(
            formula_id="custom_1",
            name="Custom Score",
            category=FormulaCategory.CUSTOM,
            description="Simple custom formula.",
            expression="a + b",
            variables=["a", "b"],
        )
        result = self.vault.execute("custom_1", {"a": 3.0, "b": 7.0})
        assert result["result"] == 10.0

    def test_use_count_increments(self):
        self.vault.execute("roi_monthly", {"revenue": 500.0, "cost": 250.0})
        formula = self.vault.get_formula("roi_monthly")
        assert formula["use_count"] == 1

    def test_search_formulas(self):
        results = self.vault.search("roi")
        assert len(results) >= 1

    def test_delete_formula(self):
        self.vault.add_formula("del_me", "Temp", FormulaCategory.CUSTOM, "", "x", ["x"])
        deleted = self.vault.delete_formula("del_me")
        assert deleted is True

    def test_get_stats(self):
        stats = self.vault.get_stats()
        assert "total_formulas" in stats

    def test_unknown_formula_raises(self):
        with pytest.raises(KeyError):
            self.vault.execute("nonexistent", {})


# ===========================================================================
# 6. Learning Matrix
# ===========================================================================

class TestLearningMatrix:
    def setup_method(self):
        self.matrix = LearningMatrix()
        self.matrix.add_learner("learner_1", "Jordan")

    def test_builtins_loaded(self):
        lessons = self.matrix.list_lessons()
        assert len(lessons) >= 7

    def test_add_learner(self):
        profile = self.matrix.get_learner("learner_1")
        assert profile["name"] == "Jordan"

    def test_complete_lesson_awards_xp(self):
        result = self.matrix.complete_lesson("learner_1", "lesson_001")
        assert result["status"] == "completed"
        assert result["xp_earned"] > 0

    def test_complete_same_lesson_twice(self):
        self.matrix.complete_lesson("learner_1", "lesson_001")
        result = self.matrix.complete_lesson("learner_1", "lesson_001")
        assert result["status"] == "already_completed"

    def test_learning_path_returns_lessons(self):
        path = self.matrix.get_learning_path("learner_1")
        assert isinstance(path, list)
        assert len(path) > 0

    def test_big_bro_motivate(self):
        msg = self.matrix.big_bro_motivate()
        assert isinstance(msg, str) and len(msg) > 0

    def test_add_custom_lesson(self):
        result = self.matrix.add_lesson(
            lesson_id="custom_l1",
            title="Custom Lesson",
            domain=LearningDomain.FINANCE,
            content="Learn about custom stuff.",
            xp_reward=50,
        )
        assert result["lesson_id"] == "custom_l1"

    def test_level_advances_with_xp(self):
        for lesson_id in ["lesson_001", "lesson_002", "lesson_003",
                          "lesson_004", "lesson_005", "lesson_006", "lesson_007"]:
            self.matrix.complete_lesson("learner_1", lesson_id)
        profile = self.matrix.get_learner("learner_1")
        assert profile["level"] > 1

    def test_unknown_learner_raises(self):
        with pytest.raises(KeyError):
            self.matrix.get_learner("ghost_user")

    def test_get_stats(self):
        stats = self.matrix.get_stats()
        assert stats["total_lessons"] >= 7


# ===========================================================================
# 7. AI Leaders
# ===========================================================================

class TestAILeaders:
    def setup_method(self):
        self.leaders = AILeaders()
        self.leaders.add_leader("l1", "RevBot 3000", LeaderRole.REVENUE_FORECASTER)

    def test_add_leader(self):
        leader = self.leaders.get_leader("l1")
        assert leader["name"] == "RevBot 3000"

    def test_leader_initial_status_active(self):
        leader = self.leaders.get_leader("l1")
        assert leader["status"] == LeaderStatus.ACTIVE.value

    def test_update_status(self):
        result = self.leaders.update_status("l1", LeaderStatus.TRAINING)
        assert result["status"] == LeaderStatus.TRAINING.value

    def test_record_decision_success(self):
        result = self.leaders.record_decision("l1", "Launch product", "Revenue +20%",
                                              revenue_impact_usd=5000.0, success=True)
        assert result["success"] is True
        assert result["revenue_impact_usd"] == 5000.0

    def test_record_decision_failure(self):
        result = self.leaders.record_decision("l1", "Bad call", "Revenue flat",
                                              revenue_impact_usd=0.0, success=False)
        assert result["success"] is False

    def test_leaderboard_returns_sorted(self):
        self.leaders.add_leader("l2", "RiskBot", LeaderRole.RISK_ANALYST)
        board = self.leaders.get_leaderboard()
        assert len(board) == 2

    def test_get_summary(self):
        summary = self.leaders.get_summary()
        assert summary["total_leaders"] == 1

    def test_decision_log(self):
        self.leaders.record_decision("l1", "Test decision", "OK")
        log = self.leaders.get_decision_log()
        assert len(log) >= 1

    def test_unknown_leader_raises(self):
        with pytest.raises(KeyError):
            self.leaders.get_leader("ghost")


# ===========================================================================
# 8. Orchestration
# ===========================================================================

class TestOrchestration:
    def setup_method(self):
        self.orch = Orchestration()

    def test_create_pipeline(self):
        result = self.orch.create_pipeline("pipe_1", "Lead Pipeline")
        assert result["pipeline_id"] == "pipe_1"

    def test_add_step(self):
        self.orch.create_pipeline("pipe_2", "Test")
        result = self.orch.add_step("pipe_2", "step_1", "lead_scraper", "scrape_leads")
        assert result["step_id"] == "step_1"

    def test_run_pipeline_all_done(self):
        self.orch.create_pipeline("pipe_3", "Run Test")
        self.orch.add_step("pipe_3", "s1", "bot_a", "action_a")
        self.orch.add_step("pipe_3", "s2", "bot_b", "action_b")
        result = self.orch.run_pipeline("pipe_3")
        assert result["status"] == PipelineStatus.COMPLETED.value

    def test_run_pipeline_with_deps(self):
        self.orch.create_pipeline("pipe_4", "Dep Test")
        self.orch.add_step("pipe_4", "s1", "bot_a", "action_a")
        self.orch.add_step("pipe_4", "s2", "bot_b", "action_b", depends_on=["s1"])
        result = self.orch.run_pipeline("pipe_4")
        assert result["status"] == PipelineStatus.COMPLETED.value

    def test_pipeline_with_unmet_deps_skips(self):
        self.orch.create_pipeline("pipe_5", "Unmet Deps")
        self.orch.add_step("pipe_5", "s1", "bot_x", "act", depends_on=["missing_step"])
        result = self.orch.run_pipeline("pipe_5")
        assert result["steps"][0]["status"] == "skipped"

    def test_list_pipelines(self):
        self.orch.create_pipeline("p1", "P1")
        self.orch.create_pipeline("p2", "P2")
        assert len(self.orch.list_pipelines()) == 2

    def test_get_summary(self):
        self.orch.create_pipeline("p_s", "Summary")
        summary = self.orch.get_summary()
        assert summary["total_pipelines"] == 1

    def test_unknown_pipeline_raises(self):
        with pytest.raises(KeyError):
            self.orch.run_pipeline("nonexistent")


# ===========================================================================
# 9. Marketplace
# ===========================================================================

class TestMarketplace:
    def setup_method(self):
        self.market = Marketplace()
        self.market.add_listing("bot_001", "Lead Gen Bot", ListingCategory.BOT,
                                "Scrapes leads 24/7.", price_usd=99.0)

    def test_add_listing(self):
        listings = self.market.search()
        assert len(listings) == 1

    def test_purchase_listing(self):
        result = self.market.purchase("bot_001", "buyer_jordan")
        assert result["listing_id"] == "bot_001"
        assert result["buyer"] == "buyer_jordan"

    def test_purchase_unavailable_raises(self):
        from bots.dreamco_empire_os.marketplace import ListingStatus
        listing = self.market._listings["bot_001"]
        listing.status = ListingStatus.SOLD_OUT
        with pytest.raises(ValueError):
            self.market.purchase("bot_001", "buyer2")

    def test_rate_listing(self):
        result = self.market.rate_listing("bot_001", 5.0)
        assert result["new_rating"] == 5.0

    def test_rate_out_of_range_raises(self):
        with pytest.raises(ValueError):
            self.market.rate_listing("bot_001", 6.0)

    def test_search_by_query(self):
        self.market.add_listing("tool_1", "Crypto Analyzer Tool", ListingCategory.TOOL,
                                "Analyzes crypto.", price_usd=49.0)
        results = self.market.search(query="crypto")
        assert len(results) == 1

    def test_get_summary(self):
        summary = self.market.get_summary()
        assert summary["total_listings"] == 1

    def test_unknown_listing_raises(self):
        with pytest.raises(KeyError):
            self.market.purchase("ghost_listing", "buyer")


# ===========================================================================
# 10. Revenue Tracker
# ===========================================================================

class TestRevenueTracker:
    def setup_method(self):
        self.tracker = RevenueTracker()

    def test_record_revenue(self):
        result = self.tracker.record_revenue("Lead Bot", 500.0)
        assert result["amount_usd"] == 500.0

    def test_record_cost(self):
        result = self.tracker.record_cost("Infrastructure", 100.0)
        assert result["amount_usd"] == 100.0

    def test_get_summary_net(self):
        self.tracker.record_revenue("source_a", 1000.0)
        self.tracker.record_cost("cost_a", 300.0)
        summary = self.tracker.get_summary()
        assert summary["gross_revenue_usd"] == 1000.0
        assert summary["net_revenue_usd"] == 700.0

    def test_get_top_sources(self):
        self.tracker.record_revenue("bot_a", 500.0)
        self.tracker.record_revenue("bot_b", 200.0)
        top = self.tracker.get_top_sources(n=1)
        assert top[0]["source"] == "bot_a"

    def test_get_mrr(self):
        self.tracker.record_revenue("a", 1000.0)
        assert self.tracker.get_mrr() == 1000.0

    def test_get_arr(self):
        self.tracker.record_revenue("a", 1000.0)
        assert self.tracker.get_arr() == 12000.0

    def test_get_recent_entries(self):
        self.tracker.record_revenue("x", 50.0)
        entries = self.tracker.get_recent_entries()
        assert len(entries) == 1


# ===========================================================================
# 11. Cost Tracking
# ===========================================================================

class TestCostTracking:
    def setup_method(self):
        self.costs = CostTracking(monthly_budget_usd=1000.0)

    def test_record_cost(self):
        result = self.costs.record_cost("Server", 200.0, CostCategory.INFRASTRUCTURE)
        assert result["amount_usd"] == 200.0

    def test_get_summary_under_budget(self):
        self.costs.record_cost("Server", 500.0, CostCategory.INFRASTRUCTURE)
        summary = self.costs.get_summary()
        assert not summary["over_budget"]
        assert summary["budget_remaining_usd"] == 500.0

    def test_get_summary_over_budget(self):
        self.costs.record_cost("Big Server", 1500.0, CostCategory.INFRASTRUCTURE)
        summary = self.costs.get_summary()
        assert summary["over_budget"]

    def test_get_top_costs(self):
        self.costs.record_cost("Cheap", 10.0, CostCategory.OTHER)
        self.costs.record_cost("Expensive", 900.0, CostCategory.AI_MODELS)
        top = self.costs.get_top_costs(n=1)
        assert top[0]["name"] == "Expensive"

    def test_recurring_monthly(self):
        self.costs.record_cost("Monthly Sub", 50.0, recurring_monthly=True)
        self.costs.record_cost("One-time", 200.0, recurring_monthly=False)
        assert self.costs.get_recurring_monthly() == 50.0

    def test_by_category_breakdown(self):
        self.costs.record_cost("AI bill", 300.0, CostCategory.AI_MODELS)
        summary = self.costs.get_summary()
        assert "ai_models" in summary["by_category"]


# ===========================================================================
# 12. Additional Modules
# ===========================================================================

class TestDivisions:
    def test_create_and_list(self):
        divs = Divisions()
        divs.create_division("Marketing", "All marketing bots")
        assert len(divs.list_divisions()) == 1

    def test_add_bot_to_division(self):
        divs = Divisions()
        divs.create_division("Sales", "Sales bots")
        result = divs.add_bot("Sales", "cold_dm_bot")
        assert result["bot_added"] == "cold_dm_bot"

    def test_unknown_division_raises(self):
        divs = Divisions()
        with pytest.raises(KeyError):
            divs.get_division("ghost")


class TestAIModelsHub:
    def test_register_and_list(self):
        hub = AIModelsHub()
        hub.register_model("gpt4", "GPT-4", "OpenAI", "text_generation", "4.0")
        models = hub.list_models()
        assert len(models) == 1

    def test_activate_model(self):
        hub = AIModelsHub()
        hub.register_model("bert", "BERT", "Google", "classification")
        result = hub.activate_model("bert")
        assert result["active"] is True

    def test_list_active_only(self):
        hub = AIModelsHub()
        hub.register_model("m1", "M1", "X", "t")
        hub.register_model("m2", "M2", "X", "t")
        hub.activate_model("m1")
        active = hub.list_models(active_only=True)
        assert len(active) == 1


class TestAIEcosystem:
    def test_add_agents_and_relationship(self):
        eco = AIEcosystem()
        eco.add_agent("a1", "Lead Bot", "scraper")
        eco.add_agent("a2", "CRM Bot", "crm")
        eco.add_relationship("a1", "a2", "feeds_into")
        graph = eco.get_graph()
        assert graph["total_agents"] == 2
        assert graph["total_relationships"] == 1


class TestCryptoTracker:
    def setup_method(self):
        self.crypto = CryptoTracker()
        self.crypto.add_asset("BTC", "Bitcoin", 0.5, 40000.0)

    def test_add_asset(self):
        portfolio = self.crypto.get_portfolio()
        assert len(portfolio["assets"]) == 1

    def test_update_price_gain(self):
        result = self.crypto.update_price("BTC", 50000.0)
        assert result["pnl_usd"] == 5000.0

    def test_update_price_loss(self):
        result = self.crypto.update_price("BTC", 30000.0)
        assert result["pnl_usd"] == -5000.0

    def test_record_signal(self):
        result = self.crypto.record_signal("BTC", "buy", 85.0)
        assert result["signal"] == "buy"

    def test_portfolio_total_value(self):
        self.crypto.update_price("BTC", 40000.0)
        portfolio = self.crypto.get_portfolio()
        assert portfolio["total_portfolio_value_usd"] == 20000.0

    def test_unknown_asset_price_update_raises(self):
        with pytest.raises(KeyError):
            self.crypto.update_price("ETH", 3000.0)


class TestPaymentsHub:
    def test_create_payment(self):
        hub = PaymentsHub()
        result = hub.create_payment("client_a", "dreamco", 500.0)
        assert result["amount_usd"] == 500.0
        assert result["status"] == PaymentStatus.PENDING.value

    def test_complete_payment(self):
        hub = PaymentsHub()
        p = hub.create_payment("a", "b", 100.0)
        result = hub.complete_payment(p["payment_id"])
        assert result["status"] == PaymentStatus.COMPLETED.value

    def test_get_summary(self):
        hub = PaymentsHub()
        p = hub.create_payment("a", "b", 200.0)
        hub.complete_payment(p["payment_id"])
        summary = hub.get_summary()
        assert summary["completed"] == 1
        assert summary["total_volume_usd"] == 200.0


class TestBizLaunch:
    def test_launch_saas(self):
        biz = BizLaunch()
        result = biz.launch_business("saas", "My SaaS")
        assert result["type"] == "saas"
        assert len(result["steps"]) > 0

    def test_get_templates(self):
        biz = BizLaunch()
        templates = biz.get_templates()
        assert len(templates) >= 4

    def test_unknown_type_raises(self):
        biz = BizLaunch()
        with pytest.raises(ValueError):
            biz.launch_business("unknown_type", "Test")


class TestCodeLab:
    def test_save_and_run_script(self):
        lab = CodeLab()
        lab.save_script("s1", "My Script", "python", "print('hello')")
        result = lab.run_script("s1")
        assert result["status"] == "executed"

    def test_list_scripts(self):
        lab = CodeLab()
        lab.save_script("s1", "Script", "js", "console.log('x')")
        scripts = lab.list_scripts()
        assert len(scripts) == 1


class TestLoansDeals:
    def test_add_loan(self):
        ld = LoansDeals()
        result = ld.add_loan("Business Loan", 10000.0, 5.0, 12)
        assert result["principal_usd"] == 10000.0
        assert result["monthly_payment_usd"] > 0

    def test_add_deal(self):
        ld = LoansDeals()
        result = ld.add_deal("Partnership", 50000.0, "Partner Corp")
        assert result["value_usd"] == 50000.0

    def test_get_summary(self):
        ld = LoansDeals()
        ld.add_loan("L1", 5000.0, 0.0, 12)
        ld.add_deal("D1", 1000.0, "X")
        summary = ld.get_summary()
        assert summary["total_loans"] == 1
        assert summary["total_deals"] == 1


class TestDebugIntel:
    def test_log_and_retrieve(self):
        debug = DebugIntel()
        debug.log("bot_a", "Something went wrong", DebugLevel.ERROR)
        errors = debug.get_errors()
        assert len(errors) == 1

    def test_filter_by_bot(self):
        debug = DebugIntel()
        debug.log("bot_a", "Error A", DebugLevel.ERROR)
        debug.log("bot_b", "Error B", DebugLevel.ERROR)
        errors = debug.get_errors(bot_name="bot_a")
        assert len(errors) == 1

    def test_get_summary(self):
        debug = DebugIntel()
        debug.log("x", "warn msg", DebugLevel.WARNING)
        debug.log("x", "err msg", DebugLevel.ERROR)
        summary = debug.get_summary()
        assert summary["warnings"] == 1
        assert summary["errors"] == 1


class TestPricingEngine:
    def test_set_price(self):
        pe = PricingEngine()
        result = pe.set_price("prod_1", "Lead Scraper Pro", 49.0)
        assert result["price_usd"] == 49.0

    def test_ab_test(self):
        pe = PricingEngine()
        result = pe.ab_test("prod_1", 49.0, 39.0)
        assert result["price_a_usd"] == 49.0

    def test_list_prices(self):
        pe = PricingEngine()
        pe.set_price("p1", "Prod A", 10.0)
        assert len(pe.list_prices()) == 1


class TestConnections:
    def test_add_integration(self):
        conn = Connections()
        result = conn.add_integration("stripe", "Stripe", "https://api.stripe.com")
        assert result["status"] == "active"

    def test_disable_integration(self):
        conn = Connections()
        conn.add_integration("twilio", "Twilio", "https://api.twilio.com")
        result = conn.disable_integration("twilio")
        assert result["status"] == "disabled"

    def test_list_active_only(self):
        conn = Connections()
        conn.add_integration("a", "A", "http://a.com")
        conn.add_integration("b", "B", "http://b.com")
        conn.disable_integration("b")
        active = conn.list_integrations(active_only=True)
        assert len(active) == 1


class TestTimeCapsule:
    def test_archive_and_retrieve(self):
        tc = TimeCapsule()
        tc.archive("snapshot_1", {"revenue": 1000})
        retrieved = tc.retrieve("snapshot_1")
        assert len(retrieved) == 1
        assert retrieved[0]["data"]["revenue"] == 1000

    def test_list_archives(self):
        tc = TimeCapsule()
        tc.archive("snap_a", {})
        tc.archive("snap_b", {})
        archives = tc.list_archives()
        assert len(archives) == 2


class TestAutonomyControl:
    def test_set_global_mode(self):
        ac = AutonomyControl()
        result = ac.set_global_mode(AutonomyMode.FULL_AUTO)
        assert result["global_autonomy_mode"] == AutonomyMode.FULL_AUTO.value

    def test_set_bot_mode(self):
        ac = AutonomyControl()
        result = ac.set_bot_mode("lead_bot", AutonomyMode.SEMI_AUTO)
        assert result["autonomy_mode"] == AutonomyMode.SEMI_AUTO.value

    def test_get_status(self):
        ac = AutonomyControl()
        ac.set_global_mode(AutonomyMode.FULL_AUTO)
        status = ac.get_status()
        assert status["global_mode"] == AutonomyMode.FULL_AUTO.value


# ===========================================================================
# 13. DreamCoEmpireOS Integration
# ===========================================================================

class TestDreamCoEmpireOSIntegration:
    def setup_method(self):
        self.empire = DreamCoEmpireOS(tier=Tier.PRO, operator_name="Jordan")

    def test_instantiation(self):
        assert self.empire is not None

    def test_tier_info(self):
        info = self.empire.get_tier_info()
        assert info["tier"] == "pro"
        assert info["price_usd_monthly"] == 49.0

    def test_dashboard_returns_dict(self):
        snap = self.empire.dashboard()
        assert "title" in snap
        assert snap["title"] == "DreamCo Empire OS"

    def test_register_and_activate_bot(self):
        self.empire.bot_fleet.register_bot("Lead Scraper", profit_per_day_usd=180)
        result = self.empire.activate_bot("Lead Scraper")
        assert result["status"] == "running"

    def test_set_fleet_speed(self):
        self.empire.bot_fleet.register_bot("Speed Bot")
        result = self.empire.set_fleet_speed(BotSpeed.AGGRESSIVE)
        assert result["fleet_speed"] == "aggressive"

    def test_chat_dashboard(self):
        resp = self.empire.chat("show dashboard")
        assert "message" in resp

    def test_chat_revenue(self):
        resp = self.empire.chat("what's my revenue?")
        assert "message" in resp

    def test_chat_deals(self):
        resp = self.empire.chat("analyze deals")
        assert "message" in resp

    def test_chat_unknown(self):
        resp = self.empire.chat("xyzzy unknown command")
        assert "message" in resp

    def test_can_access_pro_feature(self):
        assert self.empire.can_access(FEATURE_LEARNING_MATRIX)

    def test_cannot_access_enterprise_only_feature(self):
        free_empire = DreamCoEmpireOS(tier=Tier.FREE)
        assert not free_empire.can_access(FEATURE_WHITE_LABEL)

    def test_tier_error_raised_for_missing_feature(self):
        free_empire = DreamCoEmpireOS(tier=Tier.FREE)
        with pytest.raises(DreamCoTierError):
            free_empire._require(FEATURE_WHITE_LABEL)

    def test_revenue_and_cost_tracking(self):
        self.empire.revenue_tracker.record_revenue("Bot Sales", 1000.0)
        self.empire.cost_tracking.record_cost("API Cost", 200.0)
        snap = self.empire.dashboard()
        assert snap["revenue"]["gross_revenue_usd"] == 1000.0

    def test_process_method(self):
        result = self.empire.process({"command": "show status"})
        assert "message" in result

    def test_learn_via_empire(self):
        self.empire.learning_matrix.add_learner("jordan", "Jordan")
        result = self.empire.learn("jordan", "lesson_001")
        assert result["status"] == "completed"

    def test_run_pipeline_via_empire(self):
        self.empire.orchestration.create_pipeline("emp_pipe", "Empire Pipeline")
        self.empire.orchestration.add_step("emp_pipe", "s1", "lead_bot", "scrape")
        result = self.empire.run_pipeline("emp_pipe")
        assert result["status"] == "completed"

    def test_upgrade_available_for_free_tier(self):
        free_empire = DreamCoEmpireOS(tier=Tier.FREE)
        snap = free_empire.dashboard()
        assert snap["upgrade_available"] is True

    def test_no_upgrade_for_enterprise(self):
        ent = DreamCoEmpireOS(tier=Tier.ENTERPRISE)
        snap = ent.dashboard()
        assert snap["upgrade_available"] is False
