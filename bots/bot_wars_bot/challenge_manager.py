"""
Challenge Manager — handles DreamCo Bot Wars global challenges and campaigns.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import uuid
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Optional

from framework import GlobalAISourcesFlow  # noqa: F401


class ChallengeType(Enum):
    CREATIVITY_SPRINT = "creativity_sprint"
    REAL_WORLD_SOLVER = "real_world_solver"
    BOT_SHOWDOWN = "bot_showdown"
    REGIONAL_CHALLENGE = "regional_challenge"
    INDUSTRY_CHALLENGE = "industry_challenge"


CHALLENGE_TYPES = [ct.value for ct in ChallengeType]


class ChallengeManagerError(Exception):
    """Raised for invalid operations within the ChallengeManager."""


class ChallengeManager:
    """Manages DreamCo Bot Wars global challenges and campaign participation.

    All data is stored in-memory; intended for integration with a persistence
    layer in production.
    """

    def __init__(self) -> None:
        self._challenges: dict = {}
        self._participants: dict = {}
        self._solutions: dict = {}

    # ------------------------------------------------------------------
    # Challenge lifecycle
    # ------------------------------------------------------------------

    def create_challenge(
        self,
        title: str,
        challenge_type: str,
        description: str,
        duration_days: int,
        reward_tokens: int,
    ) -> dict:
        """Create a new global challenge.

        Parameters
        ----------
        title:          Human-readable challenge title.
        challenge_type: One of CHALLENGE_TYPES values.
        description:    Goals and rules of the challenge.
        duration_days:  How many days the challenge remains open.
        reward_tokens:  Token reward for winning / top submissions.

        Returns
        -------
        dict  Challenge record.
        """
        if challenge_type not in CHALLENGE_TYPES:
            raise ChallengeManagerError(
                f"Invalid challenge type '{challenge_type}'. Valid: {CHALLENGE_TYPES}"
            )
        if not title or not title.strip():
            raise ChallengeManagerError("Challenge title must not be empty.")
        if duration_days <= 0:
            raise ChallengeManagerError("duration_days must be a positive integer.")

        challenge_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        record = {
            "id": challenge_id,
            "title": title.strip(),
            "challenge_type": challenge_type,
            "description": description,
            "duration_days": duration_days,
            "reward_tokens": reward_tokens,
            "created_at": now.isoformat(),
            "expires_at": (now + timedelta(days=duration_days)).isoformat(),
            "status": "active",
            "participants": [],
            "solutions": [],
        }
        self._challenges[challenge_id] = record
        return record

    def list_active_challenges(self) -> list:
        """Return all challenges with status 'active'."""
        return [c for c in self._challenges.values() if c["status"] == "active"]

    # ------------------------------------------------------------------
    # Participation
    # ------------------------------------------------------------------

    def join_challenge(
        self,
        challenge_id: str,
        user_id: str,
        team_name: Optional[str] = None,
    ) -> dict:
        """Register a user (optionally in a team) for a challenge.

        Returns
        -------
        dict  Participant record.
        """
        challenge = self._get_challenge(challenge_id)
        if challenge["status"] != "active":
            raise ChallengeManagerError(
                f"Challenge '{challenge_id}' is not active."
            )

        key = (challenge_id, user_id)
        if key in self._participants:
            raise ChallengeManagerError(
                f"User '{user_id}' has already joined challenge '{challenge_id}'."
            )

        participant_id = str(uuid.uuid4())
        record = {
            "id": participant_id,
            "challenge_id": challenge_id,
            "user_id": user_id,
            "team_name": team_name,
            "joined_at": datetime.now(timezone.utc).isoformat(),
        }
        self._participants[key] = record
        challenge["participants"].append(user_id)
        return record

    def submit_solution(
        self,
        challenge_id: str,
        user_id: str,
        solution_description: str,
    ) -> dict:
        """Submit a solution to a challenge.

        The user must have joined the challenge before submitting.

        Returns
        -------
        dict  Solution record.
        """
        challenge = self._get_challenge(challenge_id)
        if challenge["status"] != "active":
            raise ChallengeManagerError(
                f"Challenge '{challenge_id}' is not accepting solutions."
            )

        key = (challenge_id, user_id)
        if key not in self._participants:
            raise ChallengeManagerError(
                f"User '{user_id}' has not joined challenge '{challenge_id}'. "
                "Call join_challenge first."
            )

        solution_id = str(uuid.uuid4())
        record = {
            "id": solution_id,
            "challenge_id": challenge_id,
            "user_id": user_id,
            "solution_description": solution_description,
            "submitted_at": datetime.now(timezone.utc).isoformat(),
        }
        self._solutions[solution_id] = record
        challenge["solutions"].append(solution_id)
        return record

    # ------------------------------------------------------------------
    # Stats
    # ------------------------------------------------------------------

    def get_challenge_stats(self, challenge_id: str) -> dict:
        """Return participation and submission statistics for a challenge."""
        challenge = self._get_challenge(challenge_id)
        participant_count = len(challenge["participants"])
        submission_count = len(challenge["solutions"])
        return {
            "challenge_id": challenge_id,
            "title": challenge["title"],
            "status": challenge["status"],
            "participant_count": participant_count,
            "submission_count": submission_count,
            "reward_tokens": challenge["reward_tokens"],
            "expires_at": challenge["expires_at"],
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_challenge(self, challenge_id: str) -> dict:
        if challenge_id not in self._challenges:
            raise ChallengeManagerError(
                f"Challenge '{challenge_id}' not found."
            )
        return self._challenges[challenge_id]
