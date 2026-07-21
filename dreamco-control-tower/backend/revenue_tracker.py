"""
DreamCo Control Tower — Revenue Tracker
=========================================
Tracks payment events from multiple providers (Stripe, PayPal, Square) and
summarises revenue across bots, time periods, and sources.

This module is a self-contained analytics layer.  In production it would be
wired to the real payment-provider SDKs; for the starter implementation every
provider is represented as a stub that simply records and reads from an
in-memory log.

Payment providers can be swapped in via the ``PaymentProvider`` protocol.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Provider protocol
# ---------------------------------------------------------------------------

class PaymentProvider(ABC):
    """Abstract base class for payment-provider adapters."""

    @property
    @abstractmethod
    def name(self) -> str:  # pragma: no cover
        """Human-readable provider name, e.g. ``stripe``."""

    @abstractmethod
    def fetch_payments(self, limit: int = 100) -> List[Dict[str, Any]]:  # pragma: no cover
        """Return a list of payment records as plain dicts.

        Each record must include at least:
          - ``amount_usd`` (float)
          - ``timestamp``  (ISO-8601 string)
          - ``bot_name``   (str, may be empty)
          - ``status``     (str, e.g. ``succeeded`` / ``failed``)
        """


# ---------------------------------------------------------------------------
# Stub providers (replace with real SDK calls in production)
# ---------------------------------------------------------------------------

class StripeProvider(PaymentProvider):
    """Stub Stripe provider.

    In production, replace ``fetch_payments`` with::

        import stripe
        stripe.api_key = os.environ["STRIPE_KEY"]
        intents = stripe.PaymentIntent.list(limit=limit)
        ...
    """

    @property
    def name(self) -> str:
        return "stripe"

    def fetch_payments(self, limit: int = 100) -> List[Dict[str, Any]]:
        return []


class PayPalProvider(PaymentProvider):
    """Stub PayPal provider."""

    @property
    def name(self) -> str:
        return "paypal"

    def fetch_payments(self, limit: int = 100) -> List[Dict[str, Any]]:
        return []


class SquareProvider(PaymentProvider):
    """Stub Square provider."""

    @property
    def name(self) -> str:
        return "square"

    def fetch_payments(self, limit: int = 100) -> List[Dict[str, Any]]:
        return []


# ---------------------------------------------------------------------------
# Revenue Tracker
# ---------------------------------------------------------------------------

class RevenueTracker:
    """Aggregates and analyses revenue data from multiple payment providers.

    Parameters
    ----------
    providers:
        List of :class:`PaymentProvider` instances to query.  Defaults to
        the three built-in stub providers (Stripe, PayPal, Square).
    """

    def __init__(self, providers: Optional[List[PaymentProvider]] = None) -> None:
        self._providers: List[PaymentProvider] = providers or [
            StripeProvider(),
            PayPalProvider(),
            SquareProvider(),
        ]
        self._manual_entries: List[Dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Manual entry (useful for testing and for bots that report revenue
    # directly without going through a payment provider)
    # ------------------------------------------------------------------

    def add_entry(
        self,
        amount_usd: float,
        bot_name: str = "",
        provider: str = "manual",
        status: str = "succeeded",
    ) -> Dict[str, Any]:
        """Manually record a revenue event.

        Parameters
        ----------
        amount_usd: Payment amount in US dollars.
        bot_name:   Name of the bot that generated the revenue.
        provider:   Source label (defaults to ``manual``).
        status:     Payment status (defaults to ``succeeded``).
        """
        entry: Dict[str, Any] = {
            "amount_usd": round(amount_usd, 2),
            "bot_name": bot_name,
            "provider": provider,
            "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._manual_entries.append(entry)
        return entry

    # ------------------------------------------------------------------
    # Aggregation
    # ------------------------------------------------------------------

    def get_all_payments(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Collect payments from all providers plus manual entries."""
        collected: List[Dict[str, Any]] = list(self._manual_entries)
        for provider in self._providers:
            payments = provider.fetch_payments(limit=limit)
            for p in payments:
                p.setdefault("provider", provider.name)
            collected.extend(payments)
        # Sort newest-first
        collected.sort(key=lambda p: p.get("timestamp", ""), reverse=True)
        return collected[:limit]

    def get_summary(self, limit: int = 100) -> Dict[str, Any]:
        """Return a high-level revenue summary.

        Returns
        -------
        dict with keys:
          - ``total_usd``       — total revenue across all providers
          - ``by_provider``     — breakdown per provider
          - ``by_bot``          — breakdown per bot
          - ``succeeded_count`` — number of successful payments
          - ``failed_count``    — number of failed payments
          - ``payment_count``   — total events
          - ``timestamp``       — snapshot time (ISO-8601)
        """
        payments = self.get_all_payments(limit=limit)
        total = 0.0
        by_provider: Dict[str, float] = {}
        by_bot: Dict[str, float] = {}
        succeeded = 0
        failed = 0

        for p in payments:
            amt = p.get("amount_usd", 0.0)
            status = p.get("status", "")
            prov = p.get("provider", "unknown")
            bot = p.get("bot_name", "")

            if status == "succeeded":
                total += amt
                succeeded += 1
                by_provider[prov] = round(by_provider.get(prov, 0.0) + amt, 2)
                if bot:
                    by_bot[bot] = round(by_bot.get(bot, 0.0) + amt, 2)
            elif status == "failed":
                failed += 1

        return {
            "total_usd": round(total, 2),
            "by_provider": by_provider,
            "by_bot": by_bot,
            "succeeded_count": succeeded,
            "failed_count": failed,
            "payment_count": len(payments),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def get_top_bots(self, n: int = 5) -> List[Dict[str, Any]]:
        """Return the top *n* revenue-generating bots."""
        summary = self.get_summary()
        ranked = sorted(summary["by_bot"].items(), key=lambda kv: kv[1], reverse=True)
        return [{"bot": name, "revenue_usd": rev} for name, rev in ranked[:n]]

    def get_provider_breakdown(self) -> List[Dict[str, Any]]:
        """Return revenue broken down by payment provider."""
        summary = self.get_summary()
        return [
            {"provider": prov, "revenue_usd": rev}
            for prov, rev in sorted(summary["by_provider"].items(), key=lambda kv: kv[1], reverse=True)
        ]
