"""
DreamCo Payments — Payment Processor

Handles payment processing, subscriptions, currency conversion, recurring
billing, refunds, and transaction history.  All operations are mocked; no
real money or external APIs are involved.

Supported currencies: USD, EUR, GBP, CAD, AUD, JPY, MXN
"""

import uuid
import datetime
from typing import Optional

from bots.dreamco_payments.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    FEATURE_PAYMENT_PROCESSING,
    FEATURE_BASIC_SUBSCRIPTIONS,
    FEATURE_CURRENCY_CONVERSION,
    FEATURE_RECURRING_BILLING,
    FEATURE_REFUNDS,
)
from framework import GlobalAISourcesFlow  # noqa: F401


class PaymentTierError(Exception):
    """Raised when a payment feature is not available on the current tier."""


SUPPORTED_CURRENCIES = {"USD", "EUR", "GBP", "CAD", "AUD", "JPY", "MXN"}

# Mock exchange rates relative to USD
_EXCHANGE_RATES: dict[str, float] = {
    "USD": 1.0,
    "EUR": 0.92,
    "GBP": 0.79,
    "CAD": 1.36,
    "AUD": 1.53,
    "JPY": 149.50,
    "MXN": 17.15,
}


class PaymentProcessor:
    """
    Tier-aware payment processor for DreamCo Payments.

    Parameters
    ----------
    tier : Tier
        Subscription tier controlling feature access.
    """

    def __init__(self, tier: Tier = Tier.STARTER) -> None:
        self.tier = tier
        self.config: TierConfig = get_tier_config(tier)
        self._transactions: dict[str, dict] = {}
        self._subscriptions: dict[str, dict] = {}

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _require_feature(self, feature: str) -> None:
        """Raise PaymentTierError if *feature* is not available on this tier."""
        if not self.config.has_feature(feature):
            raise PaymentTierError(
                f"Feature '{feature}' is not available on the "
                f"{self.config.name} tier.  Please upgrade."
            )

    @staticmethod
    def _new_id(prefix: str = "txn") -> str:
        return f"{prefix}_{uuid.uuid4().hex[:12]}"

    @staticmethod
    def _now_iso() -> str:
        return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def _validate_currency(self, currency: str) -> None:
        if currency.upper() not in SUPPORTED_CURRENCIES:
            raise ValueError(
                f"Unsupported currency '{currency}'.  "
                f"Supported: {sorted(SUPPORTED_CURRENCIES)}"
            )

    # ------------------------------------------------------------------
    # Payment processing
    # ------------------------------------------------------------------

    def process_payment(
        self,
        amount: float,
        currency: str,
        payment_method: str,
        customer_id: str,
    ) -> dict:
        """
        Process a one-time payment.

        Parameters
        ----------
        amount : float
            Payment amount (positive number).
        currency : str
            ISO 4217 currency code (e.g. "USD").
        payment_method : str
            Payment method identifier (e.g. "card_visa_4242").
        customer_id : str
            Unique customer identifier.

        Returns
        -------
        dict
            Transaction result containing status, transaction_id, amount, etc.
        """
        self._require_feature(FEATURE_PAYMENT_PROCESSING)
        self._validate_currency(currency)

        if amount <= 0:
            raise ValueError("amount must be positive.")

        transaction_id = self._new_id("txn")
        record = {
            "status": "success",
            "transaction_id": transaction_id,
            "amount": round(amount, 2),
            "currency": currency.upper(),
            "payment_method": payment_method,
            "customer_id": customer_id,
            "created_at": self._now_iso(),
            "tier": self.tier.value,
        }
        self._transactions[transaction_id] = record
        return record

    # ------------------------------------------------------------------
    # Subscriptions
    # ------------------------------------------------------------------

    def create_subscription(
        self,
        customer_id: str,
        plan_id: str,
        amount: float,
        currency: str,
        interval: str = "monthly",
    ) -> dict:
        """
        Create a subscription for a customer.

        Parameters
        ----------
        customer_id : str
            Unique customer identifier.
        plan_id : str
            Subscription plan identifier.
        amount : float
            Recurring charge amount.
        currency : str
            ISO 4217 currency code.
        interval : str
            Billing interval: 'monthly', 'yearly', or 'weekly'.

        Returns
        -------
        dict
            Subscription details.
        """
        self._require_feature(FEATURE_BASIC_SUBSCRIPTIONS)
        self._validate_currency(currency)

        if interval not in {"monthly", "yearly", "weekly"}:
            raise ValueError(f"Invalid interval '{interval}'.")

        sub_id = self._new_id("sub")
        record = {
            "subscription_id": sub_id,
            "customer_id": customer_id,
            "plan_id": plan_id,
            "amount": round(amount, 2),
            "currency": currency.upper(),
            "interval": interval,
            "status": "active",
            "created_at": self._now_iso(),
            "tier": self.tier.value,
        }
        self._subscriptions[sub_id] = record
        return record

    def cancel_subscription(self, subscription_id: str) -> dict:
        """
        Cancel an existing subscription.

        Parameters
        ----------
        subscription_id : str
            The subscription to cancel.

        Returns
        -------
        dict
            Updated subscription record with status 'cancelled'.
        """
        self._require_feature(FEATURE_BASIC_SUBSCRIPTIONS)

        if subscription_id not in self._subscriptions:
            raise KeyError(f"Subscription '{subscription_id}' not found.")

        self._subscriptions[subscription_id]["status"] = "cancelled"
        self._subscriptions[subscription_id]["cancelled_at"] = self._now_iso()
        return dict(self._subscriptions[subscription_id])

    # ------------------------------------------------------------------
    # Currency conversion  (GROWTH+)
    # ------------------------------------------------------------------

    def convert_currency(
        self,
        amount: float,
        from_currency: str,
        to_currency: str,
    ) -> dict:
        """
        Convert an amount between supported currencies.

        Requires GROWTH or ENTERPRISE tier.

        Parameters
        ----------
        amount : float
            Amount to convert.
        from_currency : str
            Source ISO 4217 currency code.
        to_currency : str
            Target ISO 4217 currency code.

        Returns
        -------
        dict
            Conversion result with converted_amount and exchange rate.
        """
        self._require_feature(FEATURE_CURRENCY_CONVERSION)
        self._validate_currency(from_currency)
        self._validate_currency(to_currency)

        from_rate = _EXCHANGE_RATES[from_currency.upper()]
        to_rate = _EXCHANGE_RATES[to_currency.upper()]
        rate = to_rate / from_rate
        converted = round(amount * rate, 4)

        return {
            "original_amount": amount,
            "from_currency": from_currency.upper(),
            "converted_amount": converted,
            "to_currency": to_currency.upper(),
            "rate": round(rate, 6),
            "converted_at": self._now_iso(),
        }

    # ------------------------------------------------------------------
    # Recurring billing  (GROWTH+)
    # ------------------------------------------------------------------

    def process_recurring_billing(self, subscription_id: str) -> dict:
        """
        Execute a recurring billing cycle for an active subscription.

        Requires GROWTH or ENTERPRISE tier.

        Parameters
        ----------
        subscription_id : str
            The subscription to bill.

        Returns
        -------
        dict
            New transaction record for this billing cycle.
        """
        self._require_feature(FEATURE_RECURRING_BILLING)

        if subscription_id not in self._subscriptions:
            raise KeyError(f"Subscription '{subscription_id}' not found.")

        sub = self._subscriptions[subscription_id]
        if sub["status"] != "active":
            raise ValueError(
                f"Cannot bill subscription '{subscription_id}' with status '{sub['status']}'."
            )

        transaction_id = self._new_id("txn")
        record = {
            "status": "success",
            "transaction_id": transaction_id,
            "subscription_id": subscription_id,
            "amount": sub["amount"],
            "currency": sub["currency"],
            "customer_id": sub["customer_id"],
            "billing_type": "recurring",
            "created_at": self._now_iso(),
        }
        self._transactions[transaction_id] = record
        return record

    # ------------------------------------------------------------------
    # Refunds  (all tiers)
    # ------------------------------------------------------------------

    def refund_payment(self, transaction_id: str, amount: Optional[float] = None) -> dict:
        """
        Refund a previously processed payment (full or partial).

        Parameters
        ----------
        transaction_id : str
            The transaction to refund.
        amount : float | None
            Refund amount.  Defaults to the full transaction amount.

        Returns
        -------
        dict
            Refund record.
        """
        self._require_feature(FEATURE_REFUNDS)

        if transaction_id not in self._transactions:
            raise KeyError(f"Transaction '{transaction_id}' not found.")

        txn = self._transactions[transaction_id]
        refund_amount = amount if amount is not None else txn["amount"]

        if refund_amount > txn["amount"]:
            raise ValueError("Refund amount exceeds original transaction amount.")

        refund_id = self._new_id("ref")
        record = {
            "refund_id": refund_id,
            "transaction_id": transaction_id,
            "refund_amount": round(refund_amount, 2),
            "currency": txn["currency"],
            "customer_id": txn["customer_id"],
            "status": "refunded",
            "created_at": self._now_iso(),
        }
        return record

    # ------------------------------------------------------------------
    # Transaction history
    # ------------------------------------------------------------------

    def list_transactions(self, customer_id: str) -> list:
        """
        Return all transactions for a given customer.

        Parameters
        ----------
        customer_id : str
            Customer whose transactions to retrieve.

        Returns
        -------
        list[dict]
            List of transaction records (most recent first).
        """
        results = [
            t for t in self._transactions.values()
            if t.get("customer_id") == customer_id
        ]
        return sorted(results, key=lambda t: t["created_at"], reverse=True)
