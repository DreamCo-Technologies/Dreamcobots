import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("buddy_bootcamp_generator", ROOT / "tools/generate_buddy_bootcamp_challenges.py")
generator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(generator)


class BuddyBootcampGeneratorTests(unittest.TestCase):
    def setUp(self):
        self.rights = {
            "source_id": "test-source", "license_id": "test-license",
            "commercial_use_approved": True, "training_use_approved": True,
            "evaluation_only": False, "privacy_review_status": "APPROVED",
            "review_status": "APPROVED", "reviewer": "test-reviewer",
            "reviewed_at": "2026-11-27T00:00:00Z", "evidence_uri": "review://test"
        }
        self.row = {"task_id": "T-1", "task_statement": "Prepare a compliant work plan.",
                    "occupation_code": "00-0000.00", "occupation_title": "Test occupation"}

    def test_rights_gate_accepts_explicit_approval(self):
        generator.validate_rights(self.rights, "test-source", "test-license")

    def test_rights_gate_rejects_unapproved_training(self):
        rights = dict(self.rights, training_use_approved=False)
        with self.assertRaisesRegex(ValueError, "training_use_approved"):
            generator.validate_rights(rights, "test-source", "test-license")

    def test_rights_gate_rejects_holdout(self):
        rights = dict(self.rights, evaluation_only=True)
        with self.assertRaisesRegex(ValueError, "evaluation_only"):
            generator.validate_rights(rights, "test-source", "test-license")

    def test_challenge_has_schema_and_source_provenance(self):
        division = {"id": 11, "slug": "dreamcodelab", "name": "DreamCodeLab"}
        challenge = generator.build_challenge(self.row, division, self.rights,
                                              "test-source", "test-license", 1)
        self.assertEqual(challenge["division"]["id"], 11)
        self.assertEqual(challenge["division"]["slug"], "dreamcodelab")
        self.assertEqual(challenge["source"]["source_task_id"], "T-1")
        self.assertEqual(challenge["response_schema"]["type"], "object")
        self.assertEqual(challenge["provenance"]["holdout_split"], "NEVER_GENERATE_FROM_THIS_TOOL")

    def test_manifest_covers_all_canonical_divisions_and_100_resources(self):
        manifest = json.loads((ROOT / "config/buddy-bootcamp-100-resource-manifest.json").read_text())
        registry = json.loads((ROOT / "config/masterbot-65-registry.json").read_text())
        self.assertEqual(manifest["resource_count"], 100)
        self.assertEqual(len(manifest["resources"]), 100)
        self.assertEqual(len(manifest["canonical_divisions"]), 55)
        self.assertEqual(manifest["canonical_division_count"], 55)
        self.assertEqual(len(manifest["masterbot_learning_lanes"]), 65)
        self.assertEqual(manifest["masterbot_learning_lane_count"], 65)
        self.assertEqual(len(registry["divisions"]), 65)
        self.assertEqual(manifest["division_coverage"]["uncovered_ids"], [])
        self.assertEqual(set(manifest["division_coverage"]["covered_ids"]),
                         {item["id"] for item in manifest["canonical_divisions"]})
        self.assertEqual(manifest["masterbot_lane_coverage"]["uncovered_ids"], [])
        self.assertEqual(set(manifest["masterbot_lane_coverage"]["covered_ids"]),
                         {item["id"] for item in registry["divisions"]})
        self.assertTrue(all(item["domain_division_ids"] for item in manifest["resources"]))
        self.assertTrue(all(item["masterbot_lane_ids"] for item in manifest["resources"]))
        valid_domain_ids = {item["id"] for item in manifest["canonical_divisions"]}
        valid_lane_ids = {item["id"] for item in registry["divisions"]}
        self.assertTrue(all(set(item["domain_division_ids"]) <= valid_domain_ids
                            for item in manifest["resources"]))
        self.assertTrue(all(set(item["masterbot_lane_ids"]) <= valid_lane_ids
                            for item in manifest["resources"]))
        layer_counts = {}
        for item in manifest["resources"]:
            layer_counts[item["layer_id"]] = layer_counts.get(item["layer_id"], 0) + 1
        self.assertEqual(len(layer_counts), 10)
        self.assertEqual(set(layer_counts.values()), {10})


if __name__ == "__main__":
    unittest.main()
