import unittest

from tools.buddy_failure_learning import classify, fingerprint, recommend, update_memory


class BuddyFailureLearningTests(unittest.TestCase):
    def setUp(self):
        self.observation = {
            "repository": "DreamCo-Technologies/Dreamcobots",
            "workflow": "Actions Health",
            "job": "contract-tests",
            "failed_step": "validate generated prospectus",
            "error_signature": "inventory mismatch",
        }

    def test_fingerprint_ignores_run_and_commit_identifiers(self):
        a = fingerprint({**self.observation, "run_id": 12, "commit": "abc"})
        b = fingerprint({**self.observation, "run_id": 99, "commit": "def"})
        self.assertEqual(a, b)

    def test_classifies_generated_index_failure(self):
        self.assertEqual(classify(self.observation), "generated-index")

    def test_safe_generated_index_can_use_bounded_automation(self):
        plan = recommend(self.observation, {"incidents": []})
        self.assertTrue(plan["automatic_code_change_allowed"])
        self.assertFalse(plan["requires_human_approval"])

    def test_security_failure_requires_human_approval(self):
        plan = recommend({**self.observation, "failure_class": "security"}, {"incidents": []})
        self.assertFalse(plan["automatic_code_change_allowed"])
        self.assertTrue(plan["requires_human_approval"])

    def test_verified_lesson_is_reused_on_recurrence(self):
        memory = {"incidents": [{
            "fingerprint": fingerprint({**self.observation, "failure_class": "generated-index"}),
            "occurrence_count": 2,
            "verified_lesson": {"root_cause": "stale generated index", "repair": "regenerate index"},
        }]}
        plan = recommend(self.observation, memory)
        self.assertEqual(plan["recurrence_count"], 3)
        self.assertEqual(plan["recommended_action"], "reapply_verified_lesson_in_isolated_branch")

    def test_unverified_repairs_never_become_lessons(self):
        with self.assertRaises(ValueError):
            update_memory({"incidents": []}, self.observation, {"original_failure": True, "regressions": False})

    def test_verified_repair_is_saved(self):
        memory = update_memory({"incidents": []}, self.observation, {
            "original_failure": True, "regressions": True,
            "root_cause": "stale report", "repair": "regenerate report",
            "evidence": ["run:123"], "verified_at": "2026-11-20T12:00:00Z",
        })
        self.assertEqual(len(memory["incidents"]), 1)
        self.assertEqual(memory["incidents"][0]["verified_lesson"]["repair"], "regenerate report")


if __name__ == "__main__":
    unittest.main()
