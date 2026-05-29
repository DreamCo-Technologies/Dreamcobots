import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, TierConfig, get_tier_config, get_upgrade_path, list_tiers, TIER_CATALOGUE

BOT_FEATURES = {
    Tier.FREE.value: ["trial_conversion_optimization", "upgrade_downgrade_flow_automation", "pause_resume_handling", "smart_dunning_sequences", "renewal_reminder_automation", "failed_payment_recovery"],
    Tier.PRO.value: ["trial_conversion_optimization", "upgrade_downgrade_flow_automation", "pause_resume_handling", "smart_dunning_sequences", "renewal_reminder_automation", "failed_payment_recovery", "cancellation_flow_optimizer", "stripe_billing_recurly_integration", "real_time_monitoring_dashboard", "automated_error_recovery", "cross_bot_data_sharing", "version_history_tracking"],
    Tier.ENTERPRISE.value: ["trial_conversion_optimization", "upgrade_downgrade_flow_automation", "pause_resume_handling", "smart_dunning_sequences", "renewal_reminder_automation", "failed_payment_recovery", "cancellation_flow_optimizer", "stripe_billing_recurly_integration", "real_time_monitoring_dashboard", "automated_error_recovery", "cross_bot_data_sharing", "version_history_tracking", "performance_benchmarking", "compliance_reporting", "multi_region_deployment", "auto_scaling_resources", "encrypted_data_at_rest", "soc_2_type_ii_compliant"],
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
