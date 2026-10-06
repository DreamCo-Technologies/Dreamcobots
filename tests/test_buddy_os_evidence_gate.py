"""Buddy OS evidence gate: divisions stay fail-closed; promotion needs saved runs."""

from __future__ import annotations

import unittest

from buddy.builder.division_audit import audit
from buddy.builder.division_gaps import check
from buddy.builder.division_resources import resources
from buddy.builder.model_selection import select
from buddy.builder.promotion_gate import promote


class BuddyOsEvidenceGateTests(unittest.TestCase):
    def test_division_audit_lists_folders_without_claiming_health(self) -> None:
        report = audit()
        self.assertGreaterEqual(len(report["divisions"]), 1)
        self.assertFalse(report["production_ready"])
        self.assertEqual(report["required"], ["code", "config", "tests", "docs", "health"])
        for row in report["divisions"]:
            self.assertTrue(row["present"])
            self.assertEqual(row["health"], "not measured")
            self.assertFalse(row["production_ready"])

    def test_division_gaps_keep_every_division_not_working(self) -> None:
        report = check()
        self.assertEqual(len(report["divisions"]), 40)
        self.assertEqual(report["working"], 0)
        self.assertFalse(report["production_ready"])
        self.assertTrue(all(row["working"] is False for row in report["divisions"]))
        self.assertTrue(all(row["production_ready"] is False for row in report["divisions"]))

    def test_division_resources_do_not_invent_market_data(self) -> None:
        report = resources()
        self.assertEqual(report["market_data"], "not measured")
        self.assertFalse(report["top_competitor"])
        self.assertFalse(report["production_ready"])
        self.assertEqual(report["divisions"], report["code_folder"])

    def test_model_selection_does_not_claim_weight_changes(self) -> None:
        choice = select("code")
        self.assertFalse(choice["weight_modification"])
        self.assertIn(choice["model"], {"local-note", None})
        missing = select("no-such-task-type-zzzz")
        self.assertIsNone(missing["model"])
        self.assertFalse(missing["weight_modification"])

    def test_promotion_gate_requires_two_saved_runs_and_better_quality(self) -> None:
        self.assertFalse(promote(None, None)["promoted"])
        self.assertFalse(promote({"quality": 1, "failure_rate": 0}, {"runs": 1, "quality": 2, "failure_rate": 0})["promoted"])
        self.assertFalse(
            promote({"quality": 2, "failure_rate": 0.1}, {"runs": 2, "quality": 1, "failure_rate": 0.1})["promoted"]
        )
        decision = promote({"quality": 1, "failure_rate": 0.2}, {"runs": 2, "quality": 2, "failure_rate": 0.1})
        self.assertTrue(decision["promoted"])
        self.assertEqual(decision["rollback"], "restore previous champion")


if __name__ == "__main__":
    unittest.main()
