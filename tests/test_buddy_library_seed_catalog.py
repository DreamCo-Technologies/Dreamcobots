from __future__ import annotations

import unittest
from pathlib import Path

from tools.build_buddy_library_seed_catalog import build_catalog


class BuddyLibrarySeedCatalogTests(unittest.TestCase):
    def test_catalog_matches_the_committed_dreamco_seed_curriculum(self):
        root = Path(__file__).resolve().parents[1]
        catalog = build_catalog(root)
        self.assertEqual(catalog["schema"], "dreamco.buddy_library_seed_catalog.v1")
        self.assertEqual(catalog["raw_candidate_count"], 536)
        self.assertEqual(catalog["unique_candidate_count"], 531)
        self.assertEqual(len(catalog["candidates"]), 531)
        self.assertFalse(catalog["worldwide_completeness_claimed"])

    def test_seed_candidates_do_not_infer_permissions(self):
        root = Path(__file__).resolve().parents[1]
        catalog = build_catalog(root)
        for candidate in catalog["candidates"]:
            self.assertEqual(candidate["status"], "seed_candidate_unverified")
            self.assertEqual(candidate["version"], None)
            self.assertEqual(candidate["license"], "unknown")
            self.assertEqual(candidate["rights"]["execution"], "prohibited_by_seed_catalog")
            self.assertEqual(candidate["rights"]["training"], "pending")


if __name__ == "__main__":
    unittest.main()
