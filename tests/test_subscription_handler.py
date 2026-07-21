"""
Tests for stripe/subscription_handler.py — SubscriptionHandler.
"""

from __future__ import annotations

import json
import os
import sys

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

from stripe.subscription_handler import (
    SubscriptionHandler,
    SubscriptionRecord,
    TIER_CAPABILITIES,
    _tier_capabilities,
)


# ---------------------------------------------------------------------------
# _tier_capabilities helper
# ---------------------------------------------------------------------------


class TestTierCapabilities:
    def test_free_capabilities(self):
        caps = _tier_capabilities("free")
        assert caps["concurrent_bots"] == 2

    def test_pro_capabilities(self):
        caps = _tier_capabilities("pro")
        assert caps["concurrent_bots"] == 10
        assert caps["price_monthly"] == 49.0

    def test_enterprise_capabilities(self):
        caps = _tier_capabilities("enterprise")
        assert caps["concurrent_bots"] == 50

    def test_unknown_tier_falls_back_to_free(self):
        caps = _tier_capabilities("platinum_plus")
        assert caps["concurrent_bots"] == 2


# ---------------------------------------------------------------------------
# SubscriptionRecord
# ---------------------------------------------------------------------------


class TestSubscriptionRecord:
    def test_is_active_for_active_status(self):
        rec = SubscriptionRecord(
            customer_id="cus_1",
            subscription_id="sub_1",
            tier="pro",
            status="active",
        )
        assert rec.is_active is True

    def test_is_active_for_trialing(self):
        rec = SubscriptionRecord(
            customer_id="cus_2", subscription_id="sub_2",
            tier="pro", status="trialing",
        )
        assert rec.is_active is True

    def test_not_active_for_canceled(self):
        rec = SubscriptionRecord(
            customer_id="cus_3", subscription_id="sub_3",
            tier="pro", status="canceled",
        )
        assert rec.is_active is False

    def test_created_at_auto_set(self):
        rec = SubscriptionRecord(
            customer_id="c", subscription_id="s", tier="free", status="active",
        )
        assert rec.created_at != ""

    def test_capabilities_auto_populated(self):
        rec = SubscriptionRecord(
            customer_id="c", subscription_id="s", tier="pro", status="active",
        )
        assert rec.capabilities["concurrent_bots"] == 10


# ---------------------------------------------------------------------------
# SubscriptionHandler — simulation mode
# ---------------------------------------------------------------------------


@pytest.fixture
def handler():
    """Return a SubscriptionHandler in simulation mode (no Stripe key)."""
    return SubscriptionHandler(api_key=None)


class TestSubscriptionHandlerSimMode:
    def test_initialises_in_sim_mode(self, handler):
        assert handler._simulation is True

    def test_get_or_create_customer_returns_string(self, handler):
        cid = handler.get_or_create_customer("user@example.com")
        assert isinstance(cid, str)
        assert cid.startswith("cus_sim_")

    def test_same_email_same_customer_id(self, handler):
        a = handler.get_or_create_customer("x@x.com")
        b = handler.get_or_create_customer("x@x.com")
        assert a == b

    def test_different_emails_different_ids(self, handler):
        a = handler.get_or_create_customer("a@a.com")
        b = handler.get_or_create_customer("b@b.com")
        assert a != b


# ---------------------------------------------------------------------------
# create_subscription
# ---------------------------------------------------------------------------


class TestCreateSubscription:
    def test_creates_free_subscription(self, handler):
        rec = handler.create_subscription("cus_001", tier="free")
        assert isinstance(rec, SubscriptionRecord)
        assert rec.tier == "free"
        assert rec.status == "active"

    def test_creates_pro_subscription(self, handler):
        rec = handler.create_subscription("cus_002", tier="pro")
        assert rec.tier == "pro"
        assert rec.capabilities["concurrent_bots"] == 10

    def test_creates_enterprise_subscription(self, handler):
        rec = handler.create_subscription("cus_003", tier="enterprise")
        assert rec.tier == "enterprise"
        assert rec.capabilities["concurrent_bots"] == 50

    def test_subscription_id_is_string(self, handler):
        rec = handler.create_subscription("cus_004", tier="pro")
        assert isinstance(rec.subscription_id, str)
        assert len(rec.subscription_id) > 0


