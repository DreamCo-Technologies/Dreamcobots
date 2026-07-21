"""
Athlete Module for CreatorEmpire.

Handles highlight reel editing, recruitment profile management, and NIL
(Name, Image, Likeness) monetization guides for the DreamCo platform.
"""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

from __future__ import annotations
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))

from dataclasses import dataclass, field
from typing import Optional
from tiers import Tier


class AthleteModuleError(Exception):
    """Raised when an athlete operation fails or is not available on the tier."""


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

SPORTS = [
    "basketball", "football", "soccer", "baseball", "track_and_field",
    "swimming", "tennis", "volleyball", "wrestling", "esports",
]

NIL_DEAL_CATEGORIES = [
    "social_media_sponsorship", "autograph_signing", "appearance_fee",
    "merchandise_deal", "brand_ambassador", "content_creation",
    "camp_instruction", "endorsement",
]


@dataclass
class HighlightClip:
    """Represents a single highlight clip."""
    clip_id: str
    timestamp_start: float  # seconds
    timestamp_end: float    # seconds
    description: str = ""
    score: float = 0.0      # AI-assigned quality score (0–1)

    def duration(self) -> float:
        return max(0.0, self.timestamp_end - self.timestamp_start)

    def to_dict(self) -> dict:
        return {
            "clip_id": self.clip_id,
            "timestamp_start": self.timestamp_start,
            "timestamp_end": self.timestamp_end,
            "description": self.description,
            "score": self.score,
            "duration_seconds": self.duration(),
        }


@dataclass
class HighlightReel:
    """A compiled highlight reel for an athlete."""
    reel_id: str
    talent_id: str
    title: str
    clips: list[HighlightClip] = field(default_factory=list)
    export_url: str = ""
    status: str = "draft"  # "draft" | "compiled" | "exported"

    def total_duration(self) -> float:
        return sum(c.duration() for c in self.clips)

    def to_dict(self) -> dict:
        return {
            "reel_id": self.reel_id,
            "talent_id": self.talent_id,
            "title": self.title,
            "clips": [c.to_dict() for c in self.clips],
            "total_duration_seconds": self.total_duration(),
            "export_url": self.export_url,
            "status": self.status,
        }


@dataclass
class RecruitmentProfile:
    """Athletic recruitment profile sent to colleges/teams."""
    talent_id: str
    sport: str
    position: str
    graduation_year: int
    gpa: float
    stats: dict = field(default_factory=dict)
    awards: list[str] = field(default_factory=list)
    contact_email: str = ""
    highlight_reel_url: str = ""

    def to_dict(self) -> dict:
        return {
            "talent_id": self.talent_id,
            "sport": self.sport,
            "position": self.position,
            "graduation_year": self.graduation_year,
            "gpa": self.gpa,
            "stats": self.stats,
            "awards": self.awards,
            "contact_email": self.contact_email,
            "highlight_reel_url": self.highlight_reel_url,
        }


@dataclass
class NILDeal:
    """Represents an NIL monetization opportunity."""
    deal_id: str
    talent_id: str
    category: str
    brand: str
    estimated_value_usd: float
    description: str = ""
    status: str = "prospect"  # "prospect" | "negotiating" | "signed" | "completed"

    def to_dict(self) -> dict:
        return {
            "deal_id": self.deal_id,
            "talent_id": self.talent_id,
            "category": self.category,
            "brand": self.brand,
            "estimated_value_usd": self.estimated_value_usd,
            "description": self.description,
            "status": self.status,
        }


# ---------------------------------------------------------------------------
# NIL monetization tips (per sport)
# ---------------------------------------------------------------------------

_NIL_TIPS: dict[str, list[str]] = {
    "basketball": [
        "Build a personal brand on Instagram and TikTok showcasing your skills.",
        "Partner with local sports stores for in-store appearances.",
        "Create training camp programs monetized through your NIL.",
        "Engage with brands that align with basketball culture (sneakers, sports drinks).",
    ],
    "football": [
        "Leverage local community endorsements in your team's market.",
        "Partner with sports equipment brands for product reviews.",
        "Host youth football clinics and monetize through registration fees.",
        "Build a YouTube channel for game breakdowns and analysis.",
    ],
    "soccer": [
        "Collaborate with sports nutrition brands for social media posts.",
        "Participate in local sports community events for appearance fees.",
        "Stream skill training sessions on Twitch/YouTube.",
        "Partner with apparel brands for kit sponsorships.",
    ],
    "default": [
        "Build your social media presence across Instagram, TikTok, and YouTube.",
        "Reach out to local businesses for endorsement deals.",
        "Create educational content about your sport for content creation deals.",
        "Register on NIL marketplace platforms like Opendorse or INFLCR.",
        "Document your journey — brands love authentic athlete stories.",
    ],
}


