"""Provider-neutral contract for isolated media execution workers.

This module defines validation and lifecycle rules only. It does not start containers,
invoke shell commands, allocate GPUs, download checkpoints, or bypass the Media Director's
canonical asset-consent and model-license gates.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Protocol, Sequence

JOB_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
SHA256_RE = re.compile(r"^[a-f0-9]{64}$")
MIME_ALLOWLIST = frozenset({
    "video/mp4", "video/webm", "audio/wav", "audio/mpeg",
    "audio/flac", "image/png", "image/jpeg", "image/webp",
    "application/json", "text/vtt", "text/plain",
})
JOB_STATES = frozenset({"queued", "validating", "running", "succeeded", "failed", "cancelled"})
TERMINAL_STATES = frozenset({"succeeded", "failed", "cancelled"})
TRANSITIONS = {
    "queued": frozenset({"validating", "cancelled"}),
    "validating": frozenset({"running", "failed", "cancelled"}),
    "running": frozenset({"succeeded", "failed", "cancelled"}),
    "succeeded": frozenset(),
    "failed": frozenset(),
    "cancelled": frozenset(),
}


class ExecutionContractError(ValueError):
    """Raised when a job or worker violates the execution contract."""


@dataclass(frozen=True)
class ResourceRequest:
    gpu_count: int = 0
    gpu_memory_mb: int = 0
    cpu_cores: int = 2
    memory_mb: int = 4096
    timeout_seconds: int = 1800


@dataclass(frozen=True)
class WorkerSpec:
    worker_id: str
    backend: str
    supported_media_types: tuple[str, ...]
    gpu_required: bool
    max_concurrency: int
    max_timeout_seconds: int = 7200


@dataclass(frozen=True)
class ExecutionRequest:
    job_id: str
    backend: str
    media_type: str
    plan_path: str
    plan_sha256: str
    output_dir: str
    resources: ResourceRequest


@dataclass(frozen=True)
class ExecutionContext:
    workspace_root: Path
    output_root: Path
    cancellation_requested: bool = False


@dataclass(frozen=True)
class Artifact:
    path: str
    sha256: str
    size_bytes: int
    mime_type: str


class ExecutionAdapter(Protocol):
    """Implementations must execute in an isolated worker, never in the API process."""

    def execute(
        self, request: ExecutionRequest, context: ExecutionContext
    ) -> Sequence[Mapping[str, Any]]:
        """Return artifact metadata; the orchestrator verifies bytes and path boundaries."""


def _contained_file(root: Path, relative_path: str) -> Path:
    unresolved = root / relative_path
    if unresolved.is_symlink():
        raise ExecutionContractError("symlink_paths_are_blocked")
    candidate = unresolved.resolve()
    if root.resolve() not in candidate.parents:
        raise ExecutionContractError("path_escapes_configured_root")
    if not candidate.is_file():
        raise ExecutionContractError("path_must_be_regular_file")
    return candidate


def validate_worker_spec(spec: WorkerSpec) -> None:
    if not JOB_ID_RE.fullmatch(spec.worker_id):
        raise ExecutionContractError("invalid_worker_id")
    if not JOB_ID_RE.fullmatch(spec.backend):
        raise ExecutionContractError("invalid_backend_id")
    if not spec.supported_media_types or any(
        media_type not in {"youtube", "movie", "music", "image", "audio"}
        for media_type in spec.supported_media_types
    ):
        raise ExecutionContractError("unsupported_media_type_capability")
    if not 1 <= spec.max_concurrency <= 128:
        raise ExecutionContractError("max_concurrency_out_of_range")
    if not 1 <= spec.max_timeout_seconds <= 86400:
        raise ExecutionContractError("max_timeout_seconds_out_of_range")


def validate_execution_request(
    request: ExecutionRequest,
    worker: WorkerSpec,
    workspace_root: str | Path,
) -> Path:
    validate_worker_spec(worker)
    if not JOB_ID_RE.fullmatch(request.job_id):
        raise ExecutionContractError("invalid_job_id")
    if request.backend != worker.backend:
        raise ExecutionContractError("backend_mismatch")
    if request.media_type not in worker.supported_media_types:
        raise ExecutionContractError("media_type_not_supported_by_worker")
    resources = request.resources
    if not 1 <= resources.cpu_cores <= 128 or not 256 <= resources.memory_mb <= 1_048_576:
        raise ExecutionContractError("cpu_or_memory_request_out_of_range")
    if not 1 <= resources.timeout_seconds <= min(worker.max_timeout_seconds, 86400):
        raise ExecutionContractError("timeout_out_of_range")
    if not 0 <= resources.gpu_count <= 8 or not 0 <= resources.gpu_memory_mb <= 1_048_576:
        raise ExecutionContractError("gpu_request_out_of_range")
    if worker.gpu_required and resources.gpu_count < 1:
        raise ExecutionContractError("worker_requires_gpu")
    if not worker.gpu_required and resources.gpu_count != 0:
        raise ExecutionContractError("cpu_worker_cannot_request_gpu")
    if not SHA256_RE.fullmatch(request.plan_sha256):
        raise ExecutionContractError("invalid_plan_sha256")
    root = Path(workspace_root).resolve()
    plan_file = _contained_file(root, request.plan_path)
    digest = hashlib.sha256(plan_file.read_bytes()).hexdigest()
    if digest != request.plan_sha256:
        raise ExecutionContractError("plan_hash_mismatch")
    return plan_file


def transition_job_state(current: str, target: str) -> str:
    if current not in JOB_STATES or target not in JOB_STATES:
        raise ExecutionContractError("unknown_job_state")
    if target not in TRANSITIONS[current]:
        raise ExecutionContractError(f"invalid_job_state_transition:{current}->{target}")
    return target


def verify_artifacts(
    artifacts: Sequence[Mapping[str, Any]], output_root: str | Path
) -> tuple[Artifact, ...]:
    if not artifacts:
        raise ExecutionContractError("execution_returned_no_artifacts")
    root = Path(output_root).resolve()
    verified: list[Artifact] = []
    seen: set[str] = set()
    for raw in artifacts:
        try:
            relative = str(raw["path"])
            expected_hash = str(raw["sha256"])
            expected_size = int(raw["size_bytes"])
            mime_type = str(raw["mime_type"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ExecutionContractError("malformed_artifact_manifest") from exc
        if relative in seen:
            raise ExecutionContractError("duplicate_artifact_path")
        seen.add(relative)
        if not SHA256_RE.fullmatch(expected_hash):
            raise ExecutionContractError("invalid_artifact_sha256")
        if expected_size <= 0:
            raise ExecutionContractError("empty_artifact_blocked")
        if mime_type not in MIME_ALLOWLIST:
            raise ExecutionContractError("artifact_mime_type_not_allowlisted")
        artifact_path = _contained_file(root, relative)
        if artifact_path.stat().st_size != expected_size:
            raise ExecutionContractError("artifact_size_mismatch")
        actual_hash = hashlib.sha256(artifact_path.read_bytes()).hexdigest()
        if actual_hash != expected_hash:
            raise ExecutionContractError("artifact_hash_mismatch")
        verified.append(Artifact(relative, actual_hash, expected_size, mime_type))
    return tuple(verified)
