"""Tests for task and Markdown taxonomy system coverage."""
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class BuddyTaskTaxonomyRegistryTests(unittest.TestCase):
    def test_all_task_and_markdown_taxonomies_have_individual_systems(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools/validate_buddy_task_taxonomy_registry.py"), "--check"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("369 systems", result.stdout)
        self.assertIn("11 groups", result.stdout)

if __name__ == "__main__":
    unittest.main()
