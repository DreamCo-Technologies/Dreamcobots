from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.generate_production_evidence_ledger import build  # noqa: E402


class ProductionEvidenceLedgerTest(unittest.TestCase):
    def test_every_real_division_is_reconciled_without_pseudo_buckets(self):
        data = build()
        self.assertEqual(data["summary"]["real_divisions"], 55)
        self.assertEqual(len(data["divisions"]), 55)
        self.assertEqual(data["summary"]["catalog_profiles"], 1101)
        self.assertTrue(data["summary"]["catalogs_reconciled"])
        self.assertNotIn("UNASSIGNED", {row["name"] for row in data["divisions"]})
        self.assertIn("UNASSIGNED", {row["name"] for row in data["non_division_buckets"]})

    def test_no_missing_receipt_can_be_promoted(self):
        data = build()
        self.assertEqual(data["summary"]["production_ready_divisions"], 0)
        self.assertFalse(data["summary"]["soak_24h_verified"])
        self.assertTrue(all(not row["production_ready"] for row in data["divisions"]))
        self.assertTrue(all(row["blockers"] for row in data["divisions"]))

    def test_generated_page_payload_matches(self):
        expected = build()
        actual = json.loads((ROOT / "website/data/production-evidence-ledger.json").read_text())
        self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
