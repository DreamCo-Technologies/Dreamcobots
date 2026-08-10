import json
import unittest
from pathlib import Path

from tools.run_sandbox_repair_loop import success

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "config" / "sandbox-repair-loop.json"


class SandboxRepairLoopTests(unittest.TestCase):
    def test_success_requires_every_declared_capability_contract(self):
        good = {
            "profilesTested": 1051,
            "failed": 0,
            "allDeclaredCapabilitiesTested": True,
            "sandboxCapabilityTestsFailed": 0,
            "sandboxCapabilityTestsPassed": 8408,
            "declaredCapabilitiesTested": 8408,
            "repositoryControlledFlowComplete": True,
        }
        self.assertTrue(success(good))
        for key, bad_value in [
            ("failed", 1),
            ("allDeclaredCapabilitiesTested", False),
            ("sandboxCapabilityTestsFailed", 1),
            ("sandboxCapabilityTestsPassed", 8407),
            ("repositoryControlledFlowComplete", False),
        ]:
            bad = dict(good)
            bad[key] = bad_value
            self.assertFalse(success(bad), key)

    def test_loop_is_bounded_and_does_not_weaken_tests(self):
        policy = json.loads(POLICY.read_text(encoding="utf-8"))
        self.assertLessEqual(policy["max_rounds_per_run"], 12)
        self.assertGreaterEqual(policy["stop_after_no_progress_rounds"], 1)
        forbidden = " ".join(policy["forbidden_repairs"]).lower()
        self.assertIn("weakening", forbidden)
        self.assertIn("marking a capability passed without executable evidence", forbidden)
        self.assertIn("npm audit fix --force", forbidden)
        self.assertIn("live external writes", forbidden)
        self.assertIn("merging main", forbidden)

    def test_retest_order_finishes_with_full_fleet(self):
        policy = json.loads(POLICY.read_text(encoding="utf-8"))
        self.assertEqual(policy["retest_order"][0], "failed capability acceptance path")
        self.assertIn("full 1,051-bot fleet", policy["retest_order"][-1])


if __name__ == "__main__":
    unittest.main()
