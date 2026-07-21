"""
Tests for bots/business_automation/tiers.py and
bots/business_automation/business_automation_bot.py
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
from bots.business_automation.tiers import (
    get_ba_tier_info,
    BA_EXTRA_FEATURES,
    BA_WORKFLOWS,
)
from bots.business_automation.business_automation_bot import (
    BusinessAutomationBot,
    BusinessAutomationTierError,
    BusinessAutomationRequestLimitError,
)


class TestBATierInfo:
    def test_tier_info_keys(self):
        info = get_ba_tier_info(Tier.FREE)
        for key in ("tier", "name", "price_usd_monthly", "requests_per_month",
                    "platform_features", "ba_features", "workflows", "support_level"):
            assert key in info

    def test_free_price_is_zero(self):
        assert get_ba_tier_info(Tier.FREE)["price_usd_monthly"] == 0.0

    def test_pro_price(self):
        assert get_ba_tier_info(Tier.PRO)["price_usd_monthly"] == 49.0

    def test_enterprise_unlimited(self):
        assert get_ba_tier_info(Tier.ENTERPRISE)["requests_per_month"] is None

    def test_pro_has_more_workflows_than_free(self):
        free = get_ba_tier_info(Tier.FREE)
        pro = get_ba_tier_info(Tier.PRO)
        assert len(pro["workflows"]) > len(free["workflows"])

    def test_enterprise_has_more_workflows_than_pro(self):
        pro = get_ba_tier_info(Tier.PRO)
        ent = get_ba_tier_info(Tier.ENTERPRISE)
        assert len(ent["workflows"]) > len(pro["workflows"])

    def test_free_workflows_subset_of_pro(self):
        free_wf = set(BA_WORKFLOWS[Tier.FREE.value])
        pro_wf = set(BA_WORKFLOWS[Tier.PRO.value])
        assert free_wf.issubset(pro_wf)

    def test_features_populated_for_all_tiers(self):
        for tier in Tier:
            feats = BA_EXTRA_FEATURES[tier.value]
            assert isinstance(feats, list) and len(feats) > 0

    def test_free_has_meeting_scheduler(self):
        assert "meeting_scheduler" in BA_WORKFLOWS[Tier.FREE.value]

    def test_pro_has_invoice_generator(self):
        assert "invoice_generator" in BA_WORKFLOWS[Tier.PRO.value]

    def test_enterprise_has_erp_integration(self):
        assert "erp_integration" in BA_WORKFLOWS[Tier.ENTERPRISE.value]


class TestBusinessAutomationBot:
    def test_default_tier_is_free(self):
        bot = BusinessAutomationBot()
        assert bot.tier == Tier.FREE

    def test_chat_returns_dict(self):
        bot = BusinessAutomationBot(tier=Tier.FREE)
        result = bot.chat("Schedule a meeting")
        assert isinstance(result, dict)

    def test_chat_result_keys(self):
        bot = BusinessAutomationBot(tier=Tier.FREE)
        result = bot.chat("Schedule a meeting")
        for key in ("message", "workflow", "tier", "requests_used", "requests_remaining"):
            assert key in result

    def test_chat_increments_request_count(self):
        bot = BusinessAutomationBot(tier=Tier.FREE)
        bot.chat("Task one")
        bot.chat("Task two")
        assert bot._request_count == 2

    def test_chat_tier_in_response(self):
        bot = BusinessAutomationBot(tier=Tier.PRO)
        result = bot.chat("Generate invoice")
        assert result["tier"] == "pro"

    def test_free_tier_cannot_use_pro_workflow(self):
        bot = BusinessAutomationBot(tier=Tier.FREE)
        with pytest.raises(BusinessAutomationTierError):
            bot.chat("Generate invoice", workflow="invoice_generator")

    def test_pro_tier_can_use_invoice_workflow(self):
        bot = BusinessAutomationBot(tier=Tier.PRO)
        result = bot.chat("Generate invoice", workflow="invoice_generator")
        assert result["workflow"] == "invoice_generator"

    def test_enterprise_tier_can_use_erp_workflow(self):
        bot = BusinessAutomationBot(tier=Tier.ENTERPRISE)
        result = bot.chat("ERP sync", workflow="erp_integration")
        assert result["workflow"] == "erp_integration"

    def test_run_workflow_returns_dict(self):
        bot = BusinessAutomationBot(tier=Tier.PRO)
        result = bot.run_workflow("invoice_generator", {"amount": 1000})
        assert result["status"] == "completed"
        assert result["workflow"] == "invoice_generator"

    def test_run_workflow_tier_error_on_free(self):
        bot = BusinessAutomationBot(tier=Tier.FREE)
        with pytest.raises(BusinessAutomationTierError):
            bot.run_workflow("invoice_generator")

    def test_list_workflows_returns_list(self):
        bot = BusinessAutomationBot(tier=Tier.FREE)
        assert isinstance(bot.list_workflows(), list)
        assert len(bot.list_workflows()) > 0

    def test_list_workflows_pro_contains_crm(self):
        bot = BusinessAutomationBot(tier=Tier.PRO)
        assert "crm_sync" in bot.list_workflows()

    def test_request_limit_raises(self):
        bot = BusinessAutomationBot(tier=Tier.FREE)
        bot._request_count = bot.config.requests_per_month
        with pytest.raises(BusinessAutomationRequestLimitError):
            bot.chat("one more request")

    def test_enterprise_no_request_limit(self):
        bot = BusinessAutomationBot(tier=Tier.ENTERPRISE)
        bot._request_count = 10_000_000
        result = bot.chat("unlimited request")
        assert result["requests_remaining"] is None

    def test_get_history_initially_empty(self):
        bot = BusinessAutomationBot()
        assert bot.get_history() == []

    def test_get_history_after_chat(self):
        bot = BusinessAutomationBot()
        bot.chat("Schedule meeting")
        assert len(bot.get_history()) == 2

    def test_clear_history(self):
        bot = BusinessAutomationBot()
        bot.chat("Schedule meeting")
        bot.clear_history()
        assert bot.get_history() == []

    def test_describe_tier_returns_string(self):
        bot = BusinessAutomationBot(tier=Tier.FREE)
        desc = bot.describe_tier()
        assert isinstance(desc, str)
        assert "Business Automation" in desc

    def test_show_upgrade_path_free(self):
        bot = BusinessAutomationBot(tier=Tier.FREE)
        msg = bot.show_upgrade_path()
        assert "Pro" in msg or "Upgrade" in msg

    def test_show_upgrade_path_enterprise(self):
        bot = BusinessAutomationBot(tier=Tier.ENTERPRISE)
        msg = bot.show_upgrade_path()
        assert "highest tier" in msg

    def test_requests_remaining_decreases(self):
        bot = BusinessAutomationBot(tier=Tier.FREE)
        before = bot._requests_remaining()
        bot.chat("Task")
        after = bot._requests_remaining()
        assert after == before - 1

    def test_default_workflow_scheduling(self):
        bot = BusinessAutomationBot(tier=Tier.FREE)
        result = bot.chat("Please schedule a meeting for tomorrow")
        assert result["workflow"] == "meeting_scheduler"

    def test_default_workflow_email(self):
        bot = BusinessAutomationBot(tier=Tier.FREE)
        result = bot.chat("Draft an email to my team")
        assert result["workflow"] == "email_drafter"
