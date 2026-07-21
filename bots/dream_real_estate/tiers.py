"""
DreamRealEstate Division Module — Tiers configuration.

Pricing tiers for DreamRealEstate bots:
  - PRO:        SaaS subscription, $99–$299/mo, core features.
  - ENTERPRISE: Institutional-grade, $499/mo, all features + API access.

Tiers map directly to the per-bot tier labels in bots.json so callers can
filter and gate features consistently.
"""
# GLOBAL AI SOURCES FLOW

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class DREtier(Enum):
    """DreamRealEstate subscription tiers."""

    PRO = "Pro"
    ENTERPRISE = "Enterprise"


@dataclass
class DREtierConfig:
    """Configuration for a single DreamRealEstate tier.

    Attributes
    ----------
    name : str
        Human-readable tier name.
    tier : DREtier
        Enum value identifying the tier.
    price_range : str
        Typical monthly price range (e.g. "$99–$299/mo").
    bot_access : str
        Description of which bots are accessible.
    features : List[str]
        Feature flags available at this tier.
    api_access : bool
        Whether programmatic API access is included.
    support_level : str
        Description of support offering.
    """

    name: str
    tier: DREtier
    price_range: str
    bot_access: str
    features: List[str]
    api_access: bool
    support_level: str
    monthly_price_usd: Optional[float] = None

    def has_feature(self, feature: str) -> bool:
        """Return True if *feature* is enabled on this tier."""
        return feature in self.features


# ---------------------------------------------------------------------------
# Tier catalogue
# ---------------------------------------------------------------------------

_PRO_FEATURES: List[str] = [
    "saas_subscription",
    "per_project_fee",
    "per_analysis_fee",
    "dynamic_filters",
    "property_analytics",
    "lease_analysis",
    "portfolio_management",
    "investor_reporting",
    "tax_tools",
    "email_alerts",
    "csv_export",
    "standard_support",
]

_ENTERPRISE_FEATURES: List[str] = [
    *_PRO_FEATURES,
    "enterprise_license",
    "monte_carlo_simulation",
    "institutional_scanning",
    "smart_building_integration",
    "iot_data_ingestion",
    "advanced_valuation_avm",
    "custom_integrations",
    "api_access",
    "dedicated_account_manager",
    "sla_99_9",
    "white_label_reports",
    "priority_support",
]

TIER_CATALOGUE: dict[DREtier, DREtierConfig] = {
    DREtier.PRO: DREtierConfig(
        name="Pro",
        tier=DREtier.PRO,
        price_range="$99–$299/mo",
        monthly_price_usd=199.0,
        bot_access="Access to all Pro-tier bots across 20 categories",
        features=_PRO_FEATURES,
        api_access=False,
        support_level="Email + chat support, 48-hour response SLA",
    ),
    DREtier.ENTERPRISE: DREtierConfig(
        name="Enterprise",
        tier=DREtier.ENTERPRISE,
        price_range="$499/mo",
        monthly_price_usd=499.0,
        bot_access="Access to ALL bots including institutional-grade Enterprise bots",
        features=_ENTERPRISE_FEATURES,
        api_access=True,
        support_level="Dedicated account manager, 4-hour response SLA, 99.9% uptime",
    ),
}


def get_tier_config(tier: DREtier) -> DREtierConfig:
    """Return the :class:`DREtierConfig` for *tier*.

    Raises
    ------
    KeyError
        If *tier* is not in the catalogue (should never happen with valid enum).
    """
    return TIER_CATALOGUE[tier]


def get_upgrade_path(current: DREtier) -> Optional[DREtier]:
    """Return the next tier above *current*, or None if already at the top."""
    order = [DREtier.PRO, DREtier.ENTERPRISE]
    idx = order.index(current)
    return order[idx + 1] if idx + 1 < len(order) else None
