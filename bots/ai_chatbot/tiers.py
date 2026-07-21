"""
Tier configuration for the Dreamcobots AI Chatbot.

Mirrors the broader platform tiers so that chatbot clients benefit from the
same free / pro / enterprise structure used across all AI model integrations.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))

from tiers import (   # re-export for convenience
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
    TIER_CATALOGUE,
    FEATURE_BASIC_INFERENCE,
    FEATURE_BATCH_PROCESSING,
    FEATURE_FINE_TUNING,
    FEATURE_CUSTOM_MODELS,
    FEATURE_API_ACCESS,
    FEATURE_ANALYTICS_DASHBOARD,
    FEATURE_PRIORITY_QUEUE,
    FEATURE_SLA_GUARANTEE,
    FEATURE_DEDICATED_SUPPORT,
    FEATURE_WHITE_LABEL,
    NLP_GPT35,
    NLP_GPT4,
    NLP_BERT_BASE,
    NLP_BERT_LARGE,
    NLP_T5_SMALL,
    NLP_T5_XL,
)

# Chatbot-specific add-ons that stack on top of the base tier configs
CHATBOT_EXTRA_FEATURES: dict[str, list[str]] = {
    Tier.FREE.value: [
        "5 conversation history turns",
        "Text responses only",
    ],
    Tier.PRO.value: [
        "50 conversation history turns",
        "Markdown-formatted responses",
        "Code highlighting",
        "File attachments (PDF, TXT)",
    ],
    Tier.ENTERPRISE.value: [
        "Unlimited conversation history",
        "Multimodal responses (text + images)",
        "Custom system prompts",
        "SAML/SSO integration",
        "Audit logging",
    ],
}

# Chatbot-accessible NLP models per tier
CHATBOT_MODELS: dict[str, list[str]] = {
    Tier.FREE.value: [NLP_GPT35, NLP_BERT_BASE, NLP_T5_SMALL],
    Tier.PRO.value: [NLP_GPT35, NLP_GPT4, NLP_BERT_BASE, NLP_BERT_LARGE, NLP_T5_SMALL, NLP_T5_XL],
    Tier.ENTERPRISE.value: [NLP_GPT35, NLP_GPT4, NLP_BERT_BASE, NLP_BERT_LARGE, NLP_T5_SMALL, NLP_T5_XL],
}


def get_chatbot_tier_info(tier: Tier) -> dict:
    """Return chatbot-specific tier information as a dict."""
    cfg = get_tier_config(tier)
    return {
        "tier": tier.value,
        "name": cfg.name,
        "price_usd_monthly": cfg.price_usd_monthly,
        "requests_per_month": cfg.requests_per_month,
        "platform_features": cfg.features,
        "chatbot_features": CHATBOT_EXTRA_FEATURES[tier.value],
        "available_models": CHATBOT_MODELS[tier.value],
        "support_level": cfg.support_level,
    }
