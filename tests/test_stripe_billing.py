"""
Tests for saas/stripe_billing.py

Covers the StripeBillingService in simulation mode:
  - Customer creation
  - Subscription creation (all tiers)
  - Subscription cancellation
  - Subscription upgrade
  - Webhook handling
  - Revenue summary / reporting
  - Payment flow end-to-end
  - Edge cases and validation
"""

from __future__ import annotations

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from saas.stripe_billing import (
    StripeBillingService,
    STRIPE_PRICE_IDS,
    TIER_PRICES_USD,
)


# ===========================================================================
# Fixtures
# ===========================================================================


@pytest.fixture()
def billing():
    """Fresh StripeBillingService in simulation mode."""
    return StripeBillingService(simulation_mode=True)


# ===========================================================================
# 1. Module-level constants
# ===========================================================================


class TestConstants:
    def test_price_ids_have_pro(self):
        assert "pro" in STRIPE_PRICE_IDS

    def test_price_ids_have_enterprise(self):
        assert "enterprise" in STRIPE_PRICE_IDS

    def test_tier_prices_have_free(self):
        assert TIER_PRICES_USD["free"] == 0.0

    def test_tier_prices_have_pro(self):
        assert TIER_PRICES_USD["pro"] > 0

    def test_tier_prices_have_enterprise(self):
        assert TIER_PRICES_USD["enterprise"] > TIER_PRICES_USD["pro"]


# ===========================================================================
# 2. Instantiation
# ===========================================================================


class TestInstantiation:
    def test_simulation_mode_explicit(self):
        svc = StripeBillingService(simulation_mode=True)
        summary = svc.revenue_summary()
        assert summary["simulation_mode"] is True

    def test_simulation_mode_no_api_key(self, monkeypatch):
        monkeypatch.delenv("STRIPE_API_KEY", raising=False)
        svc = StripeBillingService()
        summary = svc.revenue_summary()
        assert summary["simulation_mode"] is True

    def test_initial_revenue_is_zero(self, billing):
        summary = billing.revenue_summary()
        assert summary["total_revenue_usd"] == 0.0

    def test_initial_subscriptions_empty(self, billing):
        summary = billing.revenue_summary()
        assert summary["total_subscriptions"] == 0
        assert summary["active_subscriptions"] == 0


# ===========================================================================
# 3. Customer management
# ===========================================================================


class TestCustomerManagement:
    def test_create_customer_success(self, billing):
        result = billing.create_customer("usr_abc", "abc@example.com")
        assert result["success"] is True

    def test_create_customer_returns_customer_id(self, billing):
        result = billing.create_customer("usr_abc", "abc@example.com")
        assert "customer_id" in result
        assert result["customer_id"]

    def test_create_customer_marks_simulation(self, billing):
        result = billing.create_customer("usr_abc", "abc@example.com")
        assert result["simulation"] is True

    def test_different_users_get_different_ids(self, billing):
        r1 = billing.create_customer("usr_00000001", "a@b.com")
        r2 = billing.create_customer("usr_00000002", "c@d.com")
        assert r1["customer_id"] != r2["customer_id"]


# ===========================================================================
# 4. Subscription creation
# ===========================================================================


class TestSubscriptionCreation:
    def test_create_free_subscription(self, billing):
        cust = billing.create_customer("usr_001", "a@b.com")
        result = billing.create_subscription(cust["customer_id"], "free", "usr_001")
        assert result["success"] is True
        assert result["tier"] == "free"
        assert result["amount_usd"] == 0.0

    def test_create_pro_subscription(self, billing):
        cust = billing.create_customer("usr_002", "b@c.com")
        result = billing.create_subscription(cust["customer_id"], "pro", "usr_002")
        assert result["success"] is True
        assert result["tier"] == "pro"
        assert result["amount_usd"] == TIER_PRICES_USD["pro"]

    def test_create_enterprise_subscription(self, billing):
        cust = billing.create_customer("usr_003", "c@d.com")
        result = billing.create_subscription(cust["customer_id"], "enterprise", "usr_003")
        assert result["success"] is True
        assert result["tier"] == "enterprise"
        assert result["amount_usd"] == TIER_PRICES_USD["enterprise"]

    def test_subscription_has_id(self, billing):
        cust = billing.create_customer("usr_004", "d@e.com")
        result = billing.create_subscription(cust["customer_id"], "pro", "usr_004")
        assert "subscription_id" in result
        assert result["subscription_id"]

    def test_invalid_tier_rejected(self, billing):
        cust = billing.create_customer("usr_005", "e@f.com")
        result = billing.create_subscription(cust["customer_id"], "nonexistent_tier")
        assert result["success"] is False
        assert "error" in result
        assert "nonexistent_tier" in result["error"]

    def test_multiple_subscriptions_tracked(self, billing):
        for i in range(3):
            cust = billing.create_customer(f"usr_multi_{i:03d}", f"user{i}@test.com")
            billing.create_subscription(cust["customer_id"], "pro", f"usr_multi_{i:03d}")
        summary = billing.revenue_summary()
        assert summary["total_subscriptions"] >= 3


