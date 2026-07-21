"""
Competition Engine — manages Bot Wars competitions, submissions, scoring,
and leaderboards for the DreamCo Bot Wars Bot.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from framework import GlobalAISourcesFlow  # noqa: F401


class CompetitionCategory(Enum):
    CREATIVITY = "creativity"
    LEARNING = "learning"
    PROBLEM_SOLVING = "problem_solving"
    STUDENT = "student"
    HOBBYIST = "hobbyist"
    CORPORATE = "corporate"
    COMMUNITY = "community"


class CompetitionEngineError(Exception):
    """Raised for invalid operations within the CompetitionEngine."""


class CompetitionEngine:
    """Manages Bot Wars competitions, bot submissions, scoring, and leaderboards.

    All data is stored in-memory; intended for integration with a persistence
    layer in production.
    """

    SCORE_KEYS = {"creativity", "accuracy", "speed", "innovation"}

    def __init__(self) -> None:
        self._competitions: dict = {}
        self._submissions: dict = {}

    # ------------------------------------------------------------------
    # Competition management
    # ------------------------------------------------------------------

    def create_competition(
        self,
        name: str,
        category: str,
        description: str,
        prize_usd: float = 0.0,
    ) -> dict:
        """Create a new competition.

        Parameters
        ----------
        name:        Human-readable competition name.
        category:    One of CompetitionCategory values.
        description: Short description of the competition goals.
        prize_usd:   Prize pool in USD (0 for community competitions).

        Returns
        -------
        dict  Competition record.
        """
        try:
            CompetitionCategory(category)
        except ValueError:
            valid = [c.value for c in CompetitionCategory]
            raise CompetitionEngineError(
                f"Invalid category '{category}'. Valid values: {valid}"
            )

        if not name or not name.strip():
            raise CompetitionEngineError("Competition name must not be empty.")

        competition_id = str(uuid.uuid4())
        record = {
            "id": competition_id,
            "name": name.strip(),
            "category": category,
            "description": description,
            "prize_usd": prize_usd,
            "status": "open",
            "submissions": [],
        }
        self._competitions[competition_id] = record
        return record

    def list_competitions(self, category: Optional[str] = None) -> list:
        """Return all competitions, optionally filtered by category."""
        comps = list(self._competitions.values())
        if category is not None:
            comps = [c for c in comps if c["category"] == category]
        return comps

    # ------------------------------------------------------------------
    # Submission management
    # ------------------------------------------------------------------

    def submit_bot(
        self,
        competition_id: str,
        user_id: str,
        bot_name: str,
        bot_description: str,
    ) -> dict:
        """Submit a bot to a competition.

        Returns
        -------
        dict  Submission record.
        """
        competition = self._get_competition(competition_id)
        if competition["status"] != "open":
            raise CompetitionEngineError(
                f"Competition '{competition_id}' is not open for submissions."
            )

        submission_id = str(uuid.uuid4())
        record = {
            "id": submission_id,
            "competition_id": competition_id,
            "user_id": user_id,
            "bot_name": bot_name,
            "bot_description": bot_description,
            "scores": {},
            "total_score": 0.0,
        }
        self._submissions[submission_id] = record
        competition["submissions"].append(submission_id)
        return record

    def score_submission(
        self,
        competition_id: str,
        submission_id: str,
        scores: dict,
    ) -> dict:
        """Assign scores to a submission.

        Parameters
        ----------
        scores : dict
            Must contain keys: creativity, accuracy, speed, innovation (each 0-100).

        Returns
        -------
        dict  Updated submission record with total_score.
        """
        self._get_competition(competition_id)
        submission = self._get_submission(submission_id, competition_id)

        missing = self.SCORE_KEYS - set(scores.keys())
        if missing:
            raise CompetitionEngineError(
                f"Missing score keys: {missing}. Required: {self.SCORE_KEYS}"
            )

        for key, val in scores.items():
            if key in self.SCORE_KEYS:
                if not (0 <= float(val) <= 100):
                    raise CompetitionEngineError(
                        f"Score for '{key}' must be between 0 and 100."
                    )

        validated = {k: float(scores[k]) for k in self.SCORE_KEYS}
        submission["scores"] = validated
        submission["total_score"] = sum(validated.values()) / len(validated)
        return submission

    # ------------------------------------------------------------------
    # Leaderboard & winner
    # ------------------------------------------------------------------

    def get_leaderboard(self, competition_id: str) -> list:
        """Return submissions sorted by total_score descending."""
        competition = self._get_competition(competition_id)
        submissions = [
            self._submissions[sid]
            for sid in competition["submissions"]
            if sid in self._submissions
        ]
        return sorted(submissions, key=lambda s: s["total_score"], reverse=True)

    def get_winner(self, competition_id: str) -> dict:
        """Return the top-scoring submission, or an empty dict if none exist."""
        leaderboard = self.get_leaderboard(competition_id)
        return leaderboard[0] if leaderboard else {}

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_competition(self, competition_id: str) -> dict:
        if competition_id not in self._competitions:
            raise CompetitionEngineError(
                f"Competition '{competition_id}' not found."
            )
        return self._competitions[competition_id]

    def _get_submission(self, submission_id: str, competition_id: str) -> dict:
        if submission_id not in self._submissions:
            raise CompetitionEngineError(
                f"Submission '{submission_id}' not found."
            )
        sub = self._submissions[submission_id]
        if sub["competition_id"] != competition_id:
            raise CompetitionEngineError(
                f"Submission '{submission_id}' does not belong to competition '{competition_id}'."
            )
        return sub
