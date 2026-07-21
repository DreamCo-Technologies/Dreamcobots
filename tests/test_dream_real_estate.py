"""
Tests for bots/dream_real_estate/tiers.py and
         bots/dream_real_estate/dream_real_estate_bot.py

Run with:
    python -m pytest tests/test_dream_real_estate.py -v
"""
# GLOBAL AI SOURCES FLOW

import os
import sys

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

from bots.dream_real_estate.tiers import DREtier, get_tier_config, get_upgrade_path
from bots.dream_real_estate.dream_real_estate_bot import (
    DreamRealEstateBot,
    DREAccessError,
)


# ---------------------------------------------------------------------------
# Tier configuration tests
# ---------------------------------------------------------------------------


class TestDREtierConfig:
    def test_pro_tier_exists(self):
        config = get_tier_config(DREtier.PRO)
        assert config is not None

    def test_enterprise_tier_exists(self):
        config = get_tier_config(DREtier.ENTERPRISE)
        assert config is not None

    def test_pro_has_name(self):
        config = get_tier_config(DREtier.PRO)
        assert config.name == "Pro"

    def test_enterprise_has_name(self):
        config = get_tier_config(DREtier.ENTERPRISE)
        assert config.name == "Enterprise"

    def test_pro_has_price(self):
        config = get_tier_config(DREtier.PRO)
        assert config.monthly_price_usd is not None
        assert config.monthly_price_usd > 0

    def test_enterprise_has_price(self):
        config = get_tier_config(DREtier.ENTERPRISE)
        assert config.monthly_price_usd is not None
        assert config.monthly_price_usd >= 499.0

    def test_pro_has_features(self):
        config = get_tier_config(DREtier.PRO)
        assert len(config.features) > 0

    def test_enterprise_has_more_features_than_pro(self):
        pro = get_tier_config(DREtier.PRO)
        ent = get_tier_config(DREtier.ENTERPRISE)
        assert len(ent.features) > len(pro.features)

    def test_enterprise_has_api_access(self):
        config = get_tier_config(DREtier.ENTERPRISE)
        assert config.api_access is True

    def test_pro_no_api_access(self):
        config = get_tier_config(DREtier.PRO)
        assert config.api_access is False

    def test_has_feature_true(self):
        config = get_tier_config(DREtier.ENTERPRISE)
        assert config.has_feature("api_access") is True

    def test_has_feature_false(self):
        config = get_tier_config(DREtier.PRO)
        assert config.has_feature("api_access") is False

    def test_has_feature_unknown(self):
        config = get_tier_config(DREtier.PRO)
        assert config.has_feature("nonexistent_feature") is False

    def test_pro_has_support_level(self):
        config = get_tier_config(DREtier.PRO)
        assert config.support_level

    def test_enterprise_has_support_level(self):
        config = get_tier_config(DREtier.ENTERPRISE)
        assert config.support_level


class TestDREUpgradePath:
    def test_pro_upgrades_to_enterprise(self):
        assert get_upgrade_path(DREtier.PRO) == DREtier.ENTERPRISE

    def test_enterprise_has_no_upgrade(self):
        assert get_upgrade_path(DREtier.ENTERPRISE) is None


# ---------------------------------------------------------------------------
# DreamRealEstateBot instantiation tests
# ---------------------------------------------------------------------------


class TestDREBotInstantiation:
    def test_default_tier_is_pro(self):
        bot = DreamRealEstateBot()
        assert bot.tier == DREtier.PRO

    def test_enterprise_tier(self):
        bot = DreamRealEstateBot(tier=DREtier.ENTERPRISE)
        assert bot.tier == DREtier.ENTERPRISE

    def test_config_loaded(self):
        bot = DreamRealEstateBot()
        assert bot.config is not None

    def test_bots_catalogue_loaded(self):
        bot = DreamRealEstateBot()
        # catalogue should either have bots or be empty (graceful degradation)
        assert isinstance(bot._bots, list)

    def test_bots_catalogue_not_empty(self):
        bot = DreamRealEstateBot()
        assert len(bot._bots) > 0


