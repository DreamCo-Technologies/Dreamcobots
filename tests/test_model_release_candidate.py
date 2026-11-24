import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from tools.build_model_release_candidate import build_candidate


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ModelReleaseCandidateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.checkpoint = self.root / "model.pt"
        self.checkpoint.write_bytes(b"synthetic checkpoint bytes for gate tests")
        self.tokenizer = self.root / "tokenizer.json"
        self.tokenizer.write_text('{"type":"byte_level","vocabulary_size":256}', encoding="utf-8")
        self.metadata = self.root / "model.pt.json"
        self.metadata.write_text(json.dumps({
            "model_id": "buddy-division-01-scratch",
            "division_id": 1,
            "dataset_id": "owned-fixture",
            "dataset_sha256": "a" * 64,
            "architecture": {"family": "decoder_only_transformer"},
            "weights_sha256": digest(self.checkpoint),
            "tokenizer_sha256": digest(self.tokenizer),
            "training_status": "trained_experimental_checkpoint_not_certified",
            "initialization": "random",
            "parameter_count": 1000,
            "seed": 42,
            "optimizer": "AdamW",
            "learning_rate": 0.0002,
            "batch_size": 4,
            "total_steps": 100,
            "holdout_loss": 4.2
        }), encoding="utf-8")
        self.evaluation = self.root / "evaluation.json"
        self.evaluation.write_text(json.dumps({
            "status": "PASSED",
            "holdout_independent": True,
            "dataset_sha256": "a" * 64,
            "checkpoint_sha256": digest(self.checkpoint),
            "suite_id": "dreamco-smoke-v1",
            "report_id": "eval-0001"
        }), encoding="utf-8")
        self.manifest = {"datasets": [{
            "dataset_id": "owned-fixture",
            "sha256": "a" * 64,
            "owner": "DreamCo",
            "owner_attestation_ref": "owner-attestation:fixture",
            "license_id": "DreamCo-First-Party-v1",
            "license_evidence_ref": "license-evidence:fixture",
            "rights_status": "APPROVED",
            "permissions": {
                "training": True,
                "commercial_model_use": True,
                "derivative_models": True,
                "redistribution": True
            }
        }]}

    def tearDown(self):
        self.tmp.cleanup()

    def build(self, manifest=None, evaluation_path=None):
        return build_candidate(
            self.checkpoint, self.metadata, self.tokenizer,
            manifest or self.manifest, evaluation_path or self.evaluation,
            "run-123", "abc123"
        )

    def test_candidate_requires_full_rights_and_independent_evaluation(self):
        result = self.build()
        self.assertEqual(result["release_status"], "candidate_requires_human_release_review")
        self.assertFalse(result["storefront_listing"])
        self.assertFalse(result["checkout_enabled"])
        self.assertEqual(result["parameter_count"], 1000)

    def test_missing_redistribution_permission_blocks_candidate(self):
        manifest = json.loads(json.dumps(self.manifest))
        manifest["datasets"][0]["permissions"]["redistribution"] = False
        with self.assertRaisesRegex(ValueError, "redistribution"):
            self.build(manifest=manifest)

    def test_unapproved_rights_block_candidate(self):
        manifest = json.loads(json.dumps(self.manifest))
        manifest["datasets"][0]["rights_status"] = "UNVERIFIED"
        with self.assertRaisesRegex(ValueError, "not APPROVED"):
            self.build(manifest=manifest)

    def test_failed_or_non_independent_evaluation_blocks_candidate(self):
        report = json.loads(self.evaluation.read_text())
        report["status"] = "FAILED"
        self.evaluation.write_text(json.dumps(report))
        with self.assertRaisesRegex(ValueError, "independent evaluation"):
            self.build()

    def test_evaluation_must_reference_exact_checkpoint(self):
        report = json.loads(self.evaluation.read_text())
        report["checkpoint_sha256"] = "0" * 64
        self.evaluation.write_text(json.dumps(report))
        with self.assertRaisesRegex(ValueError, "checkpoint hash"):
            self.build()

    def test_tampered_checkpoint_is_rejected(self):
        self.checkpoint.write_bytes(b"tampered")
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            self.build()


if __name__ == "__main__":
    unittest.main()
