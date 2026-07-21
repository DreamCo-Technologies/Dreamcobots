"""
Talent Identity & Onboarding module for the CreatorEmpire bot.

Guides creators through profile setup tailored to their specific role
(streamer, rapper, athlete, etc.) and generates a personalised action plan.
"""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from .tiers import CREATOR_ROLES, Tier, CREATOR_FEATURES_BY_TIER, FEATURE_ROLE_ONBOARDING


class OnboardingError(Exception):
    """Raised when an onboarding operation cannot be completed."""


@dataclass
class CreatorProfile:
    """Represents a creator's identity and onboarding state.

    Attributes
    ----------
    name : str
        Display name chosen by the creator.
    role : str
        Primary creator role (e.g. 'streamer', 'rapper').
    bio : str
        Short biography or tagline.
    goals : list[str]
        Creator's self-reported goals (e.g. 'grow audience', 'monetize content').
    platforms : list[str]
        Target distribution platforms (e.g. 'twitch', 'youtube', 'spotify').
    tier : Tier
        Subscription tier that controls available features.
    onboarding_complete : bool
        Whether the initial onboarding flow has been completed.
    metadata : dict
        Arbitrary role-specific extra data.
    """

    name: str
    role: str
    bio: str = ""
    goals: list[str] = field(default_factory=list)
    platforms: list[str] = field(default_factory=list)
    tier: Tier = Tier.FREE
    onboarding_complete: bool = False
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "role": self.role,
            "bio": self.bio,
            "goals": self.goals,
            "platforms": self.platforms,
            "tier": self.tier.value,
            "onboarding_complete": self.onboarding_complete,
            "metadata": self.metadata,
        }


