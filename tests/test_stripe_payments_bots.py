"""
Tests for bots/real_estate_bot/stripe_payments.py and
bots/car_flipping_bot/stripe_payments.py

Covers all Stripe payment flows for real estate and car flipping bots.
"""

import sys
import os
from urllib.parse import urlparse

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

from bots.real_estate_bot.stripe_payments import (
    RealEstateStripePayments,
    REAL_ESTATE_SERVICES,
)
from bots.car_flipping_bot.stripe_payments import (
    CarFlippingStripePayments,
    CAR_FLIPPING_SERVICES,
)
from bots.stripe_integration.stripe_client import StripeClient


# ===========================================================================
# Real Estate Stripe Payments
# ===========================================================================

class TestRealEstateStripePaymentsInit:
    def test_instantiates(self):
        payments = RealEstateStripePayments()
        assert payments is not None

    def test_custom_stripe_client(self):
        client = StripeClient()
        payments = RealEstateStripePayments(stripe_client=client)
        assert payments._stripe is client


class TestRealEstateServiceSchedule:
    def test_services_defined(self):
        assert len(REAL_ESTATE_SERVICES) >= 4

    def test_listing_fee_defined(self):
        assert "listing_fee" in REAL_ESTATE_SERVICES

    def test_premium_search_defined(self):
        assert "premium_search" in REAL_ESTATE_SERVICES

    def test_investment_report_defined(self):
        assert "investment_report" in REAL_ESTATE_SERVICES

    def test_deposit_hold_defined(self):
        assert "deposit_hold" in REAL_ESTATE_SERVICES

    def test_all_services_have_amount_and_currency(self):
        for name, svc in REAL_ESTATE_SERVICES.items():
            assert "amount_cents" in svc, f"Missing amount_cents for {name}"
            assert "currency" in svc, f"Missing currency for {name}"
            assert "name" in svc, f"Missing name for {name}"


class TestRealEstateListingFeeCheckout:
    def setup_method(self):
        self.payments = RealEstateStripePayments()

    def test_returns_dict(self):
        result = self.payments.create_listing_fee_checkout(
            agent_email="agent@test.com",
            property_address="123 Main St",
            success_url="https://s.co",
            cancel_url="https://c.co",
        )
        assert isinstance(result, dict)

    def test_has_session_id(self):
        result = self.payments.create_listing_fee_checkout(
            "agent@test.com", "123 Main St", "https://s.co", "https://c.co"
        )
        assert "session_id" in result
        assert result["session_id"].startswith("cs_")

    def test_has_checkout_url(self):
        result = self.payments.create_listing_fee_checkout(
            "agent@test.com", "123 Main St", "https://s.co", "https://c.co"
        )
        assert "checkout_url" in result
        assert urlparse(result["checkout_url"]).netloc == "checkout.stripe.com"

    def test_amount_matches_schedule(self):
        result = self.payments.create_listing_fee_checkout(
            "agent@test.com", "123 Main St", "https://s.co", "https://c.co"
        )
        expected = REAL_ESTATE_SERVICES["listing_fee"]["amount_cents"] / 100
        assert result["amount_usd"] == expected

    def test_property_address_in_result(self):
        result = self.payments.create_listing_fee_checkout(
            "agent@test.com", "456 Oak Ave", "https://s.co", "https://c.co"
        )
        assert result["property_address"] == "456 Oak Ave"


class TestRealEstatePremiumSearchCheckout:
    def setup_method(self):
        self.payments = RealEstateStripePayments()

    def test_returns_dict(self):
        result = self.payments.create_premium_search_checkout(
            "buyer@test.com", "https://s.co", "https://c.co"
        )
        assert isinstance(result, dict)

    def test_has_session_id(self):
        result = self.payments.create_premium_search_checkout(
            "buyer@test.com", "https://s.co", "https://c.co"
        )
        assert result["session_id"].startswith("cs_")

    def test_correct_amount(self):
        result = self.payments.create_premium_search_checkout(
            "buyer@test.com", "https://s.co", "https://c.co"
        )
        expected = REAL_ESTATE_SERVICES["premium_search"]["amount_cents"] / 100
        assert result["amount_usd"] == expected


class TestRealEstateInvestmentReportCheckout:
    def setup_method(self):
        self.payments = RealEstateStripePayments()

    def test_returns_dict(self):
        result = self.payments.create_investment_report_checkout(
            "investor@test.com", "789 Pine Rd",
            "https://s.co", "https://c.co"
        )
        assert isinstance(result, dict)

    def test_property_address_stored(self):
        result = self.payments.create_investment_report_checkout(
            "investor@test.com", "789 Pine Rd",
            "https://s.co", "https://c.co"
        )
        assert result["property_address"] == "789 Pine Rd"


