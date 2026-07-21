import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, TierConfig, get_tier_config, get_upgrade_path, list_tiers, TIER_CATALOGUE

BOT_FEATURES = {
    Tier.FREE.value: ["10_leads_per_month", "basic_contact_info", "2_industries"],
    Tier.PRO.value: ["10_leads_per_month", "basic_contact_info", "2_industries", "100_leads_per_month", "verified_emails", "phone_numbers", "10_industries", "lead_scoring"],
    Tier.ENTERPRISE.value: ["10_leads_per_month", "basic_contact_info", "2_industries", "100_leads_per_month", "verified_emails", "phone_numbers", "10_industries", "lead_scoring", "unlimited_leads", "crm_export", "predictive_scoring", "enrichment_data", "company_intelligence"],
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
