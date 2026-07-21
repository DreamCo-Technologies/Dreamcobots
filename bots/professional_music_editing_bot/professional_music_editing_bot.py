"""
Professional Music Editing Bot — Main Entry Point

An AI-powered professional music production and editing studio for the DreamCobots ecosystem.

Core capabilities:
  • Project Management   — Create and manage multi-track music projects
  • Track Editing        — Add, remove, and edit audio tracks with per-tier track limits
  • Effects Processing   — Apply EQ, compression, reverb, delay, and more
  • AI Composition       — Generate full compositions by genre and mood (PRO+)
  • Noise Reduction      — AI-powered background noise elimination (PRO+)
  • AI Mastering         — Professional loudness normalization and mastering (ENTERPRISE)
  • DAW Export           — Export to Logic Pro, Ableton, Pro Tools compatible formats (ENTERPRISE)

Tier limits:
  - FREE:       3 projects/month, 2 tracks, basic editing, MP3 export.
  - PRO:        30 projects/month, 16 tracks, AI composition, noise reduction, WAV/AIFF export.
  - ENTERPRISE: Unlimited projects and tracks, AI mastering, DAW compatibility.

Usage
-----
    from bots.professional_music_editing_bot import ProfessionalMusicEditingBot, Tier
    bot = ProfessionalMusicEditingBot(tier=Tier.PRO)
    project = bot.load_project()
    bot.add_track("drums")
    print(bot.get_studio_dashboard())
"""

from __future__ import annotations

import sys
import os
import uuid
import random
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ai-models-integration"))
from tiers import Tier, get_tier_config, get_upgrade_path  # noqa: F401
from bots.professional_music_editing_bot.tiers import (
    BOT_FEATURES,
    get_bot_tier_info,
    MONTHLY_LIMITS,
    DAILY_LIMITS,
    TRACK_LIMITS,
    FEATURE_BASIC_EDITING,
    FEATURE_MP3_EXPORT,
    FEATURE_MULTI_TRACK_EDITING,
    FEATURE_AI_COMPOSITION,
    FEATURE_NOISE_REDUCTION,
    FEATURE_WAV_AIFF_EXPORT,
    FEATURE_AI_MASTERING,
    FEATURE_DAW_COMPATIBILITY,
)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from framework import GlobalAISourcesFlow  # noqa: F401

_EFFECTS_DEFAULTS = {
    "eq": {"low_hz": 80, "mid_hz": 1000, "high_hz": 8000, "low_gain_db": 2, "high_gain_db": -1},
    "compression": {"ratio": "4:1", "threshold_db": -18, "attack_ms": 5, "release_ms": 100},
    "reverb": {"room_size": 0.6, "damping": 0.5, "wet_mix": 0.3},
    "delay": {"delay_ms": 375, "feedback": 0.35, "wet_mix": 0.25},
    "chorus": {"rate_hz": 1.5, "depth": 0.4, "wet_mix": 0.5},
    "limiter": {"ceiling_db": -0.3, "release_ms": 50},
}


class ProfessionalMusicEditingBotError(Exception):
    """Raised when a monthly limit, track limit, or feature restriction is violated."""


