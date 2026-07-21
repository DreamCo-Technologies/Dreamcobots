import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, TierConfig, get_tier_config, get_upgrade_path, list_tiers, TIER_CATALOGUE

BOT_FEATURES = {
    Tier.FREE.value: ["500_subscribers", "2_campaigns_per_month", "basic_templates", "simple_analytics"],
    Tier.PRO.value: ["500_subscribers", "2_campaigns_per_month", "basic_templates", "simple_analytics", "10000_subscribers", "10_campaigns_per_month", "ab_testing", "open_rate_tracking", "segmentation"],
    Tier.ENTERPRISE.value: ["500_subscribers", "2_campaigns_per_month", "basic_templates", "simple_analytics", "10000_subscribers", "10_campaigns_per_month", "ab_testing", "open_rate_tracking", "segmentation", "unlimited_subscribers", "drip_sequences", "automation_triggers", "advanced_segmentation", "white_label"],
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
