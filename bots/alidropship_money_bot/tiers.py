import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, TierConfig, get_tier_config, get_upgrade_path, list_tiers, TIER_CATALOGUE

BOT_FEATURES = {
    Tier.FREE.value: [
        "product discovery (5 products/day)",
        "basic AliExpress trending scan",
        "manual store setup guide",
        "pricing formula calculator",
        "1 niche",
    ],
    Tier.PRO.value: [
        "product discovery (50 products/day)",
        "AliExpress + TikTok trend scraping",
        "auto store builder (WordPress + AliDropship)",
        "dynamic pricing engine (3x markup)",
        "auto fulfillment & order tracking",
        "TikTok viral content generator",
        "Facebook ads bot (5 ads/day)",
        "basic scaling engine",
        "5 niches",
    ],
    Tier.ENTERPRISE.value: [
        "unlimited product discovery",
        "AliExpress + TikTok + Facebook Ad Library",
        "multi-store builder (up to 10 stores)",
        "AI-powered pricing & profit optimizer",
        "auto fulfillment with customer notifications",
        "TikTok viral bot (3–10 videos/day)",
        "Facebook ads bot (unlimited)",
        "influencer outreach bot",
        "full scaling engine (auto budget increase)",
        "self-marketing network (blog/deal/review sites)",
        "AI product descriptions (ChatGPT integration)",
        "multi-niche domination (unlimited niches)",
        "white-label stores",
        "API access",
        "dedicated support",
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
