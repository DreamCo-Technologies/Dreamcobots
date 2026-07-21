import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, TierConfig, get_tier_config, get_upgrade_path, list_tiers, TIER_CATALOGUE

BOT_FEATURES = {
    Tier.FREE.value: [
        "1 location", "basic property search", "price estimate", "cap rate calculator",
        "distressed property search (3 results)", "housing revenue calculator",
    ],
    Tier.PRO.value: [
        "10 locations", "advanced search filters", "ROI calculator", "market trends",
        "cash flow analysis", "rental comps",
        "full distressed property search (foreclosures, tax sales, abandoned homes)",
        "government housing program finder (HUD, SAM.gov, Grants.gov)",
        "property-to-program revenue matching",
        "outreach message generator (property owners & housing departments)",
    ],
    Tier.ENTERPRISE.value: [
        "unlimited locations", "AI valuation", "predictive analytics",
        "investment portfolio tracker", "deal scoring", "API access",
        "full distressed property search with all filters",
        "unlimited government program search",
        "AI-powered property-to-program matching with strategy recommendation",
        "auto-send outreach (property owners & housing departments)",
        "master lease vs purchase strategy engine",
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
