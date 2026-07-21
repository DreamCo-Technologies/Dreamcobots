"""
Subscription manager for the DreamCobots billing system.

Tracks which tier each user is subscribed to and maintains a history of
subscription changes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from bots.token_billing.tiers import Tier, TierConfig, get_tier_config


class SubscriptionError(Exception):
    """Raised for invalid subscription operations."""


@dataclass
class SubscriptionRecord:
    """A record of a single subscription event.

    Attributes
    ----------
    user_id : str
        User this record belongs to.
    tier : Tier
        The tier that was activated.
    activated_at : datetime
        When the tier was activated.
    cancelled_at : datetime or None
        When the tier was cancelled (None if still active).
    """

    user_id: str
    tier: Tier
    activated_at: datetime
    cancelled_at: datetime = None


class SubscriptionManager:
    """Manages subscription tiers for all users.

    Users start on the FREE tier by default when their account is created.
    They can upgrade, downgrade, or cancel their subscription at any time.
    """

    def __init__(self) -> None:
        self._subscriptions: dict[str, SubscriptionRecord] = {}
        self._history: dict[str, list] = {}

    # ------------------------------------------------------------------
    # Account creation
    # ------------------------------------------------------------------

    def initialize_account(self, user_id: str, tier: Tier = Tier.FREE) -> SubscriptionRecord:
        """Set up a new subscription account for *user_id*.

        Parameters
        ----------
        user_id : str
            User to initialise.
        tier : Tier, optional
            Starting tier (defaults to FREE).

        Returns
        -------
        SubscriptionRecord
            The newly created subscription record.

        Raises
        ------
        SubscriptionError
            If the user already has an active subscription.
        """
        if user_id in self._subscriptions:
            raise SubscriptionError(
                f"User '{user_id}' already has an active subscription."
            )
        record = SubscriptionRecord(
            user_id=user_id,
            tier=tier,
            activated_at=datetime.utcnow(),
        )
        self._subscriptions[user_id] = record
        self._history.setdefault(user_id, []).append(record)
        return record

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get_subscription(self, user_id: str) -> SubscriptionRecord:
        """Return the active subscription for *user_id*.

        Raises
        ------
        KeyError
            If the user has no subscription record.
        """
        if user_id not in self._subscriptions:
            raise KeyError(f"No subscription found for user '{user_id}'.")
        return self._subscriptions[user_id]

    def get_tier_config(self, user_id: str) -> TierConfig:
        """Return the TierConfig for the user's active tier."""
        return get_tier_config(self.get_subscription(user_id).tier)

    def get_history(self, user_id: str) -> list:
        """Return the full subscription history for *user_id*."""
        return list(self._history.get(user_id, []))

    # ------------------------------------------------------------------
    # Mutations
    # ------------------------------------------------------------------

    def change_tier(self, user_id: str, new_tier: Tier) -> SubscriptionRecord:
        """Change *user_id*'s active subscription to *new_tier*.

        The previous record is marked as cancelled and a new active record is
        created.

        Parameters
        ----------
        user_id : str
            User whose tier should change.
        new_tier : Tier
            The tier to switch to.

        Returns
        -------
        SubscriptionRecord
            The new active subscription record.
        """
        old_record = self.get_subscription(user_id)
        old_record.cancelled_at = datetime.utcnow()

        new_record = SubscriptionRecord(
            user_id=user_id,
            tier=new_tier,
            activated_at=datetime.utcnow(),
        )
        self._subscriptions[user_id] = new_record
        self._history[user_id].append(new_record)
        return new_record

    def cancel_subscription(self, user_id: str) -> SubscriptionRecord:
        """Cancel the active subscription and revert *user_id* to FREE.

        Returns
        -------
        SubscriptionRecord
            The new FREE subscription record.
        """
        return self.change_tier(user_id, Tier.FREE)
