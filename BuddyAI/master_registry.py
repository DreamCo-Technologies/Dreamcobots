"""Master registry adapter for DreamBuddy capability governance."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional


class MasterRegistryAdapter:
    """Reads capability metadata from config/master_bot_registry.json."""

    def __init__(self, registry_path: Optional[str | Path] = None) -> None:
        default_path = Path(__file__).resolve().parent.parent / "config" / "master_bot_registry.json"
        self._registry_path = Path(registry_path) if registry_path else default_path

    def _load_registry(self) -> dict[str, Any]:
        if not self._registry_path.exists():
            return {}
        try:
            with self._registry_path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
            return data if isinstance(data, dict) else {}
        except (OSError, json.JSONDecodeError):
            return {}

    @staticmethod
    def _normalize_capability(
        raw: Any, bot: dict[str, Any], capability_name: Optional[str] = None
    ) -> Optional[dict[str, Any]]:
        if isinstance(raw, str):
            return {
                "intent": raw,
                "enabled": True,
                "approval_required": bool(bot.get("safety", {}).get("approval_required", False)),
                "risk_level": bot.get("safety", {}).get("risk_level", "low"),
                "division": bot.get("division", "Unknown"),
                "revenue_generating": False,
                "spends_money": False,
                "bot_id": bot.get("id"),
            }
        if isinstance(raw, dict):
            intent = raw.get("intent") or raw.get("capability") or capability_name
            if not intent:
                return None
            monetization = bot.get("monetization", {})
            return {
                "intent": intent,
                "enabled": bool(raw.get("enabled", True)),
                "approval_required": bool(
                    raw.get("approval_required", bot.get("safety", {}).get("approval_required", False))
                ),
                "risk_level": raw.get("risk_level", bot.get("safety", {}).get("risk_level", "low")),
                "division": raw.get("division", bot.get("division", "Unknown")),
                "revenue_generating": bool(
                    raw.get("revenue_generating", raw.get("monetization_enabled", monetization.get("enabled", False)))
                ),
                "spends_money": bool(raw.get("spends_money", False)),
                "bot_id": raw.get("bot_id", bot.get("id")),
            }
        return None

    def get_capability(self, intent: str) -> Optional[dict[str, Any]]:
        """Return registry metadata for a capability intent if present."""
        data = self._load_registry()

        capabilities = data.get("capabilities", {})
        if isinstance(capabilities, dict) and intent in capabilities:
            normalized = self._normalize_capability(capabilities[intent], {"id": "master_registry"}, intent)
            if normalized:
                return normalized

        bots = data.get("bots", [])
        if not isinstance(bots, list):
            return None

        for bot in bots:
            if not isinstance(bot, dict):
                continue
            raw_caps = bot.get("capabilities", [])
            if isinstance(raw_caps, dict):
                iterable = [
                    (name, config)
                    for name, config in raw_caps.items()
                ]
            elif isinstance(raw_caps, list):
                iterable = [(None, config) for config in raw_caps]
            else:
                iterable = []

            for cap_name, cap_config in iterable:
                normalized = self._normalize_capability(cap_config, bot, cap_name)
                if normalized and normalized.get("intent") == intent:
                    return normalized

        return None