class OnboardingEngine:
    """
    Manages creator onboarding: profile creation, role assignment, and
    generation of a tailored first-steps action plan.

    Parameters
    ----------
    tier : Tier
        The subscription tier controlling available onboarding features.
    """

    # Recommended starter platforms per role
    _ROLE_PLATFORMS: dict[str, list[str]] = {
        "streamer": ["twitch", "youtube", "kick"],
        "rapper": ["spotify", "apple_music", "soundcloud", "youtube"],
        "athlete": ["instagram", "tiktok", "youtube", "x"],
        "artist": ["instagram", "behance", "youtube", "patreon"],
        "content_creator": ["youtube", "tiktok", "instagram"],
        "podcaster": ["spotify", "apple_podcasts", "youtube"],
        "comedian": ["tiktok", "youtube", "instagram"],
        "fitness_coach": ["instagram", "youtube", "tiktok"],
        "gamer": ["twitch", "youtube", "discord"],
        "dancer": ["tiktok", "instagram", "youtube"],
    }

    # First-steps action plan per role
    _ROLE_ACTION_PLANS: dict[str, list[str]] = {
        "streamer": [
            "Choose your niche (gaming, IRL, music, etc.)",
            "Set up streaming software (OBS / Streamlabs)",
            "Design channel art and overlays",
            "Schedule consistent stream times",
            "Enable Twitch/YouTube monetisation once eligible",
        ],
        "rapper": [
            "Record and upload debut single or freestyle",
            "Build a SoundCloud / Spotify artist profile",
            "Create short-form content highlighting your bars",
            "Network with producers on BeatStars or Airbit",
            "Pitch to playlist curators for early exposure",
        ],
        "athlete": [
            "Document training highlights for social media",
            "Build a highlight reel for scouts and sponsors",
            "Partner with local or niche sports brands",
            "Create a public athlete profile on Hudl or similar",
            "Launch a fitness-tips content series",
        ],
        "artist": [
            "Post portfolio on Instagram and Behance",
            "Create a commission sheet and pricing guide",
            "Launch a Patreon for behind-the-scenes content",
            "Submit work to online galleries and competitions",
            "Collaborate with musicians or content creators",
        ],
        "content_creator": [
            "Define your content niche and target audience",
            "Set up YouTube channel with branding",
            "Film and publish first 3 videos",
            "Cross-post clips to TikTok and Instagram Reels",
            "Enable channel monetisation",
        ],
        "podcaster": [
            "Choose podcast topic and episode format",
            "Record a pilot episode",
            "Publish to Spotify for Podcasters and Apple Podcasts",
            "Design cover art and show description",
            "Promote episodes on social media",
        ],
        "comedian": [
            "Post a short stand-up or sketch clip",
            "Engage with comedy communities on Reddit and Discord",
            "Submit to open mic nights and comedy festivals",
            "Collaborate with other comedians for cross-promotion",
            "Explore brand deals or live show merchandise",
        ],
        "fitness_coach": [
            "Create a free workout plan as a lead magnet",
            "Film a daily workout series on TikTok/Instagram",
            "Launch an online coaching programme",
            "Build an email list for premium content",
            "Partner with supplement or apparel brands",
        ],
        "gamer": [
            "Set up a Discord server for your community",
            "Stream regularly on Twitch or YouTube Gaming",
            "Create tutorial or highlight clips for YouTube",
            "Participate in tournaments for visibility",
            "Seek sponsorships from gaming peripherals brands",
        ],
        "dancer": [
            "Film a signature routine for TikTok debut",
            "Post process videos (tutorials, rehearsals)",
            "Apply for brand deals with fashion/lifestyle brands",
            "Submit choreography to music video casting",
            "Launch online dance masterclasses",
        ],
    }

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self._profiles: dict[str, CreatorProfile] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def create_profile(
        self,
        name: str,
        role: str,
        bio: str = "",
        goals: Optional[list[str]] = None,
        platforms: Optional[list[str]] = None,
    ) -> CreatorProfile:
        """
        Create and register a new creator profile.

        Parameters
        ----------
        name : str
            Creator display name (must be unique within this engine instance).
        role : str
            One of the supported creator roles.
        bio : str
            Short biography.
        goals : list[str] | None
            Explicit goals; defaults to role-specific suggestions.
        platforms : list[str] | None
            Target platforms; defaults to role-specific suggestions.

        Returns
        -------
        CreatorProfile
        """
        self._check_feature(FEATURE_ROLE_ONBOARDING)

        role = role.lower().strip()
        if role not in CREATOR_ROLES:
            raise OnboardingError(
                f"Unsupported role '{role}'. "
                f"Valid roles: {', '.join(CREATOR_ROLES)}."
            )
        if name in self._profiles:
            raise OnboardingError(f"A profile for '{name}' already exists.")

        profile = CreatorProfile(
            name=name,
            role=role,
            bio=bio,
            goals=goals or self._default_goals(role),
            platforms=platforms or self._ROLE_PLATFORMS.get(role, []),
            tier=self.tier,
        )
        self._profiles[name] = profile
        return profile

    def complete_onboarding(self, name: str) -> dict:
        """
        Mark onboarding as complete and return the creator's action plan.

        Returns
        -------
        dict with keys: ``profile``, ``action_plan``.
        """
        profile = self._get_profile(name)
        profile.onboarding_complete = True
        return {
            "profile": profile.to_dict(),
            "action_plan": self.get_action_plan(profile.role),
        }

    def get_action_plan(self, role: str) -> list[str]:
        """Return the starter action plan for a given role."""
        role = role.lower().strip()
        if role not in CREATOR_ROLES:
            raise OnboardingError(f"Unsupported role '{role}'.")
        return list(self._ROLE_ACTION_PLANS.get(role, []))

    def get_profile(self, name: str) -> CreatorProfile:
        """Return the profile for *name*."""
        return self._get_profile(name)

    def list_profiles(self) -> list[dict]:
        """Return all registered profiles as a list of dicts."""
        return [p.to_dict() for p in self._profiles.values()]

    def update_profile(self, name: str, **kwargs) -> CreatorProfile:
        """Update fields on an existing profile."""
        profile = self._get_profile(name)
        allowed = {"bio", "goals", "platforms", "metadata"}
        for key, value in kwargs.items():
            if key not in allowed:
                raise OnboardingError(f"Field '{key}' cannot be updated via this method.")
            setattr(profile, key, value)
        return profile

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_profile(self, name: str) -> CreatorProfile:
        if name not in self._profiles:
            raise OnboardingError(f"No profile found for '{name}'.")
        return self._profiles[name]

    def _check_feature(self, feature: str) -> None:
        available = CREATOR_FEATURES_BY_TIER[self.tier.value]
        if feature not in available:
            raise OnboardingError(
                f"Feature '{feature}' is not available on the "
                f"{self.tier.value.capitalize()} tier."
            )

    @staticmethod
    def _default_goals(role: str) -> list[str]:
        defaults = {
            "streamer": ["grow subscriber base", "reach affiliate/partner status",
                         "generate streaming revenue"],
            "rapper": ["release debut EP", "grow SoundCloud/Spotify following",
                       "land first paid performance"],
            "athlete": ["secure sponsorship deal", "build social media presence",
                        "document journey to pro"],
            "artist": ["build commission client base", "launch Patreon",
                       "exhibit in an online gallery"],
            "content_creator": ["reach 1k subscribers", "enable monetisation",
                                 "build brand partnerships"],
            "podcaster": ["publish 10 episodes", "reach 500 listeners per episode",
                          "land a sponsorship"],
            "comedian": ["perform at 5 open mics", "grow TikTok following",
                         "book first paid comedy show"],
            "fitness_coach": ["onboard 10 online clients", "launch digital product",
                               "build email list of 1k"],
            "gamer": ["reach Twitch Affiliate", "grow Discord server to 100 members",
                      "win a tournament"],
            "dancer": ["reach 10k TikTok followers", "launch online class",
                       "book first commercial gig"],
        }
        return defaults.get(role, ["build audience", "monetise content"])
