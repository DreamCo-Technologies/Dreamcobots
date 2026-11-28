import unittest

from buddy.learning.benchmark_learning_adapter import benchmark_to_event


class BenchmarkLearningAdapterTests(unittest.TestCase):
    def test_benchmark_outcome_becomes_learning_event(self):
        event = benchmark_to_event({
            "benchmark_id": "coding-1",
            "division": "coding",
            "passed": True,
            "verified": True,
            "regression_passed": True,
            "safety_passed": True,
            "native_success": True,
        })
        self.assertEqual(event["event_type"], "benchmark")
        self.assertIs(event["success"], True)
        self.assertIs(event["native_success"], True)

    def test_benchmark_event_preserves_goal_and_research_source_provenance(self):
        event = benchmark_to_event({
            "benchmark_id": "research-1",
            "passed": True,
            "verified": True,
            "goal_id": "goal-42",
            "wikipedia_source_ids": ["wiki-1", ""],
        })
        self.assertEqual(event["goal_ids"], ["goal-42"])
        self.assertEqual(event["wikipedia_source_ids"], ["wiki-1"])


if __name__ == "__main__":
    unittest.main()
