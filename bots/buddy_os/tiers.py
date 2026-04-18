"""
Tier configuration for the Buddy OS Bot.

Tiers:
  - FREE:       Basic device management, local Bluetooth, 1 connected screen.
  - PRO ($49):  Full device suite, multi-device Bluetooth, all cast protocols,
                app framework, smart-device hub.
  - ENTERPRISE ($199): Unlimited devices, white-label OS skin, API access,
                       enterprise device management, priority support.
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
    """Configuration for a Buddy OS subscription tier."""

    name: str
    tier: Tier
    price_usd_monthly: float
    max_paired_devices: Optional[int]
    max_cast_targets: Optional[int]
    features: list
    support_level: str

    def has_feature(self, feature: str) -> bool:
        return feature in self.features

    def is_unlimited_devices(self) -> bool:
        return self.max_paired_devices is None


# ---------------------------------------------------------------------------
# Feature flags
# ---------------------------------------------------------------------------

FEATURE_DEVICE_MANAGER = "device_manager"
FEATURE_BLUETOOTH = "bluetooth"
FEATURE_CAST_SCREEN = "cast_screen"
FEATURE_MULTI_CAST = "multi_cast"
FEATURE_APP_FRAMEWORK = "app_framework"
FEATURE_SMART_DEVICES = "smart_devices"
FEATURE_BROWSER_TOOLS = "browser_tools"
FEATURE_OS_KERNEL = "os_kernel"
FEATURE_STARLINK = "starlink"
FEATURE_NVIDIA_TOOLS = "nvidia_tools"
FEATURE_WHITE_LABEL = "white_label"
FEATURE_API_ACCESS = "api_access"
FEATURE_ENTERPRISE_MDM = "enterprise_mdm"
FEATURE_DEDICATED_SUPPORT = "dedicated_support"

# New feature flags
FEATURE_WIFI = "wifi"
FEATURE_HARDWARE_PROTOCOLS = "hardware_protocols"
FEATURE_SECURITY_MANAGER = "security_manager"
FEATURE_DEPLOYMENT_MANAGER = "deployment_manager"
FEATURE_CLOUD_SYNC = "cloud_sync"
FEATURE_FLASH_BOOT = "flash_boot"

FREE_FEATURES: list = [
    FEATURE_DEVICE_MANAGER,
    FEATURE_BLUETOOTH,
    FEATURE_CAST_SCREEN,
    FEATURE_BROWSER_TOOLS,
    FEATURE_OS_KERNEL,
    FEATURE_WIFI,
    FEATURE_SECURITY_MANAGER,
]

PRO_FEATURES: list = FREE_FEATURES + [
    FEATURE_MULTI_CAST,
    FEATURE_APP_FRAMEWORK,
    FEATURE_SMART_DEVICES,
    FEATURE_STARLINK,
    FEATURE_NVIDIA_TOOLS,
    FEATURE_HARDWARE_PROTOCOLS,
    FEATURE_DEPLOYMENT_MANAGER,
    FEATURE_FLASH_BOOT,
]

ENTERPRISE_FEATURES: list = PRO_FEATURES + [
    FEATURE_WHITE_LABEL,
    FEATURE_API_ACCESS,
    FEATURE_ENTERPRISE_MDM,
    FEATURE_DEDICATED_SUPPORT,
    FEATURE_CLOUD_SYNC,
]

TIER_CATALOGUE: dict = {
    Tier.FREE.value: TierConfig(
        name="Free",
        tier=Tier.FREE,
        price_usd_monthly=0.0,
        max_paired_devices=3,
        max_cast_targets=1,
        features=FREE_FEATURES,
        support_level="Community",
    ),
    Tier.PRO.value: TierConfig(
        name="Pro",
        tier=Tier.PRO,
        price_usd_monthly=49.0,
        max_paired_devices=25,
        max_cast_targets=10,
        features=PRO_FEATURES,
        support_level="Email (24 h SLA)",
    ),
    Tier.ENTERPRISE.value: TierConfig(
        name="Enterprise",
        tier=Tier.ENTERPRISE,
        price_usd_monthly=199.0,
        max_paired_devices=None,
        max_cast_targets=None,
        features=ENTERPRISE_FEATURES,
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
