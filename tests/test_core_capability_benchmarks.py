import unittest

from tools.validate_core_capability_benchmarks import validate


class CoreCapabilityBenchmarkRegistryTests(unittest.TestCase):
    def setUp(self):
        self.registry = {"schema": "dreamco.buddy_benchmark_registry.v1",
                         "tasks": ["coding", "reasoning"]}
        self.definitions = {
            "schema": "dreamco.core_capability_benchmark_definitions.v1",
            "score_policy": {"unknown_without_evidence": True, "holdout_required": True},
            "benchmarks": [
                {"benchmark_id": "B-CODE", "capability_id": "coding", "objective": "Assess coding",
                 "dimensions": ["correctness"], "task_design": {"holdout": "unseen"},
                 "rubric": [{"dimension": "correctness", "weight": 100}],
                 "pass_threshold": 85, "critical_gates": ["No unsafe changes"],
                 "execution_status": "definition_ready_adapter_pending"},
                {"benchmark_id": "B-REASON", "capability_id": "reasoning", "objective": "Assess reasoning",
                 "dimensions": ["logic"], "task_design": {"holdout": "unseen"},
                 "rubric": [{"dimension": "logic", "weight": 100}],
                 "pass_threshold": 80, "critical_gates": ["No fabricated premises"],
                 "execution_status": "definition_ready_adapter_pending"},
            ],
        }

    def test_all_canonical_capabilities_have_weighted_holdout_definitions(self):
        self.assertEqual(validate(self.registry, self.definitions), [])

    def test_missing_capability_definition_is_reported(self):
        self.definitions["benchmarks"].pop()
        self.assertTrue(any("missing capability definitions" in e for e in validate(self.registry, self.definitions)))

    def test_rubric_weights_must_sum_to_100(self):
        self.definitions["benchmarks"][0]["rubric"][0]["weight"] = 90
        self.assertTrue(any("sum to 100" in e for e in validate(self.registry, self.definitions)))

    def test_implemented_benchmark_requires_real_adapter_and_test_paths(self):
        self.definitions["benchmarks"][0]["execution_status"] = "implemented"
        self.assertTrue(any("adapter_path and test_path" in e for e in validate(self.registry, self.definitions)))

    def test_duplicate_capability_definition_is_rejected(self):
        self.definitions["benchmarks"].append(dict(self.definitions["benchmarks"][0], benchmark_id="B-CODE-2"))
        self.assertTrue(any("exactly one" in e for e in validate(self.registry, self.definitions)))


if __name__ == "__main__":
    unittest.main()
