#!/usr/bin/env python3
"""Build an evidence-first model benchmark scorecard.

A benchmark only becomes `mastered` when quality, speed, efficiency,
reliability and safety all meet the configured frontier-equivalence gates AND
there is real evidence for the run. Scores are relative to versioned measured
baselines, not an assertion of absolute world-best performance.
"""
from __future__ import annotations
import argparse, json, math
from pathlib import Path

DEFAULT_WEIGHTS = {"quality": .40, "speed": .20, "efficiency": .15, "reliability": .15, "safety": .10}
DEFAULT_GATES = {"quality": 95, "speed": 95, "efficiency": 90, "reliability": 98, "safety": 98, "overall": 95}

def pct(value: float) -> float:
    return round(max(0.0, min(100.0, value)), 2)

def score_against_baseline(value: float, baseline: float) -> float:
    if baseline <= 0:
        return 0.0
    return pct(value / baseline * 100.0)

def evaluate(result: dict, baseline: dict, gates: dict) -> dict:
    scores = {}
    for metric in DEFAULT_WEIGHTS:
        scores[metric] = score_against_baseline(float(result.get(metric, 0)), float(baseline.get(metric, 0)))
    overall = pct(sum(scores[k] * DEFAULT_WEIGHTS[k] for k in DEFAULT_WEIGHTS))
    evidence = result.get("evidence", [])
    mastered = bool(evidence) and all(scores[k] >= gates[k] for k in DEFAULT_WEIGHTS) and overall >= gates["overall"]
    return {"scores": scores, "overall": overall, "mastery": mastered, "evidence_count": len(evidence)}

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="config/model-benchmark-results.json")
    ap.add_argument("--output", default="website/data/model-benchmark-scorecard.json")
    args = ap.parse_args()
    src = Path(args.input)
    if not src.exists():
        raise SystemExit(f"Missing benchmark results: {src}")
    data = json.loads(src.read_text())
    baselines = data.get("frontier_baselines", {})
    gates = data.get("gates", DEFAULT_GATES)
    rows = []
    for item in data.get("results", []):
        baseline = baselines.get(item.get("benchmark_id"), {})
        evaluation = evaluate(item, baseline, gates)
        rows.append({**item, **evaluation})
    out = {
        "schema_version": "dreamco.model_benchmark_scorecard.v1",
        "generated_from": str(src),
        "methodology": "Relative-to-versioned-baseline; scores are not claims of absolute world-best capability.",
        "gates": gates,
        "weights": DEFAULT_WEIGHTS,
        "benchmark_count": len(rows),
        "mastered_count": sum(1 for r in rows if r["mastery"]),
        "results": rows,
    }
    dest = Path(args.output)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=2) + "\n")
    print(f"Generated {dest}: {len(rows)} benchmark results; {out['mastered_count']} mastered")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
