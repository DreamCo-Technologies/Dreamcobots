"""Fail-closed benchmark promotion and evidence-gate workflow regression tests."""
import math
import unittest
from pathlib import Path
from buddy.builder.promotion_gate import promote

ROOT = Path(__file__).resolve().parents[1]


class PromotionGateFiniteEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.champion = {"quality": 0.7, "failure_rate": 0.1}
        self.challenger = {"runs": 2, "quality": 0.8, "failure_rate": 0.05}

    def test_normal_improvement_promotes(self):
        self.assertTrue(promote(self.champion, self.challenger)["promoted"])

    def test_invalid_challenger_measurements_fail_closed(self):
        for key, invalid in (("quality", math.nan), ("quality", math.inf),
                             ("quality", -math.inf), ("failure_rate", math.nan),
                             ("failure_rate", math.inf), ("failure_rate", -0.1),
                             ("failure_rate", 1.1), ("quality", "excellent"),
                             ("failure_rate", "0.01"), ("quality", True)):
            with self.subTest(key=key, value=invalid):
                self.assertFalse(promote(self.champion, {**self.challenger, key: invalid})["promoted"])

    def test_invalid_champion_measurements_fail_closed(self):
        for key, invalid in (("quality", math.nan), ("failure_rate", math.nan),
                             ("quality", None), ("failure_rate", -1)):
            with self.subTest(key=key, value=invalid):
                self.assertFalse(promote({**self.champion, key: invalid}, self.challenger)["promoted"])

    def test_runs_requires_integer_count(self):
        for value in (True, 2.5, "2", math.nan):
            with self.subTest(value=value):
                self.assertFalse(promote(self.champion, {**self.challenger, "runs": value})["promoted"])

    def test_missing_baseline_not_a_comparative_promotion(self):
        self.assertFalse(promote(None, self.challenger)["promoted"])

    def test_workflow_uses_existing_test_module(self):
        workflow = (ROOT / ".github/workflows/evidence-gate.yml").read_text()
        self.assertIn("python3 -m unittest discover -s tests -p 'test_buddy_os_evidence_gate.py'", workflow)
        self.assertIn("python3 -m unittest discover -s tests -p 'test_promotion_gate_finite_evidence.py'", workflow)
        self.assertNotIn("buddy.builder.evidence_gate_test", workflow)


if __name__ == "__main__":
    unittest.main()
