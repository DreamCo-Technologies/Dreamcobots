"""
LeadGenBot — Tier Definitions

Tiers:
  FREE       — 25 leads/day, real estate + directory sources, basic dashboard.
  PRO ($49)  — 2,000 leads/day, all sources, CSV export, pay-per-lead pricing,
               Stripe subscriptions, privacy vault.
  ENTERPRISE ($199) — Unlimited leads, all sources, AI scoring, white-label,
                      advanced security, autonomous workflows, dedicated support.

Pay-Per-Lead pricing (PRO+): $2.00 – $10.00 per lead depending on quality.
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
    max_sources: Optional[int]
    pay_per_lead_min: Optional[float]
    pay_per_lead_max: Optional[float]
    features: list
    support_level: str

    def has_feature(self, feature: str) -> bool:
        return feature in self.features

    def is_unlimited_leads(self) -> bool:
        return self.max_leads_per_day is None


# ---------------------------------------------------------------------------
# Feature constants
# ---------------------------------------------------------------------------

FEATURE_BASIC_SCRAPING = "basic_scraping"
FEATURE_REAL_ESTATE_SCRAPING = "real_estate_scraping"
FEATURE_BUSINESS_DIRECTORY_SCRAPING = "business_directory_scraping"
FEATURE_AGENCY_SCRAPING = "agency_scraping"
FEATURE_FORUM_SCRAPING = "forum_scraping"
FEATURE_MULTI_SOURCE = "multi_source"
FEATURE_LEAD_ENRICHMENT = "lead_enrichment"
FEATURE_AI_SCORING = "ai_scoring"
FEATURE_CSV_EXPORT = "csv_export"
FEATURE_CRM_EXPORT = "crm_export"
FEATURE_DEDUPLICATION = "deduplication"
FEATURE_EMAIL_VALIDATION = "email_validation"
FEATURE_PHONE_VALIDATION = "phone_validation"
FEATURE_STRIPE_SUBSCRIPTIONS = "stripe_subscriptions"
FEATURE_PAY_PER_LEAD = "pay_per_lead"
FEATURE_PRIVACY_VAULT = "privacy_vault"
FEATURE_AUDIT_LOGS = "audit_logs"
FEATURE_AES_ENCRYPTION = "aes_encryption"
FEATURE_AUTONOMOUS_WORKFLOWS = "autonomous_workflows"
FEATURE_WHITE_LABEL = "white_label"
FEATURE_WEBHOOK_EXPORT = "webhook_export"
FEATURE_INDUSTRY_FILTER = "industry_filter"
FEATURE_DASHBOARD = "dashboard"

# ---------------------------------------------------------------------------
# Feature bundles per tier
# ---------------------------------------------------------------------------

FREE_FEATURES = [
    FEATURE_BASIC_SCRAPING,
    FEATURE_REAL_ESTATE_SCRAPING,
    FEATURE_BUSINESS_DIRECTORY_SCRAPING,
    FEATURE_DEDUPLICATION,
    FEATURE_EMAIL_VALIDATION,
    FEATURE_DASHBOARD,
    FEATURE_AUDIT_LOGS,
]

PRO_FEATURES = FREE_FEATURES + [
    FEATURE_AGENCY_SCRAPING,
    FEATURE_FORUM_SCRAPING,
    FEATURE_MULTI_SOURCE,
    FEATURE_LEAD_ENRICHMENT,
    FEATURE_PHONE_VALIDATION,
    FEATURE_CSV_EXPORT,
    FEATURE_CRM_EXPORT,
    FEATURE_STRIPE_SUBSCRIPTIONS,
    FEATURE_PAY_PER_LEAD,
    FEATURE_PRIVACY_VAULT,
    FEATURE_AES_ENCRYPTION,
    FEATURE_INDUSTRY_FILTER,
    FEATURE_WEBHOOK_EXPORT,
]

ENTERPRISE_FEATURES = PRO_FEATURES + [
    FEATURE_AI_SCORING,
    FEATURE_AUTONOMOUS_WORKFLOWS,
    FEATURE_WHITE_LABEL,
]

# ---------------------------------------------------------------------------
# Tier catalogue
# ---------------------------------------------------------------------------

TIER_CATALOGUE = {
    Tier.FREE.value: TierConfig(
        name="Free",
        tier=Tier.FREE,
        price_usd_monthly=0.0,
        max_leads_per_day=25,
        max_sources=2,
        pay_per_lead_min=None,
        pay_per_lead_max=None,
        features=FREE_FEATURES,
        support_level="Community",
    ),
    Tier.PRO.value: TierConfig(
        name="Pro",
        tier=Tier.PRO,
        price_usd_monthly=49.0,
        max_leads_per_day=2_000,
        max_sources=6,
        pay_per_lead_min=2.0,
        pay_per_lead_max=10.0,
        features=PRO_FEATURES,
        support_level="Email (24 h SLA)",
    ),
    Tier.ENTERPRISE.value: TierConfig(
        name="Enterprise",
        tier=Tier.ENTERPRISE,
        price_usd_monthly=199.0,
        max_leads_per_day=None,
        max_sources=None,
        pay_per_lead_min=2.0,
        pay_per_lead_max=10.0,
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


BOT_FEATURES = {
    Tier.FREE.value: FREE_FEATURES,
    Tier.PRO.value: PRO_FEATURES,
    Tier.ENTERPRISE.value: ENTERPRISE_FEATURES,
}


def get_bot_tier_info(tier: Tier) -> dict:
    config = get_tier_config(tier)
    return {
        "tier": tier.value,
        "price_usd_monthly": config.price_usd_monthly,
        "max_leads_per_day": config.max_leads_per_day,
        "features": BOT_FEATURES[tier.value],
    }
