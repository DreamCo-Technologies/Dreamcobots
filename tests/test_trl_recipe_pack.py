"""TRL recipe pack stays plan-only: manifest intact, gates pending, train scripts refuse.

No torch/trl import and no downloads: dry-run and refusal both exit before `from trl import`.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

PACK = Path(__file__).resolve().parents[1] / "study_packs" / "trl"


class TrlRecipePackTest(unittest.TestCase):
    def test_manifest_hashes_match(self):
        manifest = json.loads((PACK / "MANIFEST.json").read_text())
        self.assertEqual(manifest["status"], "plan_only")
        for rel, digest in manifest["files"].items():
            self.assertEqual(hashlib.sha256((PACK / rel).read_bytes()).hexdigest(), digest, rel)

    def test_all_gates_pending_without_evidence(self):
        gates = json.loads((PACK / "gates.json").read_text())["gates"]
        self.assertTrue(gates)
        for gate in gates:
            self.assertNotEqual(gate["status"], "green", gate["id"])

    def _run(self, method, *args, approved=None):
        env = {k: v for k, v in os.environ.items() if k != "APPROVED_RUN"}
        if approved is not None:
            env["APPROVED_RUN"] = approved
        return subprocess.run(
            [sys.executable, str(PACK / "scripts" / f"train_{method}.py"), *args],
            capture_output=True, text=True, env=env, cwd=PACK / "scripts", timeout=60,
        )

    def test_dry_run_validates_without_training(self):
        try:
            import yaml  # noqa: F401
        except ImportError:
            self.skipTest("pyyaml not installed")
        for method in ("sft", "dpo", "grpo"):
            proc = self._run(method, "--dry-run")
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("no training performed", proc.stdout)

    def test_refuses_even_with_approval_while_gates_pending(self):
        try:
            import yaml  # noqa: F401
        except ImportError:
            self.skipTest("pyyaml not installed")
        for approved in (None, "1"):
            proc = self._run("sft", approved=approved)
            self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)
            self.assertIn("[refused]", proc.stdout)


if __name__ == "__main__":
    unittest.main()
