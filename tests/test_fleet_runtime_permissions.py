"""Permission-gate tests for buddy/fleet_runtime/permissions.py.

The fleet runtime may act unattended only for levels whose approval is
``none`` in buddy_os/governance/approval_policy.yaml AND inside the bot's
ceiling. Everything else must come back as ``approval_required``.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from buddy.fleet_runtime import permissions  # noqa: E402

GOVERNED = ("repository_write", "external_side_effect", "destructive", "production_deploy")


class PermissionPolicyTests(unittest.TestCase):
    def test_fallback_matches_policy_file(self):
        self.assertEqual(permissions.load_levels(), permissions.FALLBACK_LEVELS)

    def test_only_read_only_and_sandbox_run_unattended(self):
        self.assertEqual(permissions.unattended_levels(), {"read_only", "sandbox"})

    def test_decisions_inside_ceiling(self):
        self.assertTrue(permissions.decide("sandbox", "sandbox")["allowed"])
        self.assertTrue(permissions.decide("sandbox", "read_only")["allowed"])
        self.assertTrue(permissions.decide("plan_only", "read_only")["allowed"])
        self.assertTrue(permissions.decide("plan_only", "sandbox")["allowed"])

    def test_governed_levels_always_need_approval(self):
        for ceiling in ("read_only", "sandbox", "plan_only"):
            for level in GOVERNED:
                decision = permissions.decide(ceiling, level)
                self.assertFalse(decision["allowed"], (ceiling, level))
                self.assertEqual(decision["decision"], "approval_required", (ceiling, level))
                self.assertNotEqual(decision["approval"], "none", (ceiling, level))

    def test_ceiling_is_enforced(self):
        decision = permissions.decide("read_only", "sandbox")
        self.assertFalse(decision["allowed"])
        self.assertEqual(decision["decision"], "approval_required")

    def test_unknown_ceiling_denies_everything(self):
        for level in permissions.load_levels():
            self.assertFalse(permissions.decide("superuser", level)["allowed"], level)

    def test_unknown_level_is_denied_with_explicit_approval(self):
        decision = permissions.decide("sandbox", "nope")
        self.assertFalse(decision["allowed"])
        self.assertEqual(decision["decision"], "unknown_level")
        self.assertEqual(decision["approval"], "explicit")


class LiveActionDetectionTests(unittest.TestCase):
    def test_live_actions_are_flagged(self):
        for text in ("Send weekly report email", "deploy to production", "Delete stale records",
                     "process payment", "post to social", "withdraw funds"):
            self.assertTrue(permissions.text_declares_live_action(text), text)

    def test_offline_work_is_not_flagged(self):
        for text in ("Cost analysis", "KPI tracking", "summarize notes", "", None):
            self.assertFalse(permissions.text_declares_live_action(text), text)


if __name__ == "__main__":
    unittest.main()