class AthleteModule:
    """
    Manages athlete highlight reels, recruitment profiles, and NIL deals.

    Parameters
    ----------
    tier : Tier
        Controls access to advanced clip detection and NIL monetization features.
    """

    def __init__(self, tier: Tier = Tier.FREE) -> None:
        self.tier = tier
        self._reels: dict[str, HighlightReel] = {}
        self._recruitment_profiles: dict[str, RecruitmentProfile] = {}
        self._nil_deals: dict[str, NILDeal] = {}

    # ------------------------------------------------------------------
    # Highlight reel management
    # ------------------------------------------------------------------

    def create_highlight_reel(self, reel_id: str, talent_id: str, title: str) -> HighlightReel:
        """Create a new empty highlight reel."""
        if reel_id in self._reels:
            raise AthleteModuleError(f"Reel ID '{reel_id}' already exists.")
        reel = HighlightReel(reel_id=reel_id, talent_id=talent_id, title=title)
        self._reels[reel_id] = reel
        return reel

    def add_clip(
        self,
        reel_id: str,
        clip_id: str,
        timestamp_start: float,
        timestamp_end: float,
        description: str = "",
    ) -> HighlightClip:
        """Add a clip to a highlight reel."""
        reel = self._get_reel(reel_id)
        if timestamp_end <= timestamp_start:
            raise AthleteModuleError("timestamp_end must be greater than timestamp_start.")
        clip = HighlightClip(
            clip_id=clip_id,
            timestamp_start=timestamp_start,
            timestamp_end=timestamp_end,
            description=description,
            score=0.5,  # default score
        )
        reel.clips.append(clip)
        return clip

    def ai_detect_highlights(self, reel_id: str) -> HighlightReel:
        """
        Use AI clip detection to auto-score and rank clips in a reel.

        Requires PRO or ENTERPRISE tier.
        """
        if self.tier == Tier.FREE:
            raise AthleteModuleError(
                "AI clip detection requires the Pro tier or higher."
            )
        reel = self._get_reel(reel_id)
        # Simulate AI scoring: score based on clip duration and order
        for i, clip in enumerate(reel.clips):
            duration_factor = min(clip.duration() / 10.0, 1.0)
            position_factor = 1.0 - (i / max(len(reel.clips), 1)) * 0.3
            clip.score = round(min(duration_factor * position_factor, 1.0), 3)
        # Sort clips by score descending
        reel.clips.sort(key=lambda c: c.score, reverse=True)
        reel.status = "compiled"
        return reel

    def export_reel(self, reel_id: str) -> dict:
        """Mark a reel as exported and return its export info."""
        reel = self._get_reel(reel_id)
        reel.export_url = f"https://creatorempire.io/reels/{reel_id}/export.mp4"
        reel.status = "exported"
        return reel.to_dict()

    # ------------------------------------------------------------------
    # Recruitment profiles
    # ------------------------------------------------------------------

    def create_recruitment_profile(
        self,
        talent_id: str,
        sport: str,
        position: str,
        graduation_year: int,
        gpa: float,
        stats: Optional[dict] = None,
        awards: Optional[list[str]] = None,
        contact_email: str = "",
    ) -> RecruitmentProfile:
        """Create or update a recruitment profile for an athlete."""
        profile = RecruitmentProfile(
            talent_id=talent_id,
            sport=sport.lower(),
            position=position,
            graduation_year=graduation_year,
            gpa=gpa,
            stats=stats or {},
            awards=awards or [],
            contact_email=contact_email,
        )
        self._recruitment_profiles[talent_id] = profile
        return profile

    def attach_reel_to_recruitment(self, talent_id: str, reel_id: str) -> RecruitmentProfile:
        """Link a highlight reel URL to a recruitment profile."""
        if talent_id not in self._recruitment_profiles:
            raise AthleteModuleError(f"No recruitment profile for talent '{talent_id}'.")
        reel = self._get_reel(reel_id)
        profile = self._recruitment_profiles[talent_id]
        profile.highlight_reel_url = reel.export_url or f"https://creatorempire.io/reels/{reel_id}"
        return profile

    def get_recruitment_profile(self, talent_id: str) -> dict:
        if talent_id not in self._recruitment_profiles:
            raise AthleteModuleError(f"No recruitment profile for talent '{talent_id}'.")
        return self._recruitment_profiles[talent_id].to_dict()

    # ------------------------------------------------------------------
    # NIL monetization
    # ------------------------------------------------------------------

    def get_nil_tips(self, sport: str) -> list[str]:
        """Return NIL monetization tips for a sport."""
        return _NIL_TIPS.get(sport.lower(), _NIL_TIPS["default"])

    def create_nil_deal(
        self,
        deal_id: str,
        talent_id: str,
        category: str,
        brand: str,
        estimated_value_usd: float,
        description: str = "",
    ) -> NILDeal:
        """
        Register an NIL deal opportunity.

        Requires PRO or ENTERPRISE tier for full NIL deal tracking.
        """
        if self.tier == Tier.FREE:
            raise AthleteModuleError(
                "NIL deal tracking requires the Pro tier or higher."
            )
        if deal_id in self._nil_deals:
            raise AthleteModuleError(f"Deal ID '{deal_id}' already exists.")
        deal = NILDeal(
            deal_id=deal_id,
            talent_id=talent_id,
            category=category,
            brand=brand,
            estimated_value_usd=estimated_value_usd,
            description=description,
        )
        self._nil_deals[deal_id] = deal
        return deal

    def update_nil_deal_status(self, deal_id: str, status: str) -> NILDeal:
        """Update the status of an NIL deal."""
        if deal_id not in self._nil_deals:
            raise AthleteModuleError(f"Deal '{deal_id}' not found.")
        valid = {"prospect", "negotiating", "signed", "completed"}
        if status not in valid:
            raise AthleteModuleError(f"Invalid status '{status}'. Choose from: {valid}.")
        self._nil_deals[deal_id].status = status
        return self._nil_deals[deal_id]

    def list_nil_deals(self, talent_id: Optional[str] = None) -> list[dict]:
        deals = self._nil_deals.values()
        if talent_id:
            deals = [d for d in deals if d.talent_id == talent_id]
        return [d.to_dict() for d in deals]

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    def summary(self) -> dict:
        return {
            "tier": self.tier.value,
            "highlight_reels": len(self._reels),
            "recruitment_profiles": len(self._recruitment_profiles),
            "nil_deals": len(self._nil_deals),
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_reel(self, reel_id: str) -> HighlightReel:
        if reel_id not in self._reels:
            raise AthleteModuleError(f"Highlight reel '{reel_id}' not found.")
        return self._reels[reel_id]
