"""Tests for the Buddy category-system registry validator."""
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class BuddyCategorySystemRegistryTests(unittest.TestCase):
    def test_category_registry_matches_source_catalogs(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools/validate_buddy_category_system_registry.py"), "--check"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("103 systems", result.stdout)

if __name__ == "__main__":
    unittest.main()
