"""
Tests for bots/saas_bot/

Covers tiers, subscription management, webhook handling, analytics,
and Stripe integration.
"""

import json
import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

from bots.saas_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
    FEATURE_CORE_SAAS,
    FEATURE_STRIPE_SUBSCRIPTIONS,
    FEATURE_SUBSCRIPTION_WEBHOOKS,
    FEATURE_ANNUAL_BILLING,
    FEATURE_TRIAL_PERIOD,
    FEATURE_USAGE_ANALYTICS,
    FEATURE_MULTI_USER,
    FEATURE_WHITE_LABEL,
)
from bots.saas_bot.saas_bot import (
    SaasBot,
    SaasBotError,
    SaasBotTierError,
    Subscription,
)
from bots.stripe_integration.webhook_handler import StripeWebhookHandler


# ===========================================================================
# Tier configuration
# ===========================================================================

class TestSaasBotTiers:
    def test_three_tiers(self):
        assert len(list_tiers()) == 3

    def test_basic_price(self):
        assert get_tier_config(Tier.BASIC).price_usd_monthly == 29.0

    def test_professional_price(self):
        assert get_tier_config(Tier.PROFESSIONAL).price_usd_monthly == 99.0

    def test_enterprise_price(self):
        assert get_tier_config(Tier.ENTERPRISE).price_usd_monthly == 299.0

    def test_basic_max_users(self):
        assert get_tier_config(Tier.BASIC).max_users == 5

    def test_professional_max_users(self):
        assert get_tier_config(Tier.PROFESSIONAL).max_users == 25

    def test_enterprise_unlimited_users(self):
        assert get_tier_config(Tier.ENTERPRISE).is_unlimited_users() is True

    def test_basic_has_core_saas(self):
        assert get_tier_config(Tier.BASIC).has_feature(FEATURE_CORE_SAAS)

    def test_basic_has_stripe_subscriptions(self):
        assert get_tier_config(Tier.BASIC).has_feature(FEATURE_STRIPE_SUBSCRIPTIONS)

    def test_basic_lacks_webhooks(self):
        assert not get_tier_config(Tier.BASIC).has_feature(FEATURE_SUBSCRIPTION_WEBHOOKS)

    def test_professional_has_webhooks(self):
        assert get_tier_config(Tier.PROFESSIONAL).has_feature(FEATURE_SUBSCRIPTION_WEBHOOKS)

    def test_enterprise_has_white_label(self):
        assert get_tier_config(Tier.ENTERPRISE).has_feature(FEATURE_WHITE_LABEL)

    def test_upgrade_basic_to_professional(self):
        upgrade = get_upgrade_path(Tier.BASIC)
        assert upgrade.tier == Tier.PROFESSIONAL

    def test_no_upgrade_from_enterprise(self):
        assert get_upgrade_path(Tier.ENTERPRISE) is None

    def test_stripe_price_ids_defined(self):
        for tier in Tier:
            cfg = get_tier_config(tier)
            assert cfg.stripe_monthly_price_id
            assert cfg.stripe_annual_price_id


# ===========================================================================
# Instantiation
# ===========================================================================

class TestSaasBotInstantiation:
    def test_default_tier_basic(self):
        bot = SaasBot()
        assert bot.tier == Tier.BASIC

    def test_professional_tier(self):
        bot = SaasBot(tier=Tier.PROFESSIONAL)
        assert bot.tier == Tier.PROFESSIONAL

    def test_enterprise_tier(self):
        bot = SaasBot(tier=Tier.ENTERPRISE)
        assert bot.tier == Tier.ENTERPRISE

    def test_config_loaded(self):
        bot = SaasBot()
        assert bot.config is not None

    def test_custom_webhook_handler(self):
        handler = StripeWebhookHandler(verify_signatures=False)
        bot = SaasBot(tier=Tier.PROFESSIONAL, webhook_handler=handler)
        assert bot._webhook_handler is handler


# ===========================================================================
# Subscription management
# ===========================================================================

