from __future__ import annotations

import unittest

from runtime.compiled_bots import run_bot


class CompiledBotRuntimeTests(unittest.TestCase):
    def test_generated_markdown_bots_execute_in_sandbox(self):
        for slug in ("3d-asset-mgr", "5s-audit-tool"):
            with self.subTest(slug=slug):
                result = run_bot(slug, {"objective": "verify compiled runtime"})
                self.assertEqual(result["status"], "success")
                self.assertEqual(result["bot_id"], slug)
                self.assertEqual(result["data"]["mode"], "sandbox")
                self.assertEqual(result["data"]["live_actions"], [])
                self.assertEqual(result["metrics"]["live_writes"], 0)


if __name__ == "__main__":
    unittest.main()
