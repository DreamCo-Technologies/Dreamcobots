"""Offline tests for the fail-closed Buddy task router."""
import unittest
from tools.task_model_router import classify_task, load_taxonomy, rank_candidates


def candidate(**overrides):
    data = dict(id="local-model", task_families=["code_repair"],
                license_reviewed=True, training_rights_verified=True,
                adapter_verified=True, benchmark_verified=True,
                safety_verified=True, estimated_cost_usd=0,
                benchmark_score=0.8)
    data.update(overrides)
    return data


class TaskRouterTests(unittest.TestCase):
    def test_taxonomy_loads(self):
        self.assertIn("code_repair", load_taxonomy()["dimensions"]["task_families"])

    def test_classification(self):
        self.assertEqual(classify_task("Debug a failing test"), "code_repair")

    def test_verified_free_model(self):
        self.assertEqual(rank_candidates("code_repair", [candidate()])["selected"], "local-model")

    def test_no_candidate_fallback(self):
        self.assertEqual(rank_candidates("sql", [candidate()])["fallback"], "buddy_native")

    def test_unreviewed_license_rejected(self):
        self.assertIsNone(rank_candidates("code_repair", [candidate(license_reviewed=False)])["selected"])

    def test_paid_model_rejected(self):
        self.assertIsNone(rank_candidates("code_repair", [candidate(estimated_cost_usd=0.1)])["selected"])

    def test_training_rights_required(self):
        self.assertIsNone(rank_candidates("code_repair", [candidate(training_rights_verified=False)], training=True)["selected"])

    def test_missing_benchmark_rejected(self):
        self.assertIsNone(rank_candidates("code_repair", [candidate(benchmark_verified=False)])["selected"])

    def test_invalid_nan_score_rejected(self):
        self.assertIsNone(rank_candidates("code_repair", [candidate(benchmark_score=float("nan"))])["selected"])

    def test_boolean_cost_rejected(self):
        self.assertIsNone(rank_candidates("code_repair", [candidate(estimated_cost_usd=False)])["selected"])

    def test_best_score_selected(self):
        self.assertEqual(rank_candidates("code_repair", [candidate(id="a", benchmark_score=0.5), candidate(id="b", benchmark_score=0.9)])["selected"], "b")


if __name__ == "__main__":
    unittest.main()
