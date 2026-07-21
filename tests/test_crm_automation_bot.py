"""
Tests for bots/crm_automation_bot/tiers.py and bots/crm_automation_bot/bot.py
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
AI_MODELS_DIR = os.path.join(REPO_ROOT, 'bots', 'ai-models-integration')
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from bots.crm_automation_bot.tiers import CRM_AUTOMATION_FEATURES, get_crm_automation_tier_info
from bots.crm_automation_bot.bot import (
    CRMAutomationBot,
    CRMAutomationBotTierError,
    CRMAutomationBotRequestLimitError,
)


class TestCRMAutomationTierInfo:
    def test_free_tier_info_keys(self):
        info = get_crm_automation_tier_info(Tier.FREE)
        for key in ("tier", "name", "price_usd_monthly", "requests_per_month",
                    "support_level", "bot_features"):
            assert key in info

    def test_free_price_is_zero(self):
        info = get_crm_automation_tier_info(Tier.FREE)
        assert info["price_usd_monthly"] == 0.0

    def test_enterprise_unlimited(self):
        info = get_crm_automation_tier_info(Tier.ENTERPRISE)
        assert info["requests_per_month"] is None

    def test_features_exist_for_all_tiers(self):
        for tier in Tier:
            assert tier.value in CRM_AUTOMATION_FEATURES
            assert len(CRM_AUTOMATION_FEATURES[tier.value]) > 0


class TestCRMAutomationBot:
    def test_default_tier_is_free(self):
        bot = CRMAutomationBot()
        assert bot.tier == Tier.FREE

    def test_add_contact_returns_expected_keys(self):
        bot = CRMAutomationBot(tier=Tier.FREE)
        result = bot.add_contact({"name": "Alice", "email": "alice@example.com"})
        for key in ("contact_id", "name", "email", "pipeline_stage", "tier"):
            assert key in result

    def test_add_contact_tier_value(self):
        bot = CRMAutomationBot(tier=Tier.FREE)
        result = bot.add_contact({"name": "Bob", "email": "bob@example.com"})
        assert result["tier"] == "free"

    def test_add_contact_with_company(self):
        bot = CRMAutomationBot(tier=Tier.PRO)
        result = bot.add_contact({"name": "Carol", "email": "carol@corp.com", "company": "Corp Inc"})
        assert "contact_id" in result

    def test_contact_limit_free_tier(self):
        bot = CRMAutomationBot(tier=Tier.FREE)
        # Manually set contact count to limit
        bot._contact_count = 100
        with pytest.raises(CRMAutomationBotTierError):
            bot.add_contact({"name": "Extra", "email": "extra@example.com"})

    def test_update_pipeline_returns_dict(self):
        bot = CRMAutomationBot(tier=Tier.FREE)
        result = bot.add_contact({"name": "Dave", "email": "dave@example.com"})
        contact_id = result["contact_id"]
        update_result = bot.update_pipeline(contact_id, "prospect")
        assert "contact_id" in update_result
        assert "new_stage" in update_result or "pipeline_stage" in update_result

    def test_get_pipeline_stats_returns_dict(self):
        bot = CRMAutomationBot(tier=Tier.FREE)
        stats = bot.get_pipeline_stats()
        assert isinstance(stats, dict)
        assert "tier" in stats

    def test_request_counter_increments(self):
        bot = CRMAutomationBot(tier=Tier.FREE)
        bot.add_contact({"name": "Contact1", "email": "c1@example.com"})
        bot.add_contact({"name": "Contact2", "email": "c2@example.com"})
        assert bot._request_count == 2

    def test_request_limit_exceeded(self):
        bot = CRMAutomationBot(tier=Tier.FREE)
        bot._request_count = bot.config.requests_per_month
        with pytest.raises(CRMAutomationBotRequestLimitError):
            bot.add_contact({"name": "Over", "email": "over@example.com"})

    def test_enterprise_no_request_limit(self):
        bot = CRMAutomationBot(tier=Tier.ENTERPRISE)
        bot._request_count = 9999
        result = bot.add_contact({"name": "Enterprise", "email": "ent@corp.com"})
        assert "contact_id" in result

    def test_get_stats_buddy_integration(self):
        bot = CRMAutomationBot(tier=Tier.FREE)
        stats = bot.get_stats()
        assert stats["buddy_integration"] is True

    def test_get_stats_keys(self):
        bot = CRMAutomationBot(tier=Tier.PRO)
        stats = bot.get_stats()
        assert "tier" in stats
        assert "requests_used" in stats
