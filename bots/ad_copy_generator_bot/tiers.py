import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, TierConfig, get_tier_config, get_upgrade_path, list_tiers, TIER_CATALOGUE

BOT_FEATURES = {
    Tier.FREE.value: ["5_ads_per_month", "2_platforms", "basic_templates", "standard_cta"],
    Tier.PRO.value: ["5_ads_per_month", "2_platforms", "basic_templates", "standard_cta", "50_ads_per_month", "all_platforms", "ab_variants", "ctr_estimation", "advanced_targeting"],
    Tier.ENTERPRISE.value: ["5_ads_per_month", "2_platforms", "basic_templates", "standard_cta", "50_ads_per_month", "all_platforms", "ab_variants", "ctr_estimation", "advanced_targeting", "unlimited_ads", "multilingual_copy", "performance_tracking", "competitor_analysis", "white_label"],
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
