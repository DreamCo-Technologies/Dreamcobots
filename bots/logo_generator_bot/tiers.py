import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, TierConfig, get_tier_config, get_upgrade_path, list_tiers, TIER_CATALOGUE

BOT_FEATURES = {
    Tier.FREE.value: ["3_logo_concepts_per_month", "basic_templates", "5_style_options", "jpg_export"],
    Tier.PRO.value: ["3_logo_concepts_per_month", "basic_templates", "5_style_options", "jpg_export", "25_concepts_per_month", "svg_output", "custom_color_palettes", "brand_guide", "10_style_options"],
    Tier.ENTERPRISE.value: ["3_logo_concepts_per_month", "basic_templates", "5_style_options", "jpg_export", "25_concepts_per_month", "svg_output", "custom_color_palettes", "brand_guide", "10_style_options", "unlimited_concepts", "animated_logos", "white_label", "bulk_generation", "api_export"],
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
