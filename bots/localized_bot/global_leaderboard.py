"""
Global Leaderboard — community voting and ranking for the DreamCo Localized Bot.

Tracks registered regional bots, collects votes, and provides ranked views
by region, category, or overall score.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

import sys
import os
import uuid
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401


class GlobalLeaderboard:
    """In-memory community leaderboard for regional bots."""

    def __init__(self) -> None:
        self._bots: dict[str, dict] = {}
        self._votes: list[dict] = []

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register_bot(
        self,
        bot_name: str,
        creator_id: str,
        region_id: str,
        description: str,
        category: str,
    ) -> dict:
        """
        Register a new bot on the leaderboard.

        Returns the created bot record dict.
        """
        bot_id = str(uuid.uuid4())
        record = {
            "bot_id": bot_id,
            "bot_name": bot_name,
            "creator_id": creator_id,
            "region_id": region_id,
            "description": description,
            "category": category,
            "registered_at": datetime.now(timezone.utc).isoformat(),
            "vote_count": 0,
            "total_score": 0,
            "avg_score": 0.0,
        }
        self._bots[bot_id] = record
        return dict(record)

    # ------------------------------------------------------------------
    # Voting
    # ------------------------------------------------------------------

    def vote_for_bot(self, bot_id: str, voter_id: str, score: int) -> dict:
        """
        Cast a vote for *bot_id* with *score* (1–5).

        Returns the updated bot record.
        Raises ValueError for invalid score or unknown bot_id.
        """
        if score < 1 or score > 5:
            raise ValueError(f"Score must be between 1 and 5, got {score}.")
        if bot_id not in self._bots:
            raise KeyError(f"Bot '{bot_id}' not found.")

        vote = {
            "bot_id": bot_id,
            "voter_id": voter_id,
            "score": score,
            "voted_at": datetime.now(timezone.utc).isoformat(),
        }
        self._votes.append(vote)

        bot = self._bots[bot_id]
        bot["vote_count"] += 1
        bot["total_score"] += score
        bot["avg_score"] = round(bot["total_score"] / bot["vote_count"], 2)
        return dict(bot)

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    def get_leaderboard(
        self,
        region_id: str | None = None,
        category: str | None = None,
    ) -> list:
        """
        Return all registered bots, optionally filtered by *region_id* and/or
        *category*, sorted by avg_score descending then vote_count descending.
        """
        bots = list(self._bots.values())
        if region_id is not None:
            bots = [b for b in bots if b["region_id"] == region_id]
        if category is not None:
            bots = [b for b in bots if b["category"] == category]
        return sorted(bots, key=lambda b: (-b["avg_score"], -b["vote_count"]))

    def get_top_bots(self, n: int = 10) -> list:
        """Return the top *n* bots across all regions, sorted by avg_score desc."""
        return self.get_leaderboard()[:n]

    def get_regional_winner(self, region_id: str) -> dict | None:
        """Return the highest-ranked bot for *region_id*, or None if no bots exist."""
        regional = self.get_leaderboard(region_id=region_id)
        return dict(regional[0]) if regional else None
