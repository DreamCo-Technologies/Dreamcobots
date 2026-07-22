"""Rights-aware artist development and original music production packets."""

from __future__ import annotations

import hashlib
import re
from dataclasses import asdict, dataclass
from typing import Any


class MusicStudioError(ValueError):
    """Raised when music sources or release claims lack clear rights."""


@dataclass(frozen=True)
class ReferenceTrack:
    title: str
    source_reference: str
    rights_basis: str
    allowed_uses: tuple[str, ...]

    def validate(self) -> None:
        if len(self.title.strip()) < 2 or not re.fullmatch(
            r"[A-Za-z][A-Za-z0-9_.:/-]{2,159}", self.source_reference
        ):
            raise MusicStudioError("A title and durable source reference are required.")
        if self.rights_basis not in {
            "user_owned", "public_domain", "cc0", "licensed_for_analysis"
        }:
            raise MusicStudioError("Music references need an approved rights basis.")
        if "model_training" in self.allowed_uses and self.rights_basis == "licensed_for_analysis":
            raise MusicStudioError("Analysis permission does not grant model-training rights.")


@dataclass(frozen=True)
class ArtistBrief:
    owner_user_id: str
    artist_name: str
    creative_direction: str
    audience: str
    goals: tuple[str, ...]

    def validate(self) -> None:
        if not re.fullmatch(r"[A-Za-z0-9_.:-]{2,80}", self.owner_user_id):
            raise MusicStudioError("A stable owner id is required.")
        if len(self.artist_name.strip()) < 2 or len(self.creative_direction.strip()) < 20:
            raise MusicStudioError("Artist name and a detailed creative direction are required.")
        if not self.audience.strip() or not self.goals:
            raise MusicStudioError("Audience and at least one artist goal are required.")


class BuddyMusicArtistStudio:
    """Build an artist-development packet without copying protected recordings."""

    def create_plan(
        self,
        brief: ArtistBrief,
        references: tuple[ReferenceTrack, ...] = (),
    ) -> dict[str, Any]:
        brief.validate()
        for reference in references:
            reference.validate()
        fingerprint = hashlib.sha256(
            f"{brief.owner_user_id}:{brief.artist_name}:{brief.creative_direction}".encode("utf-8")
        ).hexdigest()[:20]
        return {
            "schema": "dreamco.music_artist_plan.v1",
            "artist_plan_id": f"artist-{fingerprint}",
            "brief": asdict(brief),
            "reference_manifest": [asdict(reference) for reference in references],
            "study_boundary": "analyze only user-owned, public-domain, CC0, or specifically licensed material",
            "production_workflow": [
                "define an original artistic identity and audience promise",
                "build an original song brief, structure, arrangement, and performance plan",
                "record sources, collaborators, samples, splits, and licenses",
                "produce demo, mix review, mastering checklist, artwork, and captions",
                "run similarity, rights, accessibility, and release-readiness reviews",
                "test audience hypotheses with owner-approved, non-deceptive experiments",
                "prepare distributor metadata and require owner approval before release",
            ],
            "deliverables": [
                "artist_identity", "original_repertoire_plan", "song_production_packet",
                "rights_and_split_manifest", "release_calendar", "audience_experiment_log",
            ],
            "copyrighted_catalog_scraped": False,
            "voice_or_likeness_requires_separate_consent": True,
            "automatic_release": False,
        }
