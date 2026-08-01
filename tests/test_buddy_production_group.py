from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dreamco_platform.creative import (
    ActorMode,
    BuddyProductionGroup,
    ConsentEvidence,
    CreativeStudioError,
    ModelSource,
    ProductionBrief,
    ProductionFormat,
    SimulationBrief,
    SimulationDomain,
    SyntheticActorBrief,
)


def owner_consent(**overrides) -> ConsentEvidence:
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


class BuddyProductionGroupTests(unittest.TestCase):
    def test_every_department_and_simulation_route_uses_a_real_fleet_bot(self):
        fleet_slugs = {
            bot["slug"]
            for path in (ROOT / "App_bots").glob("*.json")
            for bot in json.loads(path.read_text(encoding="utf-8"))["bots"]
        }
        group = BuddyProductionGroup()
        department_bots = {
            bot
            for department in group.production["departments"]
            for bot in [department["lead_bot"], *department["support_bots"]]
        }
        simulation = group.build_simulation_plan(
            SimulationBrief(
                title="Garage Variant Lab",
                objective="Compare approved paint and wheel variants against a measured owner vehicle model.",
                audience="Adult vehicle owner",
                domain=SimulationDomain.VEHICLE_CUSTOMIZATION,
            )
        )
        route_bots = {route["bot"] for route in simulation["routes"]}
        self.assertEqual(sorted((department_bots | route_bots) - fleet_slugs), [])

    def test_original_actor_cannot_reference_a_real_person(self):
        with self.assertRaisesRegex(CreativeStudioError, "cannot be based"):
            BuddyProductionGroup().build_actor_plan(
                SyntheticActorBrief(
                    name="Nova",
                    project_title="New Horizon",
                    character_description="An original explorer with a distinct fictional history and visual design.",
                    real_person_reference=True,
                )
            )

    def test_owner_digital_double_requires_active_adult_consent(self):
        plan = BuddyProductionGroup().build_actor_plan(
            SyntheticActorBrief(
                name="Owner Presenter",
                project_title="Workshop Story",
                character_description="The adult owner presents a clearly labeled educational workshop sequence.",
                mode=ActorMode.OWNER_DIGITAL_DOUBLE,
                use_voice=True,
                use_likeness=True,
                source_media_ref="vault:owner-media",
                adult_confirmed=True,
                real_person_reference=True,
                consent=owner_consent(),
            )
        )
        self.assertEqual(plan["render_state"], "renderer_configuration_required")
        self.assertTrue(plan["evidence"]["owner_consent_fingerprint"])
        self.assertFalse(plan["evidence"]["raw_media_stored"])

    def test_simulation_requires_model_rights_and_builds_game_conversion(self):
        group = BuddyProductionGroup()
        with self.assertRaisesRegex(CreativeStudioError, "ownership or license"):
            group.build_simulation_plan(
                SimulationBrief(
                    title="House Lab",
                    objective="Compare a room addition against a measured owner-authorized building model.",
                    audience="Home owner",
                    domain=SimulationDomain.BUILDING_DESIGN,
                    model_source=ModelSource.OWNER_UPLOAD,
                    model_ref="vault:house-model",
                )
            )
        plan = group.build_simulation_plan(
            SimulationBrief(
                title="House Lab",
                objective="Compare a room addition against a measured owner-authorized building model.",
                audience="Home owner",
                domain=SimulationDomain.BUILDING_DESIGN,
                model_source=ModelSource.OWNER_UPLOAD,
                model_ref="vault:house-model",
                rights_ref="receipt:house-owner",
                modifications=("blue exterior paint", "accessible side entrance", "rear room addition"),
                convert_to_game=True,
            )
        )
        self.assertEqual(plan["status"], "simulation_packet_ready")
        self.assertEqual(plan["brief"]["model_ref"], "redacted")
        self.assertEqual(plan["game_conversion"]["status"], "game_design_ready")
        self.assertIn("licensed professional review", plan["domain_review"])

    def test_professional_production_builds_cast_timeline_editing_and_delivery_plan(self):
        plan = BuddyProductionGroup().build_production_plan(
            ProductionBrief(
                title="City of Tomorrow",
                objective="Build an original animated series pilot with a reusable cast and professional delivery packet.",
                audience="Family streaming audiences",
                production_format=ProductionFormat.ANIMATED_SERIES,
                duration_minutes=24,
                target_platforms=("web", "streaming", "television"),
                cast=(
                    SyntheticActorBrief(
                        name="Nova",
                        project_title="City of Tomorrow",
                        character_description="An original young-adult engineer with a fictional history, visual design, and performance arc.",
                    ),
                    SyntheticActorBrief(
                        name="Beacon",
                        project_title="City of Tomorrow",
                        character_description="An original robotic guide with a distinct silhouette, movement language, and supporting role.",
                    ),
                ),
                commercial_use=True,
            )
        )
        self.assertEqual(plan["status"], "production_packet_ready")
        self.assertEqual(len(plan["cast"]), 2)
        self.assertEqual(plan["timeline"]["interchange_contract"], "OpenTimelineIO-compatible timeline manifest")
        self.assertGreaterEqual(len(plan["editing_workspaces"]), 8)
        self.assertEqual({tool["reference"] for tool in plan["toolchain"]}, {
            "OpenTimelineIO", "FFmpeg", "Blender", "OBS Studio WebSocket"
        })
        self.assertFalse(plan["release"]["rendered_assets_exist"])
        self.assertFalse(plan["release"]["platform_submission_or_publish_taken"])

    def test_live_show_requires_rehearsal_adapter_and_fresh_go_live_approval(self):
        plan = BuddyProductionGroup().build_production_plan(
            ProductionBrief(
                title="Buddy Live Workshop",
                objective="Prepare a moderated live workshop with private rehearsal, safe scene controls, and clips.",
                audience="Authorized social channel followers",
                production_format=ProductionFormat.SOCIAL_LIVE_SHOW,
                duration_minutes=45,
                target_platforms=("owner_social_channel",),
                live_mode=True,
            )
        )
        self.assertTrue(plan["live"]["requested"])
        self.assertTrue(plan["live"]["go_live_requires_fresh_owner_approval"])
        self.assertFalse(plan["live"]["autonomous_broadcast_started"])
        self.assertFalse(plan["live"]["credentials_stored"])

    def test_live_mode_is_not_available_for_a_non_live_production(self):
        with self.assertRaisesRegex(CreativeStudioError, "only for a social live show"):
            BuddyProductionGroup().build_production_plan(
                ProductionBrief(
                    title="Feature Plan",
                    objective="Prepare a feature film packet with a complete editorial and delivery workflow.",
                    audience="Film audiences",
                    production_format=ProductionFormat.FEATURE_FILM,
                    live_mode=True,
                )
            )


if __name__ == "__main__":
    unittest.main()