# ---------------------------------------------------------------------------
# run() method
# ---------------------------------------------------------------------------


class TestDREBotRun:
    def test_run_returns_string(self):
        bot = DreamRealEstateBot()
        result = bot.run()
        assert isinstance(result, str)

    def test_run_contains_tier(self):
        bot = DreamRealEstateBot(tier=DREtier.PRO)
        assert "Pro" in bot.run()

    def test_run_enterprise(self):
        bot = DreamRealEstateBot(tier=DREtier.ENTERPRISE)
        assert "Enterprise" in bot.run()

    def test_run_mentions_division(self):
        bot = DreamRealEstateBot()
        assert "DreamRealEstate" in bot.run()


# ---------------------------------------------------------------------------
# Catalogue helpers
# ---------------------------------------------------------------------------


class TestDRECatalogueHelpers:
    def test_list_bots_returns_list(self):
        bot = DreamRealEstateBot()
        assert isinstance(bot.list_bots(), list)

    def test_list_bots_all(self):
        bot = DreamRealEstateBot()
        all_bots = bot.list_bots()
        assert len(all_bots) > 0

    def test_list_bots_by_category(self):
        bot = DreamRealEstateBot()
        results = bot.list_bots(category="Tax")
        assert all("Tax" in b["category"] for b in results)

    def test_list_bots_by_tier(self):
        bot = DreamRealEstateBot()
        results = bot.list_bots(tier_filter="Enterprise")
        assert all(b["tier"] == "Enterprise" for b in results)

    def test_list_bots_category_case_insensitive(self):
        bot = DreamRealEstateBot()
        lower = bot.list_bots(category="tax")
        upper = bot.list_bots(category="Tax")
        assert len(lower) == len(upper)

    def test_get_bot_found(self):
        bot = DreamRealEstateBot()
        result = bot.get_bot("commercial-scanner")
        assert result is not None
        assert result["botId"] == "commercial-scanner"

    def test_get_bot_not_found(self):
        bot = DreamRealEstateBot()
        result = bot.get_bot("nonexistent-bot-xyz")
        assert result is None

    def test_list_categories_returns_list(self):
        bot = DreamRealEstateBot()
        cats = bot.list_categories()
        assert isinstance(cats, list)

    def test_list_categories_sorted(self):
        bot = DreamRealEstateBot()
        cats = bot.list_categories()
        assert cats == sorted(cats)

    def test_list_categories_not_empty(self):
        bot = DreamRealEstateBot()
        assert len(bot.list_categories()) > 0

    def test_acquisition_category_present(self):
        bot = DreamRealEstateBot()
        assert "Acquisition" in bot.list_categories()

    def test_tax_category_present(self):
        bot = DreamRealEstateBot()
        assert "Tax" in bot.list_categories()


# ---------------------------------------------------------------------------
# Acquisition scan
# ---------------------------------------------------------------------------


