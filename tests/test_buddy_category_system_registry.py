"""Tests for the Buddy category-system registry validator."""
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class BuddyCategorySystemRegistryTests(unittest.TestCase):
    def test_category_registry_matches_all_source_catalogs(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools/validate_buddy_category_system_registry.py"), "--check"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        registry = json.loads((ROOT / "config/buddy/category-system-registry.json").read_text(encoding="utf-8"))
        self.assertIn(str(len(registry["systems"])) + " systems", result.stdout)
        self.assertIn("403 study", result.stdout)
        self.assertIn("576 study records", result.stdout)

    def test_category_systems_dashboard_is_wired(self):
        page = (ROOT / "website/category-systems.html").read_text(encoding="utf-8")
        script = (ROOT / "website/category-systems.js").read_text(encoding="utf-8")
        nav = (ROOT / "website/nav.js").read_text(encoding="utf-8")
        self.assertIn("category-systems.js", page)
        self.assertIn("data/category-system-registry.json", script)
        self.assertIn("category-systems.html", nav)
        self.assertIn("cs-card", script)

if __name__ == "__main__":
    unittest.main()
