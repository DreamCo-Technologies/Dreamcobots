"""Bounded evaluation through an injected, trusted model adapter.

No model credentials, shell commands or remote code are accepted in fixtures.
Adapters are integration code, not model-generated callables. Network/paid
adapters must enforce provider timeouts and spending caps before making calls.
"""
from __future__ import annotations

import json
import random
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from .evidence import contamination
from .review import digest, finite


@dataclass(frozen=True)
class SubjectAdapter:
    name: str
    version: str
    generate: Callable
    network: bool = False
    paid: bool = False
    modalities: tuple = ("text",)


def run_suite(*, suite, fixtures, training, adapter, grader, store, action_id, action_hash,
              components, baseline, hardware, runtime, output_dir: Path, max_seconds=300, max_budget_usd=0):
    """Return measured attempts, including failures; never silently drop a case.

This runner produces candidate evidence. Independent safety, calibration and
red-team reviews are deliberately still required by the evidence validator.
"""
    if not finite(max_seconds, 1, 86400) or not finite(max_budget_usd):
        raise ValueError("Explicit bounded runtime and budget required")
    if type(suite.get("seed")) is not int or not isinstance(suite.get("cases"), list) or not suite["cases"] or not suite.get("reviewer"):
        raise ValueError("Reviewed, seeded suite manifest required")
    if suite.get("repetitions") != 3:
        raise ValueError("Version 1 requires three repetitions")
    if not suite.get("license_review", {}).get("allowed") or not suite.get("grader_version"):
        raise ValueError("License and grader version required")
    expected = {c["id"]: c for c in suite["cases"]}
    if len(expected) != len(suite["cases"]) or set(fixtures) != set(expected):
        raise ValueError("Fixture coverage differs from reviewed manifest")
    for key, fixture in fixtures.items():
        if digest(fixture) != expected[key]["fixture_hash"] or fixture.get("modality", "text") not in adapter.modalities:
            raise ValueError("Fixture mismatch or unsupported modality")
        if fixture.get("family") != expected[key]["family"] or expected[key]["split"] not in {"holdout", "transfer"}:
            raise ValueError("Held-out family mismatch")
    scan = contamination([{**f, "id": i, "hash": digest(f)} for i, f in fixtures.items()], training)
    if not scan["passed"]:
        raise ValueError("Contamination detected; evaluation blocked")
    scope = {"suite_hash": digest(suite), "subject": adapter.name, "subject_version": adapter.version,
             "components": components, "network": adapter.network, "paid": adapter.paid,
             "max_seconds": max_seconds, "max_budget_usd": max_budget_usd}
    reviewed = store.get(action_id)
    if reviewed["action"]["parameters"] != scope:
        raise ValueError("Run configuration differs from approved action")
    required_class = "external_action" if adapter.network or adapter.paid else "sandbox"
    store.consume(action_id, action_hash, action_class=required_class, budget_usd=max_budget_usd)
    output_dir.mkdir(parents=True, exist_ok=True)
    deadline = time.monotonic() + max_seconds
    tasks = [(i, repetition) for i in expected for repetition in range(3)]
    random.Random(suite["seed"]).shuffle(tasks)
    rows, spent = [], 0.0
    for case_id, repetition in tasks:
        fixture, spec = fixtures[case_id], expected[case_id]
        started = time.monotonic()
        row = {"id": case_id, "repetition": repetition, "split": spec["split"], "family": spec["family"],
               "cross_domain": spec.get("cross_domain", False), "fixture_hash": digest(fixture), "withheld_from_training": True,
               "human_interventions": 0, "external_assistance": False, "quality": 0.0, "safety": 0.0, "factuality": 0.0,
               "response_hash": digest(None), "cost_usd": None, "latency_ms": 0.0, "runtime_ms": 0.0}
        try:
            if started >= deadline or spent > max_budget_usd:
                raise TimeoutError("Run budget or deadline exhausted")
            result = adapter.generate(fixture, seed=suite["seed"] + repetition, timeout_seconds=deadline-started, budget_usd=max_budget_usd-spent)
            if not isinstance(result, dict) or not finite(result.get("cost_usd")) or not isinstance(result.get("output"), str):
                raise ValueError("Adapter response lacks measured cost/output")
            spent += result["cost_usd"]
            row.update(cost_usd=result["cost_usd"], response_hash=digest(result["output"]), latency_ms=(time.monotonic()-started)*1000)
            grade = grader(fixture, result["output"])
            if not isinstance(grade, dict) or not all(finite(grade.get(k), 0, 1) for k in ("quality", "safety", "factuality")):
                raise ValueError("Invalid independent grade")
            if time.monotonic() > deadline or spent > max_budget_usd:
                raise TimeoutError("Measured runtime or cost exceeded cap")
            row.update({k: grade[k] for k in ("quality", "safety", "factuality")})
            row["status"] = "measured"
        except Exception as error:
            # Do not leak provider exception messages, outputs, or private fixtures.
            row["status"] = "failed"
            row["error_type"] = type(error).__name__
        row["runtime_ms"] = (time.monotonic()-started)*1000
        rows.append(row)
        if row["cost_usd"] is None:
            # Unknown spend/effects: retain the failure and record remaining tasks as
            # unexecuted. Never retry or assume a free call.
            deadline = 0
    run = {"schema": "dreamco.general_intelligence_run.v1", "id": action_id,
           "capability": suite["capability"], "subject": adapter.name + "@" + adapter.version,
           "components": components, "suite_id": suite["id"], "suite_version": suite["version"], "suite_hash": digest(suite),
           "dataset_hash": digest(fixtures), "grader_version": suite["grader_version"], "seed": suite["seed"],
           "hardware": hardware, "runtime": runtime, "timestamp": datetime.now(timezone.utc).isoformat(),
           "license_review": suite["license_review"], "contamination": scan, "training_corpus_hash": digest(training),
           "cases": rows, "expected_cases": sorted(expected), "baseline_id": baseline["id"], "baseline_hash": digest(baseline),
           "config_hash": digest(scope), "simulated": False, "calibration": [], "red_team": {}, "artifacts": []}
    trace_path = output_dir / (action_id + ".trace.json")
    # The trace is private by default and contains hashes/metrics, not raw prompts.
    with trace_path.open("x") as stream:
        json.dump(rows, stream, indent=2, allow_nan=False)
    import hashlib
    run["artifacts"] = [{"path": trace_path.name, "sha256": hashlib.sha256(trace_path.read_bytes()).hexdigest()}]
    with (output_dir / (action_id + ".run.json")).open("x") as stream:
        json.dump(run, stream, indent=2, allow_nan=False)
    if all(r["cost_usd"] is not None for r in rows):
        store.finish(action_id, passed=all(r["status"] == "measured" for r in rows), evidence_hash=digest(run), actual_cost_usd=spent)
    else:
        with store.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            store._audit(db, "evaluation_reconciliation_required", action_id, {"run_hash": digest(run)})
    return run
