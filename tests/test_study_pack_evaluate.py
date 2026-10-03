#!/usr/bin/env python3
"""Checks the hand-authored Hugging Face `evaluate` study pack and Buddy bench map."""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "study_packs" / "evaluate"
STATUSES = {"spec_only", "harness_exists_not_hf_wired", "hf_wired", "missing"}


def _adapter():
    spec = importlib.util.spec_from_file_location("metrics_adapter", PACK / "metrics_adapter.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _offline_env() -> dict:
    env = dict(os.environ)
    env.pop("HF_PACK_ALLOW_NETWORK", None)
    env["HF_HUB_OFFLINE"] = "1"
    return env


class ManifestTest(unittest.TestCase):
    def setUp(self):
        self.index = json.loads((PACK / "index.json").read_text(encoding="utf-8"))

    def test_flags_off(self):
        self.assertEqual(self.index["pack_id"], "evaluate")
        for key in ("train_allowed", "train_in_default_ci", "automatic_download_in_ci",
                    "automatic_weight_download", "covers_entire_huggingface_hub"):
            self.assertFalse(self.index[key], key)
        self.assertEqual(self.index["network_flag"], "HF_PACK_ALLOW_NETWORK")

    def test_files_exist(self):
        self.assertEqual(self.index["count"], len(self.index["lessons"]))
        for lesson in self.index["lessons"]:
            self.assertTrue((PACK / lesson["readme"]).is_file(), lesson["readme"])
            self.assertTrue((PACK / lesson["example"]).is_file(), lesson["example"])
        for rel in self.index["files"]:
            self.assertTrue((PACK / rel).is_file(), rel)

    def test_version_pin_consistent(self):
        sources = json.loads((PACK / "sources.json").read_text(encoding="utf-8"))
        pinned = {p["name"]: p["version"] for p in sources["python_packages"]}
        self.assertEqual(pinned["evaluate"], self.index["library"]["version"])
        self.assertIn(f"evaluate=={pinned['evaluate']}", (PACK / "CARD.md").read_text(encoding="utf-8"))


class BenchMapTest(unittest.TestCase):
    def setUp(self):
        self.map = json.loads((PACK / "bench_map.json").read_text(encoding="utf-8"))

    def test_schema_and_unique_ids(self):
        self.assertEqual(self.map["schema"], "dreamco.evaluate_bench_map.v1")
        ids = [b["id"] for b in self.map["benches"]]
        self.assertEqual(len(ids), len(set(ids)))
        for bench in self.map["benches"]:
            self.assertIn(bench["status"], STATUSES, bench["id"])
            self.assertIsInstance(bench["hf_metrics"], list)

    def test_paths_real_or_marked_missing(self):
        for bench in self.map["benches"]:
            if bench["status"] == "missing":
                self.assertEqual(bench["repo_paths"], [], bench["id"])
                self.assertTrue(bench.get("missing_note"), bench["id"])
                continue
            self.assertTrue(bench["repo_paths"], bench["id"])
            for rel in bench["repo_paths"]:
                self.assertTrue((ROOT / rel).exists(), f"{bench['id']}: {rel}")

    def test_no_bench_claims_hf_wired_without_evidence(self):
        evidence = [p for p in (PACK / "evidence").iterdir() if p.name != "README.md"]
        if not evidence:
            self.assertFalse([b["id"] for b in self.map["benches"] if b["status"] == "hf_wired"])

    def test_code_eval_gated(self):
        code = next(b for b in self.map["benches"] if b["id"] == "f0.code")
        self.assertIn("HF_ALLOW_CODE_EVAL", code["hf_metric_notes"]["code_eval"])


class FallbackMetricsTest(unittest.TestCase):
    def setUp(self):
        self.m = _adapter()
        os.environ.pop("HF_PACK_ALLOW_NETWORK", None)

    def test_exact_match(self):
        self.assertEqual(self.m.exact_match(["a", "B"], ["a", "b"]), 0.5)
        self.assertEqual(self.m.exact_match(["a", "B!"], ["a", "b"], ignore_case=True, ignore_punctuation=True), 1.0)

    def test_accuracy_f1(self):
        self.assertEqual(self.m.accuracy([1, 0, 1, 1], [1, 0, 0, 1]), 0.75)
        self.assertAlmostEqual(self.m.f1([1, 0, 1, 1], [1, 0, 0, 1]), 0.8)
        self.assertEqual(self.m.f1([0, 0], [1, 1]), 0.0)

    def test_pass_at_k(self):
        self.assertEqual(self.m.pass_at_k(5, 0, 1), 0.0)
        self.assertEqual(self.m.pass_at_k(5, 5, 1), 1.0)
        self.assertAlmostEqual(self.m.pass_at_k(5, 2, 1), 0.4)
        self.assertEqual(self.m.pass_at_k(5, 2, 4), 1.0)
        with self.assertRaises(ValueError):
            self.m.pass_at_k(3, 4, 1)

    def test_compute_labels_backend(self):
        out = self.m.compute("accuracy", [1, 1], [1, 0])
        self.assertEqual(out["backend"], "local_fallback")
        self.assertEqual(out["result"]["accuracy"], 0.5)
        with self.assertRaises(RuntimeError):
            self.m.compute("rouge", ["a"], ["a"])

    def test_length_mismatch(self):
        with self.assertRaises(ValueError):
            self.m.accuracy([1], [1, 0])


class LessonExamplesTest(unittest.TestCase):
    def test_examples_pass_offline(self):
        for lesson in json.loads((PACK / "index.json").read_text(encoding="utf-8"))["lessons"]:
            proc = subprocess.run([sys.executable, str(PACK / lesson["example"])], cwd=ROOT,
                                  env=_offline_env(), capture_output=True, text=True, timeout=60)
            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
            self.assertTrue(json.loads(proc.stdout.strip().splitlines()[-1])["ok"], lesson["id"])


if __name__ == "__main__":
    unittest.main()
