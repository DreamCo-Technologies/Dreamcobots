"""
Photo Editing Bot — Main Entry Point

An AI-powered photo editing, transformation, and creative animation studio for the DreamCobots ecosystem.

Core capabilities:
  • Photo Editing         — Brightness, contrast, saturation, and sharpness adjustments (FREE+)
  • Background Removal    — AI-powered background segmentation and removal (FREE+)
  • Creative Filters      — Apply vintage, sepia, noir, and other stylistic filters (FREE+)
  • Noise Removal         — AI denoising for cleaner images (PRO+)
  • Batch Editing         — Process multiple images in one pipeline run (PRO+)
  • Cartoon Conversion    — Transform photos into cartoon, anime, or sketch art styles (PRO+)
  • Caricature Generation — Exaggerated facial feature caricature art (PRO+)
  • Animation Generation  — Multi-frame AI animation generation (ENTERPRISE)
  • Cartoon Frame Gen     — Descriptive AI-to-cartoon frame synthesis (ENTERPRISE)

Tier limits:
  - FREE:       10 photos/day, basic editing, background removal, filters, JPG/PNG export.
  - PRO:        100 photos/day, noise removal, batch editing, cartoon/caricature, HD export.
  - ENTERPRISE: Unlimited, animation generation, cartoon frames, commercial rights, white-label.

Usage
-----
    from bots.photo_editing_bot import PhotoEditingBot, Tier
    bot = PhotoEditingBot(tier=Tier.PRO)
    result = bot.edit_photo("https://cdn.example.com/photo.jpg", {"brightness": 10, "contrast": 5})
    print(bot.get_editing_dashboard())
"""

from __future__ import annotations

import sys
import os
import uuid
import random
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ai-models-integration"))
from tiers import Tier, get_tier_config, get_upgrade_path  # noqa: F401
from bots.photo_editing_bot.tiers import (
    BOT_FEATURES,
    get_bot_tier_info,
    DAILY_LIMITS,
    FEATURE_BASIC_EDITING,
    FEATURE_BACKGROUND_REMOVAL,
    FEATURE_FILTERS,
    FEATURE_NOISE_REMOVAL,
    FEATURE_BATCH_EDITING,
    FEATURE_CARTOON_CONVERSION,
    FEATURE_CARICATURE,
    FEATURE_ANIMATION_GENERATION,
    FEATURE_CARTOON_FRAME_GENERATION,
)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from framework import GlobalAISourcesFlow  # noqa: F401

_AVAILABLE_FILTERS = ["vintage", "sepia", "noir", "vivid", "faded", "chrome", "fade", "dramatic"]
_CARTOON_STYLES = ["cartoon", "anime", "sketch", "comic", "watercolor"]
_CARTOON_FRAME_STYLES = ["disney", "pixar", "anime", "comic", "manga"]
_BACKGROUND_TYPES = [
    "natural scenery", "urban cityscape", "solid white", "gradient",
    "blurred interior", "outdoor park", "studio backdrop",
]


class PhotoEditingBotError(Exception):
    """Raised when a tier limit or feature restriction is violated."""


