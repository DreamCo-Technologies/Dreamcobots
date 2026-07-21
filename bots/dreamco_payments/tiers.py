"""
Tier configuration for the DreamCo Payments Bot.

Tiers:
  - STARTER:    Basic payment processing, 1 000 transactions/month, $29/mo.
  - GROWTH:     Expanded processing, 10 000 transactions/month, $99/mo.
  - ENTERPRISE: Unlimited transactions, all features, priority support.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional


class Tier(Enum):
    STARTER = "starter"
    GROWTH = "growth"
    ENTERPRISE = "enterprise"


@dataclass
class TierConfig:
    """Configuration for a DreamCo Payments subscription tier.

    Attributes
    ----------
    name : str
        Human-readable tier name.
    tier : Tier
        Enum value identifying the tier.
    price_usd_monthly : float
        Monthly subscription price in USD.
    transactions_per_month : int | None
        Maximum transactions per calendar month.  ``None`` means unlimited.
    features : list[str]
        Feature flags enabled on this tier.
    support_level : str
        Description of the support offering.
    """

    name: str
    tier: Tier
    price_usd_monthly: float
    transactions_per_month: Optional[int]
    features: list
    support_level: str

    def is_unlimited(self) -> bool:
        """Return True if this tier has no transaction cap."""
        return self.transactions_per_month is None

    def has_feature(self, feature: str) -> bool:
        """Return True if *feature* is enabled on this tier."""
        return feature in self.features


# ---------------------------------------------------------------------------
# Feature flags
# ---------------------------------------------------------------------------

FEATURE_PAYMENT_PROCESSING = "payment_processing"
FEATURE_BASIC_SUBSCRIPTIONS = "basic_subscriptions"
FEATURE_REFUNDS = "refunds"
FEATURE_CURRENCY_CONVERSION = "currency_conversion"
FEATURE_RECURRING_BILLING = "recurring_billing"
FEATURE_FRAUD_DETECTION = "fraud_detection"
FEATURE_MULTI_CURRENCY = "multi_currency"
FEATURE_ANALYTICS_DASHBOARD = "analytics_dashboard"
FEATURE_ADVANCED_REPORTING = "advanced_reporting"
FEATURE_CUSTOM_LIMITS = "custom_limits"
FEATURE_WHITE_LABEL = "white_label"
FEATURE_API_KEY_MANAGEMENT = "api_key_management"
FEATURE_DISCOUNT_DOMINATOR = "discount_dominator"
FEATURE_REAL_ESTATE_AUTOMATION = "real_estate_automation"
FEATURE_AUTO_DEALER_AUTOMATION = "auto_dealer_automation"
FEATURE_DEDICATED_SUPPORT = "dedicated_support"
FEATURE_SLA_GUARANTEE = "sla_guarantee"

STARTER_FEATURES = [
    FEATURE_PAYMENT_PROCESSING,
    FEATURE_BASIC_SUBSCRIPTIONS,
    FEATURE_REFUNDS,
    FEATURE_API_KEY_MANAGEMENT,
]

GROWTH_FEATURES = STARTER_FEATURES + [
    FEATURE_CURRENCY_CONVERSION,
    FEATURE_RECURRING_BILLING,
    FEATURE_FRAUD_DETECTION,
    FEATURE_MULTI_CURRENCY,
    FEATURE_ANALYTICS_DASHBOARD,
    FEATURE_DISCOUNT_DOMINATOR,
]

ENTERPRISE_FEATURES = GROWTH_FEATURES + [
    FEATURE_ADVANCED_REPORTING,
    FEATURE_CUSTOM_LIMITS,
    FEATURE_WHITE_LABEL,
    FEATURE_REAL_ESTATE_AUTOMATION,
    FEATURE_AUTO_DEALER_AUTOMATION,
    FEATURE_DEDICATED_SUPPORT,
    FEATURE_SLA_GUARANTEE,
]

# ---------------------------------------------------------------------------
# Tier catalogue
# ---------------------------------------------------------------------------

TIER_CATALOGUE: dict[str, TierConfig] = {
    Tier.STARTER.value: TierConfig(
        name="Starter",
        tier=Tier.STARTER,
        price_usd_monthly=29.0,
        transactions_per_month=1_000,
        features=STARTER_FEATURES,
        support_level="Community",
    ),
    Tier.GROWTH.value: TierConfig(
        name="Growth",
        tier=Tier.GROWTH,
        price_usd_monthly=99.0,
        transactions_per_month=10_000,
        features=GROWTH_FEATURES,
        support_level="Email (24 h SLA)",
    ),
    Tier.ENTERPRISE.value: TierConfig(
        name="Enterprise",
        tier=Tier.ENTERPRISE,
        price_usd_monthly=299.0,
        transactions_per_month=None,
        features=ENTERPRISE_FEATURES,
        support_level="Dedicated 24/7",
    ),
}


def get_tier_config(tier: Tier) -> TierConfig:
    """Return the TierConfig for the given Tier enum value."""
    return TIER_CATALOGUE[tier.value]


def list_tiers() -> list[TierConfig]:
    """Return all tier configs ordered from cheapest to most expensive."""
    return [TIER_CATALOGUE[t.value] for t in Tier]


def get_upgrade_path(current: Tier) -> Optional[TierConfig]:
    """Return the next higher tier, or None if already at the top."""
    order = list(Tier)
    idx = order.index(current)
    if idx + 1 < len(order):
        return get_tier_config(order[idx + 1])
    return None
