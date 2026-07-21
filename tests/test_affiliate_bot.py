"""Tests for bots/affiliate_bot/tiers.py and bots/affiliate_bot/affiliate_bot.py"""
import sys, os

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
AI_MODELS_DIR = os.path.join(REPO_ROOT, 'bots', 'ai-models-integration')
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, os.path.join(AI_MODELS_DIR, 'models'))
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from bots.affiliate_bot.affiliate_bot import AffiliateBot, AffiliateBotTierError


class TestAffiliateBotInstantiation:
    def test_default_tier_is_free(self):
        bot = AffiliateBot()
        assert bot.tier == Tier.FREE

    def test_pro_tier(self):
        bot = AffiliateBot(tier=Tier.PRO)
        assert bot.tier == Tier.PRO

    def test_enterprise_tier(self):
        bot = AffiliateBot(tier=Tier.ENTERPRISE)
        assert bot.tier == Tier.ENTERPRISE

    def test_config_loaded(self):
        bot = AffiliateBot(tier=Tier.FREE)
        assert bot.config is not None


class TestAffiliateBotTierFeatures:
    def test_free_tier_features_present(self):
        from bots.affiliate_bot.tiers import BOT_FEATURES
        assert len(BOT_FEATURES[Tier.FREE.value]) > 0

    def test_pro_tier_has_more_features_than_free(self):
        from bots.affiliate_bot.tiers import BOT_FEATURES
        assert len(BOT_FEATURES[Tier.PRO.value]) > len(BOT_FEATURES[Tier.FREE.value])

    def test_enterprise_tier_has_api_access(self):
        from bots.affiliate_bot.tiers import BOT_FEATURES
        assert any("API" in f for f in BOT_FEATURES[Tier.ENTERPRISE.value])


class TestRecommendProducts:
    def test_returns_list(self):
        bot = AffiliateBot(tier=Tier.FREE)
        result = bot.recommend_products("tech")
        assert isinstance(result, list)

    def test_each_product_has_required_keys(self):
        bot = AffiliateBot(tier=Tier.FREE)
        products = bot.recommend_products("tech")
        assert len(products) > 0
        for p in products:
            assert "name" in p
            assert "commission_rate" in p
            assert "avg_price" in p

    def test_free_niche_limit_enforced(self):
        bot = AffiliateBot(tier=Tier.FREE)
        bot.recommend_products("tech")
        bot.recommend_products("fitness")
        bot.recommend_products("home")
        with pytest.raises(AffiliateBotTierError):
            bot.recommend_products("beauty")

    def test_pro_allows_more_niches(self):
        bot = AffiliateBot(tier=Tier.PRO)
        for niche in ["tech", "fitness", "home", "beauty", "finance"]:
            result = bot.recommend_products(niche)
            assert isinstance(result, list)

    def test_enterprise_unlimited_niches(self):
        bot = AffiliateBot(tier=Tier.ENTERPRISE)
        niches = ["tech", "fitness", "home", "beauty", "finance", "travel", "food", "gaming", "education", "pets"]
        for niche in niches:
            result = bot.recommend_products(niche)
            assert isinstance(result, list)

    def test_pro_higher_earnings_than_free(self):
        free_bot = AffiliateBot(tier=Tier.FREE)
        pro_bot = AffiliateBot(tier=Tier.PRO)
        free_products = free_bot.recommend_products("tech")
        pro_products = pro_bot.recommend_products("tech")
        free_total = sum(p["estimated_monthly_earnings"] for p in free_products)
        pro_total = sum(p["estimated_monthly_earnings"] for p in pro_products)
        assert pro_total > free_total


class TestGenerateReport:
    def test_report_is_dict(self):
        bot = AffiliateBot(tier=Tier.FREE)
        bot.recommend_products("tech")
        report = bot.generate_report()
        assert isinstance(report, dict)

    def test_report_has_required_keys(self):
        bot = AffiliateBot(tier=Tier.FREE)
        bot.recommend_products("tech")
        report = bot.generate_report()
        for key in ("tracked_niches", "total_clicks", "estimated_monthly_revenue_usd", "tier", "features"):
            assert key in report

    def test_pro_report_has_detailed_breakdown(self):
        bot = AffiliateBot(tier=Tier.PRO)
        bot.recommend_products("tech")
        bot.track_clicks("p001")
        report = bot.generate_report()
        assert "detailed_breakdown" in report

    def test_free_report_no_detailed_breakdown(self):
        bot = AffiliateBot(tier=Tier.FREE)
        bot.recommend_products("tech")
        report = bot.generate_report()
        assert "detailed_breakdown" not in report
