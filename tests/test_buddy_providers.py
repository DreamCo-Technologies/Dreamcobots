#!/usr/bin/env python3
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import buddy_providers as providers  # noqa: E402


class ProviderPresenceTests(unittest.TestCase):
    def test_presence_report_does_not_call_network(self) -> None:
        report = providers.run(live=False)
        self.assertEqual(report["schema"], "dreamco.live_providers.v1")
        self.assertFalse(report["live"])
        ids = {item["id"] for item in report["items"]}
        self.assertEqual(ids, {"grok", "openai", "claude"})
        for item in report["items"]:
            self.assertNotEqual(item["status"], "live")

    def test_redact_strips_keys(self) -> None:
        text = providers.redact("Bearer sk-abcdefghijklmnopqrstuvwxyz0123456789 extra")
        self.assertNotIn("sk-abcdefghijklmnopqrstuvwxyz0123456789", text)


if __name__ == "__main__":
    unittest.main()
