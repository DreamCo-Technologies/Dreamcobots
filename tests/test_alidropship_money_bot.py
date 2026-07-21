"""Tests for bots/alidropship_money_bot/tiers.py and bots/alidropship_money_bot/alidropship_money_bot.py"""
import sys, os

REPO_ROOT      = os.path.join(os.path.dirname(__file__), '..')
AI_MODELS_DIR  = os.path.join(REPO_ROOT, 'bots', 'ai-models-integration')
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, os.path.join(AI_MODELS_DIR, 'models'))
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from bots.alidropship_money_bot.alidropship_money_bot import (
    AliDropshipMoneyBot,
    AliDropshipBotTierError,
)
from bots.alidropship_money_bot.tiers import BOT_FEATURES, get_bot_tier_info


# ===========================================================================
# Tier configuration
# ===========================================================================

class TestTierConfig:
    def test_all_tiers_have_features(self):
        for tier in (Tier.FREE, Tier.PRO, Tier.ENTERPRISE):
            assert tier.value in BOT_FEATURES
            assert len(BOT_FEATURES[tier.value]) > 0

    def test_enterprise_has_more_features_than_pro(self):
        assert len(BOT_FEATURES[Tier.ENTERPRISE.value]) > len(BOT_FEATURES[Tier.PRO.value])

    def test_pro_has_more_features_than_free(self):
        assert len(BOT_FEATURES[Tier.PRO.value]) > len(BOT_FEATURES[Tier.FREE.value])

    def test_get_bot_tier_info_free(self):
        info = get_bot_tier_info(Tier.FREE)
        assert info["tier"] == "free"
        assert info["price_usd_monthly"] == 0.0
        assert isinstance(info["features"], list)

    def test_get_bot_tier_info_pro(self):
        info = get_bot_tier_info(Tier.PRO)
        assert info["tier"] == "pro"
        assert info["price_usd_monthly"] > 0

    def test_get_bot_tier_info_enterprise(self):
        info_enterprise = get_bot_tier_info(Tier.ENTERPRISE)
        info_pro        = get_bot_tier_info(Tier.PRO)
        assert info_enterprise["tier"] == "enterprise"
        assert info_enterprise["price_usd_monthly"] > info_pro["price_usd_monthly"]


# ===========================================================================
# Instantiation
# ===========================================================================

class TestInstantiation:
    def test_default_tier_is_free(self):
        bot = AliDropshipMoneyBot()
        assert bot.tier == Tier.FREE

    def test_pro_tier(self):
        bot = AliDropshipMoneyBot(tier=Tier.PRO)
        assert bot.tier == Tier.PRO

    def test_enterprise_tier(self):
        bot = AliDropshipMoneyBot(tier=Tier.ENTERPRISE)
        assert bot.tier == Tier.ENTERPRISE

    def test_config_loaded(self):
        bot = AliDropshipMoneyBot()
        assert bot.config is not None


# ===========================================================================
# 1. Product Hunter Engine
# ===========================================================================

class TestProductHunterEngine:
    def test_returns_list(self):
        bot = AliDropshipMoneyBot(tier=Tier.FREE)
        result = bot.find_winning_products()
        assert isinstance(result, list)

    def test_free_limited_to_5_products(self):
        bot = AliDropshipMoneyBot(tier=Tier.FREE)
        result = bot.find_winning_products()
        assert len(result) <= 5

    def test_pro_can_return_up_to_50_products(self):
        bot = AliDropshipMoneyBot(tier=Tier.PRO)
        result = bot.find_winning_products()
        assert len(result) <= 50

    def test_enterprise_returns_all_products(self):
        bot = AliDropshipMoneyBot(tier=Tier.ENTERPRISE)
        result = bot.find_winning_products()
        assert len(result) >= 5

    def test_niche_filter(self):
        bot = AliDropshipMoneyBot(tier=Tier.PRO)
        result = bot.find_winning_products(niche="fitness")
        assert all(p["niche"] == "fitness" for p in result)

    def test_products_have_required_keys(self):
        bot = AliDropshipMoneyBot(tier=Tier.FREE)
        result = bot.find_winning_products()
        assert len(result) > 0
        for p in result:
            assert "id" in p
            assert "title" in p
            assert "niche" in p
            assert "aliexpress_cost_usd" in p
            assert "suggested_sell_price_usd" in p
            assert "estimated_profit_usd" in p
            assert "profit_margin_pct" in p

    def test_product_quality_filters(self):
        bot = AliDropshipMoneyBot(tier=Tier.PRO)
        result = bot.find_winning_products()
        for p in result:
            assert p["orders"] > 500
            assert p["rating"] > 4.5

    def test_limit_parameter(self):
        bot = AliDropshipMoneyBot(tier=Tier.ENTERPRISE)
        result = bot.find_winning_products(limit=3)
        assert len(result) <= 3

    def test_tier_annotated_in_result(self):
        bot = AliDropshipMoneyBot(tier=Tier.PRO)
        result = bot.find_winning_products()
        for p in result:
            assert p["tier"] == "pro"


