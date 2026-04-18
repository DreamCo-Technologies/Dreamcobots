import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, TierConfig, get_tier_config, get_upgrade_path, list_tiers, TIER_CATALOGUE  # noqa: F401

BOT_FEATURES = {
    Tier.FREE.value: [
        "music beat generation (5/day)",
        "basic lyrics assistant",
        "1 copyright registration search/day",
        "talent profile creation",
        "basic show booking inquiry",
        "grant & loan directory (read-only)",
        "podcast intro generator",
        "basic voice preview",
    ],
    Tier.PRO.value: [
        "music beat generation (50/day)",
        "full song & lyrics creation",
        "voice cloning (up to 3 voices)",
        "commercial & podcast production",
        "Instagram Reels / TikTok content generator",
        "copyright registration filing",
        "trademark search & registration",
        "patent search assistant",
        "talent booking & scheduling (up to 20 artists)",
        "show outlet creation & promotion",
        "grant & loan application assistant",
        "royalty tracking & collection",
        "AI beat & song marketplace listing",
        "video creation for music & ads",
        "Stripe billing integration",
        "CRM dashboard for artists & clients",
        "basic analytics (plays, streams, bookings)",
    ],
    Tier.ENTERPRISE.value: [
        "unlimited music & beat generation",
        "unlimited song, lyrics, and video creation",
        "unlimited voice cloning & multi-language dubbing",
        "full commercial, podcast, and reel production suite",
        "AI-powered music mastering & mixing",
        "copyright, trademark, and patent filing (automated)",
        "invention & IP portfolio management",
        "worldwide talent agency management (unlimited artists)",
        "automated show booking & event management",
        "global show outlet network",
        "grant, loan, and investment sourcing (AI-matched)",
        "financial dashboard (royalties, licensing, revenue)",
        "AI song & beat marketplace with white-label storefront",
        "OnlyFans & adult content creator tools",
        "cross-platform distribution (Spotify, Apple Music, TikTok, YouTube)",
        "Shazam & music recognition integration",
        "advanced analytics & revenue intelligence",
        "multi-industry talent support (music, podcasts, inventions, trademarks)",
        "white-label agency platform",
        "self-healing & auto-monitoring system",
        "developer API & SDK",
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
