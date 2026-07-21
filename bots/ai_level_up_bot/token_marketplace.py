"""
Token Marketplace — usage-based billing engine for the DreamCo AI Level-Up Bot.

Revenue model:
  - User pays per token consumed.
  - DreamCo applies a 25% markup over base API costs.
  - Example: user buys $20 of tokens → DreamCo cost = $16 → profit = $4.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from dataclasses import dataclass, field
from typing import Dict, Optional

from framework import GlobalAISourcesFlow  # noqa: F401


@dataclass
class TokenTransaction:
    """Records a single token purchase or deduction."""

    transaction_id: str
    service_type: str
    tokens_used: float
    base_cost_usd: float
    total_cost_usd: float
    note: str = ""

    def to_dict(self) -> dict:
        return {
            "transaction_id": self.transaction_id,
            "service_type": self.service_type,
            "tokens_used": self.tokens_used,
            "base_cost_usd": self.base_cost_usd,
            "total_cost_usd": self.total_cost_usd,
            "note": self.note,
        }


# ---------------------------------------------------------------------------
# Base token prices (cost to DreamCo per unit)
# ---------------------------------------------------------------------------

_BASE_PRICES: Dict[str, float] = {
    "llm_standard": 0.002,      # per 1k tokens
    "llm_premium": 0.010,       # per 1k tokens (GPT-4 class)
    "image_gen": 0.040,         # per image
    "video_gen": 0.200,         # per second of video
    "voice_gen": 0.030,         # per 1k characters
    "music_gen": 0.100,         # per track
    "code_gen": 0.005,          # per 1k tokens
    "embedding": 0.0001,        # per 1k tokens
    "search": 0.010,            # per query
    "course_module": 0.500,     # per module completion
}

MARKUP_PERCENTAGE = 0.25


class TokenMarketplace:
    """Handles token pricing, purchasing, and billing.

    Parameters
    ----------
    max_daily_tokens : int | None
        Daily token cap for the current tier (None = unlimited).
    markup : float
        DreamCo markup fraction applied on top of base costs.  Defaults to
        :data:`MARKUP_PERCENTAGE` (0.25 = 25 %).
    """

    def __init__(
        self,
        max_daily_tokens: Optional[int] = None,
        markup: float = MARKUP_PERCENTAGE,
    ) -> None:
        self._max_daily_tokens = max_daily_tokens
        self._markup = markup
        self._base_prices: Dict[str, float] = dict(_BASE_PRICES)
        self._daily_tokens_used: float = 0.0
        self._transactions: list = []
        self._transaction_counter: int = 0

    # ------------------------------------------------------------------
    # Pricing
    # ------------------------------------------------------------------

    def get_price(self, service_type: str) -> Optional[float]:
        """Return the user-facing price (with markup) for a service type."""
        base = self._base_prices.get(service_type)
        if base is None:
            return None
        return round(base * (1 + self._markup), 6)

    def get_base_price(self, service_type: str) -> Optional[float]:
        """Return the raw base cost (DreamCo cost) for a service type."""
        return self._base_prices.get(service_type)

    def calculate_cost(self, service_type: str, units: float) -> Optional[dict]:
        """Calculate the cost for consuming *units* of a service.

        Returns a dict with ``base_cost_usd``, ``total_cost_usd``,
        ``dreamco_profit_usd``, and ``units``, or ``None`` if the
        service type is unknown.
        """
        base = self._base_prices.get(service_type)
        if base is None:
            return None
        base_total = round(base * units, 6)
        user_total = round(base_total * (1 + self._markup), 6)
        profit = round(user_total - base_total, 6)
        return {
            "service_type": service_type,
            "units": units,
            "base_cost_usd": base_total,
            "total_cost_usd": user_total,
            "dreamco_profit_usd": profit,
        }

    # ------------------------------------------------------------------
    # Transactions
    # ------------------------------------------------------------------

    def purchase_tokens(self, service_type: str, units: float) -> dict:
        """Record a token purchase and return transaction details.

        Enforces the daily token limit when set.
        """
        if self._max_daily_tokens is not None:
            if self._daily_tokens_used + units > self._max_daily_tokens:
                remaining = max(0.0, self._max_daily_tokens - self._daily_tokens_used)
                return {
                    "error": "Daily token limit reached",
                    "daily_limit": self._max_daily_tokens,
                    "tokens_used_today": self._daily_tokens_used,
                    "tokens_remaining": remaining,
                }

        cost = self.calculate_cost(service_type, units)
        if cost is None:
            return {"error": f"Unknown service type: '{service_type}'"}

        self._transaction_counter += 1
        tx_id = f"TX-{self._transaction_counter:06d}"
        tx = TokenTransaction(
            transaction_id=tx_id,
            service_type=service_type,
            tokens_used=units,
            base_cost_usd=cost["base_cost_usd"],
            total_cost_usd=cost["total_cost_usd"],
            note="Tokens applied to your account.",
        )
        self._transactions.append(tx)
        self._daily_tokens_used += units

        return {
            "transaction_id": tx_id,
            "service_type": service_type,
            "tokens_purchased": units,
            "total_cost_usd": cost["total_cost_usd"],
            "dreamco_profit_usd": cost["dreamco_profit_usd"],
            "note": tx.note,
        }

    def reset_daily_usage(self) -> None:
        """Reset the daily token counter (call at midnight/day boundary)."""
        self._daily_tokens_used = 0.0

    def get_usage_summary(self) -> dict:
        """Return a summary of token usage and revenue."""
        total_spent = sum(t.total_cost_usd for t in self._transactions)
        total_base = sum(t.base_cost_usd for t in self._transactions)
        return {
            "total_transactions": len(self._transactions),
            "total_tokens_used": self._daily_tokens_used,
            "total_revenue_usd": round(total_spent, 4),
            "total_cost_usd": round(total_base, 4),
            "total_profit_usd": round(total_spent - total_base, 4),
        }

    def list_service_types(self) -> list:
        """Return all available service type keys."""
        return list(self._base_prices.keys())
