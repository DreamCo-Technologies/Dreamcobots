import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, TierConfig, get_tier_config, get_upgrade_path, list_tiers, TIER_CATALOGUE

BOT_FEATURES = {
    Tier.FREE.value: ["1_resume_template", "basic_format", "pdf_ready_text", "basic_suggestions"],
    Tier.PRO.value: ["1_resume_template", "basic_format", "pdf_ready_text", "basic_suggestions", "10_templates", "cover_letter", "linkedin_optimization", "ats_score", "keyword_suggestions"],
    Tier.ENTERPRISE.value: ["1_resume_template", "basic_format", "pdf_ready_text", "basic_suggestions", "10_templates", "cover_letter", "linkedin_optimization", "ats_score", "keyword_suggestions", "unlimited_templates", "multi_language", "industry_specific_tailoring", "advanced_keyword_optimization"],
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
