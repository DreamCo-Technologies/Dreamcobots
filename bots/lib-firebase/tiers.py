import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, TierConfig, get_tier_config, get_upgrade_path, list_tiers, TIER_CATALOGUE

BOT_FEATURES = {
    Tier.FREE.value: ["firestore_data_modeling", "security_rules_design", "real_time_listeners", "firebase_auth_flows", "cloud_functions_2nd_gen", "firebase_storage", "remote_config", "fcm_push_notifications", "firebase_emulator_suite", "app_check_security"],
    Tier.PRO.value: ["firestore_data_modeling", "security_rules_design", "real_time_listeners", "firebase_auth_flows", "cloud_functions_2nd_gen", "firebase_storage", "remote_config", "fcm_push_notifications", "firebase_emulator_suite", "app_check_security", "production_code_generation", "library_specific_best_practices", "tool_library_creation", "sdk_scaffolding", "debugging_error_resolution", "documentation_generation", "code_review_refactoring", "api_integration_patterns", "testing_suite_creation", "performance_optimization"],
    Tier.ENTERPRISE.value: ["firestore_data_modeling", "security_rules_design", "real_time_listeners", "firebase_auth_flows", "cloud_functions_2nd_gen", "firebase_storage", "remote_config", "fcm_push_notifications", "firebase_emulator_suite", "app_check_security", "production_code_generation", "library_specific_best_practices", "tool_library_creation", "sdk_scaffolding", "debugging_error_resolution", "documentation_generation", "code_review_refactoring", "api_integration_patterns", "testing_suite_creation", "performance_optimization", "real_time_monitoring_dashboard", "automated_error_recovery", "cross_bot_data_sharing", "version_history_tracking", "performance_benchmarking", "compliance_reporting", "multi_region_deployment", "auto_scaling_resources", "encrypted_data_at_rest", "soc_2_type_ii_compliant"],
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
