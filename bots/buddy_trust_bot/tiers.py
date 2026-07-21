"""
Buddy Trust Bot — Tier Definitions

Tiers:
  FREE       ($0)    — Basic consent flows, public vault (read-only),
                       audit log preview (last 10 entries), Trust Seal display.
  PRO        ($49)   — Voice mimicry (up to 3 voice profiles), image synthesis
                       (up to 5 avatars), encrypted vault (up to 50 secrets),
                       full audit trail, GDPR toolkit, explainable-AI panel.
  ENTERPRISE ($199)  — Unlimited voice profiles, unlimited image avatars,
                       unlimited vault secrets, HIPAA + GDPR compliance,
                       Vault Mode, military-grade encryption, dedicated
                       compliance officer tooling, DreamCo Trust Seal API.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Tier(Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


@dataclass
class TierConfig:
    """Configuration for a Buddy Trust Bot subscription tier."""

    name: str
    tier: Tier
    price_usd_monthly: float
    max_voice_profiles: Optional[int]    # None = unlimited
    max_image_avatars: Optional[int]     # None = unlimited
    max_vault_secrets: Optional[int]     # None = unlimited
    max_audit_entries_visible: Optional[int]  # None = unlimited
    features: list
    encryption_level: str                # e.g. "AES-256", "AES-256-GCM"
    compliance_frameworks: list          # e.g. ["GDPR", "HIPAA"]
    support_level: str

    def has_feature(self, feature: str) -> bool:
        return feature in self.features

    def is_unlimited_vault(self) -> bool:
        return self.max_vault_secrets is None


# ---------------------------------------------------------------------------
# Feature flags
# ---------------------------------------------------------------------------

FEATURE_CONSENT_MANAGER = "consent_manager"
FEATURE_VOICE_MIMICRY = "voice_mimicry"
FEATURE_IMAGE_SYNTHESIS = "image_synthesis"
FEATURE_VAULT = "vault"
FEATURE_VAULT_MODE = "vault_mode"           # Locked vault (ENTERPRISE only)
FEATURE_AUDIT_LOG = "audit_log"
FEATURE_FULL_AUDIT = "full_audit_log"
FEATURE_EXPLAINABLE_AI = "explainable_ai"
FEATURE_GDPR_TOOLKIT = "gdpr_toolkit"
FEATURE_HIPAA_TOOLKIT = "hipaa_toolkit"
FEATURE_TRUST_SEAL = "trust_seal"
FEATURE_TRUST_SEAL_API = "trust_seal_api"   # Programmatic seal (ENTERPRISE only)
FEATURE_WHITE_LABEL = "white_label"
FEATURE_API_ACCESS = "api_access"
FEATURE_MILITARY_ENCRYPTION = "military_grade_encryption"
FEATURE_COMPLIANCE_TOOLS = "compliance_tools"

FREE_FEATURES: list = [
    FEATURE_CONSENT_MANAGER,
    FEATURE_AUDIT_LOG,
    FEATURE_TRUST_SEAL,
]

PRO_FEATURES: list = FREE_FEATURES + [
    FEATURE_VOICE_MIMICRY,
    FEATURE_IMAGE_SYNTHESIS,
    FEATURE_VAULT,
    FEATURE_FULL_AUDIT,
    FEATURE_EXPLAINABLE_AI,
    FEATURE_GDPR_TOOLKIT,
]

ENTERPRISE_FEATURES: list = PRO_FEATURES + [
    FEATURE_VAULT_MODE,
    FEATURE_HIPAA_TOOLKIT,
    FEATURE_TRUST_SEAL_API,
    FEATURE_WHITE_LABEL,
    FEATURE_API_ACCESS,
    FEATURE_MILITARY_ENCRYPTION,
    FEATURE_COMPLIANCE_TOOLS,
]

TIER_CATALOGUE: dict = {
    Tier.FREE.value: TierConfig(
        name="Free",
        tier=Tier.FREE,
        price_usd_monthly=0.0,
        max_voice_profiles=0,
        max_image_avatars=0,
        max_vault_secrets=0,
        max_audit_entries_visible=10,
        features=FREE_FEATURES,
        encryption_level="None",
        compliance_frameworks=[],
        support_level="Community",
    ),
    Tier.PRO.value: TierConfig(
        name="Pro",
        tier=Tier.PRO,
        price_usd_monthly=49.0,
        max_voice_profiles=3,
        max_image_avatars=5,
        max_vault_secrets=50,
        max_audit_entries_visible=None,
        features=PRO_FEATURES,
        encryption_level="AES-256",
        compliance_frameworks=["GDPR"],
        support_level="Email (24 h SLA)",
    ),
    Tier.ENTERPRISE.value: TierConfig(
        name="Enterprise",
        tier=Tier.ENTERPRISE,
        price_usd_monthly=199.0,
        max_voice_profiles=None,
        max_image_avatars=None,
        max_vault_secrets=None,
        max_audit_entries_visible=None,
        features=ENTERPRISE_FEATURES,
        encryption_level="AES-256-GCM",
        compliance_frameworks=["GDPR", "HIPAA"],
        support_level="Dedicated 24/7",
    ),
}


def get_tier_config(tier: Tier) -> TierConfig:
    return TIER_CATALOGUE[tier.value]


def list_tiers() -> list:
    return [TIER_CATALOGUE[t.value] for t in Tier]


def get_upgrade_path(current: Tier) -> Optional[TierConfig]:
    order = list(Tier)
    idx = order.index(current)
    if idx + 1 < len(order):
        return get_tier_config(order[idx + 1])
    return None


__all__ = [
    "Tier",
    "TierConfig",
    "get_tier_config",
    "list_tiers",
    "get_upgrade_path",
    "TIER_CATALOGUE",
    "FEATURE_CONSENT_MANAGER",
    "FEATURE_VOICE_MIMICRY",
    "FEATURE_IMAGE_SYNTHESIS",
    "FEATURE_VAULT",
    "FEATURE_VAULT_MODE",
    "FEATURE_AUDIT_LOG",
    "FEATURE_FULL_AUDIT",
    "FEATURE_EXPLAINABLE_AI",
    "FEATURE_GDPR_TOOLKIT",
    "FEATURE_HIPAA_TOOLKIT",
    "FEATURE_TRUST_SEAL",
    "FEATURE_TRUST_SEAL_API",
    "FEATURE_WHITE_LABEL",
    "FEATURE_API_ACCESS",
    "FEATURE_MILITARY_ENCRYPTION",
    "FEATURE_COMPLIANCE_TOOLS",
    "FREE_FEATURES",
    "PRO_FEATURES",
    "ENTERPRISE_FEATURES",
]
