"""
Tests for bots/dream_sales_pro/tiers.py and
         bots/dream_sales_pro/dream_sales_pro_bot.py

Run with:
    python -m pytest tests/test_dream_sales_pro.py -v
"""
# GLOBAL AI SOURCES FLOW

import os
import sys

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

from bots.dream_sales_pro.tiers import DSPtier, get_tier_config, get_upgrade_path
from bots.dream_sales_pro.dream_sales_pro_bot import (
    DreamSalesProBot,
    DSPAccessError,
)


# ---------------------------------------------------------------------------
# Tier configuration tests
# ---------------------------------------------------------------------------


class TestDSPtierConfig:
    def test_pro_tier_exists(self):
        assert get_tier_config(DSPtier.PRO) is not None

    def test_enterprise_tier_exists(self):
        assert get_tier_config(DSPtier.ENTERPRISE) is not None

    def test_pro_name(self):
        assert get_tier_config(DSPtier.PRO).name == "Pro"

    def test_enterprise_name(self):
        assert get_tier_config(DSPtier.ENTERPRISE).name == "Enterprise"

    def test_pro_price_positive(self):
        config = get_tier_config(DSPtier.PRO)
        assert config.monthly_price_usd > 0

    def test_enterprise_price_gte_499(self):
        config = get_tier_config(DSPtier.ENTERPRISE)
        assert config.monthly_price_usd >= 499.0

    def test_pro_has_features(self):
        assert len(get_tier_config(DSPtier.PRO).features) > 0

    def test_enterprise_has_more_features(self):
        pro = get_tier_config(DSPtier.PRO)
        ent = get_tier_config(DSPtier.ENTERPRISE)
        assert len(ent.features) > len(pro.features)

    def test_enterprise_api_access(self):
        assert get_tier_config(DSPtier.ENTERPRISE).api_access is True

    def test_pro_no_api_access(self):
        assert get_tier_config(DSPtier.PRO).api_access is False

    def test_has_feature_present(self):
        config = get_tier_config(DSPtier.ENTERPRISE)
        assert config.has_feature("white_label_saas") is True

    def test_has_feature_absent(self):
        config = get_tier_config(DSPtier.PRO)
        assert config.has_feature("white_label_saas") is False

    def test_has_feature_unknown_returns_false(self):
        config = get_tier_config(DSPtier.PRO)
        assert config.has_feature("does_not_exist") is False

    def test_pro_support_level(self):
        assert get_tier_config(DSPtier.PRO).support_level

    def test_enterprise_support_level(self):
        assert get_tier_config(DSPtier.ENTERPRISE).support_level


class TestDSPUpgradePath:
    def test_pro_upgrades_to_enterprise(self):
        assert get_upgrade_path(DSPtier.PRO) == DSPtier.ENTERPRISE

    def test_enterprise_no_upgrade(self):
        assert get_upgrade_path(DSPtier.ENTERPRISE) is None


# ---------------------------------------------------------------------------
# DreamSalesProBot instantiation
# ---------------------------------------------------------------------------


class TestDSPBotInstantiation:
    def test_default_tier_is_pro(self):
        bot = DreamSalesProBot()
        assert bot.tier == DSPtier.PRO

    def test_enterprise_tier(self):
        bot = DreamSalesProBot(tier=DSPtier.ENTERPRISE)
        assert bot.tier == DSPtier.ENTERPRISE

    def test_config_loaded(self):
        assert DreamSalesProBot().config is not None

    def test_bots_catalogue_is_list(self):
        assert isinstance(DreamSalesProBot()._bots, list)

    def test_bots_catalogue_not_empty(self):
        assert len(DreamSalesProBot()._bots) > 0


# ---------------------------------------------------------------------------
# run()
# ---------------------------------------------------------------------------


class TestDSPBotRun:
    def test_run_returns_string(self):
        assert isinstance(DreamSalesProBot().run(), str)

    def test_run_contains_tier_pro(self):
        assert "Pro" in DreamSalesProBot(tier=DSPtier.PRO).run()

    def test_run_contains_tier_enterprise(self):
        assert "Enterprise" in DreamSalesProBot(tier=DSPtier.ENTERPRISE).run()

    def test_run_mentions_division(self):
        assert "DreamSalesPro" in DreamSalesProBot().run()


# ---------------------------------------------------------------------------
# Catalogue helpers
# ---------------------------------------------------------------------------


