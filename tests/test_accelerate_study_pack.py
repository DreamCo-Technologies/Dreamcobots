import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "study_packs" / "accelerate"


class AccelerateStudyPackTest(unittest.TestCase):
    def test_structure(self):
        for rel in ["CARD.md", "sources.json", "evals.json", "scripts/smoke_offload.py",
                    "lessons/01_device_maps.md", "lessons/02_offload.md", "lessons/03_multi_gpu.md"]:
            self.assertTrue((PACK / rel).is_file(), rel)

    def test_sources_pinned(self):
        src = json.loads((PACK / "sources.json").read_text())
        lib = src["libraries"][0]
        self.assertEqual(lib["name"], "accelerate")
        self.assertEqual(len(lib["git_commit_sha"]), 40)
        self.assertEqual(lib["license"], "Apache-2.0")
        for m in src["test_models"]:
            self.assertEqual(len(m["revision"]), 40)
        self.assertFalse(src["automatic_weight_download_in_ci"])

    def test_evals_and_truth(self):
        ev = json.loads((PACK / "evals.json").read_text())
        ids = {t["id"] for t in ev["tasks"]}
        self.assertIn("acc.offload.parity", ids)
        self.assertTrue(any(t["requires_gpu"] for t in ev["tasks"]))
        card = (PACK / "CARD.md").read_text()
        self.assertIn("mastery_claimed: false", card)
        self.assertIn("trained_weights_exist: false", card)

    @unittest.skipUnless(
        all(importlib.util.find_spec(m) for m in ("torch", "accelerate", "transformers")),
        "torch/accelerate/transformers not installed",
    )
    def test_smoke_offload(self):
        r = subprocess.run([sys.executable, str(PACK / "scripts" / "smoke_offload.py")],
                           capture_output=True, text=True, timeout=600)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main()
