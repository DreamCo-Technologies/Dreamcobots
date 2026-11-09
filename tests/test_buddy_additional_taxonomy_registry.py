"""Tests for additional DreamCo taxonomy system coverage."""
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class BuddyAdditionalTaxonomyRegistryTests(unittest.TestCase):
    def test_all_additional_taxonomies_have_individual_systems(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools/validate_buddy_additional_taxonomy_registry.py"), "--check"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        registry = json.loads((ROOT / "config/buddy/additional-taxonomy-system-registry.json").read_text(encoding="utf-8"))
        self.assertIn(str(len(registry["systems"])) + " systems", result.stdout)
        self.assertIn(str(len(registry["counts"]["groups"])) + " groups", result.stdout)

if __name__ == "__main__":
    unittest.main()
