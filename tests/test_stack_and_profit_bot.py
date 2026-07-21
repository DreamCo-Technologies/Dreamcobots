"""Tests for bots/stack_and_profit_bot/tiers.py and bots/stack_and_profit_bot/stack_and_profit_bot.py"""
import sys, os

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
AI_MODELS_DIR = os.path.join(REPO_ROOT, 'bots', 'ai-models-integration')
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, os.path.join(AI_MODELS_DIR, 'models'))
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from bots.stack_and_profit_bot.stack_and_profit_bot import (
    StackAndProfitBot,
    StackAndProfitBotTierError,
    ProfitEngine,
    RankingAI,
    AlertEngine,
    DealBot,
    PennyBot,
    ReceiptBot,
    FlipBot,
    CouponBot,
    _load_deals,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def deals():
    return _load_deals()


@pytest.fixture
def free_bot():
    return StackAndProfitBot(tier=Tier.FREE)


@pytest.fixture
def pro_bot():
    return StackAndProfitBot(tier=Tier.PRO)


@pytest.fixture
def enterprise_bot():
    return StackAndProfitBot(tier=Tier.ENTERPRISE)


# ---------------------------------------------------------------------------
# Instantiation
# ---------------------------------------------------------------------------

class TestStackAndProfitBotInstantiation:
    def test_default_tier_is_free(self):
        bot = StackAndProfitBot()
        assert bot.tier == Tier.FREE

    def test_pro_tier(self):
        bot = StackAndProfitBot(tier=Tier.PRO)
        assert bot.tier == Tier.PRO

    def test_enterprise_tier(self):
        bot = StackAndProfitBot(tier=Tier.ENTERPRISE)
        assert bot.tier == Tier.ENTERPRISE

    def test_config_loaded(self, free_bot):
        assert free_bot.config is not None

    def test_sub_bots_initialized(self, pro_bot):
        assert pro_bot.deal_bot is not None
        assert pro_bot.penny_bot is not None
        assert pro_bot.receipt_bot is not None
        assert pro_bot.flip_bot is not None
        assert pro_bot.coupon_bot is not None

    def test_ai_engines_initialized(self, pro_bot):
        assert pro_bot.profit_engine is not None
        assert pro_bot.ranking_ai is not None
        assert pro_bot.alert_engine is not None


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

class TestDealsData:
    def test_loads_50_deals(self, deals):
        assert len(deals) == 50

    def test_deals_have_required_keys(self, deals):
        required = {"id", "name", "source", "type", "category", "price", "current",
                    "resale", "coupon", "cashback", "profit", "effort", "fast_payout"}
        for deal in deals:
            assert required.issubset(deal.keys()), f"Deal {deal.get('id')} missing keys"

    def test_deals_have_positive_prices(self, deals):
        for deal in deals:
            assert float(deal["price"]) >= 0
            assert float(deal["current"]) >= 0

    def test_deals_include_electronics(self, deals):
        categories = {d["category"] for d in deals}
        assert "electronics" in categories

    def test_deals_include_multiple_types(self, deals):
        types = {d["type"] for d in deals}
        assert len(types) >= 4


# ---------------------------------------------------------------------------
# ProfitEngine
# ---------------------------------------------------------------------------

class TestProfitEngine:
    def test_returns_dict(self):
        result = ProfitEngine.calculate({"current": 25, "coupon": 5, "cashback": 3, "resale": 70})
        assert isinstance(result, dict)

    def test_final_cost_formula(self):
        result = ProfitEngine.calculate({"current": 25, "coupon": 5, "cashback": 3, "resale": 70})
        assert result["final_cost"] == 17.00

    def test_profit_formula(self):
        result = ProfitEngine.calculate({"current": 25, "coupon": 5, "cashback": 3, "resale": 70})
        assert result["profit"] == 53.00

    def test_zero_resale_returns_savings(self):
        result = ProfitEngine.calculate({"current": 10, "coupon": 3, "cashback": 2, "resale": 0})
        assert result["profit"] == 5.00

    def test_final_cost_never_negative(self):
        result = ProfitEngine.calculate({"current": 5, "coupon": 10, "cashback": 5, "resale": 0})
        assert result["final_cost"] == 0.0

    def test_handles_missing_coupon_cashback(self):
        result = ProfitEngine.calculate({"current": 100, "resale": 150})
        assert result["final_cost"] == 100.0
        assert result["profit"] == 50.0


# ---------------------------------------------------------------------------
# RankingAI
# ---------------------------------------------------------------------------

class TestRankingAI:
    def test_score_returns_int(self):
        deal = {"profit": 80, "effort": 1, "fast_payout": True, "category": "electronics"}
        assert isinstance(RankingAI.score(deal), int)

    def test_score_in_range(self):
        deal = {"profit": 80, "effort": 1, "fast_payout": True, "category": "electronics"}
        score = RankingAI.score(deal)
        assert 0 <= score <= 100

    def test_high_profit_scores_higher(self):
        high = {"profit": 150, "effort": 1, "fast_payout": True, "category": "electronics"}
        low = {"profit": 5, "effort": 3, "fast_payout": False, "category": "clothing"}
        assert RankingAI.score(high) > RankingAI.score(low)

    def test_rank_returns_sorted_list(self, deals):
        ranked = RankingAI.rank(deals[:10])
        assert isinstance(ranked, list)
        scores = [d["rank_score"] for d in ranked]
        assert scores == sorted(scores, reverse=True)

    def test_rank_adds_rank_score_key(self, deals):
        ranked = RankingAI.rank(deals[:5])
        for d in ranked:
            assert "rank_score" in d

    def test_electronics_gets_bonus(self):
        elec = {"profit": 30, "effort": 2, "fast_payout": False, "category": "electronics"}
        clothing = {"profit": 30, "effort": 2, "fast_payout": False, "category": "clothing"}
        assert RankingAI.score(elec) > RankingAI.score(clothing)


# ---------------------------------------------------------------------------
# AlertEngine
# ---------------------------------------------------------------------------

class TestAlertEngine:
    def test_should_alert_high_profit(self):
        deal = {"profit": 50, "effort": 1, "fast_payout": True, "category": "electronics"}
        assert AlertEngine.should_alert(deal) is True

    def test_should_not_alert_low_profit(self):
        deal = {"profit": 2, "effort": 3, "fast_payout": False, "category": "clothing"}
        assert AlertEngine.should_alert(deal) is False

    def test_filter_alerts_returns_list(self, deals):
        alerts = AlertEngine.filter_alerts(deals)
        assert isinstance(alerts, list)

    def test_filter_alerts_all_meet_threshold(self, deals):
        alerts = AlertEngine.filter_alerts(deals)
        for d in alerts:
            assert AlertEngine.should_alert(d) is True


# ---------------------------------------------------------------------------
# DealBot
# ---------------------------------------------------------------------------

class TestDealBot:
    def test_run_returns_list(self, deals):
        bot = DealBot(Tier.FREE, deals)
        result = bot.run()
        assert isinstance(result, list)

    def test_free_limited_to_5_items(self, deals):
        bot = DealBot(Tier.FREE, deals)
        result = bot.run(min_profit=0)
        assert len(result) <= 5

    def test_pro_limited_to_50_items(self, deals):
        bot = DealBot(Tier.PRO, deals)
        result = bot.run(min_profit=0)
        assert len(result) <= 50

    def test_filters_by_min_profit(self, deals):
        bot = DealBot(Tier.PRO, deals)
        result = bot.run(min_profit=100)
        for deal in result:
            assert float(deal.get("profit", 0)) >= 100

    def test_results_include_profit_calculation(self, deals):
        bot = DealBot(Tier.PRO, deals)
        result = bot.run(min_profit=15)
        for deal in result:
            assert "final_cost" in deal
            assert "profit" in deal


# ---------------------------------------------------------------------------
# PennyBot
# ---------------------------------------------------------------------------

class TestPennyBot:
    def test_run_returns_list(self, deals):
        bot = PennyBot(Tier.FREE, deals)
        assert isinstance(bot.run(), list)

    def test_returns_only_penny_items(self, deals):
        bot = PennyBot(Tier.PRO, deals)
        result = bot.run()
        for d in result:
            assert float(d["current"]) <= 1.00

    def test_free_limited_to_3_items(self, deals):
        bot = PennyBot(Tier.FREE, deals)
        result = bot.run()
        assert len(result) <= 3

    def test_pro_returns_all_penny_items(self, deals):
        bot_free = PennyBot(Tier.FREE, deals)
        bot_pro = PennyBot(Tier.PRO, deals)
        assert len(bot_pro.run()) >= len(bot_free.run())


# ---------------------------------------------------------------------------
# ReceiptBot
# ---------------------------------------------------------------------------

class TestReceiptBot:
    def test_free_raises_tier_error(self, deals):
        bot = ReceiptBot(Tier.FREE, deals)
        with pytest.raises(StackAndProfitBotTierError):
            bot.scan_receipt(["Grocery Bundle"])

    def test_pro_can_scan(self, deals):
        bot = ReceiptBot(Tier.PRO, deals)
        result = bot.scan_receipt(["Grocery"])
        assert isinstance(result, dict)
        assert "total_cashback_usd" in result

    def test_scan_returns_required_keys(self, deals):
        bot = ReceiptBot(Tier.PRO, deals)
        result = bot.scan_receipt(["Grocery"])
        assert "items_submitted" in result
        assert "matches_found" in result
        assert "matched_deals" in result

    def test_get_cashback_sources_returns_list(self, deals):
        bot = ReceiptBot(Tier.PRO, deals)
        assert isinstance(bot.get_cashback_sources(), list)

    def test_free_gets_fewer_sources(self, deals):
        free_bot = ReceiptBot(Tier.FREE, deals)
        pro_bot = ReceiptBot(Tier.PRO, deals)
        assert len(free_bot.get_cashback_sources()) <= len(pro_bot.get_cashback_sources())


# ---------------------------------------------------------------------------
# FlipBot
# ---------------------------------------------------------------------------

class TestFlipBot:
    def test_free_raises_tier_error(self, deals):
        bot = FlipBot(Tier.FREE, deals)
        with pytest.raises(StackAndProfitBotTierError):
            bot.run()

    def test_pro_returns_list(self, deals):
        bot = FlipBot(Tier.PRO, deals)
        result = bot.run()
        assert isinstance(result, list)

    def test_results_sorted_by_rank(self, deals):
        bot = FlipBot(Tier.PRO, deals)
        result = bot.run(min_profit=0)
        scores = [d.get("rank_score", 0) for d in result]
        assert scores == sorted(scores, reverse=True)

    def test_estimate_flip_profit_returns_dict(self, deals):
        bot = FlipBot(Tier.PRO, deals)
        result = bot.estimate_flip_profit(100.0, 200.0)
        assert isinstance(result, dict)
        assert "net_profit" in result
        assert "roi_pct" in result

    def test_estimate_flip_profit_formula(self, deals):
        bot = FlipBot(Tier.PRO, deals)
        result = bot.estimate_flip_profit(100.0, 200.0, fees_pct=0.10)
        assert result["gross_profit"] == 100.0
        assert result["platform_fees"] == 20.0
        assert result["net_profit"] == 80.0

    def test_pro_limited_to_10_flips(self, deals):
        bot = FlipBot(Tier.PRO, deals)
        result = bot.run(min_profit=0)
        assert len(result) <= 10


# ---------------------------------------------------------------------------
# CouponBot
# ---------------------------------------------------------------------------

class TestCouponBot:
    def test_run_returns_list(self, deals):
        bot = CouponBot(Tier.FREE, deals)
        assert isinstance(bot.run(), list)

    def test_results_have_stacked_savings(self, deals):
        bot = CouponBot(Tier.PRO, deals)
        result = bot.run()
        for d in result:
            assert "stacked_savings" in d
            assert "final_price" in d

    def test_stacked_savings_formula(self, deals):
        bot = CouponBot(Tier.PRO, deals)
        result = bot.run()
        for d in result:
            expected = round(float(d.get("coupon", 0)) + float(d.get("cashback", 0)), 2)
            assert d["stacked_savings"] == expected

    def test_get_available_sources_returns_list(self, deals):
        bot = CouponBot(Tier.FREE, deals)
        assert isinstance(bot.get_available_sources(), list)

    def test_pro_has_more_sources_than_free(self, deals):
        free_bot = CouponBot(Tier.FREE, deals)
        pro_bot = CouponBot(Tier.PRO, deals)
        assert len(pro_bot.get_available_sources()) >= len(free_bot.get_available_sources())


# ---------------------------------------------------------------------------
# StackAndProfitBot orchestration
# ---------------------------------------------------------------------------

class TestRunAllBots:
    def test_returns_dict(self, free_bot):
        result = free_bot.run_all_bots()
        assert isinstance(result, dict)

    def test_free_has_deal_penny_coupon(self, free_bot):
        result = free_bot.run_all_bots()
        assert "deal_bot" in result
        assert "penny_bot" in result
        assert "coupon_bot" in result

    def test_free_no_flip_bot(self, free_bot):
        result = free_bot.run_all_bots()
        assert "flip_bot" not in result

    def test_pro_has_all_bots(self, pro_bot):
        result = pro_bot.run_all_bots()
        assert "deal_bot" in result
        assert "penny_bot" in result
        assert "coupon_bot" in result
        assert "flip_bot" in result
        assert "receipt_bot_sources" in result

    def test_enterprise_has_all_bots(self, enterprise_bot):
        result = enterprise_bot.run_all_bots()
        assert "flip_bot" in result

    def test_tier_included_in_result(self, pro_bot):
        result = pro_bot.run_all_bots()
        assert result["tier"] == "pro"


class TestGetTopDeals:
    def test_returns_list(self, free_bot):
        assert isinstance(free_bot.get_top_deals(), list)

    def test_limit_respected(self, pro_bot):
        result = pro_bot.get_top_deals(limit=5)
        assert len(result) <= 5

    def test_free_capped_at_5(self, free_bot):
        result = free_bot.get_top_deals(limit=20)
        assert len(result) <= 5

    def test_sorted_by_rank_score(self, pro_bot):
        result = pro_bot.get_top_deals(limit=10)
        scores = [d.get("rank_score", 0) for d in result]
        assert scores == sorted(scores, reverse=True)


class TestDealFilters:
    def test_get_deals_by_category(self, pro_bot):
        result = pro_bot.get_deals_by_category("electronics")
        assert all(d["category"] == "electronics" for d in result)
        assert len(result) > 0

    def test_get_deals_by_type(self, pro_bot):
        result = pro_bot.get_deals_by_type("clearance")
        assert all(d["type"] == "clearance" for d in result)
        assert len(result) > 0

    def test_get_deals_by_category_case_insensitive(self, pro_bot):
        result = pro_bot.get_deals_by_category("Electronics")
        assert len(result) > 0

    def test_rank_deals(self, pro_bot):
        deals = pro_bot.get_deals_by_category("electronics")
        ranked = pro_bot.rank_deals(deals)
        scores = [d["rank_score"] for d in ranked]
        assert scores == sorted(scores, reverse=True)

    def test_get_alerts(self, pro_bot):
        top = pro_bot.get_top_deals(limit=20)
        alerts = pro_bot.get_alerts(top)
        for a in alerts:
            assert AlertEngine.should_alert(a) is True

    def test_calculate_profit(self, free_bot):
        deal = {"current": 30, "coupon": 5, "cashback": 3, "resale": 60}
        result = free_bot.calculate_profit(deal)
        assert "profit" in result
        assert result["profit"] > 0


class TestMonetizationHelpers:
    def test_free_affiliate_raises_tier_error(self, free_bot):
        with pytest.raises(StackAndProfitBotTierError):
            free_bot.get_affiliate_deals()

    def test_pro_affiliate_returns_list(self, pro_bot):
        result = pro_bot.get_affiliate_deals()
        assert isinstance(result, list)

    def test_get_subscription_summary_returns_dict(self, free_bot):
        result = free_bot.get_subscription_summary()
        assert isinstance(result, dict)
        assert "current_tier" in result
        assert "upgrade_available" in result

    def test_free_has_upgrade_available(self, free_bot):
        result = free_bot.get_subscription_summary()
        assert result["upgrade_available"] is True

    def test_enterprise_no_upgrade(self, enterprise_bot):
        result = enterprise_bot.get_subscription_summary()
        assert result["upgrade_available"] is False


class TestDescribeTier:
    def test_returns_string(self, free_bot):
        result = free_bot.describe_tier()
        assert isinstance(result, str)

    def test_contains_tier_name(self, pro_bot):
        result = pro_bot.describe_tier()
        assert "Pro" in result

    def test_contains_price(self, free_bot):
        result = free_bot.describe_tier()
        assert "$" in result

    def test_contains_features(self, free_bot):
        result = free_bot.describe_tier()
        assert "dealBot" in result


# ---------------------------------------------------------------------------
# Bot library registration
# ---------------------------------------------------------------------------

class TestBotLibraryRegistration:
    def test_stack_and_profit_bot_in_library(self):
        import sys, os
        sys.path.insert(0, os.path.join(REPO_ROOT, 'bots', 'global_bot_network'))
        from bot_library import _DREAMCO_BOTS
        ids = [e.bot_id for e in _DREAMCO_BOTS]
        assert "stack_and_profit_bot" in ids

    def test_bot_has_correct_class_name(self):
        import sys, os
        sys.path.insert(0, os.path.join(REPO_ROOT, 'bots', 'global_bot_network'))
        from bot_library import _DREAMCO_BOTS
        entry = next(e for e in _DREAMCO_BOTS if e.bot_id == "stack_and_profit_bot")
        assert entry.class_name == "StackAndProfitBot"

    def test_bot_has_required_capabilities(self):
        import sys, os
        sys.path.insert(0, os.path.join(REPO_ROOT, 'bots', 'global_bot_network'))
        from bot_library import _DREAMCO_BOTS
        entry = next(e for e in _DREAMCO_BOTS if e.bot_id == "stack_and_profit_bot")
        for cap in ["deal_scanning", "penny_deals", "flip_finding", "coupon_stacking"]:
            assert cap in entry.capabilities


# ---------------------------------------------------------------------------
# Additional tests — 25 new test methods reaching 105 total
# ---------------------------------------------------------------------------

class TestProfitEngineEdgeCases:
    """ProfitEngine edge cases: zero price, no resale, large numbers."""

    def test_zero_price_returns_zero_final_cost(self):
        result = ProfitEngine.calculate({"price": 0, "coupon": 0, "cashback": 0})
        assert result["final_cost"] == 0.0

    def test_no_resale_profit_equals_cashback_plus_coupon(self):
        result = ProfitEngine.calculate({"price": 50, "coupon": 5, "cashback": 3})
        assert result["profit"] == 8.0

    def test_large_numbers_precision(self):
        result = ProfitEngine.calculate({"price": 9999.99, "coupon": 1000.00, "cashback": 500.00, "resale": 15000.00})
        assert result["final_cost"] == 8499.99
        assert result["profit"] == round(15000.00 - 8499.99, 2)

    def test_coupon_exceeds_price_clamps_to_zero(self):
        result = ProfitEngine.calculate({"price": 5, "coupon": 10, "cashback": 0})
        assert result["final_cost"] == 0.0

    def test_resale_zero_falls_back_to_coupon_cashback(self):
        result = ProfitEngine.calculate({"current": 20, "coupon": 4, "cashback": 2, "resale": 0})
        assert result["profit"] == 6.0


class TestRankingAIEdgeCases:
    """RankingAI score ranges: capped at 100, zero-profit deals."""

    def test_score_capped_at_100(self):
        deal = {"profit": 200, "effort": 1, "fast_payout": True, "category": "electronics"}
        assert RankingAI.score(deal) == 100

    def test_zero_profit_deal_scores_above_zero_with_fast_payout(self):
        deal = {"profit": 0, "effort": 1, "fast_payout": True}
        score = RankingAI.score(deal)
        assert score > 0

    def test_zero_profit_no_fast_payout_minimum_score(self):
        deal = {"profit": 0, "effort": 5, "fast_payout": False, "category": "misc"}
        assert RankingAI.score(deal) == 5

    def test_rank_returns_sorted_descending(self):
        deals = [
            {"profit": 10, "effort": 3},
            {"profit": 200, "effort": 1, "fast_payout": True, "category": "electronics"},
            {"profit": 30, "effort": 2},
        ]
        ranked = RankingAI.rank(deals)
        scores = [d["rank_score"] for d in ranked]
        assert scores == sorted(scores, reverse=True)

    def test_electronics_category_bonus_applied(self):
        deal_elec = {"profit": 25, "effort": 3, "category": "electronics"}
        deal_other = {"profit": 25, "effort": 3, "category": "clothing"}
        assert RankingAI.score(deal_elec) > RankingAI.score(deal_other)


class TestAlertEngineMinProfit:
    """AlertEngine with min_profit parameter on StackAndProfitBot.get_alerts."""

    def setup_method(self):
        self.bot = StackAndProfitBot(Tier.PRO)
        self.deals = [
            {"name": "Big Deal", "profit": 100, "effort": 2, "fast_payout": True},
            {"name": "Small Deal", "profit": 5, "effort": 3},
            {"name": "Medium Deal", "profit": 30, "effort": 2},
        ]

    def test_get_alerts_no_min_profit_uses_default(self):
        alerts = self.bot.get_alerts(self.deals)
        assert isinstance(alerts, list)

    def test_get_alerts_min_profit_filters_below_threshold(self):
        alerts = self.bot.get_alerts(self.deals, min_profit=50)
        for d in alerts:
            assert float(d.get("profit", 0)) >= 50

    def test_get_alerts_min_profit_zero_allows_all_alertable(self):
        alerts = self.bot.get_alerts(self.deals, min_profit=0)
        assert len(alerts) >= 1

    def test_get_alerts_min_profit_very_high_returns_empty(self):
        alerts = self.bot.get_alerts(self.deals, min_profit=99999)
        assert alerts == []

    def test_get_alerts_min_profit_respects_alert_engine_threshold(self):
        alerts = self.bot.get_alerts(self.deals, min_profit=20)
        for d in alerts:
            assert AlertEngine.should_alert(d)


class TestFlipBotEstimateFlipProfit:
    """FlipBot.estimate_flip_profit calculations."""

    def setup_method(self):
        self.bot = StackAndProfitBot(Tier.PRO)

    def test_basic_flip_profit(self):
        result = self.bot.flip_bot.estimate_flip_profit(50.0, 100.0)
        assert result["gross_profit"] == 50.0
        assert result["net_profit"] < 50.0

    def test_flip_fees_calculated_correctly(self):
        result = self.bot.flip_bot.estimate_flip_profit(50.0, 100.0, fees_pct=0.10)
        assert result["platform_fees"] == 10.0
        assert result["net_profit"] == 40.0

    def test_flip_roi_positive_when_profitable(self):
        result = self.bot.flip_bot.estimate_flip_profit(20.0, 50.0, fees_pct=0.0)
        assert result["roi_pct"] > 0

    def test_flip_zero_buy_price_roi_zero(self):
        result = self.bot.flip_bot.estimate_flip_profit(0.0, 50.0)
        assert result["roi_pct"] == 0


class TestCouponBotSources:
    """CouponBot.get_available_sources per tier."""

    def test_free_tier_limited_sources(self):
        bot = StackAndProfitBot(Tier.FREE)
        sources = bot.coupon_bot.get_available_sources()
        assert len(sources) <= 3

    def test_pro_tier_more_sources_than_free(self):
        free_bot = StackAndProfitBot(Tier.FREE)
        pro_bot = StackAndProfitBot(Tier.PRO)
        assert len(pro_bot.coupon_bot.get_available_sources()) > len(free_bot.coupon_bot.get_available_sources())

    def test_sources_returns_list(self):
        bot = StackAndProfitBot(Tier.PRO)
        assert isinstance(bot.coupon_bot.get_available_sources(), list)


class TestReceiptBotScanReceipt:
    """ReceiptBot.scan_receipt: PRO raises no error, FREE raises error."""

    def test_pro_scan_receipt_no_error(self):
        bot = StackAndProfitBot(Tier.PRO)
        result = bot.receipt_bot.scan_receipt(["groceries"])
        assert "items_submitted" in result

    def test_free_scan_receipt_raises_tier_error(self):
        bot = StackAndProfitBot(Tier.FREE)
        with pytest.raises(StackAndProfitBotTierError):
            bot.receipt_bot.scan_receipt(["groceries"])

    def test_enterprise_scan_receipt_no_error(self):
        bot = StackAndProfitBot(Tier.ENTERPRISE)
        result = bot.receipt_bot.scan_receipt([])
        assert result["items_submitted"] == 0


class TestLoadPreloadedDeals:
    """load_preloaded_deals() method."""

    def test_returns_list(self):
        bot = StackAndProfitBot(Tier.FREE)
        deals = bot.load_preloaded_deals()
        assert isinstance(deals, list)

    def test_returns_50_deals(self):
        bot = StackAndProfitBot(Tier.FREE)
        deals = bot.load_preloaded_deals()
        assert len(deals) == 50

    def test_returns_copy_not_original(self):
        bot = StackAndProfitBot(Tier.FREE)
        deals = bot.load_preloaded_deals()
        deals.clear()
        assert len(bot.load_preloaded_deals()) == 50
