import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, TierConfig, get_tier_config, get_upgrade_path, list_tiers, TIER_CATALOGUE

BOT_FEATURES = {
    Tier.FREE.value: ["1_platform", "10_posts_per_month", "basic_captions", "manual_scheduling"],
    Tier.PRO.value: ["1_platform", "10_posts_per_month", "basic_captions", "manual_scheduling", "5_platforms", "50_posts_per_month", "hashtag_research", "engagement_analytics", "content_calendar"],
    Tier.ENTERPRISE.value: ["1_platform", "10_posts_per_month", "basic_captions", "manual_scheduling", "5_platforms", "50_posts_per_month", "hashtag_research", "engagement_analytics", "content_calendar", "unlimited_platforms", "ai_caption_writing", "auto_scheduling", "competitor_analysis", "multi_account"],
}

def get_bot_tier_info(tier: Tier) -> dict:
    cfg = get_tier_config(tier)
    return {
        "tier": tier.value,
        "name": cfg.name,
        "price_usd_monthly": cfg.price_usd_monthly,
        "requests_per_month": cfg.requests_per_month,
        "features": BOT_FEATURES[tier.value],
        "support_level": cfg.support_level,
    }
