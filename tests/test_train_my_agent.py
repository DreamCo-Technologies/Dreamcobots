import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.dreamco_model_foundry import build_buyer_foundry_kit, load_divisions
from scripts.train_my_agent import preflight


class TrainMyAgentTests(unittest.TestCase):
    def _kit(self, root):
        return build_buyer_foundry_kit("45m-edge", load_divisions()[0], root / "kits")

    def _manifest(self, root, *, sha_override=None, evidence_reference="data/approved.jsonl", privacy_review="PASSED", retention=True):
        snapshot = root / "data" / "approved.jsonl"
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        snapshot.write_text('{"instruction":"synthetic fixture","output":"approved"}\n', encoding="utf-8")
        digest = sha_override or hashlib.sha256(snapshot.read_bytes()).hexdigest()
        entry = {
            "id": "fixture-dataset-001",
            "training_approved": True,
            "rights_status": "APPROVED",
            "content_rights_verified": True,
            "privacy_review": privacy_review,
            "retention_policy": "Delete the approved snapshot after the documented retention window.",
            "retention_evidence": "owner-approved-retention-record",
            "rights_evidence_reference": "owner-approved-rights-record",
            "sha256": digest,
            "evidence_reference": evidence_reference,
        }
        if not retention:
            entry.pop("retention_evidence")
        manifest_path = root / "authorized-manifest.json"
        manifest_path.write_text(json.dumps({"datasets": [entry]}), encoding="utf-8")
        return manifest_path

    def _hardware(self):
        return {"candidate_tiers": ["45m-edge"], "selection_is_advisory": True}

    def test_preflight_never_starts_training_without_approved_data_and_backend(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            kit = self._kit(root)
            result = preflight(
                kit, execute=True, dataset_manifest_path=root / "missing.json",
                repository_root=root, hardware_info=self._hardware(),
            )
            self.assertEqual(result["status"], "BLOCKED")
            self.assertFalse(result["training_started"])
            self.assertFalse(result["paid_compute_requested"])
            self.assertFalse(result["customer_data_uploaded"])
            self.assertTrue(result["blockers"])

    def test_manifest_weight_violation_returns_structured_blocker(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            kit = self._kit(root)
            path = kit / "BUYER_MANIFEST.json"
            manifest = json.loads(path.read_text(encoding="utf-8"))
            manifest["weights_included"] = True
            path.write_text(json.dumps(manifest), encoding="utf-8")
            result = preflight(
                kit, dataset_manifest_path=root / "missing.json",
                repository_root=root, hardware_info=self._hardware(),
            )
            self.assertEqual(result["status"], "BLOCKED")
            self.assertIn("Buyer kit weight-status contract failed", result["blockers"])

    def test_valid_local_snapshot_passes_data_admission_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            kit = self._kit(root)
            manifest = self._manifest(root)
            result = preflight(
                kit, dataset_manifest_path=manifest, repository_root=root,
                hardware_info=self._hardware(),
            )
            self.assertEqual(result["status"], "READY_FOR_BACKEND_REVIEW")
            self.assertEqual(result["approved_dataset_count"], 1)
            self.assertFalse(result["training_started"])

    def test_snapshot_hash_mismatch_blocks_admission(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            kit = self._kit(root)
            manifest = self._manifest(root, sha_override="0" * 64)
            result = preflight(
                kit, dataset_manifest_path=manifest, repository_root=root,
                hardware_info=self._hardware(),
            )
            self.assertEqual(result["status"], "BLOCKED")
            self.assertTrue(any("SHA-256 does not match" in x for x in result["blockers"]))

    def test_path_traversal_reference_is_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            kit = self._kit(root)
            manifest = self._manifest(root, evidence_reference="../outside.jsonl")
            result = preflight(
                kit, dataset_manifest_path=manifest, repository_root=root,
                hardware_info=self._hardware(),
            )
            self.assertEqual(result["status"], "BLOCKED")
            self.assertTrue(any("does not resolve" in x for x in result["blockers"]))

    def test_privacy_and_retention_evidence_are_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            kit = self._kit(root)
            manifest = self._manifest(root, privacy_review="NOT_REVIEWED", retention=False)
            result = preflight(
                kit, dataset_manifest_path=manifest, repository_root=root,
                hardware_info=self._hardware(),
            )
            self.assertEqual(result["status"], "BLOCKED")
            self.assertTrue(any("privacy_review" in x for x in result["blockers"]))
            self.assertTrue(any("retention_evidence" in x for x in result["blockers"]))


if __name__ == "__main__":
    unittest.main()
