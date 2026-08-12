from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Protocol
from uuid import uuid4


@dataclass(frozen=True)
class PaymentRequest:
    merchant_id: str
    amount: Decimal
    currency: str = "USD"
    payment_method_token: str = ""
    idempotency_key: str = ""
    metadata: dict[str, str] = field(default_factory=dict)

    def validate(self) -> None:
        if not self.merchant_id:
            raise ValueError("merchant_id is required")
        if self.amount <= 0:
            raise ValueError("amount must be greater than zero")
        if len(self.currency) != 3:
            raise ValueError("currency must be a 3-letter code")
        if not self.payment_method_token:
            raise ValueError("tokenized payment method is required; raw card data is not accepted")


@dataclass(frozen=True)
class PaymentResult:
    payment_id: str
    processor: str
    status: str
    amount: Decimal
    currency: str
    processor_reference: str | None = None


class PaymentGateway(Protocol):
    name: str
    def authorize_and_capture(self, request: PaymentRequest) -> PaymentResult: ...
    def refund(self, payment_id: str, amount: Decimal | None = None) -> PaymentResult: ...


class SandboxProcessor:
    """Non-networked adapter for tests and demos. Never processes a real card."""

    name = "dream-sandbox"

    def __init__(self) -> None:
        self._payments: dict[str, PaymentResult] = {}

    def authorize_and_capture(self, request: PaymentRequest) -> PaymentResult:
        request.validate()
        payment_id = f"dmp_{uuid4().hex}"
        result = PaymentResult(
            payment_id=payment_id,
            processor=self.name,
            status="succeeded",
            amount=request.amount,
            currency=request.currency.upper(),
            processor_reference=f"sandbox_{uuid4().hex[:16]}",
        )
        self._payments[payment_id] = result
        return result

    def refund(self, payment_id: str, amount: Decimal | None = None) -> PaymentResult:
        original = self._payments[payment_id]
        refund_amount = original.amount if amount is None else amount
        if refund_amount <= 0 or refund_amount > original.amount:
            raise ValueError("invalid refund amount")
        return PaymentResult(
            payment_id=f"dmr_{uuid4().hex}",
            processor=self.name,
            status="refunded",
            amount=refund_amount,
            currency=original.currency,
            processor_reference=f"sandbox_refund_{uuid4().hex[:12]}",
        )
