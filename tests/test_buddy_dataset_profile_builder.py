import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "dataset_profile_builder", ROOT / "buddy/learning/dataset_profile_builder.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class DatasetProfileBuilderTests(unittest.TestCase):
    def setUp(self):
        self.profile = MODULE.create_profile("user-opaque-1", "My Python Buddy", "Learn Python debugging")

    def test_default_profile_is_valid(self):
        self.assertEqual(MODULE.validate_profile(self.profile), [])

    def test_mix_must_sum_to_one(self):
        self.profile["source_mix"]["courses"] = 0.5
        self.assertIn("source_mix weights must sum to 1.0", MODULE.validate_profile(self.profile))

    def test_unknown_rights_cannot_be_added_as_approved(self):
        self.profile["sources"] = [{
            "id": "x", "uri": "https://example.org", "category": "courses",
            "status": "approved", "rights": "unknown", "content_state": "content_available",
            "content_ref": "blob://x", "provenance": {"source": "example"}
        }]
        self.assertTrue(any("rights must be reviewed" in e for e in MODULE.validate_profile(self.profile)))

    def test_metadata_only_is_not_learning(self):
        self.profile["sources"] = [{
            "id": "x", "uri": "https://example.org", "category": "courses",
            "status": "approved", "rights": "open_license", "content_state": "metadata_only",
            "provenance": {"license": "CC-BY"}
        }]
        plan = MODULE.build_learning_plan(self.profile)
        self.assertEqual(plan["sources_with_content"], 0)
        self.assertEqual(plan["metadata_only_or_unavailable_sources"], 1)

    def test_actual_content_enters_learning_plan(self):
        self.profile["sources"] = [{
            "id": "x", "uri": "https://example.org/course", "category": "courses",
            "status": "approved", "rights": "open_license", "content_state": "content_available",
            "content_ref": "blob://tenant/x", "content_hash": "abc123",
            "provenance": {"license": "CC-BY", "attribution": "Example"}
        }]
        plan = MODULE.build_learning_plan(self.profile)
        self.assertEqual(plan["sources_with_content"], 1)
        self.assertEqual(plan["source_manifest"][0]["normalized_weight"], 1.0)

    def test_training_manifest_does_not_claim_execution(self):
        plan = MODULE.build_learning_plan(self.profile)
        manifest = MODULE.build_training_manifest(self.profile, plan)
        self.assertEqual(manifest["execution_state"], "planned_not_executed")
        self.assertFalse(manifest["weight_change_claim"])

    def test_advanced_methods_require_review(self):
        self.profile["training_methods"] = ["continued_pretraining"]
        self.assertTrue(any("advanced_training_approved" in e for e in MODULE.validate_profile(self.profile)))


if __name__ == "__main__":
    unittest.main()
