"""
Tier configuration for the DreamCo Family Resource & Survival GPS (211 Bot).

Tiers:
  - FREE:       Basic resource search, standard map, limited results.
  - PRO:        Advanced filtering, route planning, AI resource matching,
                real-time crowd data, neighborhood safety scores.
  - ENTERPRISE: Full GPS features, live data feeds, white-label, dedicated
                support, custom integrations.
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

FEATURE_RESOURCE_SEARCH = "resource_search"
FEATURE_GPS_MAP = "gps_map"
FEATURE_BUILDING_INTEL_PANELS = "building_intelligence_panels"
FEATURE_ADVANCED_FILTERING = "advanced_filtering"
FEATURE_ROUTE_PLANNING = "route_planning"
FEATURE_RIDESHARE_COST_ESTIMATE = "rideshare_cost_estimate"
FEATURE_CROWD_REPORTING = "crowd_reporting"
FEATURE_SUPPLY_ALERTS = "supply_alerts"
FEATURE_SAFETY_SCORE = "neighborhood_safety_score"
FEATURE_AI_RESOURCE_MATCHING = "ai_resource_matching"
FEATURE_REAL_TIME_DATA = "real_time_data"
FEATURE_FAMILY_GPS = "family_gps_signals"
FEATURE_PANIC_BUTTON = "panic_button"
FEATURE_ARRIVAL_ALERTS = "arrival_alerts"
FEATURE_PREMIUM_MEMBERSHIP = "premium_membership"
FEATURE_SPONSORED_LISTINGS = "sponsored_listings"
FEATURE_AFFILIATE_PROGRAMS = "affiliate_programs"
FEATURE_WHITE_LABEL = "white_label"
FEATURE_CUSTOM_INTEGRATIONS = "custom_integrations"
FEATURE_ANALYTICS_DASHBOARD = "analytics_dashboard"

FREE_FEATURES = [
    FEATURE_RESOURCE_SEARCH,
    FEATURE_GPS_MAP,
]

PRO_FEATURES = FREE_FEATURES + [
    FEATURE_BUILDING_INTEL_PANELS,
    FEATURE_ADVANCED_FILTERING,
    FEATURE_ROUTE_PLANNING,
    FEATURE_RIDESHARE_COST_ESTIMATE,
    FEATURE_CROWD_REPORTING,
    FEATURE_SUPPLY_ALERTS,
    FEATURE_SAFETY_SCORE,
    FEATURE_AI_RESOURCE_MATCHING,
    FEATURE_FAMILY_GPS,
    FEATURE_PANIC_BUTTON,
    FEATURE_ARRIVAL_ALERTS,
    FEATURE_PREMIUM_MEMBERSHIP,
    FEATURE_ANALYTICS_DASHBOARD,
]

ENTERPRISE_FEATURES = PRO_FEATURES + [
    FEATURE_REAL_TIME_DATA,
    FEATURE_SPONSORED_LISTINGS,
    FEATURE_AFFILIATE_PROGRAMS,
    FEATURE_WHITE_LABEL,
    FEATURE_CUSTOM_INTEGRATIONS,
]

# ---------------------------------------------------------------------------
# Resource categories surfaced in the GPS layers
# ---------------------------------------------------------------------------

RESOURCE_CATEGORIES = [
    "food",
    "shelter",
    "job_assistance",
    "legal_aid",
    "financial_literacy",
    "healthcare",
    "childcare",
    "transportation",
    "clothing",
    "mental_health",
]

# ---------------------------------------------------------------------------
# Data source integrations
# ---------------------------------------------------------------------------

DATA_SOURCE_211 = "211"
DATA_SOURCE_FEEDING_AMERICA = "feeding_america"
DATA_SOURCE_HUD = "hud"
DATA_SOURCE_AMERICAN_JOB_CENTERS = "american_job_centers"
DATA_SOURCE_OPEN_STREET_MAP = "open_street_map"
DATA_SOURCE_GOOGLE_MAPS = "google_maps"

FREE_DATA_SOURCES = [DATA_SOURCE_211, DATA_SOURCE_OPEN_STREET_MAP]
PRO_DATA_SOURCES = FREE_DATA_SOURCES + [
    DATA_SOURCE_FEEDING_AMERICA,
    DATA_SOURCE_HUD,
    DATA_SOURCE_AMERICAN_JOB_CENTERS,
    DATA_SOURCE_GOOGLE_MAPS,
]
ENTERPRISE_DATA_SOURCES = PRO_DATA_SOURCES  # same sources; custom feeds added via API

# ---------------------------------------------------------------------------
# GPS map result limits per tier
# ---------------------------------------------------------------------------

FREE_MAX_RESULTS = 10
PRO_MAX_RESULTS = 50
ENTERPRISE_MAX_RESULTS = None  # unlimited


# ---------------------------------------------------------------------------
# Tier config dataclass
# ---------------------------------------------------------------------------

@dataclass
class TierConfig:
    """Configuration for a 211-bot subscription tier.

    Attributes
    ----------
    name : str
        Human-readable tier name.
    tier : Tier
        Enum value identifying the tier.
    price_usd_monthly : float
        Monthly subscription price in USD.
    max_results : int | None
        Maximum GPS search results per query.  ``None`` = unlimited.
    features : list[str]
        Feature flags enabled on this tier.
    data_sources : list[str]
        Integrated data sources available on this tier.
    support_level : str
        Description of the support offering.
    """

    name: str
    tier: Tier
    price_usd_monthly: float
    max_results: Optional[int]
    features: list
    data_sources: list
    support_level: str

    def is_unlimited(self) -> bool:
        return self.max_results is None

    def has_feature(self, feature: str) -> bool:
        return feature in self.features

    def has_data_source(self, source: str) -> bool:
        return source in self.data_sources


# ---------------------------------------------------------------------------
# Tier catalogue
# ---------------------------------------------------------------------------

TIER_CATALOGUE: dict[str, TierConfig] = {
    Tier.FREE.value: TierConfig(
        name="Free",
        tier=Tier.FREE,
        price_usd_monthly=0.0,
        max_results=FREE_MAX_RESULTS,
        features=FREE_FEATURES,
        data_sources=FREE_DATA_SOURCES,
        support_level="Community",
    ),
    Tier.PRO.value: TierConfig(
        name="Pro",
        tier=Tier.PRO,
        price_usd_monthly=29.0,
        max_results=PRO_MAX_RESULTS,
        features=PRO_FEATURES,
        data_sources=PRO_DATA_SOURCES,
        support_level="Email (48 h SLA)",
    ),
    Tier.ENTERPRISE.value: TierConfig(
        name="Enterprise",
        tier=Tier.ENTERPRISE,
        price_usd_monthly=199.0,
        max_results=ENTERPRISE_MAX_RESULTS,
        features=ENTERPRISE_FEATURES,
        data_sources=ENTERPRISE_DATA_SOURCES,
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
