#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.build_user_money_map import main as build_map  # noqa: E402
from tools.run_24h_sandbox_soak import record_tick  # noqa: E402


class UserMoneyMapTest(unittest.TestCase):
    def test_map_and_soak_do_not_charge(self):
        self.assertEqual(build_map(), 0)
        payload = json.loads((ROOT / "config" / "generated" / "user-money-map.json").read_text())
        self.assertGreaterEqual(payload["bot_count"], 20)
        self.assertEqual(payload["stripe"], "sandbox_only")
        self.assertTrue(all(row["autonomous_live_money"] is False for row in payload["bots"]))
        with tempfile.TemporaryDirectory() as tmp:
            scratch = Path(tmp)
            (scratch / "config/generated").mkdir(parents=True)
            (scratch / "config/generated/user-money-map.json").write_text(json.dumps(payload), encoding="utf-8")
            history = record_tick(scratch)
            tick = json.loads((scratch / "config/generated/sandbox-24h-tick.json").read_text())
            self.assertEqual(tick["charges_attempted"], 0)
            self.assertFalse(history["summary"]["complete"])
            self.assertEqual(history["summary"]["successful_ticks"], 1)

    def test_soak_requires_both_tick_count_and_real_elapsed_time(self):
        self.assertEqual(build_map(), 0)
        payload = json.loads((ROOT / "config/generated/user-money-map.json").read_text())
        with tempfile.TemporaryDirectory() as tmp:
            scratch = Path(tmp)
            (scratch / "config/generated").mkdir(parents=True)
            (scratch / "config/generated/user-money-map.json").write_text(json.dumps(payload), encoding="utf-8")
            start = datetime(2026, 1, 1, tzinfo=timezone.utc)
            history = None
            for hour in range(24):
                history = record_tick(scratch, start + timedelta(hours=hour))
            self.assertIsNotNone(history)
            self.assertFalse(history["summary"]["complete"])
            history = record_tick(scratch, start + timedelta(hours=24))
            self.assertTrue(history["summary"]["complete"])
            self.assertEqual(history["summary"]["status"], "passed_24h")


if __name__ == "__main__":
    unittest.main()
