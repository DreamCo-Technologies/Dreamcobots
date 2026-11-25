"""Canonical division gap inventory must use division manifests, not root folders."""
from pathlib import Path
import unittest

from buddy.builder.division_gaps import check

ROOT = Path(__file__).resolve().parents[1]


class BuddyDivisionGapsTests(unittest.TestCase):
    def test_gap_inventory_covers_exactly_the_canonical_division_manifests(self):
        report = check()
        expected = {
            row["identity"]["division"]
            for path in (ROOT / "config" / "divisions").glob("*.json")
            for row in [__import__("json").loads(path.read_text(encoding="utf-8"))]
        }
        self.assertEqual({row["division"] for row in report["divisions"]}, expected)
        self.assertEqual(report["working"], 0)
        self.assertTrue(all(row["working"] is False for row in report["divisions"]))
        self.assertTrue(all(row["production_ready"] is False for row in report["divisions"]))


if __name__ == "__main__":
    unittest.main()
