"""Canonical division gap inventory must use the 55-domain crosswalk."""
import json
from pathlib import Path
import unittest

from buddy.builder.division_gaps import check

ROOT = Path(__file__).resolve().parents[1]
CROSSWALK = ROOT / "config/generated/masterbot-55-domain-crosswalk.json"


class BuddyDivisionGapsTests(unittest.TestCase):
    def test_gap_inventory_covers_exactly_the_canonical_domain_crosswalk(self):
        crosswalk = json.loads(CROSSWALK.read_text(encoding="utf-8"))
        expected = {row["domain_name"] for row in crosswalk["domains"]}
        report = check()
        actual = {row["division"] for row in report["divisions"]}
        self.assertEqual(len(expected), 55)
        self.assertEqual(actual, expected)
        self.assertEqual(len(report["divisions"]), 55)
        self.assertFalse(report["production_ready"])
        self.assertTrue(all(row["production_ready"] is False for row in report["divisions"]))


if __name__ == "__main__":
    unittest.main()
