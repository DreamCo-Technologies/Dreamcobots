"""Evidence-based per-task champion selection, never a universal model ranking."""
from collections import defaultdict
from datetime import datetime, timezone

METRICS = ("task_completion", "accuracy", "reasoning_quality", "tool_execution", "reliability", "speed", "safety", "cost")
DOMAINS = ("coding", "research", "multi_step_tools")

def choose_champions(records, *, min_trials=3, min_completion=0.7, max_age_days=30, now=None):
    """Select champion only from comparable independently verified task-specific evidence.

    Scores are normalized 0..1 with higher better, including speed and cost.
    Ties broken by reliability then model ID. Unknown tasks remain unranked.
    """
    now = now or datetime.now(timezone.utc)
    groups = defaultdict(list)
    for row in records:
        if row.get("domain") not in DOMAINS or not row.get("task_id"):
            continue
        if row.get("independent_verified") is not True or not row.get("receipt_sha256"):
            continue
        if not row.get("task_set_hash") or not row.get("scorer_version"):
            continue
        if row.get("trials", 0) < min_trials:
            continue
        try:
            measured = datetime.fromisoformat(row["measured_at"].replace("Z", "+00:00"))
            if measured.tzinfo is None or (now - measured).total_seconds() > max_age_days * 86400 or measured > now:
                continue
        except (KeyError, TypeError, ValueError):
            continue
        scores = row.get("scores", {})
        if any(not isinstance(scores.get(k), (int, float)) or isinstance(scores.get(k), bool)
               or not 0 <= scores[k] <= 1 for k in METRICS):
            continue
        if scores["task_completion"] < min_completion or scores["safety"] < 0.9:
            continue
        groups[(row["domain"], row["task_id"], row["task_set_hash"], row["scorer_version"])].append(row)
    champions = []
    for (domain, task, task_hash, scorer), candidates in sorted(groups.items()):
        def value(row):
            s = row["scores"]
            return (0.3*s["task_completion"] + 0.2*s["accuracy"] +
                    0.12*s["reasoning_quality"] + 0.1*s["tool_execution"] +
                    0.1*s["reliability"] + 0.08*s["safety"] +
                    0.05*s["speed"] + 0.05*s["cost"])
        ordered = sorted(candidates, key=lambda r: (-value(r), -r["scores"]["reliability"], r["model_id"]))
        top = ordered[0]
        champions.append({"domain": domain, "task_id": task, "task_set_hash": task_hash,
                          "scorer_version": scorer, "champion_model": top["model_id"],
                          "champion_score": round(value(top), 6),
                          "runner_up": ordered[1]["model_id"] if len(ordered)>1 else None,
                          "models_evaluated": len(ordered), "single_model_only": len(ordered)==1,
                          "selection_basis": "independently_verified_comparable_trials",
                          "buddy_gap": next((round(value(top)-value(r), 6) for r in ordered
                                             if r["model_id"] == "buddy"), None)})
    return {"schema": "dreamco.task_champions.v1", "champions": champions,
            "unranked_policy": "No verified comparable results: benchmark candidates first, do not guess champion",
            "limitations": "Only compared models on matching task set/scorer. No global best-model claim."}