# ---------------------------------------------------------------------------
# cancel_subscription
# ---------------------------------------------------------------------------


class TestCancelSubscription:
    def test_cancel_existing(self, handler):
        handler.create_subscription("cus_cancel", tier="pro")
        ok = handler.cancel_subscription("cus_cancel")
        assert ok is True
        rec = handler.get_subscription("cus_cancel")
        assert rec.status == "canceled"

    def test_cancel_nonexistent_returns_false(self, handler):
        ok = handler.cancel_subscription("cus_unknown_xyz")
        assert ok is False


# ---------------------------------------------------------------------------
# get_capabilities
# ---------------------------------------------------------------------------


class TestGetCapabilities:
    def test_active_sub_returns_correct_caps(self, handler):
        handler.create_subscription("cus_caps", tier="enterprise")
        caps = handler.get_capabilities("cus_caps")
        assert caps["concurrent_bots"] == 50

    def test_no_sub_returns_free_caps(self, handler):
        caps = handler.get_capabilities("cus_nosub")
        assert caps["concurrent_bots"] == 2

    def test_canceled_sub_returns_free_caps(self, handler):
        handler.create_subscription("cus_canceled2", tier="pro")
        handler.cancel_subscription("cus_canceled2")
        caps = handler.get_capabilities("cus_canceled2")
        assert caps["concurrent_bots"] == 2


# ---------------------------------------------------------------------------
# process_webhook
# ---------------------------------------------------------------------------


class TestProcessWebhook:
    def _raw(self, event_type: str, obj: dict) -> bytes:
        return json.dumps({"type": event_type, "data": {"object": obj}}).encode()

    def test_subscription_created_event(self, handler):
        body = self._raw(
            "customer.subscription.created",
            {
                "id": "sub_w1",
                "customer": "cus_webhook",
                "status": "active",
                "metadata": {"tier": "pro"},
                "items": {"data": []},
            },
        )
        result = handler.process_webhook(body)
        assert result["event_type"] == "customer.subscription.created"
        assert result["handled"] is True

    def test_subscription_deleted_event(self, handler):
        handler.create_subscription("cus_del", tier="pro")
        body = self._raw(
            "customer.subscription.deleted",
            {"id": "sub_del", "customer": "cus_del", "status": "canceled"},
        )
        result = handler.process_webhook(body)
        assert result["handled"] is True
        assert handler.get_subscription("cus_del").status == "canceled"

    def test_payment_succeeded_event(self, handler):
        body = self._raw(
            "invoice.payment_succeeded",
            {"customer": "cus_pay", "amount_paid": 4900},
        )
        result = handler.process_webhook(body)
        assert result["event_type"] == "invoice.payment_succeeded"
        assert result["handled"] is True

    def test_payment_failed_marks_past_due(self, handler):
        handler.create_subscription("cus_fail", tier="pro")
        body = self._raw("invoice.payment_failed", {"customer": "cus_fail"})
        handler.process_webhook(body)
        rec = handler.get_subscription("cus_fail")
        assert rec.status == "past_due"

    def test_unknown_event_returns_not_handled(self, handler):
        body = self._raw("some.unknown.event", {})
        result = handler.process_webhook(body)
        assert result["handled"] is False

    def test_invalid_json_returns_error(self, handler):
        result = handler.process_webhook(b"not json at all")
        assert result["event_type"] == "error"
        assert result["handled"] is False


# ---------------------------------------------------------------------------
# summary()
# ---------------------------------------------------------------------------


class TestSummary:
    def test_returns_list(self, handler):
        assert isinstance(handler.summary(), list)

    def test_includes_created_subscriptions(self, handler):
        handler.create_subscription("cus_sum1", tier="pro")
        handler.create_subscription("cus_sum2", tier="enterprise")
        s = handler.summary()
        ids = {entry["customer_id"] for entry in s}
        assert "cus_sum1" in ids
        assert "cus_sum2" in ids
