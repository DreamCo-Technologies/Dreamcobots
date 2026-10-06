#!/usr/bin/env python3
"""Unit tests for reasoning + learning registry."""

from __future__ import annotations

import unittest

from reasoning_and_learning_registry import (
    GATE_BOOTCAMP_GRADUATION,
    GATE_MARKETPLACE_LISTING,
    GATE_PATH_D_ALLOWLIST,
    LP_FAMILY_STRATEGIES,
    discover_all,
    export_lp_strategies_manifest,
    learning_catalog_meta,
    load_learning,
    load_reasoning,
    marketplace_packs,
    run_structure_tests,
    search,
    select_for_task,
)


class RegistryTests(unittest.TestCase):
    def test_structure(self) -> None:
        failures = run_structure_tests()
        self.assertEqual(failures, [], msg=str(failures))

    def test_counts(self) -> None:
        data = discover_all()
        self.assertGreaterEqual(len(data["reasoning"]), 15)
        self.assertGreaterEqual(len(data["learning"]), 15)

    def test_unique_ids(self) -> None:
        r_ids = [i.id for i in load_reasoning()]
        l_ids = [i.id for i in load_learning()]
        self.assertEqual(len(r_ids), len(set(r_ids)))
        self.assertEqual(len(l_ids), len(set(l_ids)))

    def test_search_finds_evidence(self) -> None:
        hits = search("evidence first")
        self.assertTrue(any(h.id == "evidence_first" for h in hits))

    def test_select_deal(self) -> None:
        sel = select_for_task("score this investment deal and risks")
        rids = [x["id"] for x in sel["reasoning"]]
        self.assertTrue(any(x in rids for x in ("rubric_scoring", "counterfactual", "devil_advocate")))

    def test_marketplace_tiers(self) -> None:
        packs = marketplace_packs()
        tiers = {p["tier"] for p in packs}
        self.assertIn("free", tiers)
        self.assertIn("elite", tiers)
        complete = next(p for p in packs if p["sku"].endswith("complete"))
        self.assertGreaterEqual(complete["reasoning_count"], 15)
        self.assertGreaterEqual(complete["learning_count"], 15)


    def test_lp_strategies_export(self) -> None:
        meta = learning_catalog_meta()
        lp = export_lp_strategies_manifest()
        self.assertEqual(lp["sku"], f"{LP_FAMILY_STRATEGIES}-v{meta['version']}")
        self.assertEqual(lp["marketplace_status"], "catalog_sku")
        for k in ("sellable", "live", "path_d_allowlist_write"):
            self.assertFalse(lp["claims"][k])
        for g in (GATE_BOOTCAMP_GRADUATION, GATE_MARKETPLACE_LISTING, GATE_PATH_D_ALLOWLIST):
            self.assertFalse(lp["gates"][g])
        self.assertFalse(lp["graduation_evidence"]["eligible_for_mastery"])
        self.assertEqual(lp["strategy_ids"], [i.id for i in load_learning()])

    def test_lp_export_write_roundtrip(self) -> None:
        import json
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "LP-STRATEGIES.manifest.json"
            written = export_lp_strategies_manifest(write_path=dest)
            self.assertEqual(json.loads(dest.read_text(encoding="utf-8"))["sku"], written["sku"])


if __name__ == "__main__":
    unittest.main()
