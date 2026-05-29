import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, TierConfig, get_tier_config, get_upgrade_path, list_tiers, TIER_CATALOGUE

BOT_FEATURES = {
    Tier.FREE.value: ["pre_foreclosure_detection", "public_records_search_automation", "distressed_property_scoring", "owner_contact_data_enrichment", "equity_stack_analysis", "auction_calendar_tracking"],
    Tier.PRO.value: ["pre_foreclosure_detection", "public_records_search_automation", "distressed_property_scoring", "owner_contact_data_enrichment", "equity_stack_analysis", "auction_calendar_tracking", "skip_tracing_integration", "reo_portfolio_identification", "real_time_monitoring_dashboard", "automated_error_recovery", "cross_bot_data_sharing", "version_history_tracking"],
    Tier.ENTERPRISE.value: ["pre_foreclosure_detection", "public_records_search_automation", "distressed_property_scoring", "owner_contact_data_enrichment", "equity_stack_analysis", "auction_calendar_tracking", "skip_tracing_integration", "reo_portfolio_identification", "real_time_monitoring_dashboard", "automated_error_recovery", "cross_bot_data_sharing", "version_history_tracking", "performance_benchmarking", "compliance_reporting", "multi_region_deployment", "auto_scaling_resources", "encrypted_data_at_rest", "soc_2_type_ii_compliant"],
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
