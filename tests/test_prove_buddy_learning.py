#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import prove_buddy_learning as proof  # noqa: E402


class ProveBuddyLearningTest(unittest.TestCase):
    def test_proof_pack_shows_learning_delta(self):
        self.assertEqual(proof.HISTORY.name, 'buddy-learning-proof-history.jsonl')
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            real_history = root / 'evidence' / 'buddy-learning-history.jsonl'
            real_history.parent.mkdir()
            real_history.write_text('{"real_evidence":"preserve me"}\n')
            before = real_history.read_bytes()
            out = root / 'config' / 'proof.json'
            with patch.multiple(proof, ROOT=root, OUT_JSON=out, OUT_MD=root / 'reports' / 'proof.md', HISTORY=root / 'evidence' / proof.HISTORY.name):
                self.assertEqual(proof.main(), 0)
                payload = json.loads(out.read_text())
                self.assertTrue(payload['proven'])
                self.assertGreater(payload['cycle']['after']['progress']['native_pass_rate'], payload['cycle']['before']['progress']['native_pass_rate'])
                self.assertEqual(payload['cycle']['after']['summary']['events'], 4)
                self.assertTrue(proof.HISTORY.exists())
                self.assertEqual(real_history.read_bytes(), before)

    def test_workflow_uploads_only_the_synthetic_proof_history(self):
        workflow = (ROOT / '.github/workflows/buddy-learning-proof.yml').read_text()
        self.assertIn('evidence/buddy-learning-proof-history.jsonl', workflow)
        self.assertNotIn('evidence/buddy-learning-history.jsonl', workflow)

    def test_script_imports_with_an_isolated_python_path(self):
        with tempfile.TemporaryDirectory() as temporary:
            result = subprocess.run([sys.executable, '-I', '-c', 'import runpy,sys; runpy.run_path(sys.argv[1],run_name="proof_import_test")', str(ROOT / 'tools' / 'prove_buddy_learning.py')], cwd=temporary, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
