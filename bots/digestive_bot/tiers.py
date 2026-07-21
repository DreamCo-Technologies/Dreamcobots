"""Tier configuration for Digestive Bot."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'ai-models-integration'))
from tiers import Tier, TierConfig, get_tier_config, get_upgrade_path

FEATURES = {
    'free': ['Basic research access', 'Public findings database', 'Discovery feed (10 items)'],
    'pro': ['Full research database', 'Evidence filtering', 'Custom domains', 'Discovery feed (unlimited)', 'Cross-field insights'],
    'enterprise': ['Real-time research ingestion', 'AI hypothesis generation', 'Priority discovery alerts', 'Integration APIs', 'Dedicated research support'],
}


def get_tier_info(tier_str: str) -> dict:
    tier = Tier(tier_str)
    cfg = get_tier_config(tier)
    return {
        'tier': tier_str,
        'name': cfg.name,
        'price_usd_monthly': cfg.price_usd_monthly,
        'requests_per_month': cfg.requests_per_month,
        'features': FEATURES.get(tier_str, []),
        'support_level': cfg.support_level,
    }
