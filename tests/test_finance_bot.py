"""
Tests for bots/finance_bot/tiers.py and bots/finance_bot/finance_bot.py
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
AI_MODELS_DIR = os.path.join(REPO_ROOT, 'bots', 'ai-models-integration')
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, os.path.join(AI_MODELS_DIR, 'models'))
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from bots.finance_bot.tiers import (
    get_finance_tier_info,
    FINANCE_EXTRA_FEATURES,
    FINANCE_TOOLS,
)
from bots.finance_bot.finance_bot import (
    FinanceBot,
    FinanceTierError,
    FinanceRequestLimitError,
)


class TestFinanceTierInfo:
    def test_tier_info_keys(self):
        info = get_finance_tier_info(Tier.FREE)
        for key in ("tier", "name", "price_usd_monthly", "requests_per_month",
                    "platform_features", "finance_features", "tools", "support_level"):
            assert key in info

    def test_free_price_is_zero(self):
        assert get_finance_tier_info(Tier.FREE)["price_usd_monthly"] == 0.0

    def test_enterprise_unlimited(self):
        assert get_finance_tier_info(Tier.ENTERPRISE)["requests_per_month"] is None

    def test_pro_has_more_tools_than_free(self):
        free = get_finance_tier_info(Tier.FREE)
        pro = get_finance_tier_info(Tier.PRO)
        assert len(pro["tools"]) > len(free["tools"])

    def test_free_tools_subset_of_pro(self):
        free_tools = set(FINANCE_TOOLS[Tier.FREE.value])
        pro_tools = set(FINANCE_TOOLS[Tier.PRO.value])
        assert free_tools.issubset(pro_tools)

    def test_features_populated_for_all_tiers(self):
        for tier in Tier:
            feats = FINANCE_EXTRA_FEATURES[tier.value]
            assert isinstance(feats, list) and len(feats) > 0

    def test_free_has_budget_tracker(self):
        assert "budget_tracker" in FINANCE_TOOLS[Tier.FREE.value]

    def test_pro_has_portfolio_analyzer(self):
        assert "portfolio_analyzer" in FINANCE_TOOLS[Tier.PRO.value]

    def test_enterprise_has_erp_sync(self):
        assert "erp_sync" in FINANCE_TOOLS[Tier.ENTERPRISE.value]


class TestFinanceBot:
    def test_default_tier_is_free(self):
        bot = FinanceBot()
        assert bot.tier == Tier.FREE

    def test_chat_returns_dict(self):
        bot = FinanceBot(tier=Tier.FREE)
        result = bot.chat("Track my expenses")
        assert isinstance(result, dict)

    def test_chat_result_keys(self):
        bot = FinanceBot(tier=Tier.FREE)
        result = bot.chat("Track my expenses")
        for key in ("message", "tool", "tier", "requests_used", "requests_remaining"):
            assert key in result

    def test_free_cannot_use_pro_tool(self):
        bot = FinanceBot(tier=Tier.FREE)
        with pytest.raises(FinanceTierError):
            bot.chat("Analyze my portfolio", tool="portfolio_analyzer")

    def test_pro_can_use_portfolio_analyzer(self):
        bot = FinanceBot(tier=Tier.PRO)
        result = bot.chat("Analyze portfolio", tool="portfolio_analyzer")
        assert result["tool"] == "portfolio_analyzer"

    def test_enterprise_can_use_erp_sync(self):
        bot = FinanceBot(tier=Tier.ENTERPRISE)
        result = bot.chat("Sync ERP", tool="erp_sync")
        assert result["tool"] == "erp_sync"

    def test_analyze_returns_dict(self):
        bot = FinanceBot(tier=Tier.PRO)
        result = bot.analyze("tax_estimator", {"income": 80000})
        assert result["status"] == "completed"
        assert result["tool"] == "tax_estimator"

    def test_analyze_tier_error_on_free(self):
        bot = FinanceBot(tier=Tier.FREE)
        with pytest.raises(FinanceTierError):
            bot.analyze("portfolio_analyzer")

    def test_list_tools_returns_list(self):
        bot = FinanceBot(tier=Tier.FREE)
        tools = bot.list_tools()
        assert isinstance(tools, list) and len(tools) > 0

    def test_request_limit_raises(self):
        bot = FinanceBot(tier=Tier.FREE)
        bot._request_count = bot.config.requests_per_month
        with pytest.raises(FinanceRequestLimitError):
            bot.chat("another request")

    def test_enterprise_no_request_limit(self):
        bot = FinanceBot(tier=Tier.ENTERPRISE)
        bot._request_count = 10_000_000
        result = bot.chat("unlimited")
        assert result["requests_remaining"] is None

    def test_get_history_grows_with_chat(self):
        bot = FinanceBot()
        bot.chat("Question 1")
        bot.chat("Question 2")
        assert len(bot.get_history()) == 4

    def test_clear_history(self):
        bot = FinanceBot()
        bot.chat("Question")
        bot.clear_history()
        assert bot.get_history() == []

    def test_describe_tier_contains_finance(self):
        bot = FinanceBot(tier=Tier.FREE)
        desc = bot.describe_tier()
        assert "Finance" in desc

    def test_show_upgrade_path_free_mentions_pro(self):
        bot = FinanceBot(tier=Tier.FREE)
        msg = bot.show_upgrade_path()
        assert "Pro" in msg or "Upgrade" in msg

    def test_show_upgrade_path_enterprise(self):
        bot = FinanceBot(tier=Tier.ENTERPRISE)
        msg = bot.show_upgrade_path()
        assert "highest tier" in msg

    def test_default_tool_budget_keyword(self):
        bot = FinanceBot(tier=Tier.FREE)
        result = bot.chat("Help me budget my monthly expenses")
        assert result["tool"] == "budget_tracker"

    def test_default_tool_savings_keyword(self):
        bot = FinanceBot(tier=Tier.FREE)
        result = bot.chat("I want to improve my savings rate")
        assert result["tool"] == "savings_planner"

    def test_request_count_increments(self):
        bot = FinanceBot(tier=Tier.FREE)
        bot.chat("q1")
        bot.chat("q2")
        assert bot._request_count == 2
