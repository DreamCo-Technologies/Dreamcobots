"""CPU-only synthetic model-weight training smoke; never promotes a checkpoint."""
from __future__ import annotations

import hashlib
import os
import tempfile
import unittest
from pathlib import Path

from buddy.learning.model_foundry import SCHEMA, sha256_file, train_from_scratch


class ModelFoundrySyntheticTrainingSmokeTests(unittest.TestCase):
    def _train_and_assert(self, root: Path):
        try:
            import torch
        except ImportError:
            self.skipTest("PyTorch is installed by the model-foundry CI smoke workflow")

        root.mkdir(parents=True, exist_ok=True)
            root.mkdir()
            dataset = root / "synthetic-fixture.txt"
            dataset.write_text(
                ("DreamCo synthetic language model training fixture. "
                 "Buddy routes work through divisions and validates evidence. " * 100),
                encoding="utf-8",
            )
            owner = root / "owner-attestation.txt"
            owner.write_text("Synthetic fixture authored for this CI test only.", encoding="utf-8")
            license_evidence = root / "license-evidence.txt"
            license_evidence.write_text(
                "No third-party text. Synthetic fixture permitted for this CI-only training smoke.",
                encoding="utf-8",
            )
            digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
            dataset_id = "dreamco-synthetic-model-foundry-ci-v1"
            manifest = {
                "schema": SCHEMA,
                "datasets": [{
                    "dataset_id": dataset_id,
                    "local_path": dataset.name,
                    "sha256": digest(dataset),
                    "owner": "DreamCo CI fixture",
                    "owner_attestation_ref": "ci-synthetic-owner-attestation-v1",
                    "owner_attestation_path": owner.name,
                    "owner_attestation_sha256": digest(owner),
                    "license_id": "DreamCo-Synthetic-CI-Only-v1",
                    "license_evidence_ref": "ci-synthetic-license-evidence-v1",
                    "license_evidence_path": license_evidence.name,
                    "license_evidence_sha256": digest(license_evidence),
                    "rights_status": "APPROVED",
                    "approved_division_ids": [1],
                    "training_strategy": "domain_adaptive_pretraining",
                    "permissions": {
                        "training": True,
                        "commercial_model_use": True,
                        "derivative_models": True,
                        "redistribution": False,
                    },
                }],
            }
            profile = {
                "schema": "dreamco.buddy_cpu_llm_architecture_profile.v1",
                "profile_id": "synthetic-ci-smoke-only",
                "training_policy": {
                    "enabled": True,
                    "weight_updates_authorized": True,
                    "paid_compute_authorized": False,
                    "external_data_allowed": False,
                    "requires_rights_cleared_local_dataset": True,
                    "requires_explicit_training_approval": True,
                    "approved_by": "CI synthetic smoke harness",
                    "authorization_reference": "ci-synthetic-training-approval-v1",
                    "approved_at": "2026-11-25T00:00:00Z",
                },
            }
            checkpoint = root / "checkpoints" / "division-001-synthetic.pt"
            result = train_from_scratch(
                dataset,
                checkpoint,
                dataset_id=dataset_id,
                division_id=1,
                strategy="domain_adaptive_pretraining",
                seed=7,
                steps=2,
                architecture_profile=profile,
                authorization_manifest=manifest,
                data_root=root,
                explicit_training_authorization=True,
                authorization_reference="ci-synthetic-training-approval-v1",
                approved_by="CI synthetic smoke harness",
            )

            self.assertTrue(checkpoint.is_file())
            self.assertTrue(checkpoint.with_suffix(".pt.json").is_file())
            self.assertEqual(result["training_status"], "trained_experimental_checkpoint_not_certified")
            self.assertFalse(result["holdout_used_for_training"])
            self.assertEqual(result["dataset_id"], dataset_id)
            self.assertEqual(result["steps"], 2)
            self.assertEqual(result["weights_sha256"], sha256_file(checkpoint))
            saved = torch.load(checkpoint, map_location="cpu", weights_only=False)
        self.assertEqual(saved["metadata"]["dataset_id"], dataset_id)
        self.assertEqual(saved["metadata"]["training_status"], "trained_experimental_checkpoint_not_certified")

    def test_authorized_synthetic_fixture_trains_and_saves_unpromoted_checkpoint(self):
        output = os.environ.get("DREAMCO_MODEL_FOUNDRY_SMOKE_OUTPUT")
        if output:
            self._train_and_assert(Path(output).resolve() / "private")
        else:
            with tempfile.TemporaryDirectory() as temp:
                self._train_and_assert(Path(temp) / "private")


if __name__ == "__main__":
    unittest.main()
