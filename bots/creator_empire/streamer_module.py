"""
Streamer Module for CreatorEmpire.

Handles launching streaming accounts on Twitch and YouTube, AI-generated
overlay templates, and channel setup automation for the DreamCo platform.
"""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

from __future__ import annotations
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))

from dataclasses import dataclass, field
from typing import Optional
from tiers import Tier


class StreamerModuleError(Exception):
    """Raised when a streamer operation fails or is not permitted on the tier."""


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class OverlayTemplate:
    """AI-generated stream overlay configuration."""
    name: str
    theme: str          # e.g. "gaming", "music", "sports", "talk_show"
    primary_color: str
    secondary_color: str
    font: str
    alert_animation: str  # e.g. "fade", "slide", "bounce"
    webcam_border: str   # e.g. "rounded", "hexagon", "neon_glow"
    chat_box_style: str  # e.g. "minimal", "neon", "retro"
    tier_required: str   # "free" | "pro" | "enterprise"

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "theme": self.theme,
            "primary_color": self.primary_color,
            "secondary_color": self.secondary_color,
            "font": self.font,
            "alert_animation": self.alert_animation,
            "webcam_border": self.webcam_border,
            "chat_box_style": self.chat_box_style,
            "tier_required": self.tier_required,
        }


@dataclass
class StreamerAccount:
    """Represents a streamer's platform account setup."""
    talent_id: str
    platform: str          # "twitch" | "youtube"
    channel_name: str
    channel_url: str
    overlay: Optional[OverlayTemplate] = None
    setup_complete: bool = False
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "talent_id": self.talent_id,
            "platform": self.platform,
            "channel_name": self.channel_name,
            "channel_url": self.channel_url,
            "overlay": self.overlay.to_dict() if self.overlay else None,
            "setup_complete": self.setup_complete,
        }


# ---------------------------------------------------------------------------
# Built-in overlay library
# ---------------------------------------------------------------------------

OVERLAY_LIBRARY: list[OverlayTemplate] = [
    OverlayTemplate(
        name="Neon Gamer",
        theme="gaming",
        primary_color="#00FF88",
        secondary_color="#0D0D0D",
        font="Orbitron",
        alert_animation="bounce",
        webcam_border="neon_glow",
        chat_box_style="neon",
        tier_required="free",
    ),
    OverlayTemplate(
        name="Clean Minimal",
        theme="talk_show",
        primary_color="#FFFFFF",
        secondary_color="#222222",
        font="Inter",
        alert_animation="fade",
        webcam_border="rounded",
        chat_box_style="minimal",
        tier_required="free",
    ),
    OverlayTemplate(
        name="Hip-Hop Stage",
        theme="music",
        primary_color="#FFD700",
        secondary_color="#1A1A1A",
        font="Bebas Neue",
        alert_animation="slide",
        webcam_border="hexagon",
        chat_box_style="retro",
        tier_required="pro",
    ),
    OverlayTemplate(
        name="Sports Arena",
        theme="sports",
        primary_color="#C0392B",
        secondary_color="#ECF0F1",
        font="Oswald",
        alert_animation="slide",
        webcam_border="rounded",
        chat_box_style="minimal",
        tier_required="pro",
    ),
    OverlayTemplate(
        name="Elite Brand",
        theme="gaming",
        primary_color="#6441A5",
        secondary_color="#F0F0F0",
        font="Rajdhani",
        alert_animation="bounce",
        webcam_border="hexagon",
        chat_box_style="neon",
        tier_required="enterprise",
    ),
]

_TIER_ORDER = {Tier.FREE.value: 0, Tier.PRO.value: 1, Tier.ENTERPRISE.value: 2}

SUPPORTED_PLATFORMS = ("twitch", "youtube")


