"""
Tests for bots/lawsuit_finder_bot/tiers.py and
bots/lawsuit_finder_bot/lawsuit_finder_bot.py
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
from bots.lawsuit_finder_bot.tiers import (
    get_lf_tier_info,
    LF_EXTRA_FEATURES,
    LF_TOOLS,
)
from bots.lawsuit_finder_bot.lawsuit_finder_bot import (
    LawsuitFinderBot,
    LawsuitFinderTierError,
    LawsuitFinderRequestLimitError,
)


class TestLFTierInfo:
    def test_tier_info_keys(self):
        info = get_lf_tier_info(Tier.FREE)
        for key in ("tier", "name", "price_usd_monthly", "requests_per_month",
                    "platform_features", "lf_features", "tools", "support_level"):
            assert key in info

    def test_free_price_is_zero(self):
        assert get_lf_tier_info(Tier.FREE)["price_usd_monthly"] == 0.0

    def test_enterprise_unlimited(self):
        assert get_lf_tier_info(Tier.ENTERPRISE)["requests_per_month"] is None

    def test_pro_has_more_tools_than_free(self):
        free = get_lf_tier_info(Tier.FREE)
        pro = get_lf_tier_info(Tier.PRO)
        assert len(pro["tools"]) > len(free["tools"])

    def test_free_tools_subset_of_pro(self):
        free_tools = set(LF_TOOLS[Tier.FREE.value])
        pro_tools = set(LF_TOOLS[Tier.PRO.value])
        assert free_tools.issubset(pro_tools)

    def test_features_populated(self):
        for tier in Tier:
            assert len(LF_EXTRA_FEATURES[tier.value]) > 0

    def test_free_has_case_search(self):
        assert "case_search" in LF_TOOLS[Tier.FREE.value]

    def test_pro_has_class_action_finder(self):
        assert "class_action_finder" in LF_TOOLS[Tier.PRO.value]

    def test_enterprise_has_litigation_analytics(self):
        assert "litigation_analytics" in LF_TOOLS[Tier.ENTERPRISE.value]


class TestLawsuitFinderBot:
    def test_default_tier_is_free(self):
        bot = LawsuitFinderBot()
        assert bot.tier == Tier.FREE

    def test_chat_returns_dict(self):
        bot = LawsuitFinderBot(tier=Tier.FREE)
        result = bot.chat("Search for breach of contract cases")
        assert isinstance(result, dict)

    def test_chat_result_keys(self):
        bot = LawsuitFinderBot(tier=Tier.FREE)
        result = bot.chat("Find cases")
        for key in ("message", "tool", "tier", "disclaimer",
                    "requests_used", "requests_remaining"):
            assert key in result

    def test_disclaimer_present_in_response(self):
        bot = LawsuitFinderBot(tier=Tier.FREE)
        result = bot.chat("Find lawsuits")
        assert "DISCLAIMER" in result["disclaimer"]

    def test_free_cannot_use_class_action_finder(self):
        bot = LawsuitFinderBot(tier=Tier.FREE)
        with pytest.raises(LawsuitFinderTierError):
            bot.chat("Find class actions", tool="class_action_finder")

    def test_pro_can_use_class_action_finder(self):
        bot = LawsuitFinderBot(tier=Tier.PRO)
        result = bot.chat("Find class actions", tool="class_action_finder")
        assert result["tool"] == "class_action_finder"

    def test_enterprise_can_use_litigation_analytics(self):
        bot = LawsuitFinderBot(tier=Tier.ENTERPRISE)
        result = bot.chat("Litigation trends", tool="litigation_analytics")
        assert result["tool"] == "litigation_analytics"

    def test_search_cases_returns_dict(self):
        bot = LawsuitFinderBot(tier=Tier.FREE)
        result = bot.search_cases("breach of contract", jurisdiction="CA")
        assert result["status"] == "success"
        assert "disclaimer" in result

    def test_find_class_actions_pro(self):
        bot = LawsuitFinderBot(tier=Tier.PRO)
        result = bot.find_class_actions("pharmaceutical")
        assert result["industry"] == "pharmaceutical"
        assert "disclaimer" in result

    def test_find_class_actions_tier_error_on_free(self):
        bot = LawsuitFinderBot(tier=Tier.FREE)
        with pytest.raises(LawsuitFinderTierError):
            bot.find_class_actions("tech")

    def test_list_tools_returns_list(self):
        bot = LawsuitFinderBot(tier=Tier.FREE)
        tools = bot.list_tools()
        assert isinstance(tools, list) and len(tools) > 0

    def test_request_limit_raises(self):
        bot = LawsuitFinderBot(tier=Tier.FREE)
        bot._request_count = bot.config.requests_per_month
        with pytest.raises(LawsuitFinderRequestLimitError):
            bot.chat("another search")

    def test_enterprise_no_request_limit(self):
        bot = LawsuitFinderBot(tier=Tier.ENTERPRISE)
        bot._request_count = 10_000_000
        result = bot.chat("search")
        assert result["requests_remaining"] is None

    def test_history_grows(self):
        bot = LawsuitFinderBot()
        bot.chat("search 1")
        bot.chat("search 2")
        assert len(bot.get_history()) == 4

    def test_clear_history(self):
        bot = LawsuitFinderBot()
        bot.chat("search")
        bot.clear_history()
        assert bot.get_history() == []

    def test_describe_tier_contains_lawsuit(self):
        bot = LawsuitFinderBot(tier=Tier.FREE)
        desc = bot.describe_tier()
        assert "Lawsuit" in desc

    def test_describe_tier_contains_disclaimer(self):
        bot = LawsuitFinderBot(tier=Tier.FREE)
        desc = bot.describe_tier()
        assert "DISCLAIMER" in desc

    def test_show_upgrade_path_free(self):
        bot = LawsuitFinderBot(tier=Tier.FREE)
        msg = bot.show_upgrade_path()
        assert "Pro" in msg or "Upgrade" in msg

    def test_show_upgrade_path_enterprise(self):
        bot = LawsuitFinderBot(tier=Tier.ENTERPRISE)
        msg = bot.show_upgrade_path()
        assert "highest tier" in msg

    def test_default_tool_class_action_keyword(self):
        bot = LawsuitFinderBot(tier=Tier.PRO)
        result = bot.chat("Find class action lawsuits")
        assert result["tool"] == "class_action_finder"

    def test_default_tool_statute_keyword(self):
        bot = LawsuitFinderBot(tier=Tier.FREE)
        result = bot.chat("Look up the statute for negligence")
        assert result["tool"] == "statute_lookup"
