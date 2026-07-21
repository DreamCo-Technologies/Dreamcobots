"""Tests for integrations/payments.py"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest
from integrations.payments import PaymentsClient, SUBSCRIPTION_PLANS, SubscriptionRecord, PaymentRecord


# ---------------------------------------------------------------------------
# Instantiation
# ---------------------------------------------------------------------------

class TestInstantiation:
    def test_mock_when_no_api_key(self):
        client = PaymentsClient()
        assert client.is_mock is True

    def test_mock_forced(self):
        client = PaymentsClient(mock=True)
        assert client.is_mock is True


# ---------------------------------------------------------------------------
# create_subscription
# ---------------------------------------------------------------------------

class TestCreateSubscription:
    def setup_method(self):
        self.client = PaymentsClient(mock=True)

    def test_returns_subscription_record(self):
        sub = self.client.create_subscription("user@example.com", "PRO")
        assert isinstance(sub, SubscriptionRecord)

    def test_mock_status(self):
        sub = self.client.create_subscription("user@example.com", "PRO")
        assert sub.status == "mock"

    def test_correct_plan_price(self):
        sub = self.client.create_subscription("user@example.com", "ENTERPRISE")
        assert sub.price_cents == SUBSCRIPTION_PLANS["ENTERPRISE"]["price_cents"]

    def test_invalid_plan_raises(self):
        with pytest.raises(ValueError):
            self.client.create_subscription("user@example.com", "INVALID_PLAN")

    def test_case_insensitive_plan(self):
        sub = self.client.create_subscription("user@example.com", "pro")
        assert sub.plan == "PRO"

    def test_subscription_stored(self):
        self.client.create_subscription("a@example.com", "PRO")
        self.client.create_subscription("b@example.com", "SCALE")
        subs = self.client.get_subscriptions()
        assert len(subs) == 2

    def test_subscription_id_generated(self):
        sub = self.client.create_subscription("user@example.com", "FREE")
        assert sub.subscription_id.startswith("sub_mock_")


# ---------------------------------------------------------------------------
# cancel_subscription
# ---------------------------------------------------------------------------

class TestCancelSubscription:
    def test_cancel_existing_subscription(self):
        client = PaymentsClient(mock=True)
        sub = client.create_subscription("user@example.com", "PRO")
        result = client.cancel_subscription(sub.subscription_id)
        assert result["status"] == "cancelled"

    def test_cancel_nonexistent(self):
        client = PaymentsClient(mock=True)
        result = client.cancel_subscription("sub_nonexistent")
        assert "error" in result


# ---------------------------------------------------------------------------
# create_charge
# ---------------------------------------------------------------------------

class TestCreateCharge:
    def test_returns_payment_record(self):
        client = PaymentsClient(mock=True)
        charge = client.create_charge("user@example.com", 4999, "Setup fee")
        assert isinstance(charge, PaymentRecord)

    def test_mock_status(self):
        client = PaymentsClient(mock=True)
        charge = client.create_charge("user@example.com", 2900)
        assert charge.status == "mock"

    def test_amount_stored(self):
        client = PaymentsClient(mock=True)
        charge = client.create_charge("user@example.com", 9900)
        assert charge.amount_cents == 9900

    def test_charge_stored(self):
        client = PaymentsClient(mock=True)
        client.create_charge("a@example.com", 100)
        client.create_charge("b@example.com", 200)
        assert len(client.get_payments()) == 2


# ---------------------------------------------------------------------------
# get_revenue_summary
# ---------------------------------------------------------------------------

class TestRevenueSummary:
    def test_summary_keys(self):
        client = PaymentsClient(mock=True)
        summary = client.get_revenue_summary()
        for key in ("active_subscriptions", "mrr_usd", "one_time_revenue_usd", "total_revenue_usd"):
            assert key in summary

    def test_mrr_calculated_correctly(self):
        client = PaymentsClient(mock=True)
        client.create_subscription("a@example.com", "PRO")   # $29/mo
        client.create_subscription("b@example.com", "SCALE") # $99/mo
        summary = client.get_revenue_summary()
        assert summary["mrr_usd"] == pytest.approx(29.0 + 99.0)

    def test_one_time_revenue(self):
        client = PaymentsClient(mock=True)
        client.create_charge("a@example.com", 5000)  # $50
        summary = client.get_revenue_summary()
        assert summary["one_time_revenue_usd"] == pytest.approx(50.0)

    def test_total_revenue_sum(self):
        client = PaymentsClient(mock=True)
        client.create_subscription("a@example.com", "PRO")  # $29
        client.create_charge("b@example.com", 1000)          # $10
        summary = client.get_revenue_summary()
        assert summary["total_revenue_usd"] == pytest.approx(39.0)
