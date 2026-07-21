from enum import Enum
from dataclasses import dataclass, field
from typing import Optional

class Tier(Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"

FEATURE_REVENUE_TRACKING = "revenue_tracking"
FEATURE_GROWTH_ANALYSIS = "growth_analysis"
FEATURE_API_METRICS = "api_metrics"
FEATURE_BOT_INSIGHTS = "bot_insights"
FEATURE_EXPORTS = "exports"
FEATURE_REAL_TIME = "real_time"
FEATURE_PREDICTIVE = "predictive"
FEATURE_WHITE_LABEL = "white_label"
FEATURE_API_ACCESS = "api_access"

@dataclass
class TierConfig:
    name: str
    tier: Tier
    price_usd_monthly: float
    features: list
    support_level: str

    def has_feature(self, feature: str) -> bool:
        return feature in self.features

FREE_FEATURES = [FEATURE_REVENUE_TRACKING]
PRO_FEATURES = FREE_FEATURES + [FEATURE_GROWTH_ANALYSIS, FEATURE_API_METRICS, FEATURE_BOT_INSIGHTS, FEATURE_EXPORTS, FEATURE_REAL_TIME]
ENTERPRISE_FEATURES = PRO_FEATURES + [FEATURE_PREDICTIVE, FEATURE_WHITE_LABEL, FEATURE_API_ACCESS]

TIER_CATALOGUE = {
    Tier.FREE.value: TierConfig(name="Free", tier=Tier.FREE, price_usd_monthly=0.0, features=FREE_FEATURES, support_level="Community"),
    Tier.PRO.value: TierConfig(name="Pro", tier=Tier.PRO, price_usd_monthly=49.0, features=PRO_FEATURES, support_level="Email (24h SLA)"),
    Tier.ENTERPRISE.value: TierConfig(name="Enterprise", tier=Tier.ENTERPRISE, price_usd_monthly=199.0, features=ENTERPRISE_FEATURES, support_level="Dedicated 24/7"),
}

BOT_FEATURES = {
    Tier.FREE.value: ["revenue_tracking", "basic dashboard"],
    Tier.PRO.value: ["revenue_tracking", "growth_analysis", "api_metrics", "bot_insights", "exports", "real_time", "basic dashboard"],
    Tier.ENTERPRISE.value: ["revenue_tracking", "growth_analysis", "api_metrics", "bot_insights", "exports", "real_time", "predictive", "white_label", "api_access", "basic dashboard"],
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
