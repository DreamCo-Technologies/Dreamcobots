import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, TierConfig, get_tier_config, get_upgrade_path, list_tiers, TIER_CATALOGUE

BOT_FEATURES = {
    Tier.FREE.value: [
        "dealBot (5 deals)",
        "pennyBot (basic penny search)",
        "couponBot (3 coupon sources)",
        "profit calculator",
        "manual refresh",
    ],
    Tier.PRO.value: [
        "dealBot (50 deals, 10 sources)",
        "pennyBot (all penny sources)",
        "receiptBot (OCR receipt scanning)",
        "flipBot (local resale finder)",
        "couponBot (all coupon sources)",
        "AI profit ranking",
        "deal alerts",
        "auto stacking",
        "affiliate links",
        "premium deal feed",
    ],
    Tier.ENTERPRISE.value: [
        "dealBot (unlimited deals, all sources)",
        "pennyBot (real-time penny alerts)",
        "receiptBot (batch OCR + cashback auto-match)",
        "flipBot (multi-city radius + AI scoring)",
        "couponBot (auto-stack all coupons)",
        "AI profit ranking + alert engine",
        "referral system",
        "premium subscription management",
        "resale marketplace cut",
        "white-label API access",
        "bulk deal analysis",
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
