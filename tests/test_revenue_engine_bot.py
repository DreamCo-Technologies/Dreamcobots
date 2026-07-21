"""Tests for bots/revenue_engine_bot/tiers.py and bots/revenue_engine_bot/revenue_engine_bot.py"""
import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
AI_MODELS_DIR = os.path.join(REPO_ROOT, 'bots', 'ai-models-integration')
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from bots.revenue_engine_bot.revenue_engine_bot import (
    RevenueEngineBot,
    RevenueEngineBotTierError,
    RevenueRecord,
    ProductListing,
    PaymentEngine,
    AffiliateEngine,
    ProductEngine,
    RealEstatePipeline,
    RevenueTracker,
)
from bots.revenue_engine_bot.tiers import BOT_FEATURES, get_bot_tier_info


# ---------------------------------------------------------------------------
# Tier definitions
# ---------------------------------------------------------------------------

class TestTierDefinitions:
    def test_all_tiers_have_features(self):
        for tier in Tier:
            assert len(BOT_FEATURES[tier.value]) > 0

    def test_enterprise_has_more_features_than_pro(self):
        assert len(BOT_FEATURES[Tier.ENTERPRISE.value]) > len(BOT_FEATURES[Tier.PRO.value])

    def test_pro_has_more_features_than_free(self):
        assert len(BOT_FEATURES[Tier.PRO.value]) > len(BOT_FEATURES[Tier.FREE.value])

    def test_enterprise_has_api_access(self):
        assert any("API" in f for f in BOT_FEATURES[Tier.ENTERPRISE.value])

    def test_get_bot_tier_info_free(self):
        info = get_bot_tier_info(Tier.FREE)
        assert info["tier"] == "free"
        assert info["price_usd_monthly"] == 0.0
        assert "features" in info

    def test_get_bot_tier_info_pro(self):
        info = get_bot_tier_info(Tier.PRO)
        assert info["tier"] == "pro"
        assert info["price_usd_monthly"] > 0

    def test_get_bot_tier_info_enterprise(self):
        info = get_bot_tier_info(Tier.ENTERPRISE)
        assert info["tier"] == "enterprise"
        assert info["price_usd_monthly"] > get_bot_tier_info(Tier.PRO)["price_usd_monthly"]


# ---------------------------------------------------------------------------
# RevenueEngineBot instantiation
# ---------------------------------------------------------------------------

class TestRevenueEngineBotInstantiation:
    def test_default_tier_is_free(self):
        bot = RevenueEngineBot()
        assert bot.tier == Tier.FREE

    def test_pro_tier(self):
        bot = RevenueEngineBot(tier=Tier.PRO)
        assert bot.tier == Tier.PRO

    def test_enterprise_tier(self):
        bot = RevenueEngineBot(tier=Tier.ENTERPRISE)
        assert bot.tier == Tier.ENTERPRISE

    def test_config_loaded(self):
        bot = RevenueEngineBot()
        assert bot.config is not None


# ---------------------------------------------------------------------------
# PaymentEngine
# ---------------------------------------------------------------------------

class TestPaymentEngine:
    def test_free_tier_has_stripe_only(self):
        engine = PaymentEngine(Tier.FREE)
        assert engine.available_providers == ["stripe"]

    def test_pro_tier_has_stripe_and_paypal(self):
        engine = PaymentEngine(Tier.PRO)
        assert "stripe" in engine.available_providers
        assert "paypal" in engine.available_providers

    def test_enterprise_has_all_providers(self):
        engine = PaymentEngine(Tier.ENTERPRISE)
        assert len(engine.available_providers) >= 4

    def test_create_stripe_intent_returns_client_secret(self):
        engine = PaymentEngine(Tier.FREE)
        result = engine.create_stripe_intent(49.0, "Test Product")
        assert "client_secret" in result
        assert result["amount_usd"] == 49.0
        assert result["provider"] == "stripe"

    def test_create_stripe_intent_status(self):
        engine = PaymentEngine(Tier.FREE)
        result = engine.create_stripe_intent(99.0, "Premium Plan")
        assert result["status"] == "requires_payment_method"

    def test_create_paypal_order_free_tier_raises(self):
        engine = PaymentEngine(Tier.FREE)
        with pytest.raises(RevenueEngineBotTierError):
            engine.create_paypal_order(49.0)

    def test_create_paypal_order_pro_tier(self):
        engine = PaymentEngine(Tier.PRO)
        result = engine.create_paypal_order(49.0)
        assert result["provider"] == "paypal"
        assert result["amount_usd"] == 49.0
        assert "order_id" in result

    def test_create_paypal_order_enterprise_tier(self):
        engine = PaymentEngine(Tier.ENTERPRISE)
        result = engine.create_paypal_order(199.0)
        assert result["status"] == "CREATED"


