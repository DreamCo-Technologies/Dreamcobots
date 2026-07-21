"""
DreamSalesPro Division Module — Tiers configuration.

Pricing tiers for DreamSalesPro bots:
  - PRO:        SaaS subscription, $149–$249/mo, core outreach & pipeline features.
  - ENTERPRISE: Full platform, $499/mo, all bots + white-label + API access.

Tiers map directly to the per-bot tier labels in bots.json.
"""
# GLOBAL AI SOURCES FLOW

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class DSPtier(Enum):
    """DreamSalesPro subscription tiers."""

    PRO = "Pro"
    ENTERPRISE = "Enterprise"


@dataclass
class DSPtierConfig:
    """Configuration for a single DreamSalesPro tier.

    Attributes
    ----------
    name : str
        Human-readable tier name.
    tier : DSPtier
        Enum value identifying the tier.
    price_range : str
        Typical monthly price range.
    bot_access : str
        Description of which bots are accessible.
    features : List[str]
        Feature flags available at this tier.
    api_access : bool
        Whether programmatic API access is included.
    support_level : str
        Description of support offering.
    monthly_price_usd : float | None
        Representative monthly price in USD.
    """

    name: str
    tier: DSPtier
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
    "cold_email_sequences",
    "multi_channel_outreach",
    "lead_scraping",
    "icp_builder",
    "lead_verification",
    "deliverability_management",
    "pipeline_management",
    "appointment_setting",
    "campaign_roi_analytics",
    "landing_page_builder",
    "funnel_optimization",
    "billing_automation",
    "subscription_lifecycle",
    "objection_handler_ai",
    "standard_support",
]

_ENTERPRISE_FEATURES: List[str] = [
    *_PRO_FEATURES,
    "enterprise_license",
    "white_label_saas",
    "custom_domain_support",
    "multi_client_management",
    "revenue_tracking_engine",
    "market_intelligence",
    "predictive_analytics",
    "cro_engine",
    "deal_intelligence",
    "pitch_craft_ai",
    "risk_compliance_monitor",
    "sales_performance_tracker",
    "client_success_ai",
    "api_access",
    "dedicated_account_manager",
    "sla_99_9",
    "rbac",
    "priority_support",
]

TIER_CATALOGUE: dict[DSPtier, DSPtierConfig] = {
    DSPtier.PRO: DSPtierConfig(
        name="Pro",
        tier=DSPtier.PRO,
        price_range="$149–$249/mo",
        monthly_price_usd=199.0,
        bot_access="Access to all Pro-tier bots across 8 categories",
        features=_PRO_FEATURES,
        api_access=False,
        support_level="Email + chat support, 48-hour response SLA",
    ),
    DSPtier.ENTERPRISE: DSPtierConfig(
        name="Enterprise",
        tier=DSPtier.ENTERPRISE,
        price_range="$499/mo",
        monthly_price_usd=499.0,
        bot_access="Access to ALL bots including white-label and enterprise-grade bots",
        features=_ENTERPRISE_FEATURES,
        api_access=True,
        support_level="Dedicated account manager, 4-hour response SLA, 99.9% uptime",
    ),
}


def get_tier_config(tier: DSPtier) -> DSPtierConfig:
    """Return the :class:`DSPtierConfig` for *tier*.

    Raises
    ------
    KeyError
        If *tier* is not in the catalogue.
    """
    return TIER_CATALOGUE[tier]


def get_upgrade_path(current: DSPtier) -> Optional[DSPtier]:
    """Return the next tier above *current*, or None if already at the top."""
    order = [DSPtier.PRO, DSPtier.ENTERPRISE]
    idx = order.index(current)
    return order[idx + 1] if idx + 1 < len(order) else None
