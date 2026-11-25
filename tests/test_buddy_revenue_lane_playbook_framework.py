import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class RevenueLanePlaybookFrameworkTests(unittest.TestCase):
    def setUp(self):
        self.framework = json.loads((ROOT / "config/buddy-revenue-lane-playbook-framework.json").read_text(encoding="utf-8"))
        self.canonical = json.loads((ROOT / "money_os/config/revenue_lanes_expanded.json").read_text(encoding="utf-8"))

    def test_every_canonical_revenue_lane_has_one_framework(self):
        expected = {row["id"] for row in self.canonical["lanes"]}
        actual = [row["lane_id"] for row in self.framework["lanes"]]
        self.assertEqual(len(actual), len(set(actual)))
        self.assertEqual(set(actual), expected)
        self.assertEqual(self.framework["lane_count"], len(expected))

    def test_each_lane_has_complete_shared_stages_and_evidence_outputs(self):
        required = {"discover", "qualify", "economics", "design", "launch", "measure"}
        for lane in self.framework["lanes"]:
            with self.subTest(lane=lane["lane_id"]):
                self.assertEqual({stage["id"] for stage in lane["stages"]}, required)
                self.assertTrue(lane["lane_specific_safeguards"])
                self.assertTrue(lane["required_outputs"])
                self.assertIn("framework_only_not_a_completed_lane_course", lane["content_status"])

    def test_no_framework_claims_revenue_or_mastery(self):
        self.assertIn("not a completed course", self.framework["truth_boundary"])
        for lane in self.framework["lanes"]:
            self.assertNotIn("mastered", lane["status"])
            self.assertIn("completed_sandbox_case", lane["mastery_evidence"])

    def test_external_actions_and_live_money_remain_gated(self):
        self.assertIn("unapproved_ad_spend", self.framework["lanes"][0]["blocked_actions"])
        self.assertTrue(any("approval" in action for lane in self.framework["lanes"] for action in lane["blocked_actions"]))
        self.assertTrue(any("live revenue gate" in rule for rule in self.framework["global_rules"]))


if __name__ == "__main__":
    unittest.main()
