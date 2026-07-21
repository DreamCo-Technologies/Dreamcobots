"""Tier configuration for the Security Tech Bot."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))

from tiers import Tier, TierConfig, get_tier_config, get_upgrade_path, list_tiers

__all__ = ["Tier", "TierConfig", "get_tier_config", "get_upgrade_path", "list_tiers",
           "SECURITY_FEATURES", "SCAN_LIMITS", "get_security_tier_info"]

SECURITY_FEATURES: dict[str, list[str]] = {
    Tier.FREE.value: [
        "Basic vulnerability scan",
        "Password strength checker",
        "5 scans/month",
    ],
    Tier.PRO.value: [
        "Full vulnerability assessment",
        "Code security review",
        "100 scans/month",
        "CVE database lookup",
        "Dependency audit",
    ],
    Tier.ENTERPRISE.value: [
        "Continuous monitoring",
        "Penetration test reports",
        "Compliance scanning (SOC2, HIPAA)",
        "Unlimited scans",
        "Incident response playbooks",
        "Security dashboard",
    ],
}

SCAN_LIMITS: dict[str, int | None] = {
    Tier.FREE.value: 5,
    Tier.PRO.value: 100,
    Tier.ENTERPRISE.value: None,
}


def get_security_tier_info(tier: Tier) -> dict:
    """Return security-bot-specific tier information as a dict."""
    cfg = get_tier_config(tier)
    return {
        "tier": tier.value,
        "name": cfg.name,
        "price_usd_monthly": cfg.price_usd_monthly,
        "requests_per_month": cfg.requests_per_month,
        "support_level": cfg.support_level,
        "security_features": SECURITY_FEATURES[tier.value],
        "scan_limit": SCAN_LIMITS[tier.value],
    }
