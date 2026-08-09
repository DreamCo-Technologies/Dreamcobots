import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROGRAM = ROOT / "config" / "buddy-full-potential-sandbox-open-source-evolution-program.json"
CATALOG = ROOT / "config" / "generated" / "full-potential-sandbox-catalog.json"


class FullPotentialSandboxTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.program = json.loads(PROGRAM.read_text(encoding="utf-8"))
        subprocess.run([sys.executable, str(ROOT / "tools" / "build_full_potential_sandbox_catalog.py")], check=True, cwd=ROOT)
        cls.catalog = json.loads(CATALOG.read_text(encoding="utf-8"))

    def test_thousands_of_categories_exist(self):
        self.assertGreaterEqual(self.catalog["category_count"], 5000)
        self.assertGreaterEqual(self.catalog["test_family_count"], 50)
        self.assertGreaterEqual(self.catalog["axis_count"], 10)

    def test_categories_are_unique(self):
        ids = [row["category_id"] for row in self.catalog["categories"]]
        self.assertEqual(len(ids), len(set(ids)))

    def test_repair_loop_is_evidence_first(self):
        loop = " ".join(self.program["broken_bot_repair_loop"]["steps"]).lower()
        for phrase in ["failing evidence", "reproduce smallest", "canonical owner", "root-cause", "regression fixture", "before/after"]:
            self.assertIn(phrase, loop)

    def test_repair_loop_cannot_cheat(self):
        never = " ".join(self.program["broken_bot_repair_loop"]["never"]).lower()
        for phrase in ["delete failing tests", "weaken required thresholds", "hide errors", "self-merge unverified"]:
            self.assertIn(phrase, never)

    def test_open_source_evolution_has_model_data_library_and_runtime_coverage(self):
        targets = " ".join(self.program["open_source_evolution"]["discovery_targets"]).lower()
        for phrase in ["open-weight language models", "open datasets", "agent frameworks", "inference engines", "training/fine-tuning frameworks", "evaluation frameworks", "robotics", "game ai"]:
            self.assertIn(phrase, targets)
        source_policy = " ".join(self.program["open_source_evolution"]["source_policy"]).lower()
        self.assertIn("license", source_policy)
        self.assertIn("provenance", source_policy)

    def test_full_potential_stays_inside_safety_boundaries(self):
        rule = self.program["full_potential_rule"].lower()
        for phrase in ["safety", "permission", "legal", "cost", "resource"]:
            self.assertIn(phrase, rule)


if __name__ == "__main__":
    unittest.main()
