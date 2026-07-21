import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, TierConfig, get_tier_config, get_upgrade_path, list_tiers, TIER_CATALOGUE

BOT_FEATURES = {
    Tier.FREE.value: ["responsive_design_generation", "talking_website_creation", "seo_optimization", "accessibility_compliance", "framework_selection", "component_library", "api_integration", "database_design", "deployment_automation", "performance_optimization"],
    Tier.PRO.value: ["responsive_design_generation", "talking_website_creation", "seo_optimization", "accessibility_compliance", "framework_selection", "component_library", "api_integration", "database_design", "deployment_automation", "performance_optimization", "progressive_web_app_creation", "voice_ui_integration", "advanced_analytics_dashboard", "priority_email_support", "api_access", "custom_integrations", "webhook_notifications", "data_export_csv_json", "scheduled_automations", "multi_user_access"],
    Tier.ENTERPRISE.value: ["responsive_design_generation", "talking_website_creation", "seo_optimization", "accessibility_compliance", "framework_selection", "component_library", "api_integration", "database_design", "deployment_automation", "performance_optimization", "progressive_web_app_creation", "voice_ui_integration", "advanced_analytics_dashboard", "priority_email_support", "api_access", "custom_integrations", "webhook_notifications", "data_export_csv_json", "scheduled_automations", "multi_user_access", "real_time_monitoring_dashboard", "automated_error_recovery", "cross_bot_data_sharing", "version_history_tracking", "performance_benchmarking", "compliance_reporting", "multi_region_deployment", "auto_scaling_resources", "encrypted_data_at_rest", "soc_2_type_ii_compliant"],
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