class TestRealEstateDepositIntent:
    def setup_method(self):
        self.payments = RealEstateStripePayments()

    def test_returns_dict(self):
        result = self.payments.create_deposit_payment_intent(
            "buyer@test.com", "123 Main St"
        )
        assert isinstance(result, dict)

    def test_has_payment_intent_id(self):
        result = self.payments.create_deposit_payment_intent(
            "buyer@test.com", "123 Main St"
        )
        assert result["payment_intent_id"].startswith("pi_")

    def test_has_client_secret(self):
        result = self.payments.create_deposit_payment_intent(
            "buyer@test.com", "123 Main St"
        )
        assert "client_secret" in result

    def test_default_deposit_amount(self):
        result = self.payments.create_deposit_payment_intent(
            "buyer@test.com", "123 Main St"
        )
        assert result["amount_usd"] == 500.0

    def test_custom_deposit_amount(self):
        result = self.payments.create_deposit_payment_intent(
            "buyer@test.com", "123 Main St", deposit_amount_usd=1000.0
        )
        assert result["amount_usd"] == 1000.0


class TestRealEstatePaymentLink:
    def test_create_listing_payment_link(self):
        payments = RealEstateStripePayments()
        result = payments.create_listing_payment_link()
        assert "url" in result
        assert urlparse(result["url"]).netloc == "buy.stripe.com"

    def test_listing_link_correct_amount(self):
        payments = RealEstateStripePayments()
        result = payments.create_listing_payment_link()
        expected = REAL_ESTATE_SERVICES["listing_fee"]["amount_cents"] / 100
        assert result["amount_usd"] == expected


class TestRealEstateRefund:
    def test_refund_deposit_returns_dict(self):
        payments = RealEstateStripePayments()
        result = payments.refund_deposit("pi_test_deposit")
        assert isinstance(result, dict)

    def test_refund_has_refund_id(self):
        payments = RealEstateStripePayments()
        result = payments.refund_deposit("pi_test_deposit")
        assert result["refund_id"].startswith("re_")

    def test_refund_status_succeeded(self):
        payments = RealEstateStripePayments()
        result = payments.refund_deposit("pi_test_deposit")
        assert result["status"] == "succeeded"

    def test_refund_preserves_payment_intent_id(self):
        payments = RealEstateStripePayments()
        result = payments.refund_deposit("pi_test_abc123")
        assert result["payment_intent_id"] == "pi_test_abc123"


class TestRealEstateRevenueSummary:
    def test_revenue_summary_returns_dict(self):
        payments = RealEstateStripePayments()
        result = payments.get_revenue_summary()
        assert "balance" in result
        assert "recent_payouts" in result

    def test_balance_has_available(self):
        payments = RealEstateStripePayments()
        result = payments.get_revenue_summary()
        assert "available" in result["balance"]


# ===========================================================================
# Car Flipping Stripe Payments
# ===========================================================================

class TestCarFlippingStripePaymentsInit:
    def test_instantiates(self):
        payments = CarFlippingStripePayments()
        assert payments is not None

    def test_custom_stripe_client(self):
        client = StripeClient()
        payments = CarFlippingStripePayments(stripe_client=client)
        assert payments._stripe is client


class TestCarFlippingServiceSchedule:
    def test_services_defined(self):
        assert len(CAR_FLIPPING_SERVICES) >= 4

    def test_valuation_report_defined(self):
        assert "valuation_report" in CAR_FLIPPING_SERVICES

    def test_premium_listing_defined(self):
        assert "premium_listing" in CAR_FLIPPING_SERVICES

    def test_purchase_deposit_defined(self):
        assert "purchase_deposit" in CAR_FLIPPING_SERVICES

    def test_auction_entry_defined(self):
        assert "auction_entry" in CAR_FLIPPING_SERVICES

    def test_all_services_have_required_keys(self):
        for name, svc in CAR_FLIPPING_SERVICES.items():
            assert "amount_cents" in svc, f"Missing amount_cents for {name}"
            assert "currency" in svc
            assert "name" in svc


