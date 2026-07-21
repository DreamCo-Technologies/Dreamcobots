from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger("dreamco.payments")


class BillingModel(str, Enum):
    ONE_TIME     = "one_time"
    SUBSCRIPTION = "subscription"
    USAGE_BASED  = "usage_based"
    FREEMIUM     = "freemium"


@dataclass
class PaymentResult:
    success:        bool
    transaction_id: Optional[str]
    amount:         float
    currency:       str
    model:          BillingModel
    description:    str
    timestamp:      str = ""
    error:          Optional[str] = None
    metadata:       Dict = None

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()
        if self.metadata is None:
            self.metadata = {}


class StripeGateway:
    """Stripe payment gateway wrapper."""

    def __init__(self):
        self.api_key = os.getenv("STRIPE_SECRET_KEY")
        self._stripe = None

    def _client(self):
        if self._stripe is None:
            try:
                import stripe
                stripe.api_key = self.api_key
                self._stripe = stripe
            except ImportError:
                raise RuntimeError("stripe package not installed. Run: pip install stripe")
        return self._stripe

    def charge(
        self,
        amount_cents: int,
        currency: str = "usd",
        description: str = "",
        customer_id: Optional[str] = None,
        payment_method_id: Optional[str] = None,
    ) -> PaymentResult:
        try:
            stripe = self._client()
            intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=currency,
                description=description,
                customer=customer_id,
                payment_method=payment_method_id,
                confirm=True if payment_method_id else False,
            )
            return PaymentResult(
                success=True,
                transaction_id=intent["id"],
                amount=amount_cents / 100,
                currency=currency,
                model=BillingModel.ONE_TIME,
                description=description,
                metadata={"stripe_intent": intent["id"]},
            )
        except Exception as e:
            logger.error(f"Stripe charge error: {e}")
            return PaymentResult(
                success=False, transaction_id=None,
                amount=amount_cents / 100, currency=currency,
                model=BillingModel.ONE_TIME, description=description,
                error=str(e),
            )

    def create_subscription(
        self,
        customer_id: str,
        price_id: str,
        trial_days: int = 0,
    ) -> PaymentResult:
        try:
            stripe = self._client()
            sub_params: Dict = {"customer": customer_id, "items": [{"price": price_id}]}
            if trial_days:
                sub_params["trial_period_days"] = trial_days
            sub = stripe.Subscription.create(**sub_params)
            return PaymentResult(
                success=True,
                transaction_id=sub["id"],
                amount=0,
                currency="usd",
                model=BillingModel.SUBSCRIPTION,
                description=f"Subscription {price_id}",
                metadata={"subscription_id": sub["id"], "status": sub["status"]},
            )
        except Exception as e:
            logger.error(f"Stripe subscription error: {e}")
            return PaymentResult(
                success=False, transaction_id=None, amount=0, currency="usd",
                model=BillingModel.SUBSCRIPTION, description="subscription failed",
                error=str(e),
            )

    def record_usage(
        self,
        subscription_item_id: str,
        quantity: int,
        timestamp: Optional[int] = None,
    ) -> PaymentResult:
        try:
            stripe = self._client()
            record = stripe.SubscriptionItem.create_usage_record(
                subscription_item_id,
                quantity=quantity,
                timestamp=timestamp or int(datetime.now(timezone.utc).timestamp()),
            )
            return PaymentResult(
                success=True,
                transaction_id=record["id"],
                amount=0,
                currency="usd",
                model=BillingModel.USAGE_BASED,
                description=f"Usage record: {quantity} units",
                metadata={"usage_record_id": record["id"]},
            )
        except Exception as e:
            logger.error(f"Stripe usage record error: {e}")
            return PaymentResult(
                success=False, transaction_id=None, amount=0, currency="usd",
                model=BillingModel.USAGE_BASED, description="usage record failed",
                error=str(e),
            )

    def create_customer(self, email: str, name: str = "", metadata: Dict = None) -> str:
        """Create a Stripe customer and return their ID."""
        stripe = self._client()
        customer = stripe.Customer.create(
            email=email,
            name=name,
            metadata=metadata or {},
        )
        return customer["id"]

    def list_invoices(self, customer_id: str, limit: int = 10) -> List[Dict]:
        stripe = self._client()
        invoices = stripe.Invoice.list(customer=customer_id, limit=limit)
        return [
            {
                "id": inv["id"],
                "amount_paid": inv["amount_paid"] / 100,
                "status": inv["status"],
                "created": datetime.fromtimestamp(inv["created"], tz=timezone.utc).isoformat(),
            }
            for inv in invoices.data
        ]


# ---------------------------------------------------------------------------
# DreamCo Payments — unified facade used by all bots
# ---------------------------------------------------------------------------
class DreamCoPayments:
    """
    Unified payments interface.
    Bots call methods here; the gateway (Stripe or mock) is abstracted away.
    """

    def __init__(self, mock: bool = False):
        self._gateway = _MockGateway() if mock or not os.getenv("STRIPE_SECRET_KEY") else StripeGateway()
        self._revenue_log: List[PaymentResult] = []
        logger.info(f"DreamCoPayments initialised ({'mock' if mock else 'live'})")

    def charge(self, amount: float, description: str = "", currency: str = "usd", **kwargs) -> PaymentResult:
        result = self._gateway.charge(
            amount_cents=int(amount * 100),
            currency=currency,
            description=description,
            **{k: v for k, v in kwargs.items() if k in ("customer_id", "payment_method_id")},
        )
        if result.success:
            self._revenue_log.append(result)
        return result

    def subscribe(self, customer_id: str, price_id: str, trial_days: int = 0) -> PaymentResult:
        return self._gateway.create_subscription(customer_id, price_id, trial_days)

    def record_usage(self, subscription_item_id: str, quantity: int) -> PaymentResult:
        return self._gateway.record_usage(subscription_item_id, quantity)

    def total_revenue(self) -> float:
        return sum(r.amount for r in self._revenue_log if r.success)

    def revenue_by_model(self) -> Dict[str, float]:
        summary: Dict[str, float] = {}
        for r in self._revenue_log:
            if r.success:
                key = r.model.value
                summary[key] = summary.get(key, 0.0) + r.amount
        return summary


class _MockGateway:
    """Mock gateway for development and testing."""

    def charge(self, amount_cents: int, currency: str = "usd", description: str = "", **kwargs) -> PaymentResult:
        logger.debug(f"[MOCK] Charged {amount_cents/100:.2f} {currency} — {description}")
        return PaymentResult(
            success=True, transaction_id=f"mock_pi_{id(description)}",
            amount=amount_cents / 100, currency=currency,
            model=BillingModel.ONE_TIME, description=description,
            metadata={"mock": True},
        )

    def create_subscription(self, customer_id: str, price_id: str, trial_days: int = 0) -> PaymentResult:
        return PaymentResult(
            success=True, transaction_id=f"mock_sub_{id(price_id)}",
            amount=0, currency="usd", model=BillingModel.SUBSCRIPTION,
            description=f"Mock sub {price_id}", metadata={"mock": True},
        )

    def record_usage(self, subscription_item_id: str, quantity: int, **kwargs) -> PaymentResult:
        return PaymentResult(
            success=True, transaction_id=f"mock_usage_{id(subscription_item_id)}",
            amount=0, currency="usd", model=BillingModel.USAGE_BASED,
            description=f"Mock usage {quantity}", metadata={"mock": True},
        )


# Singleton
_payments: Optional[DreamCoPayments] = None

def get_payments() -> DreamCoPayments:
    global _payments
    if _payments is None:
        _payments = DreamCoPayments()
    return _payments