# ---------------------------------------------------------------------------
# AffiliateEngine
# ---------------------------------------------------------------------------

class TestAffiliateEngine:
    def test_promote_returns_list(self):
        engine = AffiliateEngine(Tier.FREE)
        products = engine.promote("shopify")
        assert isinstance(products, list)
        assert len(products) > 0

    def test_promote_includes_estimated_earnings(self):
        engine = AffiliateEngine(Tier.FREE)
        products = engine.promote("fiverr")
        for p in products:
            assert "estimated_monthly_earnings_usd" in p

    def test_free_tier_niche_limit_enforced(self):
        engine = AffiliateEngine(Tier.FREE)
        engine.promote("shopify")
        engine.promote("fiverr")
        engine.promote("amazon")
        with pytest.raises(RevenueEngineBotTierError):
            engine.promote("coinbase")

    def test_pro_tier_niche_limit_is_ten(self):
        engine = AffiliateEngine(Tier.PRO)
        niches = list(engine.NICHE_PROGRAMS.keys())[:10]
        for n in niches:
            engine.promote(n)
        # Should not raise on 10th niche
        assert len(engine._active_niches) == 10

    def test_enterprise_has_no_niche_limit(self):
        engine = AffiliateEngine(Tier.ENTERPRISE)
        for niche in engine.NICHE_PROGRAMS:
            engine.promote(niche)
        assert len(engine._active_niches) == len(engine.NICHE_PROGRAMS)

    def test_estimate_passive_income_returns_dict(self):
        engine = AffiliateEngine(Tier.FREE)
        engine.promote("shopify")
        result = engine.estimate_passive_income(daily_clicks=100)
        assert "estimated_monthly_passive_income_usd" in result
        assert result["estimated_monthly_passive_income_usd"] >= 0

    def test_higher_tier_higher_conversion(self):
        free_engine = AffiliateEngine(Tier.FREE)
        free_engine.promote("shopify")
        free_income = free_engine.estimate_passive_income(100)

        pro_engine = AffiliateEngine(Tier.PRO)
        pro_engine.promote("shopify")
        pro_income = pro_engine.estimate_passive_income(100)

        assert pro_income["estimated_monthly_passive_income_usd"] > free_income["estimated_monthly_passive_income_usd"]


# ---------------------------------------------------------------------------
# ProductEngine
# ---------------------------------------------------------------------------

class TestProductEngine:
    def test_add_product_returns_product_listing(self):
        engine = ProductEngine(Tier.PRO)
        product = engine.add_product("My Product", 49.0, "A great product")
        assert product.name == "My Product"
        assert product.price == 49.0

    def test_free_tier_product_limit_enforced(self):
        engine = ProductEngine(Tier.FREE)
        engine.add_product("Product 1", 49.0)
        with pytest.raises(RevenueEngineBotTierError):
            engine.add_product("Product 2", 99.0)

    def test_pro_tier_can_add_ten_products(self):
        engine = ProductEngine(Tier.PRO)
        for i in range(10):
            engine.add_product(f"Product {i}", float(i * 10 + 10))
        assert len(engine._catalog) == 10

    def test_enterprise_no_product_limit(self):
        engine = ProductEngine(Tier.ENTERPRISE)
        for i in range(20):
            engine.add_product(f"Product {i}", float(i * 5 + 5))
        assert len(engine._catalog) == 20

    def test_list_products_returns_defaults_when_empty(self):
        engine = ProductEngine(Tier.FREE)
        products = engine.list_products()
        assert len(products) > 0
        assert all("name" in p for p in products)

    def test_sell_product_records_sale(self):
        engine = ProductEngine(Tier.PRO)
        engine.add_product("AI Pack", 49.0)
        order = engine.sell_product("AI Pack")
        assert order["status"] == "confirmed"
        assert order["price_usd"] == 49.0
        assert order["units_sold_total"] == 1

    def test_sell_product_not_found_raises(self):
        engine = ProductEngine(Tier.PRO)
        with pytest.raises(ValueError):
            engine.sell_product("Nonexistent Product XYZ123")

    def test_sell_default_product(self):
        engine = ProductEngine(Tier.FREE)
        order = engine.sell_product("AI Business Starter Pack")
        assert order["status"] == "confirmed"

    def test_catalog_summary(self):
        engine = ProductEngine(Tier.PRO)
        engine.add_product("Item A", 29.0)
        engine.sell_product("Item A")
        summary = engine.catalog_summary()
        assert summary["total_units_sold"] >= 1
        assert summary["total_revenue_usd"] >= 29.0


