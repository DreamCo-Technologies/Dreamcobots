"""
DreamCo Control Tower — Bot Manager
====================================
Centralized registry and lifecycle manager for all DreamCo Buddy Bots.

Supports registering, updating, removing, and querying bots backed by a
JSON config file (``config/bots.json``).  Designed to scale to 1 000+ bots;
each bot entry tracks:

  - name, repo coordinates, tier, status
  - heartbeat timestamps
  - last update / last PR timestamps
  - conflict flag
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


_DEFAULT_CONFIG = os.path.join(os.path.dirname(__file__), "..", "config", "bots.json")

# Valid lifecycle statuses
STATUS_ACTIVE = "active"
STATUS_UPDATING = "updating"
STATUS_CONFLICT = "conflict"
STATUS_OFFLINE = "offline"
STATUS_ONBOARDING = "onboarding"

VALID_STATUSES = {STATUS_ACTIVE, STATUS_UPDATING, STATUS_CONFLICT, STATUS_OFFLINE, STATUS_ONBOARDING}


class BotManager:
    """Registry and lifecycle manager for DreamCo bots.

    Parameters
    ----------
    config_path:
        Path to the JSON file that persists the bot registry.
        Defaults to ``config/bots.json`` relative to this module.
    """

    def __init__(self, config_path: Optional[str] = None) -> None:
        self._config_path: str = config_path or _DEFAULT_CONFIG
        self._bots: Dict[str, Dict[str, Any]] = {}
        self._load()

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _load(self) -> None:
        """Load bots from the JSON config file, if it exists."""
        if not os.path.exists(self._config_path):
            return
        try:
            with open(self._config_path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            if isinstance(data, list):
                for entry in data:
                    name = entry.get("name")
                    if name:
                        self._bots[name] = entry
        except (json.JSONDecodeError, OSError):
            pass

    def save(self) -> None:
        """Persist the current bot registry to the JSON config file."""
        os.makedirs(os.path.dirname(self._config_path), exist_ok=True)
        with open(self._config_path, "w", encoding="utf-8") as fh:
            json.dump(list(self._bots.values()), fh, indent=2)

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def register_bot(
        self,
        name: str,
        repo_name: str,
        repo_path: str,
        tier: str = "free",
        description: str = "",
    ) -> Dict[str, Any]:
        """Register a new bot in the registry.

        Parameters
        ----------
        name:       Unique identifier for this bot.
        repo_name:  GitHub repository name (e.g. ``Dreamcobots``).
        repo_path:  Path within the repo where the bot lives.
        tier:       Subscription tier (``free`` / ``pro`` / ``enterprise``).
        description: Short human-readable description.

        Returns
        -------
        dict
            The newly created bot entry.
        """
        entry: Dict[str, Any] = {
            "name": name,
            "repoName": repo_name,
            "repoPath": repo_path,
            "tier": tier,
            "status": STATUS_ONBOARDING,
            "heartbeat": None,
            "lastUpdate": None,
            "lastPR": None,
            "conflictsDetected": False,
            "description": description,
            "registeredAt": datetime.now(timezone.utc).isoformat(),
        }
        self._bots[name] = entry
        return entry

    def remove_bot(self, name: str) -> bool:
        """Remove a bot from the registry.  Returns True if the bot existed."""
        if name in self._bots:
            del self._bots[name]
            return True
        return False

    def get_bot(self, name: str) -> Optional[Dict[str, Any]]:
        """Return a single bot entry, or None if not found."""
        return self._bots.get(name)

    def list_bots(self) -> List[Dict[str, Any]]:
        """Return all registered bots as a list."""
        return list(self._bots.values())

    def total_bots(self) -> int:
        """Return the total number of registered bots."""
        return len(self._bots)

    # ------------------------------------------------------------------
    # Status & heartbeat
    # ------------------------------------------------------------------

    def update_heartbeat(self, name: str) -> bool:
        """Record that a bot has sent a heartbeat signal.

        Returns True if the bot was found and updated.
        """
        if name not in self._bots:
            return False
        self._bots[name]["heartbeat"] = datetime.now(timezone.utc).isoformat()
        if self._bots[name].get("status") == STATUS_OFFLINE:
            self._bots[name]["status"] = STATUS_ACTIVE
        return True

    def set_status(self, name: str, status: str) -> bool:
        """Set the lifecycle status for a bot.

        Returns True if the update succeeded, False if the bot is unknown
        or the status value is invalid.
        """
        if name not in self._bots:
            return False
        if status not in VALID_STATUSES:
            return False
        self._bots[name]["status"] = status
        return True

    def mark_conflict(self, name: str, conflict: bool = True) -> bool:
        """Flag or clear a merge conflict on a bot.  Returns True on success."""
        if name not in self._bots:
            return False
        self._bots[name]["conflictsDetected"] = conflict
        if conflict:
            self._bots[name]["status"] = STATUS_CONFLICT
        return True

    def record_update(self, name: str) -> bool:
        """Record a successful upgrade on a bot.  Returns True on success."""
        if name not in self._bots:
            return False
        self._bots[name]["lastUpdate"] = datetime.now(timezone.utc).isoformat()
        self._bots[name]["status"] = STATUS_ACTIVE
        return True

    def record_pr(self, name: str, pr_url: str = "") -> bool:
        """Record that a PR was opened for a bot.  Returns True on success."""
        if name not in self._bots:
            return False
        self._bots[name]["lastPR"] = datetime.now(timezone.utc).isoformat()
        if pr_url:
            self._bots[name]["lastPRUrl"] = pr_url
        return True

    # ------------------------------------------------------------------
    # Summaries & queries
    # ------------------------------------------------------------------

    def get_active_bots(self) -> List[Dict[str, Any]]:
        """Return only bots whose status is ``active``."""
        return [b for b in self._bots.values() if b.get("status") == STATUS_ACTIVE]

    def get_conflicted_bots(self) -> List[Dict[str, Any]]:
        """Return bots that currently have conflicts detected."""
        return [b for b in self._bots.values() if b.get("conflictsDetected")]

    def get_offline_bots(self) -> List[Dict[str, Any]]:
        """Return bots whose status is ``offline``."""
        return [b for b in self._bots.values() if b.get("status") == STATUS_OFFLINE]

    def get_summary(self) -> Dict[str, Any]:
        """Return a high-level summary of the bot registry."""
        statuses: Dict[str, int] = {}
        for bot in self._bots.values():
            s = bot.get("status", "unknown")
            statuses[s] = statuses.get(s, 0) + 1
        return {
            "total": self.total_bots(),
            "by_status": statuses,
            "conflicts": len(self.get_conflicted_bots()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
