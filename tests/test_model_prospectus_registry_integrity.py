"""Regression tests for canonical model/suite identity and slot accounting."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools import build_500_model_prospectus_matrix as prospectus


class ModelProspectusRegistryIntegrityTests(unittest.TestCase):
    def run_case(self, catalog, suites, *, expected_error=None):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "models.json").write_text(json.dumps(catalog))
            (root / "suites.json").write_text(json.dumps(suites))
            output = root / "matrix.json"
            with (patch.object(prospectus, "CATALOG_CANDIDATES", [root / "models.json"]),
                  patch.object(prospectus, "SUITE_CANDIDATES", [root / "suites.json"]),
                  patch.object(prospectus, "EVIDENCE_CANDIDATES", [root / "absent.json"]),
                  patch.object(prospectus, "OUT", output)):
                if expected_error:
                    with self.assertRaisesRegex(ValueError, expected_error):
                        prospectus.main()
                    self.assertFalse(output.exists())
                    return None
                self.assertEqual(prospectus.main(), 0)
            return json.loads(output.read_text())

    def test_duplicate_model_identity_fails_closed(self):
        self.run_case({"models": [{"model_id": "same"}, {"model_id": "same"}]},
                      {"suites": [{"benchmark_id": "trust"}]}, expected_error="duplicate model")

    def test_duplicate_suite_identity_fails_closed(self):
        self.run_case({"models": [{"model_id": "m1"}]},
                      {"suites": [{"benchmark_id": "trust"}, {"benchmark_id": "trust"}]},
                      expected_error="duplicate benchmark suite")

    def test_empty_model_registry_does_not_emit_zero_row_success(self):
        self.run_case({"models": []}, {"suites": [{"benchmark_id": "trust"}]},
                      expected_error="model registry must contain")

    def test_missing_suite_identity_fails_closed(self):
        self.run_case({"models": [{"model_id": "m1"}]}, {"suites": [{}]},
                      expected_error="no usable identity")

    def test_slot_count_mismatch_fails_closed(self):
        self.run_case({"model_count": 500, "id_pattern": "buddy-model-{slot:03d}",
                       "slots": {"start": 1, "end": 499}},
                      {"domains": ["trust"]}, expected_error="slot range must match")

    def test_malformed_model_row_cannot_disappear_silently(self):
        self.run_case({"models": [{"model_id": "m1"}, None]},
                      {"suites": [{"benchmark_id": "trust"}]},
                      expected_error="registry entries must be objects")

    def test_blank_benchmark_domain_cannot_disappear_silently(self):
        self.run_case({"models": [{"model_id": "m1"}]},
                      {"domains": ["trust", ""]},
                      expected_error="benchmark domains must be nonblank")

    def test_valid_canonical_shape_preserves_all_7500_unverified_rows(self):
        data = self.run_case({"model_count": 500, "id_pattern": "buddy-model-{slot:03d}",
                              "slots": {"start": 1, "end": 500}},
                             {"domains": [f"suite_{i}" for i in range(15)]})
        self.assertEqual(data["catalogued_models"], 500)
        self.assertEqual(data["registered_benchmark_suites"], 15)
        self.assertEqual(data["matrix_rows"], 7500)
        self.assertEqual(data["verified_rows"], 0)
        self.assertEqual(data["unverified_rows"], 7500)


if __name__ == "__main__":
    unittest.main()
