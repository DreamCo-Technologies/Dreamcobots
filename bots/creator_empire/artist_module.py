"""
Rapper / Artist Module for CreatorEmpire.

Handles music distribution, AI beat matching, royalty split calculations,
and release management for the DreamCo platform.
"""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

from __future__ import annotations
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))

from dataclasses import dataclass, field
from typing import Optional
from tiers import Tier


class ArtistModuleError(Exception):
    """Raised when an artist operation fails or is not available on the tier."""


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

DISTRIBUTION_PLATFORMS = [
    "Spotify", "Apple Music", "Tidal", "Amazon Music",
    "YouTube Music", "SoundCloud", "Bandcamp", "Deezer",
]

BEAT_GENRES = [
    "trap", "drill", "boom_bap", "rnb", "lo_fi",
    "reggaeton", "afrobeats", "pop_rap",
]


@dataclass
class RoyaltySplit:
    """Defines how royalties are split between contributors."""
    artist_pct: float
    producer_pct: float
    label_pct: float
    distributor_pct: float
    manager_pct: float = 0.0

    def validate(self) -> None:
        total = (
            self.artist_pct + self.producer_pct + self.label_pct
            + self.distributor_pct + self.manager_pct
        )
        if abs(total - 100.0) > 0.01:
            raise ArtistModuleError(
                f"Royalty splits must sum to 100%. Current total: {total:.2f}%"
            )

    def to_dict(self) -> dict:
        return {
            "artist_pct": self.artist_pct,
            "producer_pct": self.producer_pct,
            "label_pct": self.label_pct,
            "distributor_pct": self.distributor_pct,
            "manager_pct": self.manager_pct,
        }


@dataclass
class BeatMatch:
    """Result of an AI beat matching operation."""
    track_title: str
    genre: str
    bpm: int
    key: str
    suggested_beats: list[str] = field(default_factory=list)
    confidence_score: float = 0.0

    def to_dict(self) -> dict:
        return {
            "track_title": self.track_title,
            "genre": self.genre,
            "bpm": self.bpm,
            "key": self.key,
            "suggested_beats": self.suggested_beats,
            "confidence_score": self.confidence_score,
        }


@dataclass
class MusicRelease:
    """Represents a music release submitted for distribution."""
    release_id: str
    talent_id: str
    title: str
    genre: str
    platforms: list[str] = field(default_factory=list)
    royalty_split: Optional[RoyaltySplit] = None
    beat_match: Optional[BeatMatch] = None
    status: str = "pending"  # "pending" | "distributed" | "live"

    def to_dict(self) -> dict:
        return {
            "release_id": self.release_id,
            "talent_id": self.talent_id,
            "title": self.title,
            "genre": self.genre,
            "platforms": self.platforms,
            "royalty_split": self.royalty_split.to_dict() if self.royalty_split else None,
            "beat_match": self.beat_match.to_dict() if self.beat_match else None,
            "status": self.status,
        }


# ---------------------------------------------------------------------------
# Simulated beat catalog
# ---------------------------------------------------------------------------

_BEAT_CATALOG: dict[str, list[str]] = {
    "trap": ["Dark Vibes 808", "Midnight Trap Vol.1", "Lil Prod Banger"],
    "drill": ["UK Drill Strings", "Chicago Grit Beat", "NYC Freestyle Drill"],
    "boom_bap": ["Golden Era Drums", "90s NYC Boom", "East Coast Classic"],
    "rnb": ["Smooth RnB Chords", "Late Night Vibes", "Neo-Soul Groove"],
    "lo_fi": ["Chill Study Beat", "Late Night Lo-Fi", "Cozy Rain Loops"],
    "reggaeton": ["Dembow Fuego", "Latin Trap 2024", "Perreo Instrumental"],
    "afrobeats": ["Afro Drill Fusion", "Lagos Nights", "Naija Vibe"],
    "pop_rap": ["Chart-Ready Hook", "Summer Anthem Beat", "Radio Pop Trap"],
}

_MUSIC_KEYS = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


