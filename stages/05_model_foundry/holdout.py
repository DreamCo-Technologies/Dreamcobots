"""Compatibility helpers for the single canonical 90/5/5 Foundry split."""
from __future__ import annotations
import hashlib
import importlib

_guard = importlib.import_module("stages.05_model_foundry.guardrails")

def bucket(task_id: str) -> int:
    """Return the canonical 0–99 bucket used by every Foundry consumer."""
    return _guard.split_bucket(task_id)

def split_tasks(tasks: list[dict], holdout_percent: int = 5) -> dict:
    """Partition tasks into 90% train, 5% validation and 5% evaluation-only holdout."""
    if holdout_percent != 5:
        raise ValueError("Foundry split is fixed at 90/5/5; custom holdout sizes are not supported")
    ids = [item.get("task_id") for item in tasks]
    if any(not isinstance(value, str) or not value.strip() for value in ids) or len(set(ids)) != len(ids):
        raise ValueError("task_id values must be unique and non-empty")
    train, validation, holdout = [], [], []
    for item in tasks:
        split = _guard.split_name(item["task_id"])
        {"train": train, "validation": validation, "holdout": holdout}[split].append(item)
    return {
        "schema": "dreamco.deterministic_task_split.v2",
        "algorithm": "int(sha256(task_id)[:8], 16) % 100",
        "train_buckets": "00-89",
        "validation_buckets": "90-94",
        "holdout_buckets": "95-99",
        "train": train,
        "validation": validation,
        "holdout": holdout,
        "train_ids": [item["task_id"] for item in train],
        "validation_ids": [item["task_id"] for item in validation],
        "holdout_ids": [item["task_id"] for item in holdout],
        "holdout_access": "evaluation_only",
        "split_digest": hashlib.sha256("\n".join(sorted(ids)).encode()).hexdigest(),
    }

def evaluation_recipe(base_model: str, recipe: dict, task_manifest_sha256: str) -> dict:
    """Describe a reproducible evaluation without claiming that a run occurred."""
    if not base_model or not recipe or len(task_manifest_sha256) != 64:
        raise ValueError("pinned model, recipe, and manifest SHA-256 are required")
    return {
        "schema": "dreamco.evaluation_recipe.v2",
        "base_model": base_model,
        "recipe": recipe,
        "task_manifest_sha256": task_manifest_sha256,
        "seed": 20261127,
        "split": {"train": [0, 89], "validation": [90, 94], "holdout": [95, 99]},
        "metrics": ["accuracy", "pass_rate", "safety_gate_pass_rate", "latency_ms"],
        "holdout_access": "evaluation_only",
        "truth_boundary": "A recipe is not a training run; only checkpoint and evaluation artifacts establish a result.",
    }
