import hashlib
import tempfile
import unittest
from pathlib import Path

from buddy.learning.model_foundry import (
    SCHEMA, build_parallel_plan, validate_manifest
)


class ModelFoundryRightsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.data = self.root / "owned.txt"
        self.data.write_text(("DreamCo original training example. " * 40), encoding="utf-8")
        self.entry = {
            "dataset_id": "dreamco-owner-authored-fixture-v1",
            "local_path": "owned.txt",
            "sha256": hashlib.sha256(self.data.read_bytes()).hexdigest(),
            "owner": "DreamCo",
            "owner_attestation_ref": "owner-attestation:fixture",
            "license_id": "DreamCo-First-Party-Internal-v1",
            "license_evidence_ref": "internal-policy:fixture",
            "rights_status": "APPROVED",
            "approved_division_ids": [1, 2],
            "training_strategy": "domain_adaptive_pretraining",
            "permissions": {
                "training": True,
                "commercial_model_use": True,
                "derivative_models": True,
                "redistribution": False
            }
        }

    def tearDown(self):
        self.temp.cleanup()

    def test_approved_first_party_dataset_passes_hash_and_scope_checks(self):
        approved = validate_manifest({"schema": SCHEMA, "datasets": [self.entry]}, self.root)
        self.assertEqual(len(approved), 1)
        self.assertEqual(approved[0]["dataset_id"], self.entry["dataset_id"])

    def test_unknown_rights_and_training_permission_are_blocked(self):
        unknown = {**self.entry, "rights_status": "UNVERIFIED"}
        self.assertEqual(validate_manifest({"schema": SCHEMA, "datasets": [unknown]}, self.root), [])
        no_training = {**self.entry, "permissions": {**self.entry["permissions"], "training": False}}
        self.assertEqual(validate_manifest({"schema": SCHEMA, "datasets": [no_training]}, self.root), [])

    def test_hash_mismatch_fails_closed(self):
        bad = {**self.entry, "sha256": "0" * 64}
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            validate_manifest({"schema": SCHEMA, "datasets": [bad]}, self.root)

    def test_path_traversal_is_rejected(self):
        bad = {**self.entry, "local_path": "../outside.txt"}
        with self.assertRaisesRegex(ValueError, "escapes"):
            validate_manifest({"schema": SCHEMA, "datasets": [bad]}, self.root)

    def test_parallel_plan_covers_all_65_and_only_eligible_divisions(self):
        registry = {"divisions": [{"id": i, "name": f"Division{i}"} for i in range(1, 66)]}
        approved = [
            {**self.entry, "approved_division_ids": [1], "training_strategy": "domain_adaptive_pretraining", "_resolved_path": str(self.data)},
            {**self.entry, "dataset_id": "second-fixture", "approved_division_ids": [2], "training_strategy": "code_and_tool_sequence_modeling", "_resolved_path": str(self.data)},
        ]
        plan = build_parallel_plan(registry, approved)
        self.assertEqual(plan["division_count"], 65)
        self.assertEqual(plan["eligible_divisions"], 2)
        self.assertEqual(plan["blocked_divisions"], 63)
        self.assertEqual([row["division_id"] for row in plan["include"]], [1, 2])
        self.assertEqual(plan["include"][0]["strategy"], "domain_adaptive_pretraining")
        self.assertEqual(plan["include"][1]["strategy"], "code_and_tool_sequence_modeling")

    def test_duplicate_dataset_ids_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "unique"):
            validate_manifest({"schema": SCHEMA, "datasets": [self.entry, self.entry]}, self.root)


if __name__ == "__main__":
    unittest.main()