class TestDREAcquisitionScan:
    def test_returns_dict(self):
        bot = DreamRealEstateBot()
        result = bot.scan_acquisitions(market="Austin TX")
        assert isinstance(result, dict)

    def test_has_required_keys(self):
        bot = DreamRealEstateBot()
        result = bot.scan_acquisitions(market="Austin TX")
        for key in ("division", "task", "market", "alerts", "timestamp"):
            assert key in result

    def test_division_is_dream_real_estate(self):
        bot = DreamRealEstateBot()
        result = bot.scan_acquisitions(market="Phoenix AZ")
        assert result["division"] == "DreamRealEstate"

    def test_task_is_acquisition_scan(self):
        bot = DreamRealEstateBot()
        result = bot.scan_acquisitions(market="Austin TX")
        assert result["task"] == "acquisition_scan"

    def test_alerts_is_list(self):
        bot = DreamRealEstateBot()
        result = bot.scan_acquisitions(market="Austin TX")
        assert isinstance(result["alerts"], list)

    def test_alerts_cap_rate_within_max(self):
        bot = DreamRealEstateBot()
        max_cap = 6.5
        result = bot.scan_acquisitions(market="Austin TX", max_cap_rate=max_cap)
        for alert in result["alerts"]:
            assert alert["cap_rate_pct"] <= max_cap

    def test_market_field_preserved(self):
        bot = DreamRealEstateBot()
        result = bot.scan_acquisitions(market="Tampa FL")
        assert result["market"] == "Tampa FL"

    def test_deterministic_for_same_inputs(self):
        bot = DreamRealEstateBot()
        r1 = bot.scan_acquisitions(market="Austin TX")
        r2 = bot.scan_acquisitions(market="Austin TX")
        assert r1["deals_found"] == r2["deals_found"]
        # alert_time varies between calls; compare the deterministic fields only
        for a1, a2 in zip(r1["alerts"], r2["alerts"]):
            for key in ("deal_id", "address", "price_usd", "cap_rate_pct",
                        "property_type", "status"):
                assert a1[key] == a2[key]


# ---------------------------------------------------------------------------
# Predictive maintenance
# ---------------------------------------------------------------------------


class TestDREPredictiveMaintenance:
    def test_returns_dict(self):
        bot = DreamRealEstateBot()
        result = bot.run_predictive_maintenance(building_id="BLD-001")
        assert isinstance(result, dict)

    def test_has_required_keys(self):
        bot = DreamRealEstateBot()
        result = bot.run_predictive_maintenance(building_id="BLD-001")
        for key in ("division", "task", "building_id", "alerts", "overall_health"):
            assert key in result

    def test_division_is_correct(self):
        bot = DreamRealEstateBot()
        result = bot.run_predictive_maintenance(building_id="BLD-001")
        assert result["division"] == "DreamRealEstate"

    def test_task_is_predictive_maintenance(self):
        bot = DreamRealEstateBot()
        result = bot.run_predictive_maintenance(building_id="BLD-001")
        assert result["task"] == "predictive_maintenance"

    def test_alerts_is_list(self):
        bot = DreamRealEstateBot()
        result = bot.run_predictive_maintenance(building_id="BLD-001")
        assert isinstance(result["alerts"], list)

    def test_custom_sensors(self):
        bot = DreamRealEstateBot()
        sensors = ["HVAC", "Boiler"]
        result = bot.run_predictive_maintenance(building_id="BLD-002", sensors=sensors)
        assert result["sensors_evaluated"] == sensors

    def test_overall_health_string(self):
        bot = DreamRealEstateBot()
        result = bot.run_predictive_maintenance(building_id="BLD-001")
        assert isinstance(result["overall_health"], str)


# ---------------------------------------------------------------------------
# Analytics dashboard
# ---------------------------------------------------------------------------


class TestDREAnalyticsDashboard:
    def test_returns_dict(self):
        bot = DreamRealEstateBot()
        result = bot.generate_analytics_dashboard(portfolio_id="PORT-001")
        assert isinstance(result, dict)

    def test_has_dashboard_key(self):
        bot = DreamRealEstateBot()
        result = bot.generate_analytics_dashboard(portfolio_id="PORT-001")
        assert "dashboard" in result

    def test_dashboard_has_portfolio_id(self):
        bot = DreamRealEstateBot()
        result = bot.generate_analytics_dashboard(portfolio_id="PORT-042")
        assert result["dashboard"]["portfolio_id"] == "PORT-042"

    def test_custom_metrics(self):
        bot = DreamRealEstateBot()
        metrics = ["cap_rate_pct", "noi_usd"]
        result = bot.generate_analytics_dashboard(
            portfolio_id="PORT-001", metrics=metrics
        )
        for m in metrics:
            assert m in result["dashboard"]