# ===========================================================================
# 2. Store Builder Engine
# ===========================================================================

class TestStoreBuilderEngine:
    def test_free_tier_raises(self):
        bot = AliDropshipMoneyBot(tier=Tier.FREE)
        with pytest.raises(AliDropshipBotTierError):
            bot.build_store("fitness")

    def test_pro_can_build_one_store(self):
        bot   = AliDropshipMoneyBot(tier=Tier.PRO)
        store = bot.build_store("fitness")
        assert isinstance(store, dict)
        assert store["status"] == "live"

    def test_pro_limited_to_one_store(self):
        bot = AliDropshipMoneyBot(tier=Tier.PRO)
        bot.build_store("fitness")
        with pytest.raises(AliDropshipBotTierError):
            bot.build_store("beauty")

    def test_enterprise_can_build_multiple_stores(self):
        bot = AliDropshipMoneyBot(tier=Tier.ENTERPRISE)
        s1  = bot.build_store("fitness")
        s2  = bot.build_store("beauty")
        assert s1["store_id"] != s2["store_id"]

    def test_store_has_required_keys(self):
        bot   = AliDropshipMoneyBot(tier=Tier.PRO)
        store = bot.build_store("pets")
        for key in ("store_id", "domain", "niche", "brand", "platform", "pages", "products", "features"):
            assert key in store

    def test_store_pages_populated(self):
        bot   = AliDropshipMoneyBot(tier=Tier.PRO)
        store = bot.build_store("pets")
        assert len(store["pages"]) >= 5

    def test_store_platform_is_wordpress(self):
        bot   = AliDropshipMoneyBot(tier=Tier.PRO)
        store = bot.build_store("fitness")
        assert "WordPress" in store["platform"]
        assert "AliDropship" in store["platform"]

    def test_enterprise_store_has_ai_descriptions(self):
        bot   = AliDropshipMoneyBot(tier=Tier.ENTERPRISE)
        store = bot.build_store("beauty")
        assert store["features"]["ai_descriptions"] is True

    def test_create_brand_returns_dict(self):
        bot   = AliDropshipMoneyBot()
        brand = bot.create_brand("fitness")
        assert "name" in brand
        assert "logo" in brand
        assert "slogan" in brand

    def test_create_brand_unknown_niche(self):
        bot   = AliDropshipMoneyBot()
        brand = bot.create_brand("unknown_niche")
        assert "name" in brand


# ===========================================================================
# 3. Pricing & Profit Engine
# ===========================================================================

class TestPricingEngine:
    def test_calculate_sell_price_returns_float(self):
        bot   = AliDropshipMoneyBot()
        price = bot.calculate_sell_price(10.0)
        assert isinstance(price, float)

    def test_ten_dollar_product_prices_at_29_99(self):
        bot   = AliDropshipMoneyBot()
        price = bot.calculate_sell_price(10.0)
        assert price == 29.99

    def test_five_dollar_product(self):
        bot   = AliDropshipMoneyBot()
        price = bot.calculate_sell_price(5.0)
        assert price == 14.99

    def test_sell_price_is_triple_cost(self):
        bot = AliDropshipMoneyBot()
        for cost in (5.0, 8.0, 12.0, 15.0, 20.0):
            price = bot.calculate_sell_price(cost)
            assert price >= cost * 3 * 0.95

    def test_pricing_report_returns_list(self):
        bot    = AliDropshipMoneyBot()
        report = bot.generate_pricing_report()
        assert isinstance(report, list)
        assert len(report) > 0

    def test_pricing_report_has_required_keys(self):
        bot    = AliDropshipMoneyBot()
        report = bot.generate_pricing_report()
        for item in report:
            assert "cost_usd" in item
            assert "sell_price_usd" in item
            assert "profit_usd" in item
            assert "roi_multiplier" in item

    def test_pricing_profit_is_positive(self):
        bot    = AliDropshipMoneyBot()
        report = bot.generate_pricing_report()
        for item in report:
            assert item["profit_usd"] > 0

    def test_custom_products_pricing(self):
        bot      = AliDropshipMoneyBot()
        products = [{"id": "x1", "title": "Test", "aliexpress_cost_usd": 7.0}]
        report   = bot.generate_pricing_report(products)
        assert len(report) == 1
        assert report[0]["cost_usd"] == 7.0


