# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""
Monetisation API — AI Marketplace

Provides a billing scaffold compatible with Stripe and PayPal.
In production, replace the stub adapters with real API clients.

Usage
-----
    from AIMarketplace.monetization_api import MonetizationAPI

    api = MonetizationAPI(provider="stripe")
    charge = api.charge(user_id="u_001", amount_usd=29.99, description="Pro Plan")
    refund = api.refund(charge_id=charge["charge_id"])
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any, Dict, Optional


SUPPORTED_PROVIDERS = ["stripe", "paypal"]


@dataclass
class ChargeRecord:
    charge_id: str
    user_id: str
    amount_usd: float
    description: str
    provider: str
    status: str = "succeeded"

    def to_dict(self) -> dict:
        return {
            "charge_id": self.charge_id,
            "user_id": self.user_id,
            "amount_usd": self.amount_usd,
            "description": self.description,
            "provider": self.provider,
            "status": self.status,
        }


class MonetizationAPI:
    """
    Billing scaffold for the AI Marketplace.

    Parameters
    ----------
    provider : str
        Payment provider — ``"stripe"`` (default) or ``"paypal"``.
    api_key : str | None
        API key / secret token for the provider.  Read from environment
        in production (never hard-code credentials).
    """

    def __init__(
        self,
        provider: str = "stripe",
        api_key: Optional[str] = None,
    ) -> None:
        if provider not in SUPPORTED_PROVIDERS:
            raise ValueError(f"Provider '{provider}' not supported. Choose from: {SUPPORTED_PROVIDERS}")
        self.provider = provider
        self._api_key = api_key  # Placeholder — inject via env var in production
        self._charges: Dict[str, ChargeRecord] = {}

    def charge(
        self,
        user_id: str,
        amount_usd: float,
        description: str = "",
    ) -> Dict[str, Any]:
        """
        Create a charge for *user_id*.

        Returns a serialised :class:`ChargeRecord`.

        In production wire this to ``stripe.PaymentIntent.create(...)``
        or the PayPal Orders API.
        """
        if amount_usd < 0:
            raise ValueError("Charge amount must be non-negative.")
        charge = ChargeRecord(
            charge_id=f"ch_{str(uuid.uuid4())[:8]}",
            user_id=user_id,
            amount_usd=amount_usd,
            description=description,
            provider=self.provider,
        )
        self._charges[charge.charge_id] = charge
        return charge.to_dict()

    def refund(self, charge_id: str) -> Dict[str, Any]:
        """
        Refund an existing charge.

        Returns the updated :class:`ChargeRecord` with ``status="refunded"``.
        """
        if charge_id not in self._charges:
            raise KeyError(f"Charge '{charge_id}' not found.")
        charge = self._charges[charge_id]
        charge.status = "refunded"
        return charge.to_dict()

    def list_charges(self, user_id: Optional[str] = None) -> list:
        """Return all charges, optionally filtered by user."""
        charges = list(self._charges.values())
        if user_id:
            charges = [c for c in charges if c.user_id == user_id]
        return [c.to_dict() for c in charges]
