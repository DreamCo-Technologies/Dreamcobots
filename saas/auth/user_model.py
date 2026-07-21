"""
DreamCo User Model — Subscription tiers and tier-based feature flags.

Defines the canonical tier hierarchy used across the SaaS platform.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional


class SubscriptionTier(str, Enum):
    """User subscription tier hierarchy."""

    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


# ---------------------------------------------------------------------------
# Feature flags per tier
# ---------------------------------------------------------------------------

@dataclass
class TierFeatures:
    tier: SubscriptionTier
    max_bots: int              # bots uploadable
    max_runs_per_day: int      # bot runs per day
    can_use_redis_queue: bool  # queue-based execution
    can_use_workers: bool      # multi-worker scaling
    can_use_webhooks: bool
    can_export_data: bool
    support_level: str         # "community" | "email" | "dedicated"
    price_usd_monthly: float


TIER_FEATURES: Dict[SubscriptionTier, TierFeatures] = {
    SubscriptionTier.FREE: TierFeatures(
        tier=SubscriptionTier.FREE,
        max_bots=3,
        max_runs_per_day=5,
        can_use_redis_queue=False,
        can_use_workers=False,
        can_use_webhooks=False,
        can_export_data=False,
        support_level="community",
        price_usd_monthly=0.0,
    ),
    SubscriptionTier.PRO: TierFeatures(
        tier=SubscriptionTier.PRO,
        max_bots=25,
        max_runs_per_day=100,
        can_use_redis_queue=True,
        can_use_workers=True,
        can_use_webhooks=True,
        can_export_data=True,
        support_level="email",
        price_usd_monthly=29.0,
    ),
    SubscriptionTier.ENTERPRISE: TierFeatures(
        tier=SubscriptionTier.ENTERPRISE,
        max_bots=10_000,
        max_runs_per_day=10_000,
        can_use_redis_queue=True,
        can_use_workers=True,
        can_use_webhooks=True,
        can_export_data=True,
        support_level="dedicated",
        price_usd_monthly=499.0,
    ),
}


def get_tier_features(tier: SubscriptionTier) -> TierFeatures:
    """Return the feature set for *tier*."""
    return TIER_FEATURES[tier]


def get_tier_upgrade_path(current: SubscriptionTier) -> Optional[SubscriptionTier]:
    """Return the next tier up, or None if already at the highest."""
    order = [SubscriptionTier.FREE, SubscriptionTier.PRO, SubscriptionTier.ENTERPRISE]
    idx = order.index(current)
    if idx + 1 < len(order):
        return order[idx + 1]
    return None
