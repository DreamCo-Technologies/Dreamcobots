"""
Token Billing System for DreamCobots.

Provides token-based billing management:
- FREE tier: access to all 109 AI models with a daily token allowance.
- PRO_MONTHLY / PRO_ANNUAL: higher token limits for power users.
- ENTERPRISE_MONTHLY / ENTERPRISE_ANNUAL: unlimited tokens + priority routing.
- Token credit packs for pay-as-you-go usage.

All AI model costs are attributed to the client's token balance so the
platform operates cost-neutrally.
"""

from bots.token_billing.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    list_tiers,
)
from bots.token_billing.token_manager import TokenManager, InsufficientTokensError
from bots.token_billing.subscription_manager import (
    SubscriptionManager,
    SubscriptionError,
)
from bots.token_billing.billing_system import BillingSystem

__all__ = [
    "BillingSystem",
    "InsufficientTokensError",
    "SubscriptionError",
    "SubscriptionManager",
    "Tier",
    "TierConfig",
    "TokenManager",
    "get_tier_config",
    "list_tiers",
]
