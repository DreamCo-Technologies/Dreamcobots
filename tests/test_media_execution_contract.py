"""CPU-only tests for the isolated Media Foundry execution contract."""
from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path

from stages_08_media_execution_contract import (  # loaded below from the stage path
    Artifact, ExecutionContractError, ExecutionRequest, ResourceRequest, WorkerSpec,
    transition_job_state, validate_execution_request, validate_worker_spec, verify_artifacts,
)

class ExecutionContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "plan.json").write_text('{"status":"planned_not_rendered"}', encoding="utf-8")
        self.worker = WorkerSpec("wan-video-worker", "wan", ("youtube", "movie"), True, 2)
        self.request = ExecutionRequest(
            "job-123", "wan", "youtube", "plan.json",
            hashlib.sha256((self.root / "plan.json").read_bytes()).hexdigest(),
            "outputs", ResourceRequest(gpu_count=1, gpu_memory_mb=12000),
        )

    def tearDown(self):
        self.temp.cleanup()

    def test_valid_gpu_job_contract(self):
        self.assertEqual(validate_execution_request(self.request, self.worker, self.root).name, "plan.json")

    def test_gpu_worker_requires_gpu(self):
        bad = ExecutionRequest(**{**self.request.__dict__, "resources": ResourceRequest()})
        with self.assertRaises(ExecutionContractError):
            validate_execution_request(bad, self.worker, self.root)

    def test_backend_and_media_type_must_match(self):
        bad = ExecutionRequest(**{**self.request.__dict__, "backend": "other"})
        with self.assertRaises(ExecutionContractError):
            validate_execution_request(bad, self.worker, self.root)

    def test_plan_hash_is_verified(self):
        bad = ExecutionRequest(**{**self.request.__dict__, "plan_sha256": "0" * 64})
        with self.assertRaises(ExecutionContractError):
            validate_execution_request(bad, self.worker, self.root)

    def test_worker_spec_rejects_invalid_concurrency(self):
        with self.assertRaises(ExecutionContractError):
            validate_worker_spec(WorkerSpec("worker", "wan", ("movie",), True, 0))

    def test_lifecycle_transitions_are_enforced(self):
        self.assertEqual(transition_job_state("queued", "validating"), "validating")
        self.assertEqual(transition_job_state("running", "succeeded"), "succeeded")
        with self.assertRaises(ExecutionContractError):
            transition_job_state("succeeded", "running")

    def test_artifact_bytes_are_verified(self):
        out = self.root / "outputs"
        out.mkdir()
        payload = b"synthetic video fixture"
        (out / "clip.mp4").write_bytes(payload)
        result = verify_artifacts([{
            "path": "clip.mp4", "sha256": hashlib.sha256(payload).hexdigest(),
            "size_bytes": len(payload), "mime_type": "video/mp4",
        }], out)
        self.assertEqual(result[0].size_bytes, len(payload))

    def test_artifact_path_escape_is_blocked(self):
        outside = self.root / "outside.mp4"
        outside.write_bytes(b"not inside output root")
        out = self.root / "outputs"
        out.mkdir()
        with self.assertRaises(ExecutionContractError):
            verify_artifacts([{
                "path": "../outside.mp4", "sha256": hashlib.sha256(outside.read_bytes()).hexdigest(),
                "size_bytes": outside.stat().st_size, "mime_type": "video/mp4",
            }], out)

    def test_artifact_hash_mismatch_is_blocked(self):
        out = self.root / "outputs"
        out.mkdir()
        (out / "clip.mp4").write_bytes(b"actual")
        with self.assertRaises(ExecutionContractError):
            verify_artifacts([{
                "path": "clip.mp4", "sha256": "0" * 64, "size_bytes": 6, "mime_type": "video/mp4",
            }], out)

if __name__ == "__main__":
    unittest.main()
