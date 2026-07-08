"""Tier definitions for the Enterprise Integrations Bot."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, get_tier_config

BOT_FEATURES = {
    Tier.FREE.value: [
        "5 API provider integrations",
        "100 API calls/month",
        "Google Cloud AI (basic)",
        "Enterprise AI Lite",
        "Slack webhook (read-only)",
        "community support",
    ],
    Tier.PRO.value: [
        "30 API provider integrations",
        "10,000 API calls/month",
        "Google Cloud AI (full suite)",
        "Enterprise AI full access",
        "Microsoft Azure AI",
        "Nvidia AI inference",
        "AWS AI services",
        "Databricks connector",
        "Snowflake connector",
        "Tableau data connector",
        "Slack full integration",
        "Microsoft Teams integration",
        "Zoom integration",
        "subscription resales (up to 50 seats)",
        "multi-provider routing",
        "analytics dashboard",
        "email support",
    ],
    Tier.ENTERPRISE.value: [
        "unlimited API provider integrations",
        "unlimited API calls",
        "Google Cloud AI (full suite + VPC)",
        "Enterprise AI platform access",
        "Microsoft Azure AI + Cognitive Services",
        "Nvidia AI + NIM microservices",
        "AWS AI + Bedrock + SageMaker",
        "Databricks Lakehouse platform",
        "Palantir Foundry connector",
        "Snowflake Data Cloud",
        "Tableau Analytics",
        "Oracle Cloud AI",
        "Slack Enterprise Grid",
        "Microsoft Teams advanced bots",
        "Zoom full platform API",
        "Dream AI Models (proprietary)",
        "DreamCloud compute layer",
        "DreamAnalytics engine",
        "DreamCollab workspace",
        "subscription resales (unlimited seats)",
        "white-label licensing & resale portal",
        "dynamic pricing engine",
        "custom SLA",
        "VPC / private networking",
        "SOC2 / HIPAA compliance",
        "24/7 dedicated support",
        "API access",
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
