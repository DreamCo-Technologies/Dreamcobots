#!/usr/bin/env python3
"""Plan repairs for repository health without pretending unknown checks passed."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

CATEGORIES = {
    "workflow": ["workflow", "actions", "yaml", "ci"],
    "dependency": ["dependency", "npm", "pip", "package"],
    "test": ["test", "pytest", "jest", "coverage"],
    "security": ["security", "secret", "vulnerability", "sast"],
    "benchmark": ["benchmark", "regression", "evaluation", "score"],
    "runtime": ["runtime", "production", "deploy", "route", "health"],
    "review": ["pull request", "pr", "merge", "conflict", "review"],
}

def classify(text: str) -> list[str]:
    lowered = text.lower()
    hits = []
    for category, words in CATEGORIES.items():
        if any(word in lowered for word in words):
            hits.append(category)
    return hits or ["unknown"]

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="JSON list/object of observed failures")
    parser.add_argument("--output", default="artifacts/greenkeeper/repair-plan.json")
    args = parser.parse_args()
    source = json.loads(Path(args.input).read_text(encoding="utf-8"))
    records = source if isinstance(source, list) else source.get("failures", [])
    plan = []
    for item in records:
        text = json.dumps(item, sort_keys=True) if isinstance(item, dict) else str(item)
        categories = classify(text)
        plan.append({
            "observation": item,
            "categories": categories,
            "status": "needs_evidence",
            "recommended_system": {
                "workflow": "CI/workflow repair validator",
                "dependency": "dependency compatibility and lockfile validator",
                "test": "test impact and regression runner",
                "security": "security/dependency scan gate",
                "benchmark": "benchmark regression gate",
                "runtime": "production smoke/route health checker",
                "review": "PR review/rebuild controller",
                "unknown": "manual investigation queue",
            }.get(categories[0], "manual investigation queue"),
        })
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    result = {
        "schema": "dreamco.greenkeeper_repair_plan.v1",
        "truth_rule": "unknown is never green",
        "auto_build_policy": "build only bounded validators/repair scaffolds; require verification before promotion",
        "observations": len(plan),
        "plan": plan,
    }
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
