"""Evidence contracts for consented task learning and professional model training.

This module prepares safe records and promotion decisions. It does not watch a
user, call an app, submit a GPU job, or train model weights.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from statistics import mean
from typing import Any, Iterable, Mapping


PRIVATE_FIELDS = frozenset({
    "password", "token", "secret", "api_key", "private_key", "payment_card",
    "hidden_reasoning", "chain_of_thought", "screen_capture", "holdout_answer",
})
ALLOWED_MODES = frozenset({"observe", "suggest", "guide", "assist", "supervised_automation"})


def _required_text(record: Mapping[str, Any], name: str) -> str:
    value = record.get(name)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} is required")
    return value.strip()


def distill_task(record: Mapping[str, Any]) -> dict[str, Any]:
    """Create a minimal training candidate from one authorized task result."""
    attestations = ("capture_consent", "training_consent", "rights_verified", "redacted", "outcome_verified")
    if not all(record.get(name) is True for name in attestations):
        raise ValueError("capture, training, rights, redaction and outcome attestations are required")
    if record.get("split") != "train":
        raise ValueError("only the train split can be distilled")
    supplied = {str(key).lower() for key in record}
    blocked = sorted(supplied & PRIVATE_FIELDS)
    if blocked:
        raise ValueError(f"private or evaluation-only fields are forbidden: {', '.join(blocked)}")
    steps = record.get("steps")
    if not isinstance(steps, list) or not steps or not all(isinstance(step, str) and step.strip() for step in steps):
        raise ValueError("steps must be a non-empty list of visible actions")
    mode = record.get("mode", "observe")
    if mode not in ALLOWED_MODES:
        raise ValueError("unsupported learning mode")
    candidate = {
        "schema": "dreamco.professional_task_example.v1",
        "task_id": _required_text(record, "task_id"),
        "profession": _required_text(record, "profession"),
        "goal": _required_text(record, "goal"),
        "source": _required_text(record, "source"),
        "source_revision": _required_text(record, "source_revision"),
        "wrapper_id": _required_text(record, "wrapper_id"),
        "mode": mode,
        "steps": [step.strip() for step in steps],
        "result": _required_text(record, "result"),
        "user_correction": str(record.get("user_correction", "")).strip(),
        "customization": _required_text(record, "customization"),
        "split": "train",
    }
    canonical = json.dumps(candidate, sort_keys=True, separators=(",", ":")).encode()
    return {**candidate, "example_sha256": sha256(canonical).hexdigest()}


@dataclass(frozen=True)
class BenchmarkRun:
    task_success: float
    quality: float
    safety: float
    latency_seconds: float
    cost_usd: float
    human_touches: int
    regression: float = 0.0

    def validate(self) -> None:
        for name in ("task_success", "quality", "safety", "regression"):
            value = getattr(self, name)
            if not isinstance(value, (int, float)) or not 0 <= value <= 1:
                raise ValueError(f"{name} must be between 0 and 1")
        if self.latency_seconds < 0 or self.cost_usd < 0 or self.human_touches < 0:
            raise ValueError("latency, cost and human touches cannot be negative")

    @property
    def score(self) -> float:
        self.validate()
        efficiency = 1 / (1 + self.latency_seconds / 60 + self.cost_usd + self.human_touches / 10)
        return round(.45 * self.task_success + .25 * self.quality + .20 * self.safety + .10 * efficiency, 6)


def promotion_decision(
    baseline: Iterable[BenchmarkRun], candidate: Iterable[BenchmarkRun], holdout: Iterable[BenchmarkRun]
) -> dict[str, Any]:
    """Apply the repository's three-run, holdout and regression promotion gate."""
    groups = [list(baseline), list(candidate), list(holdout)]
    if any(len(group) < 3 for group in groups):
        return {"promote": False, "reason": "minimum_repetitions_not_met"}
    for group in groups:
        for run in group:
            run.validate()
    baseline_score = mean(run.score for run in groups[0])
    candidate_score = mean(run.score for run in groups[1])
    holdout_score = mean(run.score for run in groups[2])
    maximum_regression = max(run.regression for run in groups[1] + groups[2])
    checks = {
        "improvement": candidate_score - baseline_score >= .05,
        "holdout": holdout_score >= .75,
        "regression": maximum_regression <= .02,
        "safety": min(run.safety for run in groups[1] + groups[2]) >= .75,
    }
    return {
        "promote": all(checks.values()),
        "checks": checks,
        "baseline_score": round(baseline_score, 6),
        "candidate_score": round(candidate_score, 6),
        "holdout_score": round(holdout_score, 6),
        "maximum_regression": maximum_regression,
    }


def build_training_manifest(request: Mapping[str, Any], examples: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    """Build a reviewable handoff for a separate funded training adapter."""
    required = ("run_id", "method", "base_model", "base_revision", "base_license", "dataset_license", "hardware", "max_cost_usd", "output_repo")
    values = {name: request.get(name) for name in required}
    if any(value in (None, "") for value in values.values()):
        raise ValueError("training request is incomplete")
    if request.get("owner_approved") is not True:
        raise ValueError("owner approval is required")
    if request["method"] not in {"SFT", "DPO", "GRPO", "reward_modeling", "LoRA", "QLoRA"}:
        raise ValueError("unsupported training method")
    if not isinstance(request["max_cost_usd"], (int, float)) or request["max_cost_usd"] <= 0:
        raise ValueError("max_cost_usd must be positive")
    rows = list(examples)
    if not rows or any(row.get("schema") != "dreamco.professional_task_example.v1" for row in rows):
        raise ValueError("at least one distilled professional task example is required")
    hashes = sorted(_required_text(row, "example_sha256") for row in rows)
    dataset_hash = sha256("\n".join(hashes).encode()).hexdigest()
    return {
        "schema": "dreamco.professional_training_handoff.v1",
        **values,
        "dataset_sha256": dataset_hash,
        "example_count": len(rows),
        "required_splits": ["train", "validation", "hidden_test"],
        "monitoring": "Trackio or equivalent run metrics",
        "push_checkpoint_to_private_repo": True,
        "preflight": ["validate dataset format", "estimate cost", "baseline hidden test", "confirm token can write output repository"],
        "postflight": ["hidden test", "safety and capability regressions", "three repeated evaluations", "model card", "owner promotion review"],
        "weights_trained_by_this_function": False,
        "status": "ready_for_adapter_review",
    }


def public_summary(manifest: Mapping[str, Any]) -> dict[str, Any]:
    """Return fields safe for public evidence without dataset rows or credentials."""
    keep = ("schema", "run_id", "method", "base_model", "base_revision", "hardware", "max_cost_usd", "dataset_sha256", "example_count", "status", "weights_trained_by_this_function")
    return {name: manifest[name] for name in keep if name in manifest}
