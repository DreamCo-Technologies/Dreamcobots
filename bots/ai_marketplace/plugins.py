# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional

class PluginCategory(Enum):
    AI = "ai"
    SAVINGS = "savings"
    FINANCE = "finance"
    ALERTS = "alerts"
    INTEGRATION = "integration"
    TOOLS = "tools"
    MARKETING = "marketing"

@dataclass
class Plugin:
    plugin_id: str
    name: str
    category: PluginCategory
    version: str
    description: str
    features: list
    rating: float
    install_count: int
    author: str

class PluginRegistry:
    def __init__(self):
        self._plugins: dict = {}
        self._init_plugins()

    def _init_plugins(self):
        defaults = [
            Plugin("ai_model_router", "AI Model Router", PluginCategory.AI, "v1.4.0",
                   "Routes AI tasks to optimal models for cost and quality",
                   ["model selection", "cost optimization", "quality scoring"], 5.0, 1520, "DreamCo"),
            Plugin("coupon_stacker", "Coupon Stacker", PluginCategory.SAVINGS, "v1.8.0",
                   "Automatically stacks and applies coupons for maximum savings",
                   ["coupon stacking", "auto-apply", "savings tracker"], 5.0, 980, "DreamCo"),
            Plugin("crypto_price_tracker", "Crypto Price Tracker", PluginCategory.FINANCE, "v1.6.0",
                   "Real-time cryptocurrency price tracking and alerts",
                   ["price alerts", "portfolio tracking", "multi-exchange"], 4.0, 740, "DreamCo"),
            Plugin("deal_alert_pro", "Deal Alert Pro", PluginCategory.ALERTS, "v2.1.0",
                   "Advanced deal detection with multi-channel notifications",
                   ["push notifications", "email alerts", "SMS alerts"], 5.0, 2340, "DreamCo"),
            Plugin("discord_server_bot", "Discord Server Bot", PluginCategory.INTEGRATION, "v1.1.0",
                   "Integrates AI capabilities directly into Discord servers",
                   ["command handling", "auto moderation", "bot integration"], 4.0, 610, "DreamCo"),
            Plugin("flip_profit_calculator", "Flip Profit Calculator", PluginCategory.FINANCE, "v1.5.0",
                   "Calculates profit margins and ROI for resale flipping",
                   ["profit calculation", "ROI analysis", "fee estimation"], 4.0, 830, "DreamCo"),
            Plugin("inventory_manager", "Inventory Manager", PluginCategory.TOOLS, "v1.3.0",
                   "Multi-platform inventory synchronization and management",
                   ["multi-platform sync", "stock tracking", "low stock alerts"], 4.0, 1100, "DreamCo"),
            Plugin("receipt_scanner_pro", "Receipt Scanner Pro", PluginCategory.TOOLS, "v2.0.0",
                   "OCR-powered receipt scanning with cashback matching",
                   ["OCR scanning", "cashback matching", "expense categorization"], 5.0, 1890, "DreamCo"),
            Plugin("route_optimizer", "Route Optimizer", PluginCategory.TOOLS, "v1.1.0",
                   "Optimizes delivery and pickup routes for maximum efficiency",
                   ["route planning", "fuel estimation", "ROI per stop"], 4.0, 450, "DreamCo"),
            Plugin("seo_optimizer", "SEO Optimizer", PluginCategory.MARKETING, "v1.2.0",
                   "AI-powered SEO analysis and content optimization",
                   ["keyword research", "content scoring", "competitor analysis"], 4.0, 670, "DreamCo"),
            Plugin("slack_workspace_plugin", "Slack Workspace Plugin", PluginCategory.INTEGRATION, "v1.3.0",
                   "Connects AI bots to Slack workspaces for team automation",
                   ["workspace integration", "channel notifications", "bot commands"], 4.0, 820, "DreamCo"),
            Plugin("telegram_bot_connector", "Telegram Bot Connector", PluginCategory.INTEGRATION, "v1.2.0",
                   "Connects AI capabilities to Telegram bots",
                   ["bot connection", "message handling", "inline commands"], 4.0, 590, "DreamCo"),
        ]
        for p in defaults:
            self._plugins[p.plugin_id] = p

    def get_plugin(self, plugin_id: str) -> Plugin:
        if plugin_id not in self._plugins:
            raise KeyError(f"Plugin '{plugin_id}' not found")
        return self._plugins[plugin_id]

    def list_plugins(self, category: PluginCategory = None) -> list:
        plugins = list(self._plugins.values())
        if category is not None:
            plugins = [p for p in plugins if p.category == category]
        return plugins

    def search_plugins(self, query: str) -> list:
        q = query.lower()
        return [p for p in self._plugins.values()
                if q in p.name.lower() or q in p.description.lower()
                or any(q in f.lower() for f in p.features)]

    def get_top_rated(self, n: int = 5) -> list:
        return sorted(self._plugins.values(), key=lambda p: (p.rating, p.install_count), reverse=True)[:n]

    def register_plugin(self, plugin: Plugin):
        self._plugins[plugin.plugin_id] = plugin
