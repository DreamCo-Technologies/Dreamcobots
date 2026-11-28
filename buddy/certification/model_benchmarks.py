"""Repeatable model benchmark harness with explicit opt-in adapters.

Default fixture adapter is offline and cannot prove frontier capability.
"""
import hashlib
import json
from dataclasses import dataclass

@dataclass(frozen=True)
class Task:
    id: str
    prompt: str
    expected: str

class FixtureAdapter:
    name = "fixture-only"
    def complete(self, prompt):
        return prompt  # Deterministic plumbing check only.

class CallableAdapter:
    def __init__(self, name, callback):
        self.name, self.callback = name, callback
    def complete(self, prompt):
        return self.callback(prompt)

def benchmark(tasks, adapters, *, dataset_rights, approved=False, max_tasks=100):
    if not dataset_rights or dataset_rights not in ("owned", "licensed", "public_domain"):
        raise ValueError("Authorized dataset rights required")
    if not approved:
        raise PermissionError("Explicit model-execution approval required")
    if not tasks or len(tasks) > max_tasks:
        raise ValueError("Task count outside permitted bounds")
    ids = [t.id for t in tasks]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate task ids")
    task_hash = hashlib.sha256(json.dumps([vars(t) for t in tasks], sort_keys=True).encode()).hexdigest()
    results = []
    for adapter in adapters:
        passed, receipts = 0, []
        for task in tasks:
            try:
                output = adapter.complete(task.prompt)
                if not isinstance(output, str):
                    raise TypeError("model output must be text")
                correct = output.strip() == task.expected.strip()
                passed += int(correct)
                receipts.append({"task": task.id, "passed": correct,
                                 "output_sha256": hashlib.sha256(output.encode()).hexdigest()})
            except Exception as exc:
                receipts.append({"task": task.id, "passed": False, "error_type": type(exc).__name__})
        results.append({"adapter": adapter.name, "passed": passed, "total": len(tasks),
                        "accuracy": passed / len(tasks), "receipts": receipts,
                        "independent_verified": False, "frontier_certified": False})
    return {"schema": "dreamco.model_comparison.v1", "task_set_hash": task_hash,
            "dataset_rights": dataset_rights, "scoring": "exact_match_v1",
            "results": results, "limitations": "Fixture/callable adapters are harness tests, not independent frontier comparisons. Provider adapters require configured credentials, cost approval, and privacy controls."}
