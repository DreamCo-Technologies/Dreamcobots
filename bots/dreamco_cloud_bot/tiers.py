import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, TierConfig, get_tier_config, get_upgrade_path, list_tiers, TIER_CATALOGUE

BOT_FEATURES = {
    Tier.FREE.value: [
        "1 server instance",
        "512 MB RAM",
        "10 GB storage",
        "static site hosting",
        "shared SSL certificate",
        "community support",
    ],
    Tier.PRO.value: [
        "10 server instances",
        "8 GB RAM per instance",
        "200 GB storage",
        "load balancer",
        "managed database (PostgreSQL/MySQL)",
        "auto-scaling (2x)",
        "dedicated SSL certificates",
        "CDN integration",
        "monitoring dashboard",
        "email support",
    ],
    Tier.ENTERPRISE.value: [
        "unlimited instances",
        "custom RAM/CPU",
        "unlimited storage",
        "multi-region deployment",
        "serverless functions",
        "Kubernetes orchestration",
        "managed data warehouse",
        "DDoS protection",
        "99.99% uptime SLA",
        "VPC / private networking",
        "compliance (SOC2, HIPAA)",
        "24/7 dedicated support",
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
