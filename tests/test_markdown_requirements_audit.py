"""Regression tests for the per-file Markdown requirements audit."""
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class MarkdownRequirementsAuditTests(unittest.TestCase):
    def test_manifest_covers_all_tracked_markdown_and_pages_copy(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools/validate_markdown_requirements_audit.py")],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("1624 files", result.stdout)

if __name__ == "__main__":
    unittest.main()
