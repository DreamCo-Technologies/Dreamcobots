"""OpenRouter supplemental integration for Buddy."""

from .client import OpenRouterError, chat, list_models
from .catalog_adapter import discover_openrouter_catalog, merge_supplemental

__all__ = [
    "OpenRouterError",
    "chat",
    "list_models",
    "discover_openrouter_catalog",
    "merge_supplemental",
]
