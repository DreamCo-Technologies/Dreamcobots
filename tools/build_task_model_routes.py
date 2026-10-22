"""Generate evidence-gated model routing plans for all indexed bots, benchmarks and goals.

A route is a candidate selection, never proof that a model executed. No paid API
calls, downloads, or model training occur.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from tools.task_model_router import classify_task, rank_candidates

ROOT = Path(__file__).resolve().parents[1]


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def extract_bots(value):
    """Traverse catalog layouts without inventing missing bot identities."""
    if isinstance(value, list):
        for item in value:
            yield from extract_bots(item)
    elif isinstance(value, dict):
        if isinstance(value.get("slug") or value.get("id"), str) and (
            "capabilities" in value or "description" in value or "category" in value
        ):
            yield value
        else:
            for key in ("bots", "divisions", "items", "profiles"):
                if key in value:
                    yield from extract_bots(value[key])


def build_plan(root: Path = ROOT, candidates=None) -> dict:
    candidates = [] if candidates is None else candidates
    catalog = root / "config" / "generated" / "bots.catalog.json"
    goals = root / "reports" / "goals_to_gates.json"
    benchmarks = root / "config" / "buddy-benchmark-task-registry.json"
    missing = [str(p.relative_to(root)) for p in (catalog, goals, benchmarks) if not p.exists()]
    if missing:
        return {"schema": "dreamco.model_route_plan.v1", "status": "blocked_missing_sources", "missing": missing, "routes": []}
    routes = []
    seen = set()

    def append(kind, identity, task, metadata):
        key = (kind, str(identity))
        if key in seen:
            return
        seen.add(key)
        family = classify_task(task)
        decision = rank_candidates(family, candidates)
        routes.append({
            "kind": kind, "id": str(identity), "task_family": family,
            "selected_model": decision["selected"],
            "fallback": decision["fallback"],
            "status": "candidate_selected_not_executed" if decision["selected"] else "unverified_no_eligible_model",
            "metadata": metadata,
        })

    for bot in extract_bots(read_json(catalog)):
        identity = bot.get("slug") or bot.get("id")
        task = " ".join(str(x) for x in [bot.get("category", ""), bot.get("description", ""), *(bot.get("capabilities") or [])])
        append("bot", identity, task, {"division": bot.get("division"), "source": "config/generated/bots.catalog.json"})
    for task in read_json(benchmarks).get("tasks", []):
        append("benchmark", task, str(task).replace("_", " "), {"source": "config/buddy-benchmark-task-registry.json"})
    for index, goal in enumerate(read_json(goals).get("goals", [])):
        identity = goal.get("area_id") or f"goal_{index}"
        append("goal", identity, str(goal.get("goal", identity)), {
            "priority": goal.get("priority"), "source": "reports/goals_to_gates.json",
            "existing_status": goal.get("status"),
        })
    return {
        "schema": "dreamco.model_route_plan.v1",
        "status": "planning_only",
        "counts": {k: sum(r["kind"] == k for r in routes) for k in ("bot", "benchmark", "goal")},
        "routes": routes,
        "limitations": [
            "Catalog and goal coverage is limited to source registries; missing/orphan files require separate inventory audit.",
            "Selection does not demonstrate inference, benchmarking, training or runtime integration.",
            "Unverified candidates are rejected; no paid model is auto-selected.",
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", type=Path, help="Reviewed candidate metadata JSON array")
    parser.add_argument("--output", type=Path, help="Write routing plan JSON")
    args = parser.parse_args()
    candidates = read_json(args.candidates) if args.candidates else []
    if not isinstance(candidates, list):
        raise ValueError("Candidate metadata must be a JSON array")
    result = build_plan(candidates=candidates)
    output = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output, encoding="utf-8")
    else:
        print(output, end="")


if __name__ == "__main__":
    main()
