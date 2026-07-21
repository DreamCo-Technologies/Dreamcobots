"""
Discount Dominator package.

Exposes the primary public API for settings 401–600 and the three
interoperability domain modules.
"""

from .settings import (
    Setting,
    DISCOUNT_DOMINATOR_SETTINGS,
    SETTINGS_BY_GROUP,
    ALL_GROUPS,
    GROUP_ANALYTICS,
    GROUP_INSTORE,
    GROUP_ONLINE,
    GROUP_ENTERPRISE,
    GROUP_BEHAVIORAL,
    get_setting,
    apply_settings,
    get_group_settings,
    reset_all,
    as_dict,
)
from .analytics import AdvancedAnalytics
from .in_store_controls import InStoreTacticalControls
from .online_optimization import OnlinePlatformOptimization
from .enterprise_features import EnterpriseFeatures
from .behavioral_settings import BehavioralSettings
from .real_estate_optimizer import RealEstateOptimizer
from .car_flipping_bot import CarFlippingBot
from .retail_intelligence import RetailIntelligenceNetwork
from .discount_dominator import DiscountDominator

__all__ = [
    # Settings
    "Setting",
    "DISCOUNT_DOMINATOR_SETTINGS",
    "SETTINGS_BY_GROUP",
    "ALL_GROUPS",
    "GROUP_ANALYTICS",
    "GROUP_INSTORE",
    "GROUP_ONLINE",
    "GROUP_ENTERPRISE",
    "GROUP_BEHAVIORAL",
    "get_setting",
    "apply_settings",
    "get_group_settings",
    "reset_all",
    "as_dict",
    # Module facades
    "AdvancedAnalytics",
    "InStoreTacticalControls",
    "OnlinePlatformOptimization",
    "EnterpriseFeatures",
    "BehavioralSettings",
    # Domain interoperability
    "RealEstateOptimizer",
    "CarFlippingBot",
    "RetailIntelligenceNetwork",
    # Main bot
    "DiscountDominator",
]
