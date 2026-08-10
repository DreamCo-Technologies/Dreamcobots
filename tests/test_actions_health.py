from __future__ import annotations

import unittest

from tools import audit_actions_health


class ActionsHealthTests(unittest.TestCase):
    def test_supported_action_major_baselines_match_current_policy(self):
        self.assertEqual(audit_actions_health.MAX_MAJOR["actions/checkout"], 6)
        self.assertEqual(audit_actions_health.MAX_MAJOR["actions/setup-node"], 6)
        self.assertEqual(audit_actions_health.MAX_MAJOR["actions/setup-python"], 6)
        self.assertEqual(audit_actions_health.MAX_MAJOR["actions/upload-artifact"], 7)
        self.assertEqual(audit_actions_health.MAX_MAJOR["actions/configure-pages"], 6)
        self.assertEqual(audit_actions_health.MAX_MAJOR["actions/upload-pages-artifact"], 5)
        self.assertEqual(audit_actions_health.MAX_MAJOR["actions/deploy-pages"], 5)

    def test_action_parser_detects_major_versions(self):
        sample = "\n".join([
            "- uses: actions/checkout@v6",
            "- uses: actions/upload-artifact@v7",
        ])
        self.assertEqual(
            audit_actions_health.USES_RE.findall(sample),
            [("actions/checkout", "6"), ("actions/upload-artifact", "7")],
        )

    def test_invalid_future_checkout_major_is_detectable(self):
        action = "actions/checkout"
        major = 7
        self.assertGreater(major, audit_actions_health.MAX_MAJOR[action])


if __name__ == "__main__":
    unittest.main()