# ===========================================================================
# 5. Subscription cancellation
# ===========================================================================


class TestSubscriptionCancellation:
    def test_cancel_subscription_success(self, billing):
        cust = billing.create_customer("usr_006", "f@g.com")
        sub = billing.create_subscription(cust["customer_id"], "pro", "usr_006")
        result = billing.cancel_subscription(sub["subscription_id"])
        assert result["success"] is True

    def test_cancel_subscription_status_cancelled(self, billing):
        cust = billing.create_customer("usr_007", "g@h.com")
        sub = billing.create_subscription(cust["customer_id"], "pro", "usr_007")
        result = billing.cancel_subscription(sub["subscription_id"])
        assert result["status"] == "cancelled"

    def test_cancel_subscription_returns_id(self, billing):
        cust = billing.create_customer("usr_008", "h@i.com")
        sub = billing.create_subscription(cust["customer_id"], "enterprise", "usr_008")
        result = billing.cancel_subscription(sub["subscription_id"])
        assert result["subscription_id"] == sub["subscription_id"]

    def test_cancelled_subscription_reduces_active_count(self, billing):
        cust = billing.create_customer("usr_009", "i@j.com")
        sub = billing.create_subscription(cust["customer_id"], "pro", "usr_009")
        before = billing.revenue_summary()["active_subscriptions"]
        billing.cancel_subscription(sub["subscription_id"])
        after = billing.revenue_summary()["active_subscriptions"]
        assert after == before - 1


# ===========================================================================
# 6. Subscription upgrade
# ===========================================================================


class TestSubscriptionUpgrade:
    def test_upgrade_free_to_pro(self, billing):
        cust = billing.create_customer("usr_010", "j@k.com")
        sub = billing.create_subscription(cust["customer_id"], "free", "usr_010")
        result = billing.upgrade_subscription(sub["subscription_id"], "pro", "usr_010")
        assert result["success"] is True
        assert result["new_tier"] == "pro"

    def test_upgrade_pro_to_enterprise(self, billing):
        cust = billing.create_customer("usr_011", "k@l.com")
        sub = billing.create_subscription(cust["customer_id"], "pro", "usr_011")
        result = billing.upgrade_subscription(sub["subscription_id"], "enterprise", "usr_011")
        assert result["success"] is True
        assert result["new_tier"] == "enterprise"

    def test_upgrade_records_old_tier(self, billing):
        cust = billing.create_customer("usr_012", "l@m.com")
        sub = billing.create_subscription(cust["customer_id"], "free", "usr_012")
        result = billing.upgrade_subscription(sub["subscription_id"], "pro", "usr_012")
        assert result["old_tier"] == "free"

    def test_upgrade_returns_subscription_id(self, billing):
        cust = billing.create_customer("usr_013", "m@n.com")
        sub = billing.create_subscription(cust["customer_id"], "pro", "usr_013")
        result = billing.upgrade_subscription(sub["subscription_id"], "enterprise", "usr_013")
        assert result["subscription_id"] == sub["subscription_id"]


# ===========================================================================
# 7. Webhook handling
# ===========================================================================


class TestWebhookHandling:
    def test_webhook_simulation_succeeds(self, billing):
        result = billing.handle_webhook(b'{"type":"test"}', "sig_test_header")
        assert result["success"] is True

    def test_webhook_simulation_event_type(self, billing):
        result = billing.handle_webhook(b"{}", "sig_test")
        assert result["event_type"] == "simulation"

    def test_webhook_marks_simulation(self, billing):
        result = billing.handle_webhook(b"{}", "sig_test")
        assert result["simulation"] is True

    def test_webhook_succeeds_in_simulation_when_no_secret(self, monkeypatch):
        monkeypatch.delenv("STRIPE_API_KEY", raising=False)
        monkeypatch.delenv("STRIPE_WEBHOOK_SECRET", raising=False)
        # Without an API key the service is in simulation mode, so
        # handle_webhook should still succeed (simulation path).
        svc = StripeBillingService()
        result = svc.handle_webhook(b"{}", "sig_test")
        assert result["success"] is True


# ===========================================================================
# 8. Revenue summary / reporting
# ===========================================================================


