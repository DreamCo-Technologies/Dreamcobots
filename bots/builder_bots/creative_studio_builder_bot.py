# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""
Creative Studio Builder Bot

Completes the Creative Hub — ads, music, and cinematic content:

  Phase 1 — Foundation
    • Builds end-to-end ad-creation workflow (script → voice → video).
    • Integrates music_track_synthesizer for dynamic instrumental generation.
    • Expands CineCore capabilities with script-to-trailer automation.
    • Stamps milestones via TimestampButton.

  Phase 2 — Placeholders & Ideation
    • Scaffolds placeholder workflows for experimental creative features.
    • Logs creative-domain bot ideas to bot_ideas_log.txt.

Adheres to the DreamCobots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from core.timestamp_button import TimestampButton
from bots.builder_bots._shared import append_bot_ideas
from bots.creative_studio_bot.music_track_synthesizer import MusicTrackSynthesizer


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class AdCreationJob:
    """Represents an end-to-end ad creation job."""

    job_id: str
    business_name: str
    product: str
    platform: str
    script: str = ""
    voiceover_ref: str = ""
    video_ref: str = ""
    music_ref: str = ""
    status: str = "queued"

    def to_dict(self) -> dict:
        return {
            "job_id": self.job_id,
            "business_name": self.business_name,
            "product": self.product,
            "platform": self.platform,
            "script": self.script,
            "voiceover_ref": self.voiceover_ref,
            "video_ref": self.video_ref,
            "music_ref": self.music_ref,
            "status": self.status,
        }


@dataclass
class CinematicProject:
    """Represents a cinematic production project."""

    project_id: str
    title: str
    genre: str
    synopsis: str
    script_ref: str = ""
    trailer_ref: str = ""
    status: str = "development"

    def to_dict(self) -> dict:
        return {
            "project_id": self.project_id,
            "title": self.title,
            "genre": self.genre,
            "synopsis": self.synopsis,
            "script_ref": self.script_ref,
            "trailer_ref": self.trailer_ref,
            "status": self.status,
        }


# ---------------------------------------------------------------------------
# CreativeStudioBuilderBot
# ---------------------------------------------------------------------------


