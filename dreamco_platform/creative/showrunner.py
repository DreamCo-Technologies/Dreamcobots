"""Reusable character, show, channel, and episode planning for Buddy Studio."""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from .studio import CreativeStudioError


ROOT = Path(__file__).resolve().parents[2]


class CreatorFormat(str, Enum):
    YOUTUBE_CHANNEL = "youtube_channel"
    SOCIAL_CONTENT_SERIES = "social_content_series"
    LEARNING_SERIES = "learning_series"
    SIMULATION_SERIES = "simulation_series"
    MUSIC_PERFORMANCE_SERIES = "music_performance_series"
    FICTION_OR_VARIETY_SHOW = "fiction_or_variety_show"


class CharacterRightsMode(str, Enum):
    ORIGINAL_SYNTHETIC = "original_synthetic"
    COMPANY_MASCOT = "company_mascot"
    OWNER_DIGITAL_DOUBLE = "owner_digital_double"
    LICENSED_ADULT_PERFORMER = "licensed_adult_performer"


@dataclass(frozen=True)
class ShowCharacter:
    character_id: str
    name: str
    role: str
    description: str
    personality_traits: dict[str, float]
    voice_direction: str = ""
    visual_direction: str = ""
    continuity_facts: tuple[str, ...] = ()
    rights_mode: CharacterRightsMode = CharacterRightsMode.ORIGINAL_SYNTHETIC
    rights_receipt_ref: str = ""
    adult_confirmed: bool = False
    active: bool = True

    def validate(self) -> None:
        if not self.character_id.strip() or len(self.name.strip()) < 2 or len(self.role.strip()) < 2:
            raise CreativeStudioError("Every show character needs a stable id, production name, and role.")
        if len(self.description.strip()) < 20:
            raise CreativeStudioError("Every show character needs an original description of at least 20 characters.")
        if not self.personality_traits or any(
            not isinstance(value, (int, float)) or value < 0 or value > 1
            for value in self.personality_traits.values()
        ):
            raise CreativeStudioError("Character personality traits must be between zero and one.")
        if len(self.continuity_facts) > 100 or any(len(item.strip()) < 2 for item in self.continuity_facts):
            raise CreativeStudioError("Use up to 100 clearly named continuity facts per character.")
        if self.rights_mode in {
            CharacterRightsMode.OWNER_DIGITAL_DOUBLE,
            CharacterRightsMode.LICENSED_ADULT_PERFORMER,
        }:
            if not self.adult_confirmed or not self.rights_receipt_ref.strip():
                raise CreativeStudioError("Real-person show characters require an adult confirmation and rights receipt.")
        elif self.rights_receipt_ref:
            raise CreativeStudioError("Original characters and company mascots cannot reference performer media rights.")


@dataclass(frozen=True)
class CreatorShowBrief:
    title: str
    format: CreatorFormat
    premise: str
    audience: str
    content_pillars: tuple[str, ...]
    platforms: tuple[str, ...] = ("youtube_long", "youtube_short")
    cadence: str = "weekly"
    season_episode_count: int = 8
    characters: tuple[ShowCharacter, ...] = ()
    learning_objectives: tuple[str, ...] = ()
    made_for_children: bool = False
    commercial_use: bool = False

    def validate(self, registry: dict[str, Any]) -> None:
        if len(self.title.strip()) < 3 or len(self.premise.strip()) < 20 or not self.audience.strip():
            raise CreativeStudioError("A show title, detailed premise, and audience are required.")
        if not 1 <= self.season_episode_count <= 1000:
            raise CreativeStudioError("A season must contain between one and 1,000 planned episodes.")
        if not 1 <= len(self.content_pillars) <= 20 or any(len(item.strip()) < 2 for item in self.content_pillars):
            raise CreativeStudioError("Use between one and 20 clearly named content pillars.")
        cadence_ids = set(registry["content_calendar"]["cadences"])
        if self.cadence not in cadence_ids:
            raise CreativeStudioError("Choose a cadence from the creator registry.")
        platform_ids = {item["id"] for item in registry["platform_profiles"]}
        if not self.platforms or set(self.platforms) - platform_ids:
            raise CreativeStudioError("Every target platform must exist in the creator registry.")
        character_ids = [item.character_id.strip().casefold() for item in self.characters]
        character_names = [item.name.strip().casefold() for item in self.characters]
        if len(character_ids) != len(set(character_ids)) or len(character_names) != len(set(character_names)):
            raise CreativeStudioError("Character ids and production names must be unique within a show.")
        for character in self.characters:
            character.validate()
        if self.format in {CreatorFormat.LEARNING_SERIES, CreatorFormat.SIMULATION_SERIES} and not self.learning_objectives:
            raise CreativeStudioError("Learning and simulation series require at least one measurable learning objective.")


