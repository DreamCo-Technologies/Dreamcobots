import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, TierConfig, get_tier_config, get_upgrade_path, list_tiers, TIER_CATALOGUE

BOT_FEATURES = {
    Tier.FREE.value: [
        "1 workspace environment",
        "2 GB storage",
        "basic VS Code-like editor",
        "GitHub repo connection",
        "2-hour auto-sleep",
    ],
    Tier.PRO.value: [
        "5 workspace environments",
        "32 GB storage",
        "full IDE features",
        "port forwarding",
        "custom environment config",
        "no auto-sleep",
        "dotfiles support",
        "prebuilt environment images",
        "team sharing (3 users)",
    ],
    Tier.ENTERPRISE.value: [
        "unlimited workspaces",
        "unlimited storage",
        "custom Docker images",
        "GPU-enabled environments",
        "SSO/SAML authentication",
        "audit logging",
        "dedicated compute",
        "99.9% uptime SLA",
        "API access",
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
