"""
Subscription tier configuration for the DreamCobots token billing system.

Tiers
-----
FREE               - $0/month.  100 tokens/day.  All 109 models (limited capacity).
PRO_MONTHLY        - $49/month. 10,000 tokens/day. All 109 models (full capacity).
PRO_ANNUAL         - $490/year. 10,000 tokens/day. ~17 % saving over monthly.
ENTERPRISE_MONTHLY - $299/month. Unlimited tokens. Custom models + dedicated support.
ENTERPRISE_ANNUAL  - $2,990/year. Unlimited tokens. ~17 % saving over monthly.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Tier(Enum):
    FREE = "free"
    PRO_MONTHLY = "pro_monthly"
    PRO_ANNUAL = "pro_annual"
    ENTERPRISE_MONTHLY = "enterprise_monthly"
    ENTERPRISE_ANNUAL = "enterprise_annual"


@dataclass
class TierConfig:
    """Configuration for a single DreamCobots billing tier.

    Attributes
    ----------
    tier : Tier
        Enum value identifying the tier.
    name : str
        Human-readable display name.
    price_usd_monthly : float
        Effective monthly price in USD.  For annual plans this is computed
        automatically as ``price_usd_total / 12`` (rounded to 2 dp).
    price_usd_total : float
        Total charge per billing cycle in USD.
    billing_cycle : str
        ``"monthly"`` or ``"annual"``.
    daily_tokens : Optional[int]
        Daily token allowance. ``None`` means unlimited.
    ai_models_count : int
        Number of AI models accessible on this tier.
    full_capacity : bool
        Whether the tier allows full model capacity (vs limited / rate-capped).
    features : list[str]
        Feature flags enabled on this tier.
    support_level : str
        Description of the support offering.
    """

    tier: Tier
    name: str
    price_usd_total: float
    billing_cycle: str
    daily_tokens: Optional[int]
    ai_models_count: int
    full_capacity: bool
    features: list
    support_level: str
    price_usd_monthly: float = field(default=0.0)

    def __post_init__(self) -> None:
        if self.billing_cycle == "annual":
            self.price_usd_monthly = round(self.price_usd_total / 12, 2)
        elif self.price_usd_monthly == 0.0:
            self.price_usd_monthly = self.price_usd_total

    def is_unlimited(self) -> bool:
        """Return True when there is no daily token cap."""
        return self.daily_tokens is None

    def has_feature(self, feature: str) -> bool:
        """Return True when *feature* is enabled on this tier."""
        return feature in self.features


# ---------------------------------------------------------------------------
# Feature flags
# ---------------------------------------------------------------------------

FEATURE_ALL_109_MODELS = "all_109_models"
FEATURE_LIMITED_CAPACITY = "limited_capacity"
FEATURE_FULL_CAPACITY = "full_capacity"
FEATURE_TOKEN_CREDITS = "token_credits"
FEATURE_ANALYTICS_DASHBOARD = "analytics_dashboard"
FEATURE_BATCH_PROCESSING = "batch_processing"
FEATURE_FINE_TUNING = "fine_tuning"
FEATURE_PRIORITY_ROUTING = "priority_routing"
FEATURE_CUSTOM_MODELS = "custom_models"
FEATURE_WHITE_LABEL = "white_label"
FEATURE_SLA_GUARANTEE = "sla_guarantee"
FEATURE_DEDICATED_SUPPORT = "dedicated_support"

FREE_FEATURES = [
    FEATURE_ALL_109_MODELS,
    FEATURE_LIMITED_CAPACITY,
    FEATURE_TOKEN_CREDITS,
]

PRO_FEATURES = [
    FEATURE_ALL_109_MODELS,
    FEATURE_FULL_CAPACITY,
    FEATURE_TOKEN_CREDITS,
    FEATURE_ANALYTICS_DASHBOARD,
    FEATURE_BATCH_PROCESSING,
    FEATURE_FINE_TUNING,
]

ENTERPRISE_FEATURES = PRO_FEATURES + [
    FEATURE_PRIORITY_ROUTING,
    FEATURE_CUSTOM_MODELS,
    FEATURE_WHITE_LABEL,
    FEATURE_SLA_GUARANTEE,
    FEATURE_DEDICATED_SUPPORT,
]

# ---------------------------------------------------------------------------
# Tier catalogue
# ---------------------------------------------------------------------------

TIER_CATALOGUE: dict[str, TierConfig] = {
    Tier.FREE.value: TierConfig(
        tier=Tier.FREE,
        name="Free",
        price_usd_total=0.0,
        billing_cycle="monthly",
        daily_tokens=100,
        ai_models_count=109,
        full_capacity=False,
        features=FREE_FEATURES,
        support_level="Community",
    ),
    Tier.PRO_MONTHLY.value: TierConfig(
        tier=Tier.PRO_MONTHLY,
        name="Pro (Monthly)",
        price_usd_total=49.0,
        billing_cycle="monthly",
        daily_tokens=10_000,
        ai_models_count=109,
        full_capacity=True,
        features=PRO_FEATURES,
        support_level="Email (48 h SLA)",
    ),
    Tier.PRO_ANNUAL.value: TierConfig(
        tier=Tier.PRO_ANNUAL,
        name="Pro (Annual)",
        price_usd_total=490.0,
        billing_cycle="annual",
        daily_tokens=10_000,
        ai_models_count=109,
        full_capacity=True,
        features=PRO_FEATURES,
        support_level="Email (48 h SLA)",
    ),
    Tier.ENTERPRISE_MONTHLY.value: TierConfig(
        tier=Tier.ENTERPRISE_MONTHLY,
        name="Enterprise (Monthly)",
        price_usd_total=299.0,
        billing_cycle="monthly",
        daily_tokens=None,
        ai_models_count=109,
        full_capacity=True,
        features=ENTERPRISE_FEATURES,
        support_level="Dedicated 24/7",
    ),
    Tier.ENTERPRISE_ANNUAL.value: TierConfig(
        tier=Tier.ENTERPRISE_ANNUAL,
        name="Enterprise (Annual)",
        price_usd_total=2_990.0,
        billing_cycle="annual",
        daily_tokens=None,
        ai_models_count=109,
        full_capacity=True,
        features=ENTERPRISE_FEATURES,
        support_level="Dedicated 24/7",
    ),
}


def get_tier_config(tier: Tier) -> TierConfig:
    """Return the TierConfig for the given Tier enum value."""
    return TIER_CATALOGUE[tier.value]


def list_tiers() -> list:
    """Return all tier configs ordered from cheapest to most expensive."""
    order = [
        Tier.FREE,
        Tier.PRO_MONTHLY,
        Tier.PRO_ANNUAL,
        Tier.ENTERPRISE_MONTHLY,
        Tier.ENTERPRISE_ANNUAL,
    ]
    return [TIER_CATALOGUE[t.value] for t in order]
