"""Evidence-first benchmark primitives for DreamCo's 500-model evaluation system.

This module deliberately does not execute model-generated code, launch arbitrary
subprocesses, train weights, or deploy models. A trusted isolated runner is
injected by the caller and must return a structured execution record.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable

SCHEMA_VERSION = "dreamco.benchmark_evidence.v1"
SENSITIVE_PATTERNS = (
    re.compile(r"(?i)(api[_-]?key|secret|password|token)\s*[:=]\s*[^\s,;]+"),
    re.compile(r"(?i)\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"(?i)\bsk-[A-Za-z0-9_-]{20,}\b"),
)


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def redact_text(value: str, limit: int = 2000) -> str:
    text = value[:limit]
    for pattern in SENSITIVE_PATTERNS:
        text = pattern.sub("[REDACTED]", text)
    return text


@dataclass(frozen=True)
class BenchmarkTask:
    task_id: str
    division_id: str
    model_id: str
    model_revision: str
    dataset_revision: str
    split: str
    seed: int
    test_sha256: str
    hardware_profile: str


@dataclass(frozen=True)
class RunnerResult:
    passed: bool
    exit_code: int
    duration_ms: float
    stdout: str = ""
    stderr: str = ""
    peak_memory_mb: float | None = None
    timeout: bool = False
    security_findings: tuple[str, ...] = ()


def validate_task(task: BenchmarkTask) -> None:
    required = (task.task_id, task.division_id, task.model_id, task.model_revision,
                task.dataset_revision, task.split, task.test_sha256, task.hardware_profile)
    if any(not str(item).strip() for item in required):
        raise ValueError("Benchmark task is missing required provenance fields")
    if task.seed < 0:
        raise ValueError("seed must be non-negative")
    if task.split.lower() in {"train", "training"}:
        raise ValueError("benchmark evaluation must use a non-training split")
    if not re.fullmatch(r"[a-fA-F0-9]{64}", task.test_sha256):
        raise ValueError("test_sha256 must be a 64-character SHA-256 digest")


def evaluate(
    task: BenchmarkTask,
    runner: Callable[[BenchmarkTask], RunnerResult],
    *,
    max_duration_ms: float,
    max_memory_mb: float,
) -> dict[str, Any]:
    """Call a trusted sandbox adapter and fail closed on missing/unsafe evidence."""
    validate_task(task)
    if max_duration_ms <= 0 or max_memory_mb <= 0:
        raise ValueError("resource ceilings must be positive")
    result = runner(task)
    if not isinstance(result, RunnerResult):
        raise TypeError("runner must return RunnerResult")
    passed = (
        result.passed
        and result.exit_code == 0
        and not result.timeout
        and result.duration_ms <= max_duration_ms
        and result.peak_memory_mb is not None
        and result.peak_memory_mb <= max_memory_mb
        and not result.security_findings
    )
    payload = {
        "schema": SCHEMA_VERSION,
        "task": asdict(task),
        "result": {
            "passed": bool(result.passed),
            "exit_code": int(result.exit_code),
            "duration_ms": float(result.duration_ms),
            "peak_memory_mb": result.peak_memory_mb,
            "timeout": bool(result.timeout),
            "security_findings": list(result.security_findings),
            "stdout_redacted": redact_text(result.stdout),
            "stderr_redacted": redact_text(result.stderr),
        },
        "gate": "PASS" if passed else "FAIL_CLOSED",
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }
    payload["evidence_sha256"] = sha256_text(canonical_json(payload))
    return payload


def append_failure_replay(path: Path, evidence: dict[str, Any], *, priority: float = 4.0) -> None:
    """Persist only minimized, redacted metadata; never treat replay as training approval."""
    if evidence.get("gate") != "FAIL_CLOSED":
        raise ValueError("only failed evidence can enter failure replay")
    if priority <= 0 or not math.isfinite(priority):
        raise ValueError("priority must be finite and positive")
    task = evidence["task"]
    result = evidence["result"]
    record = {
        "schema": "dreamco.failure_replay.v1",
        "task_id": task["task_id"],
        "division_id": task["division_id"],
        "model_id": task["model_id"],
        "model_revision": task["model_revision"],
        "dataset_revision": task["dataset_revision"],
        "split": task["split"],
        "test_sha256": task["test_sha256"],
        "failure_summary": redact_text(result.get("stderr_redacted", "")),
        "priority_weight": priority,
        "training_eligible": False,
        "human_review_required": True,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(canonical_json(record) + "\n")


def select_failure_replay(records: Iterable[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    if limit < 0:
        raise ValueError("limit must be non-negative")
    eligible = [r for r in records if r.get("schema") == "dreamco.failure_replay.v1"]
    return sorted(eligible, key=lambda r: (-float(r.get("priority_weight", 1)), r.get("task_id", "")))[:limit]


def update_elo_pair(
    rating_a: float, rating_b: float, score_a: float, *, k_factor: float = 24.0
) -> tuple[float, float]:
    """Update both competitors from a comparable head-to-head match (1, .5, 0)."""
    if score_a not in (0.0, 0.5, 1.0):
        raise ValueError("score_a must be 0, 0.5, or 1")
    if k_factor <= 0:
        raise ValueError("k_factor must be positive")
    expected_a = 1.0 / (1.0 + 10 ** ((rating_b - rating_a) / 400.0))
    delta = k_factor * (score_a - expected_a)
    return round(rating_a + delta, 2), round(rating_b - delta, 2)


def self_debug_with_reviewed_patch(
    task: BenchmarkTask,
    runner: Callable[[BenchmarkTask], RunnerResult],
    patch_proposer: Callable[[BenchmarkTask, dict[str, Any], int], dict[str, Any] | None],
    patch_reviewer: Callable[[dict[str, Any]], bool],
    *,
    max_attempts: int = 3,
    max_duration_ms: float = 30_000,
    max_memory_mb: float = 2048,
) -> dict[str, Any]:
    """Bounded proposal/review/retest protocol; this module never applies a patch."""
    if max_attempts < 1 or max_attempts > 3:
        raise ValueError("max_attempts must be between 1 and 3")
    history = []
    current_task = task
    for attempt in range(1, max_attempts + 1):
        evidence = evaluate(current_task, runner, max_duration_ms=max_duration_ms, max_memory_mb=max_memory_mb)
        history.append(evidence)
        if evidence["gate"] == "PASS":
            return {"status": "PASS_WITH_EVIDENCE", "attempts": attempt, "history": history}
        if attempt == max_attempts:
            break
        proposal = patch_proposer(current_task, evidence, attempt)
        if not proposal or not patch_reviewer(proposal):
            return {"status": "BLOCKED_PATCH_REVIEW", "attempts": attempt, "history": history}
        # Patch application and new test-hash generation belong to the trusted
        # sandbox adapter. A proposer cannot silently mutate the benchmark task.
        next_task = proposal.get("revalidated_task")
        if not isinstance(next_task, BenchmarkTask):
            return {"status": "BLOCKED_MISSING_REVALIDATED_TASK", "attempts": attempt, "history": history}
        current_task = next_task
    return {"status": "FAIL_CLOSED", "attempts": len(history), "history": history}
