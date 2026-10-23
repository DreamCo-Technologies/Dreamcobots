"""Deterministic, offline paired inference evaluation of an authorized callable.

No external model calls, downloads, training or paid compute. For a real Buddy
candidate replace callable adapters in an isolated runner and retain evidence.
"""
import hashlib
import json
import math
import statistics
import time

def evaluate_pair(cases, champion, candidate, repeats=3):
    if repeats < 2:
        raise ValueError("at least two repeats required")
    if not isinstance(cases, list) or not cases:
        raise ValueError("nonempty list of cases required")
    records = []
    for case in cases:
        if not case.get("authorized") or case.get("protected_holdout"):
            raise ValueError("unauthorized or protected cases cannot run here")
        if not all(k in case for k in ("id", "input", "expected")):
            raise ValueError("case must have id, input, expected")
        for repeat in range(repeats):
            row = {"case_id": case["id"], "repeat": repeat}
            for name, model in (("champion", champion), ("candidate", candidate)):
                start = time.perf_counter()
                output = model(case["input"])
                row[name] = {"correct": output == case["expected"],
                             "latency_ms": (time.perf_counter() - start) * 1000,
                             "output_sha256": hashlib.sha256(str(output).encode()).hexdigest()}
            records.append(row)
    differences = [int(r["candidate"]["correct"]) - int(r["champion"]["correct"]) for r in records]
    mean = statistics.mean(differences)
    se = statistics.stdev(differences) / math.sqrt(len(differences)) if len(differences) > 1 else 0.0
    return {"schema_version": 1, "trials": records,
            "paired_accuracy_delta": mean, "naive_95pct_interval": [mean - 1.96*se, mean + 1.96*se],
            "uncertainty_note": "Repeated trials are correlated; use per-task bootstrap for certification.",
            "model_weight_training_executed": False, "independent_verification": False,
            "promotion_approved": False}
