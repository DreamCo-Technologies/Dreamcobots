import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, get_tier_config

BOT_FEATURES = {
    Tier.FREE.value: [
        "script generator (up to 5 scripts/day)",
        "basic ad copy generation",
        "15-second commercial scripts",
        "TikTok platform optimization",
        "3 client leads per day",
        "basic revenue tracking",
    ],
    Tier.PRO.value: [
        "script generator (unlimited)",
        "hook + emotional trigger generation",
        "15–60 second commercial scripts",
        "multi-platform ad optimizer (TikTok, YouTube, Instagram, Facebook)",
        "video scene builder",
        "voiceover script generation (male/female/AI tones)",
        "AI closing agent",
        "bulk commercial generator (up to 50/day)",
        "CRM dashboard (up to 100 leads)",
        "Stripe billing integration",
        "auto outreach messaging",
        "performance analytics",
        "Google Maps lead scraping",
        "Shopify store targeting",
    ],
    Tier.ENTERPRISE.value: [
        "all PRO features",
        "unlimited bulk commercial generation",
        "real video generation API (Runway / Pika)",
        "auto posting (TikTok, YouTube, Instagram)",
        "full CRM pipeline (unlimited clients)",
        "multi-region campaign management",
        "white-label system",
        "movie & biography creator engine",
        "self-healing system",
        "advanced performance analytics",
        "AI film director + scene renderer",
        "subscription upsell engine",
        "affiliate ad passive income",
        "API access",
        "dedicated support",
    ],
}


def get_bot_tier_info(tier: Tier) -> dict:
    cfg = get_tier_config(tier)
    return {
        "tier": tier.value,
        "price_usd_monthly": cfg.price_usd_monthly,
        "features": BOT_FEATURES[tier.value],
    }
