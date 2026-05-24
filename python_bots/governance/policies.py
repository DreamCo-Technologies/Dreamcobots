"""
DreamCo OS — Bot Execution Policies
======================================

YAML/JSON-configurable execution policies per bot.  Each ``BotPolicy``
defines what the bot is allowed to do and enforces execution constraints
at runtime.

Usage::

    registry = PolicyRegistry()
    registry.load_from_dict({
        "lead_gen_bot": {
            "max_execution_time": 60,
            "allowed_capabilities": ["web_search", "email"],
            "require_approval_above_cost_usd": 1.0,
            "max_calls_per_minute": 10,
        }
    })
    policy = registry.get("lead_gen_bot")
    policy.check_execution_time(120)  # raises PolicyViolationError
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any


class PolicyViolationError(Exception):
    """Raised when a bot violates its declared policy."""


@dataclass
class BotPolicy:
    """Execution policy for a single bot category or instance.

    Attributes
    ----------
    bot_id:
        Bot identifier (can be a glob pattern like ``"*"`` for catch-all).
    max_execution_time:
        Maximum wall-clock seconds per run (0 = unlimited).
    allowed_capabilities:
        Whitelist of tool names.  Empty = all tools allowed.
    blocked_capabilities:
        Blacklist of tool names always denied.
    require_approval_above_cost_usd:
        Trigger human-in-the-loop when estimated cost exceeds this.
    max_calls_per_minute:
        Per-bot API call rate cap.
    max_memory_mb:
        Soft memory limit in MB (0 = unlimited).
    audit_all_actions:
        When True, every action is written to the audit log.
    allow_network:
        Whether this bot may make outbound network calls.
    allow_file_write:
        Whether this bot may write to the file system.
    metadata:
        Arbitrary extra policy metadata.
    """

    bot_id: str = "*"
    max_execution_time: float = 300.0
    allowed_capabilities: list[str] = field(default_factory=list)
    blocked_capabilities: list[str] = field(default_factory=list)
    require_approval_above_cost_usd: float = 10.0
    max_calls_per_minute: int = 60
    max_memory_mb: int = 0
    audit_all_actions: bool = True
    allow_network: bool = True
    allow_file_write: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def check_execution_time(self, elapsed_s: float) -> None:
        if self.max_execution_time and elapsed_s > self.max_execution_time:
            raise PolicyViolationError(
                f"Execution time {elapsed_s:.1f}s exceeds policy limit "
                f"{self.max_execution_time}s for bot '{self.bot_id}'"
            )

    def check_capability(self, capability: str) -> None:
        if capability in self.blocked_capabilities:
            raise PolicyViolationError(
                f"Capability '{capability}' is blocked by policy for bot '{self.bot_id}'"
            )
        if self.allowed_capabilities and capability not in self.allowed_capabilities:
            raise PolicyViolationError(
                f"Capability '{capability}' is not in the allowed list for bot '{self.bot_id}'"
            )

    def check_cost(self, estimated_cost_usd: float) -> bool:
        """Return True if human approval is required for this cost."""
        return estimated_cost_usd > self.require_approval_above_cost_usd

    def check_network(self) -> None:
        if not self.allow_network:
            raise PolicyViolationError(
                f"Network access is denied by policy for bot '{self.bot_id}'"
            )

    def check_file_write(self) -> None:
        if not self.allow_file_write:
            raise PolicyViolationError(
                f"File write is denied by policy for bot '{self.bot_id}'"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "bot_id": self.bot_id,
            "max_execution_time": self.max_execution_time,
            "allowed_capabilities": self.allowed_capabilities,
            "blocked_capabilities": self.blocked_capabilities,
            "require_approval_above_cost_usd": self.require_approval_above_cost_usd,
            "max_calls_per_minute": self.max_calls_per_minute,
            "max_memory_mb": self.max_memory_mb,
            "audit_all_actions": self.audit_all_actions,
            "allow_network": self.allow_network,
            "allow_file_write": self.allow_file_write,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BotPolicy":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


_DEFAULT_POLICY = BotPolicy()


class PolicyRegistry:
    """Registry of ``BotPolicy`` objects, loadable from JSON/YAML files."""

    def __init__(self) -> None:
        self._policies: dict[str, BotPolicy] = {}

    def register(self, policy: BotPolicy) -> None:
        self._policies[policy.bot_id] = policy

    def get(self, bot_id: str) -> BotPolicy:
        """Return the policy for *bot_id*, falling back to catch-all ``"*"``."""
        return self._policies.get(bot_id) or self._policies.get("*") or _DEFAULT_POLICY

    def load_from_dict(self, data: dict[str, Any]) -> None:
        """Load policies from a dict keyed by bot_id."""
        for bot_id, cfg in data.items():
            cfg["bot_id"] = bot_id
            self.register(BotPolicy.from_dict(cfg))

    def load_from_file(self, path: str) -> None:
        """Load policies from a JSON or YAML file."""
        with open(path) as f:
            if path.endswith((".yml", ".yaml")):
                try:
                    import yaml  # type: ignore
                    data = yaml.safe_load(f)
                except ImportError:
                    raise ImportError("PyYAML required for YAML policy files: pip install pyyaml")
            else:
                data = json.load(f)
        self.load_from_dict(data)

    def list_policies(self) -> list[dict[str, Any]]:
        return [p.to_dict() for p in self._policies.values()]
