#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.compile_md_bots import main, parse_md  # noqa: E402


class CompileMdBotsTest(unittest.TestCase):
    def test_parse_known_spec(self):
        path = ROOT / "bots" / "dreambot.md"
        self.assertTrue(path.exists())
        spec = parse_md(path)
        self.assertIsNotNone(spec)
        assert spec is not None
        self.assertEqual(spec["slug"], "dreambot")
        self.assertTrue(spec["capabilities"])
        self.assertIn(spec["autonomy"], {"plan_only", "sandbox_execute"})

    def test_compiler_writes_registry_and_runnable_bot(self):
        rc = main()
        self.assertEqual(rc, 0)
        registry_path = ROOT / "runtime" / "compiled_bots" / "registry.json"
        self.assertTrue(registry_path.exists())
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        self.assertGreaterEqual(registry["count"], 1)
        from runtime.compiled_bots import run_bot

        first = registry["bots"][0]["slug"]
        result = run_bot(first, {"probe": True})
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["bot_id"], first)
        self.assertIn("plan", result["data"])
        self.assertEqual(result["metrics"].get("live_writes"), 0)


if __name__ == "__main__":
    unittest.main()
