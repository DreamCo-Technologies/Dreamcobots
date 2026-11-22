"""Regression tests for fail-closed Buddy evidence and model-promotion gates."""
from __future__ import annotations

import unittest

from buddy.builder.division_audit import audit
from buddy.builder.model_selection import select
from buddy.builder.promotion_gate import promote


class EvidenceGateTests(unittest.TestCase):
    def test_promotion_requires_two_saved_runs(self):
        decision = promote(None, {"runs": 1, "failure_rate": 0.0, "quality": 1.0})
        self.assertFalse(decision["promoted"])
        self.assertEqual(decision["reason"], "two saved runs required")

    def test_promotion_requires_measured_quality_and_failure_rate(self):
        for challenger in (
            {"runs": 2, "failure_rate": None, "quality": 0.9},
            {"runs": 2, "failure_rate": 0.0, "quality": None},
        ):
            with self.subTest(challenger=challenger):
                self.assertFalse(promote(None, challenger)["promoted"])

    def test_promotion_rejects_worse_failure_rate(self):
        decision = promote(
            {"failure_rate": 0.1, "quality": 0.7},
            {"runs": 2, "failure_rate": 0.2, "quality": 0.9},
        )
        self.assertFalse(decision["promoted"])
        self.assertEqual(decision["reason"], "failure rate worse")

    def test_promotion_requires_strict_quality_improvement(self):
        decision = promote(
            {"failure_rate": 0.1, "quality": 0.8},
            {"runs": 2, "failure_rate": 0.1, "quality": 0.8},
        )
        self.assertFalse(decision["promoted"])
        self.assertEqual(decision["reason"], "quality not better")

    def test_only_measured_improvement_can_promote(self):
        decision = promote(
            {"failure_rate": 0.1, "quality": 0.8},
            {"runs": 2, "failure_rate": 0.1, "quality": 0.9},
        )
        self.assertTrue(decision["promoted"])

    def test_model_selection_never_modifies_weights(self):
        for task in ("plan", "code", "deploy", "unlisted-task"):
            with self.subTest(task=task):
                self.assertFalse(select(task)["weight_modification"])

    def test_division_audit_never_claims_production_readiness(self):
        report = audit()
        self.assertTrue(report["divisions"])
        self.assertFalse(report["production_ready"])
        self.assertTrue(all(row["production_ready"] is False for row in report["divisions"]))


if __name__ == "__main__":
    unittest.main()
