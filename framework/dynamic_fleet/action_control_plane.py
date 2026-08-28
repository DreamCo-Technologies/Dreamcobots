"""Dynamic, resource-scaled control-plane primitives for Buddy.

This module deliberately contains no fixed fleet-size assumptions. Modules and
superbots are discovered and registered at runtime, then exposed through the
stable ten Actions facade.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Iterable


ACTIONS = (
    "full_system_audit",
    "reasoning_health_check",
    "connectivity_audit",
    "run_capability_batch",
    "failure_injection",
    "auto_diagnose",
    "regression_sweep",
    "benchmark_buddy",
    "self_healing_check",
    "production_readiness",
)


class Health(str, Enum):
    DISCOVERED = "DISCOVERED"
    REGISTERED = "REGISTERED"
    ROUTABLE = "ROUTABLE"
    TESTABLE = "TESTABLE"
    OBSERVABLE = "OBSERVABLE"
    VERIFIED = "VERIFIED"
    PROMOTED = "PROMOTED"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"


@dataclass(slots=True)
class Module:
    module_id: str
    capabilities: set[str] = field(default_factory=set)
    supported_actions: set[str] = field(default_factory=lambda: set(ACTIONS))
    dependencies: set[str] = field(default_factory=set)
    health: Health = Health.DISCOVERED
    metadata: dict[str, Any] = field(default_factory=dict)

    def register(self) -> None:
        unknown = self.supported_actions.difference(ACTIONS)
        if unknown:
            raise ValueError(f"unsupported actions: {sorted(unknown)}")
        self.health = Health.REGISTERED


@dataclass(slots=True)
class Superbot:
    superbot_id: str
    module_ids: set[str] = field(default_factory=set)
    domains: set[str] = field(default_factory=set)
    supported_actions: set[str] = field(default_factory=lambda: set(ACTIONS))
    health: Health = Health.DISCOVERED

    def register(self) -> None:
        unknown = self.supported_actions.difference(ACTIONS)
        if unknown:
            raise ValueError(f"unsupported actions: {sorted(unknown)}")
        self.health = Health.REGISTERED


class DynamicRegistry:
    """Registry whose size is determined by discovered resources, not constants."""

    def __init__(self) -> None:
        self.modules: dict[str, Module] = {}
        self.superbots: dict[str, Superbot] = {}

    def discover_modules(self, modules: Iterable[Module]) -> int:
        added = 0
        for module in modules:
            if module.module_id not in self.modules:
                self.modules[module.module_id] = module
                added += 1
        return added

    def register_superbot(self, superbot: Superbot) -> None:
        superbot.register()
        missing = superbot.module_ids.difference(self.modules)
        if missing:
            raise ValueError(f"unknown modules: {sorted(missing)}")
        self.superbots[superbot.superbot_id] = superbot

    def route(self, action: str, capability: str | None = None) -> list[tuple[str, str]]:
        if action not in ACTIONS:
            raise ValueError(f"unknown action: {action}")
        routes: list[tuple[str, str]] = []
        for bot in self.superbots.values():
            if action not in bot.supported_actions:
                continue
            for module_id in bot.module_ids:
                module = self.modules.get(module_id)
                if module and action in module.supported_actions:
                    if capability is None or capability in module.capabilities:
                        routes.append((bot.superbot_id, module_id))
        return routes

    def snapshot(self) -> dict[str, Any]:
        return {
            "actions": list(ACTIONS),
            "module_count": len(self.modules),
            "superbot_count": len(self.superbots),
            "module_health": self._health_counts(self.modules.values()),
            "superbot_health": self._health_counts(self.superbots.values()),
        }

    @staticmethod
    def _health_counts(items: Iterable[Any]) -> dict[str, int]:
        counts: dict[str, int] = {}
        for item in items:
            value = item.health.value
            counts[value] = counts.get(value, 0) + 1
        return counts
