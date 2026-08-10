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
