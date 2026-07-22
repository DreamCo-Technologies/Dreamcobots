from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dreamco_platform.creative import (
    BuddyCreativeStudio,
    ConsentEvidence,
    CreativeBrief,
    CreativeStudioError,
    ProjectType,
)


def consent(**overrides) -> ConsentEvidence:
    values = {
        "owner_user_id": "owner-1",
        "subject_user_id": "owner-1",
        "owner_is_subject": True,
        "adult_confirmed": True,
        "voice_use_approved": True,
        "likeness_use_approved": True,
        "synthetic_media_label_approved": True,
    }
    values.update(overrides)
    return ConsentEvidence(**values)


def brief(project_type: ProjectType = ProjectType.SCHOOL_SIMULATION, **overrides) -> CreativeBrief:
    values = {
        "title": "Fraction Quest",
        "project_type": project_type,
        "objective": "Teach learners to compare fractions through a playable kitchen challenge.",
        "subject": "fraction comparison",
        "audience": "ages 9 to 11",
    }
    values.update(overrides)
    return CreativeBrief(**values)


class BuddyCreativeStudioTests(unittest.TestCase):
    def test_every_creative_route_is_a_real_fleet_profile(self):
        fleet_slugs = {
            bot["slug"]
            for path in (ROOT / "App_bots").glob("*.json")
            for bot in json.loads(path.read_text(encoding="utf-8"))["bots"]
        }
        routes = [
            *BuddyCreativeStudio.COMMON_ROUTES,
            *(route for group in BuddyCreativeStudio.TYPE_ROUTES.values() for route in group),
            {"bot": "adaptive-learning"},
        ]
        missing = sorted({route["bot"] for route in routes} - fleet_slugs)
        self.assertEqual(missing, [])

    def test_supports_governed_game_learning_and_media_tracks(self):
        self.assertEqual(
            {item.value for item in ProjectType},
            {
                "game",
                "school_simulation",
                "parent_learning_video",
                "music_video",
                "biography",
                "commercial",
                "college_course",
            },
        )

    def test_creates_biography_and_commercial_rights_workflows(self):
        biography = BuddyCreativeStudio().create_project(
            brief(ProjectType.BIOGRAPHY, title="My Story", objective="Create a sourced personal history for my family.")
        )
        commercial = BuddyCreativeStudio().create_project(
            brief(ProjectType.COMMERCIAL, title="Launch Story", objective="Create a truthful product commercial with approved claims.")
        )
        self.assertIn("source_log", biography.deliverables)
        self.assertIn("claim_substantiation", commercial.deliverables)

    def test_creates_local_first_school_simulation_packet(self):
        project = BuddyCreativeStudio().create_project(brief())
        self.assertEqual(project.status, "planned")
        self.assertEqual(project.sandbox["network_default"], "off")
        self.assertFalse(project.audit["live_external_action_taken"])
        self.assertIn("teacher_guide", project.deliverables)

    def test_voice_clone_requires_consent_and_sample(self):
        with self.assertRaisesRegex(CreativeStudioError, "voice sample"):
            BuddyCreativeStudio().create_project(brief(use_voice_clone=True))
        with self.assertRaisesRegex(CreativeStudioError, "Consent evidence"):
            BuddyCreativeStudio().create_project(
                brief(use_voice_clone=True, voice_sample_ref="local:voice-sample")
            )

    def test_media_workflow_blocks_minor_and_non_owner_cloning(self):
        with self.assertRaisesRegex(CreativeStudioError, "minors"):
            BuddyCreativeStudio().create_project(
                brief(
                    use_voice_clone=True,
                    voice_sample_ref="local:voice-sample",
                    consent=consent(adult_confirmed=False),
                )
            )
        with self.assertRaisesRegex(CreativeStudioError, "self-owned"):
            BuddyCreativeStudio().create_project(
                brief(
                    use_image_avatar=True,
                    image_sample_ref="local:image-sample",
                    consent=consent(subject_user_id="someone-else", owner_is_subject=False),
                )
            )

    def test_approved_media_is_pending_until_an_engine_returns_assets(self):
        project = BuddyCreativeStudio().create_project(
            brief(
                use_voice_clone=True,
                use_image_avatar=True,
                voice_sample_ref="local:voice-sample",
                image_sample_ref="local:image-sample",
                consent=consent(),
            )
        )
        self.assertEqual(project.media["voice"]["status"], "consent_verified_pending_render")
        result = BuddyCreativeStudio().render_media(
            project,
            narration="Welcome to Fraction Quest.",
            avatar_prompt="Friendly instructor in a learning kitchen.",
            renderer=None,
        )
        self.assertEqual(result.status, "media_engine_configuration_required")
        self.assertEqual(result.media["renderer"]["status"], "not_configured")

    def test_revoked_consent_blocks_render_and_export(self):
        evidence = consent()
        studio = BuddyCreativeStudio()
        project = studio.create_project(
            brief(
                use_voice_clone=True,
                voice_sample_ref="local:voice-sample",
                consent=evidence,
            )
        )
        evidence.revoke()
        with self.assertRaisesRegex(CreativeStudioError, "revoked"):
            studio.render_media(
                project,
                narration="This should not render.",
                avatar_prompt="",
                renderer=None,
            )
        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaisesRegex(CreativeStudioError, "revoked"):
                studio.write_project_packet(project, Path(temp_dir))

    def test_renderer_completion_and_project_scaffold(self):
        class Renderer:
            name = "test-local-engine"

            def render_voice(self, **kwargs):
                return f"asset:voice:{kwargs['project_id']}"

            def render_avatar(self, **kwargs):
                return f"asset:avatar:{kwargs['project_id']}"

        studio = BuddyCreativeStudio()
        project = studio.create_project(
            brief(
                ProjectType.PARENT_LEARNING_VIDEO,
                use_voice_clone=True,
                use_image_avatar=True,
                voice_sample_ref="vault:voice-sample",
                image_sample_ref="vault:image-sample",
                consent=consent(),
            )
        )
        studio.render_media(
            project,
            narration="Practice this together.",
            avatar_prompt="The adult creator presents the lesson.",
            renderer=Renderer(),
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir)
            files = studio.write_project_packet(project, output)
            self.assertEqual(project.status, "ready_for_sandbox")
            self.assertEqual(len(files), 4)
            manifest = json.loads((output / "project.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["media"]["renderer"]["status"], "rendered")
            self.assertNotIn("owner_user_id", manifest["brief"]["consent"])
            self.assertEqual(manifest["brief"]["voice_sample_ref"], "redacted")
            self.assertIn("AI-assisted media", (output / "index.html").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
