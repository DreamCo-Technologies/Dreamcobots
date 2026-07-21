"""
Car Flipping Bot — Stripe Payments Module

Handles Stripe payment flows for car flipping bot services:
  - Service fee checkout sessions for premium car valuations
  - Deposit collection for car purchase transactions
  - Shareable payment links for buyer/seller interactions
  - Premium listing fees for auction-style car listings

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

CAR_FLIPPING_SERVICES = {
    "valuation_report": {
        "name": "Professional Car Valuation Report",
        "amount_cents": 2900,
        "currency": "usd",
        "description": "Detailed market valuation with flip profit analysis.",
    },
    "premium_listing": {
        "name": "Premium Car Listing (30 days)",
        "amount_cents": 4900,
        "currency": "usd",
        "description": "Featured listing with priority placement and analytics.",
    },
    "purchase_deposit": {
        "name": "Car Purchase Deposit (Refundable)",
        "amount_cents": 25000,
        "currency": "usd",
        "description": "Refundable deposit to reserve a vehicle during inspection.",
    },
    "auction_entry": {
        "name": "Auction Entry Fee",
        "amount_cents": 9900,
        "currency": "usd",
        "description": "Entry fee to list or bid on a vehicle in the Dreamcobots auction.",
    },
    "full_purchase": {
        "name": "Car Purchase Transaction Fee (1%)",
        "amount_cents": 10000,
        "currency": "usd",
        "description": "1% platform fee on completed car sale (charged separately).",
    },
}


class CarFlippingStripePayments:
    """
    Stripe payment handler for the Car Flipping Bot.

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

    def create_valuation_checkout(
        self,
        customer_email: str,
        car_details: str,
        success_url: str,
        cancel_url: str,
    ) -> dict:
        """
        Create a Checkout Session for a professional car valuation report.

        Parameters
        ----------
        customer_email : str
            Buyer's/seller's email.
        car_details : str
            Brief car description (e.g. ``"2018 Toyota Camry 72k miles"``).
        success_url : str
            Redirect URL after payment.
        cancel_url : str
            Redirect URL on cancel.

        Returns
        -------
        dict
            ``session_id``, ``checkout_url``, ``amount_usd``, ``service``.
        """
        svc = CAR_FLIPPING_SERVICES["valuation_report"]
        session = self._stripe.create_checkout_session(
            amount_cents=svc["amount_cents"],
            currency=svc["currency"],
            product_name=svc["name"],
            success_url=success_url,
            cancel_url=cancel_url,
            customer_email=customer_email,
            metadata={
                "bot": "car_flipping_bot",
                "service": "valuation_report",
                "car_details": car_details,
            },
        )
        return {
            "session_id": session["id"],
            "checkout_url": session["url"],
            "amount_usd": svc["amount_cents"] / 100,
            "service": svc["name"],
            "car_details": car_details,
        }

    def create_premium_listing_checkout(
        self,
        seller_email: str,
        car_details: str,
        success_url: str,
        cancel_url: str,
    ) -> dict:
        """
        Create a Checkout Session for a premium car listing.

        Returns
        -------
        dict
            ``session_id``, ``checkout_url``, ``amount_usd``, ``service``.
        """
        svc = CAR_FLIPPING_SERVICES["premium_listing"]
        session = self._stripe.create_checkout_session(
            amount_cents=svc["amount_cents"],
            currency=svc["currency"],
            product_name=svc["name"],
            success_url=success_url,
            cancel_url=cancel_url,
            customer_email=seller_email,
            metadata={
                "bot": "car_flipping_bot",
                "service": "premium_listing",
                "car_details": car_details,
            },
        )
        return {
            "session_id": session["id"],
            "checkout_url": session["url"],
            "amount_usd": svc["amount_cents"] / 100,
            "service": svc["name"],
            "car_details": car_details,
        }

    def create_auction_entry_checkout(
        self,
        participant_email: str,
        car_details: str,
        success_url: str,
        cancel_url: str,
    ) -> dict:
        """
        Create a Checkout Session for an auction entry fee.

        Returns
        -------
        dict
            ``session_id``, ``checkout_url``, ``amount_usd``, ``service``.
        """
        svc = CAR_FLIPPING_SERVICES["auction_entry"]
        session = self._stripe.create_checkout_session(
            amount_cents=svc["amount_cents"],
            currency=svc["currency"],
            product_name=svc["name"],
            success_url=success_url,
            cancel_url=cancel_url,
            customer_email=participant_email,
            metadata={
                "bot": "car_flipping_bot",
                "service": "auction_entry",
                "car_details": car_details,
            },
        )
        return {
            "session_id": session["id"],
            "checkout_url": session["url"],
            "amount_usd": svc["amount_cents"] / 100,
            "service": svc["name"],
        }

    # ------------------------------------------------------------------
    # Deposit / payment intents
    # ------------------------------------------------------------------

    def create_purchase_deposit_intent(
        self,
        buyer_email: str,
        car_id: str,
        deposit_amount_usd: float = 250.00,
    ) -> dict:
        """
        Create a PaymentIntent for a refundable purchase deposit.

        Parameters
        ----------
        buyer_email : str
            Buyer's email address.
        car_id : str
            Internal car identifier (e.g. ``"c001"``).
        deposit_amount_usd : float
            Deposit amount in USD (default $250).

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
                "bot": "car_flipping_bot",
                "service": "purchase_deposit",
                "car_id": car_id,
                "buyer_email": buyer_email,
            },
        )
        return {
            "payment_intent_id": intent["id"],
            "client_secret": intent["client_secret"],
            "amount_usd": deposit_amount_usd,
            "status": intent["status"],
            "car_id": car_id,
        }

    # ------------------------------------------------------------------
    # Payment links
    # ------------------------------------------------------------------

    def create_valuation_payment_link(self) -> dict:
        """
        Create a shareable Stripe Payment Link for car valuation reports.

        Returns
        -------
        dict
            ``link_id``, ``url``, ``amount_usd``, ``service``.
        """
        svc = CAR_FLIPPING_SERVICES["valuation_report"]
        link = self._stripe.create_payment_link(
            amount_cents=svc["amount_cents"],
            currency=svc["currency"],
            product_name=svc["name"],
            metadata={"bot": "car_flipping_bot", "service": "valuation_report"},
        )
        return {
            "link_id": link["id"],
            "url": link["url"],
            "amount_usd": svc["amount_cents"] / 100,
            "service": svc["name"],
        }

    def create_listing_payment_link(self) -> dict:
        """
        Create a shareable Stripe Payment Link for premium car listings.

        Returns
        -------
        dict
            ``link_id``, ``url``, ``amount_usd``, ``service``.
        """
        svc = CAR_FLIPPING_SERVICES["premium_listing"]
        link = self._stripe.create_payment_link(
            amount_cents=svc["amount_cents"],
            currency=svc["currency"],
            product_name=svc["name"],
            metadata={"bot": "car_flipping_bot", "service": "premium_listing"},
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

    def refund_deposit(
        self,
        payment_intent_id: str,
        reason: str = "requested_by_customer",
    ) -> dict:
        """
        Refund a purchase deposit.

        Returns
        -------
        dict
            ``refund_id``, ``status``, ``payment_intent_id``.
        """
        refund = self._stripe.refund_payment(
            payment_intent_id=payment_intent_id,
            reason=reason,
        )
        return {
            "refund_id": refund["id"],
            "status": refund["status"],
            "payment_intent_id": payment_intent_id,
        }

    # ------------------------------------------------------------------
    # Revenue summary
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
