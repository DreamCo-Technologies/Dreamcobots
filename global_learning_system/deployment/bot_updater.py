"""
bot_updater.py — Updates the bot infrastructure upon retraining.

Manages bot version tracking, applies model updates, and triggers
continuous-retraining cycles to keep DreamCo bots current.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class BotVersion:
    """Describes a specific version of a DreamCo bot."""

    bot_name: str
    version: str
    model_ids: List[str]
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    is_active: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


class BotUpdater:
    """
    Tracks bot versions and applies updates after retraining.

    Parameters
    ----------
    auto_activate : bool
        When ``True``, newly registered versions are immediately activated.
    """

    def __init__(self, auto_activate: bool = True):
        self.auto_activate = auto_activate
        self._versions: Dict[str, List[BotVersion]] = {}

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def register_version(
        self,
        bot_name: str,
        version: str,
        model_ids: List[str],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> BotVersion:
        """
        Register a new version for *bot_name*.

        Parameters
        ----------
        bot_name : str
        version : str
            Semantic version string (e.g. ``"1.2.0"``).
        model_ids : list[str]
            Identifiers of the models bundled in this version.
        metadata : dict | None
            Optional extra metadata.

        Returns
        -------
        BotVersion
        """
        bv = BotVersion(
            bot_name=bot_name,
            version=version,
            model_ids=list(model_ids),
            metadata=metadata or {},
        )
        if bot_name not in self._versions:
            self._versions[bot_name] = []

        if self.auto_activate:
            for existing in self._versions[bot_name]:
                existing.is_active = False
            bv.is_active = True

        self._versions[bot_name].append(bv)
        return bv

    def activate(self, bot_name: str, version: str) -> BotVersion:
        """
        Activate a specific version of *bot_name*.

        Parameters
        ----------
        bot_name : str
        version : str

        Returns
        -------
        BotVersion

        Raises
        ------
        KeyError
            If the bot or version is not found.
        """
        versions = self._versions.get(bot_name, [])
        target = next((v for v in versions if v.version == version), None)
        if target is None:
            raise KeyError(f"Version '{version}' of bot '{bot_name}' not found.")
        for v in versions:
            v.is_active = False
        target.is_active = True
        return target

    def active_version(self, bot_name: str) -> Optional[BotVersion]:
        """Return the currently active version of *bot_name*, or ``None``."""
        for v in self._versions.get(bot_name, []):
            if v.is_active:
                return v
        return None

    def list_versions(self, bot_name: str) -> List[BotVersion]:
        """Return all registered versions of *bot_name*."""
        return list(self._versions.get(bot_name, []))

    def list_bots(self) -> List[str]:
        """Return all tracked bot names."""
        return list(self._versions.keys())

    def trigger_retrain(self, bot_name: str) -> Dict[str, Any]:
        """
        Simulate triggering a retraining cycle for *bot_name*.

        Returns a status dict with ``"bot_name"`` and ``"triggered_at"``.
        """
        if bot_name not in self._versions:
            raise KeyError(f"Bot '{bot_name}' is not tracked.")
        return {
            "bot_name": bot_name,
            "triggered_at": datetime.now(timezone.utc).isoformat(),
            "status": "retraining_scheduled",
        }
