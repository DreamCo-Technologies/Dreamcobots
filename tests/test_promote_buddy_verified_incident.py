import unittest

from tools.promote_buddy_verified_incident import promote, validate


class BuddyVerifiedIncidentPromotionTests(unittest.TestCase):
    def setUp(self):
        self.observation = {
            "repository": "DreamCo-Technologies/Dreamcobots",
            "workflow": "Buddy CI Safe Generated-Artifact Repair",
            "job": "regenerate-and-verify",
            "failed_step": "file prospectus drift",
            "error_signature": "stale generated index",
            "run_id": "45305674269",
        }
        sha_a = "a" * 40
        sha_b = "b" * 40
        sha_c = "c" * 40
        self.verification = {
            "original_failure": True,
            "regressions": True,
            "verification_run_conclusion": "success",
            "repair_pr_state": "merged",
            "human_reviewed": True,
            "source_ownership_confirmed": True,
            "contains_secrets": False,
            "contains_personal_data": False,
            "third_party_content_included": False,
            "failure_commit": sha_a,
            "repair_merge_commit": sha_b,
            "verified_commit": sha_c,
            "original_failure_run_id": "45305674269",
            "verification_run_id": "45306000001",
            "original_failure_url": "https://github.com/DreamCo-Technologies/Dreamcobots/actions/runs/45305674269",
            "verification_run_url": "https://github.com/DreamCo-Technologies/Dreamcobots/actions/runs/45306000001",
            "repair_pr_url": "https://github.com/DreamCo-Technologies/Dreamcobots/pull/18126",
            "reviewer": "repository-maintainer",
            "root_cause": "The main-branch failure path skipped deterministic index regeneration.",
            "repair": "Run allowlisted deterministic builders before the verification checks.",
            "original_failure_test": "python tools/build_file_prospectus.py --check",
            "regression_tests": ["tests.test_file_prospectus_inventory"],
            "evidence": ["GitHub Actions run 45305674269", "merged repair PR 18126"],
            "verified_at": "2026-11-24T02:00:00Z",
        }

    def test_promotion_requires_complete_merged_and_successful_lineage(self):
        memory, promoted = promote({"incidents": []}, self.observation, self.verification)
        self.assertTrue(promoted)
        self.assertEqual(memory["schema"], "dreamco.buddy_failure_learning_memory.v2")
        incident = memory["incidents"][0]
        self.assertEqual(incident["occurrence_count"], 1)
        self.assertEqual(incident["verification_events"][0]["verification_run_id"], "45306000001")
        self.assertFalse(memory["promotion_policy"]["training_eligible_by_default"])

    def test_duplicate_verification_run_is_idempotent(self):
        memory, promoted = promote({"incidents": []}, self.observation, self.verification)
        self.assertTrue(promoted)
        repeated, promoted_again = promote(memory, self.observation, self.verification)
        self.assertFalse(promoted_again)
        self.assertEqual(repeated, memory)
        self.assertEqual(repeated["incidents"][0]["occurrence_count"], 1)

    def test_unmerged_pr_is_rejected(self):
        invalid = dict(self.verification, repair_pr_state="open")
        with self.assertRaisesRegex(ValueError, "must be merged"):
            validate(self.observation, invalid)

    def test_failed_verification_run_is_rejected(self):
        invalid = dict(self.verification, verification_run_conclusion="failure")
        with self.assertRaisesRegex(ValueError, "success conclusion"):
            validate(self.observation, invalid)

    def test_missing_original_failure_confirmation_is_rejected(self):
        invalid = dict(self.verification, original_failure=False)
        with self.assertRaisesRegex(ValueError, "original failure"):
            validate(self.observation, invalid)

    def test_secret_or_personal_data_is_rejected(self):
        invalid = dict(self.verification, contains_personal_data=True)
        with self.assertRaisesRegex(ValueError, "contains_personal_data"):
            validate(self.observation, invalid)

    def test_immutable_commit_sha_is_required(self):
        invalid = dict(self.verification, repair_merge_commit="main")
        with self.assertRaisesRegex(ValueError, "full immutable"):
            validate(self.observation, invalid)

    def test_regression_test_evidence_is_required(self):
        invalid = dict(self.verification, regression_tests=[])
        with self.assertRaisesRegex(ValueError, "regression test"):
            validate(self.observation, invalid)


if __name__ == "__main__":
    unittest.main()
