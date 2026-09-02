import importlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


class RunEverythingNowTests(unittest.TestCase):
    def test_writes_inflight_status_before_dependent_step(self) -> None:
        module = importlib.import_module("tools.run_everything_now")
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "config").mkdir()
            (root / "config" / "run-everything-now.json").write_text(
                json.dumps({"truth_rule": "test truth rule"}) + "\n",
                encoding="utf-8",
            )
            (root / "tools").mkdir()
            (root / "tools" / "noop.py").write_text("print('ok')\n", encoding="utf-8")
            (root / "tools" / "assert_snapshot.py").write_text(
                "import json\n"
                "from pathlib import Path\n"
                "status = json.loads(Path('config/generated/run-everything-now-latest.json').read_text())\n"
                "assert status['in_progress'] is True\n"
                "assert status['failed'] == 0\n"
                "assert status['completed_steps'] == 1\n"
                "assert status['pending_steps'] == 1\n"
                "assert status['results'][0]['name'] == 'first'\n"
                "print('snapshot ok')\n",
                encoding="utf-8",
            )
            steps = [
                ("first", [sys.executable, "tools/noop.py"]),
                ("second", [sys.executable, "tools/assert_snapshot.py"]),
            ]
            original = {
                "ROOT": module.ROOT,
                "CFG": module.CFG,
                "OUT": module.OUT,
                "REPORT": module.REPORT,
                "MAX_STEPS": module.MAX_STEPS,
            }
            try:
                module.ROOT = root
                module.CFG = {"truth_rule": "test truth rule"}
                module.OUT = root / "config" / "generated" / "run-everything-now-latest.json"
                module.REPORT = root / "reports" / "RUN_EVERYTHING_NOW.md"
                module.MAX_STEPS = steps
                with patch.object(sys, "argv", ["run_everything_now.py", "--mode", "maximum"]):
                    self.assertEqual(module.main(), 0)
                final = json.loads(module.OUT.read_text(encoding="utf-8"))
                self.assertFalse(final["in_progress"])
                self.assertEqual(final["completed_steps"], 2)
                self.assertEqual(final["pending_steps"], 0)
                self.assertEqual(final["failed"], 0)
                self.assertEqual(final["passed"], 2)
            finally:
                module.ROOT = original["ROOT"]
                module.CFG = original["CFG"]
                module.OUT = original["OUT"]
                module.REPORT = original["REPORT"]
                module.MAX_STEPS = original["MAX_STEPS"]


if __name__ == "__main__":
    unittest.main()
