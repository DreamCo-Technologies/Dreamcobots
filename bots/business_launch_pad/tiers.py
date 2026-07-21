"""
Tier definitions for the Business Launch Pad bot.

Tiers:
  - FREE:       Plan generator only, max 3 plans/month.
  - PRO:        All main tools, max 50 plans/month.
  - ENTERPRISE: Everything unlimited, white-label, API access.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional


class Tier(Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


# ---------------------------------------------------------------------------
# Feature flags
# ---------------------------------------------------------------------------

FEATURE_PLAN_GENERATOR = "plan_generator"
FEATURE_MARKET_RESEARCH = "market_research"
FEATURE_LEGAL_FORMATION = "legal_formation"
FEATURE_BRAND_IDENTITY = "brand_identity"
FEATURE_WEBSITE_SETUP = "website_setup"
FEATURE_FINANCIAL_PROJECTIONS = "financial_projections"
FEATURE_PITCH_DECK = "pitch_deck"
FEATURE_TAM_ANALYSIS = "tam_analysis"
FEATURE_SWOT_ANALYSIS = "swot_analysis"
FEATURE_COMPLIANCE_MONITORING = "compliance_monitoring"
FEATURE_WHITE_LABEL = "white_label"
FEATURE_API_ACCESS = "api_access"

FREE_FEATURES = [
    FEATURE_PLAN_GENERATOR,
]

PRO_FEATURES = FREE_FEATURES + [
    FEATURE_MARKET_RESEARCH,
    FEATURE_LEGAL_FORMATION,
    FEATURE_BRAND_IDENTITY,
    FEATURE_WEBSITE_SETUP,
    FEATURE_FINANCIAL_PROJECTIONS,
    FEATURE_PITCH_DECK,
    FEATURE_TAM_ANALYSIS,
    FEATURE_SWOT_ANALYSIS,
]

ENTERPRISE_FEATURES = PRO_FEATURES + [
    FEATURE_COMPLIANCE_MONITORING,
    FEATURE_WHITE_LABEL,
    FEATURE_API_ACCESS,
]

BOT_FEATURES = {
    Tier.FREE.value: FREE_FEATURES,
    Tier.PRO.value: PRO_FEATURES,
    Tier.ENTERPRISE.value: ENTERPRISE_FEATURES,
}


@dataclass
class TierConfig:
    """Configuration for a Business Launch Pad subscription tier."""

    name: str
    tier: Tier
    price_usd_monthly: float
    features: list
    max_plans_per_month: Optional[int]  # None = unlimited

    def has_feature(self, feature: str) -> bool:
        return feature in self.features

    def is_unlimited(self) -> bool:
        return self.max_plans_per_month is None


TIER_CATALOGUE: dict[str, TierConfig] = {
    Tier.FREE.value: TierConfig(
        name="Free",
        tier=Tier.FREE,
        price_usd_monthly=0.0,
        features=FREE_FEATURES,
        max_plans_per_month=3,
    ),
    Tier.PRO.value: TierConfig(
        name="Pro",
        tier=Tier.PRO,
        price_usd_monthly=49.0,
        features=PRO_FEATURES,
        max_plans_per_month=50,
    ),
    Tier.ENTERPRISE.value: TierConfig(
        name="Enterprise",
        tier=Tier.ENTERPRISE,
        price_usd_monthly=199.0,
        features=ENTERPRISE_FEATURES,
        max_plans_per_month=None,
    ),
}


def get_tier_config(tier: Tier) -> TierConfig:
    """Return the TierConfig for the given Tier enum value."""
    return TIER_CATALOGUE[tier.value]


def list_tiers() -> list[TierConfig]:
    """Return all tier configs ordered from cheapest to most expensive."""
    return [TIER_CATALOGUE[t.value] for t in Tier]
