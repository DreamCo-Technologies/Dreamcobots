"""Fail-closed, task-specific teacher selection from independently verified benchmark receipts.

No model is selected for distillation unless output-training rights were explicitly
reviewed. Rankings do not themselves authorize API use or training.
"""
from __future__ import annotations
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

DOMAINS = {"coding", "research", "multi_step_tools", "reasoning", "multilingual", "summarization", "classification", "math", "science"}
METRICS = ("quality", "safety", "completion", "latency_ms", "cost_usd")

def select_teachers(records: list[dict[str, Any]], *, max_age_days: int = 30, min_trials: int = 3,
                    now: datetime | None = None) -> dict[str, Any]:
    now = now or datetime.now(timezone.utc)
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    rejected = 0
    for row in records:
        try:
            domain = row["domain"]
            if domain not in DOMAINS or row.get("independent_verified") is not True:
                raise ValueError("unverified")
            if row.get("teacher_output_training_permitted") is not True or row.get("license_reviewed") is not True:
                raise ValueError("rights")
            if not row.get("benchmark_id") or not row.get("model_id") or not row.get("model_revision"):
                raise ValueError("identity")
            if not row.get("evidence_sha256") or len(row["evidence_sha256"]) != 64:
                raise ValueError("evidence")
            when = datetime.fromisoformat(row["evaluated_at"].replace("Z", "+00:00"))
            if when.tzinfo is None or (now - when).total_seconds() < 0 or (now - when).days > max_age_days:
                raise ValueError("stale")
            scores = [float(row[k]) for k in METRICS]
            if any(not __import__("math").isfinite(v) for v in scores):
                raise ValueError("nonfinite")
            quality, safety, completion, latency, cost = scores
            if not (0 <= quality <= 1 and .9 <= safety <= 1 and .7 <= completion <= 1 and latency >= 0 and cost >= 0):
                raise ValueError("metrics")
            groups[domain].append(row)
        except (KeyError, ValueError, TypeError, OverflowError, AttributeError):
            rejected += 1
    champions = {}
    for domain, candidates in sorted(groups.items()):
        by_model = defaultdict(list)
        for row in candidates:
            by_model[(row["model_id"], row["model_revision"], row["benchmark_id"])].append(row)
        eligible = []
        for (model, revision, benchmark), trials in by_model.items():
            if len(trials) < min_trials:
                continue
            quality = sum(float(x["quality"]) for x in trials) / len(trials)
            safety = sum(float(x["safety"]) for x in trials) / len(trials)
            completion = sum(float(x["completion"]) for x in trials) / len(trials)
            latency = sum(float(x["latency_ms"]) for x in trials) / len(trials)
            cost = sum(float(x["cost_usd"]) for x in trials) / len(trials)
            score = round(.65 * quality + .2 * completion + .15 * safety - min(.15, cost * .01), 6)
            eligible.append({"model_id": model, "revision": revision, "benchmark_id": benchmark,
                             "trials": len(trials), "score": score, "quality": round(quality, 5),
                             "completion": round(completion, 5), "safety": round(safety, 5),
                             "mean_latency_ms": round(latency, 2), "mean_cost_usd": round(cost, 6),
                             "status": "candidate_requires_human_approval"})
        eligible.sort(key=lambda x: (-x["score"], x["mean_cost_usd"], x["mean_latency_ms"], x["model_id"]))
        champions[domain] = {"candidates": eligible, "provisional_leader": eligible[0] if eligible else None,
                             "distillation_authorized": False}
    return {"domains": champions, "rejected_records": rejected,
            "automatic_training_enabled": False, "external_api_calls_made": False,
            "warning": "Verification flags and hashes are claims; authenticate receipts before approval."}
