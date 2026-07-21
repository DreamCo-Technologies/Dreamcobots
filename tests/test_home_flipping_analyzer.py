"""Tests for bots/home_flipping_analyzer/tiers.py and bots/home_flipping_analyzer/home_flipping_analyzer.py"""
import sys, os

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
AI_MODELS_DIR = os.path.join(REPO_ROOT, 'bots', 'ai-models-integration')
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, os.path.join(AI_MODELS_DIR, 'models'))
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from bots.home_flipping_analyzer.home_flipping_analyzer import HomeFlippingAnalyzerBot, HomeFlippingAnalyzerTierError
from bots.home_flipping_analyzer.tiers import BOT_FEATURES, get_bot_tier_info


class TestHomeFlippingAnalyzerInstantiation:
    def test_default_tier_is_free(self):
        bot = HomeFlippingAnalyzerBot()
        assert bot.tier == Tier.FREE

    def test_pro_tier(self):
        bot = HomeFlippingAnalyzerBot(tier=Tier.PRO)
        assert bot.tier == Tier.PRO

    def test_enterprise_tier(self):
        bot = HomeFlippingAnalyzerBot(tier=Tier.ENTERPRISE)
        assert bot.tier == Tier.ENTERPRISE

    def test_config_loaded(self):
        bot = HomeFlippingAnalyzerBot()
        assert bot.config is not None

    def test_flow_initialized(self):
        bot = HomeFlippingAnalyzerBot()
        assert bot.flow is not None


class TestTiersModule:
    def test_bot_features_has_all_tiers(self):
        assert Tier.FREE.value in BOT_FEATURES
        assert Tier.PRO.value in BOT_FEATURES
        assert Tier.ENTERPRISE.value in BOT_FEATURES

    def test_get_bot_tier_info_returns_dict(self):
        info = get_bot_tier_info(Tier.FREE)
        assert isinstance(info, dict)

    def test_get_bot_tier_info_has_required_keys(self):
        info = get_bot_tier_info(Tier.PRO)
        for key in ("tier", "name", "price_usd_monthly", "features", "support_level"):
            assert key in info

    def test_enterprise_has_more_features_than_free(self):
        assert len(BOT_FEATURES[Tier.ENTERPRISE.value]) > len(BOT_FEATURES[Tier.FREE.value])


class TestAnalyzeFlip:
    def test_returns_dict(self):
        bot = HomeFlippingAnalyzerBot(tier=Tier.FREE)
        result = bot.analyze_flip("FLP001")
        assert isinstance(result, dict)

    def test_has_required_keys(self):
        bot = HomeFlippingAnalyzerBot(tier=Tier.FREE)
        result = bot.analyze_flip("FLP001")
        for key in ("arv_usd", "renovation_cost_usd", "estimated_profit_usd", "flip_score", "roi_pct"):
            assert key in result

    def test_flip_score_in_range(self):
        bot = HomeFlippingAnalyzerBot(tier=Tier.FREE)
        result = bot.analyze_flip("FLP001")
        assert 0 <= result["flip_score"] <= 100

    def test_free_tier_property_limit(self):
        bot = HomeFlippingAnalyzerBot(tier=Tier.FREE)
        bot.analyze_flip("FLP001")
        with pytest.raises(HomeFlippingAnalyzerTierError):
            bot.analyze_flip("FLP002")

    def test_pro_allows_5_properties(self):
        bot = HomeFlippingAnalyzerBot(tier=Tier.PRO)
        for pid in ["FLP001", "FLP002", "FLP003", "FLP004", "FLP005"]:
            result = bot.analyze_flip(pid)
            assert isinstance(result, dict)

    def test_pro_includes_itemized_renovation(self):
        bot = HomeFlippingAnalyzerBot(tier=Tier.PRO)
        result = bot.analyze_flip("FLP001")
        assert "itemized_renovation" in result

    def test_enterprise_unlimited_properties(self):
        bot = HomeFlippingAnalyzerBot(tier=Tier.ENTERPRISE)
        for pid in list(HomeFlippingAnalyzerBot.FLIP_DATABASE.keys())[:10]:
            result = bot.analyze_flip(pid)
            assert isinstance(result, dict)

    def test_enterprise_has_market_timing_score(self):
        bot = HomeFlippingAnalyzerBot(tier=Tier.ENTERPRISE)
        result = bot.analyze_flip("FLP001")
        assert "market_timing_score" in result

    def test_address_lookup(self):
        bot = HomeFlippingAnalyzerBot(tier=Tier.FREE)
        result = bot.analyze_flip("Memphis")
        assert isinstance(result, dict)
        assert "flip_score" in result


