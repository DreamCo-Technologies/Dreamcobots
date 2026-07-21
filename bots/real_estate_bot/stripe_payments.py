"""
Real Estate Bot — Stripe Payments Module

Handles Stripe payment flows for real estate bot services:
  - Listing fee checkout sessions
  - Premium search payment links
  - Deposit collection for property transactions
  - Subscription management for ongoing market intelligence

All API credentials are loaded from environment variables.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from typing import Optional
from bots.stripe_integration.stripe_client import StripeClient, StripeClientError
from framework import GlobalAISourcesFlow  # noqa: F401


# ---------------------------------------------------------------------------
# Service fee schedule
# ---------------------------------------------------------------------------

REAL_ESTATE_SERVICES = {
    "listing_fee": {
        "name": "Property Listing Fee",
        "amount_cents": 9900,
        "currency": "usd",
        "description": "List your property on the Dreamcobots marketplace.",
    },
    "premium_search": {
        "name": "Premium Market Search (30 days)",
        "amount_cents": 4900,
        "currency": "usd",
        "description": "Unlimited location searches and market trend reports for 30 days.",
    },
    "investment_report": {
        "name": "Investment Analysis Report",
        "amount_cents": 19900,
        "currency": "usd",
        "description": "Full AI-powered investment report for a selected property.",
    },
    "deposit_hold": {
        "name": "Transaction Deposit (Refundable)",
        "amount_cents": 50000,
        "currency": "usd",
        "description": "Refundable deposit to hold a property during due diligence.",
    },
}


class RealEstateStripePayments:
    """
    Stripe payment handler for the Real Estate Bot.

    Parameters
    ----------
    stripe_client : StripeClient | None
        Optional injected StripeClient (useful for testing).
    """

    def __init__(self, stripe_client: Optional[StripeClient] = None) -> None:
        self._stripe = stripe_client or StripeClient()

    # ------------------------------------------------------------------
    # Checkout sessions
    # ------------------------------------------------------------------

    def create_listing_fee_checkout(
        self,
        agent_email: str,
        property_address: str,
        success_url: str,
        cancel_url: str,
    ) -> dict:
        """
        Create a Stripe Checkout Session for a property listing fee.

        Parameters
        ----------
        agent_email : str
            Agent's or seller's email.
        property_address : str
            Property address (stored in metadata).
        success_url : str
            Redirect URL after payment.
        cancel_url : str
            Redirect URL on cancel.

        Returns
        -------
        dict
            ``session_id``, ``checkout_url``, ``amount_usd``, ``service``.
        """
        svc = REAL_ESTATE_SERVICES["listing_fee"]
        session = self._stripe.create_checkout_session(
            amount_cents=svc["amount_cents"],
            currency=svc["currency"],
            product_name=svc["name"],
            success_url=success_url,
            cancel_url=cancel_url,
            customer_email=agent_email,
            metadata={
                "bot": "real_estate_bot",
                "service": "listing_fee",
                "property_address": property_address,
            },
        )
        return {
            "session_id": session["id"],
            "checkout_url": session["url"],
            "amount_usd": svc["amount_cents"] / 100,
            "service": svc["name"],
            "property_address": property_address,
        }

    def create_premium_search_checkout(
        self,
        customer_email: str,
        success_url: str,
        cancel_url: str,
    ) -> dict:
        """
        Create a Checkout Session for premium market search access.

        Returns
        -------
        dict
            ``session_id``, ``checkout_url``, ``amount_usd``, ``service``.
        """
        svc = REAL_ESTATE_SERVICES["premium_search"]
        session = self._stripe.create_checkout_session(
            amount_cents=svc["amount_cents"],
            currency=svc["currency"],
            product_name=svc["name"],
            success_url=success_url,
            cancel_url=cancel_url,
            customer_email=customer_email,
            metadata={"bot": "real_estate_bot", "service": "premium_search"},
        )
        return {
            "session_id": session["id"],
            "checkout_url": session["url"],
            "amount_usd": svc["amount_cents"] / 100,
            "service": svc["name"],
        }

    def create_investment_report_checkout(
        self,
        customer_email: str,
        property_address: str,
        success_url: str,
        cancel_url: str,
    ) -> dict:
        """
        Create a Checkout Session for an AI investment analysis report.

        Returns
        -------
        dict
            ``session_id``, ``checkout_url``, ``amount_usd``, ``service``.
        """
        svc = REAL_ESTATE_SERVICES["investment_report"]
        session = self._stripe.create_checkout_session(
            amount_cents=svc["amount_cents"],
            currency=svc["currency"],
            product_name=svc["name"],
            success_url=success_url,
            cancel_url=cancel_url,
            customer_email=customer_email,
            metadata={
                "bot": "real_estate_bot",
                "service": "investment_report",
                "property_address": property_address,
            },
        )
        return {
            "session_id": session["id"],
            "checkout_url": session["url"],
            "amount_usd": svc["amount_cents"] / 100,
            "service": svc["name"],
            "property_address": property_address,
        }

    def create_deposit_payment_intent(
        self,
        customer_email: str,
        property_address: str,
        deposit_amount_usd: float = 500.00,
    ) -> dict:
        """
        Create a PaymentIntent for a refundable transaction deposit.

        Parameters
        ----------
        customer_email : str
            Buyer's email.
        property_address : str
            Property being reserved.
        deposit_amount_usd : float
            Deposit amount in USD (default $500).

        Returns
        -------
        dict
            ``payment_intent_id``, ``client_secret``, ``amount_usd``, ``status``.
        """
        amount_cents = int(deposit_amount_usd * 100)
        intent = self._stripe.create_payment_intent(
            amount_cents=amount_cents,
            currency="usd",
            metadata={
                "bot": "real_estate_bot",
                "service": "deposit_hold",
                "property_address": property_address,
                "customer_email": customer_email,
            },
        )
        return {
            "payment_intent_id": intent["id"],
            "client_secret": intent["client_secret"],
            "amount_usd": deposit_amount_usd,
            "status": intent["status"],
            "property_address": property_address,
        }

    # ------------------------------------------------------------------
    # Payment links
    # ------------------------------------------------------------------

    def create_listing_payment_link(self) -> dict:
        """
        Create a shareable Stripe Payment Link for property listing fees.

        Returns
        -------
        dict
            ``link_id``, ``url``, ``amount_usd``, ``service``.
        """
        svc = REAL_ESTATE_SERVICES["listing_fee"]
        link = self._stripe.create_payment_link(
            amount_cents=svc["amount_cents"],
            currency=svc["currency"],
            product_name=svc["name"],
            metadata={"bot": "real_estate_bot", "service": "listing_fee"},
        )
        return {
            "link_id": link["id"],
            "url": link["url"],
            "amount_usd": svc["amount_cents"] / 100,
            "service": svc["name"],
        }

    # ------------------------------------------------------------------
    # Refunds
    # ------------------------------------------------------------------

    def refund_deposit(self, payment_intent_id: str) -> dict:
        """
        Refund a deposit after transaction completion or cancellation.

        Returns
        -------
        dict
            ``refund_id``, ``status``, ``payment_intent_id``.
        """
        refund = self._stripe.refund_payment(
            payment_intent_id=payment_intent_id,
            reason="requested_by_customer",
        )
        return {
            "refund_id": refund["id"],
            "status": refund["status"],
            "payment_intent_id": payment_intent_id,
        }

    # ------------------------------------------------------------------
    # Balance / payouts
    # ------------------------------------------------------------------

    def get_revenue_summary(self) -> dict:
        """
        Return Stripe account balance and recent payouts.

        Returns
        -------
        dict
            ``balance``, ``recent_payouts``.
        """
        balance = self._stripe.get_balance()
        payouts = self._stripe.list_payouts(limit=5)
        return {"balance": balance, "recent_payouts": payouts}