class TestSubscriptionManagement:
    def test_create_subscription_returns_subscription(self):
        bot = SaasBot(tier=Tier.BASIC)
        sub = bot.create_subscription("customer@test.com")
        assert isinstance(sub, Subscription)

    def test_subscription_has_id(self):
        bot = SaasBot(tier=Tier.BASIC)
        sub = bot.create_subscription("customer@test.com")
        assert sub.subscription_id.startswith("sub_")

    def test_subscription_stores_email(self):
        bot = SaasBot(tier=Tier.BASIC)
        sub = bot.create_subscription("alice@example.com")
        assert sub.customer_email == "alice@example.com"

    def test_subscription_has_stripe_sub_id(self):
        bot = SaasBot(tier=Tier.BASIC)
        sub = bot.create_subscription("b@test.com")
        assert sub.stripe_subscription_id

    def test_subscription_has_stripe_customer_id(self):
        bot = SaasBot(tier=Tier.BASIC)
        sub = bot.create_subscription("c@test.com")
        assert sub.stripe_customer_id.startswith("cus_")

    def test_default_billing_monthly(self):
        bot = SaasBot(tier=Tier.BASIC)
        sub = bot.create_subscription("d@test.com")
        assert sub.billing_interval == "monthly"

    def test_trial_days_applied(self):
        bot = SaasBot(tier=Tier.BASIC)
        sub = bot.create_subscription("e@test.com", trial_days=14)
        assert sub.trial_days == 14
        assert sub.status == "trialing"

    def test_annual_billing_requires_professional(self):
        bot = SaasBot(tier=Tier.BASIC)
        with pytest.raises(SaasBotTierError):
            bot.create_subscription("f@test.com", billing_interval="annual")

    def test_annual_billing_professional(self):
        bot = SaasBot(tier=Tier.PROFESSIONAL)
        sub = bot.create_subscription("g@test.com", billing_interval="annual")
        assert sub.billing_interval == "annual"

    def test_subscription_stored(self):
        bot = SaasBot(tier=Tier.BASIC)
        sub = bot.create_subscription("h@test.com")
        retrieved = bot.get_subscription(sub.subscription_id)
        assert retrieved is sub

    def test_cancel_subscription(self):
        bot = SaasBot(tier=Tier.BASIC)
        sub = bot.create_subscription("i@test.com")
        canceled = bot.cancel_subscription(sub.subscription_id)
        assert canceled.status == "canceled"
        assert canceled.canceled_at is not None

    def test_cancel_unknown_subscription(self):
        bot = SaasBot(tier=Tier.BASIC)
        with pytest.raises(SaasBotError):
            bot.cancel_subscription("sub_nonexistent")

    def test_list_subscriptions(self):
        bot = SaasBot(tier=Tier.BASIC)
        bot.create_subscription("j@test.com")
        bot.create_subscription("k@test.com")
        subs = bot.list_subscriptions()
        assert len(subs) == 2

    def test_list_subscriptions_filter_by_status(self):
        bot = SaasBot(tier=Tier.BASIC)
        sub1 = bot.create_subscription("l@test.com", trial_days=0)
        sub2 = bot.create_subscription("m@test.com", trial_days=0)
        bot.cancel_subscription(sub1.subscription_id)
        active = bot.list_subscriptions(status="active")
        canceled = bot.list_subscriptions(status="canceled")
        assert len(active) == 1
        assert len(canceled) == 1

    def test_upgrade_subscription(self):
        bot = SaasBot(tier=Tier.PROFESSIONAL)
        sub = bot.create_subscription("n@test.com")
        upgraded = bot.upgrade_subscription(sub.subscription_id, Tier.ENTERPRISE)
        assert upgraded.tier == Tier.ENTERPRISE

    def test_upgrade_unknown_subscription(self):
        bot = SaasBot(tier=Tier.PROFESSIONAL)
        with pytest.raises(SaasBotError):
            bot.upgrade_subscription("sub_xxx", Tier.ENTERPRISE)

    def test_get_nonexistent_subscription_returns_none(self):
        bot = SaasBot(tier=Tier.BASIC)
        assert bot.get_subscription("sub_unknown") is None


# ===========================================================================
# Webhook processing
# ===========================================================================

class TestWebhookProcessing:
    def test_process_webhook_requires_professional(self):
        bot = SaasBot(tier=Tier.BASIC)
        with pytest.raises(SaasBotTierError):
            bot.process_webhook(b"{}")

    def test_process_webhook_professional(self):
        bot = SaasBot(tier=Tier.PROFESSIONAL)
        payload = StripeWebhookHandler.build_event_payload(
            "invoice.payment_succeeded", {"subscription": "sub_abc"}
        )
        result = bot.process_webhook(payload)
        assert result["received"] is True
        assert result["event_type"] == "invoice.payment_succeeded"

    def test_webhook_subscription_canceled(self):
        bot = SaasBot(tier=Tier.PROFESSIONAL)
        sub = bot.create_subscription("webhook_test@test.com")
        sub.stripe_subscription_id = "sub_stripe_webhook_test"

        payload = StripeWebhookHandler.build_event_payload(
            "customer.subscription.deleted",
            {"id": "sub_stripe_webhook_test"},
        )
        bot.process_webhook(payload)
        assert bot.get_subscription(sub.subscription_id).status == "canceled"

    def test_webhook_subscription_past_due(self):
        bot = SaasBot(tier=Tier.PROFESSIONAL)
        sub = bot.create_subscription("pastdue@test.com")
        sub.stripe_subscription_id = "sub_past_due_test"

        payload = StripeWebhookHandler.build_event_payload(
            "invoice.payment_failed",
            {"subscription": "sub_past_due_test"},
        )
        bot.process_webhook(payload)
        assert bot.get_subscription(sub.subscription_id).status == "past_due"

    def test_register_custom_webhook_handler(self):
        bot = SaasBot(tier=Tier.PROFESSIONAL)
        received = []
        bot.register_webhook_handler("charge.refunded", lambda e: received.append(e))
        payload = StripeWebhookHandler.build_event_payload("charge.refunded", {})
        bot.process_webhook(payload)
        assert len(received) == 1

    def test_register_webhook_requires_professional(self):
        bot = SaasBot(tier=Tier.BASIC)
        with pytest.raises(SaasBotTierError):
            bot.register_webhook_handler("charge.refunded", lambda e: None)


