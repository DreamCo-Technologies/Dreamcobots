import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, TierConfig, get_tier_config, get_upgrade_path, list_tiers, TIER_CATALOGUE

BOT_FEATURES = {
    Tier.FREE.value: ["supplier_discovery_automation", "vendor_negotiation_scripts", "bulk_order_optimization", "margin_calculator", "moq_tracking", "price_comparison_engine"],
    Tier.PRO.value: ["supplier_discovery_automation", "vendor_negotiation_scripts", "bulk_order_optimization", "margin_calculator", "moq_tracking", "price_comparison_engine", "dropship_integration", "alibaba_faire_api_integration", "real_time_monitoring_dashboard", "automated_error_recovery", "cross_bot_data_sharing", "version_history_tracking"],
    Tier.ENTERPRISE.value: ["supplier_discovery_automation", "vendor_negotiation_scripts", "bulk_order_optimization", "margin_calculator", "moq_tracking", "price_comparison_engine", "dropship_integration", "alibaba_faire_api_integration", "real_time_monitoring_dashboard", "automated_error_recovery", "cross_bot_data_sharing", "version_history_tracking", "performance_benchmarking", "compliance_reporting", "multi_region_deployment", "auto_scaling_resources", "encrypted_data_at_rest", "soc_2_type_ii_compliant"],
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
