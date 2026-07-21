"""
Tests for bots/god_mode_bot/

Covers:
  1. Tiers (FREE / PRO / ENTERPRISE)
  2. AutoClientHunter engine
  3. AutoCloser engine
  4. PaymentAutoCollector engine
  5. ViralEngine engine
  6. SelfImprovingAI engine
  7. GodModeBot orchestrator (run_all_engines / get_summary)
  8. Tier gating (feature access + lead caps)
  9. Error handling & edge cases
  10. Bot Library registration
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

# ---------------------------------------------------------------------------
# Tier imports
# ---------------------------------------------------------------------------
from bots.god_mode_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
    TIER_CATALOGUE,
    FEATURE_LEAD_HUNTING,
    FEATURE_AUTO_CLOSER,
    FEATURE_PAYMENT_COLLECTION,
    FEATURE_VIRAL_ENGINE,
    FEATURE_SELF_IMPROVING_AI,
    FEATURE_WHITE_LABEL,
    FEATURE_API_ACCESS,
    FEATURE_DEDICATED_SUPPORT,
)

# ---------------------------------------------------------------------------
# Bot imports
# ---------------------------------------------------------------------------
from bots.god_mode_bot.god_mode_bot import (
    GodModeBot,
    AutoClientHunter,
    AutoCloser,
    PaymentAutoCollector,
    ViralEngine,
    SelfImprovingAI,
)


# ===========================================================================
# 1. Tier tests
# ===========================================================================

class TestTierEnum:
    def test_tier_values(self):
        assert Tier.FREE.value == "free"
        assert Tier.PRO.value == "pro"
        assert Tier.ENTERPRISE.value == "enterprise"

    def test_three_tiers_exist(self):
        assert len(list(Tier)) == 3


class TestTierConfig:
    def test_free_tier_config(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.price_usd_monthly == 0.0
        assert cfg.max_leads_per_cycle == 5
        assert cfg.max_viral_posts == 3
        assert cfg.tier == Tier.FREE

    def test_pro_tier_config(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.price_usd_monthly == 97.0
        assert cfg.max_leads_per_cycle == 20
        assert cfg.max_subscribers == 50
        assert cfg.tier == Tier.PRO

    def test_enterprise_tier_config(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.price_usd_monthly == 297.0
        assert cfg.max_leads_per_cycle is None
        assert cfg.max_subscribers is None
        assert cfg.tier == Tier.ENTERPRISE

    def test_has_feature_true(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.has_feature(FEATURE_AUTO_CLOSER) is True

    def test_has_feature_false(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.has_feature(FEATURE_AUTO_CLOSER) is False

    def test_is_unlimited_leads_enterprise(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.is_unlimited_leads() is True

    def test_is_unlimited_leads_free(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.is_unlimited_leads() is False

    def test_free_does_not_have_payment_collection(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.has_feature(FEATURE_PAYMENT_COLLECTION) is False

    def test_enterprise_has_all_features(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        for feat in [
            FEATURE_LEAD_HUNTING,
            FEATURE_AUTO_CLOSER,
            FEATURE_PAYMENT_COLLECTION,
            FEATURE_VIRAL_ENGINE,
            FEATURE_SELF_IMPROVING_AI,
            FEATURE_WHITE_LABEL,
            FEATURE_API_ACCESS,
            FEATURE_DEDICATED_SUPPORT,
        ]:
            assert cfg.has_feature(feat), f"Enterprise missing {feat}"


class TestTierHelpers:
    def test_list_tiers_returns_three(self):
        tiers = list_tiers()
        assert len(tiers) == 3

    def test_list_tiers_order(self):
        tiers = list_tiers()
        assert tiers[0].tier == Tier.FREE
        assert tiers[1].tier == Tier.PRO
        assert tiers[2].tier == Tier.ENTERPRISE

    def test_upgrade_free_to_pro(self):
        upgrade = get_upgrade_path(Tier.FREE)
        assert upgrade is not None
        assert upgrade.tier == Tier.PRO

    def test_upgrade_pro_to_enterprise(self):
        upgrade = get_upgrade_path(Tier.PRO)
        assert upgrade is not None
        assert upgrade.tier == Tier.ENTERPRISE

    def test_upgrade_enterprise_is_none(self):
        upgrade = get_upgrade_path(Tier.ENTERPRISE)
        assert upgrade is None

    def test_tier_catalogue_has_all_keys(self):
        for tier in Tier:
            assert tier.value in TIER_CATALOGUE


# ===========================================================================
# 2. AutoClientHunter tests
# ===========================================================================

class TestAutoClientHunter:
    def setup_method(self):
        self.hunter = AutoClientHunter()

    def test_hunt_returns_list(self):
        leads = self.hunter.hunt_leads("ecommerce", 5)
        assert isinstance(leads, list)
        assert len(leads) == 5

    def test_lead_has_required_fields(self):
        leads = self.hunter.hunt_leads("tech_startups", 1)
        lead = leads[0]
        assert "id" in lead
        assert "niche" in lead
        assert "score" in lead
        assert "email" in lead
        assert "pain_point" in lead

    def test_lead_score_valid(self):
        leads = self.hunter.hunt_leads("real_estate", 10)
        valid_scores = {"hot", "warm", "cold"}
        for lead in leads:
            assert lead["score"] in valid_scores

    def test_niche_is_set_correctly(self):
        leads = self.hunter.hunt_leads("health_wellness", 3)
        for lead in leads:
            assert lead["niche"] == "health_wellness"

    def test_count_respected(self):
        leads = self.hunter.hunt_leads("local_business", 7)
        assert len(leads) == 7

    def test_zero_count_returns_empty(self):
        leads = self.hunter.hunt_leads("ecommerce", 0)
        assert leads == []

    def test_qualified_field_present(self):
        leads = self.hunter.hunt_leads("ecommerce", 5)
        for lead in leads:
            assert "qualified" in lead
            assert isinstance(lead["qualified"], bool)


# ===========================================================================
# 3. AutoCloser tests
# ===========================================================================

class TestAutoCloser:
    def setup_method(self):
        self.closer = AutoCloser()

    def _make_leads(self, count=5, qualified=True):
        return [
            {"id": f"L-{i}", "company": f"Corp {i}", "qualified": qualified}
            for i in range(count)
        ]

    def test_close_returns_list(self):
        leads = self._make_leads(3)
        deals = self.closer.close_leads(leads)
        assert isinstance(deals, list)

    def test_unqualified_leads_skipped(self):
        leads = self._make_leads(5, qualified=False)
        deals = self.closer.close_leads(leads)
        assert deals == []

    def test_deal_has_required_fields(self):
        leads = self._make_leads(1)
        deals = self.closer.close_leads(leads)
        if deals:
            deal = deals[0]
            assert "lead_id" in deal
            assert "won" in deal
            assert "final_stage" in deal
            assert "stages_traversed" in deal

    def test_won_deal_has_positive_value(self):
        leads = self._make_leads(20)
        deals = self.closer.close_leads(leads)
        for deal in deals:
            if deal["won"]:
                assert deal["deal_value"] > 0

    def test_lost_deal_has_zero_value(self):
        leads = self._make_leads(20)
        deals = self.closer.close_leads(leads)
        for deal in deals:
            if not deal["won"]:
                assert deal["deal_value"] == 0

    def test_stages_traversed_is_list(self):
        leads = self._make_leads(5)
        deals = self.closer.close_leads(leads)
        for deal in deals:
            assert isinstance(deal["stages_traversed"], list)
            assert len(deal["stages_traversed"]) >= 1

    def test_empty_leads_returns_empty(self):
        assert self.closer.close_leads([]) == []


# ===========================================================================
# 4. PaymentAutoCollector tests
# ===========================================================================

class TestPaymentAutoCollector:
    def setup_method(self):
        self.collector = PaymentAutoCollector()

    def _make_clients(self, count=3):
        return [{"lead_id": f"L-{i}", "won": True} for i in range(count)]

    def test_collect_returns_dict(self):
        result = self.collector.collect_payments(self._make_clients(3))
        assert isinstance(result, dict)

    def test_subscribers_added(self):
        clients = self._make_clients(4)
        result = self.collector.collect_payments(clients)
        assert result["subscribers_added"] == 4

    def test_mrr_is_positive(self):
        result = self.collector.collect_payments(self._make_clients(5))
        assert result["mrr"] >= 0

    def test_arr_equals_mrr_times_12(self):
        result = self.collector.collect_payments(self._make_clients(3))
        assert result["arr"] == result["mrr"] * 12

    def test_total_invoices_increments(self):
        result = self.collector.collect_payments(self._make_clients(2))
        assert result["total_invoices"] == 2

    def test_empty_clients_returns_zero_stats(self):
        result = self.collector.collect_payments([])
        assert result["subscribers_added"] == 0
        assert result["mrr"] == 0

    def test_payments_collected_lte_subscribers(self):
        clients = self._make_clients(10)
        result = self.collector.collect_payments(clients)
        assert result["payments_collected"] <= result["subscribers_added"]


# ===========================================================================
# 5. ViralEngine tests
# ===========================================================================

class TestViralEngine:
    def setup_method(self):
        self.engine = ViralEngine()

    def test_returns_list(self):
        posts = self.engine.create_viral_content("business")
        assert isinstance(posts, list)

    def test_all_platforms_covered(self):
        posts = self.engine.create_viral_content("business")
        platforms = {p["platform"] for p in posts}
        expected = {"tiktok", "instagram", "twitter", "facebook", "linkedin", "youtube"}
        assert platforms == expected

    def test_post_has_required_fields(self):
        posts = self.engine.create_viral_content("finance")
        for post in posts:
            assert "platform" in post
            assert "content" in post
            assert "trend" in post
            assert "optimal_post_time" in post
            assert "engagement_score" in post
            assert "estimated_reach" in post

    def test_engagement_score_in_range(self):
        posts = self.engine.create_viral_content("tech")
        for post in posts:
            assert 0 <= post["engagement_score"] <= 10

    def test_estimated_reach_positive(self):
        posts = self.engine.create_viral_content("fitness")
        for post in posts:
            assert post["estimated_reach"] > 0

    def test_scheduled_is_true(self):
        posts = self.engine.create_viral_content("lifestyle")
        for post in posts:
            assert post["scheduled"] is True

    def test_unknown_niche_falls_back(self):
        posts = self.engine.create_viral_content("unknown_niche")
        assert len(posts) > 0


# ===========================================================================
# 6. SelfImprovingAI tests
# ===========================================================================

class TestSelfImprovingAI:
    def setup_method(self):
        self.ai = SelfImprovingAI()

    def test_returns_dict(self):
        result = self.ai.analyze_performance({"total_revenue": 5000, "total_leads": 20})
        assert isinstance(result, dict)

    def test_has_performance_score(self):
        result = self.ai.analyze_performance({"total_revenue": 3000, "total_leads": 10})
        assert "performance_score" in result
        assert isinstance(result["performance_score"], (int, float))

    def test_has_recommendations(self):
        result = self.ai.analyze_performance({"total_revenue": 0, "total_leads": 0})
        assert "recommendations" in result
        assert isinstance(result["recommendations"], list)
        assert len(result["recommendations"]) > 0

    def test_has_service_priority(self):
        result = self.ai.analyze_performance({"total_revenue": 2000, "total_leads": 5})
        assert "service_priority" in result
        assert isinstance(result["service_priority"], list)

    def test_next_cycle_target_higher_than_current(self):
        result = self.ai.analyze_performance({"total_revenue": 4000, "total_leads": 15})
        assert result["next_cycle_target"] >= 4000

    def test_revenue_analysis_string(self):
        result = self.ai.analyze_performance({"total_revenue": 8000, "total_leads": 30})
        assert isinstance(result["revenue_analysis"], str)

    def test_empty_results_handled(self):
        result = self.ai.analyze_performance({})
        assert "performance_score" in result


# ===========================================================================
# 7. GodModeBot orchestrator tests
# ===========================================================================

class TestGodModeBotInit:
    def test_default_tier_is_free(self):
        bot = GodModeBot()
        assert bot.tier == Tier.FREE

    def test_pro_tier_set(self):
        bot = GodModeBot(tier=Tier.PRO)
        assert bot.tier == Tier.PRO

    def test_enterprise_tier_set(self):
        bot = GodModeBot(tier=Tier.ENTERPRISE)
        assert bot.tier == Tier.ENTERPRISE

    def test_default_niche(self):
        bot = GodModeBot()
        assert bot.niche == "business"

    def test_custom_niche(self):
        bot = GodModeBot(niche="tech")
        assert bot.niche == "tech"


class TestGodModeBotRunAllEngines:
    def test_returns_dict(self):
        bot = GodModeBot(tier=Tier.PRO)
        report = bot.run_all_engines()
        assert isinstance(report, dict)

    def test_report_has_required_keys(self):
        bot = GodModeBot(tier=Tier.PRO)
        report = bot.run_all_engines()
        for key in ["bot", "tier", "niche", "leads_hunted", "deals_won", "total_revenue", "timestamp"]:
            assert key in report, f"Missing key: {key}"

    def test_bot_name_correct(self):
        bot = GodModeBot(tier=Tier.PRO)
        report = bot.run_all_engines()
        assert report["bot"] == "GodModeBot"

    def test_tier_in_report(self):
        bot = GodModeBot(tier=Tier.ENTERPRISE)
        report = bot.run_all_engines()
        assert report["tier"] == "enterprise"

    def test_leads_hunted_non_negative(self):
        bot = GodModeBot(tier=Tier.PRO)
        report = bot.run_all_engines()
        assert report["leads_hunted"] >= 0

    def test_total_revenue_non_negative(self):
        bot = GodModeBot(tier=Tier.PRO)
        report = bot.run_all_engines()
        assert report["total_revenue"] >= 0

    def test_viral_posts_present(self):
        bot = GodModeBot(tier=Tier.PRO)
        report = bot.run_all_engines()
        assert "viral_posts" in report
        assert isinstance(report["viral_posts"], list)

    def test_payment_stats_present(self):
        bot = GodModeBot(tier=Tier.PRO)
        report = bot.run_all_engines()
        assert "payment_stats" in report

    def test_ai_analysis_present_for_pro(self):
        bot = GodModeBot(tier=Tier.PRO)
        report = bot.run_all_engines()
        assert "ai_analysis" in report

    def test_free_tier_run_all_engines(self):
        bot = GodModeBot(tier=Tier.FREE)
        report = bot.run_all_engines()
        assert isinstance(report, dict)
        assert report["bot"] == "GodModeBot"


class TestGodModeBotGetSummary:
    def test_returns_dict(self):
        bot = GodModeBot(tier=Tier.PRO)
        summary = bot.get_summary()
        assert isinstance(summary, dict)

    def test_summary_has_required_keys(self):
        bot = GodModeBot(tier=Tier.PRO)
        summary = bot.get_summary()
        for key in ["bot", "tier", "status", "total_revenue", "total_leads", "deals_won", "mrr"]:
            assert key in summary, f"Missing summary key: {key}"

    def test_summary_status_active(self):
        bot = GodModeBot(tier=Tier.PRO)
        summary = bot.get_summary()
        assert summary["status"] == "active"

    def test_upgrade_available_for_free(self):
        bot = GodModeBot(tier=Tier.FREE)
        summary = bot.get_summary()
        assert summary["upgrade_available"] == "Pro"

    def test_upgrade_available_for_pro(self):
        bot = GodModeBot(tier=Tier.PRO)
        summary = bot.get_summary()
        assert summary["upgrade_available"] == "Enterprise"

    def test_upgrade_none_for_enterprise(self):
        bot = GodModeBot(tier=Tier.ENTERPRISE)
        summary = bot.get_summary()
        assert summary["upgrade_available"] is None

    def test_get_summary_triggers_run_if_empty(self):
        bot = GodModeBot(tier=Tier.PRO)
        assert bot._last_report == {}
        summary = bot.get_summary()
        assert bot._last_report != {}
        assert summary["total_revenue"] >= 0


# ===========================================================================
# 8. Tier gating tests
# ===========================================================================

class TestTierGating:
    def test_free_leads_capped_at_5(self):
        bot = GodModeBot(tier=Tier.FREE)
        leads = bot.hunt_leads(count=100)
        assert len(leads) <= 5

    def test_pro_leads_capped_at_20(self):
        bot = GodModeBot(tier=Tier.PRO)
        leads = bot.hunt_leads(count=100)
        assert len(leads) <= 20

    def test_enterprise_leads_uncapped(self):
        bot = GodModeBot(tier=Tier.ENTERPRISE)
        leads = bot.hunt_leads(count=50)
        assert len(leads) == 50

    def test_free_auto_closer_returns_empty(self):
        bot = GodModeBot(tier=Tier.FREE)
        leads = [{"id": "L1", "company": "X", "qualified": True}]
        result = bot.close_leads(leads)
        assert result == []

    def test_free_payment_collection_returns_error(self):
        bot = GodModeBot(tier=Tier.FREE)
        result = bot.collect_payments([{"lead_id": "L1"}])
        assert "error" in result

    def test_free_viral_posts_capped_at_3(self):
        bot = GodModeBot(tier=Tier.FREE)
        posts = bot.create_viral_content()
        assert len(posts) <= 3

    def test_pro_viral_posts_all_platforms(self):
        bot = GodModeBot(tier=Tier.PRO)
        posts = bot.create_viral_content()
        assert len(posts) == 6

    def test_free_self_improving_ai_returns_error(self):
        bot = GodModeBot(tier=Tier.FREE)
        result = bot.analyze_performance({"total_revenue": 1000, "total_leads": 5})
        assert "error" in result

    def test_pro_self_improving_ai_works(self):
        bot = GodModeBot(tier=Tier.PRO)
        result = bot.analyze_performance({"total_revenue": 3000, "total_leads": 10})
        assert "recommendations" in result

    def test_enterprise_has_all_features(self):
        bot = GodModeBot(tier=Tier.ENTERPRISE)
        cfg = bot._config
        assert cfg.has_feature(FEATURE_WHITE_LABEL)
        assert cfg.has_feature(FEATURE_API_ACCESS)
        assert cfg.has_feature(FEATURE_DEDICATED_SUPPORT)


# ===========================================================================
# 9. Error handling & edge cases
# ===========================================================================

class TestEdgeCases:
    def test_hunt_leads_zero_count(self):
        bot = GodModeBot(tier=Tier.PRO)
        leads = bot.hunt_leads(count=0)
        assert leads == []

    def test_close_empty_leads(self):
        bot = GodModeBot(tier=Tier.PRO)
        result = bot.close_leads([])
        assert result == []

    def test_collect_payments_empty_clients(self):
        bot = GodModeBot(tier=Tier.PRO)
        result = bot.collect_payments([])
        assert result["subscribers_added"] == 0

    def test_viral_content_unknown_niche(self):
        bot = GodModeBot(tier=Tier.PRO, niche="unknown_niche_xyz")
        posts = bot.create_viral_content()
        assert isinstance(posts, list)

    def test_analyze_performance_missing_keys(self):
        bot = GodModeBot(tier=Tier.PRO)
        result = bot.analyze_performance({})
        assert isinstance(result, dict)

    def test_run_all_engines_multiple_cycles(self):
        bot = GodModeBot(tier=Tier.PRO)
        for _ in range(3):
            report = bot.run_all_engines()
            assert report["total_revenue"] >= 0

    def test_payment_collector_state_independent(self):
        bot1 = GodModeBot(tier=Tier.PRO)
        bot2 = GodModeBot(tier=Tier.PRO)
        bot1.collect_payments([{"lead_id": "A"}])
        result2 = bot2.collect_payments([{"lead_id": "B"}])
        assert result2["total_invoices"] == 1


# ===========================================================================
# 10. Bot Library registration
# ===========================================================================

class TestBotLibraryRegistration:
    def test_god_mode_bot_in_library(self):
        from bots.global_bot_network.bot_library import BotLibrary, BotNotFound
        lib = BotLibrary()
        lib.populate_dreamco_bots()
        try:
            entry = lib.get_bot("god_mode_bot")
            assert entry.bot_id == "god_mode_bot"
        except BotNotFound:
            raise AssertionError("god_mode_bot not found in library")

    def test_god_mode_bot_entry_fields(self):
        from bots.global_bot_network.bot_library import BotLibrary
        lib = BotLibrary()
        lib.populate_dreamco_bots()
        entry = lib.get_bot("god_mode_bot")
        assert entry.display_name == "God Mode Bot"
        assert entry.class_name == "GodModeBot"
        assert entry.module_path == "bots.god_mode_bot.god_mode_bot"

    def test_god_mode_bot_capabilities(self):
        from bots.global_bot_network.bot_library import BotLibrary
        lib = BotLibrary()
        lib.populate_dreamco_bots()
        entry = lib.get_bot("god_mode_bot")
        expected = ["lead_hunting", "auto_closing", "payment_collection", "viral_engine", "god_mode"]
        for cap in expected:
            assert cap in entry.capabilities, f"Missing capability: {cap}"
