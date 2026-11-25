import hashlib
import tempfile
import unittest
from pathlib import Path

from buddy.learning.model_foundry import (
    SCHEMA, STRATEGY_PROFILES, build_parallel_plan, validate_manifest,
    train_from_scratch, validate_training_authorization,
)


class ModelFoundryRightsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.data = self.root / "owned.txt"
        self.data.write_text(("DreamCo original training example. " * 40), encoding="utf-8")
        self.owner_evidence = self.root / "owner-attestation.txt"
        self.owner_evidence.write_text("Owner created and controls this fixture.", encoding="utf-8")
        self.license_evidence = self.root / "license-evidence.txt"
        self.license_evidence.write_text("Explicit training, commercial and derivative permissions.", encoding="utf-8")
        self.entry = {
            "dataset_id": "dreamco-owner-authored-fixture-v1",
            "local_path": "owned.txt",
            "sha256": hashlib.sha256(self.data.read_bytes()).hexdigest(),
            "owner": "DreamCo",
            "owner_attestation_ref": "owner-attestation:fixture",
            "owner_attestation_path": "owner-attestation.txt",
            "owner_attestation_sha256": hashlib.sha256(self.owner_evidence.read_bytes()).hexdigest(),
            "license_id": "DreamCo-First-Party-Internal-v1",
            "license_evidence_ref": "internal-policy:fixture",
            "license_evidence_path": "license-evidence.txt",
            "license_evidence_sha256": hashlib.sha256(self.license_evidence.read_bytes()).hexdigest(),
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

    def test_training_profiles_use_distinct_experiment_settings(self):
        self.assertGreaterEqual(len(STRATEGY_PROFILES), 8)
        settings = {(p["sequence_length"], p["batch_size"], p["learning_rate"]) for p in STRATEGY_PROFILES.values()}
        self.assertGreater(len(settings), 1)

    def test_unsupported_training_strategy_is_blocked(self):
        bad = {**self.entry, "training_strategy": "unknown_or_unimplemented"}
        self.assertEqual(validate_manifest({"schema": SCHEMA, "datasets": [bad]}, self.root), [])

    def test_duplicate_dataset_ids_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "unique"):
            validate_manifest({"schema": SCHEMA, "datasets": [self.entry, self.entry]}, self.root)

    
    def test_25m_architecture_profile_parameter_count_is_exact(self):
        from buddy.learning.model_foundry import estimate_decoder_parameter_count
        profile = {
            "vocab_size": 256, "context_size": 256, "width": 640,
            "layers": 5, "attention_heads": 10, "feed_forward_size": 2560,
            "tied_embeddings": True, "bias": True,
        }
        self.assertEqual(estimate_decoder_parameter_count(profile), 24_946_560)

    def test_untied_output_head_adds_one_vocabulary_matrix(self):
        from buddy.learning.model_foundry import estimate_decoder_parameter_count
        tied = {
            "vocab_size": 256, "context_size": 128, "width": 128,
            "layers": 2, "attention_heads": 4, "feed_forward_size": 512,
            "tied_embeddings": True, "bias": True,
        }
        untied = {**tied, "tied_embeddings": False}
        self.assertEqual(
            estimate_decoder_parameter_count(untied) - estimate_decoder_parameter_count(tied),
            256 * 128,
        )

    def test_invalid_architecture_geometry_is_rejected(self):
        from buddy.learning.model_foundry import estimate_decoder_parameter_count
        invalid = {
            "vocab_size": 256, "context_size": 128, "width": 128,
            "layers": 2, "attention_heads": 3, "feed_forward_size": 512,
        }
        with self.assertRaisesRegex(ValueError, "divisible"):
            estimate_decoder_parameter_count(invalid)


    def _training_profile(self):
        return {
            "schema": "dreamco.buddy_cpu_llm_architecture_profile.v1",
            "training_policy": {
                "enabled": True,
                "weight_updates_authorized": True,
                "paid_compute_authorized": False,
                "external_data_allowed": False,
                "requires_rights_cleared_local_dataset": True,
                "requires_explicit_training_approval": True,
                "approved_by": "DreamCo owner",
                "authorization_reference": "owner-approval-2026-001",
                "approved_at": "2026-11-25T08:00:00Z",
            },
        }

    def test_profiled_weight_updates_require_profile_and_runtime_approval(self):
        blocked = {
            "schema": "dreamco.buddy_cpu_llm_architecture_profile.v1",
            "training_policy": {"enabled": False, "weight_updates_authorized": False},
        }
        with self.assertRaisesRegex(PermissionError, "not enabled and authorized"):
            validate_training_authorization(
                blocked, explicit_authorization=True,
                authorization_reference="owner-approval-2026-001", approved_by="DreamCo owner"
            )
        approved = self._training_profile()
        with self.assertRaisesRegex(PermissionError, "explicit --authorize-weight-updates"):
            validate_training_authorization(
                approved, authorization_reference="owner-approval-2026-001", approved_by="DreamCo owner"
            )
        with self.assertRaisesRegex(PermissionError, "match the authorization"):
            validate_training_authorization(
                approved, explicit_authorization=True,
                authorization_reference="different-reference", approved_by="DreamCo owner"
            )
        self.assertIsNone(validate_training_authorization(
            approved, explicit_authorization=True,
            authorization_reference="owner-approval-2026-001", approved_by="DreamCo owner"
        ))

    def test_training_function_fails_closed_without_profile_or_dataset_manifest(self):
        with self.assertRaisesRegex(PermissionError, "versioned explicit training profile"):
            train_from_scratch(
                self.data, self.root / "checkpoint.pt", dataset_id=self.entry["dataset_id"],
                division_id=1, strategy="domain_adaptive_pretraining", seed=1,
            )
        with self.assertRaisesRegex(PermissionError, "approved dataset manifest"):
            train_from_scratch(
                self.data, self.root / "checkpoint.pt", dataset_id=self.entry["dataset_id"],
                division_id=1, strategy="domain_adaptive_pretraining", seed=1,
                architecture_profile=self._training_profile(),
                explicit_training_authorization=True,
                authorization_reference="owner-approval-2026-001",
                approved_by="DreamCo owner",
            )


if __name__ == "__main__":
    unittest.main()
