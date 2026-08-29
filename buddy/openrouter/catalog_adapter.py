"""Adapt live OpenRouter models into Buddy's supplemental catalog.

This adapter deliberately keeps OpenRouter entries separate from the
protected DreamCo model catalog.
"""
from __future__ import annotations

from typing import Any

from .client import list_models


def discover_openrouter_catalog() -> list[dict[str, Any]]:
    discovered = []
    for model in list_models():
        discovered.append({
            "id": model.get("id"),
            "name": model.get("name"),
            "source": "openrouter",
            "context_length": model.get("context_length"),
            "pricing": model.get("pricing", {}),
            "architecture": model.get("architecture", {}),
            "supported_parameters": model.get("supported_parameters", []),
        })
    return discovered


def merge_supplemental(existing: list[dict[str, Any]], openrouter: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return a combined view; never mutate or delete `existing`."""
    seen = {item.get("id") for item in existing}
    additions = [item for item in openrouter if item.get("id") not in seen]
    return [*existing, *additions]
