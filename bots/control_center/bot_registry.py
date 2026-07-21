"""
DreamCo Control Tower — Bot Registry

Centralised, JSON-backed store of all registered bots and their repos.
Designed to scale; a MongoDB backend can be swapped in by subclassing.

# GLOBAL AI SOURCES FLOW
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from framework import GlobalAISourcesFlow  # noqa: F401


class BotRegistry:
    """Centralised registry for all DreamCo bots and their repositories.

    By default the registry is **in-memory** only.  Pass *persist_path* to
    automatically load from and save to a JSON file.
    """

    def __init__(self, persist_path: Optional[str] = None) -> None:
        self._persist_path = persist_path
        self._bots: dict[str, dict] = {}
        if persist_path and Path(persist_path).exists():
            self._load()

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(
        self,
        bot_name: str,
        repo_name: str = "",
        config: Optional[dict] = None,
    ) -> dict:
        """Register (or update) a bot in the registry.

        Parameters
        ----------
        bot_name:   Unique bot identifier (e.g. ``"real_estate_bot"``).
        repo_name:  GitHub repository name for the bot.
        config:     Optional dict of additional configuration.

        Returns
        -------
        The registry entry for *bot_name*.
        """
        existing = self._bots.get(bot_name, {})
        entry: dict[str, Any] = {
            "bot_name": bot_name,
            "repo_name": repo_name or existing.get("repo_name", ""),
            "status": existing.get("status", "idle"),
            "registered_at": existing.get(
                "registered_at", datetime.now(timezone.utc).isoformat()
            ),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "last_heartbeat": existing.get("last_heartbeat"),
            "last_pr": existing.get("last_pr"),
            "last_commit": existing.get("last_commit"),
            "open_issues": existing.get("open_issues", 0),
            "config": {**existing.get("config", {}), **(config or {})},
        }
        self._bots[bot_name] = entry
        self._save()
        return entry

    def deregister(self, bot_name: str) -> bool:
        """Remove a bot from the registry.  Returns True if it existed."""
        existed = bot_name in self._bots
        self._bots.pop(bot_name, None)
        self._save()
        return existed

    # ------------------------------------------------------------------
    # Status updates
    # ------------------------------------------------------------------

    def update_status(self, bot_name: str, status: str, **kwargs: Any) -> dict:
        """Update the *status* (and any extra fields) for *bot_name*.

        Creates a minimal entry if the bot is not yet registered.
        """
        if bot_name not in self._bots:
            self.register(bot_name)
        self._bots[bot_name]["status"] = status
        self._bots[bot_name]["updated_at"] = datetime.now(timezone.utc).isoformat()
        for key, value in kwargs.items():
            self._bots[bot_name][key] = value
        self._save()
        return self._bots[bot_name]

    def record_heartbeat(self, bot_name: str) -> dict:
        """Update ``last_heartbeat`` timestamp for *bot_name*."""
        return self.update_status(
            bot_name,
            status=self._bots.get(bot_name, {}).get("status", "idle"),
            last_heartbeat=datetime.now(timezone.utc).isoformat(),
        )

    def record_pr(self, bot_name: str, pr_url: str) -> dict:
        """Record the most recent pull request for *bot_name*."""
        return self.update_status(bot_name, status="updated", last_pr=pr_url)

    def record_commit(self, bot_name: str, sha: str) -> dict:
        """Record the most recent commit SHA for *bot_name*."""
        return self.update_status(bot_name, status="updated", last_commit=sha)

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get(self, bot_name: str) -> Optional[dict]:
        """Return the registry entry for *bot_name*, or None."""
        return self._bots.get(bot_name)

    def get_all(self) -> list[dict]:
        """Return all registered bots as a list."""
        return list(self._bots.values())

    def get_by_status(self, status: str) -> list[dict]:
        """Return bots filtered by *status*."""
        return [b for b in self._bots.values() if b.get("status") == status]

    def count(self) -> int:
        """Return the total number of registered bots."""
        return len(self._bots)

    def summary(self) -> dict:
        """Return aggregate registry statistics."""
        statuses: dict[str, int] = {}
        for bot in self._bots.values():
            s = bot.get("status", "unknown")
            statuses[s] = statuses.get(s, 0) + 1
        return {
            "total_bots": self.count(),
            "by_status": statuses,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------

    def _save(self) -> None:
        if not self._persist_path:
            return
        path = Path(self._persist_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps({"bots": list(self._bots.values())}, indent=2),
            encoding="utf-8",
        )

    def _load(self) -> None:
        if not self._persist_path:
            return
        try:
            data = json.loads(Path(self._persist_path).read_text(encoding="utf-8"))
            for bot in data.get("bots", []):
                name = bot.get("bot_name")
                if name:
                    self._bots[name] = bot
        except (json.JSONDecodeError, OSError):
            pass

    def export_json(self) -> str:
        """Return the full registry as a JSON string."""
        return json.dumps({"bots": list(self._bots.values())}, indent=2)


__all__ = ["BotRegistry"]
