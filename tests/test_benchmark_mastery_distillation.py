import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class BenchmarkMasteryDistillationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run(["python3", "tools/build_benchmark_mastery_distillation.py"], cwd=ROOT, check=True)
        cls.plan = json.loads((ROOT / "config/generated/benchmark-mastery-distillation-plan.json").read_text())
        cls.suites = json.loads((ROOT / "config/repository-test-suites.json").read_text())
        cls.policy = json.loads((ROOT / "config/benchmark-mastery-distillation-policy.json").read_text())

    def test_every_suite_has_one_benchmark_master(self):
        self.assertEqual(self.plan["suite_count"], len(self.suites["suites"]))
        self.assertEqual(self.plan["worker_count"], self.plan["suite_count"])
        self.assertEqual(len({row["worker"]["id"] for row in self.plan["suites"]}), self.plan["suite_count"])

    def test_every_suite_has_chatgpt_reviewed_gap_closure_path(self):
        self.assertEqual(self.plan["gap_closure_path_count"], self.plan["suite_count"])
        self.assertTrue(self.plan["all_suites_have_gap_closure_path"])
        self.assertEqual(self.plan["gap_closure_review_standard"], "ChatGPT-reviewed path")
        required_steps = self.policy["gap_closure_policy"]["required_steps"]
        self.assertGreaterEqual(len(required_steps), 10)
        for row in self.plan["suites"]:
            gap = row["gap_closure"]
            self.assertTrue(gap["required"])
            self.assertEqual(gap["review_standard"], "ChatGPT-reviewed path")
            self.assertEqual(gap["steps"], required_steps)
            self.assertTrue(gap["promotion_requires_passing_evidence"])
            self.assertIn("measure", gap["loop"])
            self.assertIn("retest", gap["loop"])
            self.assertIn("master or iterate", gap["loop"])

    def test_gap_closure_cannot_fake_mastery(self):
        prohibited = self.policy["gap_closure_policy"]["prohibited_shortcuts"]
        joined = " ".join(prohibited).lower()
        self.assertIn("weakening", joined)
        self.assertIn("fabricating", joined)
        self.assertIn("passing evidence", self.policy["truth_boundary"].lower())
        for row in self.plan["suites"]:
            self.assertTrue(row["mastery"]["regression_revokes_mastery"])
            self.assertTrue(row["gap_closure"]["promotion_requires_passing_evidence"])

    def test_parallelism_is_bounded_and_lazy(self):
        self.assertLessEqual(self.plan["maximum_parallel_workers"], 32)
        self.assertTrue(self.plan["workers_are_task_scoped"])
        self.assertFalse(self.plan["all_workers_active_simultaneously"])
        for row in self.plan["suites"]:
            self.assertLessEqual(row["worker"]["parallel_slot"], self.plan["maximum_parallel_workers"])
            self.assertTrue(row["worker"]["expires_after_suite"])

    def test_distillation_preserves_quality_and_rollback(self):
        acceptance = self.policy["distillation_policy"]["acceptance"]
        self.assertIn("student meets benchmark quality floor", acceptance)
        self.assertIn("rollback teacher route retained", acceptance)
        for row in self.plan["suites"]:
            self.assertEqual(row["distillation"]["state"], "candidate_after_mastery")
            self.assertIn("quality", row["distillation"]["promotion_rule"].lower())
            self.assertIn("regression", row["distillation"]["rollback_rule"].lower())


if __name__ == "__main__":
    unittest.main()
