"""Marketing Bot package."""

from .marketing_bot import MarketingBot, MarketingTierError, MarketingRequestLimitError
from .tiers import get_marketing_tier_info, MARKETING_EXTRA_FEATURES, MARKETING_CHANNELS

__all__ = [
    "MarketingBot",
    "MarketingTierError",
    "MarketingRequestLimitError",
    "get_marketing_tier_info",
    "MARKETING_EXTRA_FEATURES",
    "MARKETING_CHANNELS",
]
