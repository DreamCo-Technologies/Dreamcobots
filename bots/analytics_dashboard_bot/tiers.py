import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, TierConfig, get_tier_config, get_upgrade_path, list_tiers, TIER_CATALOGUE

BOT_FEATURES = {
    Tier.FREE.value: ["3_metrics", "30_day_history", "basic_charts_data", "csv_export"],
    Tier.PRO.value: ["3_metrics", "30_day_history", "basic_charts_data", "csv_export", "20_metrics", "90_day_history", "funnel_analysis", "roi_tracking", "custom_reports"],
    Tier.ENTERPRISE.value: ["3_metrics", "30_day_history", "basic_charts_data", "csv_export", "20_metrics", "90_day_history", "funnel_analysis", "roi_tracking", "custom_reports", "unlimited_metrics", "custom_kpis", "predictive_analytics", "white_label_reports", "api_access"],
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
