import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "dataset_profile_builder", ROOT / "buddy/learning/dataset_profile_builder.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def verified_source(**overrides):
    source = {
        "id": "course-python-1",
        "uri": "https://example.org/course",
        "category": "courses",
        "status": "approved",
        "rights": "open_license",
        "license_id": "CC-BY-4.0",
        "license_url": "https://creativecommons.org/licenses/by/4.0/",
        "training_permission_verified": True,
        "rights_evidence": "rights-review-record:course-python-1",
        "content_state": "content_available",
        "content_ref": "blob://tenant/course-python-1",
        "content_hash": "sha256:abc123",
        "provenance": {"source": "Example course", "revision": "v1"},
    }
    source.update(overrides)
    return source


class DatasetProfileBuilderTests(unittest.TestCase):
    def setUp(self):
        self.profile = MODULE.create_profile("user-opaque-1", "My Python Buddy", "Learn Python debugging")

    def test_default_profile_is_valid(self):
        self.assertEqual(MODULE.validate_profile(self.profile), [])

    def test_mix_must_sum_to_one(self):
        self.profile["source_mix"]["courses"] = 0.5
        self.assertIn("source_mix weights must sum to 1.0", MODULE.validate_profile(self.profile))

    def test_unknown_rights_cannot_be_approved(self):
        self.profile["sources"] = [verified_source(rights="unknown")]
        self.assertTrue(any("rights must be reviewed" in error for error in MODULE.validate_profile(self.profile)))

    def test_unknown_rights_can_be_recorded_pending_but_never_learned(self):
        source = verified_source(rights="unknown", status="pending_review",
                                 training_permission_verified=False, license_id=None, license_url=None)
        self.profile["sources"] = [source]
        self.assertEqual(MODULE.validate_profile(self.profile), [])
        plan = MODULE.build_learning_plan(self.profile)
        self.assertEqual(plan["sources_with_content"], 0)

    def test_approved_source_without_rights_evidence_is_blocked(self):
        source = verified_source()
        del source["rights_evidence"]
        self.profile["sources"] = [source]
        self.assertTrue(any("verified rights evidence and permission" in error
                            for error in MODULE.validate_profile(self.profile)))

    def test_user_authorized_source_requires_owner_approval(self):
        source = verified_source(rights="user_authorized", license_id=None, license_url=None)
        self.profile["sources"] = [source]
        self.assertTrue(any("verified rights evidence and permission" in error
                            for error in MODULE.validate_profile(self.profile)))

    def test_metadata_only_is_not_learning(self):
        self.profile["sources"] = [verified_source(content_state="metadata_only",
                                                   content_ref=None, content_hash=None)]
        plan = MODULE.build_learning_plan(self.profile)
        self.assertEqual(plan["sources_with_content"], 0)
        self.assertEqual(plan["metadata_only_or_unavailable_sources"], 1)

    def test_pending_source_never_enters_learning_plan(self):
        self.profile["sources"] = [verified_source(status="pending_review")]
        plan = MODULE.build_learning_plan(self.profile)
        self.assertEqual(plan["sources_with_content"], 0)
        self.assertEqual(plan["metadata_only_or_unavailable_sources"], 1)

    def test_actual_content_enters_learning_plan_only_with_evidence(self):
        self.profile["sources"] = [verified_source()]
        plan = MODULE.build_learning_plan(self.profile)
        self.assertEqual(plan["sources_with_content"], 1)
        self.assertEqual(plan["source_manifest"][0]["normalized_weight"], 1.0)
        self.assertEqual(plan["source_manifest"][0]["rights_evidence"], "rights-review-record:course-python-1")

    def test_content_available_requires_hash_and_provenance(self):
        source = verified_source(content_hash=None, provenance={})
        self.profile["sources"] = [source]
        errors = MODULE.validate_profile(self.profile)
        self.assertTrue(any("content_ref and content_hash required" in error for error in errors))
        self.assertTrue(any("provenance required" in error for error in errors))

    def test_training_manifest_does_not_claim_execution(self):
        plan = MODULE.build_learning_plan(self.profile)
        manifest = MODULE.build_training_manifest(self.profile, plan)
        self.assertEqual(manifest["execution_state"], "planned_not_executed")
        self.assertFalse(manifest["weight_change_claim"])

    def test_advanced_methods_require_review(self):
        self.profile["training_methods"] = ["continued_pretraining"]
        self.assertTrue(any("advanced_training_approved" in error for error in MODULE.validate_profile(self.profile)))

    def test_owner_id_must_be_opaque(self):
        self.profile["owner_id"] = "person@example.com"
        self.assertTrue(any("opaque app-scoped ID" in error for error in MODULE.validate_profile(self.profile)))

    def test_training_limits_must_be_numeric(self):
        self.profile["training"]["max_compute_usd"] = "unlimited"
        self.assertTrue(any("max_compute_usd" in error for error in MODULE.validate_profile(self.profile)))


if __name__ == "__main__":
    unittest.main()