class TestCarFlippingValuationCheckout:
    def setup_method(self):
        self.payments = CarFlippingStripePayments()

    def test_returns_dict(self):
        result = self.payments.create_valuation_checkout(
            "buyer@test.com", "2018 Toyota Camry",
            "https://s.co", "https://c.co"
        )
        assert isinstance(result, dict)

    def test_has_session_id(self):
        result = self.payments.create_valuation_checkout(
            "buyer@test.com", "2018 Toyota Camry",
            "https://s.co", "https://c.co"
        )
        assert result["session_id"].startswith("cs_")

    def test_correct_amount(self):
        result = self.payments.create_valuation_checkout(
            "buyer@test.com", "2018 Toyota Camry",
            "https://s.co", "https://c.co"
        )
        expected = CAR_FLIPPING_SERVICES["valuation_report"]["amount_cents"] / 100
        assert result["amount_usd"] == expected

    def test_car_details_in_result(self):
        result = self.payments.create_valuation_checkout(
            "buyer@test.com", "2019 Honda Civic",
            "https://s.co", "https://c.co"
        )
        assert result["car_details"] == "2019 Honda Civic"


class TestCarFlippingPremiumListingCheckout:
    def setup_method(self):
        self.payments = CarFlippingStripePayments()

    def test_returns_dict(self):
        result = self.payments.create_premium_listing_checkout(
            "seller@test.com", "2020 Ford F-150",
            "https://s.co", "https://c.co"
        )
        assert isinstance(result, dict)

    def test_has_checkout_url(self):
        result = self.payments.create_premium_listing_checkout(
            "seller@test.com", "2020 Ford F-150",
            "https://s.co", "https://c.co"
        )
        assert "checkout_url" in result


class TestCarFlippingAuctionEntryCheckout:
    def test_returns_dict(self):
        payments = CarFlippingStripePayments()
        result = payments.create_auction_entry_checkout(
            "bidder@test.com", "2017 Jeep Wrangler",
            "https://s.co", "https://c.co"
        )
        assert isinstance(result, dict)

    def test_correct_amount(self):
        payments = CarFlippingStripePayments()
        result = payments.create_auction_entry_checkout(
            "bidder@test.com", "2017 Jeep Wrangler",
            "https://s.co", "https://c.co"
        )
        expected = CAR_FLIPPING_SERVICES["auction_entry"]["amount_cents"] / 100
        assert result["amount_usd"] == expected


class TestCarFlippingDepositIntent:
    def setup_method(self):
        self.payments = CarFlippingStripePayments()

    def test_returns_dict(self):
        result = self.payments.create_purchase_deposit_intent("buyer@test.com", "c001")
        assert isinstance(result, dict)

    def test_has_payment_intent_id(self):
        result = self.payments.create_purchase_deposit_intent("buyer@test.com", "c001")
        assert result["payment_intent_id"].startswith("pi_")

    def test_has_client_secret(self):
        result = self.payments.create_purchase_deposit_intent("buyer@test.com", "c001")
        assert "client_secret" in result

    def test_default_deposit_250(self):
        result = self.payments.create_purchase_deposit_intent("buyer@test.com", "c001")
        assert result["amount_usd"] == 250.0

    def test_custom_deposit_amount(self):
        result = self.payments.create_purchase_deposit_intent(
            "buyer@test.com", "c001", deposit_amount_usd=500.0
        )
        assert result["amount_usd"] == 500.0

    def test_car_id_stored(self):
        result = self.payments.create_purchase_deposit_intent("buyer@test.com", "c003")
        assert result["car_id"] == "c003"


class TestCarFlippingPaymentLinks:
    def test_valuation_payment_link(self):
        payments = CarFlippingStripePayments()
        result = payments.create_valuation_payment_link()
        assert "url" in result
        assert urlparse(result["url"]).netloc == "buy.stripe.com"

    def test_listing_payment_link(self):
        payments = CarFlippingStripePayments()
        result = payments.create_listing_payment_link()
        assert "url" in result
        assert result["link_id"].startswith("plink_")


class TestCarFlippingRefund:
    def test_refund_deposit_returns_dict(self):
        payments = CarFlippingStripePayments()
        result = payments.refund_deposit("pi_car_deposit_test")
        assert isinstance(result, dict)

    def test_refund_status_succeeded(self):
        payments = CarFlippingStripePayments()
        result = payments.refund_deposit("pi_car_deposit_test")
        assert result["status"] == "succeeded"

    def test_refund_preserves_pi_id(self):
        payments = CarFlippingStripePayments()
        result = payments.refund_deposit("pi_abc_car_test")
        assert result["payment_intent_id"] == "pi_abc_car_test"


class TestCarFlippingRevenueSummary:
    def test_revenue_summary_returns_dict(self):
        payments = CarFlippingStripePayments()
        result = payments.get_revenue_summary()
        assert "balance" in result
        assert "recent_payouts" in result