# ===========================================================================
# 4. Auto Fulfillment Engine
# ===========================================================================

class TestAutoFulfillmentEngine:
    def test_free_fulfill_raises(self):
        bot   = AliDropshipMoneyBot(tier=Tier.FREE)
        order = {"order_id": "ORD-001", "product_id": "p001", "customer": "Test", "amount_usd": 29.99, "status": "pending"}
        with pytest.raises(AliDropshipBotTierError):
            bot.fulfill_order(order)

    def test_pro_can_fulfill_order(self):
        bot   = AliDropshipMoneyBot(tier=Tier.PRO)
        order = {"order_id": "ORD-001", "product_id": "p001", "customer": "Test", "amount_usd": 29.99, "status": "pending"}
        result = bot.fulfill_order(order)
        assert result["status"] == "fulfilled"

    def test_fulfilled_order_has_tracking(self):
        bot   = AliDropshipMoneyBot(tier=Tier.PRO)
        order = {"order_id": "ORD-002", "product_id": "p002", "customer": "Alice", "amount_usd": 24.99, "status": "pending"}
        result = bot.fulfill_order(order)
        assert "tracking_number" in result
        assert result["tracking_number"].startswith("AE")

    def test_fulfilled_order_has_notification(self):
        bot   = AliDropshipMoneyBot(tier=Tier.ENTERPRISE)
        order = {"order_id": "ORD-003", "product_id": "p003", "customer": "Bob", "amount_usd": 19.99, "status": "pending"}
        result = bot.fulfill_order(order)
        assert result["customer_notified"] is True

    def test_bulk_fulfill_free_raises(self):
        bot = AliDropshipMoneyBot(tier=Tier.FREE)
        with pytest.raises(AliDropshipBotTierError):
            bot.bulk_fulfill_orders()

    def test_bulk_fulfill_pro(self):
        bot    = AliDropshipMoneyBot(tier=Tier.PRO)
        orders = [
            {"order_id": "ORD-A", "product_id": "p001", "customer": "A", "amount_usd": 29.99, "status": "pending"},
            {"order_id": "ORD-B", "product_id": "p004", "customer": "B", "amount_usd": 19.99, "status": "pending"},
        ]
        result = bot.bulk_fulfill_orders(orders)
        assert len(result) == 2
        assert all(r["status"] == "fulfilled" for r in result)


# ===========================================================================
# 5. Traffic Generator
# ===========================================================================

