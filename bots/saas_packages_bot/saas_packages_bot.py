"""
SaaS Packages Bot — Main Entry Point.

Composes all SaaS Domination sub-systems into a single platform:

  • Package Catalog      — 15+ industry-specific SaaS packages
  • Modular Builder      — custom SaaS plan composer with per-module pricing
  • Enterprise Scaler    — infrastructure scaling advisor and Fortune 500 integrations

Architecture:
    DreamCoBots
    │
    ├── buddybot
    │
    ├── saas_packages_bot
    │     ├── package_catalog
    │     ├── modular_builder
    │     └── enterprise_scaler
    │
    └── ai_level_up_bot

Usage
-----
    from bots.saas_packages_bot import SaaSPackagesBot, Tier

    bot = SaaSPackagesBot(tier=Tier.PRO, user_id="alice")
    print(bot.run())
    packages = bot.list_packages()
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from bots.saas_packages_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    FEATURE_BASIC_PACKAGES,
    FEATURE_ADVANCED_TEMPLATES,
    FEATURE_USAGE_ANALYTICS,
    FEATURE_ECOMMERCE_MODULE,
    FEATURE_CRM_MODULE,
    FEATURE_HR_MODULE,
    FEATURE_CUSTOM_BUILDER,
    FEATURE_FORTUNE500_INTEGRATIONS,
    FEATURE_API_ACCESS,
)
from bots.saas_packages_bot.package_catalog import PackageCatalog, Industry
from bots.saas_packages_bot.modular_builder import ModularSaaSBuilder
from bots.saas_packages_bot.enterprise_scaler import EnterpriseScaler

from framework import GlobalAISourcesFlow  # noqa: F401


class SaaSPackagesBotError(Exception):
    """Base exception for SaaS Packages Bot errors."""


class SaaSPackagesTierError(SaaSPackagesBotError):
    """Raised when accessing a feature unavailable on the current tier."""


class SaaSPackagesBot:
    """DreamCo SaaS Packages Bot orchestrator.

    Combines the Package Catalog, Modular Builder, and Enterprise Scaler
    into a unified SaaS Domination platform.

    Parameters
    ----------
    tier : Tier
        Subscription tier (FREE / PRO / ENTERPRISE).
    user_id : str
        Identifier for the current user session.
    """

    def __init__(self, tier: Tier = Tier.FREE, user_id: str = "user") -> None:
        self.bot_name = "SaaS Packages Bot"
        self.version = "1.0"
        self.tier = tier
        self.config: TierConfig = get_tier_config(tier)
        self.user_id = user_id

        self.catalog = PackageCatalog()
        self.builder = ModularSaaSBuilder()
        self.scaler = EnterpriseScaler()

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def run(self) -> str:
        """Return a status message confirming the bot is online."""
        return f"{self.bot_name} v{self.version} Online [{self.tier.value.upper()} tier]"

    # ------------------------------------------------------------------
    # Package Catalog delegation
    # ------------------------------------------------------------------

    def list_packages(self, industry: str | None = None) -> list:
        """List available packages, optionally filtered by industry name."""
        self._require_feature(FEATURE_BASIC_PACKAGES)
        ind = self._parse_industry(industry) if industry else None
        packages = self.catalog.list_packages(ind)
        limit = self.config.max_packages
        if limit is not None:
            packages = packages[:limit]
        return [p.to_dict() for p in packages]

    def get_package(self, package_id: str) -> dict:
        """Return a package by ID."""
        self._require_feature(FEATURE_BASIC_PACKAGES)
        pkg = self.catalog.get_package(package_id)
        if pkg is None:
            return {"error": f"Package '{package_id}' not found."}
        return pkg.to_dict()

    def search_packages(self, query: str) -> list:
        """Search the catalog by keyword."""
        self._require_feature(FEATURE_BASIC_PACKAGES)
        results = self.catalog.search_packages(query)
        return [p.to_dict() for p in results]

    def get_pricing_summary(self) -> list:
        """Return a pricing summary of the catalog."""
        self._require_feature(FEATURE_BASIC_PACKAGES)
        return self.catalog.get_pricing_summary()

    # ------------------------------------------------------------------
    # Modular Builder delegation
    # ------------------------------------------------------------------

    def create_saas_plan(
        self,
        plan_name: str,
        business_type: str,
        description: str = "",
    ) -> dict:
        """Create a new modular SaaS plan."""
        self._require_feature(FEATURE_CUSTOM_BUILDER)
        return self.builder.create_saas_plan(
            user_id=self.user_id,
            plan_name=plan_name,
            business_type=business_type,
            description=description,
        )

    def add_module(
        self,
        plan_id: str,
        module_name: str,
        config: dict | None = None,
    ) -> dict:
        """Add a module to a plan."""
        self._require_feature(FEATURE_CUSTOM_BUILDER)
        return self.builder.add_module(plan_id, module_name, config)

    def remove_module(self, plan_id: str, module_name: str) -> dict:
        """Remove a module from a plan."""
        self._require_feature(FEATURE_CUSTOM_BUILDER)
        return self.builder.remove_module(plan_id, module_name)

    def calculate_plan_cost(self, plan_id: str) -> dict:
        """Calculate the cost of a plan."""
        self._require_feature(FEATURE_CUSTOM_BUILDER)
        return self.builder.calculate_plan_cost(plan_id)

    def generate_plan_spec(self, plan_id: str) -> dict:
        """Generate a deployment-ready spec for a plan."""
        self._require_feature(FEATURE_CUSTOM_BUILDER)
        return self.builder.generate_plan_spec(plan_id)

    def list_plans(self) -> list:
        """List all plans for the current user."""
        self._require_feature(FEATURE_CUSTOM_BUILDER)
        return self.builder.list_plans(self.user_id)

    # ------------------------------------------------------------------
    # Enterprise Scaler delegation
    # ------------------------------------------------------------------

    def assess_scale_tier(self, user_count: int) -> str:
        """Assess the scale tier for a given user count."""
        self._require_feature(FEATURE_BASIC_PACKAGES)
        return self.scaler.assess_scale_tier(user_count)

    def generate_scaling_plan(
        self,
        plan_id: str,
        current_users: int,
        projected_users: int,
    ) -> dict:
        """Generate an infrastructure scaling plan."""
        self._require_feature(FEATURE_BASIC_PACKAGES)
        return self.scaler.generate_scaling_plan(plan_id, current_users, projected_users)

    def estimate_infrastructure_cost(
        self,
        user_count: int,
        modules: list | None = None,
    ) -> dict:
        """Estimate monthly infrastructure cost."""
        self._require_feature(FEATURE_BASIC_PACKAGES)
        return self.scaler.estimate_infrastructure_cost(user_count, modules or [])

    def generate_fortune500_integration(
        self,
        company_name: str,
        integration_type: str,
    ) -> dict:
        """Generate a Fortune 500 integration specification."""
        self._require_feature(FEATURE_FORTUNE500_INTEGRATIONS)
        return self.scaler.generate_fortune500_integration(company_name, integration_type)

    # ------------------------------------------------------------------
    # Chat
    # ------------------------------------------------------------------

    def chat(self, message: str) -> str:
        """Handle a natural language message and return a bot response."""
        msg = message.lower().strip()
        if "package" in msg or "catalog" in msg:
            count = self.catalog.count()
            return (
                f"SaaS Packages Bot has {count} industry-specific packages ready. "
                "Use list_packages() to browse, or search_packages(query) to find one."
            )
        if "tier" in msg or "plan" in msg or "price" in msg or "upgrade" in msg:
            cfg = self.config
            upgrade = get_upgrade_path(self.tier)
            resp = (
                f"You are on the {cfg.name} tier (${cfg.price_usd_monthly}/mo). "
                f"Features: {', '.join(cfg.features)}."
            )
            if upgrade:
                resp += f" Upgrade to {upgrade.name} for ${upgrade.price_usd_monthly}/mo."
            return resp
        if "module" in msg or "build" in msg or "custom" in msg:
            return (
                "Use create_saas_plan() to start building your custom SaaS. "
                "Then add_module() to compose your stack. Requires ENTERPRISE tier."
            )
        if "scale" in msg or "enterprise" in msg or "fortune" in msg:
            return (
                "Use generate_scaling_plan() for infrastructure planning, "
                "or generate_fortune500_integration() for Fortune 500 integrations. "
                "Fortune 500 integrations require ENTERPRISE tier."
            )
        return (
            f"Hello! I'm the {self.bot_name}. "
            "I can help you discover SaaS packages, build custom plans, and scale your business. "
            "Ask me about packages, tiers, modules, or enterprise scaling."
        )

    # ------------------------------------------------------------------
    # Dashboard
    # ------------------------------------------------------------------

    def dashboard(self) -> dict:
        """Return a unified dashboard of bot status and key metrics."""
        upgrade = get_upgrade_path(self.tier)
        return {
            "bot": self.bot_name,
            "version": self.version,
            "tier": self.tier.value,
            "user_id": self.user_id,
            "catalog_size": self.catalog.count(),
            "features": self.config.features,
            "max_packages": self.config.max_packages,
            "max_users": self.config.max_users,
            "support_level": self.config.support_level,
            "upgrade_available": upgrade is not None,
            "upgrade_to": upgrade.name if upgrade else None,
        }

    def describe_tier(self) -> dict:
        """Return details about the current subscription tier."""
        cfg = self.config
        upgrade = get_upgrade_path(self.tier)
        return {
            "tier": cfg.tier.value,
            "name": cfg.name,
            "price_usd_monthly": cfg.price_usd_monthly,
            "max_packages": cfg.max_packages,
            "max_users": cfg.max_users,
            "features": cfg.features,
            "support_level": cfg.support_level,
            "upgrade_available": upgrade is not None,
            "upgrade_to": upgrade.name if upgrade else None,
            "upgrade_price": upgrade.price_usd_monthly if upgrade else None,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _require_feature(self, feature: str) -> None:
        if not self.config.has_feature(feature):
            raise SaaSPackagesTierError(
                f"Feature '{feature}' is not available on the {self.tier.value} tier. "
                "Please upgrade your subscription."
            )

    def _parse_industry(self, industry: str) -> Industry:
        try:
            return Industry(industry.lower())
        except ValueError:
            try:
                return Industry[industry.upper()]
            except KeyError:
                raise ValueError(f"Unknown industry: '{industry}'")
