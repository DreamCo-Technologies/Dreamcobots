"""Tests for bots/email_campaign_manager_bot"""
import sys, os

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
AI_MODELS_DIR = os.path.join(REPO_ROOT, 'bots', 'ai-models-integration')
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, os.path.join(AI_MODELS_DIR, 'models'))
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from bots.email_campaign_manager_bot.email_campaign_manager_bot import EmailCampaignManagerBot
from bots.email_campaign_manager_bot.tiers import BOT_FEATURES, get_bot_tier_info


class TestEmailCampaignManagerBotInstantiation:
    def test_default_tier_is_free(self):
        bot = EmailCampaignManagerBot()
        assert bot.tier == Tier.FREE

    def test_pro_tier(self):
        bot = EmailCampaignManagerBot(tier=Tier.PRO)
        assert bot.tier == Tier.PRO

    def test_enterprise_tier(self):
        bot = EmailCampaignManagerBot(tier=Tier.ENTERPRISE)
        assert bot.tier == Tier.ENTERPRISE


class TestAddSubscriber:
    def test_add_subscriber_returns_dict(self):
        bot = EmailCampaignManagerBot()
        sub = bot.add_subscriber("user@test.com", "Alice")
        assert isinstance(sub, dict)
        assert sub["email"] == "user@test.com"

    def test_subscriber_has_required_fields(self):
        bot = EmailCampaignManagerBot()
        sub = bot.add_subscriber("x@test.com", "Bob", segment="vip")
        assert sub["segment"] == "vip"
        assert sub["status"] == "active"

    def test_free_tier_subscriber_limit(self):
        bot = EmailCampaignManagerBot()
        bot._subscribers = [{"email": f"u{i}@test.com"} for i in range(500)]
        with pytest.raises(PermissionError):
            bot.add_subscriber("extra@test.com", "Extra")

    def test_enterprise_no_subscriber_limit(self):
        bot = EmailCampaignManagerBot(tier=Tier.ENTERPRISE)
        bot._subscribers = [{"email": f"u{i}@test.com"} for i in range(10000)]
        sub = bot.add_subscriber("more@test.com", "More")
        assert sub["email"] == "more@test.com"


class TestCreateCampaign:
    def test_create_campaign_returns_dict(self):
        bot = EmailCampaignManagerBot()
        camp = bot.create_campaign("Summer Sale", "Big Deals!", "general")
        assert isinstance(camp, dict)
        assert "campaign_id" in camp

    def test_campaign_has_required_fields(self):
        bot = EmailCampaignManagerBot()
        camp = bot.create_campaign("Newsletter", "Monthly Update", "subscribers", goal="awareness")
        assert camp["goal"] == "awareness"
        assert camp["status"] == "draft"

    def test_free_tier_campaign_limit(self):
        bot = EmailCampaignManagerBot()
        bot.create_campaign("C1", "S1", "all")
        bot.create_campaign("C2", "S2", "all")
        with pytest.raises(PermissionError):
            bot.create_campaign("C3", "S3", "all")


class TestEmailContent:
    def test_generate_email_content_returns_dict(self):
        bot = EmailCampaignManagerBot()
        camp = {"name": "Summer Sale", "subject": "Big Deals!", "goal": "sales"}
        result = bot.generate_email_content(camp)
        assert "subject" in result
        assert "body_text" in result
        assert "body_html" in result

    def test_email_word_count_positive(self):
        bot = EmailCampaignManagerBot()
        result = bot.generate_email_content({"name": "Test", "subject": "Hello", "goal": "engagement"})
        assert result["word_count"] > 0


class TestCampaignStats:
    def test_get_campaign_stats_returns_dict(self):
        bot = EmailCampaignManagerBot()
        stats = bot.get_campaign_stats("camp_1")
        assert "sent" in stats
        assert "open_rate" in stats
        assert "click_rate" in stats


class TestDripSequence:
    def test_drip_sequence_raises_on_free(self):
        bot = EmailCampaignManagerBot()
        with pytest.raises(PermissionError):
            bot.create_drip_sequence("new_signup")

    def test_drip_sequence_works_on_pro(self):
        bot = EmailCampaignManagerBot(tier=Tier.PRO)
        seq = bot.create_drip_sequence("new_signup", num_emails=3)
        assert seq["num_emails"] == 3
        assert len(seq["emails"]) == 3

    def test_drip_sequence_works_on_enterprise(self):
        bot = EmailCampaignManagerBot(tier=Tier.ENTERPRISE)
        seq = bot.create_drip_sequence("purchase", num_emails=5)
        assert "sequence_id" in seq


class TestEmailCampaignBotTiers:
    def test_bot_features_has_all_tiers(self):
        assert Tier.FREE.value in BOT_FEATURES
        assert Tier.PRO.value in BOT_FEATURES
        assert Tier.ENTERPRISE.value in BOT_FEATURES

    def test_pro_has_more_features_than_free(self):
        assert len(BOT_FEATURES[Tier.PRO.value]) > len(BOT_FEATURES[Tier.FREE.value])

    def test_tier_config_price(self):
        info = get_bot_tier_info(Tier.FREE)
        assert info["price_usd_monthly"] == 0.0

    def test_run_returns_pipeline_complete(self):
        bot = EmailCampaignManagerBot()
        result = bot.run()
        assert result.get("pipeline_complete") is True
