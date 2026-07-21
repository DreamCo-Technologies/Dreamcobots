"""
Tests for bots/discount_dominator — settings 401–600 and interoperability modules.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest

from bots.discount_dominator.settings import (
    Setting,
    DISCOUNT_DOMINATOR_SETTINGS,
    SETTINGS_BY_GROUP,
    ALL_GROUPS,
    GROUP_ANALYTICS,
    GROUP_INSTORE,
    GROUP_ONLINE,
    GROUP_ENTERPRISE,
    GROUP_BEHAVIORAL,
    get_setting,
    apply_settings,
    get_group_settings,
    reset_all,
    as_dict,
)
from bots.discount_dominator.analytics import AdvancedAnalytics
from bots.discount_dominator.in_store_controls import InStoreTacticalControls
from bots.discount_dominator.online_optimization import OnlinePlatformOptimization
from bots.discount_dominator.enterprise_features import EnterpriseFeatures
from bots.discount_dominator.behavioral_settings import BehavioralSettings
from bots.discount_dominator.real_estate_optimizer import RealEstateOptimizer
from bots.discount_dominator.car_flipping_bot import CarFlippingBot
from bots.discount_dominator.retail_intelligence import RetailIntelligenceNetwork
from bots.discount_dominator.discount_dominator import DiscountDominator


@pytest.fixture(autouse=True)
def reset_settings():
    """Reset all settings to defaults before each test."""
    reset_all()
    yield
    reset_all()


# ---------------------------------------------------------------------------
# Settings registry tests
# ---------------------------------------------------------------------------

class TestSettingsRegistry:
    def test_total_setting_count(self):
        assert len(DISCOUNT_DOMINATOR_SETTINGS) == 200

    def test_settings_range(self):
        ids = list(DISCOUNT_DOMINATOR_SETTINGS.keys())
        assert min(ids) == 401
        assert max(ids) == 600

    def test_all_ids_sequential(self):
        ids = sorted(DISCOUNT_DOMINATOR_SETTINGS.keys())
        assert ids == list(range(401, 601))

    def test_all_groups_present(self):
        assert set(SETTINGS_BY_GROUP.keys()) == set(ALL_GROUPS)

    def test_analytics_group_range(self):
        analytics = get_group_settings(GROUP_ANALYTICS)
        ids = [s.id for s in analytics]
        assert min(ids) == 401
        assert max(ids) == 450
        assert len(ids) == 50

    def test_instore_group_range(self):
        instore = get_group_settings(GROUP_INSTORE)
        ids = [s.id for s in instore]
        assert min(ids) == 451
        assert max(ids) == 500
        assert len(ids) == 50

    def test_online_group_range(self):
        online = get_group_settings(GROUP_ONLINE)
        ids = [s.id for s in online]
        assert min(ids) == 501
        assert max(ids) == 550
        assert len(ids) == 50

    def test_enterprise_group_range(self):
        enterprise = get_group_settings(GROUP_ENTERPRISE)
        ids = [s.id for s in enterprise]
        assert min(ids) == 551
        assert max(ids) == 580
        assert len(ids) == 30

    def test_behavioral_group_range(self):
        behavioral = get_group_settings(GROUP_BEHAVIORAL)
        ids = [s.id for s in behavioral]
        assert min(ids) == 581
        assert max(ids) == 600
        assert len(ids) == 20

    def test_get_setting_valid(self):
        s = get_setting(401)
        assert isinstance(s, Setting)
        assert s.id == 401
        assert s.name == "realtime_analytics_enabled"

    def test_get_setting_invalid(self):
        with pytest.raises(KeyError):
            get_setting(400)

    def test_get_setting_boundary_high(self):
        s = get_setting(600)
        assert s.id == 600

    def test_get_setting_above_range(self):
        with pytest.raises(KeyError):
            get_setting(601)

    def test_apply_settings_single(self):
        apply_settings({402: 180})
        assert get_setting(402).value == 180

    def test_apply_settings_multiple(self):
        apply_settings({401: False, 402: 365, 432: "EUR"})
        assert get_setting(401).value is False
        assert get_setting(402).value == 365
        assert get_setting(432).value == "EUR"

    def test_apply_settings_unknown_id_ignored(self):
        apply_settings({999: "ignored"})  # Should not raise

    def test_reset_all_restores_defaults(self):
        apply_settings({401: False, 402: 999})
        reset_all()
        assert get_setting(401).value is True
        assert get_setting(402).value == 90

    def test_as_dict_all(self):
        d = as_dict()
        assert len(d) == 200
        assert 401 in d and 600 in d

    def test_as_dict_group(self):
        d = as_dict(GROUP_ANALYTICS)
        assert len(d) == 50
        assert all(401 <= k <= 450 for k in d)

    def test_as_dict_invalid_group(self):
        with pytest.raises(KeyError):
            as_dict("nonexistent_group")

    def test_setting_reset(self):
        s = get_setting(402)
        s.value = 999
        s.reset()
        assert s.value == 90

    def test_all_settings_have_non_none_values(self):
        for s in DISCOUNT_DOMINATOR_SETTINGS.values():
            assert s.value is not None, f"Setting {s.id} has None value"

    def test_all_settings_have_descriptions(self):
        for s in DISCOUNT_DOMINATOR_SETTINGS.values():
            assert s.description, f"Setting {s.id} missing description"

    def test_all_settings_have_names(self):
        for s in DISCOUNT_DOMINATOR_SETTINGS.values():
            assert s.name, f"Setting {s.id} missing name"


# ---------------------------------------------------------------------------
# Advanced Analytics tests
# ---------------------------------------------------------------------------

class TestAdvancedAnalytics:
    def test_instantiation(self):
        a = AdvancedAnalytics()
        assert a is not None

    def test_realtime_enabled_default(self):
        a = AdvancedAnalytics()
        assert a.realtime_enabled is True

    def test_retention_days_default(self):
        a = AdvancedAnalytics()
        assert a.retention_days == 90

    def test_base_currency_default(self):
        a = AdvancedAnalytics()
        assert a.base_currency == "USD"

    def test_export_format_default(self):
        a = AdvancedAnalytics()
        assert a.export_format == "json"

    def test_override_at_construction(self):
        a = AdvancedAnalytics(overrides={402: 180, 432: "GBP"})
        assert a.retention_days == 180
        assert a.base_currency == "GBP"

    def test_get_all_settings_returns_50(self):
        a = AdvancedAnalytics()
        d = a.get_all_settings()
        assert len(d) == 50

    def test_get_enabled_features_list(self):
        a = AdvancedAnalytics()
        feats = a.get_enabled_features()
        assert isinstance(feats, list)
        assert "realtime_analytics_enabled" in feats

    def test_configure_for_real_estate(self):
        a = AdvancedAnalytics()
        a.configure_for_real_estate()
        assert a.real_estate_price_index is True

    def test_configure_for_car_flipping(self):
        a = AdvancedAnalytics()
        a.configure_for_car_flipping()
        assert a.auto_parts_market_feed is True
        assert a.competitor_monitoring is True

    def test_configure_for_retail_intelligence(self):
        a = AdvancedAnalytics()
        a.configure_for_retail_intelligence()
        assert a.retail_basket_analysis is True
        assert a.cross_bot_data_sharing is True

    def test_summary_keys(self):
        a = AdvancedAnalytics()
        s = a.summary()
        assert "realtime_enabled" in s
        assert "base_currency" in s
        assert "enabled_feature_count" in s

    def test_analytics_api_enabled_default(self):
        a = AdvancedAnalytics()
        assert a.analytics_api_enabled is True


# ---------------------------------------------------------------------------
# In-Store Tactical Controls tests
# ---------------------------------------------------------------------------

class TestInStoreTacticalControls:
    def test_instantiation(self):
        c = InStoreTacticalControls()
        assert c is not None

    def test_display_optimisation_default(self):
        c = InStoreTacticalControls()
        assert c.display_optimisation is True

    def test_shelf_placement_default(self):
        c = InStoreTacticalControls()
        assert c.shelf_placement_strategy == "eye_level"

    def test_clearance_threshold_default(self):
        c = InStoreTacticalControls()
        assert c.clearance_threshold_pct == 20

    def test_pos_integration_default(self):
        c = InStoreTacticalControls()
        assert c.pos_integration is True

    def test_bopis_enabled_default(self):
        c = InStoreTacticalControls()
        assert c.bopis_enabled is True

    def test_trigger_flash_sale_when_enabled(self):
        c = InStoreTacticalControls()
        result = c.trigger_flash_sale("SKU-ABC", 15)
        assert result["status"] == "triggered"
        assert result["sku"] == "SKU-ABC"
        assert result["discount_pct"] == 15

    def test_trigger_flash_sale_when_disabled(self):
        c = InStoreTacticalControls(overrides={454: False})
        result = c.trigger_flash_sale("SKU-ABC", 15)
        assert result["status"] == "disabled"

    def test_get_clearance_candidates(self):
        c = InStoreTacticalControls()
        inventory = {"SKU-A": 15, "SKU-B": 50, "SKU-C": 20}
        candidates = c.get_clearance_candidates(inventory)
        assert "SKU-A" in candidates
        assert "SKU-C" in candidates
        assert "SKU-B" not in candidates

    def test_get_clearance_candidates_empty(self):
        c = InStoreTacticalControls()
        assert c.get_clearance_candidates({}) == []

    def test_configure_for_retail_intelligence(self):
        c = InStoreTacticalControls()
        c.configure_for_retail_intelligence()
        assert c.display_optimisation is True
        assert c.pos_integration is True

    def test_get_enabled_features(self):
        c = InStoreTacticalControls()
        feats = c.get_enabled_features()
        assert isinstance(feats, list)
        assert len(feats) > 0

    def test_summary_keys(self):
        c = InStoreTacticalControls()
        s = c.summary()
        assert "shelf_placement_strategy" in s
        assert "clearance_threshold_pct" in s
        assert "enabled_feature_count" in s


# ---------------------------------------------------------------------------
# Online Platform Optimization tests
# ---------------------------------------------------------------------------

class TestOnlinePlatformOptimization:
    def test_instantiation(self):
        o = OnlinePlatformOptimization()
        assert o is not None

    def test_seo_level_default(self):
        o = OnlinePlatformOptimization()
        assert o.seo_level == "standard"

    def test_dynamic_pricing_default(self):
        o = OnlinePlatformOptimization()
        assert o.dynamic_pricing_enabled is True

    def test_buy_box_strategy_default(self):
        o = OnlinePlatformOptimization()
        assert o.buy_box_strategy == "mixed"

    def test_gdpr_consent_default(self):
        o = OnlinePlatformOptimization()
        assert o.gdpr_consent_management is True

    def test_accessibility_level_default(self):
        o = OnlinePlatformOptimization()
        assert o.accessibility_level == "AA"

    def test_site_speed_target_default(self):
        o = OnlinePlatformOptimization()
        assert o.site_speed_target_ms == 2000

    def test_generate_coupon_when_enabled(self):
        o = OnlinePlatformOptimization()
        result = o.generate_coupon("high_value", 10)
        assert result["status"] == "generated"
        assert result["discount_pct"] == 10

    def test_generate_coupon_when_disabled(self):
        o = OnlinePlatformOptimization(overrides={549: False})
        result = o.generate_coupon("high_value", 10)
        assert result["status"] == "disabled"

    def test_configure_for_marketplace(self):
        o = OnlinePlatformOptimization()
        o.configure_for_marketplace()
        assert o.seo_level == "aggressive"
        assert o.dynamic_pricing_enabled is True

    def test_configure_for_car_flipping(self):
        o = OnlinePlatformOptimization()
        o.configure_for_car_flipping()
        assert o.dynamic_pricing_enabled is True
        assert o.fraud_scoring_at_checkout is True

    def test_configure_for_real_estate(self):
        o = OnlinePlatformOptimization()
        o.configure_for_real_estate()
        assert o.recommendation_engine is True

    def test_get_enabled_features_list(self):
        o = OnlinePlatformOptimization()
        feats = o.get_enabled_features()
        assert isinstance(feats, list)

    def test_summary_keys(self):
        o = OnlinePlatformOptimization()
        s = o.summary()
        assert "seo_level" in s
        assert "dynamic_pricing_enabled" in s
        assert "enabled_feature_count" in s


# ---------------------------------------------------------------------------
# Enterprise Features tests
# ---------------------------------------------------------------------------

class TestEnterpriseFeatures:
    def test_instantiation(self):
        e = EnterpriseFeatures()
        assert e is not None

    def test_multi_location_default(self):
        e = EnterpriseFeatures()
        assert e.multi_location_support is True

    def test_encryption_level_default(self):
        e = EnterpriseFeatures()
        assert e.encryption_level == "AES256"

    def test_sso_enabled_default(self):
        e = EnterpriseFeatures()
        assert e.sso_enabled is True

    def test_rbac_enabled_default(self):
        e = EnterpriseFeatures()
        assert e.rbac_enabled is True

    def test_sla_uptime_default(self):
        e = EnterpriseFeatures()
        assert e.sla_uptime_pct == 99.9

    def test_api_rate_limit_default(self):
        e = EnterpriseFeatures()
        assert e.api_rate_limit_per_min == 600

    def test_is_compliant_default(self):
        e = EnterpriseFeatures()
        assert e.is_compliant() is True

    def test_is_not_compliant_when_rbac_disabled(self):
        e = EnterpriseFeatures(overrides={557: False})
        assert e.is_compliant() is False

    def test_is_not_compliant_when_encryption_weak(self):
        e = EnterpriseFeatures(overrides={555: "AES128"})
        assert e.is_compliant() is False

    def test_configure_for_real_estate_enterprise(self):
        e = EnterpriseFeatures()
        e.configure_for_real_estate_enterprise()
        assert e.multi_location_support is True
        assert e.crm_integration is True

    def test_configure_for_retail_network(self):
        e = EnterpriseFeatures()
        e.configure_for_retail_network()
        assert e.wms_integration is True
        assert e.oms_integration is True
        assert e.advanced_fraud_detection is True

    def test_get_enabled_features(self):
        e = EnterpriseFeatures()
        feats = e.get_enabled_features()
        assert isinstance(feats, list)
        assert len(feats) > 0

    def test_summary_keys(self):
        e = EnterpriseFeatures()
        s = e.summary()
        assert "encryption_level" in s
        assert "sla_uptime_pct" in s
        assert "compliant" in s


# ---------------------------------------------------------------------------
# Behavioral Settings tests
# ---------------------------------------------------------------------------

class TestBehavioralSettings:
    def test_instantiation(self):
        b = BehavioralSettings()
        assert b is not None

    def test_segmentation_model_default(self):
        b = BehavioralSettings()
        assert b.segmentation_model == "rfm"

    def test_purchase_tracking_default(self):
        b = BehavioralSettings()
        assert b.purchase_tracking is True

    def test_churn_prediction_default(self):
        b = BehavioralSettings()
        assert b.churn_prediction is True

    def test_opt_out_management_default(self):
        b = BehavioralSettings()
        assert b.opt_out_management is True

    def test_score_customer_high_value(self):
        b = BehavioralSettings()
        result = b.score_customer({
            "recency_days": 5,
            "frequency": 20,
            "monetary_value": 500,
        })
        assert result["segment"] == "high_value"
        assert "churn_risk" in result
        assert "intent_score" in result

    def test_score_customer_low_value(self):
        b = BehavioralSettings()
        result = b.score_customer({
            "recency_days": 300,
            "frequency": 1,
            "monetary_value": 10,
        })
        assert result["segment"] == "low_value"

    def test_score_customer_includes_model(self):
        b = BehavioralSettings()
        result = b.score_customer({"recency_days": 10, "frequency": 5})
        assert result["model"] == "rfm"

    def test_configure_for_real_estate(self):
        b = BehavioralSettings()
        b.configure_for_real_estate()
        assert b.real_estate_buyer_scoring is True

    def test_configure_for_car_flipping(self):
        b = BehavioralSettings()
        b.configure_for_car_flipping()
        assert b.car_buyer_intent_model is True

    def test_configure_for_retail_intelligence(self):
        b = BehavioralSettings()
        b.configure_for_retail_intelligence()
        assert b.segmentation_model == "kmeans"
        assert b.urgency_scarcity_engine is True

    def test_get_enabled_features(self):
        b = BehavioralSettings()
        feats = b.get_enabled_features()
        assert isinstance(feats, list)
        assert len(feats) > 0

    def test_summary_keys(self):
        b = BehavioralSettings()
        s = b.summary()
        assert "segmentation_model" in s
        assert "churn_prediction" in s
        assert "enabled_feature_count" in s


# ---------------------------------------------------------------------------
# RealEstateOptimizer tests
# ---------------------------------------------------------------------------

class TestRealEstateOptimizer:
    def test_instantiation(self):
        r = RealEstateOptimizer()
        assert r is not None

    def test_score_property_strong_buy(self):
        r = RealEstateOptimizer()
        result = r.score_property({
            "price": 100_000,
            "sqft": 2_000,
            "days_on_market": 5,
        })
        assert result["recommendation"] in ("strong_buy", "consider")
        assert 0.0 <= result["investment_score"] <= 1.0

    def test_score_property_pass(self):
        r = RealEstateOptimizer()
        result = r.score_property({
            "price": 5_000_000,
            "sqft": 500,
            "days_on_market": 175,
        })
        assert result["recommendation"] == "pass"

    def test_score_property_has_required_keys(self):
        r = RealEstateOptimizer()
        result = r.score_property({"price": 200_000, "sqft": 1_000})
        for key in ("investment_score", "recommendation", "price_per_sqft",
                    "days_on_market", "analytics_enabled"):
            assert key in result

    def test_score_buyer(self):
        r = RealEstateOptimizer()
        result = r.score_buyer({"recency_days": 7, "frequency": 10, "monetary_value": 200})
        assert "segment" in result
        assert "churn_risk" in result

    def test_list_active_features_structure(self):
        r = RealEstateOptimizer()
        feats = r.list_active_features()
        assert "analytics" in feats
        assert "behavioral" in feats
        assert "enterprise" in feats
        assert "online" in feats

    def test_analytics_enabled_after_preset(self):
        r = RealEstateOptimizer()
        assert r.analytics.real_estate_price_index is True

    def test_summary_module_key(self):
        r = RealEstateOptimizer()
        s = r.summary()
        assert s["module"] == "real_estate_optimizer"


# ---------------------------------------------------------------------------
# CarFlippingBot tests
# ---------------------------------------------------------------------------

class TestCarFlippingBot:
    def test_instantiation(self):
        b = CarFlippingBot()
        assert b is not None

    def test_evaluate_vehicle_buy(self):
        b = CarFlippingBot()
        result = b.evaluate_vehicle({
            "purchase_price": 8_000,
            "estimated_sale_price": 12_000,
            "repair_cost": 500,
            "days_to_flip": 30,
        })
        assert result["recommendation"] == "buy"
        assert result["gross_profit"] == 3500.0

    def test_evaluate_vehicle_pass(self):
        b = CarFlippingBot()
        result = b.evaluate_vehicle({
            "purchase_price": 10_000,
            "estimated_sale_price": 10_100,
            "repair_cost": 1_000,
            "days_to_flip": 60,
        })
        assert result["recommendation"] == "pass"

    def test_evaluate_vehicle_has_required_keys(self):
        b = CarFlippingBot()
        result = b.evaluate_vehicle({
            "purchase_price": 5_000,
            "estimated_sale_price": 7_000,
        })
        for key in ("gross_profit", "roi_pct", "days_to_flip",
                    "recommendation", "competitor_monitoring",
                    "dynamic_pricing"):
            assert key in result

    def test_evaluate_part_profitable(self):
        b = CarFlippingBot()
        result = b.evaluate_part({
            "buy_price": 40.0,
            "sell_price": 90.0,
            "platform_fee_pct": 10,
        })
        assert result["recommendation"] == "buy"
        assert result["net_profit"] > 0

    def test_evaluate_part_unprofitable(self):
        b = CarFlippingBot()
        result = b.evaluate_part({
            "buy_price": 100.0,
            "sell_price": 80.0,
            "platform_fee_pct": 10,
        })
        assert result["recommendation"] == "pass"
        assert result["net_profit"] < 0

    def test_evaluate_part_has_auto_parts_feed_flag(self):
        b = CarFlippingBot()
        result = b.evaluate_part({"buy_price": 10, "sell_price": 20})
        assert "auto_parts_feed_enabled" in result

    def test_score_buyer_intent(self):
        b = CarFlippingBot()
        result = b.score_buyer_intent({"recency_days": 3, "frequency": 5})
        assert "segment" in result

    def test_analytics_preset_applied(self):
        b = CarFlippingBot()
        assert b.analytics.auto_parts_market_feed is True
        assert b.analytics.competitor_monitoring is True

    def test_summary_module_key(self):
        b = CarFlippingBot()
        s = b.summary()
        assert s["module"] == "car_flipping_bot"


# ---------------------------------------------------------------------------
# RetailIntelligenceNetwork tests
# ---------------------------------------------------------------------------

class TestRetailIntelligenceNetwork:
    def test_instantiation(self):
        n = RetailIntelligenceNetwork()
        assert n is not None

    def test_analyse_sku_returns_actions(self):
        n = RetailIntelligenceNetwork()
        result = n.analyse_sku({
            "sku": "SKU-001",
            "price": 29.99,
            "stock_pct": 10,
            "sales_velocity": 0.02,
            "competitor_price": 24.99,
        })
        assert "recommended_actions" in result
        assert isinstance(result["recommended_actions"], list)

    def test_analyse_sku_clearance_triggered(self):
        n = RetailIntelligenceNetwork()
        result = n.analyse_sku({
            "sku": "SKU-002",
            "price": 15.0,
            "stock_pct": 5,
            "sales_velocity": 0.5,
        })
        assert "trigger_clearance_pricing" in result["recommended_actions"]

    def test_analyse_sku_social_proof(self):
        n = RetailIntelligenceNetwork()
        result = n.analyse_sku({
            "sku": "SKU-003",
            "price": 50.0,
            "stock_pct": 80,
            "sales_velocity": 2.0,
            "competitor_price": 55.0,
        })
        assert "inject_social_proof" in result["recommended_actions"]

    def test_analyse_customer(self):
        n = RetailIntelligenceNetwork()
        result = n.analyse_customer({"recency_days": 10, "frequency": 8})
        assert "segment" in result

    def test_get_clearance_candidates(self):
        n = RetailIntelligenceNetwork()
        candidates = n.get_clearance_candidates(
            {"A": 15, "B": 50, "C": 20}
        )
        assert "A" in candidates
        assert "B" not in candidates

    def test_generate_coupon(self):
        n = RetailIntelligenceNetwork()
        result = n.generate_coupon("mid_value", 5)
        assert result["status"] == "generated"

    def test_trigger_flash_sale(self):
        n = RetailIntelligenceNetwork()
        result = n.trigger_flash_sale("SKU-XYZ", 20)
        assert result["status"] == "triggered"
        assert result["sku"] == "SKU-XYZ"

    def test_list_active_features_all_modules(self):
        n = RetailIntelligenceNetwork()
        feats = n.list_active_features()
        for module in ("analytics", "in_store", "online",
                       "enterprise", "behavioral"):
            assert module in feats
            assert isinstance(feats[module], list)

    def test_summary_module_key(self):
        n = RetailIntelligenceNetwork()
        s = n.summary()
        assert s["module"] == "retail_intelligence_network"
        for key in ("analytics", "in_store", "online",
                    "enterprise", "behavioral"):
            assert key in s

    def test_behavioral_preset_applied(self):
        n = RetailIntelligenceNetwork()
        assert n.behavioral.segmentation_model == "kmeans"


# ---------------------------------------------------------------------------
# DiscountDominator main bot tests
# ---------------------------------------------------------------------------

class TestDiscountDominator:
    def test_instantiation(self):
        bot = DiscountDominator()
        assert bot is not None

    def test_settings_count(self):
        assert DiscountDominator.SETTINGS_COUNT == 200

    def test_settings_range(self):
        assert DiscountDominator.SETTINGS_START == 401
        assert DiscountDominator.SETTINGS_END == 600

    def test_get_all_settings(self):
        bot = DiscountDominator()
        settings = bot.get_all_settings()
        assert len(settings) == 200

    def test_get_settings_for_group(self):
        bot = DiscountDominator()
        group_settings = bot.get_settings_for_group(GROUP_ANALYTICS)
        assert len(group_settings) == 50

    def test_configure_override(self):
        bot = DiscountDominator()
        bot.configure({432: "EUR"})
        assert get_setting(432).value == "EUR"

    def test_reset(self):
        bot = DiscountDominator()
        bot.configure({432: "EUR"})
        bot.reset()
        assert get_setting(432).value == "USD"

    def test_summary_structure(self):
        bot = DiscountDominator()
        s = bot.summary()
        assert s["bot"] == "DiscountDominator"
        assert s["total_settings"] == 200
        for key in ("analytics_summary", "in_store_summary", "online_summary",
                    "enterprise_summary", "behavioral_summary"):
            assert key in s

    def test_domain_modules_accessible(self):
        bot = DiscountDominator()
        assert bot.real_estate is not None
        assert bot.car_flipping is not None
        assert bot.retail is not None

    def test_overrides_at_construction(self):
        bot = DiscountDominator(overrides={501: "aggressive", 581: "kmeans"})
        assert get_setting(501).value == "aggressive"
        assert get_setting(581).value == "kmeans"

    def test_run_does_not_raise(self, capsys):
        bot = DiscountDominator()
        bot.run()
        captured = capsys.readouterr()
        assert "Discount Dominator" in captured.out
        assert "ready" in captured.out

    def test_all_groups_in_summary(self):
        bot = DiscountDominator()
        s = bot.summary()
        assert set(s["groups"]) == set(ALL_GROUPS)
