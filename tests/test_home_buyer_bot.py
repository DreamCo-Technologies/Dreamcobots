"""Tests for bots/home_buyer_bot/home_buyer_bot.py"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
AI_MODELS_DIR = os.path.join(REPO_ROOT, "bots", "ai-models-integration")
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from bots.home_buyer_bot.home_buyer_bot import (
    HomeBuyerBot,
    DealType,
    LeadStatus,
    PaymentProvider,
    HomeBuyerBotError,
    SERVICE_FEES,
    CHICAGO_LISTINGS,
)


# ---------------------------------------------------------------------------
# Instantiation
# ---------------------------------------------------------------------------


class TestHomeBuyerBotInstantiation:
    def test_default_tier_is_free(self):
        bot = HomeBuyerBot()
        assert bot.tier == Tier.FREE

    def test_pro_tier(self):
        bot = HomeBuyerBot(tier=Tier.PRO)
        assert bot.tier == Tier.PRO

    def test_enterprise_tier(self):
        bot = HomeBuyerBot(tier=Tier.ENTERPRISE)
        assert bot.tier == Tier.ENTERPRISE

    def test_config_loaded(self):
        bot = HomeBuyerBot()
        assert bot.config is not None

    def test_initial_leads_empty(self):
        bot = HomeBuyerBot()
        assert bot.list_leads() == []

    def test_initial_payments_empty(self):
        bot = HomeBuyerBot()
        assert bot.revenue_summary()["total_payments"] == 0


# ---------------------------------------------------------------------------
# Lead management
# ---------------------------------------------------------------------------


class TestLeadSubmission:
    def setup_method(self):
        self.bot = HomeBuyerBot(tier=Tier.FREE)

    def test_submit_lead_returns_dict(self):
        result = self.bot.submit_lead(
            "Alice", "alice@example.com", "312-555-0001",
            DealType.BUY, 400000
        )
        assert isinstance(result, dict)

    def test_submit_lead_has_lead_id(self):
        result = self.bot.submit_lead(
            "Bob", "bob@example.com", "312-555-0002",
            DealType.RENT, 2000
        )
        assert "lead_id" in result
        assert result["lead_id"].startswith("lead-")

    def test_submit_lead_stores_name(self):
        result = self.bot.submit_lead(
            "Carol", "carol@example.com", "312-555-0003",
            DealType.BUY, 300000
        )
        assert result["name"] == "Carol"

    def test_submit_lead_stores_deal_type(self):
        result = self.bot.submit_lead(
            "Dave", "dave@example.com", "312-555-0004",
            DealType.OFF_MARKET, 150000
        )
        assert result["deal_type"] == "off_market"

    def test_submit_lead_default_status_is_new(self):
        result = self.bot.submit_lead(
            "Eve", "eve@example.com", "312-555-0005",
            DealType.BUY, 500000
        )
        assert result["status"] == "new"

    def test_get_lead_returns_correct_data(self):
        submitted = self.bot.submit_lead(
            "Frank", "frank@example.com", "312-555-0006",
            DealType.BUY, 250000
        )
        fetched = self.bot.get_lead(submitted["lead_id"])
        assert fetched["lead_id"] == submitted["lead_id"]

    def test_get_lead_unknown_raises_error(self):
        with pytest.raises(HomeBuyerBotError):
            self.bot.get_lead("lead-nonexistent")

    def test_list_leads_returns_all(self):
        for i in range(3):
            self.bot.submit_lead(
                f"User{i}", f"u{i}@example.com", "312-555-0000",
                DealType.RENT, 1500
            )
        assert len(self.bot.list_leads()) == 3

    def test_update_lead_status(self):
        lead = self.bot.submit_lead(
            "Grace", "grace@example.com", "312-555-0007",
            DealType.BUY, 350000
        )
        updated = self.bot.update_lead_status(
            lead["lead_id"], LeadStatus.QUALIFIED, notes="Ready to close"
        )
        assert updated["status"] == "qualified"
        assert updated["notes"] == "Ready to close"

    def test_update_unknown_lead_raises(self):
        with pytest.raises(HomeBuyerBotError):
            self.bot.update_lead_status("lead-unknown", LeadStatus.CONTACTED)

    def test_list_leads_filter_by_status(self):
        lead = self.bot.submit_lead(
            "Hank", "hank@example.com", "312-555-0008",
            DealType.BUY, 300000
        )
        self.bot.update_lead_status(lead["lead_id"], LeadStatus.QUALIFIED)
        qualified = self.bot.list_leads(status=LeadStatus.QUALIFIED)
        new_leads = self.bot.list_leads(status=LeadStatus.NEW)
        assert len(qualified) == 1
        assert len(new_leads) == 0


# ---------------------------------------------------------------------------
# Property search
# ---------------------------------------------------------------------------


class TestSearchListings:
    def setup_method(self):
        self.bot = HomeBuyerBot(tier=Tier.FREE)

    def test_search_buy_returns_list(self):
        results = self.bot.search_listings(DealType.BUY)
        assert isinstance(results, list)
        assert len(results) > 0

    def test_search_rent_returns_list(self):
        results = self.bot.search_listings(DealType.RENT)
        assert isinstance(results, list)
        assert len(results) > 0

    def test_search_buy_with_max_price_filters(self):
        results = self.bot.search_listings(DealType.BUY, max_price=300000)
        for listing in results:
            assert listing["price"] <= 300000

    def test_search_rent_with_max_price_filters(self):
        results = self.bot.search_listings(DealType.RENT, max_price=2000)
        for listing in results:
            assert listing["monthly_rent"] <= 2000

    def test_search_with_neighborhood_filter(self):
        results = self.bot.search_listings(DealType.BUY, neighborhood="Lakeview")
        for listing in results:
            assert "lakeview" in listing["neighborhood"].lower()

    def test_search_nonexistent_neighborhood_returns_empty(self):
        results = self.bot.search_listings(DealType.BUY, neighborhood="Atlantis")
        assert results == []

    def test_search_off_market_free_tier_requires_upgrade(self):
        with pytest.raises(HomeBuyerBotError):
            self.bot.get_off_market_deals()

    def test_search_off_market_pro_tier_works(self):
        bot = HomeBuyerBot(tier=Tier.PRO)
        results = bot.get_off_market_deals()
        assert isinstance(results, list)
        assert len(results) > 0


# ---------------------------------------------------------------------------
# Payment processing
# ---------------------------------------------------------------------------


class TestPaymentProcessing:
    def setup_method(self):
        self.bot = HomeBuyerBot(tier=Tier.FREE)
        lead = self.bot.submit_lead(
            "Ivan", "ivan@example.com", "312-555-0009",
            DealType.BUY, 400000
        )
        self.lead_id = lead["lead_id"]

    def test_process_payment_returns_dict(self):
        result = self.bot.process_payment(self.lead_id)
        assert isinstance(result, dict)

    def test_payment_has_id(self):
        result = self.bot.process_payment(self.lead_id)
        assert "payment_id" in result
        assert result["payment_id"].startswith("pay-")

    def test_payment_status_is_completed(self):
        result = self.bot.process_payment(self.lead_id)
        assert result["status"] == "completed"

    def test_payment_amount_matches_tier_fee(self):
        result = self.bot.process_payment(self.lead_id)
        assert result["amount"] == SERVICE_FEES[Tier.FREE.value]

    def test_payment_via_paypal(self):
        result = self.bot.process_payment(
            self.lead_id, provider=PaymentProvider.PAYPAL
        )
        assert result["provider"] == "paypal"

    def test_payment_unknown_lead_raises(self):
        with pytest.raises(HomeBuyerBotError):
            self.bot.process_payment("lead-nonexistent")

    def test_get_payment(self):
        pay = self.bot.process_payment(self.lead_id)
        fetched = self.bot.get_payment(pay["payment_id"])
        assert fetched["payment_id"] == pay["payment_id"]

    def test_get_unknown_payment_raises(self):
        with pytest.raises(HomeBuyerBotError):
            self.bot.get_payment("pay-nonexistent")

    def test_refund_completed_payment(self):
        pay = self.bot.process_payment(self.lead_id)
        refunded = self.bot.refund_payment(pay["payment_id"])
        assert refunded["status"] == "refunded"

    def test_refund_already_refunded_raises(self):
        pay = self.bot.process_payment(self.lead_id)
        self.bot.refund_payment(pay["payment_id"])
        with pytest.raises(HomeBuyerBotError):
            self.bot.refund_payment(pay["payment_id"])

    def test_pro_tier_has_lower_fee(self):
        assert SERVICE_FEES[Tier.PRO.value] < SERVICE_FEES[Tier.FREE.value]

    def test_enterprise_tier_has_lowest_fee(self):
        assert SERVICE_FEES[Tier.ENTERPRISE.value] < SERVICE_FEES[Tier.PRO.value]


# ---------------------------------------------------------------------------
# Revenue summary
# ---------------------------------------------------------------------------


class TestRevenueSummary:
    def setup_method(self):
        self.bot = HomeBuyerBot(tier=Tier.FREE)

    def test_empty_revenue_summary(self):
        summary = self.bot.revenue_summary()
        assert summary["total_revenue_usd"] == 0.0
        assert summary["total_payments"] == 0

    def test_revenue_accumulates(self):
        for i in range(3):
            lead = self.bot.submit_lead(
                f"User{i}", f"u{i}@ex.com", "312-000-0000",
                DealType.BUY, 200000
            )
            self.bot.process_payment(lead["lead_id"])
        summary = self.bot.revenue_summary()
        expected = SERVICE_FEES[Tier.FREE.value] * 3
        assert summary["total_revenue_usd"] == pytest.approx(expected)
        assert summary["completed_payments"] == 3

    def test_refunded_payment_not_in_revenue(self):
        lead = self.bot.submit_lead(
            "Refund User", "r@ex.com", "312-111-1111",
            DealType.BUY, 200000
        )
        pay = self.bot.process_payment(lead["lead_id"])
        self.bot.refund_payment(pay["payment_id"])
        summary = self.bot.revenue_summary()
        assert summary["total_revenue_usd"] == 0.0


# ---------------------------------------------------------------------------
# Interaction log
# ---------------------------------------------------------------------------


class TestInteractionLog:
    def test_lead_submission_logged(self):
        bot = HomeBuyerBot()
        bot.submit_lead("A", "a@b.com", "000", DealType.BUY, 1000)
        log = bot.get_interaction_log()
        events = [entry["event"] for entry in log]
        assert "lead_submitted" in events

    def test_payment_logged(self):
        bot = HomeBuyerBot()
        lead = bot.submit_lead("B", "b@c.com", "000", DealType.RENT, 1500)
        bot.process_payment(lead["lead_id"])
        log = bot.get_interaction_log()
        events = [entry["event"] for entry in log]
        assert "payment_processed" in events


# ---------------------------------------------------------------------------
# Tier info and upgrade path
# ---------------------------------------------------------------------------


class TestTierInfo:
    def test_get_tier_info_returns_dict(self):
        bot = HomeBuyerBot()
        info = bot.get_tier_info()
        assert isinstance(info, dict)
        assert "tier" in info

    def test_upgrade_path_free_to_pro(self):
        bot = HomeBuyerBot(tier=Tier.FREE)
        path = bot.upgrade_path()
        assert path == "pro"

    def test_enterprise_has_no_upgrade(self):
        bot = HomeBuyerBot(tier=Tier.ENTERPRISE)
        assert bot.upgrade_path() is None


# ---------------------------------------------------------------------------
# run() helper
# ---------------------------------------------------------------------------


class TestRunHelper:
    def test_run_returns_dict(self):
        bot = HomeBuyerBot()
        result = bot.run()
        assert isinstance(result, dict)

    def test_run_contains_bot_name(self):
        bot = HomeBuyerBot()
        result = bot.run()
        assert result["bot"] == "HomeBuyerBot"

    def test_run_contains_tier(self):
        bot = HomeBuyerBot(tier=Tier.PRO)
        result = bot.run()
        assert result["tier"] == "pro"
