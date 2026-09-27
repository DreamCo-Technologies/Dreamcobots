#!/usr/bin/env python3
"""Verify actual tiny-model parameter updates without changing repository evidence.

Only the safe JSON record is retained. Training checkpoints and reports are
created in a fresh temporary directory; no chat exports or network sources are
ingested. Training-set improvement is deliberately not called generalization.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from buddy.learning import note_model


PROTECTED_FILES = (
    "buddy/learning/note_model.npz",
    "website/data/note-model.json",
    "evidence/buddy-learning-history.jsonl",
    "evidence/buddy-learning-proof-history.jsonl",
)
PARAMETER_ARRAYS = ("embed", "weight", "bias")


def digest(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


def source_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def fixed_training_score(arrays: dict, windows: np.ndarray, targets: np.ndarray) -> dict:
    flat = arrays["embed"][windows].reshape(len(windows), -1)
    logits = flat @ arrays["weight"] + arrays["bias"]
    logits -= logits.max(axis=1, keepdims=True)
    probabilities = np.exp(logits)
    probabilities /= probabilities.sum(axis=1, keepdims=True)
    return {
        "cross_entropy": float(-np.log(probabilities[np.arange(len(windows)), targets] + 1e-9).mean()),
        "next_character_accuracy": float((probabilities.argmax(axis=1) == targets).mean()),
    }


def verify_parameter_learning(*, steps: int = 80, seed: int = 1) -> dict:
    if not 1 <= steps <= 10_000:
        raise ValueError("steps must be between 1 and 10000")
    if seed < 0:
        raise ValueError("seed must be non-negative")
    protected_before = {name: digest(ROOT / name) for name in PROTECTED_FILES}
    lines = note_model.notes()
    text = "\n".join(lines)
    if len(text) <= note_model.CONTEXT + 1:
        raise ValueError("The approved note corpus is too short for the model context")
    characters = sorted(set(text))
    vocabulary = len(characters)
    index = {character: position for position, character in enumerate(characters)}
    data = np.array([index[character] for character in text], dtype=np.int32)
    rng = np.random.default_rng(seed)
    # Match the existing trainer's initialization, then inspect the real updates.
    initial = {
        "embed": rng.normal(0, 0.02, (vocabulary, note_model.WIDTH)),
        "weight": rng.normal(0, 0.02, (note_model.CONTEXT * note_model.WIDTH, vocabulary)),
        "bias": np.zeros(vocabulary),
    }
    starts = np.linspace(0, len(data) - note_model.CONTEXT - 2, 256, dtype=int)
    windows = np.stack([data[start:start + note_model.CONTEXT] for start in starts])
    targets = data[starts + note_model.CONTEXT]
    fixed_before = fixed_training_score(initial, windows, targets)
    trained = note_model.train(steps=steps, seed=seed)
    arrays = trained["_arrays"]
    fixed_after = fixed_training_score(arrays, windows, targets)
    parameter_count = sum(arrays[name].size for name in PARAMETER_ARRAYS)
    deltas = {name: float(np.linalg.norm(arrays[name] - initial[name])) for name in PARAMETER_ARRAYS}
    arrays_changed = all(np.isfinite(delta) and delta > 0 for delta in deltas.values())

    with tempfile.TemporaryDirectory(prefix="buddy-parameter-verification-") as temporary:
        scratch = Path(temporary)
        checkpoint = scratch / "note-model.npz"
        with patch.multiple(note_model, WEIGHTS=checkpoint, REPORT=scratch / "note-model-report.json"):
            training_report = note_model.save(trained)
        checkpoint_sha256 = digest(checkpoint)
        with np.load(checkpoint, allow_pickle=False) as restored:
            roundtrip_equal = set(restored.files) == set(arrays) and all(
                np.array_equal(restored[name], arrays[name]) for name in arrays
            )

    protected_unchanged = protected_before == {name: digest(ROOT / name) for name in PROTECTED_FILES}
    fixed_loss_dropped = fixed_after["cross_entropy"] < fixed_before["cross_entropy"]
    verified = bool(arrays_changed and roundtrip_equal and protected_unchanged and fixed_loss_dropped and training_report["loss_dropped"])
    summary = (
        f"Verified a small local character model: {parameter_count:,} parameters changed and training loss "
        f"fell from {training_report['start_loss']:.4f} to {training_report['end_loss']:.4f}. "
        "No held-out performance or improvement to Buddy chat has been demonstrated."
        if verified else
        "Parameter-learning verification did not pass every check. Review the recorded checks before claiming improvement."
    )
    return {
        "schema": "dreamco.parameter_learning_verification.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "passed" if verified else "failed",
        "verified": verified,
        "summary": summary,
        "source_commit": source_commit(),
        "source_hashes": {
            name: digest(ROOT / name) for name in (
                "buddy/learning/note_model.py", "buddy/learning/own_versions.jsonl",
                "tools/verify_buddy_parameter_learning.py",
            )
        },
        "environment": {"python": platform.python_version(), "numpy": np.__version__},
        "algorithm": {
            "name": "Character embeddings and linear softmax with minibatch gradient descent",
            "context_characters": note_model.CONTEXT, "embedding_width": note_model.WIDTH,
            "vocabulary_characters": vocabulary, "parameter_count": parameter_count,
            "batch_size": 96, "learning_rate": 0.5, "steps": steps, "seed": seed,
        },
        "training_report": training_report,
        "parameter_l2_changes": deltas,
        "fixed_training_sample": {
            "sample_count": len(starts), "before": fixed_before, "after": fixed_after,
            "held_out": False,
        },
        "checks": {
            "all_parameter_arrays_changed": bool(arrays_changed),
            "fixed_training_loss_decreased": bool(fixed_loss_dropped),
            "minibatch_training_loss_decreased": bool(training_report["loss_dropped"]),
            "checkpoint_roundtrip_equal": bool(roundtrip_equal),
            "protected_files_unchanged": protected_unchanged,
        },
        "checkpoint_sha256": checkpoint_sha256,
        "temporary_checkpoint_retained": False,
        "protected_files": list(PROTECTED_FILES),
        "boundaries": {
            "input": "Existing template-derived own_version note strings only",
            "webpages_read_by_this_run": 0, "private_chat_exports_ingested": False,
            "network_requests": 0, "paid_jobs": 0, "holdout_evaluated": False,
            "buddy_chat_model_updated": False, "frontier_capability_proven": False,
        },
        "records": [
            {
                "title": "Real parameter updates",
                "result": f"{parameter_count:,} parameters across embedding, output-weight, and bias arrays; all arrays changed: {bool(arrays_changed)}.",
                "limit": "This is a tiny local next-character model, not the model powering Buddy chat.",
            },
            {
                "title": "Measured training loss",
                "result": f"{training_report['start_loss']:.4f} → {training_report['end_loss']:.4f} over {steps} training steps; checkpoint roundtrip equal: {bool(roundtrip_equal)}.",
                "limit": "Training-set loss only. No held-out evaluation, new-task generalization, or leaderboard comparison was performed.",
            },
            {
                "title": "Fixed training-sample check",
                "result": f"The same {len(starts)} training windows scored {fixed_before['cross_entropy']:.4f} → {fixed_after['cross_entropy']:.4f} cross-entropy.",
                "limit": "These examples came from the training corpus and are not an independent test set.",
            },
            {
                "title": "Source and preservation",
                "result": f"Used {len(lines)} existing template-derived notes; tracked weights and histories unchanged: {protected_unchanged}.",
                "limit": "Note count is not a count of webpages read or topics mastered. Temporary training artifacts were removed after verification.",
            },
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "tmp/learning-verification")
    parser.add_argument("--steps", type=int, default=80)
    parser.add_argument("--seed", type=int, default=1)
    args = parser.parse_args(argv)
    report = verify_parameter_learning(steps=args.steps, seed=args.seed)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "learning-verification.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": report["verified"], "artifact": "learning-verification.json", "summary": report["summary"]}))
    return 0 if report["verified"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
