"""WebhooksBot — Universal webhook management system for all DreamCo bots."""
from .webhook_bot import WebhooksBot
from .registry import WebhookBotRegistry
from .health import WebhookHealthMonitor

__all__ = ["WebhooksBot", "WebhookBotRegistry", "WebhookHealthMonitor"]
