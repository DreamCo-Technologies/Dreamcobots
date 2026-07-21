"""
AI Marketplace — DreamCo

Central hub to manage, extend, and monetize AI capabilities with plugins,
subscriptions, skill packs, and industry verticals.
Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""
from framework import GlobalAISourcesFlow
from bots.ai_marketplace.tiers import Tier, get_tier_config, FEATURE_PLUGIN_INSTALL, FEATURE_ALERTS, FEATURE_ANALYTICS, FEATURE_CUSTOM_PLUGINS
from bots.ai_marketplace.plugins import PluginRegistry, PluginCategory
from bots.ai_marketplace.subscriptions import SubscriptionManager, SubscriptionPlan
from bots.ai_marketplace.skill_packs import SkillPackRegistry


class AIMarketplaceError(Exception):
    """Base error for AI Marketplace."""

class AIMarketplaceTierError(AIMarketplaceError):
    """Raised when a feature requires a higher tier."""


class AIMarketplace:
    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)
        self._flow = GlobalAISourcesFlow(bot_name="AIMarketplace")
        self._registry = PluginRegistry()
        self._subscriptions = SubscriptionManager()
        self._skill_packs = SkillPackRegistry()
        self._installed: list = []

    def _require_feature(self, feature: str):
        if not self.config.has_feature(feature):
            raise AIMarketplaceTierError(
                f"Feature '{feature}' requires a higher tier. Current tier: {self.tier.value}"
            )

    def browse_plugins(self, category: str = None) -> list:
        cat = None
        if category is not None:
            try:
                cat = PluginCategory(category.lower())
            except ValueError:
                raise AIMarketplaceError(f"Unknown category: {category}")
        plugins = self._registry.list_plugins(category=cat)
        return [self._plugin_to_dict(p) for p in plugins]

    def install_plugin(self, plugin_id: str) -> dict:
        self._require_feature(FEATURE_PLUGIN_INSTALL)
        plugin = self._registry.get_plugin(plugin_id)
        if plugin_id in self._installed:
            raise AIMarketplaceError(f"Plugin '{plugin_id}' is already installed")
        max_p = self.config.max_plugins
        if max_p is not None and len(self._installed) >= max_p:
            raise AIMarketplaceTierError(
                f"Plugin limit reached ({max_p}). Upgrade to install more plugins."
            )
        self._installed.append(plugin_id)
        plugin.install_count += 1
        return {"installed": True, "plugin_id": plugin_id, "name": plugin.name}

    def uninstall_plugin(self, plugin_id: str):
        if plugin_id not in self._installed:
            raise AIMarketplaceError(f"Plugin '{plugin_id}' is not installed")
        self._installed.remove(plugin_id)

    def get_installed_plugins(self) -> list:
        return [self._plugin_to_dict(self._registry.get_plugin(pid)) for pid in self._installed]

    def search_plugins(self, query: str) -> list:
        results = self._registry.search_plugins(query)
        return [self._plugin_to_dict(p) for p in results]

    def subscribe(self, user_id: str, plan_str: str) -> dict:
        self._require_feature(FEATURE_ALERTS)
        try:
            plan = SubscriptionPlan(plan_str.lower())
        except ValueError:
            raise AIMarketplaceError(f"Unknown subscription plan: {plan_str}")
        return self._subscriptions.subscribe(user_id, plan)

    def get_skill_packs(self) -> list:
        return [self._pack_to_dict(p) for p in self._skill_packs.list_packs()]

    def purchase_skill_pack(self, pack_id: str) -> dict:
        self._require_feature(FEATURE_ALERTS)
        pack = self._skill_packs.get_pack(pack_id)
        installed = []
        for pid in pack.plugins:
            try:
                self.install_plugin(pid)
                installed.append(pid)
            except AIMarketplaceTierError:
                break
            except AIMarketplaceError:
                pass
        return {
            "pack_id": pack_id,
            "name": pack.name,
            "price_usd": pack.price_usd,
            "plugins_installed": installed,
        }

    def dashboard(self) -> str:
        lines = [
            f"=== AI Marketplace ({self.config.name} Tier) ===",
            f"Available Plugins: {len(self._registry.list_plugins())}",
            f"Installed: {len(self._installed)}/{self.config.max_plugins or 'unlimited'}",
            f"Skill Packs: {len(self._skill_packs.list_packs())}",
        ]
        if self._installed:
            lines.append(f"Active Plugins: {', '.join(self._installed)}")
        return "\n".join(lines)

    @staticmethod
    def _plugin_to_dict(plugin) -> dict:
        return {
            "plugin_id": plugin.plugin_id,
            "name": plugin.name,
            "category": plugin.category.value,
            "version": plugin.version,
            "description": plugin.description,
            "features": plugin.features,
            "rating": plugin.rating,
            "install_count": plugin.install_count,
            "author": plugin.author,
        }

    @staticmethod
    def _pack_to_dict(pack) -> dict:
        return {
            "pack_id": pack.pack_id,
            "name": pack.name,
            "description": pack.description,
            "plugins": pack.plugins,
            "price_usd": pack.price_usd,
            "industry": pack.industry,
        }
