"""
Big Bro AI — Memory System

Realistic, consent-based user memory.  Big Bro only remembers what people
choose to share.  Every profile can be queried, updated, or deleted.

GLOBAL AI SOURCES FLOW: participates via big_bro_ai.py pipeline.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Life situation categories
# ---------------------------------------------------------------------------

class LifeSituation(Enum):
    STRESS = "stress"
    ANGER = "anger"
    CONFUSION = "confusion"
    MOTIVATION_DIP = "motivation_dip"
    WIN = "win"
    SETBACK = "setback"
    RELATIONSHIP = "relationship"
    FINANCIAL = "financial"
    SCHOOL = "school"
    WORK = "work"
    HEALTH = "health"
    CONFIDENCE = "confidence"
    NEUTRAL = "neutral"


# ---------------------------------------------------------------------------
# Memory tags
# ---------------------------------------------------------------------------

MEMORY_TAGS: frozenset[str] = frozenset(
    {
        "confidence",
        "money",
        "relationships",
        "stress",
        "wins",
        "focus",
        "school",
        "work",
        "tech",
        "fitness",
        "family",
        "dating",
        "goals",
    }
)


# ---------------------------------------------------------------------------
# User profile
# ---------------------------------------------------------------------------

@dataclass
class MemoryEntry:
    """A single timestamped memory entry."""
    timestamp: str
    situation: str
    note: str
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "situation": self.situation,
            "note": self.note,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MemoryEntry":
        return cls(
            timestamp=data["timestamp"],
            situation=data["situation"],
            note=data["note"],
            tags=data.get("tags", []),
        )


@dataclass
class UserProfile:
    """
    Persistent memory profile for a single user.

    Attributes
    ----------
    user_id : str
        Unique identifier (e.g. username or UUID).
    name : str
        Display name.
    nickname : str
        Optional nickname Big Bro uses.
    how_we_met : str
        Context of first interaction.
    goals : list[str]
        Current goals (money, coding, life, etc.).
    struggles : list[str]
        Active struggles.
    wins : list[str]
        Documented wins.
    advice_given : list[str]
        Advice already delivered so Big Bro doesn't repeat himself.
    income_paths : list[str]
        Income lanes the user has chosen.
    skill_level : str
        Self-reported skill level (beginner / intermediate / advanced).
    relationship_tier : str
        One of: creator, inner_circle, friend, community, new_user.
    memory_entries : list[MemoryEntry]
        Chronological log of life situations shared.
    tags : list[str]
        Active topic tags derived from conversations.
    created_at : str
        ISO timestamp of profile creation.
    updated_at : str
        ISO timestamp of last update.
    """

    user_id: str
    name: str
    nickname: str = ""
    how_we_met: str = ""
    goals: list[str] = field(default_factory=list)
    struggles: list[str] = field(default_factory=list)
    wins: list[str] = field(default_factory=list)
    advice_given: list[str] = field(default_factory=list)
    income_paths: list[str] = field(default_factory=list)
    skill_level: str = "beginner"
    relationship_tier: str = "new_user"
    memory_entries: list[MemoryEntry] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    updated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def add_memory(
        self,
        situation: str,
        note: str,
        tags: Optional[list[str]] = None,
    ) -> MemoryEntry:
        """Log a new memory entry and return it."""
        entry = MemoryEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            situation=situation,
            note=note,
            tags=tags or [],
        )
        self.memory_entries.append(entry)
        self._touch()
        return entry

    def latest_memory(self) -> Optional[MemoryEntry]:
        """Return the most recent memory entry, or None."""
        return self.memory_entries[-1] if self.memory_entries else None

    def memories_by_tag(self, tag: str) -> list[MemoryEntry]:
        """Return all memory entries that carry *tag*."""
        return [e for e in self.memory_entries if tag in e.tags]

    def add_goal(self, goal: str) -> None:
        if goal not in self.goals:
            self.goals.append(goal)
            self._touch()

    def add_struggle(self, struggle: str) -> None:
        if struggle not in self.struggles:
            self.struggles.append(struggle)
            self._touch()

    def add_win(self, win: str) -> None:
        self.wins.append(win)
        self._touch()

    def mark_advice_given(self, advice: str) -> None:
        if advice not in self.advice_given:
            self.advice_given.append(advice)
            self._touch()

    def add_income_path(self, path: str) -> None:
        if path not in self.income_paths:
            self.income_paths.append(path)
            self._touch()

    def _touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc).isoformat()

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "name": self.name,
            "nickname": self.nickname,
            "how_we_met": self.how_we_met,
            "goals": self.goals,
            "struggles": self.struggles,
            "wins": self.wins,
            "advice_given": self.advice_given,
            "income_paths": self.income_paths,
            "skill_level": self.skill_level,
            "relationship_tier": self.relationship_tier,
            "memory_entries": [e.to_dict() for e in self.memory_entries],
            "tags": self.tags,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "UserProfile":
        entries = [MemoryEntry.from_dict(e) for e in data.get("memory_entries", [])]
        return cls(
            user_id=data["user_id"],
            name=data["name"],
            nickname=data.get("nickname", ""),
            how_we_met=data.get("how_we_met", ""),
            goals=data.get("goals", []),
            struggles=data.get("struggles", []),
            wins=data.get("wins", []),
            advice_given=data.get("advice_given", []),
            income_paths=data.get("income_paths", []),
            skill_level=data.get("skill_level", "beginner"),
            relationship_tier=data.get("relationship_tier", "new_user"),
            memory_entries=entries,
            tags=data.get("tags", []),
            created_at=data.get("created_at", datetime.now(timezone.utc).isoformat()),
            updated_at=data.get("updated_at", datetime.now(timezone.utc).isoformat()),
        )


# ---------------------------------------------------------------------------
# Memory System (in-memory store)
# ---------------------------------------------------------------------------

class MemorySystemError(Exception):
    """Raised when a memory operation cannot be completed."""


class MemorySystem:
    """
    Manages user profiles for Big Bro AI.

    All memory is consent-based: users can read, update, or delete their
    own profile at any time.

    Parameters
    ----------
    max_profiles : int | None
        Maximum number of profiles to store.  None means unlimited.
    """

    def __init__(self, max_profiles: Optional[int] = None) -> None:
        self._profiles: dict[str, UserProfile] = {}
        self.max_profiles = max_profiles

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def create_profile(
        self,
        user_id: str,
        name: str,
        nickname: str = "",
        how_we_met: str = "",
        relationship_tier: str = "new_user",
    ) -> UserProfile:
        """Create and register a new user profile."""
        if self.max_profiles is not None and len(self._profiles) >= self.max_profiles:
            raise MemorySystemError(
                f"Profile limit ({self.max_profiles}) reached. Upgrade your tier."
            )
        if user_id in self._profiles:
            raise MemorySystemError(f"Profile for '{user_id}' already exists.")
        profile = UserProfile(
            user_id=user_id,
            name=name,
            nickname=nickname,
            how_we_met=how_we_met,
            relationship_tier=relationship_tier,
        )
        self._profiles[user_id] = profile
        return profile

    def get_profile(self, user_id: str) -> Optional[UserProfile]:
        """Return the profile for *user_id*, or None if not found."""
        return self._profiles.get(user_id)

    def update_profile(self, user_id: str, **fields: Any) -> UserProfile:
        """Update scalar fields on a user's profile."""
        profile = self._require_profile(user_id)
        allowed = {
            "name",
            "nickname",
            "how_we_met",
            "skill_level",
            "relationship_tier",
        }
        for key, value in fields.items():
            if key in allowed:
                setattr(profile, key, value)
        profile._touch()
        return profile

    def delete_profile(self, user_id: str) -> bool:
        """Permanently delete a user's profile.  Returns True on success."""
        if user_id in self._profiles:
            del self._profiles[user_id]
            return True
        return False

    # ------------------------------------------------------------------
    # Memory operations
    # ------------------------------------------------------------------

    def log_memory(
        self,
        user_id: str,
        situation: str,
        note: str,
        tags: Optional[list[str]] = None,
    ) -> MemoryEntry:
        """Log a new memory entry for *user_id*."""
        profile = self._require_profile(user_id)
        return profile.add_memory(situation, note, tags)

    def recall(self, user_id: str) -> str:
        """
        Generate a human-like recall message that Big Bro might say.

        Example: "Last time we talked, you said school was stressing you."
        """
        profile = self._require_profile(user_id)
        latest = profile.latest_memory()
        if latest is None:
            return f"This is the first time we've spoken, {profile.name}."
        return (
            f"Last time we talked, {profile.name}, you mentioned "
            f"'{latest.situation}' — {latest.note}. How's that going now?"
        )

    def summary(self, user_id: str) -> dict:
        """Return a structured summary of what Big Bro remembers."""
        profile = self._require_profile(user_id)
        return {
            "name": profile.name,
            "nickname": profile.nickname,
            "goals": profile.goals,
            "struggles": profile.struggles,
            "wins": profile.wins,
            "income_paths": profile.income_paths,
            "skill_level": profile.skill_level,
            "relationship_tier": profile.relationship_tier,
            "memory_count": len(profile.memory_entries),
            "tags": profile.tags,
            "how_we_met": profile.how_we_met,
        }

    # ------------------------------------------------------------------
    # Bulk operations
    # ------------------------------------------------------------------

    def list_users(self) -> list[str]:
        """Return all registered user IDs."""
        return sorted(self._profiles.keys())

    def profile_count(self) -> int:
        """Return the number of stored profiles."""
        return len(self._profiles)

    # ------------------------------------------------------------------
    # Serialisation helpers (for persistence layer)
    # ------------------------------------------------------------------

    def export_all(self) -> list[dict]:
        """Export all profiles as a list of dicts (for JSON persistence)."""
        return [p.to_dict() for p in self._profiles.values()]

    def import_profiles(self, data: list[dict]) -> int:
        """Import profiles from a list of dicts.  Returns count imported."""
        count = 0
        for item in data:
            profile = UserProfile.from_dict(item)
            self._profiles[profile.user_id] = profile
            count += 1
        return count

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _require_profile(self, user_id: str) -> UserProfile:
        profile = self._profiles.get(user_id)
        if profile is None:
            raise MemorySystemError(f"No profile found for '{user_id}'.")
        return profile
