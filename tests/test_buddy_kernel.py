#!/usr/bin/env python3
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import buddy_kernel as kernel  # noqa: E402


class KernelFillTests(unittest.TestCase):
    def test_all_catalogued_sections_have_fills(self) -> None:
        self.assertEqual(set(kernel.CATALOGUED), set(kernel.FILLS))
        self.assertEqual(len(kernel.CATALOGUED), 55)

    def test_rate_limiter_and_idempotency(self) -> None:
        self.assertTrue(kernel.fill_226()["allowed"][:2] == [True, True])
        self.assertEqual(kernel.fill_225()["result"], {"issue": 1})

    def test_cancel_stops_task(self) -> None:
        self.assertEqual(kernel.fill_223()["state"], "cancelled")

    def test_rbac_denies_viewer_merge(self) -> None:
        self.assertFalse(kernel.fill_305()["viewer_merge"])

    def test_openai_does_not_fake_a_pass(self) -> None:
        result = kernel.fill_254()
        self.assertFalse(result["live_called"])
        self.assertFalse(result["secret_printed"])

    def test_run_writes_report(self) -> None:
        report = kernel.run()
        self.assertGreaterEqual(report["passed"], 50)
        payload = json.loads((ROOT / "website" / "data" / "kernel-fill.json").read_text())
        self.assertEqual(payload["schema"], "dreamco.kernel_fill.v1")
        self.assertEqual(payload["live_stripe"], False)


if __name__ == "__main__":
    unittest.main()
