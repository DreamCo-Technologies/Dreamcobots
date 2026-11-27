import json
import tempfile
import unittest
from pathlib import Path

from benchmarks.buddy_benchmark_runner import evaluate_task, run


class BenchmarkRunnerMasteryTruthTests(unittest.TestCase):
    def test_high_score_override_does_not_award_mastery(self):
        result = evaluate_task({
            "task_id": "fixture-1",
            "benchmark_id": 1,
            "mastery_threshold": 0.9,
            "baseline_score": 0.0,
        }, score=1.0)
        self.assertTrue(result.passed)
        self.assertEqual(result.status, "SIMULATED_THRESHOLD_MET")
        self.assertFalse(result.mastery_eligible)
        self.assertEqual(result.mastery_state, "discovered")
        self.assertEqual(result.result_type, "score_override_simulation")

    def test_configured_baseline_is_not_presented_as_a_real_evaluation(self):
        result = evaluate_task({
            "task_id": "fixture-2",
            "benchmark_id": 2,
            "mastery_threshold": 0.8,
            "baseline_score": 0.95,
        })
        self.assertTrue(result.passed)
        self.assertEqual(result.status, "SIMULATED_THRESHOLD_MET")
        self.assertFalse(result.mastery_eligible)
        self.assertEqual(result.result_type, "configured_baseline_placeholder")

    def test_report_labels_all_rates_as_simulated(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "tasks.json"
            path.write_text(json.dumps({
                "benchmark_id": 9,
                "tasks": [{"task_id": "one", "mastery_threshold": 0.9, "baseline_score": 1.0}],
            }), encoding="utf-8")
            report = run(path)
        self.assertTrue(report["simulation_only"])
        self.assertFalse(report["mastery_awarded"])
        self.assertIn("simulated", report["pass_rate_semantics"])
        self.assertFalse(report["results"][0]["mastery_eligible"])


if __name__ == "__main__":
    unittest.main()
