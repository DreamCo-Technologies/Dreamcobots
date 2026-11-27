from __future__ import annotations

import hashlib
import json
import struct
import tempfile
import unittest
from pathlib import Path

from tools.verify_45m_checkpoints import EXPECTED_PARAMETERS, safetensors_parameter_count, validate_division


def write_safetensors(path: Path, parameter_count: int = EXPECTED_PARAMETERS) -> None:
    header = {"weight": {"dtype": "U8", "shape": [parameter_count], "data_offsets": [0, parameter_count]}}
    encoded = json.dumps(header, separators=(",", ":")).encode()
    path.write_bytes(struct.pack("<Q", len(encoded)) + encoded + b"\x01" * parameter_count)


class CheckpointGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.directory = self.root / "buddy-dreamcyber-45m"
        self.directory.mkdir()
        write_safetensors(self.directory / "model.safetensors")
        (self.directory / "tokenizer.json").write_text(json.dumps({
            "version": "1.0", "model": {"type": "WordLevel", "vocab": {"[UNK]": 0, "hello": 1}}
        }))
        checkpoint_hash = hashlib.sha256((self.directory / "model.safetensors").read_bytes()).hexdigest()
        tokenizer_hash = hashlib.sha256((self.directory / "tokenizer.json").read_bytes()).hexdigest()
        (self.directory / "evidence_stamp.json").write_text(json.dumps({
            "steps_completed": 100,
            "parameter_count": EXPECTED_PARAMETERS,
            "training_run_id": "run-test-001",
            "dataset_manifest_sha256": "a" * 64,
            "training_config_sha256": "b" * 64,
            "checkpoint_sha256": checkpoint_hash,
            "tokenizer_sha256": tokenizer_hash,
            "loss_history": [3.2, 2.1, 1.4]
        }))

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_valid_artifacts_are_structurally_verified(self) -> None:
        result = validate_division(self.directory, "dreamcyber")
        self.assertTrue(result["status"].startswith("STRUCTURALLY_VERIFIED"))

    def test_rejects_fewer_than_100_steps(self) -> None:
        path = self.directory / "evidence_stamp.json"
        evidence = json.loads(path.read_text())
        evidence["steps_completed"] = 99
        path.write_text(json.dumps(evidence))
        with self.assertRaisesRegex(ValueError, "steps_completed"):
            validate_division(self.directory, "dreamcyber")

    def test_rejects_non_convergent_loss(self) -> None:
        path = self.directory / "evidence_stamp.json"
        evidence = json.loads(path.read_text())
        evidence["loss_history"] = [1.0, 1.0]
        path.write_text(json.dumps(evidence))
        with self.assertRaisesRegex(ValueError, "convergence"):
            validate_division(self.directory, "dreamcyber")

    def test_rejects_checkpoint_hash_mismatch(self) -> None:
        with (self.directory / "model.safetensors").open("ab") as stream:
            stream.write(b"x")
        with self.assertRaisesRegex(ValueError, "checkpoint_sha256"):
            validate_division(self.directory, "dreamcyber")

    def test_rejects_wrong_parameter_count(self) -> None:
        checkpoint = self.directory / "model.safetensors"
        write_safetensors(checkpoint, 123)
        stamp_path = self.directory / "evidence_stamp.json"
        evidence = json.loads(stamp_path.read_text())
        evidence["checkpoint_sha256"] = hashlib.sha256(checkpoint.read_bytes()).hexdigest()
        stamp_path.write_text(json.dumps(evidence))
        with self.assertRaisesRegex(ValueError, "parameter count"):
            validate_division(self.directory, "dreamcyber")


if __name__ == "__main__":
    unittest.main()
