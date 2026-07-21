from enum import Enum
from dataclasses import dataclass
from typing import Optional

class Tier(Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"

FEATURE_PLUGIN_INSTALL = "plugin_install"
FEATURE_ALERTS = "alerts"
FEATURE_ANALYTICS = "analytics"
FEATURE_ENTERPRISE_PLUGINS = "enterprise_plugins"
FEATURE_CUSTOM_PLUGINS = "custom_plugins"
FEATURE_WHITE_LABEL = "white_label"
FEATURE_API_ACCESS = "api_access"

@dataclass
class TierConfig:
    name: str
    tier: Tier
    price_usd_monthly: float
    max_plugins: Optional[int]
    features: list
    support_level: str

    def has_feature(self, feature: str) -> bool:
        return feature in self.features

    def is_unlimited_plugins(self) -> bool:
        return self.max_plugins is None

FREE_FEATURES = [FEATURE_PLUGIN_INSTALL]
PRO_FEATURES = FREE_FEATURES + [FEATURE_ALERTS, FEATURE_ANALYTICS]
ENTERPRISE_FEATURES = PRO_FEATURES + [FEATURE_ENTERPRISE_PLUGINS, FEATURE_CUSTOM_PLUGINS, FEATURE_WHITE_LABEL, FEATURE_API_ACCESS]

TIER_CATALOGUE = {
    Tier.FREE.value: TierConfig(name="Free", tier=Tier.FREE, price_usd_monthly=0.0, max_plugins=3, features=FREE_FEATURES, support_level="Community"),
    Tier.PRO.value: TierConfig(name="Pro", tier=Tier.PRO, price_usd_monthly=49.0, max_plugins=20, features=PRO_FEATURES, support_level="Email (24h SLA)"),
    Tier.ENTERPRISE.value: TierConfig(name="Enterprise", tier=Tier.ENTERPRISE, price_usd_monthly=199.0, max_plugins=None, features=ENTERPRISE_FEATURES, support_level="Dedicated 24/7"),
}

BOT_FEATURES = {
    Tier.FREE.value: ["plugin_install (max 3)", "browse marketplace"],
    Tier.PRO.value: ["plugin_install (max 20)", "alerts", "analytics", "subscriptions", "skill packs"],
    Tier.ENTERPRISE.value: ["unlimited plugins", "alerts", "analytics", "enterprise plugins", "custom plugins", "white_label", "api_access"],
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