class TestCalculateARV:
    def test_returns_float(self):
        bot = HomeFlippingAnalyzerBot(tier=Tier.FREE)
        arv = bot.calculate_arv("FLP001")
        assert isinstance(arv, (int, float))
        assert arv > 0

    def test_pro_uses_comps(self):
        bot = HomeFlippingAnalyzerBot(tier=Tier.PRO)
        comps = [155000, 160000, 148000]
        arv_with_comps = bot.calculate_arv("FLP001", comparable_sales=comps)
        arv_without = bot.calculate_arv("FLP001")
        assert arv_with_comps != arv_without

    def test_enterprise_appreciates_value(self):
        bot_ent = HomeFlippingAnalyzerBot(tier=Tier.ENTERPRISE)
        bot_free = HomeFlippingAnalyzerBot(tier=Tier.FREE)
        arv_ent = bot_ent.calculate_arv("FLP018")  # Austin market, high appreciation
        arv_free = bot_free.calculate_arv("FLP018")
        assert arv_ent >= arv_free


class TestEstimateRenovationCost:
    def test_returns_dict_with_total(self):
        bot = HomeFlippingAnalyzerBot(tier=Tier.FREE)
        result = bot.estimate_renovation_cost("FLP001", "moderate")
        assert "estimated_total_usd" in result
        assert result["estimated_total_usd"] > 0

    def test_full_gut_more_expensive_than_cosmetic(self):
        bot = HomeFlippingAnalyzerBot(tier=Tier.FREE)
        cosmetic = bot.estimate_renovation_cost("FLP001", "cosmetic")
        full_gut = bot.estimate_renovation_cost("FLP001", "full_gut")
        assert full_gut["estimated_total_usd"] > cosmetic["estimated_total_usd"]

    def test_pro_includes_itemized_costs(self):
        bot = HomeFlippingAnalyzerBot(tier=Tier.PRO)
        result = bot.estimate_renovation_cost("FLP001", "full_gut")
        assert "itemized_costs" in result
        assert isinstance(result["itemized_costs"], dict)

    def test_enterprise_includes_contractor_bids(self):
        bot = HomeFlippingAnalyzerBot(tier=Tier.ENTERPRISE)
        result = bot.estimate_renovation_cost("FLP001", "full_gut")
        assert "contractor_bids" in result
        assert len(result["contractor_bids"]) == 3


class TestGetTopFlipOpportunities:
    def test_returns_list(self):
        bot = HomeFlippingAnalyzerBot(tier=Tier.FREE)
        results = bot.get_top_flip_opportunities(limit=5)
        assert isinstance(results, list)

    def test_respects_limit(self):
        bot = HomeFlippingAnalyzerBot(tier=Tier.FREE)
        results = bot.get_top_flip_opportunities(limit=3)
        assert len(results) <= 3

    def test_sorted_by_flip_score(self):
        bot = HomeFlippingAnalyzerBot(tier=Tier.FREE)
        results = bot.get_top_flip_opportunities(limit=5)
        scores = [r["flip_score"] for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_each_result_has_required_keys(self):
        bot = HomeFlippingAnalyzerBot(tier=Tier.FREE)
        results = bot.get_top_flip_opportunities(limit=5)
        for r in results:
            assert "flip_score" in r
            assert "estimated_profit_usd" in r
            assert "address" in r


class TestDescribeTier:
    def test_returns_string(self):
        bot = HomeFlippingAnalyzerBot(tier=Tier.FREE)
        result = bot.describe_tier()
        assert isinstance(result, str)

    def test_contains_tier_name(self):
        bot = HomeFlippingAnalyzerBot(tier=Tier.PRO)
        result = bot.describe_tier()
        assert "Pro" in result


class TestRunPipeline:
    def test_run_returns_dict(self):
        bot = HomeFlippingAnalyzerBot(tier=Tier.FREE)
        result = bot.run()
        assert isinstance(result, dict)

    def test_run_pro_tier(self):
        bot = HomeFlippingAnalyzerBot(tier=Tier.PRO)
        result = bot.run()
        assert isinstance(result, dict)
