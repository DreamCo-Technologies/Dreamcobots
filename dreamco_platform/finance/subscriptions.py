"""Local bill tracking and exact-action approval packets."""

from __future__ import annotations

import time
import uuid
from dataclasses import asdict, dataclass
from decimal import Decimal, InvalidOperation
from typing import Any


class FinanceAssistantError(ValueError):
    """Raised when a financial request is incomplete or unsafe."""


def _amount(value: str) -> Decimal:
    try:
        amount = Decimal(value).quantize(Decimal("0.01"))
    except InvalidOperation as error:
        raise FinanceAssistantError("Use a valid decimal amount.") from error
    if amount < 0 or amount > Decimal("1000000.00"):
        raise FinanceAssistantError("Amount is outside the supported range.")
    return amount


@dataclass(frozen=True)
class Bill:
    bill_id: str
    payee: str
    amount: str
    currency: str
    due_at: float
    account_reference: str
    autopay_enabled: bool = False

    def validate(self) -> None:
        if len(self.payee.strip()) < 2 or self.due_at <= 0:
            raise FinanceAssistantError("Payee and due date are required.")
        _amount(self.amount)
        if not self.currency.isalpha() or len(self.currency) != 3:
            raise FinanceAssistantError("Currency must be a three-letter code.")
        if len(self.account_reference) < 3 or any(char.isspace() for char in self.account_reference):
            raise FinanceAssistantError("Use an opaque account reference, never account numbers.")


@dataclass(frozen=True)
class Subscription:
    subscription_id: str
    merchant: str
    amount: str
    currency: str
    renewal_at: float
    cadence: str
    cancel_url: str = ""

    def validate(self) -> None:
        if len(self.merchant.strip()) < 2 or self.cadence not in {"weekly", "monthly", "quarterly", "annual"}:
            raise FinanceAssistantError("Merchant and supported renewal cadence are required.")
        _amount(self.amount)
        if not self.currency.isalpha() or len(self.currency) != 3:
            raise FinanceAssistantError("Currency must be a three-letter code.")
        if self.cancel_url and not self.cancel_url.startswith("https://"):
            raise FinanceAssistantError("Cancellation links must use HTTPS.")


class BuddySubscriptionManager:
    def __init__(self) -> None:
        self.bills: dict[str, Bill] = {}
        self.subscriptions: dict[str, Subscription] = {}

    def add_bill(self, bill: Bill) -> None:
        bill.validate()
        self.bills[bill.bill_id] = bill

    def add_subscription(self, subscription: Subscription) -> None:
        subscription.validate()
        self.subscriptions[subscription.subscription_id] = subscription

    def dashboard(self, *, now: float | None = None, window_days: int = 30) -> dict[str, Any]:
        current = time.time() if now is None else now
        horizon = current + min(max(window_days, 1), 365) * 86400
        upcoming_bills = [asdict(bill) for bill in self.bills.values() if current <= bill.due_at <= horizon]
        upcoming_subscriptions = [
            asdict(item) for item in self.subscriptions.values() if current <= item.renewal_at <= horizon
        ]
        duplicate_groups: dict[tuple[str, str, str], list[str]] = {}
        for item in self.subscriptions.values():
            key = (item.merchant.strip().lower(), str(_amount(item.amount)), item.currency.upper())
            duplicate_groups.setdefault(key, []).append(item.subscription_id)
        duplicates = [ids for ids in duplicate_groups.values() if len(ids) > 1]
        return {
            "schema": "dreamco.bill_subscription_dashboard.v1",
            "upcoming_bills": upcoming_bills,
            "upcoming_subscriptions": upcoming_subscriptions,
            "possible_duplicate_subscriptions": duplicates,
            "payment_credentials_stored": False,
        }

    def payment_approval_packet(self, bill_id: str) -> dict[str, Any]:
        bill = self.bills.get(bill_id)
        if bill is None:
            raise FinanceAssistantError("Bill not found.")
        return {
            "schema": "dreamco.bill_payment_approval.v1",
            "approval_request_id": f"approval-{uuid.uuid4().hex[:16]}",
            "status": "owner_approval_required",
            "bill_id": bill.bill_id,
            "payee": bill.payee,
            "amount": str(_amount(bill.amount)),
            "currency": bill.currency.upper(),
            "due_at": bill.due_at,
            "one_action_only": True,
            "payment_executed": False,
            "payment_method_reference": "not_included",
        }

    def cancellation_handoff(self, subscription_id: str) -> dict[str, Any]:
        item = self.subscriptions.get(subscription_id)
        if item is None:
            raise FinanceAssistantError("Subscription not found.")
        return {
            "schema": "dreamco.subscription_cancellation_handoff.v1",
            "status": "owner_action_required",
            "subscription_id": item.subscription_id,
            "merchant": item.merchant,
            "official_cancel_url": item.cancel_url or None,
            "steps": ["review retention or refund terms", "confirm cancellation", "save receipt"],
            "cancellation_submitted": False,
        }
