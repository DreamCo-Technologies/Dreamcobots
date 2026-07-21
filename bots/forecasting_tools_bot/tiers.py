import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, TierConfig, get_tier_config, get_upgrade_path, list_tiers, TIER_CATALOGUE

BOT_FEATURES = {
    Tier.FREE.value: ["3_month_forecast", "single_metric", "trend_analysis"],
    Tier.PRO.value: ["3_month_forecast", "single_metric", "trend_analysis", "12_month_forecast", "multiple_metrics", "seasonality_detection", "confidence_intervals"],
    Tier.ENTERPRISE.value: ["3_month_forecast", "single_metric", "trend_analysis", "12_month_forecast", "multiple_metrics", "seasonality_detection", "confidence_intervals", "unlimited_forecasting", "ml_powered", "scenario_planning", "integrated_dashboards"],
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
