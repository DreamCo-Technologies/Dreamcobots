"""
Tier configuration for the Global Bot Communication Network (GBN).

Tiers:
  - FREE:        Connect up to 5 bots, basic UBP messaging, read-only dashboard,
                 1 external API integration, basic bot verification.
  - PRO ($49):   Up to 50 bots, full UBP features, real-time dashboard, 5 API
                 integrations, advanced verification, rate-limit controls.
  - ENTERPRISE ($199): Unlimited bots, full API gateway suite, white-label
                 dashboard, marketplace access, trusted-bot status, priority support.
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
    name: str
    tier: Tier
    price_usd_monthly: float
    max_bots: Optional[int]            # None = unlimited
    max_api_integrations: Optional[int]
    max_messages_per_minute: int
    features: list = field(default_factory=list)
    support_level: str = "community"

    def has_feature(self, feature: str) -> bool:
        return feature in self.features

    def is_unlimited_bots(self) -> bool:
        return self.max_bots is None


# ---------------------------------------------------------------------------
# Feature flags
# ---------------------------------------------------------------------------

FEATURE_UBP_MESSAGING = "ubp_messaging"
FEATURE_BOT_REGISTRY = "bot_registry"
FEATURE_BASIC_DASHBOARD = "basic_dashboard"
FEATURE_REALTIME_DASHBOARD = "realtime_dashboard"
FEATURE_EARNINGS_TRACKER = "earnings_tracker"
FEATURE_KILL_SWITCH = "kill_switch"
FEATURE_ACTIVITY_LOGS = "activity_logs"
FEATURE_RATE_LIMITING = "rate_limiting"
FEATURE_PERMISSIONS = "permissions"
FEATURE_BASIC_VERIFICATION = "basic_verification"
FEATURE_ADVANCED_VERIFICATION = "advanced_verification"
FEATURE_TRUSTED_BOT_STATUS = "trusted_bot_status"
FEATURE_SLACK_INTEGRATION = "slack_integration"
FEATURE_DISCORD_INTEGRATION = "discord_integration"
FEATURE_OPENAI_INTEGRATION = "openai_integration"
FEATURE_TRELLO_INTEGRATION = "trello_integration"
FEATURE_NOTION_INTEGRATION = "notion_integration"
FEATURE_FULL_API_GATEWAY = "full_api_gateway"
FEATURE_MARKETPLACE = "marketplace"
FEATURE_MARKETPLACE_SELL = "marketplace_sell"
FEATURE_BOT_SUBSCRIPTIONS = "bot_subscriptions"
FEATURE_WHITE_LABEL = "white_label"
FEATURE_STRIPE_BILLING = "stripe_billing"

FREE_FEATURES = [
    FEATURE_UBP_MESSAGING,
    FEATURE_BOT_REGISTRY,
    FEATURE_BASIC_DASHBOARD,
    FEATURE_ACTIVITY_LOGS,
    FEATURE_BASIC_VERIFICATION,
    FEATURE_SLACK_INTEGRATION,
]

PRO_FEATURES = FREE_FEATURES + [
    FEATURE_REALTIME_DASHBOARD,
    FEATURE_EARNINGS_TRACKER,
    FEATURE_KILL_SWITCH,
    FEATURE_RATE_LIMITING,
    FEATURE_PERMISSIONS,
    FEATURE_ADVANCED_VERIFICATION,
    FEATURE_DISCORD_INTEGRATION,
    FEATURE_OPENAI_INTEGRATION,
    FEATURE_TRELLO_INTEGRATION,
    FEATURE_NOTION_INTEGRATION,
    FEATURE_MARKETPLACE,
    FEATURE_STRIPE_BILLING,
]

ENTERPRISE_FEATURES = PRO_FEATURES + [
    FEATURE_FULL_API_GATEWAY,
    FEATURE_TRUSTED_BOT_STATUS,
    FEATURE_MARKETPLACE_SELL,
    FEATURE_BOT_SUBSCRIPTIONS,
    FEATURE_WHITE_LABEL,
]

_CONFIGS = {
    Tier.FREE: TierConfig(
        name="Free",
        tier=Tier.FREE,
        price_usd_monthly=0.0,
        max_bots=5,
        max_api_integrations=1,
        max_messages_per_minute=10,
        features=FREE_FEATURES,
        support_level="community",
    ),
    Tier.PRO: TierConfig(
        name="Pro",
        tier=Tier.PRO,
        price_usd_monthly=49.0,
        max_bots=50,
        max_api_integrations=5,
        max_messages_per_minute=100,
        features=PRO_FEATURES,
        support_level="email",
    ),
    Tier.ENTERPRISE: TierConfig(
        name="Enterprise",
        tier=Tier.ENTERPRISE,
        price_usd_monthly=199.0,
        max_bots=None,
        max_api_integrations=None,
        max_messages_per_minute=1000,
        features=ENTERPRISE_FEATURES,
        support_level="priority",
    ),
}


def get_tier_config(tier: Tier) -> TierConfig:
    """Return the TierConfig for the given tier."""
    return _CONFIGS[tier]


def list_tiers() -> list:
    """Return all available tiers."""
    return list(_CONFIGS.values())


def get_upgrade_path(current_tier: Tier) -> Optional[Tier]:
    """Return the next tier above the current one, or None if already max."""
    order = [Tier.FREE, Tier.PRO, Tier.ENTERPRISE]
    idx = order.index(current_tier)
    return order[idx + 1] if idx + 1 < len(order) else None
