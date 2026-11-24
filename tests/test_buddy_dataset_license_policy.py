import unittest

from buddy.datasets.license_policy import assess_training_candidate


def internal_candidate():
    return {
        "source": "dreamco_authored",
        "id": "dreamco.bootcamp.core.v1",
        "url": "https://github.com/DreamCo-Technologies/Dreamcobots",
        "license": "DREAMCO_INTERNAL_OWNED",
        "ai_training_allowed": True,
        "content_rights_verified": True,
        "privacy_review": "PASSED",
        "owner_assignment_verified": True,
        "contributor_rights_verified": True,
        "owner_approval_id": "OWNER-APPROVAL-001",
        "rights_evidence": "internal-rights-review-001",
    }


class DatasetLicensePolicyTests(unittest.TestCase):
    def test_internal_dreamco_data_requires_every_ownership_and_rights_gate(self):
        result = assess_training_candidate(internal_candidate())
        self.assertEqual(result["status"], "INTERNAL_OWNED_TRAINING_CANDIDATE_REQUIRES_DATA_QUALITY_AND_FINAL_REVIEW")
        self.assertTrue(result["internal_owned_path"])
        self.assertTrue(result["internal_ownership_evidence_verified"])
        self.assertFalse(result["training_approved"])

    def test_internal_data_is_blocked_without_owner_assignment(self):
        candidate = internal_candidate()
        candidate["owner_assignment_verified"] = False
        result = assess_training_candidate(candidate)
        self.assertEqual(result["status"], "BLOCKED_INTERNAL_OWNERSHIP_OR_CONTRIBUTOR_RIGHTS")

    def test_internal_data_is_blocked_without_contributor_rights(self):
        candidate = internal_candidate()
        candidate["contributor_rights_verified"] = False
        result = assess_training_candidate(candidate)
        self.assertEqual(result["status"], "BLOCKED_INTERNAL_OWNERSHIP_OR_CONTRIBUTOR_RIGHTS")

    def test_internal_data_is_blocked_without_explicit_ai_training_permission(self):
        candidate = internal_candidate()
        candidate["ai_training_allowed"] = False
        result = assess_training_candidate(candidate)
        self.assertEqual(result["status"], "BLOCKED_NO_EXPLICIT_AI_TRAINING_PERMISSION")

    def test_internal_license_cannot_be_used_for_third_party_source(self):
        candidate = internal_candidate()
        candidate["source"] = "huggingface"
        result = assess_training_candidate(candidate)
        self.assertEqual(result["status"], "BLOCKED_INTERNAL_OWNERSHIP_OR_CONTRIBUTOR_RIGHTS")

    def test_existing_permissive_public_license_path_remains_supported(self):
        candidate = {
            "source": "huggingface", "id": "org/dataset",
            "url": "https://huggingface.co/datasets/org/dataset",
            "license": "CC-BY-4.0", "ai_training_allowed": True,
            "content_rights_verified": True, "privacy_review": "PASSED",
        }
        result = assess_training_candidate(candidate)
        self.assertEqual(result["status"], "PERMISSIVE_LICENSE_TRAINING_CANDIDATE_REQUIRES_DATA_QUALITY_AND_FINAL_REVIEW")
        self.assertFalse(result["internal_owned_path"])


if __name__ == "__main__":
    unittest.main()
