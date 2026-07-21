"""
Talent Onboarding Engine for CreatorEmpire.

Handles personal brand kits, media asset collection, and talent profile
management for the DreamCo CreatorEmpire platform.
"""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

from __future__ import annotations
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))

from dataclasses import dataclass, field
from typing import Optional
from tiers import Tier


class OnboardingError(Exception):
    """Raised when an onboarding operation fails or exceeds tier limits."""


@dataclass
class MediaAsset:
    """Represents a single media asset attached to a talent profile."""
    asset_type: str          # e.g. "headshot", "demo_reel", "logo", "banner"
    url: str
    description: str = ""


@dataclass
class BrandKit:
    """Personal brand kit for a talent."""
    primary_color: str = "#000000"
    secondary_color: str = "#FFFFFF"
    font: str = "Montserrat"
    tagline: str = ""
    logo_url: str = ""
    banner_url: str = ""
    bio: str = ""


@dataclass
class TalentProfile:
    """Full talent profile including brand kit and media assets."""
    talent_id: str
    name: str
    category: str          # e.g. "streamer", "rapper", "athlete", "general"
    email: str
    brand_kit: BrandKit = field(default_factory=BrandKit)
    media_assets: list[MediaAsset] = field(default_factory=list)
    social_handles: dict[str, str] = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)

    def add_media_asset(self, asset: MediaAsset) -> None:
        self.media_assets.append(asset)

    def update_brand_kit(self, **kwargs) -> None:
        for key, value in kwargs.items():
            if hasattr(self.brand_kit, key):
                setattr(self.brand_kit, key, value)

    def to_dict(self) -> dict:
        return {
            "talent_id": self.talent_id,
            "name": self.name,
            "category": self.category,
            "email": self.email,
            "brand_kit": {
                "primary_color": self.brand_kit.primary_color,
                "secondary_color": self.brand_kit.secondary_color,
                "font": self.brand_kit.font,
                "tagline": self.brand_kit.tagline,
                "logo_url": self.brand_kit.logo_url,
                "banner_url": self.brand_kit.banner_url,
                "bio": self.brand_kit.bio,
            },
            "media_assets": [
                {"asset_type": a.asset_type, "url": a.url, "description": a.description}
                for a in self.media_assets
            ],
            "social_handles": self.social_handles,
        }


# Free tier allows up to 3 talent profiles; Pro/Enterprise = unlimited.
_TIER_PROFILE_LIMITS: dict[str, Optional[int]] = {
    Tier.FREE.value: 3,
    Tier.PRO.value: None,
    Tier.ENTERPRISE.value: None,
}

_AI_BRAND_KIT_TEMPLATES: dict[str, BrandKit] = {
    "streamer": BrandKit(
        primary_color="#6441A5",
        secondary_color="#FFFFFF",
        font="Rajdhani",
        tagline="Live, Stream, Conquer.",
        bio="Next-generation content creator pushing boundaries every stream.",
    ),
    "rapper": BrandKit(
        primary_color="#FFD700",
        secondary_color="#1A1A1A",
        font="Bebas Neue",
        tagline="From the underground to the top.",
        bio="Independent artist dropping heat and building legacy.",
    ),
    "athlete": BrandKit(
        primary_color="#C0392B",
        secondary_color="#F0F0F0",
        font="Oswald",
        tagline="Train hard. Rise higher.",
        bio="Elite athlete chasing greatness on and off the field.",
    ),
    "general": BrandKit(
        primary_color="#2C3E50",
        secondary_color="#ECF0F1",
        font="Lato",
        tagline="Building something extraordinary.",
        bio="Creator, entrepreneur, visionary.",
    ),
}


class TalentOnboardingEngine:
    """
    Manages talent onboarding, brand kit generation, and media asset tracking.

    Parameters
    ----------
    tier : Tier
        Subscription tier controlling how many profiles can be created.
    """

    def __init__(self, tier: Tier = Tier.FREE) -> None:
        self.tier = tier
        self._profiles: dict[str, TalentProfile] = {}

    # ------------------------------------------------------------------
    # Profile management
    # ------------------------------------------------------------------

    def onboard_talent(
        self,
        talent_id: str,
        name: str,
        category: str,
        email: str,
        social_handles: Optional[dict[str, str]] = None,
    ) -> TalentProfile:
        """
        Create and register a new talent profile.

        Raises
        ------
        OnboardingError
            If the tier limit for talent profiles is exceeded or the
            talent_id already exists.
        """
        limit = _TIER_PROFILE_LIMITS[self.tier.value]
        if limit is not None and len(self._profiles) >= limit:
            raise OnboardingError(
                f"Talent profile limit of {limit} reached on the "
                f"{self.tier.value.title()} tier. Upgrade to add more talent."
            )
        if talent_id in self._profiles:
            raise OnboardingError(f"Talent ID '{talent_id}' already exists.")

        profile = TalentProfile(
            talent_id=talent_id,
            name=name,
            category=category.lower(),
            email=email,
            social_handles=social_handles or {},
        )
        self._profiles[talent_id] = profile
        return profile

    def get_profile(self, talent_id: str) -> TalentProfile:
        """Return the talent profile for the given ID."""
        if talent_id not in self._profiles:
            raise OnboardingError(f"Talent ID '{talent_id}' not found.")
        return self._profiles[talent_id]

    def list_profiles(self) -> list[dict]:
        """Return a list of all talent profiles as dicts."""
        return [p.to_dict() for p in self._profiles.values()]

    def remove_profile(self, talent_id: str) -> None:
        """Remove a talent profile."""
        if talent_id not in self._profiles:
            raise OnboardingError(f"Talent ID '{talent_id}' not found.")
        del self._profiles[talent_id]

    # ------------------------------------------------------------------
    # Brand kit helpers
    # ------------------------------------------------------------------

    def generate_ai_brand_kit(self, talent_id: str) -> BrandKit:
        """
        Generate and apply an AI-suggested brand kit for the talent.

        On FREE tier this returns a template-based kit.
        On PRO/ENTERPRISE a richer AI-generated kit is produced (mocked here).
        """
        profile = self.get_profile(talent_id)
        template = _AI_BRAND_KIT_TEMPLATES.get(
            profile.category,
            _AI_BRAND_KIT_TEMPLATES["general"],
        )
        if self.tier in (Tier.PRO, Tier.ENTERPRISE):
            # Simulate a richer AI-generated kit
            template = BrandKit(
                primary_color=template.primary_color,
                secondary_color=template.secondary_color,
                font=template.font,
                tagline=f"[AI-Enhanced] {template.tagline}",
                bio=f"[AI-Enhanced for {profile.name}] {template.bio}",
            )
        profile.brand_kit = template
        return template

    def add_media_asset(self, talent_id: str, asset_type: str, url: str, description: str = "") -> MediaAsset:
        """Attach a media asset to a talent profile."""
        profile = self.get_profile(talent_id)
        asset = MediaAsset(asset_type=asset_type, url=url, description=description)
        profile.add_media_asset(asset)
        return asset

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    def summary(self) -> dict:
        """Return a summary of the onboarding engine state."""
        limit = _TIER_PROFILE_LIMITS[self.tier.value]
        return {
            "tier": self.tier.value,
            "profiles_created": len(self._profiles),
            "profile_limit": limit if limit is not None else "unlimited",
            "talent_ids": list(self._profiles.keys()),
        }
