import unittest

from tools.leaderboard_math import pareto_frontier, update_glicko2


class Glicko2Tests(unittest.TestCase):
    def test_standard_glicko2_example(self):
        result = update_glicko2(
            1500, 200, 0.06,
            [
                {"rating": 1400, "rd": 30, "score": 1},
                {"rating": 1550, "rd": 100, "score": 0},
                {"rating": 1700, "rd": 300, "score": 0},
            ],
        )
        self.assertAlmostEqual(result["rating"], 1464.06, delta=0.1)
        self.assertAlmostEqual(result["rd"], 151.52, delta=0.1)
        self.assertAlmostEqual(result["volatility"], 0.059996, delta=0.00001)
        self.assertEqual(result["games"], 3)

    def test_no_head_to_head_evidence_does_not_change_rating(self):
        result = update_glicko2(1500, 200, 0.06, [])
        self.assertEqual(result, {"rating": 1500.0, "rd": 200.0, "volatility": 0.06, "games": 0})

    def test_invalid_match_score_is_rejected(self):
        with self.assertRaises(ValueError):
            update_glicko2(1500, 200, 0.06, [{"rating": 1500, "rd": 100, "score": 0.7}])


class ParetoFrontierTests(unittest.TestCase):
    def test_returns_non_dominated_models_only(self):
        result = pareto_frontier([
            {"model_id": "balanced", "accuracy": 0.9, "latency_ms": 20, "parameters_m": 45},
            {"model_id": "fast-small", "accuracy": 0.88, "latency_ms": 8, "parameters_m": 18},
            {"model_id": "dominated", "accuracy": 0.85, "latency_ms": 30, "parameters_m": 90},
            {"model_id": "accurate", "accuracy": 0.96, "latency_ms": 60, "parameters_m": 120},
        ])
        self.assertEqual({row["model_id"] for row in result}, {"balanced", "fast-small", "accurate"})
        self.assertTrue(all(row["efficiency_index"] > 0 for row in result))

    def test_duplicate_models_are_rejected(self):
        rows = [
            {"model_id": "same", "accuracy": 0.9, "latency_ms": 10, "parameters_m": 10},
            {"model_id": "same", "accuracy": 0.8, "latency_ms": 20, "parameters_m": 20},
        ]
        with self.assertRaisesRegex(ValueError, "unique"):
            pareto_frontier(rows)


if __name__ == "__main__":
    unittest.main()
