"""
Tier configuration for the Company Lookup Bot.

Tiers:
  - FREE ($0/mo):        Look up 5 companies/day, basic fields (name, domain,
                          description), save to data/companies.json.
  - PRO ($49/mo):        50 companies/day, enriched fields (funding, employees,
                          LinkedIn, Crunchbase), Slack notifications, export CSV.
  - ENTERPRISE ($199/mo): Unlimited lookups, all fields, bulk import, API access,
                           webhook delivery, dedicated support.
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
    """Configuration for a Company Lookup Bot subscription tier.

    Attributes
    ----------
    name : str
        Human-readable tier name.
    tier : Tier
        Enum value.
    price_usd_monthly : float
        Monthly subscription price in USD.
    max_lookups_per_day : int | None
        Max company lookups per day.  None = unlimited.
    features : list[str]
        Feature flags enabled on this tier.
    support_level : str
        Support offering description.
    """

    name: str
    tier: Tier
    price_usd_monthly: float
    max_lookups_per_day: Optional[int]
    features: list
    support_level: str

    def has_feature(self, feature: str) -> bool:
        """Return True if *feature* is available on this tier."""
        return feature in self.features

    def is_unlimited(self) -> bool:
        """Return True if lookups per day are unlimited."""
        return self.max_lookups_per_day is None


# ---------------------------------------------------------------------------
# Feature flags
# ---------------------------------------------------------------------------

FEATURE_BASIC_LOOKUP = "basic_lookup"
FEATURE_ENRICHED_FIELDS = "enriched_fields"
FEATURE_SLACK_NOTIFY = "slack_notify"
FEATURE_EXPORT_CSV = "export_csv"
FEATURE_BULK_IMPORT = "bulk_import"
FEATURE_API_ACCESS = "api_access"
FEATURE_WEBHOOK = "webhook"
FEATURE_DEDICATED_SUPPORT = "dedicated_support"
FEATURE_RECOMMENDATIONS = "recommendations"

FREE_FEATURES: list = [
    FEATURE_BASIC_LOOKUP,
]

PRO_FEATURES: list = FREE_FEATURES + [
    FEATURE_ENRICHED_FIELDS,
    FEATURE_SLACK_NOTIFY,
    FEATURE_EXPORT_CSV,
    FEATURE_RECOMMENDATIONS,
]

ENTERPRISE_FEATURES: list = PRO_FEATURES + [
    FEATURE_BULK_IMPORT,
    FEATURE_API_ACCESS,
    FEATURE_WEBHOOK,
    FEATURE_DEDICATED_SUPPORT,
]

TIER_CATALOGUE: dict = {
    Tier.FREE.value: TierConfig(
        name="Free",
        tier=Tier.FREE,
        price_usd_monthly=0.0,
        max_lookups_per_day=5,
        features=FREE_FEATURES,
        support_level="Community",
    ),
    Tier.PRO.value: TierConfig(
        name="Pro",
        tier=Tier.PRO,
        price_usd_monthly=49.0,
        max_lookups_per_day=50,
        features=PRO_FEATURES,
        support_level="Email (24 h SLA)",
    ),
    Tier.ENTERPRISE.value: TierConfig(
        name="Enterprise",
        tier=Tier.ENTERPRISE,
        price_usd_monthly=199.0,
        max_lookups_per_day=None,
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
