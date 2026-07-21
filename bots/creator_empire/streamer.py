"""
Streaming Launch System module for the CreatorEmpire bot.

Handles stream configuration, go-live checklists, channel optimisation
tips, and monetisation milestones for streamer creators.
"""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from .tiers import (
    Tier,
    CREATOR_FEATURES_BY_TIER,
    FEATURE_STREAM_SETUP,
    FEATURE_MONETIZATION_BASIC,
    FEATURE_MONETIZATION_ADVANCED,
)


class StreamerError(Exception):
    """Raised when a streaming operation cannot be completed."""


@dataclass
class StreamConfig:
    """Configuration for a creator's streaming setup.

    Attributes
    ----------
    creator_name : str
        The creator's display name.
    platform : str
        Primary streaming platform (e.g. 'twitch', 'youtube', 'kick').
    niche : str
        Stream niche (e.g. 'gaming', 'irl', 'music', 'just_chatting').
    schedule : list[str]
        Scheduled stream days/times (e.g. ['Mon 18:00', 'Wed 18:00']).
    resolution : str
        Target output resolution (e.g. '1080p60').
    bitrate_kbps : int
        Target video bitrate in kbps.
    monetisation_enabled : bool
        Whether platform monetisation has been activated.
    overlay_configured : bool
        Whether stream overlays and alerts have been set up.
    metadata : dict
        Arbitrary extra settings.
    """

    creator_name: str
    platform: str
    niche: str = "general"
    schedule: list[str] = field(default_factory=list)
    resolution: str = "1080p60"
    bitrate_kbps: int = 6000
    monetisation_enabled: bool = False
    overlay_configured: bool = False
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "creator_name": self.creator_name,
            "platform": self.platform,
            "niche": self.niche,
            "schedule": self.schedule,
            "resolution": self.resolution,
            "bitrate_kbps": self.bitrate_kbps,
            "monetisation_enabled": self.monetisation_enabled,
            "overlay_configured": self.overlay_configured,
            "metadata": self.metadata,
        }


# Supported streaming platforms
STREAMING_PLATFORMS = ["twitch", "youtube", "kick", "facebook_gaming", "trovo"]

# Supported stream niches
STREAM_NICHES = [
    "gaming", "irl", "music", "just_chatting", "sports",
    "art", "cooking", "fitness", "education", "talk_show",
]

# Monetisation milestones per platform
MONETISATION_MILESTONES: dict[str, list[dict]] = {
    "twitch": [
        {"milestone": "Affiliate", "requirements": "50 followers, 3 avg viewers, 500 mins broadcast, 7 unique days"},
        {"milestone": "Partner", "requirements": "~75 avg viewers, consistent schedule, community guidelines"},
    ],
    "youtube": [
        {"milestone": "YPP (basic)", "requirements": "500 subscribers, 3 public uploads in 90 days, 3k watch hours or 3M Shorts views"},
        {"milestone": "YPP (full)", "requirements": "1k subscribers, 4k watch hours or 10M Shorts views in 12 months"},
    ],
    "kick": [
        {"milestone": "Kick Partner", "requirements": "75 avg viewers, consistent streaming schedule"},
    ],
    "facebook_gaming": [
        {"milestone": "Level Up", "requirements": "100 followers, 4 hours streamed, 2 different days"},
        {"milestone": "Partner Plus", "requirements": "Apply with established audience and consistent content"},
    ],
    "trovo": [
        {"milestone": "Partner", "requirements": "Apply with audience data via Trovo partner programme"},
    ],
}

# Go-live checklist
GO_LIVE_CHECKLIST = [
    "Test audio levels and microphone quality",
    "Check camera focus and lighting",
    "Verify stream key is correct for target platform",
    "Test stream at reduced bitrate before going live",
    "Confirm overlays and alerts are displaying correctly",
    "Prepare stream title and category/tags",
    "Check internet upload speed (minimum 5 Mbps recommended)",
    "Announce go-live on social media channels",
    "Enable stream delay if desired (reduces stream sniping)",
    "Have backup content ready in case of technical issues",
]


