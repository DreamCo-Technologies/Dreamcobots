"""
Tests for bots/lead_generation_bot/tiers.py and bots/lead_generation_bot/bot.py
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
AI_MODELS_DIR = os.path.join(REPO_ROOT, 'bots', 'ai-models-integration')
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from bots.lead_generation_bot.tiers import LEAD_GENERATION_FEATURES, get_lead_generation_tier_info
from bots.lead_generation_bot.bot import (
    LeadGenerationBot,
    LeadGenerationBotTierError,
    LeadGenerationBotRequestLimitError,
)


class TestLeadGenerationTierInfo:
    def test_free_tier_info_keys(self):
        info = get_lead_generation_tier_info(Tier.FREE)
        for key in ("tier", "name", "price_usd_monthly", "requests_per_month",
                    "support_level", "bot_features"):
            assert key in info

    def test_free_price_is_zero(self):
        info = get_lead_generation_tier_info(Tier.FREE)
        assert info["price_usd_monthly"] == 0.0

    def test_pro_price(self):
        info = get_lead_generation_tier_info(Tier.PRO)
        assert info["price_usd_monthly"] == 49.0

    def test_enterprise_unlimited(self):
        info = get_lead_generation_tier_info(Tier.ENTERPRISE)
        assert info["requests_per_month"] is None

    def test_features_exist_for_all_tiers(self):
        for tier in Tier:
            assert tier.value in LEAD_GENERATION_FEATURES
            assert len(LEAD_GENERATION_FEATURES[tier.value]) > 0


class TestLeadGenerationBot:
    def test_default_tier_is_free(self):
        bot = LeadGenerationBot()
        assert bot.tier == Tier.FREE

    def test_capture_lead_returns_expected_keys(self):
        bot = LeadGenerationBot(tier=Tier.FREE)
        result = bot.capture_lead({"name": "Alice", "email": "alice@example.com"})
        for key in ("lead_id", "name", "email", "score", "tier"):
            assert key in result

    def test_capture_lead_tier_value(self):
        bot = LeadGenerationBot(tier=Tier.FREE)
        result = bot.capture_lead({"name": "Bob", "email": "bob@example.com"})
        assert result["tier"] == "free"

    def test_capture_lead_score_is_float(self):
        bot = LeadGenerationBot(tier=Tier.FREE)
        result = bot.capture_lead({"name": "Carol", "email": "carol@example.com"})
        assert isinstance(result["score"], float)
        assert 0.0 <= result["score"] <= 1.0

    def test_capture_lead_stores_lead(self):
        bot = LeadGenerationBot(tier=Tier.PRO)
        result = bot.capture_lead({"name": "Dave", "email": "dave@example.com"})
        assert result["lead_id"] is not None

    def test_score_lead_free_tier_raises(self):
        bot = LeadGenerationBot(tier=Tier.FREE)
        with pytest.raises(LeadGenerationBotTierError):
            bot.score_lead("some-lead-id")

    def test_score_lead_pro_tier(self):
        bot = LeadGenerationBot(tier=Tier.PRO)
        result = bot.capture_lead({"name": "Eve", "email": "eve@company.com"})
        lead_id = result["lead_id"]
        score_result = bot.score_lead(lead_id)
        assert "lead_id" in score_result
        assert "score" in score_result

    def test_export_leads_free_only_csv(self):
        bot = LeadGenerationBot(tier=Tier.FREE)
        result = bot.export_leads("csv")
        assert "format" in result
        assert result["format"] == "csv"

    def test_export_leads_free_json_raises(self):
        bot = LeadGenerationBot(tier=Tier.FREE)
        with pytest.raises(LeadGenerationBotTierError):
            bot.export_leads("json")

    def test_request_counter_increments(self):
        bot = LeadGenerationBot(tier=Tier.FREE)
        bot.capture_lead({"name": "Lead1", "email": "l1@example.com"})
        bot.capture_lead({"name": "Lead2", "email": "l2@example.com"})
        assert bot._request_count == 2

    def test_request_limit_exceeded(self):
        bot = LeadGenerationBot(tier=Tier.FREE)
        bot._request_count = bot.config.requests_per_month
        with pytest.raises(LeadGenerationBotRequestLimitError):
            bot.capture_lead({"name": "Over", "email": "over@example.com"})

    def test_enterprise_no_request_limit(self):
        bot = LeadGenerationBot(tier=Tier.ENTERPRISE)
        bot._request_count = 9999
        result = bot.capture_lead({"name": "Enterprise Lead", "email": "ent@company.com"})
        assert "lead_id" in result

    def test_get_stats_buddy_integration(self):
        bot = LeadGenerationBot(tier=Tier.FREE)
        stats = bot.get_stats()
        assert stats["buddy_integration"] is True

    def test_get_stats_keys(self):
        bot = LeadGenerationBot(tier=Tier.PRO)
        stats = bot.get_stats()
        assert "tier" in stats
        assert "requests_used" in stats
        assert "requests_remaining" in stats