# ---------------------------------------------------------------------------
# RealEstatePipeline
# ---------------------------------------------------------------------------

class TestRealEstatePipeline:
    def test_free_tier_raises_on_find_deals(self):
        pipeline = RealEstatePipeline(Tier.FREE)
        with pytest.raises(RevenueEngineBotTierError):
            pipeline.find_deals("austin", 200_000)

    def test_pro_tier_finds_deals(self):
        pipeline = RealEstatePipeline(Tier.PRO)
        deals = pipeline.find_deals("austin", 200_000)
        assert isinstance(deals, list)
        assert len(deals) > 0

    def test_deals_have_profit_estimate(self):
        pipeline = RealEstatePipeline(Tier.PRO)
        deals = pipeline.find_deals("austin", 500_000)
        for d in deals:
            assert "estimated_profit_usd" in d
            assert "roi_pct" in d
            assert "deal_score" in d

    def test_pro_tier_market_limit_enforced(self):
        pipeline = RealEstatePipeline(Tier.PRO)
        pipeline.find_deals("austin", 500_000)
        pipeline.find_deals("phoenix", 500_000)
        pipeline.find_deals("dallas", 500_000)
        with pytest.raises(RevenueEngineBotTierError):
            pipeline.find_deals("atlanta", 500_000)

    def test_enterprise_no_market_limit(self):
        pipeline = RealEstatePipeline(Tier.ENTERPRISE)
        markets = ["austin", "phoenix", "dallas", "atlanta", "houston"]
        for market in markets:
            pipeline.find_deals(market, 500_000)
        assert len(pipeline._searched_markets) == len(markets)

    def test_budget_filter_applied(self):
        pipeline = RealEstatePipeline(Tier.PRO)
        deals = pipeline.find_deals("austin", 60_000)
        for d in deals:
            assert d["price"] <= 60_000

    def test_pipeline_summary(self):
        pipeline = RealEstatePipeline(Tier.PRO)
        pipeline.find_deals("austin", 500_000)
        summary = pipeline.pipeline_summary()
        assert "markets_searched" in summary
        assert "total_deals_found" in summary
        assert summary["total_deals_found"] > 0


# ---------------------------------------------------------------------------
# RevenueTracker
# ---------------------------------------------------------------------------

class TestRevenueTracker:
    def test_track_creates_record(self):
        tracker = RevenueTracker()
        record = tracker.track("stripe", 49.0, "Test payment")
        assert isinstance(record, RevenueRecord)
        assert record.amount == 49.0
        assert record.source == "stripe"

    def test_summary_totals(self):
        tracker = RevenueTracker()
        tracker.track("stripe", 49.0)
        tracker.track("stripe", 99.0)
        tracker.track("affiliate", 25.0)
        summary = tracker.summary()
        assert summary["total_revenue_usd"] == pytest.approx(173.0)
        assert summary["by_source"]["stripe"] == pytest.approx(148.0)
        assert summary["by_source"]["affiliate"] == pytest.approx(25.0)

    def test_summary_total_events(self):
        tracker = RevenueTracker()
        for i in range(7):
            tracker.track("product", float(i * 10))
        summary = tracker.summary()
        assert summary["total_events"] == 7

    def test_summary_recent_events_limit(self):
        tracker = RevenueTracker()
        for i in range(10):
            tracker.track("product", float(i))
        summary = tracker.summary()
        assert len(summary["recent_events"]) == 5

    def test_records_returns_list_of_dicts(self):
        tracker = RevenueTracker()
        tracker.track("affiliate", 30.0, "Shopify")
        records = tracker.records()
        assert isinstance(records, list)
        assert records[0]["source"] == "affiliate"
        assert "timestamp" in records[0]