class TestRevenueSummary:
    def test_revenue_increases_after_pro_subscription(self, billing):
        cust = billing.create_customer("usr_014", "n@o.com")
        billing.create_subscription(cust["customer_id"], "pro", "usr_014")
        summary = billing.revenue_summary()
        assert summary["total_revenue_usd"] >= TIER_PRICES_USD["pro"]

    def test_revenue_zero_for_free_tier(self, billing):
        cust = billing.create_customer("usr_015", "o@p.com")
        billing.create_subscription(cust["customer_id"], "free", "usr_015")
        summary = billing.revenue_summary()
        assert summary["total_revenue_usd"] == 0.0

    def test_revenue_log_count_increments(self, billing):
        cust = billing.create_customer("usr_016", "p@q.com")
        billing.create_subscription(cust["customer_id"], "pro", "usr_016")
        summary = billing.revenue_summary()
        assert summary["revenue_log_count"] >= 1

    def test_multiple_subscriptions_sum_revenue(self, billing):
        for i in range(3):
            cust = billing.create_customer(f"usr_rev_{i:03d}", f"rev{i}@test.com")
            billing.create_subscription(cust["customer_id"], "pro", f"usr_rev_{i:03d}")
        summary = billing.revenue_summary()
        expected = TIER_PRICES_USD["pro"] * 3
        assert summary["total_revenue_usd"] >= expected

    def test_summary_simulation_flag(self, billing):
        summary = billing.revenue_summary()
        assert summary["simulation_mode"] is True

    def test_summary_keys_present(self, billing):
        summary = billing.revenue_summary()
        expected_keys = {
            "total_revenue_usd",
            "active_subscriptions",
            "total_subscriptions",
            "revenue_log_count",
            "simulation_mode",
        }
        assert expected_keys.issubset(summary.keys())


# ===========================================================================
# 9. Full payment-flow end-to-end scenarios
# ===========================================================================


class TestPaymentFlows:
    def test_complete_pro_lifecycle(self, billing):
        """Create → subscribe → upgrade → cancel."""
        cust = billing.create_customer("usr_e2e_001", "e2e@example.com")
        assert cust["success"] is True

        sub = billing.create_subscription(cust["customer_id"], "free", "usr_e2e_001")
        assert sub["success"] is True

        upgrade = billing.upgrade_subscription(sub["subscription_id"], "pro", "usr_e2e_001")
        assert upgrade["success"] is True
        assert upgrade["new_tier"] == "pro"

        cancel = billing.cancel_subscription(sub["subscription_id"])
        assert cancel["success"] is True
        assert cancel["status"] == "cancelled"

    def test_enterprise_subscription_flow(self, billing):
        """Create customer → enterprise subscription → check revenue."""
        cust = billing.create_customer("usr_e2e_002", "enterprise@example.com")
        sub = billing.create_subscription(cust["customer_id"], "enterprise", "usr_e2e_002")
        assert sub["success"] is True

        summary = billing.revenue_summary()
        assert summary["total_revenue_usd"] >= TIER_PRICES_USD["enterprise"]
        assert summary["active_subscriptions"] >= 1

    def test_webhook_followed_by_revenue_check(self, billing):
        """Subscribe, process a webhook, verify revenue summary remains consistent."""
        cust = billing.create_customer("usr_e2e_003", "webhook@example.com")
        billing.create_subscription(cust["customer_id"], "pro", "usr_e2e_003")

        wh = billing.handle_webhook(b'{"type":"invoice.payment_succeeded"}', "sig_test")
        assert wh["success"] is True

        summary = billing.revenue_summary()
        assert summary["revenue_log_count"] >= 1

    def test_multi_customer_isolation(self, billing):
        """Two customers' subscriptions are independently tracked."""
        c1 = billing.create_customer("usr_iso_001", "iso1@example.com")
        c2 = billing.create_customer("usr_iso_002", "iso2@example.com")

        s1 = billing.create_subscription(c1["customer_id"], "pro", "usr_iso_001")
        s2 = billing.create_subscription(c2["customer_id"], "enterprise", "usr_iso_002")

        assert s1["subscription_id"] != s2["subscription_id"]

        cancel = billing.cancel_subscription(s1["subscription_id"])
        assert cancel["success"] is True

        # s2 should still be active
        summary = billing.revenue_summary()
        assert summary["active_subscriptions"] >= 1

    def test_free_to_enterprise_upgrade_flow(self, billing):
        """Full upgrade path: free → pro → enterprise."""
        cust = billing.create_customer("usr_e2e_004", "upgrade@example.com")
        sub = billing.create_subscription(cust["customer_id"], "free", "usr_e2e_004")

        up1 = billing.upgrade_subscription(sub["subscription_id"], "pro", "usr_e2e_004")
        assert up1["new_tier"] == "pro"

        up2 = billing.upgrade_subscription(sub["subscription_id"], "enterprise", "usr_e2e_004")
        assert up2["new_tier"] == "enterprise"
