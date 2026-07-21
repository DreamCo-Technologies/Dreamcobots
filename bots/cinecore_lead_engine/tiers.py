"""
Tier configuration for the CineCore Lead Engine Bot.

Tiers:
  - FREE:             100 leads/day, basic business scanning, script generation.
  - PRO ($29):        2,000 leads/day, scoring, outreach drafts, CRM export.
  - ENTERPRISE ($99): Unlimited leads, bulk generation, analytics, white-label.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Tier(Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


@dataclass
class TierConfig:
    name: str
    tier: Tier
    price_usd_monthly: float
    max_leads_per_day: Optional[int]
    features: list
    support_level: str

    def has_feature(self, feature: str) -> bool:
        return feature in self.features

    def is_unlimited_leads(self) -> bool:
        return self.max_leads_per_day is None


# Feature constants
FEATURE_BUSINESS_SCAN = "business_scan"
FEATURE_SCRIPT_GENERATION = "script_generation"
FEATURE_LEAD_SCORING = "lead_scoring"
FEATURE_OUTREACH_DRAFT = "outreach_draft"
FEATURE_CRM_EXPORT = "crm_export"
FEATURE_BULK_GENERATION = "bulk_generation"
FEATURE_ANALYTICS = "analytics"
FEATURE_WHITE_LABEL = "white_label"
FEATURE_NICHE_FILTER = "niche_filter"
FEATURE_AD_PACKAGE = "ad_package"

FREE_FEATURES = [
    FEATURE_BUSINESS_SCAN,
    FEATURE_SCRIPT_GENERATION,
]

PRO_FEATURES = FREE_FEATURES + [
    FEATURE_LEAD_SCORING,
    FEATURE_OUTREACH_DRAFT,
    FEATURE_CRM_EXPORT,
    FEATURE_NICHE_FILTER,
    FEATURE_AD_PACKAGE,
]

ENTERPRISE_FEATURES = PRO_FEATURES + [
    FEATURE_BULK_GENERATION,
    FEATURE_ANALYTICS,
    FEATURE_WHITE_LABEL,
]

TIER_CATALOGUE = {
    Tier.FREE.value: TierConfig(
        name="Free",
        tier=Tier.FREE,
        price_usd_monthly=0.0,
        max_leads_per_day=100,
        features=FREE_FEATURES,
        support_level="Community",
    ),
    Tier.PRO.value: TierConfig(
        name="Pro",
        tier=Tier.PRO,
        price_usd_monthly=29.0,
        max_leads_per_day=2_000,
        features=PRO_FEATURES,
        support_level="Email (24 h SLA)",
    ),
    Tier.ENTERPRISE.value: TierConfig(
        name="Enterprise",
        tier=Tier.ENTERPRISE,
        price_usd_monthly=99.0,
        max_leads_per_day=None,
        features=ENTERPRISE_FEATURES,
        support_level="Dedicated 24/7",
    ),
}


def get_tier_config(tier: Tier) -> TierConfig:
    return TIER_CATALOGUE[tier.value]


def list_tiers() -> list:
    return [TIER_CATALOGUE[t.value] for t in Tier]


def get_upgrade_path(current: Tier) -> Optional[TierConfig]:
    order = list(Tier)
    idx = order.index(current)
    if idx + 1 < len(order):
        return get_tier_config(order[idx + 1])
    return None
