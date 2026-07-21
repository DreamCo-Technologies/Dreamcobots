"""DreamCo SaaS Packages Bot — modular SaaS packages for businesses."""

from bots.saas_packages_bot.saas_packages_bot import SaaSPackagesBot, SaaSPackagesBotError, SaaSPackagesTierError
from bots.saas_packages_bot.tiers import Tier
from bots.saas_packages_bot.package_catalog import PackageCatalog, SaaSPackage
from bots.saas_packages_bot.modular_builder import ModularSaaSBuilder
from bots.saas_packages_bot.enterprise_scaler import EnterpriseScaler

__all__ = [
    "SaaSPackagesBot",
    "SaaSPackagesBotError",
    "SaaSPackagesTierError",
    "Tier",
    "PackageCatalog",
    "SaaSPackage",
    "ModularSaaSBuilder",
    "EnterpriseScaler",
]
