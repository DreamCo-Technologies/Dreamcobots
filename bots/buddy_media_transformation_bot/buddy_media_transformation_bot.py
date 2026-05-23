"""
Buddy Media Transformation Bot — Main Entry Point

An AI-powered media creation and transformation assistant for the DreamCobots ecosystem.

Core capabilities:
  • Text-to-Music           — Convert text/lyrics into original music tracks (FREE+)
  • Video Creation          — Generate short-form and long-form videos from scripts (PRO+)
  • Personalized Song       — Create songs using the user's cloned voice (ENTERPRISE)
  • Avatar Video            — Lip-synced avatar video from script and user photo (ENTERPRISE)
  • Visual Style Customization — Apply custom brand styles to media output (ENTERPRISE)

Tier limits:
  - FREE:       3 creations/day, basic music, watermarked output.
  - PRO:        20 creations/day, advanced music, voice integration, video creation.
  - ENTERPRISE: Unlimited, user voice cloning, avatar videos, custom styles, commercial rights.

Usage
-----
    from bots.buddy_media_transformation_bot import BuddyMediaTransformationBot, Tier
    bot = BuddyMediaTransformationBot(tier=Tier.PRO)
    track = bot.text_to_music("Upbeat summer anthem about chasing dreams", style="pop")
    print(bot.get_media_dashboard())
"""

from __future__ import annotations

import sys
import os
import uuid
import hashlib
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ai-models-integration"))
from tiers import Tier, get_tier_config, get_upgrade_path  # noqa: F401
from bots.buddy_media_transformation_bot.tiers import (
    BOT_FEATURES,
    get_bot_tier_info,
    DAILY_LIMITS,
    FEATURE_TEXT_TO_MUSIC_BASIC,
    FEATURE_TEXT_TO_MUSIC_ADVANCED,
    FEATURE_VIDEO_CREATION,
    FEATURE_USER_VOICE_CLONING,
    FEATURE_AVATAR_CREATION,
    FEATURE_CUSTOM_VISUAL_STYLES,
    FEATURE_WATERMARK,
    FEATURE_COMMERCIAL_RIGHTS,
)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from framework import GlobalAISourcesFlow  # noqa: F401
from bots.media_runtime import (
    InferenceGateway,
    LocalAssetStore,
    MediaEngine,
    MediaJobRuntime,
    QueuePriority,
    build_media_lifecycle_contract,
)

_MUSICAL_KEYS = ["C major", "G major", "D major", "A minor", "E minor", "F major", "B♭ major"]
_INSTRUMENTS = [
    ["piano", "strings", "drums", "bass"],
    ["guitar", "synth", "percussion", "vocals"],
    ["violin", "cello", "flute", "piano"],
    ["drums", "bass", "lead_guitar", "rhythm_guitar"],
    ["synthesizer", "808_bass", "hi_hat", "claps"],
]


class BuddyMediaTransformationBotError(Exception):
    """Raised when a tier limit or feature restriction is violated."""


