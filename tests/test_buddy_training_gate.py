import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from buddy.certification.train_original_25m import _authorized_training_input, train


class BuddyTrainingGateTests(unittest.TestCase):
    def _fixture(self, root: Path, **overrides):
        data = root / "train.txt"
        holdout = root / "holdout.txt"
        train_raw = b"DreamCo original licensed training fixture. " * 64
        holdout_raw = b"Independent DreamCo holdout fixture. " * 64
        data.write_bytes(train_raw)
        holdout.write_bytes(holdout_raw)
        spec = {
            "dataset_id": "dreamco-fixture-v1",
            "dataset_sha256": "a" * 64,
            "license": "owner-authored-fixture",
            "model_id": "buddy-original-25m",
            "model_revision": "candidate-1",
            "train_split_sha256": hashlib.sha256(train_raw).hexdigest(),
            "holdout_split_sha256": hashlib.sha256(holdout_raw).hexdigest(),
            "compute_profile": "local_cpu",
            "max_cost_usd": 0,
            "owner_approved": True,
            "dataset_authorized": True,
            "training_execution_approved": True,
        }
        spec.update(overrides)
        authorization = root / "authorization.json"
        authorization.write_text(json.dumps(spec), encoding="utf-8")
        return data, holdout, authorization

    def test_explicit_zero_cost_authorization_is_required_before_training(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            data, holdout, authorization = self._fixture(root, training_execution_approved=False)
            with self.assertRaisesRegex(PermissionError, "training_execution_approved"):
                train(
                    str(data), str(root / "weights"), steps=1,
                    holdout_data_path=str(holdout),
                    authorization_path=str(authorization), context=16,
                )
            self.assertFalse((root / "weights").exists())

    def test_paid_compute_budget_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            data, holdout, authorization = self._fixture(root, max_cost_usd=0.01)
            with self.assertRaisesRegex(PermissionError, "zero-cost"):
                _authorized_training_input(str(data), str(holdout), str(authorization))

    def test_identical_train_and_holdout_splits_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            data, holdout, authorization = self._fixture(root)
            holdout.write_bytes(data.read_bytes())
            spec = json.loads(authorization.read_text(encoding="utf-8"))
            spec["holdout_split_sha256"] = spec["train_split_sha256"]
            authorization.write_text(json.dumps(spec), encoding="utf-8")
            with self.assertRaisesRegex(PermissionError, "independent"):
                _authorized_training_input(str(data), str(holdout), str(authorization))

    def test_train_file_hash_must_match_authorized_split(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            data, holdout, authorization = self._fixture(root)
            data.write_bytes(b"tampered training content")
            with self.assertRaisesRegex(PermissionError, "training split SHA-256"):
                _authorized_training_input(str(data), str(holdout), str(authorization))

    def test_holdout_file_hash_must_match_authorized_split(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            data, holdout, authorization = self._fixture(root)
            holdout.write_bytes(b"tampered holdout content")
            with self.assertRaisesRegex(PermissionError, "holdout split SHA-256"):
                _authorized_training_input(str(data), str(holdout), str(authorization))


if __name__ == "__main__":
    unittest.main()
