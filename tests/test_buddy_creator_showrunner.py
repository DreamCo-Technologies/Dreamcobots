from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dreamco_platform.creative import (
    BuddyCreatorShowrunner,
    CharacterRightsMode,
    CreatorFormat,
    CreatorShowBrief,
    CreativeStudioError,
    EpisodeBrief,
    ShowCharacter,
)


def character(character_id: str = "guide", name: str = "Nova Guide", **overrides) -> ShowCharacter:
    values = {
        "character_id": character_id,
        "name": name,
        "role": "Host and learning guide",
        "description": "An original patient guide with a distinct silhouette, history, and speaking style.",
        "personality_traits": {"warmth": 0.9, "curiosity": 0.8, "energy": 0.7},
        "voice_direction": "Clear, conversational, and encouraging.",
        "visual_direction": "High-contrast wardrobe and consistent blue notebook.",
        "continuity_facts": ("Carries a blue notebook", "Asks one reflection question per lesson"),
    }
    values.update(overrides)
    return ShowCharacter(**values)


def show(format: CreatorFormat = CreatorFormat.YOUTUBE_CHANNEL, **overrides) -> CreatorShowBrief:
    values = {
        "title": "Build It With Buddy",
        "format": format,
        "premise": "Turn practical questions into short demonstrations, learning checks, and reusable projects.",
        "audience": "Families, students, and first-time creators",
        "content_pillars": ("build", "learn", "practice"),
        "platforms": ("youtube_long", "youtube_short", "classroom"),
        "characters": (character(),),
        "season_episode_count": 12,
    }
    values.update(overrides)
    return CreatorShowBrief(**values)


class BuddyCreatorShowrunnerTests(unittest.TestCase):
    def test_every_showrunner_route_resolves_to_a_registered_bot(self):
        registered = {
            bot["identity"]["slug"]
            for bot in json.loads((ROOT / "config/master_bot_registry.json").read_text(encoding="utf-8"))["bots"]
        }
        registry = json.loads((ROOT / "config/buddy-creator-showrunner.json").read_text(encoding="utf-8"))
        routed = {bot for profile in registry["formats"] for bot in profile["routes"]}
        self.assertEqual(sorted(routed - registered), [])

    def test_builds_youtube_show_bible_character_library_and_calendar(self):
        plan = BuddyCreatorShowrunner().build_show_plan(show())
        self.assertEqual(plan["status"], "show_bible_and_season_plan_ready")
        self.assertEqual(plan["character_library"]["character_count"], 1)
        self.assertIsNone(plan["character_library"]["application_character_limit"])
        self.assertEqual(len(plan["calendar"]["episodes"]), 12)
        self.assertFalse(plan["release"]["channel_connected"])
        self.assertFalse(plan["release"]["content_published"])
        self.assertTrue(plan["release"]["publish_requires_exact_owner_approval"])

    def test_open_ended_library_uses_bounded_episode_units(self):
        characters = tuple(character(f"character-{index}", f"Character {index}") for index in range(130))
        brief = show(characters=characters)
        plan = BuddyCreatorShowrunner().build_show_plan(brief)
        self.assertEqual(plan["character_library"]["character_count"], 130)
        self.assertEqual(plan["character_library"]["active_characters_per_production_unit"], 100)
        with self.assertRaisesRegex(CreativeStudioError, "at most 100"):
            BuddyCreatorShowrunner().build_episode_plan(
                brief,
                EpisodeBrief(
                    episode_number=1,
                    title="Everyone Arrives",
                    objective="Introduce the complete cast through a controlled production exercise.",
                    active_character_ids=tuple(item.character_id for item in characters[:101]),
                    content_pillar="build",
                ),
            )

    def test_episode_plan_uses_known_active_characters(self):
        brief = show()
        episode = BuddyCreatorShowrunner().build_episode_plan(
            brief,
            EpisodeBrief(
                episode_number=2,
                title="Fraction Kitchen",
                objective="Teach equivalent fractions through a repeatable kitchen simulation.",
                active_character_ids=("guide",),
                content_pillar="learn",
            ),
        )
        self.assertEqual(episode["status"], "episode_packet_ready")
        self.assertEqual(episode["production_unit"]["active_character_count"], 1)
        self.assertEqual(episode["render_state"], "renderer_configuration_required")

    def test_learning_and_simulation_series_require_measurable_objectives(self):
        for format in (CreatorFormat.LEARNING_SERIES, CreatorFormat.SIMULATION_SERIES):
            with self.subTest(format=format.value):
                with self.assertRaisesRegex(CreativeStudioError, "learning objective"):
                    BuddyCreatorShowrunner().build_show_plan(show(format))
                plan = BuddyCreatorShowrunner().build_show_plan(
                    show(format, learning_objectives=("Learners complete three safe practice decisions.",))
                )
                self.assertEqual(plan["show"]["format"], format.value)

    def test_real_person_character_requires_adult_rights_receipt(self):
        with self.assertRaisesRegex(CreativeStudioError, "rights receipt"):
            BuddyCreatorShowrunner().build_show_plan(
                show(
                    characters=(
                        character(
                            rights_mode=CharacterRightsMode.OWNER_DIGITAL_DOUBLE,
                            adult_confirmed=True,
                        ),
                    )
                )
            )
        plan = BuddyCreatorShowrunner().build_show_plan(
            show(
                characters=(
                    character(
                        rights_mode=CharacterRightsMode.OWNER_DIGITAL_DOUBLE,
                        adult_confirmed=True,
                        rights_receipt_ref="owner-vault:consent-1",
                    ),
                )
            )
        )
        record = plan["character_library"]["characters"][0]
        self.assertTrue(record["rights_receipt_sha256"])
        self.assertNotIn("rights_receipt_ref", record)


if __name__ == "__main__":
    unittest.main()
