import json
import unittest
from pathlib import Path

from tools.build_division_reconciliation import build_reconciliation, load_domain_names
from tools.normalize_legacy_portfolios import DIVISION_ALIASES

ROOT = Path(__file__).resolve().parents[1]


class DivisionReconciliationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = build_reconciliation()

    def test_exactly_45_canonical_business_divisions_remain(self):
        names = load_domain_names((ROOT / "shared/division-production-contract.ts").read_text(encoding="utf-8"))
        self.assertEqual(len(names), 45)
        self.assertEqual(len(self.result["domain_divisions"]), 45)
        self.assertEqual(self.result["counts"]["canonical_division_total_after_reconciliation"], 45)
        self.assertEqual(len({row["id"] for row in self.result["domain_divisions"]}), 45)

    def test_all_ten_supplemental_portfolios_have_one_canonical_owner(self):
        rows = self.result["supplemental_portfolio_aliases"]
        self.assertEqual(len(rows), 10)
        self.assertEqual(set(DIVISION_ALIASES), {row["source_portfolio"] for row in rows})
        for row in rows:
            self.assertTrue((ROOT / row["source_path"]).is_file())
            self.assertTrue((ROOT / row["target_path"]).is_file())
            self.assertFalse(row["counts_as_new_division"])
            self.assertTrue(row["preserve_source_identity"])
            self.assertIn(row["canonical_division"], {d["name"] for d in self.result["domain_divisions"]})

    def test_all_20_platform_masterbots_are_shared_services_not_divisions(self):
        rows = self.result["shared_platform_masterbots"]
        self.assertEqual([row["id"] for row in rows], list(range(46, 66)))
        self.assertTrue(all(row["kind"] == "shared_platform_service" for row in rows))
        self.assertTrue(all(row["available_to_all_domain_divisions"] for row in rows))
        self.assertTrue(all(row["primary_domain_owner"] is None for row in rows))
        domain_names = {row["name"] for row in self.result["domain_divisions"]}
        self.assertTrue(domain_names.isdisjoint({row["name"] for row in rows}))

    def test_every_canonical_division_can_call_each_shared_platform_lane(self):
        platform_ids = list(range(46, 66))
        for domain in self.result["domain_divisions"]:
            self.assertEqual(domain["shared_platform_masterbot_ids"], platform_ids)

    def test_generated_artifact_is_deterministic_and_current(self):
        import tools.build_division_reconciliation as builder
        rendered = json.dumps(self.result, indent=2, ensure_ascii=False) + "\n"
        self.assertEqual(builder.OUTPUT.read_text(encoding="utf-8"), rendered)

    def test_policy_contains_no_unmapped_or_duplicate_supplemental_sources(self):
        rows = self.result["supplemental_portfolio_aliases"]
        sources = [row["source_portfolio"] for row in rows]
        self.assertEqual(len(sources), len(set(sources)))
        self.assertEqual(self.result["counts"]["supplemental_source_portfolios"], 10)
        self.assertEqual(self.result["counts"]["shared_platform_masterbots"], 20)


if __name__ == "__main__":
    unittest.main()