# ===========================================================================
# Usage analytics
# ===========================================================================

class TestUsageAnalytics:
    def test_analytics_requires_professional(self):
        bot = SaasBot(tier=Tier.BASIC)
        with pytest.raises(SaasBotTierError):
            bot.get_subscription_analytics()

    def test_analytics_professional(self):
        bot = SaasBot(tier=Tier.PROFESSIONAL)
        bot.create_subscription("a@test.com")
        bot.create_subscription("b@test.com")
        analytics = bot.get_subscription_analytics()
        assert analytics["total_subscriptions"] == 2

    def test_analytics_active_count(self):
        bot = SaasBot(tier=Tier.PROFESSIONAL)
        sub = bot.create_subscription("c@test.com", trial_days=0)
        bot.create_subscription("d@test.com", trial_days=0)
        bot.cancel_subscription(sub.subscription_id)
        analytics = bot.get_subscription_analytics()
        assert analytics["active"] == 1
        assert analytics["canceled"] == 1

    def test_analytics_revenue(self):
        bot = SaasBot(tier=Tier.PROFESSIONAL)
        bot.create_subscription("e@test.com", trial_days=0)
        analytics = bot.get_subscription_analytics()
        assert analytics["estimated_monthly_revenue_usd"] > 0

    def test_analytics_by_tier(self):
        bot = SaasBot(tier=Tier.PROFESSIONAL)
        bot.create_subscription("f@test.com")
        analytics = bot.get_subscription_analytics()
        assert "professional" in analytics["by_tier"]


# ===========================================================================
# Tier description
# ===========================================================================

class TestSaasBotDescribeTier:
    def test_returns_string(self):
        bot = SaasBot()
        assert isinstance(bot.describe_tier(), str)

    def test_contains_tier_name(self):
        bot = SaasBot(tier=Tier.PROFESSIONAL)
        assert "Professional" in bot.describe_tier()

    def test_contains_price(self):
        bot = SaasBot(tier=Tier.PROFESSIONAL)
        assert "99" in bot.describe_tier()


# ===========================================================================
# Chat interface
# ===========================================================================

class TestSaasBotChat:
    def test_chat_returns_dict(self):
        bot = SaasBot()
        result = bot.chat("hello")
        assert isinstance(result, dict)

    def test_chat_has_response(self):
        bot = SaasBot()
        result = bot.chat("hello")
        assert "response" in result

    def test_chat_bot_name(self):
        bot = SaasBot()
        result = bot.chat("hi")
        assert result["bot_name"] == "saas_bot"

    def test_chat_tier_query(self):
        bot = SaasBot(tier=Tier.PROFESSIONAL)
        result = bot.chat("what plan am I on?")
        assert "Professional" in result["response"]

    def test_chat_subscription_query(self):
        bot = SaasBot()
        result = bot.chat("how many subscriptions do I have?")
        assert "subscription" in result["response"].lower()

    def test_chat_webhook_query_basic(self):
        bot = SaasBot(tier=Tier.BASIC)
        result = bot.chat("tell me about webhooks")
        assert "Professional" in result["response"] or "professional" in result["response"].lower()

    def test_chat_webhook_query_professional(self):
        bot = SaasBot(tier=Tier.PROFESSIONAL)
        result = bot.chat("webhook processing")
        assert "webhook" in result["response"].lower() or "active" in result["response"].lower()

    def test_chat_stripe_query(self):
        bot = SaasBot()
        result = bot.chat("how does Stripe work?")
        assert "stripe" in result["response"].lower() or "subscription" in result["response"].lower()