class ProfessionalMusicEditingBot:
    """AI-powered professional music editing and production bot with tier-based feature gating.

    Parameters
    ----------
    tier : Tier
        Subscription tier controlling monthly limits, track limits, and feature access.
    """

    def __init__(self, tier: Tier = Tier.FREE) -> None:
        self.tier = tier
        self.config = get_tier_config(tier)
        self.tier_info = get_bot_tier_info(tier)
        self.flow = GlobalAISourcesFlow(bot_name="ProfessionalMusicEditingBot")
        self._monthly_count: int = 0
        self._projects: dict[str, dict] = {}
        self._active_project_id: str | None = None

    def _check_monthly_limit(self) -> None:
        """Raise ProfessionalMusicEditingBotError if the monthly project limit is exceeded."""
        limit = MONTHLY_LIMITS[self.tier.value]
        if limit is not None and self._monthly_count >= limit:
            upgrade = get_upgrade_path(self.tier)
            upgrade_msg = (
                f" Upgrade to {upgrade.name} (${upgrade.price_usd_monthly}/mo) for more."
                if upgrade else ""
            )
            raise ProfessionalMusicEditingBotError(
                f"Monthly project limit of {limit} reached for the "
                f"{self.tier.value.upper()} tier.{upgrade_msg}"
            )

    def _check_feature(self, feature: str) -> None:
        """Raise ProfessionalMusicEditingBotError if the feature is not available on the current tier."""
        if feature not in BOT_FEATURES[self.tier.value]:
            upgrade = get_upgrade_path(self.tier)
            upgrade_msg = (
                f" Upgrade to {upgrade.name} for access." if upgrade else ""
            )
            raise ProfessionalMusicEditingBotError(
                f"Feature '{feature}' is not available on the {self.tier.value.upper()} tier.{upgrade_msg}"
            )

    def _record(self) -> None:
        self._monthly_count += 1

    def load_project(self, project_id: str | None = None) -> dict:
        """Load an existing project or create a new one.

        When creating a new project, defaults are: sample_rate=44100 Hz, bit_depth=24-bit.

        Parameters
        ----------
        project_id : str | None
            Existing project ID to load, or None to create a new project.
        """
        self._check_feature(FEATURE_BASIC_EDITING)
        result = self.flow.run_pipeline(
            raw_data={"task": "load_project", "project_id": project_id},
            learning_method="unsupervised",
        )
        if project_id and project_id in self._projects:
            project = self._projects[project_id]
            status = "loaded"
        else:
            project_id = project_id or f"proj_{uuid.uuid4().hex[:10]}"
            project = {
                "project_id": project_id,
                "name": f"Project {len(self._projects) + 1}",
                "tracks": [],
                "created_at": datetime.utcnow().isoformat() + "Z",
                "sample_rate": 44100,
                "bit_depth": 24,
            }
            self._projects[project_id] = project
            self._active_project_id = project_id
            self._record()
            status = "created"
        self._active_project_id = project_id
        return {
            "project_id": project_id,
            "name": project["name"],
            "tracks": project["tracks"],
            "track_count": len(project["tracks"]),
            "created_at": project["created_at"],
            "sample_rate": project.get("sample_rate", 44100),
            "bit_depth": project.get("bit_depth", 24),
            "status": status,
            "framework_pipeline": result.get("bot_name"),
        }

    def add_track(self, track_type: str, audio_source: str | None = None) -> dict:
        """Add an audio track to the active project (track count limits apply by tier).

        Parameters
        ----------
        track_type : str
            Track type (e.g. 'drums', 'bass', 'melody', 'vocals', 'fx').
        audio_source : str | None
            Optional URL or file path for the audio content.
        """
        self._check_feature(FEATURE_BASIC_EDITING)
        project_id = self._active_project_id or f"proj_{uuid.uuid4().hex[:10]}"
        if project_id not in self._projects:
            self._projects[project_id] = {
                "project_id": project_id, "name": "Auto Project", "tracks": [],
                "created_at": datetime.utcnow().isoformat() + "Z",
            }
            self._active_project_id = project_id

        project = self._projects[project_id]
        track_limit = TRACK_LIMITS[self.tier.value]
        current_tracks = len(project["tracks"])
        if track_limit is not None and current_tracks >= track_limit:
            upgrade = get_upgrade_path(self.tier)
            upgrade_msg = f" Upgrade to {upgrade.name} for more tracks." if upgrade else ""
            raise ProfessionalMusicEditingBotError(
                f"Track limit of {track_limit} reached for the {self.tier.value.upper()} tier.{upgrade_msg}"
            )
        result = self.flow.run_pipeline(
            raw_data={"task": "add_track", "track_type": track_type, "audio_source": audio_source},
            learning_method="supervised",
        )
        track_id = f"track_{uuid.uuid4().hex[:8]}"
        track = {
            "track_id": track_id,
            "track_type": track_type,
            "audio_source": audio_source,
            "effects": [],
            "volume_db": 0.0,
            "pan": 0.0,
        }
        project["tracks"].append(track)
        return {
            "track_id": track_id,
            "track_type": track_type,
            "audio_source": audio_source,
            "project_id": project_id,
            "track_number": len(project["tracks"]),
            "volume_db": 0.0,
            "pan": 0.0,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "framework_pipeline": result.get("bot_name"),
        }

    def apply_effect(self, track_id: str, effect: str, params: dict | None = None) -> dict:
        """Apply an audio effect to a track.

        FREE tier: basic effects. PRO+: full multi-track effects suite.

        Parameters
        ----------
        track_id : str
            The track to apply the effect to.
        effect : str
            Effect name: eq, compression, reverb, delay, chorus, limiter.
        params : dict | None
            Effect parameters; defaults are applied if None.
        """
        self._check_feature(FEATURE_BASIC_EDITING)
        advanced_effects = {"chorus", "limiter"}
        if effect in advanced_effects:
            self._check_feature(FEATURE_MULTI_TRACK_EDITING)
        resolved_params = params or _EFFECTS_DEFAULTS.get(effect, {})
        result = self.flow.run_pipeline(
            raw_data={"task": "apply_effect", "track_id": track_id, "effect": effect, "params": resolved_params},
            learning_method="supervised",
        )
        return {
            "track_id": track_id,
            "effect": effect,
            "params": resolved_params,
            "status": "applied",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "framework_pipeline": result.get("bot_name"),
        }

    def compose_with_ai(self, genre: str, mood: str, duration_sec: int = 60) -> dict:
        """Use AI to compose an original music arrangement (PRO+).

        Parameters
        ----------
        genre : str
            Musical genre (e.g. 'jazz', 'electronic', 'orchestral', 'hip-hop').
        mood : str
            Emotional mood (e.g. 'uplifting', 'melancholic', 'energetic', 'calm').
        duration_sec : int
            Target duration in seconds.
        """
        self._check_feature(FEATURE_AI_COMPOSITION)
        self._check_monthly_limit()
        result = self.flow.run_pipeline(
            raw_data={"task": "compose_with_ai", "genre": genre, "mood": mood, "duration_sec": duration_sec},
            learning_method="self_supervised",
        )
        project_id = f"proj_{uuid.uuid4().hex[:10]}"
        tempo = random.randint(70, 160)
        track_types = ["drums", "bass", "chord_pads", "melody", "atmosphere"]
        tracks = [
            {"track_id": f"track_{uuid.uuid4().hex[:8]}", "track_type": t, "role": t}
            for t in track_types
        ]
        self._projects[project_id] = {
            "project_id": project_id, "name": f"{genre.title()} AI Composition",
            "tracks": tracks, "created_at": datetime.utcnow().isoformat() + "Z",
        }
        self._active_project_id = project_id
        self._record()
        return {
            "genre": genre,
            "mood": mood,
            "duration_sec": duration_sec,
            "project_id": project_id,
            "tracks": tracks,
            "tempo": tempo,
            "key": random.choice(["C major", "G major", "A minor", "E minor", "F major"]),
            "time_signature": random.choice(["4/4", "3/4", "6/8"]),
            "ai_model": "MusicComposer-v4",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "framework_pipeline": result.get("bot_name"),
        }

    def reduce_noise(self, track_id: str) -> dict:
        """Apply AI noise reduction to a track (PRO+).

        Parameters
        ----------
        track_id : str
            The track to denoise.
        """
        self._check_feature(FEATURE_NOISE_REDUCTION)
        result = self.flow.run_pipeline(
            raw_data={"task": "reduce_noise", "track_id": track_id},
            learning_method="supervised",
        )
        noise_before = round(random.uniform(-45, -30), 1)
        reduction = round(random.uniform(15, 25), 1)
        return {
            "track_id": track_id,
            "noise_floor_before_db": noise_before,
            "noise_floor_after_db": round(noise_before - reduction, 1),
            "reduction_db": reduction,
            "algorithm": "SpectralSubtraction-v2",
            "status": "completed",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "framework_pipeline": result.get("bot_name"),
        }

    def master_track(self, project_id: str) -> dict:
        """Apply AI mastering to a project for streaming-ready loudness (ENTERPRISE only).

        Parameters
        ----------
        project_id : str
            The project to master.
        """
        self._check_feature(FEATURE_AI_MASTERING)
        result = self.flow.run_pipeline(
            raw_data={"task": "master_track", "project_id": project_id},
            learning_method="supervised",
        )
        return {
            "project_id": project_id,
            "loudness_lufs": -14.0,
            "true_peak_dbtp": -1.0,
            "dynamic_range": round(random.uniform(7.0, 12.0), 1),
            "eq_adjustments": {
                "sub_bass_boost_db": 1.5,
                "low_mid_cut_db": -0.8,
                "high_freq_air_db": 2.0,
            },
            "compression_ratio": "4:1",
            "stereo_width_enhancement": True,
            "master_standard": "Spotify / Apple Music",
            "status": "mastered",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "framework_pipeline": result.get("bot_name"),
        }

    def export_project(
        self, project_id: str, export_format: str = "WAV", daw_compatible: str | None = None
    ) -> dict:
        """Export the project to an audio file.

        FREE: MP3 only. PRO: WAV/AIFF. ENTERPRISE: DAW-compatible stems.

        Parameters
        ----------
        project_id : str
            Project to export.
        export_format : str
            Output format: MP3, WAV, AIFF.
        daw_compatible : str | None
            DAW name for stem export (e.g. 'Logic Pro', 'Ableton Live'). ENTERPRISE only.
        """
        format_upper = export_format.upper()
        if format_upper in ("WAV", "AIFF"):
            self._check_feature(FEATURE_WAV_AIFF_EXPORT)
        else:
            self._check_feature(FEATURE_MP3_EXPORT)
        if daw_compatible:
            self._check_feature(FEATURE_DAW_COMPATIBILITY)
        result = self.flow.run_pipeline(
            raw_data={"task": "export_project", "project_id": project_id, "format": format_upper, "daw": daw_compatible},
            learning_method="supervised",
        )
        uid = uuid.uuid4().hex[:12]
        project = self._projects.get(project_id, {})
        track_count = max(1, len(project.get("tracks", [])))
        size_mb = round(track_count * random.uniform(3.5, 8.0), 1)
        return {
            "project_id": project_id,
            "export_format": format_upper,
            "file_url": f"https://cdn.dreamcobots.ai/exports/{uid}.{format_upper.lower()}",
            "file_size_mb": size_mb,
            "daw_compatible": daw_compatible,
            "stems_included": daw_compatible is not None,
            "status": "exported",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "framework_pipeline": result.get("bot_name"),
        }

    def get_studio_dashboard(self) -> dict:
        """Return studio dashboard with monthly usage stats and tier information."""
        limit = MONTHLY_LIMITS[self.tier.value]
        track_limit = TRACK_LIMITS[self.tier.value]
        upgrade = get_upgrade_path(self.tier)
        return {
            "bot_name": "ProfessionalMusicEditingBot",
            "tier": self.tier.value,
            "tier_display": self.config.name,
            "price_usd_monthly": self.config.price_usd_monthly,
            "monthly_limit": limit,
            "monthly_count": self._monthly_count,
            "remaining": (limit - self._monthly_count) if limit is not None else "unlimited",
            "track_limit": track_limit if track_limit is not None else "unlimited",
            "projects_open": len(self._projects),
            "active_project_id": self._active_project_id,
            "features": BOT_FEATURES[self.tier.value],
            "commercial_rights": self.tier_info["commercial_rights"],
            "upgrade_available": upgrade is not None,
            "upgrade_to": upgrade.name if upgrade else None,
            "upgrade_price_usd": upgrade.price_usd_monthly if upgrade else None,
        }
