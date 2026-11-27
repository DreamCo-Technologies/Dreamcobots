import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class BuddyUniversalLearningGovernanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policy=json.loads((ROOT/"config/buddy-conversation-learning-governance.json").read_text())

    def test_every_learning_source_is_classified_and_gated(self):
        coverage=self.policy["learning_coverage"]
        self.assertGreaterEqual(len(coverage["source_classes"]), 15)
        self.assertEqual(coverage["default_access"], "deny")
        self.assertTrue(coverage["access_is_not_training_consent"])
        self.assertIn("verify_source_scope_and_rights", coverage["mandatory_pipeline"])
        self.assertIn("resolve_purpose_specific_consent", coverage["mandatory_pipeline"])

    def test_learning_planes_are_separate(self):
        planes=self.policy["learning_coverage"]["learning_planes"]
        self.assertEqual(set(planes), {"personal_memory","procedural_knowledge","product_improvement","cross_user_shared","foundation_model_training"})
        self.assertTrue(self.policy["principles"]["raw_transcripts_never_enter_shared_learning"])

    def test_no_unsafe_access_or_automatic_weight_updates(self):
        coverage=self.policy["learning_coverage"]
        self.assertTrue(coverage["no_bypass_of_paywalls_logins_captchas_or_access_controls"])
        self.assertTrue(coverage["no_credential_harvesting"])
        self.assertIn("separately approved reproducible training", coverage["model_update_policy"])

    def test_holdout_and_provenance_are_mandatory(self):
        coverage=self.policy["learning_coverage"]
        self.assertTrue(coverage["benchmark_holdouts_excluded_from_training"])
        self.assertIn("attach_provenance_and_content_hash", coverage["mandatory_pipeline"])
        self.assertTrue(self.policy["quality_gates"]["learning_pipeline_evidence_required"])

if __name__ == "__main__":
    unittest.main()