class TestDSPCatalogueHelpers:
    def test_list_bots_returns_list(self):
        bot = DreamSalesProBot()
        assert isinstance(bot.list_bots(), list)

    def test_list_bots_all(self):
        bot = DreamSalesProBot()
        assert len(bot.list_bots()) > 0

    def test_list_bots_by_category(self):
        bot = DreamSalesProBot()
        results = bot.list_bots(category="Leads")
        assert all("Leads" in b["category"] for b in results)

    def test_list_bots_by_tier(self):
        bot = DreamSalesProBot()
        results = bot.list_bots(tier_filter="Enterprise")
        assert all(b["tier"] == "Enterprise" for b in results)

    def test_list_bots_case_insensitive(self):
        bot = DreamSalesProBot()
        lower = bot.list_bots(category="leads")
        upper = bot.list_bots(category="Leads")
        assert len(lower) == len(upper)

    def test_get_bot_found(self):
        bot = DreamSalesProBot()
        result = bot.get_bot("lead-scraper")
        assert result is not None
        assert result["botId"] == "lead-scraper"

    def test_get_bot_not_found(self):
        bot = DreamSalesProBot()
        assert bot.get_bot("this-bot-does-not-exist") is None

    def test_list_categories_sorted(self):
        bot = DreamSalesProBot()
        cats = bot.list_categories()
        assert cats == sorted(cats)

    def test_list_categories_not_empty(self):
        assert len(DreamSalesProBot().list_categories()) > 0

    def test_analytics_category_present(self):
        assert "Analytics" in DreamSalesProBot().list_categories()

    def test_leads_category_present(self):
        assert "Leads" in DreamSalesProBot().list_categories()


# ---------------------------------------------------------------------------
# Lead generation
# ---------------------------------------------------------------------------


class TestDSPLeadGeneration:
    def test_returns_dict(self):
        bot = DreamSalesProBot()
        result = bot.generate_leads(icp={"industry": "SaaS"})
        assert isinstance(result, dict)

    def test_has_required_keys(self):
        bot = DreamSalesProBot()
        result = bot.generate_leads(icp={"industry": "SaaS"})
        for key in ("division", "task", "icp", "leads", "leads_generated"):
            assert key in result

    def test_division_is_dream_sales_pro(self):
        bot = DreamSalesProBot()
        result = bot.generate_leads(icp={})
        assert result["division"] == "DreamSalesPro"

    def test_task_is_lead_generation(self):
        bot = DreamSalesProBot()
        result = bot.generate_leads(icp={})
        assert result["task"] == "lead_generation"

    def test_leads_count_matches_count_param(self):
        bot = DreamSalesProBot()
        result = bot.generate_leads(icp={}, count=5)
        assert result["leads_generated"] == 5
        assert len(result["leads"]) == 5

    def test_leads_have_email_confidence(self):
        bot = DreamSalesProBot()
        result = bot.generate_leads(icp={}, count=3)
        for lead in result["leads"]:
            assert "email_confidence" in lead

    def test_deterministic_for_same_icp(self):
        bot = DreamSalesProBot()
        r1 = bot.generate_leads(icp={"industry": "SaaS"}, count=5)
        r2 = bot.generate_leads(icp={"industry": "SaaS"}, count=5)
        assert r1["leads_generated"] == r2["leads_generated"]
        assert r1["leads"] == r2["leads"]


# ---------------------------------------------------------------------------
# Outreach campaign
# ---------------------------------------------------------------------------


class TestDSPOutreachCampaign:
    def test_returns_dict(self):
        bot = DreamSalesProBot()
        result = bot.execute_outreach_campaign(campaign_id="CAMP-001")
        assert isinstance(result, dict)

    def test_has_required_keys(self):
        bot = DreamSalesProBot()
        result = bot.execute_outreach_campaign(campaign_id="CAMP-001")
        for key in ("division", "task", "campaign_id", "results", "status"):
            assert key in result

    def test_status_executed(self):
        bot = DreamSalesProBot()
        result = bot.execute_outreach_campaign(campaign_id="CAMP-001")
        assert result["status"] == "executed"

    def test_results_has_channels(self):
        bot = DreamSalesProBot()
        result = bot.execute_outreach_campaign(
            campaign_id="CAMP-001", channels=["email"]
        )
        assert "email" in result["results"]

    def test_custom_channels(self):
        bot = DreamSalesProBot()
        result = bot.execute_outreach_campaign(
            campaign_id="CAMP-002", channels=["email", "sms"]
        )
        assert "email" in result["results"]
        assert "sms" in result["results"]

    def test_max_sends_respected(self):
        bot = DreamSalesProBot()
        max_sends = 100
        result = bot.execute_outreach_campaign(
            campaign_id="CAMP-003", channels=["email"], max_sends=max_sends
        )
        assert result["results"]["email"]["sent"] <= max_sends


# ---------------------------------------------------------------------------
# Revenue simulation
# ---------------------------------------------------------------------------


