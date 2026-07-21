"""
Buddy Bot — Memory System

Persistent, user-tailored memory enabling truly personal interactions:
  • Long-term user profiles with interests, habits, and preferences
  • Life milestone tracking (anniversaries, promotions, goals)
  • Anniversary and important date reminders
  • Dynamic learning — profiles update automatically from conversations
  • Relationship depth scoring (casual → intimate companion)
  • Privacy controls — users can delete any or all stored data
  • Episodic memory — stores "chapters" of a user's life journey

GLOBAL AI SOURCES FLOW: this module participates in GlobalAISourcesFlow
via BuddyBot.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Milestone categories
# ---------------------------------------------------------------------------

class MilestoneCategory(Enum):
    PERSONAL = "personal"
    CAREER = "career"
    HEALTH = "health"
    RELATIONSHIP = "relationship"
    FINANCIAL = "financial"
    EDUCATION = "education"
    CREATIVE = "creative"
    TRAVEL = "travel"
    SPIRITUAL = "spiritual"
    OTHER = "other"


class RelationshipDepth(Enum):
    """How deeply Buddy knows this user."""
    ACQUAINTANCE = "acquaintance"     # < 5 interactions
    CASUAL = "casual"                 # 5–20 interactions
    FAMILIAR = "familiar"             # 21–100 interactions
    CLOSE = "close"                   # 101–500 interactions
    COMPANION = "companion"           # > 500 interactions


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class LifeMilestone:
    """Represents a significant life event for a user."""
    milestone_id: str
    user_id: str
    title: str
    description: str
    category: MilestoneCategory
    date_achieved: str          # ISO date string, e.g. "2024-03-15"
    recurring_annually: bool = False
    celebrated: bool = False
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "milestone_id": self.milestone_id,
            "user_id": self.user_id,
            "title": self.title,
            "description": self.description,
            "category": self.category.value,
            "date_achieved": self.date_achieved,
            "recurring_annually": self.recurring_annually,
            "celebrated": self.celebrated,
            "tags": self.tags,
        }


@dataclass
class ImportantDate:
    """An anniversary or recurring important date."""
    date_id: str
    user_id: str
    label: str              # e.g. "Wedding Anniversary", "Mom's Birthday"
    month: int              # 1–12
    day: int                # 1–31
    year_started: Optional[int] = None
    reminder_days_before: int = 3
    notes: str = ""

    def to_dict(self) -> dict:
        return {
            "date_id": self.date_id,
            "user_id": self.user_id,
            "label": self.label,
            "month": self.month,
            "day": self.day,
            "year_started": self.year_started,
            "reminder_days_before": self.reminder_days_before,
            "notes": self.notes,
        }


@dataclass
class EpisodicMemory:
    """A single 'chapter' in a user's life as remembered by Buddy."""
    episode_id: str
    user_id: str
    title: str
    summary: str
    timestamp: float = field(default_factory=time.time)
    emotion_at_time: str = "neutral"
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "episode_id": self.episode_id,
            "user_id": self.user_id,
            "title": self.title,
            "summary": self.summary,
            "timestamp": self.timestamp,
            "emotion_at_time": self.emotion_at_time,
            "tags": self.tags,
        }


@dataclass
class UserProfile:
    """Comprehensive memory profile for a single user."""
    user_id: str
    display_name: str
    interaction_count: int = 0
    preferred_language: str = "en"
    interests: list[str] = field(default_factory=list)
    hobbies: list[str] = field(default_factory=list)
    goals: list[str] = field(default_factory=list)
    milestones: list[LifeMilestone] = field(default_factory=list)
    important_dates: list[ImportantDate] = field(default_factory=list)
    episodes: list[EpisodicMemory] = field(default_factory=list)
    personality_preference: str = "casual_friend"
    inside_jokes: list[str] = field(default_factory=list)
    custom_data: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    last_interaction: float = field(default_factory=time.time)

    @property
    def relationship_depth(self) -> RelationshipDepth:
        """Derive relationship depth from interaction count."""
        if self.interaction_count < 5:
            return RelationshipDepth.ACQUAINTANCE
        if self.interaction_count < 21:
            return RelationshipDepth.CASUAL
        if self.interaction_count < 101:
            return RelationshipDepth.FAMILIAR
        if self.interaction_count < 501:
            return RelationshipDepth.CLOSE
        return RelationshipDepth.COMPANION

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "display_name": self.display_name,
            "interaction_count": self.interaction_count,
            "preferred_language": self.preferred_language,
            "relationship_depth": self.relationship_depth.value,
            "interests": self.interests,
            "hobbies": self.hobbies,
            "goals": self.goals,
            "personality_preference": self.personality_preference,
            "inside_jokes": self.inside_jokes,
            "milestones_count": len(self.milestones),
            "important_dates_count": len(self.important_dates),
            "episodes_count": len(self.episodes),
            "custom_data": self.custom_data,
            "created_at": self.created_at,
            "last_interaction": self.last_interaction,
        }


