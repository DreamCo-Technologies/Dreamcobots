"""
Tests for bots/stripe_payment_bot/

Covers:
  1. Tiers
  2. StripePaymentBot — checkout, subscriptions, coupons, invoices,
     webhooks, refunds, Connect split payments, fraud radar, analytics
  3. Chat & process interfaces
  4. Edge cases and error handling
"""

from __future__ import annotations

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

from bots.stripe_payment_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
    FEATURE_CHECKOUT,
    FEATURE_SUBSCRIPTIONS,
    FEATURE_WEBHOOKS,
    FEATURE_REFUNDS,
    FEATURE_COUPONS,
    FEATURE_INVOICES,
    FEATURE_CONNECT,
    FEATURE_SPLIT_PAYMENTS,
    FEATURE_ANALYTICS,
    FEATURE_FRAUD_RADAR,
)
from bots.stripe_payment_bot.stripe_payment_bot import (
    StripePaymentBot,
    StripeTierError,
    StripeValidationError,
    Bot,
    PLAN_CATALOGUE,
)


# ===========================================================================
# 1. Tiers
# ===========================================================================

class TestTiers:
    def test_three_tiers_exist(self):
        tiers = list_tiers()
        assert len(tiers) == 3

    def test_starter_price(self):
        cfg = get_tier_config(Tier.STARTER)
        assert cfg.price_usd_monthly == 29.0

    def test_growth_price(self):
        cfg = get_tier_config(Tier.GROWTH)
        assert cfg.price_usd_monthly == 99.0

    def test_enterprise_price(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.price_usd_monthly == 299.0

    def test_starter_payment_limit(self):
        cfg = get_tier_config(Tier.STARTER)
        assert cfg.payments_per_month == 500

    def test_enterprise_unlimited(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.is_unlimited()

    def test_upgrade_from_starter_to_growth(self):
        nxt = get_upgrade_path(Tier.STARTER)
        assert nxt is not None
        assert nxt.tier == Tier.GROWTH

    def test_upgrade_from_growth_to_enterprise(self):
        nxt = get_upgrade_path(Tier.GROWTH)
        assert nxt.tier == Tier.ENTERPRISE

    def test_no_upgrade_from_enterprise(self):
        assert get_upgrade_path(Tier.ENTERPRISE) is None

    def test_starter_has_checkout(self):
        cfg = get_tier_config(Tier.STARTER)
        assert cfg.has_feature(FEATURE_CHECKOUT)

    def test_starter_lacks_subscriptions(self):
        cfg = get_tier_config(Tier.STARTER)
        assert not cfg.has_feature(FEATURE_SUBSCRIPTIONS)

    def test_growth_has_subscriptions(self):
        cfg = get_tier_config(Tier.GROWTH)
        assert cfg.has_feature(FEATURE_SUBSCRIPTIONS)

    def test_enterprise_has_connect(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.has_feature(FEATURE_CONNECT)

    def test_enterprise_has_fraud_radar(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.has_feature(FEATURE_FRAUD_RADAR)

    def test_tier_names(self):
        names = [t.name for t in list_tiers()]
        assert "Starter" in names
        assert "Growth" in names
        assert "Enterprise" in names

    def test_platform_fee_decreases_with_tier(self):
        s = get_tier_config(Tier.STARTER)
        g = get_tier_config(Tier.GROWTH)
        e = get_tier_config(Tier.ENTERPRISE)
        assert s.platform_fee_pct > g.platform_fee_pct >= e.platform_fee_pct


# ===========================================================================
# 2. Checkout
# ===========================================================================

class TestCheckout:
    @pytest.fixture
    def starter(self):
        return StripePaymentBot(tier=Tier.STARTER)

    @pytest.fixture
    def growth(self):
        return StripePaymentBot(tier=Tier.GROWTH)

    def test_create_checkout_returns_session(self, starter):
        s = starter.create_checkout_session(
            amount=99.0, currency="USD",
            product_name="Test Product",
            customer_email="test@example.com",
        )
        assert s["id"].startswith("cs_")
        assert s["payment_status"] == "unpaid"

    def test_checkout_status_open(self, starter):
        s = starter.create_checkout_session(99.0, "USD", "P", "a@b.com")
        assert s["status"] == "open"

    def test_checkout_url_contains_session_id(self, starter):
        s = starter.create_checkout_session(50.0, "USD", "P", "a@b.com")
        assert s["id"] in s["url"]

    def test_checkout_amount_in_cents(self, starter):
        s = starter.create_checkout_session(9.99, "USD", "P", "a@b.com")
        assert s["amount_total"] == 999

    def test_checkout_net_amount_accounts_for_fee(self, starter):
        fee = get_tier_config(Tier.STARTER).platform_fee_pct
        s = starter.create_checkout_session(100.0, "USD", "P", "a@b.com")
        expected_net = round(100.0 * (1 - fee / 100), 2)
        assert s["net_amount_usd"] == expected_net

    def test_confirm_checkout_sets_paid(self, starter):
        s = starter.create_checkout_session(50.0, "USD", "P", "a@b.com")
        confirmed = starter.confirm_checkout(s["id"])
        assert confirmed["payment_status"] == "paid"
        assert confirmed["status"] == "complete"

    def test_confirm_nonexistent_session_raises(self, starter):
        with pytest.raises(StripeValidationError):
            starter.confirm_checkout("cs_does_not_exist")

    def test_invalid_currency_raises(self, starter):
        with pytest.raises(StripeValidationError):
            starter.create_checkout_session(10.0, "XYZ", "P", "a@b.com")

    def test_zero_amount_raises(self, starter):
        with pytest.raises(StripeValidationError):
            starter.create_checkout_session(0.0, "USD", "P", "a@b.com")

    def test_negative_amount_raises(self, starter):
        with pytest.raises(StripeValidationError):
            starter.create_checkout_session(-5.0, "USD", "P", "a@b.com")

    def test_eur_checkout(self, starter):
        s = starter.create_checkout_session(50.0, "EUR", "P", "a@b.com")
        assert s["currency"] == "EUR"

    def test_checkout_metadata_stored(self, starter):
        s = starter.create_checkout_session(
            10.0, "USD", "P", "a@b.com", metadata={"bot": "lead_gen"}
        )
        assert s["metadata"]["bot"] == "lead_gen"

    def test_payment_count_increments(self, starter):
        assert starter._payment_count == 0
        starter.create_checkout_session(10.0, "USD", "P", "a@b.com")
        assert starter._payment_count == 1


# ===========================================================================
# 3. Subscriptions (GROWTH+)
# ===========================================================================

class TestSubscriptions:
    @pytest.fixture
    def growth(self):
        return StripePaymentBot(tier=Tier.GROWTH)

    @pytest.fixture
    def starter(self):
        return StripePaymentBot(tier=Tier.STARTER)

    def test_starter_cannot_subscribe(self, starter):
        with pytest.raises(StripeTierError):
            starter.create_subscription("cus_1", "lead_generator_pro")

    def test_create_subscription_returns_record(self, growth):
        sub = growth.create_subscription("cus_1", "lead_generator_pro")
        assert sub["id"].startswith("sub_")
        assert sub["status"] == "active"

    def test_subscription_uses_plan_price(self, growth):
        sub = growth.create_subscription("cus_1", "lead_generator_pro")
        assert sub["amount_usd"] == PLAN_CATALOGUE["lead_generator_pro"]

    def test_annual_subscription_discounted(self, growth):
        monthly = growth.create_subscription("cus_1", "lead_generator_pro", interval="monthly")
        annual = growth.create_subscription("cus_2", "lead_generator_pro", interval="yearly")
        # Annual = monthly * 10 (2 months free)
        assert annual["amount_usd"] == pytest.approx(monthly["amount_usd"] * 10)

    def test_trial_subscription_status(self, growth):
        sub = growth.create_subscription("cus_1", "lead_generator_pro", trial_days=14)
        assert sub["status"] == "trialing"
        assert sub["trial_days"] == 14

    def test_cancel_subscription(self, growth):
        sub = growth.create_subscription("cus_1", "lead_generator_pro")
        cancelled = growth.cancel_subscription(sub["id"])
        assert cancelled["status"] == "canceled"

    def test_cancel_nonexistent_raises(self, growth):
        with pytest.raises(StripeValidationError):
            growth.cancel_subscription("sub_doesnotexist")

    def test_list_subscriptions_by_customer(self, growth):
        growth.create_subscription("cus_A", "lead_generator_pro")
        growth.create_subscription("cus_A", "crypto_bot_pro")
        growth.create_subscription("cus_B", "fiverr_bot_pro")
        subs = growth.list_subscriptions("cus_A")
        assert len(subs) == 2

    def test_invalid_interval_raises(self, growth):
        with pytest.raises(StripeValidationError):
            growth.create_subscription("cus_1", "lead_generator_pro", interval="weekly")


# ===========================================================================
# 4. Coupons (GROWTH+)
# ===========================================================================

class TestCoupons:
    @pytest.fixture
    def growth(self):
        return StripePaymentBot(tier=Tier.GROWTH)

    @pytest.fixture
    def starter(self):
        return StripePaymentBot(tier=Tier.STARTER)

    def test_starter_cannot_validate_coupon(self, starter):
        with pytest.raises(StripeTierError):
            starter.validate_coupon("DREAMCO10")

    def test_valid_coupon_returns_discount(self, growth):
        result = growth.validate_coupon("DREAMCO10")
        assert result["valid"] is True
        assert result["discount_pct"] == 10.0

    def test_invalid_coupon_returns_false(self, growth):
        result = growth.validate_coupon("NOTACODE")
        assert result["valid"] is False
        assert result["discount_pct"] == 0.0

    def test_coupon_case_insensitive(self, growth):
        result = growth.validate_coupon("dreamco20")
        assert result["valid"] is True

    def test_coupon_applied_to_subscription(self, growth):
        no_coupon = growth.create_subscription("cus_1", "lead_generator_pro")
        with_coupon = growth.create_subscription("cus_2", "lead_generator_pro", coupon_id="DREAMCO10")
        assert with_coupon["amount_usd"] < no_coupon["amount_usd"]

    def test_launch_50_coupon(self, growth):
        result = growth.validate_coupon("LAUNCH50")
        assert result["discount_pct"] == 50.0


# ===========================================================================
# 5. Invoices (GROWTH+)
# ===========================================================================

class TestInvoices:
    @pytest.fixture
    def growth(self):
        return StripePaymentBot(tier=Tier.GROWTH)

    @pytest.fixture
    def starter(self):
        return StripePaymentBot(tier=Tier.STARTER)

    def test_starter_cannot_create_invoice(self, starter):
        with pytest.raises(StripeTierError):
            starter.create_invoice("cus_1", [{"description": "x", "amount": 100}])

    def test_create_invoice_returns_record(self, growth):
        inv = growth.create_invoice(
            "cus_1",
            [{"description": "Lead Gen API Access", "amount": 299.0}],
        )
        assert inv["id"].startswith("in_")
        assert inv["status"] == "open"

    def test_invoice_total_is_sum_of_line_items(self, growth):
        inv = growth.create_invoice(
            "cus_1",
            [{"description": "A", "amount": 100.0}, {"description": "B", "amount": 50.0}],
        )
        assert inv["total_amount"] == 150.0

    def test_pay_invoice(self, growth):
        inv = growth.create_invoice("cus_1", [{"description": "x", "amount": 200.0}])
        paid = growth.pay_invoice(inv["id"])
        assert paid["status"] == "paid"

    def test_pay_nonexistent_invoice_raises(self, growth):
        with pytest.raises(StripeValidationError):
            growth.pay_invoice("in_doesnotexist")

    def test_invoice_increases_revenue(self, growth):
        rev_before = growth._revenue_usd
        inv = growth.create_invoice("cus_1", [{"description": "x", "amount": 500.0}])
        growth.pay_invoice(inv["id"])
        assert growth._revenue_usd > rev_before

    def test_invoice_invalid_currency_raises(self, growth):
        with pytest.raises(StripeValidationError):
            growth.create_invoice("cus_1", [{"description": "x", "amount": 100}], currency="XYZ")

    def test_invoice_zero_total_raises(self, growth):
        with pytest.raises(StripeValidationError):
            growth.create_invoice("cus_1", [{"description": "x", "amount": 0}])


# ===========================================================================
# 6. Webhooks (GROWTH+)
# ===========================================================================

class TestWebhooks:
    @pytest.fixture
    def growth(self):
        return StripePaymentBot(tier=Tier.GROWTH)

    @pytest.fixture
    def starter(self):
        return StripePaymentBot(tier=Tier.STARTER)

    def test_starter_cannot_process_webhooks(self, starter):
        with pytest.raises(StripeTierError):
            starter.process_webhook({"type": "payment_intent.succeeded"})

    def test_payment_succeeded_event(self, growth):
        result = growth.process_webhook({
            "type": "payment_intent.succeeded",
            "data": {"object": {"amount": 9900}},
        })
        assert result["handled"] is True
        assert result["action"] == "revenue_recorded"

    def test_payment_failed_event(self, growth):
        result = growth.process_webhook({"type": "payment_intent.payment_failed", "data": {"object": {}}})
        assert result["action"] == "payment_failed_logged"

    def test_subscription_created_event(self, growth):
        result = growth.process_webhook({"type": "customer.subscription.created", "data": {"object": {}}})
        assert result["action"] == "subscription_activated"

    def test_subscription_deleted_event(self, growth):
        result = growth.process_webhook({"type": "customer.subscription.deleted", "data": {"object": {}}})
        assert result["action"] == "subscription_deactivated"

    def test_invoice_payment_succeeded_event(self, growth):
        result = growth.process_webhook({
            "type": "invoice.payment_succeeded",
            "data": {"object": {"amount_paid": 4900}},
        })
        assert result["action"] == "invoice_paid"

    def test_invoice_payment_failed_event(self, growth):
        result = growth.process_webhook({"type": "invoice.payment_failed", "data": {"object": {}}})
        assert result["action"] == "invoice_payment_failed_logged"

    def test_unknown_event_not_handled(self, growth):
        result = growth.process_webhook({"type": "mystery.event", "data": {"object": {}}})
        assert result["handled"] is False

    def test_webhook_log_stores_events(self, growth):
        growth.process_webhook({"type": "payment_intent.succeeded", "data": {"object": {"amount": 100}}})
        log = growth.get_webhook_log()
        assert len(log) == 1

    def test_multiple_webhooks_logged(self, growth):
        for _ in range(5):
            growth.process_webhook({"type": "payment_intent.succeeded", "data": {"object": {"amount": 1000}}})
        assert len(growth.get_webhook_log()) == 5


# ===========================================================================
# 7. Refunds (all tiers)
# ===========================================================================

class TestRefunds:
    @pytest.fixture
    def starter(self):
        return StripePaymentBot(tier=Tier.STARTER)

    def test_full_refund(self, starter):
        s = starter.create_checkout_session(100.0, "USD", "P", "a@b.com")
        ref = starter.create_refund(s["id"])
        assert ref["status"] == "succeeded"
        assert ref["amount"] == 100.0

    def test_partial_refund(self, starter):
        s = starter.create_checkout_session(100.0, "USD", "P", "a@b.com")
        ref = starter.create_refund(s["id"], amount=25.0)
        assert ref["amount"] == 25.0

    def test_refund_exceeds_original_raises(self, starter):
        s = starter.create_checkout_session(50.0, "USD", "P", "a@b.com")
        with pytest.raises(StripeValidationError):
            starter.create_refund(s["id"], amount=999.0)

    def test_refund_nonexistent_session_raises(self, starter):
        with pytest.raises(StripeValidationError):
            starter.create_refund("cs_nope")

    def test_refund_decreases_revenue(self, starter):
        s = starter.create_checkout_session(100.0, "USD", "P", "a@b.com")
        before = starter._revenue_usd
        starter.create_refund(s["id"], amount=100.0)
        assert starter._revenue_usd < before

    def test_refund_id_starts_with_re(self, starter):
        s = starter.create_checkout_session(50.0, "USD", "P", "a@b.com")
        ref = starter.create_refund(s["id"])
        assert ref["id"].startswith("re_")


# ===========================================================================
# 8. Stripe Connect (ENTERPRISE)
# ===========================================================================

class TestConnect:
    @pytest.fixture
    def enterprise(self):
        return StripePaymentBot(tier=Tier.ENTERPRISE)

    @pytest.fixture
    def growth(self):
        return StripePaymentBot(tier=Tier.GROWTH)

    def test_growth_cannot_create_connect_account(self, growth):
        with pytest.raises(StripeTierError):
            growth.create_connect_account("seller@example.com")

    def test_create_connect_account(self, enterprise):
        acct = enterprise.create_connect_account("seller@example.com")
        assert acct["id"].startswith("acct_")
        assert "onboarding_url" in acct

    def test_split_payment(self, enterprise):
        acct = enterprise.create_connect_account("seller@example.com")
        transfer = enterprise.split_payment(
            amount=100.0,
            currency="USD",
            destination_account_id=acct["id"],
            platform_fee_usd=20.0,
        )
        assert transfer["net_to_seller"] == 80.0
        assert transfer["platform_fee_usd"] == 20.0

    def test_split_payment_to_unknown_account_raises(self, enterprise):
        with pytest.raises(StripeValidationError):
            enterprise.split_payment(100.0, "USD", "acct_unknown", 10.0)

    def test_split_payment_increases_revenue_by_fee(self, enterprise):
        acct = enterprise.create_connect_account("s@e.com")
        before = enterprise._revenue_usd
        enterprise.split_payment(100.0, "USD", acct["id"], 25.0)
        assert enterprise._revenue_usd == pytest.approx(before + 25.0)


# ===========================================================================
# 9. Fraud Radar (ENTERPRISE)
# ===========================================================================

class TestFraudRadar:
    @pytest.fixture
    def enterprise(self):
        return StripePaymentBot(tier=Tier.ENTERPRISE)

    @pytest.fixture
    def growth(self):
        return StripePaymentBot(tier=Tier.GROWTH)

    def test_growth_cannot_check_fraud(self, growth):
        with pytest.raises(StripeTierError):
            growth.check_fraud_score("pm_card", 100.0, "1.2.3.4")

    def test_fraud_check_returns_risk_level(self, enterprise):
        result = enterprise.check_fraud_score("pm_card_visa", 50.0, "10.0.0.1")
        assert "risk_level" in result
        assert result["risk_level"] in {"normal", "elevated", "high"}

    def test_fraud_check_returns_recommendation(self, enterprise):
        result = enterprise.check_fraud_score("pm_card_visa", 50.0, "10.0.0.1")
        assert result["recommendation"] in {"allow", "review", "block"}

    def test_fraud_score_range(self, enterprise):
        result = enterprise.check_fraud_score("pm_card", 100.0, "1.1.1.1")
        assert 0 <= result["risk_score"] <= 100


# ===========================================================================
# 10. Analytics (GROWTH+)
# ===========================================================================

class TestAnalytics:
    @pytest.fixture
    def growth(self):
        return StripePaymentBot(tier=Tier.GROWTH)

    @pytest.fixture
    def starter(self):
        return StripePaymentBot(tier=Tier.STARTER)

    def test_starter_cannot_get_analytics(self, starter):
        with pytest.raises(StripeTierError):
            starter.get_revenue_summary()

    def test_revenue_summary_keys(self, growth):
        summary = growth.get_revenue_summary()
        for key in ("total_revenue_usd", "total_checkouts", "total_subscriptions", "tier"):
            assert key in summary

    def test_revenue_tracks_checkouts(self, growth):
        growth.create_checkout_session(200.0, "USD", "P", "a@b.com")
        summary = growth.get_revenue_summary()
        assert summary["total_checkouts"] == 1

    def test_active_subscription_count(self, growth):
        growth.create_subscription("cus_1", "lead_generator_pro")
        growth.create_subscription("cus_2", "crypto_bot_pro")
        summary = growth.get_revenue_summary()
        assert summary["active_subscriptions"] == 2

    def test_revenue_by_plan_populated(self, growth):
        growth.create_subscription("cus_1", "lead_generator_pro")
        summary = growth.get_revenue_summary()
        assert "lead_generator_pro" in summary["revenue_by_plan"]


# ===========================================================================
# 11. Monthly cap enforcement
# ===========================================================================

class TestMonthlyCap:
    def test_cap_enforced_on_starter(self):
        bot = StripePaymentBot(tier=Tier.STARTER)
        bot._payment_count = 500  # Simulate cap reached
        with pytest.raises(StripeTierError):
            bot.create_checkout_session(10.0, "USD", "P", "a@b.com")

    def test_enterprise_ignores_cap(self):
        bot = StripePaymentBot(tier=Tier.ENTERPRISE)
        bot._payment_count = 999_999  # Way above any cap
        # Should not raise
        bot.create_checkout_session(10.0, "USD", "P", "a@b.com")


# ===========================================================================
# 12. Chat & process interfaces
# ===========================================================================

class TestChatProcess:
    @pytest.fixture
    def growth(self):
        return StripePaymentBot(tier=Tier.GROWTH)

    def test_chat_checkout_trigger(self, growth):
        result = growth.chat("I want to create a checkout for a new product")
        assert "url" in result.get("data", {}) or "checkout" in result["message"].lower()

    def test_chat_subscribe_trigger(self, growth):
        result = growth.chat("I want to subscribe to a plan")
        assert "sub_" in result.get("data", {}).get("id", "") or "subscription" in result["message"].lower()

    def test_chat_revenue_trigger(self, growth):
        result = growth.chat("show me the revenue summary")
        assert "data" in result or "analytics" in result["message"].lower()

    def test_chat_refund_info(self, growth):
        result = growth.chat("I need a refund")
        assert "refund" in result["message"].lower()

    def test_chat_default_response(self, growth):
        result = growth.chat("hello there")
        assert "tier" in result["message"].lower() or "stripe" in result["message"].lower()

    def test_process_delegates_to_chat(self, growth):
        result = growth.process({"command": "check revenue"})
        assert "message" in result

    def test_bot_alias(self):
        assert Bot is StripePaymentBot


# ===========================================================================
# 13. Plan catalogue
# ===========================================================================

class TestPlanCatalogue:
    def test_all_dreamco_plans_present(self):
        expected_plans = [
            "lead_generator_starter",
            "lead_generator_pro",
            "lead_generator_enterprise",
            "real_estate_starter",
            "real_estate_pro",
            "crypto_bot_starter",
            "fiverr_bot_pro",
            "empire_enterprise",
        ]
        for plan in expected_plans:
            assert plan in PLAN_CATALOGUE

    def test_plan_prices_positive(self):
        for name, price in PLAN_CATALOGUE.items():
            assert price > 0, f"Plan '{name}' has non-positive price"

    def test_enterprise_plans_cost_more(self):
        assert PLAN_CATALOGUE["lead_generator_enterprise"] > PLAN_CATALOGUE["lead_generator_pro"]
        assert PLAN_CATALOGUE["lead_generator_pro"] > PLAN_CATALOGUE["lead_generator_starter"]