class StreamerModule:
    """
    Launches and manages streamer accounts on Twitch/YouTube, assigns
    AI-generated overlays, and tracks channel setup.

    Parameters
    ----------
    tier : Tier
        Controls access to advanced overlay templates and automation features.
    """

    def __init__(self, tier: Tier = Tier.FREE) -> None:
        self.tier = tier
        self._accounts: dict[str, list[StreamerAccount]] = {}  # talent_id -> accounts

    # ------------------------------------------------------------------
    # Account launch
    # ------------------------------------------------------------------

    def launch_account(
        self,
        talent_id: str,
        platform: str,
        channel_name: str,
    ) -> StreamerAccount:
        """
        Simulate launching a streaming account for a talent on a platform.

        Parameters
        ----------
        talent_id : str
            The talent's unique ID.
        platform : str
            "twitch" or "youtube".
        channel_name : str
            Desired channel name.

        Returns
        -------
        StreamerAccount
        """
        platform = platform.lower()
        if platform not in SUPPORTED_PLATFORMS:
            raise StreamerModuleError(
                f"Platform '{platform}' is not supported. "
                f"Choose from: {', '.join(SUPPORTED_PLATFORMS)}."
            )

        channel_url = self._build_channel_url(platform, channel_name)
        account = StreamerAccount(
            talent_id=talent_id,
            platform=platform,
            channel_name=channel_name,
            channel_url=channel_url,
            setup_complete=True,
        )
        self._accounts.setdefault(talent_id, []).append(account)
        return account

    # ------------------------------------------------------------------
    # Overlay management
    # ------------------------------------------------------------------

    def list_available_overlays(self) -> list[dict]:
        """Return overlays accessible on the current tier."""
        tier_level = _TIER_ORDER[self.tier.value]
        return [
            o.to_dict()
            for o in OVERLAY_LIBRARY
            if _TIER_ORDER[o.tier_required] <= tier_level
        ]

    def assign_overlay(self, talent_id: str, platform: str, overlay_name: str) -> StreamerAccount:
        """
        Assign a named overlay template to the streamer's account.

        Raises
        ------
        StreamerModuleError
            If the overlay is not found or not available on the current tier.
        """
        account = self._get_account(talent_id, platform)
        overlay = self._find_overlay(overlay_name)
        if _TIER_ORDER[overlay.tier_required] > _TIER_ORDER[self.tier.value]:
            raise StreamerModuleError(
                f"Overlay '{overlay_name}' requires the "
                f"{overlay.tier_required.title()} tier."
            )
        account.overlay = overlay
        return account

    def generate_ai_overlay(self, talent_id: str, platform: str, theme: str) -> OverlayTemplate:
        """
        Generate a custom AI overlay for a streamer (PRO/ENTERPRISE only).

        On FREE tier this raises StreamerModuleError.
        """
        if self.tier == Tier.FREE:
            raise StreamerModuleError(
                "AI overlay generation requires the Pro tier or higher."
            )
        account = self._get_account(talent_id, platform)

        # Simulate AI generation by customizing a base template
        base = next(
            (o for o in OVERLAY_LIBRARY if o.theme == theme.lower()),
            OVERLAY_LIBRARY[0],
        )
        ai_overlay = OverlayTemplate(
            name=f"[AI Generated] {base.name} for {talent_id}",
            theme=base.theme,
            primary_color=base.primary_color,
            secondary_color=base.secondary_color,
            font=base.font,
            alert_animation=base.alert_animation,
            webcam_border=base.webcam_border,
            chat_box_style=base.chat_box_style,
            tier_required=self.tier.value,
        )
        account.overlay = ai_overlay
        return ai_overlay

    # ------------------------------------------------------------------
    # Query helpers
    # ------------------------------------------------------------------

    def get_accounts(self, talent_id: str) -> list[dict]:
        """Return all accounts for a talent."""
        return [a.to_dict() for a in self._accounts.get(talent_id, [])]

    def summary(self) -> dict:
        """Return a summary of the streamer module state."""
        total_accounts = sum(len(v) for v in self._accounts.values())
        return {
            "tier": self.tier.value,
            "talents_with_accounts": len(self._accounts),
            "total_accounts": total_accounts,
            "available_overlay_count": len(self.list_available_overlays()),
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_channel_url(self, platform: str, channel_name: str) -> str:
        base_urls = {
            "twitch": "https://twitch.tv/",
            "youtube": "https://youtube.com/@",
        }
        return base_urls[platform] + channel_name.replace(" ", "_")

    def _get_account(self, talent_id: str, platform: str) -> StreamerAccount:
        platform = platform.lower()
        accounts = self._accounts.get(talent_id, [])
        for a in accounts:
            if a.platform == platform:
                return a
        raise StreamerModuleError(
            f"No {platform} account found for talent '{talent_id}'. "
            "Launch an account first."
        )

    def _find_overlay(self, name: str) -> OverlayTemplate:
        for o in OVERLAY_LIBRARY:
            if o.name.lower() == name.lower():
                return o
        raise StreamerModuleError(f"Overlay '{name}' not found in the library.")
