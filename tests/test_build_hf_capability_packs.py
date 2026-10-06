#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import build_hf_capability_packs as build  # noqa: E402
from tools.build_hf_capability_packs import main  # noqa: E402

SP = ROOT / "study_packs"
EXPECTED = {
    "pack.instruct", "pack.code", "pack.reason", "pack.tools", "pack.research", "pack.safety",
    "pack.embed", "pack.rerank", "pack.vision", "pack.speech", "pack.translate", "pack.summarize",
}


class HfPacksTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        assert main() == 0

    def test_index_union_of_twelve_packs_train_off(self):
        index = json.loads((SP / "index.json").read_text())
        self.assertEqual(index["schema"], "dreamco.study_packs_index.v1")
        self.assertEqual(index["count"], 12)
        self.assertEqual(set(index["packs"]), EXPECTED)
        self.assertFalse(index["train_in_default_ci"])
        self.assertTrue(all(lane["train_allowed"] is False for lane in index["lanes"]))

    def test_every_pack_has_full_layout(self):
        for pid in EXPECTED:
            d = SP / pid
            for rel in ("CARD.md", "sources.json", "evals.json", "recipes/sft.yaml",
                        "recipes/dpo.yaml", "evidence/.gitkeep"):
                self.assertTrue((d / rel).is_file(), f"{pid}/{rel}")
            card = (d / "CARD.md").read_text()
            self.assertIn("automatic weight download: no", card)
            self.assertIn("xai/grok-best-available", card)

    def test_sources_seeded_unpinned(self):
        src = json.loads((SP / "pack.code" / "sources.json").read_text())
        ids = [m["repo_id"] for m in src["hf_models"]]
        self.assertIn("bigcode/starcoder2-7b", ids)
        for entry in src["hf_models"] + src["hf_datasets"]:
            self.assertIsNone(entry["revision"])
            self.assertEqual(entry["license"], "TBD")
            self.assertEqual(entry["pin_status"], "unpinned")
        tools = json.loads((SP / "pack.tools" / "sources.json").read_text())
        self.assertEqual(tools["hf_models"], [])
        self.assertEqual(tools["hf_datasets"], [])
        self.assertTrue(tools["search_hints"])

    def test_known_non_commercial_seeds_are_labelled(self):
        instruct = json.loads((SP / "pack.instruct" / "sources.json").read_text())
        alpaca = next(e for e in instruct["hf_datasets"] if e["repo_id"] == "tatsu-lab/alpaca")
        self.assertEqual(alpaca["license"], "cc-by-nc-4.0")
        self.assertIs(alpaca["commercial_ok"], False)
        self.assertIsNone(alpaca["revision"])
        self.assertEqual(alpaca["pin_status"], "unpinned")
        self.assertIn("NON-COMMERCIAL", alpaca["note"])
        for repo_id in build.KNOWN_NON_COMMERCIAL:
            entry = build._entry(repo_id)
            self.assertTrue(entry["license"].startswith("cc-by-nc"), repo_id)
            self.assertIs(entry["commercial_ok"], False, repo_id)
        self.assertEqual(build._entry("bigcode/starcoder2-7b")["license"], "TBD")

    def test_evals_floors(self):
        evals = json.loads((SP / "pack.embed" / "evals.json").read_text())
        self.assertEqual(evals["floor"], 0.7)
        self.assertEqual(evals["tasks"], [])
        self.assertIn("embeddings", evals["capability_ids"])
        safety = json.loads((SP / "pack.safety" / "evals.json").read_text())
        self.assertEqual(safety["floor"], 0.9)

    def test_readme_day1_and_report(self):
        readme = (SP / "README.md").read_text()
        self.assertIn("pack.summarize/CARD.md", readme)
        day1 = (SP / "DAY1_INVENTORY.md").read_text()
        self.assertIn("deepseek-ai/DeepSeek-V3", day1)
        self.assertIn("TBD", day1)
        report = (ROOT / "reports" / "HUGGINGFACE_CAPABILITY_PACKS.md").read_text()
        self.assertIn("Packs: **12**", report)


if __name__ == "__main__":
    unittest.main()