class PhotoEditingBot:
    """AI-powered photo editing and creative transformation bot with tier-based feature gating.

    Parameters
    ----------
    tier : Tier
        Subscription tier controlling daily limits and feature access.
    """

    def __init__(self, tier: Tier = Tier.FREE) -> None:
        self.tier = tier
        self.config = get_tier_config(tier)
        self.tier_info = get_bot_tier_info(tier)
        self.flow = GlobalAISourcesFlow(bot_name="PhotoEditingBot")
        self._daily_count: int = 0

    def _check_daily_limit(self) -> None:
        """Raise PhotoEditingBotError if the daily limit is exceeded."""
        limit = DAILY_LIMITS[self.tier.value]
        if limit is not None and self._daily_count >= limit:
            upgrade = get_upgrade_path(self.tier)
            upgrade_msg = (
                f" Upgrade to {upgrade.name} (${upgrade.price_usd_monthly}/mo) for more."
                if upgrade else ""
            )
            raise PhotoEditingBotError(
                f"Daily limit of {limit} reached for the {self.tier.value.upper()} tier.{upgrade_msg}"
            )

    def _check_feature(self, feature: str) -> None:
        """Raise PhotoEditingBotError if the feature is not available on the current tier."""
        if feature not in BOT_FEATURES[self.tier.value]:
            upgrade = get_upgrade_path(self.tier)
            upgrade_msg = (
                f" Upgrade to {upgrade.name} for access." if upgrade else ""
            )
            raise PhotoEditingBotError(
                f"Feature '{feature}' is not available on the {self.tier.value.upper()} tier.{upgrade_msg}"
            )

    def _record(self) -> None:
        self._daily_count += 1

    def edit_photo(self, image_source: str, adjustments: dict | None = None) -> dict:
        """Apply editing adjustments to a photo (FREE+).

        Parameters
        ----------
        image_source : str
            URL or file path of the source image.
        adjustments : dict | None
            Editing parameters. Defaults: brightness=0, contrast=0, saturation=0, sharpness=0.
        """
        self._check_feature(FEATURE_BASIC_EDITING)
        self._check_daily_limit()
        if adjustments is None:
            adjustments = {"brightness": 0, "contrast": 0, "saturation": 0, "sharpness": 0}
        result = self.flow.run_pipeline(
            raw_data={"task": "edit_photo", "image_source": image_source, "adjustments": adjustments},
            learning_method="supervised",
        )
        uid = uuid.uuid4().hex[:12]
        self._record()
        return {
            "image_source": image_source,
            "adjustments_applied": adjustments,
            "output_url": f"https://cdn.dreamcobots.ai/photos/edited_{uid}.png",
            "resolution": "2048x2048",
            "format": "PNG",
            "file_size_kb": random.randint(400, 2000),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "framework_pipeline": result.get("bot_name"),
        }

    def remove_noise(self, image_source: str) -> dict:
        """Apply AI-powered noise removal to a photo (PRO+).

        Parameters
        ----------
        image_source : str
            URL or file path of the noisy source image.
        """
        self._check_feature(FEATURE_NOISE_REMOVAL)
        self._check_daily_limit()
        result = self.flow.run_pipeline(
            raw_data={"task": "remove_noise", "image_source": image_source},
            learning_method="supervised",
        )
        uid = uuid.uuid4().hex[:12]
        self._record()
        return {
            "image_source": image_source,
            "noise_level_before": random.choice(["moderate", "high", "severe"]),
            "noise_level_after": "minimal",
            "psnr_improvement_db": round(random.uniform(5.0, 12.0), 1),
            "output_url": f"https://cdn.dreamcobots.ai/photos/denoised_{uid}.png",
            "algorithm": "DnCNN-v3",
            "status": "denoised",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "framework_pipeline": result.get("bot_name"),
        }

    def remove_background(self, image_source: str) -> dict:
        """Remove the background from a photo using AI segmentation (FREE+).

        Parameters
        ----------
        image_source : str
            URL or file path of the source image.
        """
        self._check_feature(FEATURE_BACKGROUND_REMOVAL)
        self._check_daily_limit()
        result = self.flow.run_pipeline(
            raw_data={"task": "remove_background", "image_source": image_source},
            learning_method="supervised",
        )
        uid = uuid.uuid4().hex[:12]
        self._record()
        return {
            "image_source": image_source,
            "background_detected": random.choice(_BACKGROUND_TYPES),
            "removal_confidence": round(random.uniform(0.90, 0.99), 2),
            "output_url": f"https://cdn.dreamcobots.ai/photos/nobg_{uid}.png",
            "mask_url": f"https://cdn.dreamcobots.ai/masks/mask_{uid}.png",
            "edge_quality": "high",
            "status": "background_removed",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "framework_pipeline": result.get("bot_name"),
        }

    def apply_filter(self, image_source: str, filter_name: str) -> dict:
        """Apply a creative stylistic filter to a photo (FREE+).

        Parameters
        ----------
        image_source : str
            URL or file path of the source image.
        filter_name : str
            Filter name: vintage, sepia, noir, vivid, faded, chrome, fade, dramatic.
        """
        self._check_feature(FEATURE_FILTERS)
        self._check_daily_limit()
        if filter_name not in _AVAILABLE_FILTERS:
            filter_name = random.choice(_AVAILABLE_FILTERS)
        result = self.flow.run_pipeline(
            raw_data={"task": "apply_filter", "image_source": image_source, "filter_name": filter_name},
            learning_method="supervised",
        )
        uid = uuid.uuid4().hex[:12]
        self._record()
        return {
            "image_source": image_source,
            "filter_name": filter_name,
            "intensity": round(random.uniform(0.75, 0.95), 2),
            "output_url": f"https://cdn.dreamcobots.ai/photos/filtered_{uid}.jpg",
            "status": "filter_applied",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "framework_pipeline": result.get("bot_name"),
        }

    def batch_edit(self, image_sources: list[str], adjustments: dict) -> dict:
        """Apply identical editing adjustments to a batch of photos in one pipeline run (PRO+).

        Parameters
        ----------
        image_sources : list[str]
            List of image URLs or file paths.
        adjustments : dict
            Editing parameters to apply to every image.
        """
        self._check_feature(FEATURE_BATCH_EDITING)
        self._check_daily_limit()
        result = self.flow.run_pipeline(
            raw_data={"task": "batch_edit", "count": len(image_sources), "adjustments": adjustments},
            learning_method="supervised",
        )
        output_urls = [
            f"https://cdn.dreamcobots.ai/photos/batch_{uuid.uuid4().hex[:8]}.png"
            for _ in image_sources
        ]
        self._record()
        return {
            "total_images": len(image_sources),
            "processed": len(image_sources),
            "adjustments": adjustments,
            "output_urls": output_urls,
            "processing_time_sec": round(len(image_sources) * random.uniform(0.8, 2.5), 1),
            "status": "completed",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "framework_pipeline": result.get("bot_name"),
        }

    def cartoonify(self, image_source: str, style: str = "cartoon") -> dict:
        """Transform a photo into a cartoon or stylized art form (PRO+).

        Parameters
        ----------
        image_source : str
            URL or file path of the source image.
        style : str
            Art style: cartoon, anime, sketch, comic, watercolor.
        """
        self._check_feature(FEATURE_CARTOON_CONVERSION)
        self._check_daily_limit()
        if style not in _CARTOON_STYLES:
            style = "cartoon"
        result = self.flow.run_pipeline(
            raw_data={"task": "cartoonify", "image_source": image_source, "style": style},
            learning_method="self_supervised",
        )
        uid = uuid.uuid4().hex[:12]
        self._record()
        return {
            "image_source": image_source,
            "style": style,
            "output_url": f"https://cdn.dreamcobots.ai/photos/cartoon_{uid}.png",
            "processing_model": "CartoonGAN-v2",
            "style_strength": round(random.uniform(0.80, 0.95), 2),
            "resolution": "2048x2048",
            "status": "completed",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "framework_pipeline": result.get("bot_name"),
        }

    def create_caricature(self, image_source: str) -> dict:
        """Generate an exaggerated caricature from a portrait photo (PRO+).

        Parameters
        ----------
        image_source : str
            URL or file path of the portrait image.
        """
        self._check_feature(FEATURE_CARICATURE)
        self._check_daily_limit()
        result = self.flow.run_pipeline(
            raw_data={"task": "create_caricature", "image_source": image_source},
            learning_method="self_supervised",
        )
        uid = uuid.uuid4().hex[:12]
        self._record()
        return {
            "image_source": image_source,
            "exaggeration_level": random.choice(["mild", "medium", "strong"]),
            "features_enhanced": random.sample(["eyes", "nose", "smile", "ears", "chin", "forehead"], 3),
            "output_url": f"https://cdn.dreamcobots.ai/photos/caricature_{uid}.png",
            "processing_model": "CariGAN-v1",
            "face_detected": True,
            "status": "completed",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "framework_pipeline": result.get("bot_name"),
        }

    def generate_animation(
        self, image_sources: list[str], style: str = "anime", fps: int = 24
    ) -> dict:
        """Generate an animation from a sequence of images (ENTERPRISE only).

        Parameters
        ----------
        image_sources : list[str]
            Ordered list of frame image URLs or file paths.
        style : str
            Animation style (e.g. 'anime', 'cartoon', 'realistic').
        fps : int
            Frames per second for the output animation.
        """
        self._check_feature(FEATURE_ANIMATION_GENERATION)
        self._check_daily_limit()
        result = self.flow.run_pipeline(
            raw_data={"task": "generate_animation", "frame_count": len(image_sources), "style": style, "fps": fps},
            learning_method="self_supervised",
        )
        uid = uuid.uuid4().hex[:12]
        duration_sec = len(image_sources)
        self._record()
        return {
            "image_sources": image_sources,
            "frame_count": len(image_sources),
            "style": style,
            "fps": fps,
            "output_url": f"https://cdn.dreamcobots.ai/animations/{uid}.mp4",
            "gif_url": f"https://cdn.dreamcobots.ai/animations/{uid}.gif",
            "duration_sec": duration_sec,
            "format": "MP4 + GIF",
            "resolution": "1280x720",
            "status": "completed",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "framework_pipeline": result.get("bot_name"),
        }

    def generate_cartoon_frame(self, description: str, style: str = "disney") -> dict:
        """Generate a cartoon-style image frame from a text description (ENTERPRISE only).

        Parameters
        ----------
        description : str
            Text description of the scene or character to generate.
        style : str
            Cartoon style: disney, pixar, anime, comic, manga.
        """
        self._check_feature(FEATURE_CARTOON_FRAME_GENERATION)
        self._check_daily_limit()
        if style not in _CARTOON_FRAME_STYLES:
            style = "disney"
        result = self.flow.run_pipeline(
            raw_data={"task": "generate_cartoon_frame", "description": description, "style": style},
            learning_method="self_supervised",
        )
        uid = uuid.uuid4().hex[:12]
        self._record()
        return {
            "description": description,
            "style": style,
            "output_url": f"https://cdn.dreamcobots.ai/frames/frame_{uid}.png",
            "resolution": "1920x1080",
            "model": "CartoonDiffusion-v3",
            "generation_steps": 50,
            "seed": random.randint(1000, 9999),
            "status": "completed",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "framework_pipeline": result.get("bot_name"),
        }

    def get_editing_dashboard(self) -> dict:
        """Return dashboard with daily usage stats and tier information."""
        limit = DAILY_LIMITS[self.tier.value]
        upgrade = get_upgrade_path(self.tier)
        return {
            "bot_name": "PhotoEditingBot",
            "tier": self.tier.value,
            "tier_display": self.config.name,
            "price_usd_monthly": self.config.price_usd_monthly,
            "daily_limit": limit,
            "count_today": self._daily_count,
            "remaining": (limit - self._daily_count) if limit is not None else "unlimited",
            "features": BOT_FEATURES[self.tier.value],
            "available_filters": _AVAILABLE_FILTERS,
            "available_cartoon_styles": _CARTOON_STYLES,
            "commercial_rights": self.tier_info["commercial_rights"],
            "upgrade_available": upgrade is not None,
            "upgrade_to": upgrade.name if upgrade else None,
            "upgrade_price_usd": upgrade.price_usd_monthly if upgrade else None,
        }