class CreativeStudioBuilderBot:
    """
    Builder bot that completes the Creative Hub infrastructure.

    Parameters
    ----------
    timestamp_button : TimestampButton | None
        Shared milestone tracker.
    """

    bot_id = "creative_studio_builder_bot"
    name = "Creative Studio Builder Bot"
    category = "builder"

    SUPPORTED_PLATFORMS = ["tiktok", "youtube", "instagram", "facebook", "cinema"]
    SUPPORTED_GENRES = ["thriller", "comedy", "drama", "sci-fi", "documentary", "musical"]

    PLACEHOLDER_TEMPLATES: List[str] = [
        "interactive_ad_bot_placeholder",
        "music_video_sync_placeholder",
        "tiktok_trend_content_placeholder",
        "script_to_trailer_automation_placeholder",
        "personalized_content_creator_placeholder",
        "music_overlay_compositor_placeholder",
    ]

    BOT_IDEAS: List[str] = [
        "InteractiveAdBot — adapts ad content in real-time based on viewer interactions",
        "MusicVideoDirectorBot — syncs AI visuals to beat timings of an uploaded track",
        "TikTokTrendBot — auto-generates short-form content aligned with trending sounds",
        "ScriptToTrailerBot — converts a screenplay synopsis into a 60-second teaser",
        "PersonalisedContentBot — tailors ads to individual viewer demographics",
        "CineColorGraderBot — applies Hollywood-grade colour grading to raw footage",
        "LyricVideoBot — generates animated lyric videos from music tracks",
        "BrandKitBot — creates a full visual brand identity (logo, palette, fonts) on demand",
    ]

    def __init__(self, timestamp_button: Optional[TimestampButton] = None) -> None:
        self._ts = timestamp_button or TimestampButton()
        self._synthesizer = MusicTrackSynthesizer()
        self._ad_jobs: List[AdCreationJob] = []
        self._cinematic_projects: List[CinematicProject] = []

    # ------------------------------------------------------------------
    # Phase 1: Foundation — Ad creation
    # ------------------------------------------------------------------

    def create_ad(
        self,
        business_name: str,
        product: str,
        platform: str = "tiktok",
        include_music: bool = True,
        genre: str = "pop",
    ) -> AdCreationJob:
        """
        Orchestrate an end-to-end ad creation pipeline:
        script → voiceover → video → music overlay.
        """
        if platform not in self.SUPPORTED_PLATFORMS:
            raise ValueError(f"Platform '{platform}' not supported.")

        job_id = str(uuid.uuid4())[:8]

        # Simulate script generation
        script = (
            f"Introducing {product} by {business_name}. "
            "Experience the future of AI-powered creativity. Try it today!"
        )

        # Simulate voiceover reference
        voiceover_ref = f"voice:{job_id}"

        # Simulate video reference
        video_ref = f"video:{platform}:{job_id}"

        # Optionally attach a generated music track
        music_ref = ""
        if include_music:
            track = self._synthesizer.generate(genre=genre, tempo=120)
            music_ref = track["track_ref"]

        job = AdCreationJob(
            job_id=job_id,
            business_name=business_name,
            product=product,
            platform=platform,
            script=script,
            voiceover_ref=voiceover_ref,
            video_ref=video_ref,
            music_ref=music_ref,
            status="completed",
        )
        self._ad_jobs.append(job)
        self._ts.stamp(
            event="ad_created",
            detail=f"business={business_name} platform={platform}",
            bot=self.name,
        )
        return job

    # ------------------------------------------------------------------
    # Phase 1: Foundation — Cinematic production
    # ------------------------------------------------------------------

    def create_cinematic_project(
        self,
        title: str,
        genre: str,
        synopsis: str,
    ) -> CinematicProject:
        """
        Start a cinematic production project with script and trailer stubs.
        """
        if genre not in self.SUPPORTED_GENRES:
            raise ValueError(f"Genre '{genre}' not supported. Choose from: {self.SUPPORTED_GENRES}")

        project_id = str(uuid.uuid4())[:8]
        project = CinematicProject(
            project_id=project_id,
            title=title,
            genre=genre,
            synopsis=synopsis,
            script_ref=f"script:{project_id}",
            trailer_ref=f"trailer:{project_id}",
            status="in_production",
        )
        self._cinematic_projects.append(project)
        self._ts.stamp(
            event="cinematic_project_created",
            detail=f"title={title} genre={genre}",
            bot=self.name,
        )
        return project

    def list_ad_jobs(self) -> List[Dict[str, Any]]:
        """Return all ad creation jobs."""
        return [j.to_dict() for j in self._ad_jobs]

    def list_cinematic_projects(self) -> List[Dict[str, Any]]:
        """Return all cinematic projects."""
        return [p.to_dict() for p in self._cinematic_projects]

    # ------------------------------------------------------------------
    # Phase 2: Placeholders & ideation
    # ------------------------------------------------------------------

    def generate_placeholders(self) -> List[str]:
        """Return scaffold template names for future creative bot categories."""
        self._ts.stamp(
            event="creative_placeholders_generated",
            detail=f"{len(self.PLACEHOLDER_TEMPLATES)} templates",
            bot=self.name,
        )
        return list(self.PLACEHOLDER_TEMPLATES)

    def log_bot_ideas(self, log_path: str = "bot_ideas_log.txt") -> None:
        """Append creative-domain bot ideas to bot_ideas_log.txt."""
        append_bot_ideas(log_path, self.name, self.BOT_IDEAS)
        self._ts.stamp(event="bot_ideas_logged", detail=f"section={self.name}", bot=self.name)

    # ------------------------------------------------------------------
    # Unified run()
    # ------------------------------------------------------------------

    def run(self, task: dict | None = None) -> dict:
        """Execute the full builder lifecycle for the creative studio."""
        task = task or {}

        # Phase 1 — create sample ad and cinematic project
        ad_job = self.create_ad(
            business_name=task.get("business_name", "DreamCo Technologies"),
            product=task.get("product", "DreamMimic AI Suite"),
            platform=task.get("platform", "youtube"),
            include_music=task.get("include_music", True),
        )
        cinema_project = self.create_cinematic_project(
            title=task.get("film_title", "The DreamCo Chronicles"),
            genre=task.get("film_genre", "sci-fi"),
            synopsis=task.get(
                "synopsis",
                "A visionary AI company transforms human creativity at global scale.",
            ),
        )

        # Phase 2
        placeholders = self.generate_placeholders()
        self.log_bot_ideas(task.get("ideas_log", "bot_ideas_log.txt"))

        return {
            "status": "success",
            "bot": self.name,
            "ad_job": ad_job.to_dict(),
            "cinematic_project": cinema_project.to_dict(),
            "placeholders": placeholders,
        }
