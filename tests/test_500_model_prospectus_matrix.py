import importlib
import json
import tempfile
import unittest
from pathlib import Path


def verified_models(count=3):
    return {
        "status": "VERIFIED",
        "expected_model_count": 500,
        "models": [{
            "model_id": f"provider/model-{i:03d}",
            "name": f"Model {i:03d}",
            "provider": "ExampleProvider",
            "model_revision": f"sha256:{i:064x}",
            "adapter_id": "example-adapter-v1",
            "model_card_uri": f"https://example.org/models/{i}",
            "access_status": "AVAILABLE",
            "license_review_status": "APPROVED",
            "evaluation_authorized": True,
            "benchmark_suites": ["hallucination", "privacy"],
            "review_record_id": f"review-{i:03d}",
        } for i in range(1, count + 1)],
    }


class Build500ModelProspectusMatrixTests(unittest.TestCase):
    def _run_with_temp_root(self, module, root, catalog_path):
        (root / "website" / "data").mkdir(parents=True, exist_ok=True)
        (root / "config" / "buddy").mkdir(parents=True, exist_ok=True)
        (root / "config" / "buddy" / "500-model-registry.json").write_text(
            json.dumps({
                "model_count": 500,
                "id_pattern": "buddy-model-{slot:03d}",
                "slots": {"start": 1, "end": 500},
            }) + "\n",
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
            "EVIDENCE_CANDIDATES": module.EVIDENCE_CANDIDATES,
        }
        try:
            module.ROOT = root
            module.OUT = root / "website" / "data" / "buddy-500-model-prospectus-matrix.json"
            module.CATALOG_CANDIDATES = [catalog_path]
            module.SUITE_CANDIDATES = [root / "config" / "buddy" / "trust-benchmark-suite.json"]
            module.EVIDENCE_CANDIDATES = [root / "config" / "generated" / "missing-evidence.json"]
            self.assertEqual(module.main(), 0)
            return json.loads(module.OUT.read_text(encoding="utf-8"))
        finally:
            module.ROOT = original["ROOT"]
            module.OUT = original["OUT"]
            module.CATALOG_CANDIDATES = original["CATALOG_CANDIDATES"]
            module.SUITE_CANDIDATES = original["SUITE_CANDIDATES"]
            module.EVIDENCE_CANDIDATES = original["EVIDENCE_CANDIDATES"]

    def test_placeholder_registry_never_becomes_model_inventory(self) -> None:
        module = importlib.import_module("tools.build_500_model_prospectus_matrix")
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            registry = root / "config" / "buddy" / "500-model-registry.json"
            registry.parent.mkdir(parents=True)
            registry.write_text(json.dumps({
                "model_count": 500,
                "id_pattern": "buddy-model-{slot:03d}",
                "slots": {"start": 1, "end": 500},
            }) + "\n", encoding="utf-8")
            output = self._run_with_temp_root(module, root, registry)
            self.assertEqual(output["status"], "BLOCKED_NO_VERIFIED_500_MODEL_INVENTORY")
            self.assertEqual(output["prospective_slots_not_models"], 500)
            self.assertEqual(output["catalogued_models"], 0)
            self.assertEqual(output["matrix_rows"], 0)
            self.assertEqual(output["verified_rows"], 0)

    def test_only_rights_reviewed_model_records_enter_matrix(self) -> None:
        module = importlib.import_module("tools.build_500_model_prospectus_matrix")
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            catalog = root / "config" / "verified-model-inventory.json"
            catalog.parent.mkdir(parents=True)
            inventory = verified_models(3)
            inventory["models"][1]["license_review_status"] = "PENDING"
            catalog.write_text(json.dumps(inventory) + "\n", encoding="utf-8")
            output = self._run_with_temp_root(module, root, catalog)
            self.assertEqual(output["status"], "READY_WITH_VERIFIED_MODEL_RECORDS")
            self.assertEqual(output["catalogued_models"], 2)
            self.assertEqual(output["matrix_rows"], 4)
            self.assertEqual(output["unverified_rows"], 4)
            self.assertEqual(output["matrix"][0]["model_id"], "provider/model-001")
            self.assertEqual(output["matrix"][0]["benchmark_suite"], "hallucination")


if __name__ == "__main__":
    unittest.main()
