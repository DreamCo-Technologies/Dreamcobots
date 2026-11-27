"""Contract tests for the first-party Buddy Bootcamp curriculum."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CURRICULUM_PATH = ROOT / "config/dreamco-buddy-bootcamp-curriculum.json"


class BuddyBootcampCurriculumTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.curriculum = json.loads(CURRICULUM_PATH.read_text(encoding="utf-8"))

    def test_schema_and_dreamco_authorship_are_explicit(self):
        self.assertEqual(
            self.curriculum["schema"],
            "dreamco.buddy_first_party_bootcamp_curriculum.v1",
        )
        self.assertEqual(
            self.curriculum["authorship"]["curriculum_owner"], "DreamCo"
        )

    def test_track_ids_are_unique_and_nonempty(self):
        tracks = self.curriculum["tracks"]
        ids = [track["id"] for track in tracks]
        self.assertGreaterEqual(len(tracks), 10)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(ids))

    def test_seven_day_sprint_has_one_gate_per_day(self):
        days = self.curriculum["intensive_seven_day_plan"]
        self.assertEqual([day["day"] for day in days], list(range(1, 8)))
        for day in days:
            self.assertTrue(day["deliverables"])
            self.assertTrue(day["exit_gate"])

    def test_mastery_requires_execution_and_transfer_evidence(self):
        required = self.curriculum["learning_contract"]["required_stages"]
        self.assertIn("sandbox_lab_executed", required)
        self.assertIn("automated_tests_passed", required)
        self.assertIn("unseen_transfer_task_passed", required)
        self.assertIn("capability_registered", required)

    def test_source_permissions_are_not_conflated(self):
        permissions = self.curriculum["authorship"]["permissions"]
        self.assertIn("transcript_use", permissions)
        self.assertIn("redistribution", permissions)
        self.assertIn("model_weight_training", permissions)
        self.assertIn("requires_separate_explicit_training_authorization",
                      permissions["model_weight_training"])

    def test_integration_extends_existing_learning_system(self):
        integration = self.curriculum["integration_contract"]
        self.assertTrue(integration["existing_catalog"].endswith("catalog.json"))
        self.assertTrue(integration["existing_course_registry"].endswith(".json"))
        self.assertIn("Do not create duplicate catalogs", integration["policy"])

    def test_curriculum_does_not_claim_bootcamp_is_running(self):
        self.assertEqual(
            self.curriculum["status"],
            "curriculum_definition_created_runtime_integration_and_validation_pending",
        )
        self.assertIn("live_verified", self.curriculum["evidence_states"])


if __name__ == "__main__":
    unittest.main()
