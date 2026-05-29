import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, TierConfig, get_tier_config, get_upgrade_path, list_tiers, TIER_CATALOGUE

BOT_FEATURES = {
    Tier.FREE.value: ["cross_entity_governance_audit", "practice_consistency_checking", "regulatory_alignment_scoring", "remediation_priority_ranking", "governance_maturity_assessment", "advanced_analytics_dashboard", "priority_email_support", "api_access", "custom_integrations", "webhook_notifications"],
    Tier.PRO.value: ["cross_entity_governance_audit", "practice_consistency_checking", "regulatory_alignment_scoring", "remediation_priority_ranking", "governance_maturity_assessment", "advanced_analytics_dashboard", "priority_email_support", "api_access", "custom_integrations", "webhook_notifications", "data_export_csv_json", "scheduled_automations", "multi_user_access", "dedicated_account_manager", "sla_guarantee_99_9", "custom_model_fine_tuning", "sso_saml_authentication", "audit_logging", "role_based_access_control", "white_label_options"],
    Tier.ENTERPRISE.value: ["cross_entity_governance_audit", "practice_consistency_checking", "regulatory_alignment_scoring", "remediation_priority_ranking", "governance_maturity_assessment", "advanced_analytics_dashboard", "priority_email_support", "api_access", "custom_integrations", "webhook_notifications", "data_export_csv_json", "scheduled_automations", "multi_user_access", "dedicated_account_manager", "sla_guarantee_99_9", "custom_model_fine_tuning", "sso_saml_authentication", "audit_logging", "role_based_access_control", "white_label_options", "on_premise_deployment_option", "real_time_monitoring_dashboard", "automated_error_recovery", "cross_bot_data_sharing", "version_history_tracking", "performance_benchmarking", "compliance_reporting", "multi_region_deployment", "auto_scaling_resources", "encrypted_data_at_rest", "soc_2_type_ii_compliant"],
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