class TestDSPRevenueSimulation:
    def test_returns_dict(self):
        bot = DreamSalesProBot()
        result = bot.simulate_revenue(mrr=10000, growth_rate=0.10)
        assert isinstance(result, dict)

    def test_has_required_keys(self):
        bot = DreamSalesProBot()
        result = bot.simulate_revenue(mrr=10000, growth_rate=0.10)
        for key in ("division", "task", "inputs", "projections", "summary"):
            assert key in result

    def test_projections_length(self):
        bot = DreamSalesProBot()
        result = bot.simulate_revenue(mrr=10000, growth_rate=0.10, months=6)
        assert len(result["projections"]) == 6

    def test_summary_has_arr(self):
        bot = DreamSalesProBot()
        result = bot.simulate_revenue(mrr=10000, growth_rate=0.10)
        assert "arr_usd" in result["summary"]

    def test_mrr_grows_with_positive_growth(self):
        bot = DreamSalesProBot()
        result = bot.simulate_revenue(mrr=10000, growth_rate=0.20, churn_rate=0.02)
        assert result["projections"][-1]["mrr_usd"] > 10000

    def test_invalid_months_raises(self):
        bot = DreamSalesProBot()
        with pytest.raises(ValueError):
            bot.simulate_revenue(mrr=10000, growth_rate=0.10, months=0)

    def test_invalid_churn_raises(self):
        bot = DreamSalesProBot()
        with pytest.raises(ValueError):
            bot.simulate_revenue(mrr=10000, growth_rate=0.10, churn_rate=1.5)

    def test_zero_mrr(self):
        bot = DreamSalesProBot()
        result = bot.simulate_revenue(mrr=0, growth_rate=0.10)
        assert result["summary"]["final_mrr_usd"] == 0.0


# ---------------------------------------------------------------------------
# Pipeline summary
# ---------------------------------------------------------------------------


class TestDSPPipelineSummary:
    def test_returns_dict(self):
        bot = DreamSalesProBot()
        result = bot.get_pipeline_summary(pipeline_id="PIPE-001")
        assert isinstance(result, dict)

    def test_has_required_keys(self):
        bot = DreamSalesProBot()
        result = bot.get_pipeline_summary(pipeline_id="PIPE-001")
        for key in ("division", "task", "pipeline_id", "stages", "pipeline_health"):
            assert key in result

    def test_stages_is_list(self):
        bot = DreamSalesProBot()
        result = bot.get_pipeline_summary(pipeline_id="PIPE-001")
        assert isinstance(result["stages"], list)

    def test_custom_stages(self):
        bot = DreamSalesProBot()
        stages = ["Discovery", "Proposal"]
        result = bot.get_pipeline_summary(pipeline_id="PIPE-002", stages=stages)
        assert len(result["stages"]) == 2

    def test_weighted_pipeline_is_numeric(self):
        bot = DreamSalesProBot()
        result = bot.get_pipeline_summary(pipeline_id="PIPE-001")
        assert isinstance(result["total_weighted_pipeline_usd"], (int, float))


# ---------------------------------------------------------------------------
# Payment info
# ---------------------------------------------------------------------------


class TestDSPPaymentInfo:
    def test_found_bot(self):
        bot = DreamSalesProBot()
        result = bot.get_payment_info("lead-scraper")
        assert "error" not in result
        assert result["bot_id"] == "lead-scraper"

    def test_unknown_bot(self):
        bot = DreamSalesProBot()
        result = bot.get_payment_info("no-such-bot")
        assert "error" in result

    def test_has_checkout_params(self):
        bot = DreamSalesProBot()
        result = bot.get_payment_info("cold-email-engine")
        assert "checkout_params" in result

    def test_checkout_params_division(self):
        bot = DreamSalesProBot()
        result = bot.get_payment_info("cold-email-engine")
        assert result["checkout_params"]["division"] == "DreamSalesPro"


# ---------------------------------------------------------------------------
# describe_tier
# ---------------------------------------------------------------------------


class TestDSPDescribeTier:
    def test_returns_string(self):
        assert isinstance(DreamSalesProBot().describe_tier(), str)

    def test_contains_pro(self):
        assert "Pro" in DreamSalesProBot(tier=DSPtier.PRO).describe_tier()

    def test_enterprise_upgrade_absent(self):
        bot = DreamSalesProBot(tier=DSPtier.ENTERPRISE)
        assert "Upgrade" not in bot.describe_tier()

    def test_pro_upgrade_present(self):
        bot = DreamSalesProBot(tier=DSPtier.PRO)
        assert "Enterprise" in bot.describe_tier()


# ---------------------------------------------------------------------------
# Feature gating
# ---------------------------------------------------------------------------


class TestDSPFeatureGating:
    def test_enterprise_feature_blocked_on_pro(self):
        bot = DreamSalesProBot(tier=DSPtier.PRO)
        with pytest.raises(DSPAccessError):
            bot._require_feature("white_label_saas")

    def test_enterprise_feature_allowed(self):
        bot = DreamSalesProBot(tier=DSPtier.ENTERPRISE)
        bot._require_feature("white_label_saas")  # should not raise

    def test_pro_feature_allowed_on_pro(self):
        bot = DreamSalesProBot(tier=DSPtier.PRO)
        bot._require_feature("saas_subscription")

    def test_pro_feature_allowed_on_enterprise(self):
        bot = DreamSalesProBot(tier=DSPtier.ENTERPRISE)
        bot._require_feature("saas_subscription")