class TestTrafficGenerator:
    # TikTok
    def test_tiktok_free_raises(self):
        bot     = AliDropshipMoneyBot(tier=Tier.FREE)
        product = {"id": "p001", "title": "Posture Corrector", "niche": "health", "aliexpress_cost_usd": 6.50}
        with pytest.raises(AliDropshipBotTierError):
            bot.create_tiktok_content(product)

    def test_tiktok_pro_returns_videos(self):
        bot     = AliDropshipMoneyBot(tier=Tier.PRO)
        product = {"id": "p001", "title": "Posture Corrector", "niche": "health", "aliexpress_cost_usd": 6.50}
        videos  = bot.create_tiktok_content(product)
        assert isinstance(videos, list)
        assert len(videos) <= 3

    def test_tiktok_enterprise_returns_up_to_10_videos(self):
        bot     = AliDropshipMoneyBot(tier=Tier.ENTERPRISE)
        product = {"id": "p001", "title": "Posture Corrector", "niche": "health", "aliexpress_cost_usd": 6.50}
        videos  = bot.create_tiktok_content(product)
        assert len(videos) <= 10

    def test_tiktok_video_has_required_keys(self):
        bot     = AliDropshipMoneyBot(tier=Tier.PRO)
        product = {"id": "p001", "title": "Posture Corrector", "niche": "health", "aliexpress_cost_usd": 6.50}
        videos  = bot.create_tiktok_content(product)
        assert len(videos) > 0
        for v in videos:
            assert "hook" in v
            assert "platform" in v
            assert v["platform"] == "TikTok"

    # Facebook Ads
    def test_facebook_ads_free_raises(self):
        bot     = AliDropshipMoneyBot(tier=Tier.FREE)
        product = {"id": "p001", "title": "Posture Corrector", "niche": "health", "aliexpress_cost_usd": 6.50}
        with pytest.raises(AliDropshipBotTierError):
            bot.run_facebook_ads(product)

    def test_facebook_ads_pro_returns_ads(self):
        bot     = AliDropshipMoneyBot(tier=Tier.PRO)
        product = {"id": "p001", "title": "Posture Corrector", "niche": "health", "aliexpress_cost_usd": 6.50}
        ads     = bot.run_facebook_ads(product)
        assert isinstance(ads, list)
        assert len(ads) > 0

    def test_facebook_ads_have_required_keys(self):
        bot     = AliDropshipMoneyBot(tier=Tier.PRO)
        product = {"id": "p001", "title": "Posture Corrector", "niche": "health", "aliexpress_cost_usd": 6.50}
        ads     = bot.run_facebook_ads(product)
        for ad in ads:
            assert "copy" in ad
            assert "daily_budget" in ad
            assert "roas" in ad
            assert "status" in ad

    def test_facebook_ads_pro_limited_to_5(self):
        bot     = AliDropshipMoneyBot(tier=Tier.PRO)
        product = {"id": "p001", "title": "Posture Corrector", "niche": "health", "aliexpress_cost_usd": 6.50}
        ads     = bot.run_facebook_ads(product)
        assert len(ads) <= 5

    # Influencer Outreach
    def test_influencer_outreach_free_raises(self):
        bot = AliDropshipMoneyBot(tier=Tier.FREE)
        with pytest.raises(AliDropshipBotTierError):
            bot.run_influencer_outreach("fitness")

    def test_influencer_outreach_pro_raises(self):
        bot = AliDropshipMoneyBot(tier=Tier.PRO)
        with pytest.raises(AliDropshipBotTierError):
            bot.run_influencer_outreach("fitness")

    def test_influencer_outreach_enterprise(self):
        bot     = AliDropshipMoneyBot(tier=Tier.ENTERPRISE)
        results = bot.run_influencer_outreach("fitness")
        assert isinstance(results, list)
        assert len(results) > 0
        for r in results:
            assert "handle" in r
            assert "dm_script" in r
            assert r["sent"] is True


# ===========================================================================
# 6. Scaling Engine
# ===========================================================================

class TestScalingEngine:
    def test_scale_or_kill_free_raises(self):
        bot     = AliDropshipMoneyBot(tier=Tier.FREE)
        product = {"id": "p001", "title": "Test"}
        with pytest.raises(AliDropshipBotTierError):
            bot.scale_or_kill_product(product, roi=2.5)

    def test_high_roi_scales(self):
        bot     = AliDropshipMoneyBot(tier=Tier.PRO)
        product = {"id": "p001", "title": "Posture Corrector"}
        result  = bot.scale_or_kill_product(product, roi=3.0)
        assert result["action"] == "scale"

    def test_low_roi_kills(self):
        bot     = AliDropshipMoneyBot(tier=Tier.PRO)
        product = {"id": "p001", "title": "Posture Corrector"}
        result  = bot.scale_or_kill_product(product, roi=0.8)
        assert result["action"] == "kill"

    def test_roi_2_scales(self):
        bot     = AliDropshipMoneyBot(tier=Tier.PRO)
        product = {"id": "p001", "title": "Posture Corrector"}
        result  = bot.scale_or_kill_product(product, roi=2.0)
        assert result["action"] == "scale"

    def test_scale_result_has_budget_increase(self):
        bot     = AliDropshipMoneyBot(tier=Tier.PRO)
        product = {"id": "p001", "title": "Posture Corrector"}
        result  = bot.scale_or_kill_product(product, roi=2.5)
        assert "budget_increase" in result

    def test_kill_result_has_reason(self):
        bot     = AliDropshipMoneyBot(tier=Tier.PRO)
        product = {"id": "p001", "title": "Posture Corrector"}
        result  = bot.scale_or_kill_product(product, roi=1.0)
        assert "reason" in result

    def test_scaling_report_free_raises(self):
        bot = AliDropshipMoneyBot(tier=Tier.FREE)
        with pytest.raises(AliDropshipBotTierError):
            bot.get_scaling_report()

    def test_scaling_report_pro(self):
        bot    = AliDropshipMoneyBot(tier=Tier.PRO)
        report = bot.get_scaling_report()
        assert isinstance(report, list)
        assert len(report) > 0

    def test_scaling_report_custom_rois(self):
        bot    = AliDropshipMoneyBot(tier=Tier.ENTERPRISE)
        rois   = {"p001": 3.0, "p004": 0.5}
        report = bot.get_scaling_report(product_roi_map=rois)
        assert isinstance(report, list)


