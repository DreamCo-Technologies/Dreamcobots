"""Preserve canonical and supplemental bot counts in the unified generator."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools import build_unified_bot_system as generator


class UnifiedBotCohortTests(unittest.TestCase):
    def test_growth_profiles_never_become_canonical(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            app = root / "App_bots"
            app.mkdir()
            recovery = root / "config/generated/legacy-bot-recovery-manifest.json"
            recovery.parent.mkdir(parents=True)
            recovery.write_text(json.dumps({"items": [], "state_counts": {}}))
            (app / "Core.json").write_text(json.dumps({"division": "Core", "bots": [{"slug": "core", "displayName": "Core", "capabilities": ["plan"]}]}))
            (app / "Growth.json").write_text(json.dumps({"division": "Growth", "growth": True, "bots": [{"slug": "growth", "displayName": "Growth", "capabilities": ["plan"]}]}))
            output = root / "config/generated/unified-bot-system.json"
            with patch.multiple(generator, ROOT=root, APP=app, RECOVERY=recovery, OUT=output):
                self.assertEqual(generator.main(), 0)
            result = json.loads(output.read_text())
            self.assertEqual(result["canonical_bot_count"], 1)
            self.assertEqual(result["supplemental_bot_count"], 1)
            self.assertEqual(result["total_accounted_worker_records"], 2)
            self.assertEqual([bot["slug"] for bot in result["canonical_bots"]], ["core"])
            self.assertEqual([bot["slug"] for bot in result["supplemental_bots"]], ["growth"])
            self.assertEqual(result["supplemental_bots"][0]["status"], "supplemental_pending_promotion")


if __name__ == "__main__":
    unittest.main()
