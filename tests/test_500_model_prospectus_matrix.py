import importlib
import json
import tempfile
import unittest
from pathlib import Path


class Build500ModelProspectusMatrixTests(unittest.TestCase):
    def test_contract_fallback_builds_full_matrix(self) -> None:
        module = importlib.import_module("tools.build_500_model_prospectus_matrix")
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "config" / "buddy").mkdir(parents=True)
            (root / "website" / "data").mkdir(parents=True)
            (root / "config" / "buddy" / "500-model-registry.json").write_text(
                json.dumps(
                    {
                        "model_count": 3,
                        "id_pattern": "buddy-model-{slot:03d}",
                        "slots": {"start": 1, "end": 3},
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            (root / "config" / "buddy" / "trust-benchmark-suite.json").write_text(
                json.dumps({"domains": ["hallucination", "privacy"]}) + "\n",
                encoding="utf-8",
            )
            original = {
                "ROOT": module.ROOT,
                "OUT": module.OUT,
                "CATALOG_CANDIDATES": module.CATALOG_CANDIDATES,
                "SUITE_CANDIDATES": module.SUITE_CANDIDATES,
            }
            try:
                module.ROOT = root
                module.OUT = root / "website" / "data" / "buddy-500-model-prospectus-matrix.json"
                module.CATALOG_CANDIDATES = [root / "config" / "buddy" / "500-model-registry.json"]
                module.SUITE_CANDIDATES = [root / "config" / "buddy" / "trust-benchmark-suite.json"]
                self.assertEqual(module.main(), 0)
                output = json.loads(module.OUT.read_text(encoding="utf-8"))
                self.assertEqual(output["catalogued_models"], 3)
                self.assertEqual(output["registered_benchmark_suites"], 2)
                self.assertEqual(output["matrix_rows"], 6)
                self.assertEqual(output["unverified_rows"], 6)
                self.assertEqual(output["matrix"][0]["model_id"], "buddy-model-001")
                self.assertEqual(output["matrix"][0]["benchmark_suite"], "hallucination")
            finally:
                module.ROOT = original["ROOT"]
                module.OUT = original["OUT"]
                module.CATALOG_CANDIDATES = original["CATALOG_CANDIDATES"]
                module.SUITE_CANDIDATES = original["SUITE_CANDIDATES"]


if __name__ == "__main__":
    unittest.main()