# ---------------------------------------------------------------------------
# RevenueEngineBot integration
# ---------------------------------------------------------------------------

class TestRevenueEngineBotIntegration:
    def test_create_payment_intent(self):
        bot = RevenueEngineBot(tier=Tier.FREE)
        result = bot.create_payment_intent(49.0, "AI Pack")
        assert "client_secret" in result
        assert result["amount_usd"] == 49.0

    def test_payment_intent_tracks_revenue(self):
        bot = RevenueEngineBot(tier=Tier.FREE)
        bot.create_payment_intent(49.0, "Test")
        summary = bot.revenue_summary()
        assert summary["by_source"].get("stripe_payment", 0) == pytest.approx(49.0)

    def test_create_paypal_order_free_tier_raises(self):
        bot = RevenueEngineBot(tier=Tier.FREE)
        with pytest.raises(RevenueEngineBotTierError):
            bot.create_paypal_order(49.0)

    def test_create_paypal_order_pro(self):
        bot = RevenueEngineBot(tier=Tier.PRO)
        result = bot.create_paypal_order(99.0)
        assert result["provider"] == "paypal"

    def test_available_payment_providers_free(self):
        bot = RevenueEngineBot(tier=Tier.FREE)
        assert bot.available_payment_providers == ["stripe"]

    def test_promote_affiliate_products(self):
        bot = RevenueEngineBot(tier=Tier.FREE)
        products = bot.promote_affiliate_products("shopify")
        assert len(products) > 0

    def test_promote_affiliate_tracks_revenue(self):
        bot = RevenueEngineBot(tier=Tier.FREE)
        bot.promote_affiliate_products("shopify")
        summary = bot.revenue_summary()
        assert "affiliate" in summary["by_source"]

    def test_estimate_affiliate_income(self):
        bot = RevenueEngineBot(tier=Tier.PRO)
        bot.promote_affiliate_products("shopify")
        result = bot.estimate_affiliate_income(200)
        assert result["daily_clicks"] == 200
        assert "estimated_monthly_passive_income_usd" in result

    def test_add_and_sell_product(self):
        bot = RevenueEngineBot(tier=Tier.PRO)
        bot.add_product("DreamCo Pack", 97.0)
        order = bot.sell_product("DreamCo Pack")
        assert order["status"] == "confirmed"

    def test_sell_product_tracks_revenue(self):
        bot = RevenueEngineBot(tier=Tier.PRO)
        bot.add_product("DreamCo Pack", 97.0)
        bot.sell_product("DreamCo Pack")
        summary = bot.revenue_summary()
        assert summary["by_source"].get("product_sale", 0) == pytest.approx(97.0)

    def test_find_real_estate_deals_free_raises(self):
        bot = RevenueEngineBot(tier=Tier.FREE)
        with pytest.raises(RevenueEngineBotTierError):
            bot.find_real_estate_deals("austin", 200_000)

    def test_find_real_estate_deals_pro(self):
        bot = RevenueEngineBot(tier=Tier.PRO)
        deals = bot.find_real_estate_deals("austin", 500_000)
        assert len(deals) > 0

    def test_real_estate_tracks_revenue(self):
        bot = RevenueEngineBot(tier=Tier.PRO)
        deals = bot.find_real_estate_deals("austin", 500_000)
        if deals:
            summary = bot.revenue_summary()
            assert "real_estate" in summary["by_source"]

    def test_real_estate_pipeline_summary(self):
        bot = RevenueEngineBot(tier=Tier.PRO)
        bot.find_real_estate_deals("austin", 500_000)
        summary = bot.real_estate_pipeline_summary()
        assert "markets_searched" in summary

    def test_revenue_summary_empty(self):
        bot = RevenueEngineBot()
        summary = bot.revenue_summary()
        assert summary["total_revenue_usd"] == 0.0
        assert summary["total_events"] == 0

    def test_track_revenue_manual(self):
        bot = RevenueEngineBot()
        record = bot.track_revenue("custom", 500.0, "Manual entry")
        assert record["source"] == "custom"
        assert record["amount"] == 500.0

    def test_revenue_records_list(self):
        bot = RevenueEngineBot()
        bot.track_revenue("stripe", 49.0)
        bot.track_revenue("affiliate", 25.0)
        records = bot.revenue_records()
        assert len(records) == 2

    def test_product_catalog_summary(self):
        bot = RevenueEngineBot(tier=Tier.PRO)
        bot.add_product("Item", 29.0)
        bot.sell_product("Item")
        summary = bot.product_catalog_summary()
        assert summary["total_revenue_usd"] >= 29.0

    def test_list_products(self):
        bot = RevenueEngineBot()
        products = bot.list_products()
        assert isinstance(products, list)
        assert len(products) > 0