class ArtistModule:
    """
    Manages music releases, AI beat matching, and royalty split calculations.

    Parameters
    ----------
    tier : Tier
        Controls access to advanced beat matching and distribution features.
    """

    def __init__(self, tier: Tier = Tier.FREE) -> None:
        self.tier = tier
        self._releases: dict[str, MusicRelease] = {}

    # ------------------------------------------------------------------
    # Release management
    # ------------------------------------------------------------------

    def create_release(
        self,
        release_id: str,
        talent_id: str,
        title: str,
        genre: str,
        platforms: Optional[list[str]] = None,
    ) -> MusicRelease:
        """
        Register a new music release for distribution.

        On FREE tier, distribution is limited to 3 platforms.
        On PRO/ENTERPRISE, all platforms are available.
        """
        if release_id in self._releases:
            raise ArtistModuleError(f"Release ID '{release_id}' already exists.")

        if platforms is None:
            platforms = DISTRIBUTION_PLATFORMS[:3] if self.tier == Tier.FREE else DISTRIBUTION_PLATFORMS

        if self.tier == Tier.FREE and len(platforms) > 3:
            raise ArtistModuleError(
                "Free tier supports distribution to a maximum of 3 platforms. "
                "Upgrade to Pro for full distribution."
            )

        genre_lower = genre.lower()
        release = MusicRelease(
            release_id=release_id,
            talent_id=talent_id,
            title=title,
            genre=genre_lower,
            platforms=platforms,
        )
        self._releases[release_id] = release
        return release

    def distribute_release(self, release_id: str) -> MusicRelease:
        """Mark a release as distributed."""
        release = self._get_release(release_id)
        release.status = "distributed"
        return release

    def get_release(self, release_id: str) -> dict:
        return self._get_release(release_id).to_dict()

    def list_releases(self, talent_id: Optional[str] = None) -> list[dict]:
        releases = self._releases.values()
        if talent_id:
            releases = [r for r in releases if r.talent_id == talent_id]
        return [r.to_dict() for r in releases]

    # ------------------------------------------------------------------
    # AI Beat Matching (PRO/ENTERPRISE)
    # ------------------------------------------------------------------

    def ai_beat_match(
        self,
        release_id: str,
        bpm: int,
        key: str,
    ) -> BeatMatch:
        """
        Run AI beat matching for a release to find suitable production beats.

        Requires PRO or ENTERPRISE tier.
        """
        if self.tier == Tier.FREE:
            raise ArtistModuleError(
                "AI beat matching requires the Pro tier or higher."
            )
        release = self._get_release(release_id)
        genre = release.genre if release.genre in _BEAT_CATALOG else "trap"
        suggested = _BEAT_CATALOG.get(genre, [])
        bm = BeatMatch(
            track_title=release.title,
            genre=genre,
            bpm=bpm,
            key=key if key in _MUSIC_KEYS else "C",
            suggested_beats=suggested,
            confidence_score=0.87 if self.tier == Tier.ENTERPRISE else 0.74,
        )
        release.beat_match = bm
        return bm

    # ------------------------------------------------------------------
    # Royalty Splits
    # ------------------------------------------------------------------

    def set_royalty_split(
        self,
        release_id: str,
        artist_pct: float,
        producer_pct: float,
        label_pct: float,
        distributor_pct: float,
        manager_pct: float = 0.0,
    ) -> RoyaltySplit:
        """
        Set the royalty split for a release and validate it sums to 100%.

        Requires PRO or ENTERPRISE tier.
        """
        if self.tier == Tier.FREE:
            raise ArtistModuleError(
                "Custom royalty splits require the Pro tier or higher."
            )
        release = self._get_release(release_id)
        split = RoyaltySplit(
            artist_pct=artist_pct,
            producer_pct=producer_pct,
            label_pct=label_pct,
            distributor_pct=distributor_pct,
            manager_pct=manager_pct,
        )
        split.validate()
        release.royalty_split = split
        return split

    def calculate_royalty_earnings(
        self, release_id: str, total_revenue: float
    ) -> dict:
        """
        Calculate per-party earnings given total revenue for a release.

        Requires PRO or ENTERPRISE tier.
        """
        if self.tier == Tier.FREE:
            raise ArtistModuleError(
                "Royalty earnings calculation requires the Pro tier or higher."
            )
        release = self._get_release(release_id)
        if release.royalty_split is None:
            raise ArtistModuleError(
                f"No royalty split configured for release '{release_id}'."
            )
        split = release.royalty_split
        return {
            "release_id": release_id,
            "total_revenue": total_revenue,
            "artist": round(total_revenue * split.artist_pct / 100, 2),
            "producer": round(total_revenue * split.producer_pct / 100, 2),
            "label": round(total_revenue * split.label_pct / 100, 2),
            "distributor": round(total_revenue * split.distributor_pct / 100, 2),
            "manager": round(total_revenue * split.manager_pct / 100, 2),
        }

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    def summary(self) -> dict:
        return {
            "tier": self.tier.value,
            "total_releases": len(self._releases),
            "distributed": sum(1 for r in self._releases.values() if r.status == "distributed"),
            "available_platforms": len(DISTRIBUTION_PLATFORMS) if self.tier != Tier.FREE else 3,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_release(self, release_id: str) -> MusicRelease:
        if release_id not in self._releases:
            raise ArtistModuleError(f"Release '{release_id}' not found.")
        return self._releases[release_id]
