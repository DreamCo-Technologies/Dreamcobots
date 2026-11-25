"""Validate the core benchmark definition registry against the canonical task list."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "config/buddy-benchmark-task-registry.json"
DEFINITIONS = ROOT / "config/buddy-core-capability-benchmark-definitions.json"


def validate(registry: dict[str, Any], definitions: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if registry.get("schema") != "dreamco.buddy_benchmark_registry.v1":
        errors.append("unsupported canonical benchmark task registry schema")
    if definitions.get("schema") != "dreamco.core_capability_benchmark_definitions.v1":
        errors.append("unsupported core benchmark definitions schema")
    tasks = registry.get("tasks")
    rows = definitions.get("benchmarks")
    if not isinstance(tasks, list) or not all(isinstance(x, str) and x for x in tasks):
        errors.append("canonical tasks must be a list of non-empty strings")
        return errors
    if not isinstance(rows, list):
        errors.append("benchmarks must be an array")
        return errors
    ids: set[str] = set()
    capabilities: list[str] = []
    for row in rows:
        if not isinstance(row, dict):
            errors.append("benchmark entries must be objects")
            continue
        benchmark_id = row.get("benchmark_id")
        capability = row.get("capability_id")
        if not isinstance(benchmark_id, str) or not benchmark_id:
            errors.append("benchmark_id is required")
        elif benchmark_id in ids:
            errors.append(f"duplicate benchmark_id: {benchmark_id}")
        else:
            ids.add(benchmark_id)
        if not isinstance(capability, str) or not capability:
            errors.append(f"{benchmark_id}: capability_id is required")
        else:
            capabilities.append(capability)
        for field in ("objective", "dimensions", "task_design", "rubric", "pass_threshold", "critical_gates", "execution_status"):
            if field not in row or row[field] in (None, "", [], {}):
                errors.append(f"{benchmark_id}: missing {field}")
        if isinstance(row.get("pass_threshold"), int) and not 0 <= row["pass_threshold"] <= 100:
            errors.append(f"{benchmark_id}: pass_threshold must be 0-100")
        rubric = row.get("rubric")
        if isinstance(rubric, list) and rubric:
            weights = [item.get("weight") for item in rubric if isinstance(item, dict)]
            if len(weights) != len(rubric) or any(not isinstance(w, int) or w <= 0 for w in weights):
                errors.append(f"{benchmark_id}: rubric weights must be positive integers")
            elif sum(weights) != 100:
                errors.append(f"{benchmark_id}: rubric weights must sum to 100")
        design = row.get("task_design")
        if isinstance(design, dict) and not str(design.get("holdout", "")).strip():
            errors.append(f"{benchmark_id}: independent holdout policy is required")
        if row.get("execution_status") == "implemented":
            if not row.get("adapter_path") or not row.get("test_path"):
                errors.append(f"{benchmark_id}: implemented benchmark requires adapter_path and test_path")
    if len(capabilities) != len(set(capabilities)):
        errors.append("each canonical capability must have exactly one core benchmark definition")
    missing = sorted(set(tasks) - set(capabilities))
    extra = sorted(set(capabilities) - set(tasks))
    if missing:
        errors.append("missing capability definitions: " + ", ".join(missing))
    if extra:
        errors.append("definitions not in canonical task registry: " + ", ".join(extra))
    policy = definitions.get("score_policy", {})
    if policy.get("unknown_without_evidence") is not True or policy.get("holdout_required") is not True:
        errors.append("score policy must require evidence and holdout testing")
    return errors


def main() -> int:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    definitions = json.loads(DEFINITIONS.read_text(encoding="utf-8"))
    errors = validate(registry, definitions)
    print(json.dumps({"status": "invalid" if errors else "valid", "errors": errors,
                      "benchmark_count": len(definitions.get("benchmarks", [])),
                      "execution_adapters_implemented": sum(1 for row in definitions.get("benchmarks", []) if row.get("execution_status") == "implemented")}, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