# ---------------------------------------------------------------------------
# run_all_engines
# ---------------------------------------------------------------------------

class TestRunAllEngines:
    def test_free_tier_runs_core_engines(self):
        bot = RevenueEngineBot(tier=Tier.FREE)
        report = bot.run_all_engines()
        assert "affiliate" in report["engines_run"]
        assert "product" in report["engines_run"]
        assert "payment" in report["engines_run"]

    def test_free_tier_skips_real_estate(self):
        bot = RevenueEngineBot(tier=Tier.FREE)
        report = bot.run_all_engines()
        assert "real_estate" not in report["engines_run"]

    def test_pro_tier_includes_real_estate(self):
        bot = RevenueEngineBot(tier=Tier.PRO)
        report = bot.run_all_engines()
        assert "real_estate" in report["engines_run"]

    def test_enterprise_tier_includes_ai_pricing(self):
        bot = RevenueEngineBot(tier=Tier.ENTERPRISE)
        report = bot.run_all_engines()
        assert "ai_pricing" in report["engines_run"]
        assert "optimized_prices" in report["results"]["ai_pricing"]

    def test_report_includes_revenue_summary(self):
        bot = RevenueEngineBot(tier=Tier.PRO)
        report = bot.run_all_engines()
        assert "revenue_summary" in report
        assert "total_revenue_usd" in report["revenue_summary"]

    def test_report_tier_field(self):
        bot = RevenueEngineBot(tier=Tier.PRO)
        report = bot.run_all_engines()
        assert report["tier"] == "pro"


# ---------------------------------------------------------------------------
# describe_tier
# ---------------------------------------------------------------------------

class TestDescribeTier:
    def test_describe_tier_free(self, capsys):
        bot = RevenueEngineBot(tier=Tier.FREE)
        result = bot.describe_tier()
        assert "Free" in result

    def test_describe_tier_pro(self, capsys):
        bot = RevenueEngineBot(tier=Tier.PRO)
        result = bot.describe_tier()
        assert "Pro" in result

    def test_describe_tier_enterprise(self, capsys):
        bot = RevenueEngineBot(tier=Tier.ENTERPRISE)
        result = bot.describe_tier()
        assert "Enterprise" in result

    def test_describe_tier_shows_upgrade_for_free(self, capsys):
        bot = RevenueEngineBot(tier=Tier.FREE)
        result = bot.describe_tier()
        assert "Upgrade" in result

    def test_describe_tier_no_upgrade_for_enterprise(self, capsys):
        bot = RevenueEngineBot(tier=Tier.ENTERPRISE)
        result = bot.describe_tier()
        assert "Upgrade" not in result


# ---------------------------------------------------------------------------
# Bot library registration
# ---------------------------------------------------------------------------

class TestBotLibraryRegistration:
    def test_revenue_engine_bot_registered(self):
        from bots.global_bot_network.bot_library import BotLibrary
        lib = BotLibrary()
        lib.populate_dreamco_bots()
        bot_entry = lib.get_bot("revenue_engine_bot")
        assert bot_entry is not None
        assert bot_entry.display_name == "Revenue Engine Bot"

    def test_revenue_engine_bot_capabilities(self):
        from bots.global_bot_network.bot_library import BotLibrary
        lib = BotLibrary()
        lib.populate_dreamco_bots()
        bot_entry = lib.get_bot("revenue_engine_bot")
        assert "stripe_payments" in bot_entry.capabilities
        assert "paypal_orders" in bot_entry.capabilities
        assert "affiliate_automation" in bot_entry.capabilities
        assert "digital_product_selling" in bot_entry.capabilities
        assert "real_estate_deals" in bot_entry.capabilities
        assert "revenue_tracking" in bot_entry.capabilities