class StreamerEngine:
    """
    Manages streaming configuration and launch guidance for creators.

    Parameters
    ----------
    tier : Tier
        Subscription tier controlling available streaming features.
    """

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self._configs: dict[str, StreamConfig] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def setup_stream(
        self,
        creator_name: str,
        platform: str,
        niche: str = "general",
        schedule: Optional[list[str]] = None,
        resolution: str = "1080p60",
        bitrate_kbps: int = 6000,
    ) -> StreamConfig:
        """
        Create a streaming configuration for a creator.

        Parameters
        ----------
        creator_name : str
            Creator's display name.
        platform : str
            Target streaming platform.
        niche : str
            Stream niche/category.
        schedule : list[str] | None
            Weekly stream schedule.
        resolution : str
            Output resolution.
        bitrate_kbps : int
            Video bitrate in kbps.

        Returns
        -------
        StreamConfig
        """
        self._check_feature(FEATURE_STREAM_SETUP)

        platform = platform.lower().strip()
        if platform not in STREAMING_PLATFORMS:
            raise StreamerError(
                f"Unsupported platform '{platform}'. "
                f"Valid platforms: {', '.join(STREAMING_PLATFORMS)}."
            )
        niche = niche.lower().strip()

        config = StreamConfig(
            creator_name=creator_name,
            platform=platform,
            niche=niche,
            schedule=schedule or [],
            resolution=resolution,
            bitrate_kbps=bitrate_kbps,
        )
        self._configs[creator_name] = config
        return config

    def get_go_live_checklist(self) -> list[str]:
        """Return the standard go-live checklist."""
        self._check_feature(FEATURE_STREAM_SETUP)
        return list(GO_LIVE_CHECKLIST)

    def get_monetisation_milestones(self, platform: str) -> list[dict]:
        """Return monetisation milestones for a given platform."""
        self._check_feature(FEATURE_MONETIZATION_BASIC)
        platform = platform.lower().strip()
        if platform not in STREAMING_PLATFORMS:
            raise StreamerError(f"Unsupported platform '{platform}'.")
        return list(MONETISATION_MILESTONES.get(platform, []))

    def enable_monetisation(self, creator_name: str) -> StreamConfig:
        """Mark monetisation as enabled for a creator's stream config."""
        self._check_feature(FEATURE_MONETIZATION_BASIC)
        config = self._get_config(creator_name)
        config.monetisation_enabled = True
        return config

    def configure_overlay(self, creator_name: str, metadata: Optional[dict] = None) -> StreamConfig:
        """Mark stream overlay as configured, optionally storing overlay details."""
        self._check_feature(FEATURE_STREAM_SETUP)
        config = self._get_config(creator_name)
        config.overlay_configured = True
        if metadata:
            config.metadata.update(metadata)
        return config

    def get_stream_config(self, creator_name: str) -> StreamConfig:
        """Return the stream config for *creator_name*."""
        return self._get_config(creator_name)

    def list_configs(self) -> list[dict]:
        """Return all stream configs as a list of dicts."""
        return [c.to_dict() for c in self._configs.values()]

    def get_optimisation_tips(self, niche: str) -> list[str]:
        """Return niche-specific stream optimisation tips."""
        self._check_feature(FEATURE_STREAM_SETUP)
        niche = niche.lower().strip()
        tips_map: dict[str, list[str]] = {
            "gaming": [
                "Use a face-cam to build personal connection with viewers",
                "Keep overlay minimal so gameplay is always visible",
                "Set up channel point rewards to boost engagement",
                "Raid other small streamers after going offline",
            ],
            "irl": [
                "Invest in a good mobile rig and stable internet solution",
                "Interact heavily with chat to drive engagement",
                "Plan locations in advance and notify viewers",
                "Check local laws regarding public filming",
            ],
            "music": [
                "Use high-quality audio interface and condenser microphone",
                "Enable noise gate to eliminate background noise",
                "Schedule themed sessions (covers night, original music night)",
                "Promote VODs on SoundCloud / YouTube after the stream",
            ],
            "just_chatting": [
                "Prepare topics or talking points to avoid dead air",
                "Use polls and predictions to drive chat interaction",
                "Set clear community guidelines in your channel panels",
                "Collaborate with guests for interview-style streams",
            ],
            "fitness": [
                "Secure camera at a fixed angle showing full body movements",
                "Post workout plans in channel description before going live",
                "Offer viewer challenges to boost participation",
                "Link to your coaching programme or subscription in bio",
            ],
        }
        return tips_map.get(niche, [
            "Maintain a consistent streaming schedule",
            "Engage actively with chat throughout every stream",
            "Promote upcoming streams on all social channels",
            "Analyse VOD analytics to improve future content",
        ])

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_config(self, creator_name: str) -> StreamConfig:
        if creator_name not in self._configs:
            raise StreamerError(f"No stream config found for '{creator_name}'.")
        return self._configs[creator_name]

    def _check_feature(self, feature: str) -> None:
        available = CREATOR_FEATURES_BY_TIER[self.tier.value]
        if feature not in available:
            raise StreamerError(
                f"Feature '{feature}' is not available on the "
                f"{self.tier.value.capitalize()} tier."
            )
