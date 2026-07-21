"""
Tier configuration for the God Mode Bot — DreamCo's autonomous business operator.

Tiers:
  - FREE ($0/mo):        Basic lead hunting (5 leads/cycle), basic viral content
                         (3 posts), view-only payment stats.
  - PRO ($97/mo):        20 leads/cycle, viral engine (all platforms), auto-closer,
                         payment collection (up to 50 subscribers), self-improving AI.
  - ENTERPRISE ($297/mo): Unlimited leads, all engines, white-label, API access,
                           dedicated support.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Tier(Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


@dataclass
class TierConfig:
    """Configuration for a God Mode Bot subscription tier.

    Attributes
    ----------
    name : str
        Human-readable tier name.
    tier : Tier
        Enum value.
    price_usd_monthly : float
        Monthly subscription price in USD.
    max_leads_per_cycle : int | None
        Maximum leads hunted per cycle.  None = unlimited.
    max_subscribers : int | None
        Maximum payment subscribers managed.  None = unlimited.
    max_viral_posts : int | None
        Maximum viral posts created per cycle.  None = unlimited.
    features : list[str]
        Feature flags enabled on this tier.
    support_level : str
        Support offering description.
    """

    name: str
    tier: Tier
    price_usd_monthly: float
    max_leads_per_cycle: Optional[int]
    max_subscribers: Optional[int]
    max_viral_posts: Optional[int]
    features: list
    support_level: str

    def has_feature(self, feature: str) -> bool:
        """Return True if *feature* is available on this tier."""
        return feature in self.features

    def is_unlimited_leads(self) -> bool:
        """Return True if leads per cycle are unlimited."""
        return self.max_leads_per_cycle is None


# ---------------------------------------------------------------------------
# Feature flags
# ---------------------------------------------------------------------------

FEATURE_LEAD_HUNTING = "lead_hunting"
FEATURE_AUTO_CLOSER = "auto_closer"
FEATURE_PAYMENT_COLLECTION = "payment_collection"
FEATURE_VIRAL_ENGINE = "viral_engine"
FEATURE_SELF_IMPROVING_AI = "self_improving_ai"
FEATURE_WHITE_LABEL = "white_label"
FEATURE_API_ACCESS = "api_access"
FEATURE_DEDICATED_SUPPORT = "dedicated_support"

FREE_FEATURES: list = [
    FEATURE_LEAD_HUNTING,
    FEATURE_VIRAL_ENGINE,
]

PRO_FEATURES: list = FREE_FEATURES + [
    FEATURE_AUTO_CLOSER,
    FEATURE_PAYMENT_COLLECTION,
    FEATURE_SELF_IMPROVING_AI,
]

ENTERPRISE_FEATURES: list = PRO_FEATURES + [
    FEATURE_WHITE_LABEL,
    FEATURE_API_ACCESS,
    FEATURE_DEDICATED_SUPPORT,
]

TIER_CATALOGUE: dict = {
    Tier.FREE.value: TierConfig(
        name="Free",
        tier=Tier.FREE,
        price_usd_monthly=0.0,
        max_leads_per_cycle=5,
        max_subscribers=None,
        max_viral_posts=3,
        features=FREE_FEATURES,
        support_level="Community",
    ),
    Tier.PRO.value: TierConfig(
        name="Pro",
        tier=Tier.PRO,
        price_usd_monthly=97.0,
        max_leads_per_cycle=20,
        max_subscribers=50,
        max_viral_posts=None,
        features=PRO_FEATURES,
        support_level="Email (24 h SLA)",
    ),
    Tier.ENTERPRISE.value: TierConfig(
        name="Enterprise",
        tier=Tier.ENTERPRISE,
        price_usd_monthly=297.0,
        max_leads_per_cycle=None,
        max_subscribers=None,
        max_viral_posts=None,
        features=ENTERPRISE_FEATURES,
        support_level="Dedicated 24/7",
    ),
}


def get_tier_config(tier: Tier) -> TierConfig:
    """Return the TierConfig for *tier*."""
    return TIER_CATALOGUE[tier.value]


def list_tiers() -> list:
    """Return all TierConfig objects in tier order."""
    return [TIER_CATALOGUE[t.value] for t in Tier]


def get_upgrade_path(current: Tier) -> Optional[TierConfig]:
    """Return the next tier's config, or None if already at the top."""
    order = list(Tier)
    idx = order.index(current)
    if idx + 1 < len(order):
        return get_tier_config(order[idx + 1])
    return None
