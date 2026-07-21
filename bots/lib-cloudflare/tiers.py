import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, TierConfig, get_tier_config, get_upgrade_path, list_tiers, TIER_CATALOGUE

BOT_FEATURES = {
    Tier.FREE.value: ["workers_route_patterns", "durable_objects_design", "d1_sqlite_at_edge", "kv_storage_patterns", "r2_object_storage", "workers_ai_integration", "cloudflare_pages_deployment", "hono_on_workers", "cron_triggers", "queue_consumers"],
    Tier.PRO.value: ["workers_route_patterns", "durable_objects_design", "d1_sqlite_at_edge", "kv_storage_patterns", "r2_object_storage", "workers_ai_integration", "cloudflare_pages_deployment", "hono_on_workers", "cron_triggers", "queue_consumers", "production_code_generation", "library_specific_best_practices", "tool_library_creation", "sdk_scaffolding", "debugging_error_resolution", "documentation_generation", "code_review_refactoring", "api_integration_patterns", "testing_suite_creation", "performance_optimization"],
    Tier.ENTERPRISE.value: ["workers_route_patterns", "durable_objects_design", "d1_sqlite_at_edge", "kv_storage_patterns", "r2_object_storage", "workers_ai_integration", "cloudflare_pages_deployment", "hono_on_workers", "cron_triggers", "queue_consumers", "production_code_generation", "library_specific_best_practices", "tool_library_creation", "sdk_scaffolding", "debugging_error_resolution", "documentation_generation", "code_review_refactoring", "api_integration_patterns", "testing_suite_creation", "performance_optimization", "real_time_monitoring_dashboard", "automated_error_recovery", "cross_bot_data_sharing", "version_history_tracking", "performance_benchmarking", "compliance_reporting", "multi_region_deployment", "auto_scaling_resources", "encrypted_data_at_rest", "soc_2_type_ii_compliant"],
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
