"""Smoke tests for fleet bots: generic per-engine tasks and bot-specific fixtures."""
from __future__ import annotations

from typing import Any

from .engines import GENERIC_SMOKE_TASKS
from .executor import FleetExecutor


def _get(value: Any, path: str) -> Any:
    for part in path.split("."):
        if isinstance(value, list):
            value = value[int(part)] if part.isdigit() and int(part) < len(value) else None
        elif isinstance(value, dict):
            value = value.get(part)
        else:
            return None
    return value


def check_expectations(output: dict[str, Any], expect: list[dict[str, Any]]) -> list[str]:
    """Assertion language: {path, equals|contains|gte|lte|truthy|falsy}."""
    failures = []
    for rule in expect:
        actual = _get(output, rule["path"])
        if "equals" in rule and actual != rule["equals"]:
            failures.append(f"{rule['path']}: expected {rule['equals']!r}, got {actual!r}")
        if "contains" in rule and (actual is None or rule["contains"] not in actual):
            failures.append(f"{rule['path']}: expected to contain {rule['contains']!r}")
        if "gte" in rule and not (isinstance(actual, (int, float)) and actual >= rule["gte"]):
            failures.append(f"{rule['path']}: expected >= {rule['gte']}, got {actual!r}")
        if "lte" in rule and not (isinstance(actual, (int, float)) and actual <= rule["lte"]):
            failures.append(f"{rule['path']}: expected <= {rule['lte']}, got {actual!r}")
        if rule.get("truthy") and not actual:
            failures.append(f"{rule['path']}: expected truthy, got {actual!r}")
        if rule.get("falsy") and actual:
            failures.append(f"{rule['path']}: expected falsy, got {actual!r}")
    return failures


def generic_smoke(executor: FleetExecutor, slug: str) -> dict[str, Any]:
    manifest = executor.manifest(slug)
    task = GENERIC_SMOKE_TASKS.get(manifest["engine"])
    if task is None:
        return {"slug": slug, "ran": False, "passed": False, "status": "unmapped", "failures": ["engine_unmapped"]}
    out = executor.run(slug, task)
    failures = check_expectations(out, [
        {"path": "status", "equals": "ok"},
        {"path": "live_external_action_taken", "equals": False},
        {"path": "evidence.run_id", "truthy": True},
    ])
    return {"slug": slug, "ran": True, "passed": not failures, "status": out["status"],
            "mode": out["mode"], "run_id": out["evidence"]["run_id"], "failures": failures,
            "error": out.get("error")}


def fixture_smoke(executor: FleetExecutor, slug: str, fixture: dict[str, Any]) -> dict[str, Any]:
    out = executor.run(slug, fixture["task"])
    rules = [{"path": "live_external_action_taken", "equals": False}, *fixture.get("expect", [])]
    failures = check_expectations(out, rules)
    return {"slug": slug, "ran": True, "passed": not failures, "status": out["status"],
            "run_id": out["evidence"]["run_id"], "failures": failures}