# ---------------------------------------------------------------------------
# Investor report
# ---------------------------------------------------------------------------


class TestDREInvestorReport:
    def test_returns_dict(self):
        bot = DreamRealEstateBot()
        result = bot.generate_investor_report(fund_id="FUND-001")
        assert isinstance(result, dict)

    def test_has_report_key(self):
        bot = DreamRealEstateBot()
        result = bot.generate_investor_report(fund_id="FUND-001")
        assert "report" in result

    def test_report_has_irr(self):
        bot = DreamRealEstateBot()
        result = bot.generate_investor_report(fund_id="FUND-001")
        assert "irr_pct" in result["report"]

    def test_custom_quarter(self):
        bot = DreamRealEstateBot()
        result = bot.generate_investor_report(fund_id="FUND-001", quarter="2025-Q2")
        assert result["quarter"] == "2025-Q2"

    def test_default_quarter_set(self):
        bot = DreamRealEstateBot()
        result = bot.generate_investor_report(fund_id="FUND-001")
        assert result["quarter"] is not None
        assert "Q" in result["quarter"]


# ---------------------------------------------------------------------------
# Payment info
# ---------------------------------------------------------------------------


class TestDREPaymentInfo:
    def test_found_bot(self):
        bot = DreamRealEstateBot()
        result = bot.get_payment_info("commercial-scanner")
        assert "error" not in result
        assert result["bot_id"] == "commercial-scanner"

    def test_unknown_bot(self):
        bot = DreamRealEstateBot()
        result = bot.get_payment_info("no-such-bot")
        assert "error" in result

    def test_payment_info_has_checkout_params(self):
        bot = DreamRealEstateBot()
        result = bot.get_payment_info("urban-heatmap")
        assert "checkout_params" in result

    def test_checkout_params_has_product(self):
        bot = DreamRealEstateBot()
        result = bot.get_payment_info("urban-heatmap")
        assert result["checkout_params"]["product"] == "urban-heatmap"


# ---------------------------------------------------------------------------
# describe_tier
# ---------------------------------------------------------------------------


class TestDREDescribeTier:
    def test_returns_string(self):
        bot = DreamRealEstateBot()
        assert isinstance(bot.describe_tier(), str)

    def test_contains_tier_name(self):
        bot = DreamRealEstateBot(tier=DREtier.PRO)
        assert "Pro" in bot.describe_tier()

    def test_enterprise_contains_api(self):
        bot = DreamRealEstateBot(tier=DREtier.ENTERPRISE)
        assert "api_access" in bot.describe_tier()

    def test_pro_upgrade_hint(self):
        bot = DreamRealEstateBot(tier=DREtier.PRO)
        assert "Enterprise" in bot.describe_tier()

    def test_enterprise_no_upgrade_hint(self):
        bot = DreamRealEstateBot(tier=DREtier.ENTERPRISE)
        assert "Upgrade" not in bot.describe_tier()


# ---------------------------------------------------------------------------
# Feature gating
# ---------------------------------------------------------------------------


class TestDREFeatureGating:
    def test_enterprise_feature_blocked_on_pro(self):
        bot = DreamRealEstateBot(tier=DREtier.PRO)
        with pytest.raises(DREAccessError):
            bot._require_feature("api_access")

    def test_enterprise_feature_allowed_on_enterprise(self):
        bot = DreamRealEstateBot(tier=DREtier.ENTERPRISE)
        # Should not raise
        bot._require_feature("api_access")

    def test_pro_feature_allowed_on_pro(self):
        bot = DreamRealEstateBot(tier=DREtier.PRO)
        bot._require_feature("saas_subscription")

    def test_pro_feature_allowed_on_enterprise(self):
        bot = DreamRealEstateBot(tier=DREtier.ENTERPRISE)
        bot._require_feature("saas_subscription")
