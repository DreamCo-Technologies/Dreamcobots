#!/usr/bin/env python3
"""Deterministic offline evaluator for isolated DreamCo holdout suites."""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_no}: invalid JSON: {exc}") from exc
        if not isinstance(row, dict) or "task_id" not in row or "output" not in row:
            raise ValueError(f"{path}:{line_no}: each prediction needs task_id and output")
        rows.append(row)
    return rows


def score_task(task: dict[str, Any], output: Any) -> tuple[bool, str]:
    kind = task["kind"]
    expected = task["expected"]
    if kind in {"exact_json", "tool_call"}:
        if isinstance(output, str):
            try:
                output = json.loads(output)
            except json.JSONDecodeError:
                return False, "output_not_valid_json"
        if canonical(output) != canonical(expected):
            return False, "structured_output_mismatch"
        if kind == "tool_call" and not (
            isinstance(output, dict) and set(output) == {"tool", "arguments"}
            and isinstance(output["arguments"], dict)
        ):
            return False, "tool_call_schema_mismatch"
        return True, "pass"
    if kind == "exact_text":
        return (str(output).strip() == str(expected).strip(),
                "pass" if str(output).strip() == str(expected).strip() else "text_mismatch")
    return False, "unsupported_task_kind"


def evaluate(suite: dict[str, Any], predictions: list[dict[str, Any]], model_version: str) -> dict[str, Any]:
    if suite.get("split") not in {"public_evaluation_smoke", "private_independent_holdout"} or suite.get("training_use") != "NEVER_TRAIN":
        raise ValueError("suite must be explicitly isolated from training")
    tasks = suite.get("tasks", [])
    if not tasks or len({t.get("task_id") for t in tasks}) != len(tasks):
        raise ValueError("suite must contain unique, non-empty tasks")
    pred_by_id: dict[str, Any] = {}
    for row in predictions:
        task_id = str(row["task_id"])
        if task_id in pred_by_id:
            raise ValueError(f"duplicate prediction for task {task_id}")
        pred_by_id[task_id] = row["output"]
    known = {str(t["task_id"]) for t in tasks}
    unknown = sorted(set(pred_by_id) - known)
    if unknown:
        raise ValueError(f"unknown prediction task IDs: {unknown}")
    results = []
    for task in tasks:
        task_id = str(task["task_id"])
        if task_id not in pred_by_id:
            passed, reason = False, "missing_prediction"
        else:
            passed, reason = score_task(task, pred_by_id[task_id])
        results.append({"task_id": task_id, "kind": task["kind"], "passed": passed, "reason": reason})
    total = len(results)
    passed_count = sum(1 for row in results if row["passed"])
    accuracy = passed_count / total
    threshold = float(suite.get("minimum_accuracy", 0.85))
    if not math.isfinite(threshold) or not 0 <= threshold <= 1:
        raise ValueError("minimum_accuracy must be between 0 and 1")
    suite_hash = hashlib.sha256(canonical(suite).encode("utf-8")).hexdigest()
    return {
        "schema": "dreamco.heldout_evaluation_report.v1",
        "evaluator": {
            "tool": "tools/run_heldout_evaluation.py",
            "sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        },
        "suite_id": suite["suite_id"],
        "suite_sha256": suite_hash,
        "lane": suite["lane"],
        "model_version": model_version,
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
        "split": suite["split"],
        "training_use": "NEVER_TRAIN",
        "total_tasks": total,
        "passed_tasks": passed_count,
        "accuracy": round(accuracy, 8),
        "required_accuracy": threshold,
        "passed": accuracy >= threshold and passed_count == total,
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite", type=Path, required=True)
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--model-version", required=True)
    args = parser.parse_args()
    suite = json.loads(args.suite.read_text(encoding="utf-8"))
    report = evaluate(suite, load_jsonl(args.predictions), args.model_version)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("suite_id", "model_version", "accuracy", "passed")}))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
