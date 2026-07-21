"""Tests for bots/saas_upsell/saas_upsell.py"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest
from bots.saas_upsell.saas_upsell import (
    SaaSUpsell,
    Subscriber,
    MicroBusiness,
    SubscriptionTier,
    TIER_MONTHLY_PRICE,
    ONBOARDING_STEPS,
)


# ---------------------------------------------------------------------------
# Subscriber registration
# ---------------------------------------------------------------------------

class TestRegisterSubscriber:
    def setup_method(self):
        self.saas = SaaSUpsell()

    def test_returns_subscriber(self):
        sub = self.saas.register_subscriber("user@example.com")
        assert isinstance(sub, Subscriber)

    def test_default_tier_free(self):
        sub = self.saas.register_subscriber("user@example.com")
        assert sub.tier == SubscriptionTier.FREE

    def test_subscriber_id_assigned(self):
        sub = self.saas.register_subscriber("user@example.com")
        assert sub.subscriber_id.startswith("sub_")

    def test_list_subscribers(self):
        self.saas.register_subscriber("a@ex.com")
        self.saas.register_subscriber("b@ex.com")
        assert len(self.saas.list_subscribers()) == 2


# ---------------------------------------------------------------------------
# Onboarding tutorial
# ---------------------------------------------------------------------------

class TestOnboarding:
    def setup_method(self):
        self.saas = SaaSUpsell()
        self.sub = self.saas.register_subscriber("user@example.com")

    def test_advance_returns_step_name(self):
        result = self.saas.advance_onboarding(self.sub.subscriber_id)
        assert "step_name" in result
        assert result["step"] == 1

    def test_advance_increments_step(self):
        self.saas.advance_onboarding(self.sub.subscriber_id)
        self.saas.advance_onboarding(self.sub.subscriber_id)
        assert self.sub.onboarding_step == 2

    def test_complete_after_all_steps(self):
        for _ in range(len(ONBOARDING_STEPS)):
            self.saas.advance_onboarding(self.sub.subscriber_id)
        assert self.sub.onboarding_complete is True

    def test_complete_onboarding_immediate(self):
        result = self.saas.complete_onboarding(self.sub.subscriber_id)
        assert result["onboarding_complete"] is True
        assert self.sub.onboarding_complete is True

    def test_advance_after_complete(self):
        self.saas.complete_onboarding(self.sub.subscriber_id)
        result = self.saas.advance_onboarding(self.sub.subscriber_id)
        assert result["status"] == "already_complete"

    def test_invalid_subscriber_raises(self):
        with pytest.raises(KeyError):
            self.saas.advance_onboarding("sub_nonexistent")


# ---------------------------------------------------------------------------
# Upsell
# ---------------------------------------------------------------------------

class TestUpsell:
    def setup_method(self):
        self.saas = SaaSUpsell()
        self.sub = self.saas.register_subscriber("user@example.com")

    def test_upsell_accepted_upgrades_tier(self):
        result = self.saas.upsell(self.sub.subscriber_id, accepted=True)
        assert result["status"] == "upgraded"
        assert self.sub.tier == SubscriptionTier.PRO

    def test_upsell_declined_stays_at_tier(self):
        original_tier = self.sub.tier
        result = self.saas.upsell(self.sub.subscriber_id, accepted=False)
        assert result["status"] == "declined"
        assert self.sub.tier == original_tier

    def test_upsell_sequential_upgrades(self):
        self.saas.upsell(self.sub.subscriber_id, accepted=True)  # FREE → PRO
        self.saas.upsell(self.sub.subscriber_id, accepted=True)  # PRO → SCALE
        assert self.sub.tier == SubscriptionTier.SCALE

    def test_upsell_at_max_tier(self):
        # Upgrade to ENTERPRISE manually
        self.sub.tier = SubscriptionTier.ENTERPRISE
        result = self.saas.upsell(self.sub.subscriber_id, accepted=True)
        assert result["status"] == "already_at_max_tier"

    def test_monthly_revenue_after_upgrade(self):
        self.saas.upsell(self.sub.subscriber_id, accepted=True)  # FREE → PRO
        assert self.sub.monthly_revenue == pytest.approx(TIER_MONTHLY_PRICE["PRO"])


# ---------------------------------------------------------------------------
# Micro-business network
# ---------------------------------------------------------------------------

class TestMicroBusiness:
    def setup_method(self):
        self.saas = SaaSUpsell()

    def test_register_returns_micro_business(self):
        biz = self.saas.register_micro_business("My Biz", "owner@ex.com", 5_000)
        assert isinstance(biz, MicroBusiness)

    def test_business_id_assigned(self):
        biz = self.saas.register_micro_business("Biz", "o@ex.com", 3_000)
        assert biz.business_id.startswith("biz_")

    def test_dreamco_share_calculated(self):
        biz = self.saas.register_micro_business("Biz", "o@ex.com", 10_000, revenue_share_pct=0.10)
        assert biz.dreamco_share == pytest.approx(1_000.0)

    def test_list_micro_businesses(self):
        self.saas.register_micro_business("A", "a@ex.com", 2_000)
        self.saas.register_micro_business("B", "b@ex.com", 3_000)
        assert len(self.saas.list_micro_businesses()) == 2


# ---------------------------------------------------------------------------
# get_revenue_output
# ---------------------------------------------------------------------------

class TestGetRevenueOutput:
    def test_revenue_output_keys(self):
        saas = SaaSUpsell()
        output = saas.get_revenue_output()
        for key in ("revenue", "leads_generated", "conversion_rate", "action"):
            assert key in output

    def test_revenue_includes_mrr(self):
        saas = SaaSUpsell()
        sub = saas.register_subscriber("user@ex.com")
        saas.upsell(sub.subscriber_id, accepted=True)  # → PRO = $29
        output = saas.get_revenue_output()
        assert output["revenue"] >= TIER_MONTHLY_PRICE["PRO"]

    def test_revenue_includes_network_share(self):
        saas = SaaSUpsell()
        saas.register_micro_business("Biz", "o@ex.com", 10_000, revenue_share_pct=0.1)
        output = saas.get_revenue_output()
        assert output["revenue"] >= 1_000.0


# ---------------------------------------------------------------------------
# Dashboard metrics
# ---------------------------------------------------------------------------

class TestDashboardMetrics:
    def test_metrics_keys(self):
        saas = SaaSUpsell()
        metrics = saas.get_dashboard_metrics()
        for key in ("mrr_usd", "arr_usd", "total_subscribers", "paid_subscribers",
                    "tier_breakdown", "micro_business_network_share_usd"):
            assert key in metrics

    def test_arr_equals_mrr_times_12(self):
        saas = SaaSUpsell()
        sub = saas.register_subscriber("u@ex.com")
        saas.upsell(sub.subscriber_id, accepted=True)
        metrics = saas.get_dashboard_metrics()
        assert metrics["arr_usd"] == pytest.approx(metrics["mrr_usd"] * 12)

    def test_tier_breakdown_has_all_tiers(self):
        saas = SaaSUpsell()
        metrics = saas.get_dashboard_metrics()
        for tier in SubscriptionTier:
            assert tier.value in metrics["tier_breakdown"]
