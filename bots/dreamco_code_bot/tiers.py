import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, TierConfig, get_tier_config, get_upgrade_path, list_tiers, TIER_CATALOGUE

BOT_FEATURES = {
    Tier.FREE.value: [
        "2 languages (Python, JavaScript)",
        "100 executions/month",
        "basic code sandbox",
        "stdin/stdout capture",
    ],
    Tier.PRO.value: [
        "10 languages",
        "1000 executions/month",
        "package installation",
        "persistent sessions",
        "execution history",
        "shareable snippets",
        "AI code suggestions",
    ],
    Tier.ENTERPRISE.value: [
        "all languages",
        "unlimited executions",
        "Docker-style containers",
        "CI/CD pipeline integration",
        "team collaboration",
        "private environments",
        "GPU compute",
        "API access",
        "custom runtimes",
        "white-label branding",
    ],
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