@dataclass(frozen=True)
class EpisodeBrief:
    episode_number: int
    title: str
    objective: str
    active_character_ids: tuple[str, ...]
    content_pillar: str

    def validate(self, show: CreatorShowBrief, active_limit: int) -> None:
        if not 1 <= self.episode_number <= show.season_episode_count:
            raise CreativeStudioError("Episode number must fit inside the planned season.")
        if len(self.title.strip()) < 3 or len(self.objective.strip()) < 15:
            raise CreativeStudioError("An episode title and detailed objective are required.")
        if self.content_pillar not in show.content_pillars:
            raise CreativeStudioError("The episode content pillar must belong to the show bible.")
        known_ids = {item.character_id for item in show.characters if item.active}
        if len(self.active_character_ids) > active_limit:
            raise CreativeStudioError(f"Use at most {active_limit} active characters in one production unit.")
        if set(self.active_character_ids) - known_ids:
            raise CreativeStudioError("Every active episode character must exist and be active in the show library.")


class BuddyCreatorShowrunner:
    """Create local, auditable show and episode packets without publishing."""

    def __init__(self) -> None:
        self.registry = json.loads(
            (ROOT / "config" / "buddy-creator-showrunner.json").read_text(encoding="utf-8")
        )

    def build_show_plan(self, brief: CreatorShowBrief) -> dict[str, Any]:
        brief.validate(self.registry)
        profile = next(item for item in self.registry["formats"] if item["id"] == brief.format.value)
        show_id = f"show-{uuid.uuid4().hex[:12]}"
        characters = [self._character_record(item) for item in brief.characters]
        return {
            "schema": "dreamco.buddy_creator_show_plan.v1",
            "status": "show_bible_and_season_plan_ready",
            "show_id": show_id,
            "show": {
                "title": brief.title.strip(),
                "format": brief.format.value,
                "premise": brief.premise.strip(),
                "audience": brief.audience.strip(),
                "content_pillars": list(brief.content_pillars),
                "platforms": list(dict.fromkeys(brief.platforms)),
                "cadence": brief.cadence,
                "season_episode_count": brief.season_episode_count,
                "learning_objectives": list(brief.learning_objectives),
                "made_for_children": brief.made_for_children,
                "commercial_use_requested": brief.commercial_use,
            },
            "character_library": {
                "characters": characters,
                "character_count": len(characters),
                "application_character_limit": None,
                "active_characters_per_production_unit": self.registry["character_library"]["active_characters_per_production_unit"],
                "scale_strategy": self.registry["character_library"]["scale_strategy"],
                "raw_identity_media_stored": False,
            },
            "routes": [{"bot": bot, "mode": "sandbox_and_draft"} for bot in profile["routes"]],
            "deliverables": profile["deliverables"],
            "lifecycle": self.registry["show_lifecycle"],
            "calendar": {
                "states": self.registry["content_calendar"]["states"],
                "automation_default": self.registry["content_calendar"]["automation_default"],
                "episodes": [
                    {
                        "episode_number": number,
                        "status": "idea",
                        "title": f"Episode {number}",
                        "content_pillar": brief.content_pillars[(number - 1) % len(brief.content_pillars)],
                    }
                    for number in range(1, brief.season_episode_count + 1)
                ],
            },
            "quality_and_safety_gates": self.registry["quality_and_safety_gates"],
            "hard_blocks": self.registry["hard_blocks"],
            "release": {
                "rendered_assets_exist": False,
                "channel_connected": False,
                "content_published": False,
                "publish_requires_exact_owner_approval": True,
            },
            "truth_boundary": self.registry["truth_boundary"],
        }

    def build_episode_plan(
        self,
        show: CreatorShowBrief,
        episode: EpisodeBrief,
    ) -> dict[str, Any]:
        show.validate(self.registry)
        active_limit = self.registry["character_library"]["active_characters_per_production_unit"]
        episode.validate(show, active_limit)
        character_index = {item.character_id: item for item in show.characters}
        active_cast = [self._character_record(character_index[item]) for item in episode.active_character_ids]
        return {
            "schema": "dreamco.buddy_creator_episode_plan.v1",
            "status": "episode_packet_ready",
            "episode": asdict(episode),
            "active_cast": active_cast,
            "production_unit": {
                "active_character_count": len(active_cast),
                "active_character_limit": active_limit,
                "research_required": True,
                "script_required": True,
                "storyboard_required": True,
                "captions_required": True,
                "continuity_review_required": True,
                "learning_review_required": show.format in {CreatorFormat.LEARNING_SERIES, CreatorFormat.SIMULATION_SERIES},
            },
            "render_state": "renderer_configuration_required",
            "publish_state": "authenticated_adapter_and_exact_owner_approval_required",
        }

    @staticmethod
    def _character_record(character: ShowCharacter) -> dict[str, Any]:
        payload = asdict(character)
        payload["rights_mode"] = character.rights_mode.value
        payload["rights_receipt_sha256"] = (
            hashlib.sha256(character.rights_receipt_ref.encode("utf-8")).hexdigest()
            if character.rights_receipt_ref
            else None
        )
        payload.pop("rights_receipt_ref", None)
        return payload
