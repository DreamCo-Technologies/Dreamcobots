"""Tests for bots/money_finder_bot/tiers.py and bots/money_finder_bot/money_finder_bot.py"""
import sys, os

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
AI_MODELS_DIR = os.path.join(REPO_ROOT, 'bots', 'ai-models-integration')
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, os.path.join(AI_MODELS_DIR, 'models'))
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from bots.money_finder_bot.money_finder_bot import MoneyFinderBot, MoneyFinderBotTierError


class TestMoneyFinderBotInstantiation:
    def test_default_tier_is_free(self):
        bot = MoneyFinderBot()
        assert bot.tier == Tier.FREE

    def test_pro_tier(self):
        bot = MoneyFinderBot(tier=Tier.PRO)
        assert bot.tier == Tier.PRO

    def test_enterprise_tier(self):
        bot = MoneyFinderBot(tier=Tier.ENTERPRISE)
        assert bot.tier == Tier.ENTERPRISE

    def test_config_loaded(self):
        bot = MoneyFinderBot()
        assert bot.config is not None


class TestScanUnclaimedFunds:
    def test_returns_list(self):
        bot = MoneyFinderBot(tier=Tier.FREE)
        result = bot.scan_unclaimed_funds("John Smith", "CA")
        assert isinstance(result, list)

    def test_results_have_required_keys(self):
        bot = MoneyFinderBot(tier=Tier.FREE)
        result = bot.scan_unclaimed_funds("Jane Doe", "NY")
        assert len(result) > 0
        for record in result:
            assert "source" in record
            assert "amount_usd" in record

    def test_free_limited_to_1_state(self):
        bot = MoneyFinderBot(tier=Tier.FREE)
        bot.scan_unclaimed_funds("John Smith", "CA")
        with pytest.raises(MoneyFinderBotTierError):
            bot.scan_unclaimed_funds("John Smith", "TX")

    def test_pro_allows_multiple_states(self):
        bot = MoneyFinderBot(tier=Tier.PRO)
        for state in ["CA", "TX", "NY", "FL", "WA"]:
            result = bot.scan_unclaimed_funds("John Smith", state)
            assert isinstance(result, list)

    def test_pro_returns_more_results_than_free(self):
        free_bot = MoneyFinderBot(tier=Tier.FREE)
        pro_bot = MoneyFinderBot(tier=Tier.PRO)
        free_result = free_bot.scan_unclaimed_funds("John Smith", "CA")
        pro_result = pro_bot.scan_unclaimed_funds("John Smith", "CA")
        assert len(pro_result) >= len(free_result)

    def test_enterprise_returns_most_results(self):
        bot = MoneyFinderBot(tier=Tier.ENTERPRISE)
        result = bot.scan_unclaimed_funds("John Smith", "CA")
        assert len(result) >= 5


class TestCheckGovernmentBenefits:
    def test_pro_returns_list(self):
        bot = MoneyFinderBot(tier=Tier.PRO)
        profile = {"annual_income_usd": 25000, "household_size": 3}
        result = bot.check_government_benefits(profile)
        assert isinstance(result, list)

    def test_free_raises(self):
        bot = MoneyFinderBot(tier=Tier.FREE)
        with pytest.raises(MoneyFinderBotTierError):
            bot.check_government_benefits({"annual_income_usd": 25000})

    def test_low_income_gets_more_benefits(self):
        bot = MoneyFinderBot(tier=Tier.PRO)
        low = bot.check_government_benefits({"annual_income_usd": 15000, "household_size": 2})
        high = bot.check_government_benefits({"annual_income_usd": 100000, "household_size": 2})
        assert len(low) >= len(high)


class TestFindCashbackOpportunities:
    def test_returns_list(self):
        bot = MoneyFinderBot(tier=Tier.FREE)
        result = bot.find_cashback_opportunities()
        assert isinstance(result, list)
        assert len(result) > 0

    def test_pro_returns_more_than_free(self):
        free_bot = MoneyFinderBot(tier=Tier.FREE)
        pro_bot = MoneyFinderBot(tier=Tier.PRO)
        assert len(pro_bot.find_cashback_opportunities()) > len(free_bot.find_cashback_opportunities())

    def test_records_have_source_and_category(self):
        bot = MoneyFinderBot(tier=Tier.PRO)
        result = bot.find_cashback_opportunities()
        for item in result:
            assert "source" in item
            assert "category" in item


class TestGenerateRecoveryReport:
    def test_returns_dict(self):
        bot = MoneyFinderBot(tier=Tier.FREE)
        result = bot.generate_recovery_report("John Smith")
        assert isinstance(result, dict)

    def test_has_required_keys(self):
        bot = MoneyFinderBot(tier=Tier.FREE)
        result = bot.generate_recovery_report("John Smith")
        for key in ("unclaimed_funds_count", "total_unclaimed_usd", "total_recovery_potential_usd"):
            assert key in result

    def test_enterprise_has_international_search(self):
        bot = MoneyFinderBot(tier=Tier.ENTERPRISE)
        result = bot.generate_recovery_report("John Smith")
        assert "international_search" in result
        assert result["international_search"]["available"] is True
