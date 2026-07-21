"""
Tests for bots/revenue_growth_bot/tiers.py and bots/revenue_growth_bot/revenue_growth_bot.py
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
AI_MODELS_DIR = os.path.join(REPO_ROOT, 'bots', 'ai-models-integration')
BOT_DIR = os.path.join(REPO_ROOT, 'bots', 'revenue_growth_bot')
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from bots.revenue_growth_bot.revenue_growth_bot import (
    RevenueGrowthBot,
    RevenueGrowthBotTierError,
    RevenueGrowthBotRequestLimitError,
)


# -----------------------------------------------------------------------
# Tier info tests
# -----------------------------------------------------------------------

class TestRevenueGrowthBotTierInfo:
    def _load_tiers(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "_rev_tiers", os.path.join(BOT_DIR, "tiers.py")
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def test_tier_info_keys(self):
        mod = self._load_tiers()
        info = mod.get_revenue_tier_info(Tier.FREE)
        for key in ("tier", "name", "price_usd_monthly", "requests_per_month",
                    "revenue_features", "support_level"):
            assert key in info

    def test_free_price_zero(self):
        mod = self._load_tiers()
        assert mod.get_revenue_tier_info(Tier.FREE)["price_usd_monthly"] == 0.0

    def test_enterprise_unlimited(self):
        mod = self._load_tiers()
        assert mod.get_revenue_tier_info(Tier.ENTERPRISE)["requests_per_month"] is None

    def test_all_tiers_have_features(self):
        mod = self._load_tiers()
        for tier in Tier:
            assert len(mod.get_revenue_tier_info(tier)["revenue_features"]) > 0


# -----------------------------------------------------------------------
# RevenueGrowthBot tests
# -----------------------------------------------------------------------

class TestRevenueGrowthBot:
    def test_default_tier_free(self):
        bot = RevenueGrowthBot()
        assert bot.tier == Tier.FREE

    def test_analyze_revenue_returns_dict(self):
        bot = RevenueGrowthBot()
        result = bot.analyze_revenue({"sales": [100, 200, 300]})
        assert isinstance(result, dict)

    def test_analyze_revenue_keys(self):
        bot = RevenueGrowthBot()
        result = bot.analyze_revenue({"sales": [100, 200]})
        for key in ("metrics", "tier", "requests_used", "requests_remaining"):
            assert key in result

    def test_analyze_revenue_increments_count(self):
        bot = RevenueGrowthBot()
        bot.analyze_revenue({"sales": [100]})
        bot.analyze_revenue({"sales": [200]})
        assert bot._request_count == 2

    def test_optimize_pricing_pro_only(self):
        bot = RevenueGrowthBot(tier=Tier.FREE)
        with pytest.raises(RevenueGrowthBotTierError):
            bot.optimize_pricing({"name": "Widget", "cost": 10.0})

    def test_optimize_pricing_pro_ok(self):
        bot = RevenueGrowthBot(tier=Tier.PRO)
        result = bot.optimize_pricing({"name": "Widget", "cost": 10.0})
        assert isinstance(result, dict)
        assert "suggested_price" in result

    def test_forecast_revenue_enterprise_only(self):
        bot_free = RevenueGrowthBot(tier=Tier.FREE)
        with pytest.raises(RevenueGrowthBotTierError):
            bot_free.forecast_revenue(3)

    def test_forecast_revenue_pro_only(self):
        bot_pro = RevenueGrowthBot(tier=Tier.PRO)
        with pytest.raises(RevenueGrowthBotTierError):
            bot_pro.forecast_revenue(3)

    def test_forecast_revenue_enterprise_ok(self):
        bot = RevenueGrowthBot(tier=Tier.ENTERPRISE)
        result = bot.forecast_revenue(3)
        assert isinstance(result, dict)
        assert "forecasts" in result
        assert len(result["forecasts"]) == 3

    def test_request_limit_raises(self):
        bot = RevenueGrowthBot(tier=Tier.FREE)
        bot._request_count = bot.config.requests_per_month
        with pytest.raises(RevenueGrowthBotRequestLimitError):
            bot.analyze_revenue({})

    def test_enterprise_no_request_limit(self):
        bot = RevenueGrowthBot(tier=Tier.ENTERPRISE)
        bot._request_count = 999_999
        result = bot.analyze_revenue({"sales": [1]})
        assert result["requests_remaining"] == "unlimited"

    def test_describe_tier_returns_string(self):
        bot = RevenueGrowthBot()
        output = bot.describe_tier()
        assert isinstance(output, str)
        assert "Free" in output

    def test_show_upgrade_path_from_free(self):
        bot = RevenueGrowthBot()
        output = bot.show_upgrade_path()
        assert "Pro" in output

    def test_show_upgrade_path_enterprise(self):
        bot = RevenueGrowthBot(tier=Tier.ENTERPRISE)
        output = bot.show_upgrade_path()
        assert "top-tier" in output

    def test_tier_attribute(self):
        for tier in Tier:
            bot = RevenueGrowthBot(tier=tier)
            assert bot.tier == tier
