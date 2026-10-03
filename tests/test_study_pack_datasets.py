#!/usr/bin/env python3
"""Checks the hand-authored Hugging Face `datasets` study pack.

Manifest/flag checks always run. The offline lesson examples run only when the
`datasets` library is importable (it is not in the default CI requirements), and
always with the network flag removed so nothing is downloaded.
"""
from __future__ import annotations

import importlib.util
import json
import os
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "study_packs" / "datasets"
HAS_DATASETS = importlib.util.find_spec("datasets") is not None


def _offline_env() -> dict:
    env = dict(os.environ)
    env.pop("HF_PACK_ALLOW_NETWORK", None)
    env["HF_HUB_OFFLINE"] = "1"
    env["HF_DATASETS_OFFLINE"] = "1"
    return env


class StudyPackDatasetsManifestTest(unittest.TestCase):
    def setUp(self):
        self.index = json.loads((PACK / "index.json").read_text(encoding="utf-8"))

    def test_manifest_flags_off(self):
        self.assertEqual(self.index["pack_id"], "datasets")
        self.assertFalse(self.index["train_allowed"])
        self.assertFalse(self.index["train_in_default_ci"])
        self.assertFalse(self.index["automatic_download_in_ci"])
        self.assertFalse(self.index["automatic_weight_download"])
        self.assertFalse(self.index["covers_entire_huggingface_hub"])
        self.assertEqual(self.index["network_flag"], "HF_PACK_ALLOW_NETWORK")

    def test_lessons_and_files_exist(self):
        ids = [lesson["id"] for lesson in self.index["lessons"]]
        self.assertEqual(ids, ["load_dataset", "map", "streaming"])
        self.assertEqual(self.index["count"], 3)
        for lesson in self.index["lessons"]:
            self.assertTrue((PACK / lesson["readme"]).is_file(), lesson["readme"])
            self.assertTrue((PACK / lesson["example"]).is_file(), lesson["example"])
            self.assertTrue(lesson["offline"])
        for rel in self.index["files"]:
            self.assertTrue((PACK / rel).is_file(), rel)

    def test_card_flags_and_pins(self):
        card = (PACK / "CARD.md").read_text(encoding="utf-8")
        self.assertIn("train_in_default_ci: false", card)
        self.assertIn("automatic_download_in_ci: false", card)
        self.assertIn("automatic weight download: no", card)
        self.assertIn(f"datasets=={self.index['library']['version']}", card)
        self.assertIn("Revision-pin policy", card)

    def test_sources_pinned_to_full_sha_and_used_by_lessons(self):
        sources = json.loads((PACK / "sources.json").read_text(encoding="utf-8"))
        self.assertEqual(sources["pack_id"], "datasets")
        self.assertTrue(sources["hf_datasets"])
        for src in sources["hf_datasets"]:
            self.assertRegex(src["revision"], r"^[0-9a-f]{40}$")
            self.assertTrue(src["license"])
        pinned = {src["revision"] for src in sources["hf_datasets"]}
        for lesson in self.index["lessons"]:
            text = (PACK / lesson["example"]).read_text(encoding="utf-8")
            for rev in re.findall(r'HUB_REVISION = "([^"]+)"', text):
                self.assertIn(rev, pinned, lesson["example"])
            if "HUB_REPO_ID" in text:
                self.assertIn("revision=HUB_REVISION", text)
                self.assertIn('os.environ.get("HF_PACK_ALLOW_NETWORK") == "1"', text)

    def test_evals_train_off(self):
        evals = json.loads((PACK / "evals.json").read_text(encoding="utf-8"))
        self.assertFalse(evals["train_allowed"])
        self.assertEqual(len(evals["tasks"]), 3)

    def test_not_listed_in_generated_capability_config(self):
        # The builder overwrites CARD.md for listed ids; this pack must stay unlisted.
        config = json.loads((ROOT / "config" / "huggingface-capability-packs.json").read_text(encoding="utf-8"))
        self.assertNotIn("datasets", [p["id"] for p in config["packs"]])


@unittest.skipUnless(HAS_DATASETS, "datasets library not installed; offline lesson examples skipped")
class StudyPackDatasetsExamplesTest(unittest.TestCase):
    def _run(self, rel: str) -> dict:
        proc = subprocess.run(
            [sys.executable, str(PACK / rel)],
            cwd=str(ROOT),
            env=_offline_env(),
            capture_output=True,
            text=True,
            timeout=300,
        )
        self.assertEqual(proc.returncode, 0, f"{rel} failed:\n{proc.stdout}\n{proc.stderr}")
        last = [line for line in proc.stdout.splitlines() if line.strip()][-1]
        result = json.loads(last)
        self.assertTrue(result["ok"])
        self.assertIn("skipped", str(result.get("hub", "skipped")))
        return result

    def test_load_dataset_offline(self):
        result = self._run("lessons/01_load_dataset/example_load_dataset.py")
        off = result["offline"]
        for key in ("csv_rows", "json_rows", "parquet_rows"):
            self.assertEqual(off[key], 10)
        self.assertEqual(off["splits"], ["test", "train"])
        self.assertGreater(off["cache_arrow_files"], 0)

    def test_map_offline(self):
        result = self._run("lessons/02_map/example_map.py")
        self.assertTrue(result["fingerprint_reused"])
        self.assertEqual(result["num_proc_rows"], 64)
        self.assertEqual(result["tokenized_columns"], ["id", "label", "input_ids"])
        self.assertEqual(result["numpy_shape"], [4, 8])

    def test_streaming_offline(self):
        result = self._run("lessons/03_streaming/example_streaming.py")
        self.assertEqual(result["take_skip"]["head"], [0, 1, 2, 3, 4])
        self.assertEqual(result["interleave"]["round_robin"], ["local", "extra"] * 3)
        self.assertEqual(result["to_iterable_shards"], 3)
        self.assertEqual(result["arrow_cache_files"], 0)


if __name__ == "__main__":
    unittest.main()