class BuddyMediaTransformationBot:
    """AI-powered media transformation and content generation bot with tier-based feature gating.

    Parameters
    ----------
    tier : Tier
        Subscription tier controlling daily limits and feature access.
    """

    def __init__(self, tier: Tier = Tier.FREE) -> None:
        self.tier = tier
        self.config = get_tier_config(tier)
        self.tier_info = get_bot_tier_info(tier)
        self.flow = GlobalAISourcesFlow(bot_name="BuddyMediaTransformationBot")
        self._daily_count: int = 0
        self.asset_store = LocalAssetStore()
        self.inference_gateway = InferenceGateway()
        self.runtime = MediaJobRuntime(asset_store=self.asset_store, gateway=self.inference_gateway)
        self.media_engine = MediaEngine(
            owner="buddy_media_transformation_bot",
            runtime=self.runtime,
            asset_store=self.asset_store,
        )

    def _check_daily_limit(self) -> None:
        """Raise BuddyMediaTransformationBotError if the daily limit is exceeded."""
        limit = DAILY_LIMITS[self.tier.value]
        if limit is not None and self._daily_count >= limit:
            upgrade = get_upgrade_path(self.tier)
            upgrade_msg = (
                f" Upgrade to {upgrade.name} (${upgrade.price_usd_monthly}/mo) for more."
                if upgrade else ""
            )
            raise BuddyMediaTransformationBotError(
                f"Daily limit of {limit} reached for the {self.tier.value.upper()} tier.{upgrade_msg}"
            )

    def _check_feature(self, feature: str) -> None:
        """Raise BuddyMediaTransformationBotError if the feature is not available on the current tier."""
        if feature not in BOT_FEATURES[self.tier.value]:
            upgrade = get_upgrade_path(self.tier)
            upgrade_msg = (
                f" Upgrade to {upgrade.name} for access." if upgrade else ""
            )
            raise BuddyMediaTransformationBotError(
                f"Feature '{feature}' is not available on the {self.tier.value.upper()} tier.{upgrade_msg}"
            )

    def _record(self) -> None:
        self._daily_count += 1

    @staticmethod
    def _deterministic_seed(*parts: str) -> int:
        digest = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()
        return int(digest[:8], 16)

    def _run_media_job(
        self,
        *,
        operation: str,
        media_type: str,
        payload: dict,
        media_format: str,
        content_type: str,
        lineage: list[str] | None = None,
    ) -> tuple[dict, dict]:
        return self.media_engine.execute_render(
            operation=operation,
            media_type=media_type,
            payload=payload,
            output_format=media_format,
            output_content_type=content_type,
            provider_chain=["openai", "elevenlabs", "ffmpeg-local"],
            estimated_duration_sec=max(10, len(str(payload)) // 4),
            lineage=lineage,
            extra_metadata={"tier": self.tier.value},
            retention_days=30,
            max_retries=2,
            tier=self.tier.value,
            priority=QueuePriority.HIGH if self.tier.value == "enterprise" else QueuePriority.NORMAL,
        )

    def text_to_music(self, text: str, style: str = "auto") -> dict:
        """Convert text or song lyrics into an original music track.

        FREE tier: basic quality. PRO/ENTERPRISE: advanced AI composition.

        Parameters
        ----------
        text : str
            Lyrics, description, or mood text to base the music on.
        style : str
            Musical style hint (e.g. 'pop', 'jazz', 'classical', 'auto').
        """
        self._check_feature(FEATURE_TEXT_TO_MUSIC_BASIC)
        self._check_daily_limit()
        is_advanced = FEATURE_TEXT_TO_MUSIC_ADVANCED in BOT_FEATURES[self.tier.value]
        is_watermarked = FEATURE_WATERMARK in BOT_FEATURES[self.tier.value]
        result = self.flow.run_pipeline(
            raw_data={"task": "text_to_music", "text": text, "style": style, "advanced": is_advanced},
            learning_method="self_supervised",
        )
        style_value = style if style != "auto" else ["pop", "electronic", "cinematic", "ambient"][
            self._deterministic_seed(text, self.tier.value) % 4
        ]
        seed = self._deterministic_seed(text, style_value, self.tier.value)
        job, asset = self._run_media_job(
            operation="text_to_music",
            media_type="audio",
            payload={"text": text, "style": style_value, "advanced": is_advanced},
            media_format="mp3",
            content_type="audio/mpeg",
        )
        self._record()
        lifecycle = build_media_lifecycle_contract(
            job=job,
            primary_asset=asset,
            lineage={"operation": "text_to_music", "text_prompt": text},
            project_id=f"buddy_music_{job['job_id']}",
        )
        return {
            **lifecycle,
            "text": text,
            "style": style_value,
            "audio_url": asset["delivery_url"],
            "duration_secs": max(30, min(180, len(text.split()) * 5)),
            "bpm": 80 + (seed % 81),
            "key": _MUSICAL_KEYS[seed % len(_MUSICAL_KEYS)],
            "instruments": _INSTRUMENTS[seed % len(_INSTRUMENTS)],
            "quality": "Advanced AI" if is_advanced else "Standard",
            "watermarked": is_watermarked,
            "job": job,
            "asset": asset,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "framework_pipeline": result.get("bot_name"),
        }

    def create_video(
        self, script: str, voice_sample: str | None = None, image_sample: str | None = None
    ) -> dict:
        """Generate a video from a script with optional voice and image samples (PRO+).

        Parameters
        ----------
        script : str
            Video script or narration text.
        voice_sample : str | None
            Optional voice sample URL for voice matching.
        image_sample : str | None
            Optional image URL for visual style reference.
        """
        self._check_feature(FEATURE_VIDEO_CREATION)
        self._check_daily_limit()
        result = self.flow.run_pipeline(
            raw_data={
                "task": "create_video",
                "script": script,
                "voice_sample": voice_sample,
                "image_sample": image_sample,
            },
            learning_method="supervised",
        )
        seed = self._deterministic_seed(script, str(voice_sample), str(image_sample), self.tier.value)
        job, asset = self._run_media_job(
            operation="create_video",
            media_type="video",
            payload={"script": script, "voice_sample": voice_sample, "image_sample": image_sample},
            media_format="mp4",
            content_type="video/mp4",
        )
        thumb_job, thumb_asset = self._run_media_job(
            operation="create_video_thumbnail",
            media_type="image",
            payload={"script": script, "source_asset_id": asset["asset_id"]},
            media_format="jpg",
            content_type="image/jpeg",
            lineage=[asset["asset_id"]],
        )
        self._record()
        lifecycle = build_media_lifecycle_contract(
            job=job,
            primary_asset=asset,
            preview_assets=[thumb_asset],
            lineage={"operation": "create_video", "thumbnail_asset_id": thumb_asset["asset_id"]},
            project_id=f"buddy_video_{job['job_id']}",
        )
        return {
            **lifecycle,
            "script": script[:100] + "..." if len(script) > 100 else script,
            "video_url": asset["delivery_url"],
            "thumbnail_url": thumb_asset["delivery_url"],
            "duration_secs": max(30, min(300, len(script.split()) * 3)),
            "resolution": "1920x1080",
            "fps": 30,
            "voice_used": voice_sample or "default_narrator_v2",
            "image_style_applied": image_sample is not None,
            "job": job,
            "asset": asset,
            "thumbnail_job": thumb_job,
            "thumbnail_asset": thumb_asset,
            "render_checksum": hashlib.sha256(f"{script}|{seed}".encode("utf-8")).hexdigest(),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "framework_pipeline": result.get("bot_name"),
        }

    def create_personalized_song(self, lyrics: str, user_voice_id: str, genre: str) -> dict:
        """Create a personalized song sung in the user's cloned voice (ENTERPRISE only).

        Parameters
        ----------
        lyrics : str
            Full song lyrics.
        user_voice_id : str
            Cloned voice model ID from the voice cloning service.
        genre : str
            Musical genre (e.g. 'pop', 'r&b', 'country', 'rap').
        """
        self._check_feature(FEATURE_USER_VOICE_CLONING)
        self._check_daily_limit()
        result = self.flow.run_pipeline(
            raw_data={"task": "create_personalized_song", "lyrics": lyrics, "voice_id": user_voice_id, "genre": genre},
            learning_method="supervised",
        )
        seed = self._deterministic_seed(lyrics, user_voice_id, genre, self.tier.value)
        job, asset = self._run_media_job(
            operation="create_personalized_song",
            media_type="audio",
            payload={"lyrics": lyrics, "voice_id": user_voice_id, "genre": genre},
            media_format="wav",
            content_type="audio/wav",
        )
        self._record()
        lifecycle = build_media_lifecycle_contract(
            job=job,
            primary_asset=asset,
            lineage={"operation": "create_personalized_song", "voice_id": user_voice_id},
            project_id=f"buddy_voice_{job['job_id']}",
        )
        return {
            **lifecycle,
            "lyrics": lyrics[:100] + "..." if len(lyrics) > 100 else lyrics,
            "genre": genre,
            "voice_id": user_voice_id,
            "audio_url": asset["delivery_url"],
            "duration_secs": max(120, min(300, len(lyrics.split()) * 4)),
            "bpm": 70 + (seed % 71),
            "key": _MUSICAL_KEYS[seed % len(_MUSICAL_KEYS)],
            "vocal_quality_score": round(0.88 + ((seed % 10) / 100), 2),
            "job": job,
            "asset": asset,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "framework_pipeline": result.get("bot_name"),
        }

    def create_avatar_video(self, script: str, user_image: str) -> dict:
        """Create an AI avatar video lip-synced to the script using the user's photo (ENTERPRISE only).

        Parameters
        ----------
        script : str
            Narration script for the avatar video.
        user_image : str
            URL or file path to the user's reference image.
        """
        self._check_feature(FEATURE_AVATAR_CREATION)
        self._check_daily_limit()
        result = self.flow.run_pipeline(
            raw_data={"task": "create_avatar_video", "script": script, "user_image": user_image},
            learning_method="supervised",
        )
        job, asset = self._run_media_job(
            operation="create_avatar_video",
            media_type="video",
            payload={"script": script, "user_image": user_image},
            media_format="mp4",
            content_type="video/mp4",
        )
        self._record()
        lifecycle = build_media_lifecycle_contract(
            job=job,
            primary_asset=asset,
            lineage={"operation": "create_avatar_video", "source_image": user_image},
            project_id=f"buddy_avatar_{job['job_id']}",
        )
        return {
            **lifecycle,
            "script": script[:100] + "..." if len(script) > 100 else script,
            "user_image": user_image,
            "avatar_video_url": asset["delivery_url"],
            "resolution": "1920x1080",
            "fps": 30,
            "duration_secs": round(len(script.split()) / 2.5, 1),
            "lip_sync_quality": "excellent",
            "facial_expression_mapping": True,
            "job": job,
            "asset": asset,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "framework_pipeline": result.get("bot_name"),
        }

    def customize_visual_style(self, style_options: dict) -> dict:
        """Apply custom visual style settings to all generated media (ENTERPRISE only).

        Parameters
        ----------
        style_options : dict
            Style configuration including color palette, font, overlay, brand logo, etc.
        """
        self._check_feature(FEATURE_CUSTOM_VISUAL_STYLES)
        self._check_daily_limit()
        result = self.flow.run_pipeline(
            raw_data={"task": "customize_visual_style", "style_options": style_options},
            learning_method="unsupervised",
        )
        uid = uuid.uuid4().hex[:12]
        applied_styles = [k for k in style_options if style_options[k]]
        self._record()
        return {
            "style_options": style_options,
            "applied_styles": applied_styles if applied_styles else ["color_palette", "typography", "brand_overlay"],
            "preview_url": f"https://cdn.dreamcobots.ai/previews/style_{uid}.jpg",
            "style_preset_id": f"style_{uid}",
            "status": "applied",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "framework_pipeline": result.get("bot_name"),
        }

    def get_media_dashboard(self) -> dict:
        """Return dashboard with usage stats and tier information."""
        limit = DAILY_LIMITS[self.tier.value]
        upgrade = get_upgrade_path(self.tier)
        return {
            "bot_name": "BuddyMediaTransformationBot",
            "tier": self.tier.value,
            "tier_display": self.config.name,
            "price_usd_monthly": self.config.price_usd_monthly,
            "daily_limit": limit,
            "count_today": self._daily_count,
            "remaining": (limit - self._daily_count) if limit is not None else "unlimited",
            "features": BOT_FEATURES[self.tier.value],
            "watermark_applied": FEATURE_WATERMARK in BOT_FEATURES[self.tier.value],
            "commercial_rights": self.tier_info["commercial_rights"],
            "upgrade_available": upgrade is not None,
            "upgrade_to": upgrade.name if upgrade else None,
            "upgrade_price_usd": upgrade.price_usd_monthly if upgrade else None,
        }
