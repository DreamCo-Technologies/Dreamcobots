"""
DreamCo Payments Client — Stripe Integration

Manages SaaS subscriptions and one-time charges.  When ``STRIPE_SECRET_KEY``
is absent the client operates in mock mode so no real charges are made
during testing.

Usage
-----
    client = PaymentsClient()
    sub    = client.create_subscription("user@example.com", "PRO")
    charge = client.create_charge("user@example.com", 4999, "One-time setup fee")
"""

from __future__ import annotations

import os
import sys
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from framework import GlobalAISourcesFlow  # noqa: F401


# ---------------------------------------------------------------------------
# Pricing tiers  (amounts in USD cents)
# ---------------------------------------------------------------------------

SUBSCRIPTION_PLANS = {
    "FREE": {"price_cents": 0, "price_id": "price_free"},
    "PRO": {"price_cents": 2_900, "price_id": "price_pro_29"},
    "SCALE": {"price_cents": 9_900, "price_id": "price_scale_99"},
    "ENTERPRISE": {"price_cents": 49_900, "price_id": "price_ent_499"},
}


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class PaymentRecord:
    record_id: str
    email: str
    amount_cents: int
    currency: str
    description: str
    status: str  # "succeeded" | "mock" | "failed"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return {
            "record_id": self.record_id,
            "email": self.email,
            "amount_cents": self.amount_cents,
            "amount_usd": round(self.amount_cents / 100, 2),
            "currency": self.currency,
            "description": self.description,
            "status": self.status,
            "created_at": self.created_at,
        }


@dataclass
class SubscriptionRecord:
    subscription_id: str
    customer_id: str
    email: str
    plan: str
    price_cents: int
    status: str  # "active" | "mock" | "failed"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return {
            "subscription_id": self.subscription_id,
            "customer_id": self.customer_id,
            "email": self.email,
            "plan": self.plan,
            "price_usd": round(self.price_cents / 100, 2),
            "status": self.status,
            "created_at": self.created_at,
        }


# ---------------------------------------------------------------------------
# PaymentsClient
# ---------------------------------------------------------------------------


class PaymentsClient:
    """
    Stripe-backed (or mock) payments client for DreamCo subscriptions.

    Parameters
    ----------
    api_key : Stripe secret key (default: env STRIPE_SECRET_KEY).
    mock    : Force mock mode regardless of credentials.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        mock: bool = False,
    ) -> None:
        self._api_key = api_key or os.environ.get("STRIPE_SECRET_KEY", "")
        self._mock = mock or not self._api_key
        self._payments: List[PaymentRecord] = []
        self._subscriptions: List[SubscriptionRecord] = []

    @property
    def is_mock(self) -> bool:
        return self._mock

    # ------------------------------------------------------------------
    # Subscriptions
    # ------------------------------------------------------------------

    def create_subscription(self, email: str, plan: str = "PRO") -> SubscriptionRecord:
        """
        Create a recurring subscription for *email* at the given *plan*.

        In mock mode returns a local record without hitting Stripe.
        """
        plan_upper = plan.upper()
        if plan_upper not in SUBSCRIPTION_PLANS:
            raise ValueError(f"Unknown plan '{plan}'. Valid: {list(SUBSCRIPTION_PLANS)}")

        plan_info = SUBSCRIPTION_PLANS[plan_upper]

        if self._mock:
            record = SubscriptionRecord(
                subscription_id=f"sub_mock_{uuid.uuid4().hex[:8]}",
                customer_id=f"cus_mock_{uuid.uuid4().hex[:8]}",
                email=email,
                plan=plan_upper,
                price_cents=plan_info["price_cents"],
                status="mock",
            )
        else:
            record = self._stripe_subscribe(email, plan_upper, plan_info)

        self._subscriptions.append(record)
        return record

    def cancel_subscription(self, subscription_id: str) -> dict:
        """Cancel a subscription by ID (mock or live)."""
        for sub in self._subscriptions:
            if sub.subscription_id == subscription_id:
                sub.status = "cancelled"
                return {"subscription_id": subscription_id, "status": "cancelled"}
        return {"error": f"Subscription '{subscription_id}' not found"}

    # ------------------------------------------------------------------
    # One-time charges
    # ------------------------------------------------------------------

    def create_charge(
        self, email: str, amount_cents: int, description: str = "", currency: str = "usd"
    ) -> PaymentRecord:
        """Create a one-time charge (mock or live via Stripe)."""
        if self._mock:
            record = PaymentRecord(
                record_id=f"ch_mock_{uuid.uuid4().hex[:8]}",
                email=email,
                amount_cents=amount_cents,
                currency=currency,
                description=description,
                status="mock",
            )
        else:
            record = self._stripe_charge(email, amount_cents, description, currency)

        self._payments.append(record)
        return record

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    def get_subscriptions(self) -> List[dict]:
        return [s.to_dict() for s in self._subscriptions]

    def get_payments(self) -> List[dict]:
        return [p.to_dict() for p in self._payments]

    def get_revenue_summary(self) -> dict:
        total_mrr = sum(
            s.price_cents
            for s in self._subscriptions
            if s.status in ("active", "mock")
        )
        total_one_time = sum(
            p.amount_cents
            for p in self._payments
            if p.status in ("succeeded", "mock")
        )
        return {
            "active_subscriptions": len(
                [s for s in self._subscriptions if s.status in ("active", "mock")]
            ),
            "mrr_cents": total_mrr,
            "mrr_usd": round(total_mrr / 100, 2),
            "one_time_revenue_cents": total_one_time,
            "one_time_revenue_usd": round(total_one_time / 100, 2),
            "total_revenue_usd": round((total_mrr + total_one_time) / 100, 2),
        }

    # ------------------------------------------------------------------
    # Stripe internals (only reached when not mock)
    # ------------------------------------------------------------------

    def _stripe_subscribe(self, email: str, plan: str, plan_info: dict) -> SubscriptionRecord:  # pragma: no cover
        import stripe  # type: ignore[import]

        stripe.api_key = self._api_key
        customer = stripe.Customer.create(email=email)
        subscription = stripe.Subscription.create(
            customer=customer.id,
            items=[{"price": plan_info["price_id"]}],
        )
        return SubscriptionRecord(
            subscription_id=subscription.id,
            customer_id=customer.id,
            email=email,
            plan=plan,
            price_cents=plan_info["price_cents"],
            status="active",
        )

    def _stripe_charge(
        self, email: str, amount_cents: int, description: str, currency: str
    ) -> PaymentRecord:  # pragma: no cover
        import stripe  # type: ignore[import]

        stripe.api_key = self._api_key
        customer = stripe.Customer.create(email=email)
        charge = stripe.Charge.create(
            amount=amount_cents,
            currency=currency,
            customer=customer.id,
            description=description,
        )
        return PaymentRecord(
            record_id=charge.id,
            email=email,
            amount_cents=amount_cents,
            currency=currency,
            description=description,
            status="succeeded",
        )
