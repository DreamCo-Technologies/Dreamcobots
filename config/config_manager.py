"""
MasterConfigManager — Singleton config loader for DreamCobots.

Loads ``config/master_config.yaml``, resolves ``${ENV_VAR:-default}``
placeholders, and exposes a dot-path ``get()`` helper.

Usage
-----
    from config.config_manager import config

    print(config.get("profit_targets.daily"))       # 500.0
    print(config.get("tiers.pro.price_monthly"))    # 49.0
    print(config.get("missing.key", "fallback"))    # "fallback"
"""

from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Optional YAML support
# ---------------------------------------------------------------------------

try:
    import yaml  # type: ignore[import-not-found]

    _YAML_AVAILABLE = True
except ImportError:  # pragma: no cover
    _YAML_AVAILABLE = False


# ---------------------------------------------------------------------------
# Helper dataclass
# ---------------------------------------------------------------------------


@dataclass
class BotPriority:
    """Priority descriptor for a single bot category."""

    bot_name: str
    priority: int
    max_concurrent: int = 1
    budget_allocation_pct: float = 0.0


# ---------------------------------------------------------------------------
# MasterConfigManager
# ---------------------------------------------------------------------------

_ENV_VAR_RE = re.compile(r"^\$\{([^}]+)\}$")


class MasterConfigManager:
    """
    Singleton wrapper around ``config/master_config.yaml``.

    The singleton is reset between tests by calling
    ``MasterConfigManager._reset()`` (test helper only).
    """

    _instance: Optional["MasterConfigManager"] = None
    _config: Dict[str, Any] = {}

    def __new__(cls) -> "MasterConfigManager":
        if cls._instance is None:
            inst = super().__new__(cls)
            inst._config = {}
            inst._load_config()
            cls._instance = inst
        return cls._instance

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------

    def _load_config(self) -> None:
        config_path = Path(__file__).parent / "master_config.yaml"
        if not config_path.exists():
            logger.warning("master_config.yaml not found at %s", config_path)
            return

        if not _YAML_AVAILABLE:
            logger.warning("PyYAML is not installed; config will be empty.")
            return

        with open(config_path, encoding="utf-8") as fh:
            self._config = yaml.safe_load(fh) or {}

        self._resolve_env_vars(self._config)
        logger.info("Master config loaded from %s", config_path)

    def _resolve_env_vars(self, node: Any) -> None:
        """Recursively resolve ``${VAR_NAME:-default}`` strings in *node*."""
        if isinstance(node, dict):
            for key, value in node.items():
                if isinstance(value, str):
                    node[key] = self._expand(value)
                elif isinstance(value, (dict, list)):
                    self._resolve_env_vars(value)
        elif isinstance(node, list):
            for i, item in enumerate(node):
                if isinstance(item, str):
                    node[i] = self._expand(item)
                elif isinstance(item, (dict, list)):
                    self._resolve_env_vars(item)

    @staticmethod
    def _expand(value: str) -> str:
        """Expand a single ``${VAR:-default}`` placeholder."""
        m = _ENV_VAR_RE.match(value)
        if not m:
            return value
        inner = m.group(1)
        if ":-" in inner:
            var_name, default = inner.split(":-", 1)
        else:
            var_name, default = inner, ""
        return os.getenv(var_name.strip(), default)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Retrieve a value using a dot-separated key path.

        Examples::

            config.get("profit_targets.daily")          # 500.0
            config.get("tiers.pro.price_monthly")       # 49.0
            config.get("nonexistent.key", "fallback")   # "fallback"
        """
        keys = key_path.split(".")
        node: Any = self._config
        try:
            for k in keys:
                node = node[k]
            return node
        except (KeyError, TypeError):
            return default

    def all(self) -> Dict[str, Any]:
        """Return a shallow copy of the full configuration dict."""
        return dict(self._config)

    # ------------------------------------------------------------------
    # Test helper
    # ------------------------------------------------------------------

    @classmethod
    def _reset(cls) -> None:
        """Destroy the singleton so the next access reloads the config."""
        cls._instance = None
        cls._config = {}


# ---------------------------------------------------------------------------
# Module-level singleton — import this object everywhere
# ---------------------------------------------------------------------------

config = MasterConfigManager()
