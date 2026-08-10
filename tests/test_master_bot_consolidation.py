from __future__ import annotations

import unittest

from tools.build_master_bot_consolidation import build_plan, load_bots, overlap


class MasterBotConsolidationTests(unittest.TestCase):
    def test_consolidation_scans_existing_fleet_without_deleting_profiles(self):
        plan = build_plan()
        self.assertEqual(plan["fleet_profiles_scanned"], len(load_bots()))
        self.assertGreater(plan["fleet_profiles_scanned"], 0)
        self.assertTrue(all(item["original_profile_preserved"] is True for item in plan["proposals"]))

    def test_one_master_is_selected_per_detected_division(self):
        plan = build_plan()
        self.assertEqual(plan["divisions"], len(plan["division_masters"]))
        self.assertGreater(plan["divisions"], 0)
        self.assertEqual(len(set(plan["division_masters"].values())), plan["divisions"])

    def test_missing_usage_telemetry_is_not_treated_as_zero_usage(self):
        plan = build_plan()
        if not plan["usage_telemetry_available"]:
            self.assertFalse(plan["low_use_rule_active"])
            self.assertTrue(all(item["executions"] is None for item in plan["proposals"]))
            self.assertTrue(all(not any("usage <=" in reason for reason in item["reason"]) for item in plan["proposals"]))

    def test_overlap_is_bounded(self):
        bots = load_bots()
        if len(bots) >= 2:
            value = overlap(bots[0], bots[1])
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 1.0)

    def test_merge_proposals_are_reversible_aliases(self):
        plan = build_plan()
        for item in plan["proposals"]:
            self.assertNotEqual(item["alias_slug"], item["master_slug"])
            self.assertEqual(item["activation_mode"], "reversible_alias")
            self.assertIn(item["status"], {"ready_for_regression_testing", "master_capability_union_required"})


if __name__ == "__main__":
    unittest.main()
