import importlib
import tempfile
import unittest
from pathlib import Path

rights = importlib.import_module("stages.10_media_studio.rights_gate")
director = importlib.import_module("stages.10_media_studio.director")
render = importlib.import_module("stages.10_media_studio.render_orchestrator")
quality = importlib.import_module("stages.10_media_studio.quality_gate")
assets = importlib.import_module("stages.10_media_studio.asset_manager")


class MediaFoundryTests(unittest.TestCase):
    def test_unknown_asset_rights_fail_closed(self):
        decision = rights.authorize_asset({"asset_id": "unknown", "review_status": "unreviewed"}, "display")
        self.assertFalse(decision.allowed)
        self.assertTrue(decision.reasons)

    def test_asset_requires_explicit_use_and_commercial_permission(self):
        record = {
            "asset_id": "dreamco-original-logo",
            "ownership_class": "dreamco_owned",
            "review_status": "approved",
            "permissions": {"display": True, "commercial_use": True},
        }
        self.assertTrue(rights.authorize_asset(record, "display", commercial=True).allowed)
        self.assertFalse(rights.authorize_asset(record, "train", commercial=True).allowed)

    def test_model_code_license_does_not_substitute_for_weights_and_dependencies(self):
        model = {
            "model_id": "candidate",
            "status": "approved",
            "code_license_status": "verified",
            "weights_license_status": "unverified",
            "dependencies_reviewed": False,
            "commercial_use_allowed": True,
            "training_allowed": False,
        }
        decision = rights.authorize_model(model, commercial=True)
        self.assertFalse(decision.allowed)
        self.assertTrue(any("weights" in reason for reason in decision.reasons))
        self.assertTrue(any("dependencies" in reason for reason in decision.reasons))

    def test_director_builds_plan_only_packet_with_verified_rights(self):
        packet = director.build_production_packet(
            {"title": "DreamCo Pilot", "objective": "Create an original channel trailer", "audience": "general"},
            [{"shot_id": "shot-001", "description": "Original DreamCo logo appears over a dark studio stage",
              "duration_seconds": 5, "asset_ids": ["logo"]}],
            assets=[{"asset_id": "logo", "ownership_class": "dreamco_owned", "review_status": "approved",
                     "permissions": {"display": True, "commercial_use": True}}],
            commercial=True,
        )
        self.assertEqual(packet["status"], "planned_not_rendered")
        self.assertEqual(packet["timeline"]["duration_seconds"], 5)
        self.assertEqual(packet["rendered_assets"], [])

    def test_missing_asset_rights_record_blocks_packet(self):
        with self.assertRaises(PermissionError):
            director.build_production_packet(
                {"title": "DreamCo Pilot", "objective": "Create an original channel trailer"},
                [{"shot_id": "shot-001", "description": "A detailed visual scene with a new character",
                  "asset_ids": ["unreviewed"]}],
            )

    def test_no_renderer_never_claims_rendered(self):
        result = render.execute_render({"status": "planned_not_rendered"})
        self.assertEqual(result["render_status"], "planned_not_rendered")
        self.assertIsNone(result["renderer_id"])

    def test_quality_gate_checks_real_file_hash_and_shot_provenance(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = root / "shot.mp4"
            output.write_bytes(b"sample render bytes")
            import hashlib
            digest = hashlib.sha256(output.read_bytes()).hexdigest()
            passed = quality.verify_render_outputs(
                [{"relative_path": "shot.mp4", "sha256": digest, "shot_id": "shot-001"}], root
            )
            self.assertTrue(passed["passed"])
            failed = quality.verify_render_outputs(
                [{"relative_path": "shot.mp4", "sha256": "0" * 64, "shot_id": "shot-001"}], root
            )
            self.assertFalse(failed["passed"])

    def test_asset_manifest_rejects_path_traversal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaises(ValueError):
                assets.write_asset_manifest(root, [{"relative_path": "../secret"}], root / "manifest.json")


if __name__ == "__main__":
    unittest.main()
