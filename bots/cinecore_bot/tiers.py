import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, TierConfig, get_tier_config, get_upgrade_path, list_tiers, TIER_CATALOGUE

BOT_FEATURES = {
    Tier.FREE.value: [
        "script generation (up to 5/day)",
        "basic hook and CTA generation",
        "1 platform optimizer (TikTok)",
        "up to 3 lead searches/day",
        "AI closer (basic responses)",
        "self-healing system monitoring",
        "basic analytics (views only)",
    ],
    Tier.PRO.value: [
        "script generation (up to 50/day)",
        "advanced emotional storytelling",
        "AI video generation (Runway / Pika)",
        "voiceover with tone control",
        "all platform optimizers (TikTok, YouTube, Instagram, Facebook)",
        "up to 50 lead searches/day",
        "business scoring and ranking",
        "AI closer with objection handling",
        "Stripe billing integration",
        "bulk commercial generator (up to 20/run)",
        "auto posting to 3 platforms",
        "CRM dashboard (leads + clients)",
        "full analytics (views, clicks, conversions, revenue)",
        "outreach draft generator (human-in-loop)",
        "email + SMS outreach",
    ],
    Tier.ENTERPRISE.value: [
        "unlimited script generation",
        "full cinematic movie + biography creation",
        "real AI video generation (Runway + Pika + custom)",
        "multi-language dubbing and subtitles",
        "voice cloning",
        "unlimited platform distribution",
        "unlimited lead searches with scoring",
        "AI CEO and autonomous company mode",
        "full AI closer with deal closing",
        "Stripe + all billing providers",
        "unlimited bulk commercial generator",
        "auto posting + scheduling to all platforms",
        "full CRM with pipeline tracking",
        "advanced analytics + revenue dashboard",
        "white-label system",
        "agency mode (multi-client dashboard)",
        "SaaS builder",
        "VR/AR and metaverse support",
        "developer SDK and open API",
        "global scaling engine",
        "self-healing + auto bug detection",
        "dedicated account manager",
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
