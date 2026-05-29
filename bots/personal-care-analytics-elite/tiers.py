import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, TierConfig, get_tier_config, get_upgrade_path, list_tiers, TIER_CATALOGUE

BOT_FEATURES = {
    Tier.FREE.value: ["client_lifetime_value_modeling", "market_positioning_analysis", "service_demand_forecasting", "staff_productivity_optimization", "revenue_per_client_analytics", "multi_location_benchmarking", "advanced_analytics_dashboard", "priority_email_support", "api_access", "custom_integrations", "webhook_notifications", "data_export_csv_json"],
    Tier.PRO.value: ["client_lifetime_value_modeling", "market_positioning_analysis", "service_demand_forecasting", "staff_productivity_optimization", "revenue_per_client_analytics", "multi_location_benchmarking", "advanced_analytics_dashboard", "priority_email_support", "api_access", "custom_integrations", "webhook_notifications", "data_export_csv_json", "scheduled_automations", "multi_user_access", "dedicated_account_manager", "sla_guarantee_99_99", "custom_model_fine_tuning", "sso_saml_authentication", "audit_logging", "role_based_access_control", "white_label_options", "on_premise_deployment_option", "feature_24_7_phone_support", "custom_ai_model_training", "unlimited_api_calls"],
    Tier.ENTERPRISE.value: ["client_lifetime_value_modeling", "market_positioning_analysis", "service_demand_forecasting", "staff_productivity_optimization", "revenue_per_client_analytics", "multi_location_benchmarking", "advanced_analytics_dashboard", "priority_email_support", "api_access", "custom_integrations", "webhook_notifications", "data_export_csv_json", "scheduled_automations", "multi_user_access", "dedicated_account_manager", "sla_guarantee_99_99", "custom_model_fine_tuning", "sso_saml_authentication", "audit_logging", "role_based_access_control", "white_label_options", "on_premise_deployment_option", "feature_24_7_phone_support", "custom_ai_model_training", "unlimited_api_calls", "dedicated_infrastructure", "quarterly_business_reviews", "early_access_to_features", "real_time_monitoring_dashboard", "automated_error_recovery", "cross_bot_data_sharing", "version_history_tracking", "performance_benchmarking", "compliance_reporting", "multi_region_deployment", "auto_scaling_resources", "encrypted_data_at_rest", "soc_2_type_ii_compliant"],
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
