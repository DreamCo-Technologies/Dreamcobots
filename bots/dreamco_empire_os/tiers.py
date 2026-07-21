"""
Tier configuration for the DreamCo Empire OS.

Tiers:
  - FREE:       Basic empire management, 10 bots, core modules.
  - PRO ($49):  Full suite, 100 bots, all OS modules, analytics.
  - ENTERPRISE ($199): Unlimited bots, white-label, API access, dedicated support.
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
    """Configuration for a DreamCo Empire OS subscription tier."""

    name: str
    tier: Tier
    price_usd_monthly: float
    max_bots: Optional[int]
    max_divisions: Optional[int]
    features: list
    support_level: str

    def has_feature(self, feature: str) -> bool:
        return feature in self.features

    def is_unlimited_bots(self) -> bool:
        return self.max_bots is None


# ---------------------------------------------------------------------------
# Feature flags
# ---------------------------------------------------------------------------

FEATURE_EMPIRE_HQ = "empire_hq"
FEATURE_DIVISIONS = "divisions"
FEATURE_BOT_FLEET = "bot_fleet"
FEATURE_DEAL_ANALYZER = "deal_analyzer"
FEATURE_FORMULA_VAULT = "formula_vault"
FEATURE_LEARNING_MATRIX = "learning_matrix"
FEATURE_AI_LEADERS = "ai_leaders"
FEATURE_AI_MODELS_HUB = "ai_models_hub"
FEATURE_AI_ECOSYSTEM = "ai_ecosystem"
FEATURE_ORCHESTRATION = "orchestration"
FEATURE_MARKETPLACE = "marketplace"
FEATURE_CRYPTO = "crypto"
FEATURE_PAYMENTS = "payments"
FEATURE_BIZ_LAUNCH = "biz_launch"
FEATURE_CODE_LAB = "code_lab"
FEATURE_LOANS_DEALS = "loans_deals"
FEATURE_DEBUG_INTEL = "debug_intel"
FEATURE_REVENUE = "revenue"
FEATURE_PRICING = "pricing"
FEATURE_CONNECTIONS = "connections"
FEATURE_TIME_CAPSULE = "time_capsule"
FEATURE_COST_TRACKING = "cost_tracking"
FEATURE_AUTONOMY = "autonomy"
FEATURE_WHITE_LABEL = "white_label"
FEATURE_API_ACCESS = "api_access"
FEATURE_DEDICATED_SUPPORT = "dedicated_support"

FREE_FEATURES: list = [
    FEATURE_EMPIRE_HQ,
    FEATURE_DIVISIONS,
    FEATURE_BOT_FLEET,
    FEATURE_DEAL_ANALYZER,
    FEATURE_FORMULA_VAULT,
    FEATURE_REVENUE,
    FEATURE_COST_TRACKING,
]

PRO_FEATURES: list = FREE_FEATURES + [
    FEATURE_LEARNING_MATRIX,
    FEATURE_AI_LEADERS,
    FEATURE_AI_MODELS_HUB,
    FEATURE_AI_ECOSYSTEM,
    FEATURE_ORCHESTRATION,
    FEATURE_MARKETPLACE,
    FEATURE_CRYPTO,
    FEATURE_PAYMENTS,
    FEATURE_BIZ_LAUNCH,
    FEATURE_CODE_LAB,
    FEATURE_LOANS_DEALS,
    FEATURE_DEBUG_INTEL,
    FEATURE_PRICING,
    FEATURE_CONNECTIONS,
    FEATURE_TIME_CAPSULE,
    FEATURE_AUTONOMY,
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
        max_bots=10,
        max_divisions=3,
        features=FREE_FEATURES,
        support_level="Community",
    ),
    Tier.PRO.value: TierConfig(
        name="Pro",
        tier=Tier.PRO,
        price_usd_monthly=49.0,
        max_bots=100,
        max_divisions=20,
        features=PRO_FEATURES,
        support_level="Email (24 h SLA)",
    ),
    Tier.ENTERPRISE.value: TierConfig(
        name="Enterprise",
        tier=Tier.ENTERPRISE,
        price_usd_monthly=199.0,
        max_bots=None,
        max_divisions=None,
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
