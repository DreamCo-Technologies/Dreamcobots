#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.compile_md_bots import parse_md  # noqa: E402


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
        # The runtime package is a compiler output, not a checkout dependency.
        # Build and import it in an isolated process so the test cannot pollute
        # the repository or make later dependency checks pass by test order.
        with tempfile.TemporaryDirectory() as directory:
            fixture = Path(directory)
            (fixture / "bots").mkdir()
            shutil.copyfile(ROOT / "bots" / "dreambot.md", fixture / "bots" / "dreambot.md")
            probe = '''
import contextlib
import importlib
import io
import json
import sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from tools import compile_md_bots as compiler
fixture = Path(sys.argv[2])
compiler.ROOT = fixture
compiler.BOTS_DIR = fixture / "bots"
compiler.OUT_DIR = fixture / "runtime" / "compiled_bots"
sys.argv = ["compile_md_bots.py"]
with contextlib.redirect_stdout(io.StringIO()):
    assert compiler.main() == 0
sys.path.insert(0, str(fixture))
importlib.invalidate_caches()
generated = importlib.import_module("runtime.compiled_bots")
assert Path(generated.__file__).resolve().is_relative_to(fixture.resolve())
registry = generated.load_registry()
result = generated.run_bot(registry["bots"][0]["slug"], {"probe": True})
try:
    generated.run_bot("missing-bot", {})
except ModuleNotFoundError:
    missing_rejected = True
else:
    missing_rejected = False
print(json.dumps({"registry": registry, "result": result, "missing_rejected": missing_rejected}))
'''
            completed = subprocess.run(
                [sys.executable, "-c", probe, str(ROOT), str(fixture)],
                check=True, capture_output=True, text=True,
            )
            payload = json.loads(completed.stdout)
            registry = payload["registry"]
            self.assertEqual(registry["count"], 1)
            self.assertTrue((fixture / "runtime" / "compiled_bots" / "registry.json").exists())
            result = payload["result"]
            self.assertEqual(result["status"], "success")
            self.assertEqual(result["bot_id"], registry["bots"][0]["slug"])
            self.assertIn("plan", result["data"])
            self.assertEqual(result["data"]["task"], {"probe": True})
            self.assertEqual(result["data"]["live_actions"], [])
            self.assertEqual(result["metrics"].get("live_writes"), 0)
            self.assertTrue(payload["missing_rejected"])


if __name__ == "__main__":
    unittest.main()
