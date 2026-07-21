"""
BillingSystem — top-level facade for DreamCobots token billing.

Combines TokenManager and SubscriptionManager into a single interface so that
other parts of the codebase (e.g. BuddyBot) only need to import and call this
class.

All AI model costs are attributed to the client's token balance, ensuring the
platform operates cost-neutrally.
"""

from __future__ import annotations

from datetime import date
from typing import Optional

from bots.token_billing.tiers import Tier, TierConfig, get_tier_config
from bots.token_billing.token_manager import TokenManager, InsufficientTokensError
from bots.token_billing.subscription_manager import (
    SubscriptionManager,
    SubscriptionError,
)

# Pre-defined token credit packs (amount: price_usd)
TOKEN_PACKS: dict[int, float] = {
    500: 5.0,
    2_500: 20.0,
    10_000: 70.0,
    50_000: 300.0,
}

_UNLIMITED_DAILY = TokenManager.UNLIMITED_SENTINEL


class BillingSystem:
    """Unified billing facade for the DreamCobots platform.

    Usage
    -----
    ::

        billing = BillingSystem()
        user_id = billing.create_account("alice", Tier.FREE)
        billing.purchase_tokens(user_id, 500)
        billing.deduct_tokens(user_id, 5, description="GPT-4 call")
        report = billing.get_usage_report(user_id)
    """

    def __init__(self) -> None:
        self._tokens = TokenManager()
        self._subs = SubscriptionManager()

    # ------------------------------------------------------------------
    # Account lifecycle
    # ------------------------------------------------------------------

    def create_account(self, user_id: str, tier: Tier = Tier.FREE) -> str:
        """Create a billing account for *user_id* on *tier*.

        Parameters
        ----------
        user_id : str
            Unique user identifier.
        tier : Tier, optional
            Starting tier (defaults to FREE).

        Returns
        -------
        str
            The user_id (unchanged — returned for convenience).
        """
        self._tokens.create_account(user_id)
        self._subs.initialize_account(user_id, tier)
        return user_id

    def get_account(self, user_id: str) -> dict:
        """Return account details for *user_id*.

        Returns
        -------
        dict
            Keys: ``user_id``, ``tier``, ``tier_name``, ``billing_cycle``,
            ``price_usd_monthly``, ``daily_tokens``, ``full_capacity``.
        """
        cfg = self._subs.get_tier_config(user_id)
        return {
            "user_id": user_id,
            "tier": cfg.tier.value,
            "tier_name": cfg.name,
            "billing_cycle": cfg.billing_cycle,
            "price_usd_monthly": cfg.price_usd_monthly,
            "daily_tokens": cfg.daily_tokens,
            "full_capacity": cfg.full_capacity,
        }

    # ------------------------------------------------------------------
    # Token credits
    # ------------------------------------------------------------------

    def purchase_tokens(self, user_id: str, amount: int, description: str = "Token purchase") -> int:
        """Add purchased (non-expiring) token credits to *user_id*.

        Parameters
        ----------
        user_id : str
            Target user.
        amount : int
            Number of tokens to purchase (must be positive).
        description : str
            Ledger description.

        Returns
        -------
        int
            New purchased token balance.
        """
        return self._tokens.add_tokens(user_id, amount, description)

    def deduct_tokens(
        self,
        user_id: str,
        cost: int,
        description: str = "AI model usage",
        today: Optional[date] = None,
    ) -> int:
        """Deduct *cost* tokens from *user_id* (platform cost attribution).

        Purchased credits are consumed first; the daily free allowance is drawn
        on afterwards.  Raises InsufficientTokensError if the user has no
        tokens left.

        Parameters
        ----------
        user_id : str
            Target user.
        cost : int
            Tokens to deduct.
        description : str
            Ledger description (e.g. ``"GPT-4 call"``).
        today : date, optional
            Override date for testing.

        Returns
        -------
        int
            Remaining purchased token balance.
        """
        daily = self._daily_allowance(user_id)
        return self._tokens.deduct_tokens(user_id, cost, daily, description, today)

    def get_balance(self, user_id: str) -> dict:
        """Return token balance summary for *user_id*.

        Returns
        -------
        dict
            Keys: ``user_id``, ``purchased_tokens``,
            ``daily_tokens_remaining``, ``total_available``.
        """
        daily = self._daily_allowance(user_id)
        return self._tokens.get_balance(user_id, daily)

    # ------------------------------------------------------------------
    # Subscriptions
    # ------------------------------------------------------------------

    def create_subscription(self, user_id: str, tier: Tier) -> dict:
        """Create or update the subscription for *user_id* to *tier*.

        Parameters
        ----------
        user_id : str
            Target user.
        tier : Tier
            New subscription tier.

        Returns
        -------
        dict
            Updated account details (same shape as ``get_account``).
        """
        self._subs.change_tier(user_id, tier)
        return self.get_account(user_id)

    def cancel_subscription(self, user_id: str) -> dict:
        """Cancel *user_id*'s active subscription and revert to FREE.

        Returns
        -------
        dict
            Updated account details.
        """
        self._subs.cancel_subscription(user_id)
        return self.get_account(user_id)

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    def get_usage_report(self, user_id: str) -> dict:
        """Return a full usage and billing report for *user_id*.

        Returns
        -------
        dict
            Keys: ``user_id``, ``account``, ``balance``,
            ``subscription_history``, ``ledger``.
        """
        return {
            "user_id": user_id,
            "account": self.get_account(user_id),
            "balance": self.get_balance(user_id),
            "subscription_history": [
                {
                    "tier": r.tier.value,
                    "activated_at": r.activated_at.isoformat(),
                    "cancelled_at": r.cancelled_at.isoformat() if r.cancelled_at else None,
                }
                for r in self._subs.get_history(user_id)
            ],
            "ledger": [
                {
                    "timestamp": e.timestamp.isoformat(),
                    "delta": e.delta,
                    "description": e.description,
                    "balance_after": e.balance_after,
                }
                for e in self._tokens.get_ledger(user_id)
            ],
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _daily_allowance(self, user_id: str) -> int:
        """Return the daily token allowance for *user_id*'s current tier."""
        cfg = self._subs.get_tier_config(user_id)
        if cfg.daily_tokens is None:
            return _UNLIMITED_DAILY
        return cfg.daily_tokens