# ===========================================================================
# Master Orchestrator
# ===========================================================================

class TestMasterOrchestrator:
    def test_free_raises(self):
        bot = AliDropshipMoneyBot(tier=Tier.FREE)
        with pytest.raises(AliDropshipBotTierError):
            bot.run_dreamco_master()

    def test_pro_raises(self):
        bot = AliDropshipMoneyBot(tier=Tier.PRO)
        with pytest.raises(AliDropshipBotTierError):
            bot.run_dreamco_master()

    def test_enterprise_returns_dict(self):
        bot    = AliDropshipMoneyBot(tier=Tier.ENTERPRISE)
        result = bot.run_dreamco_master(niches=["fitness"])
        assert isinstance(result, dict)

    def test_master_result_has_stores(self):
        bot    = AliDropshipMoneyBot(tier=Tier.ENTERPRISE)
        result = bot.run_dreamco_master(niches=["fitness"])
        assert "stores" in result
        assert len(result["stores"]) >= 1

    def test_master_result_has_content_and_ads(self):
        bot    = AliDropshipMoneyBot(tier=Tier.ENTERPRISE)
        result = bot.run_dreamco_master(niches=["beauty"])
        assert "content" in result
        assert "ads" in result


# ===========================================================================
# Support-site network
# ===========================================================================

class TestSupportSiteNetwork:
    def test_free_raises(self):
        bot = AliDropshipMoneyBot(tier=Tier.FREE)
        with pytest.raises(AliDropshipBotTierError):
            bot.build_support_sites("fitness", "https://example.com")

    def test_pro_raises(self):
        bot = AliDropshipMoneyBot(tier=Tier.PRO)
        with pytest.raises(AliDropshipBotTierError):
            bot.build_support_sites("fitness", "https://example.com")

    def test_enterprise_returns_network(self):
        bot    = AliDropshipMoneyBot(tier=Tier.ENTERPRISE)
        result = bot.build_support_sites("fitness", "https://ironedgegear.com")
        assert isinstance(result, dict)
        assert "sites" in result
        assert len(result["sites"]) == 4

    def test_support_sites_link_back(self):
        bot    = AliDropshipMoneyBot(tier=Tier.ENTERPRISE)
        result = bot.build_support_sites("fitness", "https://ironedgegear.com")
        for site in result["sites"]:
            assert site["links_to"] == "https://ironedgegear.com"


# ===========================================================================
# Revenue Projections
# ===========================================================================

class TestRevenueProjections:
    def test_returns_dict(self):
        for tier in (Tier.FREE, Tier.PRO, Tier.ENTERPRISE):
            bot  = AliDropshipMoneyBot(tier=tier)
            proj = bot.get_revenue_projections()
            assert isinstance(proj, dict)
            assert "tier" in proj

    def test_enterprise_has_months_projection(self):
        bot  = AliDropshipMoneyBot(tier=Tier.ENTERPRISE)
        proj = bot.get_revenue_projections()
        assert "months_3_6" in proj


# ===========================================================================
# describe_tier
# ===========================================================================

class TestDescribeTier:
    def test_returns_string(self):
        for tier in (Tier.FREE, Tier.PRO, Tier.ENTERPRISE):
            bot  = AliDropshipMoneyBot(tier=tier)
            desc = bot.describe_tier()
            assert isinstance(desc, str)
            assert "AliDropship Money Bot" in desc

    def test_free_tier_description_contains_price(self):
        bot  = AliDropshipMoneyBot(tier=Tier.FREE)
        desc = bot.describe_tier()
        assert "$0.00" in desc
