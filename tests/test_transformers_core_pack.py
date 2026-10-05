#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import os
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "study_packs" / "transformers"


class TransformersCorePackContractTest(unittest.TestCase):
    def test_sources_are_pinned_and_licensed(self):
        sources = json.loads((PACK / "sources.json").read_text())
        self.assertTrue(sources["hf_models"])
        for model in sources["hf_models"]:
            self.assertRegex(model["revision"], re.compile(r"^[0-9a-f]{40}$"))
            self.assertTrue(model["license"])
            self.assertEqual(model["weights_format"], "safetensors")

    def test_evals_cover_four_modules(self):
        evals = json.loads((PACK / "evals.json").read_text())
        modules = {d["module"] for d in evals["drills"]}
        self.assertEqual(modules, {"pipeline", "auto", "generate", "chat_template"})

    def test_card_keeps_training_off(self):
        card = (PACK / "CARD.md").read_text()
        self.assertIn("train_allowed: false", card)
        self.assertIn("automatic weight download in default CI: no", card)

    def test_evidence_has_a_passing_run(self):
        logs = [json.loads(p.read_text()) for p in (PACK / "evidence").glob("run_*.json")]
        self.assertTrue(any(l["passed"] == l["total"] == 4 for l in logs))


@unittest.skipUnless(
    os.environ.get("TRANSFORMERS_CORE_DRILLS") == "1"
    and importlib.util.find_spec("transformers")
    and importlib.util.find_spec("torch"),
    "set TRANSFORMERS_CORE_DRILLS=1 with torch+transformers installed to run live drills",
)
class TransformersCoreDrillsLiveTest(unittest.TestCase):
    def test_all_drills_pass(self):
        spec = importlib.util.spec_from_file_location("run_drills", PACK / "drills" / "run_drills.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        self.assertEqual(mod.main(["--no-evidence"]), 0)


if __name__ == "__main__":
    unittest.main()
