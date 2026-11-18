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