class MemorySystemError(Exception):
    """Raised when a memory operation cannot be completed."""


class MemorySystem:
    """
    Long-term user memory for Buddy Bot.

    Parameters
    ----------
    max_profiles : int | None
        Maximum number of user profiles to store.  None = unlimited.
    """

    def __init__(self, max_profiles: Optional[int] = None) -> None:
        self.max_profiles = max_profiles
        self._profiles: dict[str, UserProfile] = {}
        self._milestone_counter: int = 0
        self._date_counter: int = 0
        self._episode_counter: int = 0

    # ------------------------------------------------------------------
    # Profile management
    # ------------------------------------------------------------------

    def create_profile(
        self,
        user_id: str,
        display_name: str,
        preferred_language: str = "en",
    ) -> UserProfile:
        """
        Create a new user memory profile.

        Parameters
        ----------
        user_id : str
            Unique user identifier.
        display_name : str
            User's preferred display name.
        preferred_language : str
            ISO 639-1 language code.

        Returns
        -------
        UserProfile

        Raises
        ------
        MemorySystemError
            If the profile limit has been reached or user_id already exists.
        """
        if user_id in self._profiles:
            raise MemorySystemError(f"Profile for user '{user_id}' already exists.")
        if self.max_profiles is not None and len(self._profiles) >= self.max_profiles:
            raise MemorySystemError(
                f"Profile limit of {self.max_profiles} reached. Upgrade to store more users."
            )
        profile = UserProfile(
            user_id=user_id,
            display_name=display_name,
            preferred_language=preferred_language,
        )
        self._profiles[user_id] = profile
        return profile

    def get_profile(self, user_id: str) -> UserProfile:
        """
        Retrieve a user profile.

        Raises
        ------
        MemorySystemError
            If the profile does not exist.
        """
        if user_id not in self._profiles:
            raise MemorySystemError(f"No profile found for user '{user_id}'.")
        return self._profiles[user_id]

    def update_profile(self, user_id: str, **kwargs) -> UserProfile:
        """
        Update mutable fields on a user profile.

        Accepted keyword arguments: ``display_name``, ``preferred_language``,
        ``personality_preference``, ``interests``, ``hobbies``, ``goals``,
        ``custom_data``.
        """
        profile = self.get_profile(user_id)
        allowed = {
            "display_name", "preferred_language", "personality_preference",
            "interests", "hobbies", "goals", "custom_data",
        }
        for key, value in kwargs.items():
            if key not in allowed:
                raise MemorySystemError(f"Field '{key}' is not updatable.")
            setattr(profile, key, value)
        return profile

    def record_interaction(self, user_id: str) -> UserProfile:
        """Increment the interaction counter and refresh last_interaction timestamp."""
        profile = self.get_profile(user_id)
        profile.interaction_count += 1
        profile.last_interaction = time.time()
        return profile

    def learn_interest(self, user_id: str, interest: str) -> UserProfile:
        """Dynamically add an interest to the user's profile."""
        profile = self.get_profile(user_id)
        if interest not in profile.interests:
            profile.interests.append(interest)
        return profile

    def add_inside_joke(self, user_id: str, joke: str) -> UserProfile:
        """Store a shared inside joke for personalised conversations."""
        profile = self.get_profile(user_id)
        if joke not in profile.inside_jokes:
            profile.inside_jokes.append(joke)
        return profile

    def delete_profile(self, user_id: str) -> None:
        """Permanently delete a user profile (GDPR / privacy action)."""
        if user_id not in self._profiles:
            raise MemorySystemError(f"No profile found for user '{user_id}'.")
        del self._profiles[user_id]

    def list_profiles(self) -> list[dict]:
        """Return a summary list of all profiles."""
        return [p.to_dict() for p in self._profiles.values()]

    # ------------------------------------------------------------------
    # Milestones
    # ------------------------------------------------------------------

    def add_milestone(
        self,
        user_id: str,
        title: str,
        description: str,
        category: MilestoneCategory,
        date_achieved: str,
        recurring_annually: bool = False,
        tags: Optional[list[str]] = None,
    ) -> LifeMilestone:
        """
        Add a life milestone to a user's profile.

        Parameters
        ----------
        user_id : str
            Target user.
        title : str
            Short milestone title (e.g. "Got promoted to Senior Engineer").
        description : str
            Longer context.
        category : MilestoneCategory
            Category tag.
        date_achieved : str
            ISO date string (``YYYY-MM-DD``).
        recurring_annually : bool
            If True, Buddy will remind the user every year.
        tags : list[str] | None
            Optional keyword tags.

        Returns
        -------
        LifeMilestone
        """
        profile = self.get_profile(user_id)
        self._milestone_counter += 1
        milestone = LifeMilestone(
            milestone_id=f"ms_{self._milestone_counter:05d}",
            user_id=user_id,
            title=title,
            description=description,
            category=category,
            date_achieved=date_achieved,
            recurring_annually=recurring_annually,
            tags=tags or [],
        )
        profile.milestones.append(milestone)
        return milestone

    def get_milestones(self, user_id: str) -> list[dict]:
        """Return all milestones for *user_id*."""
        profile = self.get_profile(user_id)
        return [m.to_dict() for m in profile.milestones]

    def celebrate_milestone(self, user_id: str, milestone_id: str) -> str:
        """Mark a milestone as celebrated and return a congratulatory message."""
        profile = self.get_profile(user_id)
        for ms in profile.milestones:
            if ms.milestone_id == milestone_id:
                ms.celebrated = True
                return (
                    f"🎉 Congratulations on \"{ms.title}\", {profile.display_name}! "
                    "This is a moment worth celebrating!"
                )
        raise MemorySystemError(f"Milestone '{milestone_id}' not found for user '{user_id}'.")

    # ------------------------------------------------------------------
    # Important dates
    # ------------------------------------------------------------------

    def add_important_date(
        self,
        user_id: str,
        label: str,
        month: int,
        day: int,
        year_started: Optional[int] = None,
        reminder_days_before: int = 3,
        notes: str = "",
    ) -> ImportantDate:
        """
        Add an important recurring date (anniversary, birthday, etc.).

        Parameters
        ----------
        user_id : str
            Target user.
        label : str
            Name of the occasion.
        month : int
            Month (1–12).
        day : int
            Day (1–31).
        year_started : int | None
            Year the occasion began (used to calculate years elapsed).
        reminder_days_before : int
            How many days in advance to send a reminder.
        notes : str
            Personal notes attached to the date.

        Returns
        -------
        ImportantDate
        """
        if not 1 <= month <= 12:
            raise MemorySystemError("Month must be between 1 and 12.")
        if not 1 <= day <= 31:
            raise MemorySystemError("Day must be between 1 and 31.")

        profile = self.get_profile(user_id)
        self._date_counter += 1
        date_obj = ImportantDate(
            date_id=f"dt_{self._date_counter:05d}",
            user_id=user_id,
            label=label,
            month=month,
            day=day,
            year_started=year_started,
            reminder_days_before=reminder_days_before,
            notes=notes,
        )
        profile.important_dates.append(date_obj)
        return date_obj

    def get_important_dates(self, user_id: str) -> list[dict]:
        """Return all important dates for *user_id*."""
        profile = self.get_profile(user_id)
        return [d.to_dict() for d in profile.important_dates]

    # ------------------------------------------------------------------
    # Episodic memory
    # ------------------------------------------------------------------

    def record_episode(
        self,
        user_id: str,
        title: str,
        summary: str,
        emotion_at_time: str = "neutral",
        tags: Optional[list[str]] = None,
    ) -> EpisodicMemory:
        """
        Record a new chapter in the user's life story.

        Parameters
        ----------
        user_id : str
            Target user.
        title : str
            Short episode title.
        summary : str
            What happened.
        emotion_at_time : str
            The dominant emotion during this episode.
        tags : list[str] | None
            Optional keyword tags.

        Returns
        -------
        EpisodicMemory
        """
        profile = self.get_profile(user_id)
        self._episode_counter += 1
        episode = EpisodicMemory(
            episode_id=f"ep_{self._episode_counter:05d}",
            user_id=user_id,
            title=title,
            summary=summary,
            emotion_at_time=emotion_at_time,
            tags=tags or [],
        )
        profile.episodes.append(episode)
        return episode

    def get_episodes(self, user_id: str) -> list[dict]:
        """Return all episodic memories for *user_id*."""
        profile = self.get_profile(user_id)
        return [e.to_dict() for e in profile.episodes]

    def recall_context(self, user_id: str) -> str:
        """
        Generate a personalised context summary for Buddy to use in conversations.

        Returns
        -------
        str
            A natural-language summary of who this user is.
        """
        profile = self.get_profile(user_id)
        depth = profile.relationship_depth.value
        interests = ", ".join(profile.interests[:5]) if profile.interests else "not yet specified"
        goals = ", ".join(profile.goals[:3]) if profile.goals else "not yet shared"
        jokes = len(profile.inside_jokes)
        milestones = len(profile.milestones)

        return (
            f"I know {profile.display_name} ({depth} relationship, "
            f"{profile.interaction_count} interactions). "
            f"Interests: {interests}. Goals: {goals}. "
            f"We share {jokes} inside joke(s). "
            f"They've hit {milestones} life milestone(s) together with me."
        )

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        """Return memory system status as a dict."""
        return {
            "total_profiles": len(self._profiles),
            "max_profiles": self.max_profiles,
            "total_milestones": self._milestone_counter,
            "total_important_dates": self._date_counter,
            "total_episodes": self._episode_counter,
        }
