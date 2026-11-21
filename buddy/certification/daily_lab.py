"""Daily inventory, deduplication, gap analysis and training plans.

Does not scrape external code, train weights, or claim frontier comparisons.
Only evidence-backed measured results may be compared.
"""
from __future__ import annotations
import hashlib
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

KINDS = ("capability", "workflow", "tool", "function", "library", "generator")
DIMENSIONS = ("correctness", "safety", "reliability", "latency", "cost", "independence")

def fingerprint(entry):
    """Semantic key: identical contract and version, not similar-looking names."""
    stable = {k: entry.get(k) for k in ("kind", "contract", "version", "inputs", "outputs")}
    return hashlib.sha256(json.dumps(stable, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def inspect(entries, *, observations=None, frontier=None, revision="unknown"):
    """Generate conservative reviewable plans; no arbitrary commands are executed."""
    observations = observations or {}
    frontier = frontier or {}
    seen = {}
    results = []
    for entry in entries:
        kind, name = entry.get("kind"), entry.get("id")
        if kind not in KINDS or not isinstance(name, str) or not name:
            raise ValueError("invalid kind or id")
        if not isinstance(entry.get("contract"), str) or not entry["contract"]:
            raise ValueError("nonempty contract required")
        fp = fingerprint(entry)
        duplicate_of = seen.get(fp)
        seen.setdefault(fp, name)
        observation = observations.get(name, {})
        verified = observation.get("independent_verified") is True and bool(observation.get("receipt_sha256"))
        scores = observation.get("scores", {}) if verified else {}
        missing = [d for d in DIMENSIONS if d not in scores or not isinstance(scores[d], (int, float)) or isinstance(scores[d], bool)]
        benchmark = frontier.get(name, {})
        comparable = (verified and benchmark.get("independent_verified") is True
                      and bool(benchmark.get("receipt_sha256"))
                      and benchmark.get("task_set_hash") == observation.get("task_set_hash")
                      and benchmark.get("metric_version") == observation.get("metric_version")
                      and not missing
                      and all(isinstance(benchmark.get("scores", {}).get(d), (int, float))
                              for d in DIMENSIONS))
        gaps = (["Duplicate contract: review before consolidation"] if duplicate_of else [])
        gaps += ["Missing independently verified result"] if not verified else []
        gaps += ["Missing measured " + d for d in missing]
        if not comparable:
            gaps.append("Frontier comparison unavailable or not comparable")
        training = [
            "Collect authorized source and license/provenance metadata",
            "Map input/output contract and write independent task fixtures",
            "Run sandboxed unit, integration, adversarial and regression tests",
            "Deduplicate by exact contract/version; human-review semantic near-duplicates",
            "Record held-out task hashes, environment, metrics and independent receipts",
            "Compare a configured frontier model on identical tasks and scoring rules",
            "Propose supervised improvement; require rights and owner approval before training",
            "Retest holdouts, safety and regression; review before promotion",
        ]
        results.append({"id": name, "kind": kind, "fingerprint": fp,
                        "duplicate_of": duplicate_of, "verified": verified,
                        "measured_scores": scores, "frontier_comparable": comparable,
                        "frontier_gaps": ({d: benchmark["scores"][d] - scores[d] for d in DIMENSIONS}
                                          if comparable else None),
                        "gaps": gaps, "training_plan": training,
                        "training_executed": False, "reverse_engineering_executed": False,
                        "source_study_executed": False, "benchmark_executed": False})
    return {"schema": "dreamco.daily_capability_lab.v1", "revision": revision,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "scope": "manifest_inventory_not_all_repository_symbols",
            "counts": {"total": len(results), "duplicates": sum(bool(x["duplicate_of"]) for x in results),
                       "verified": sum(x["verified"] for x in results),
                       "frontier_comparable": sum(x["frontier_comparable"] for x in results)},
            "results": results}

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default="config/buddy/daily-lab-manifest.json")
    parser.add_argument("--output", default="website/data/buddy-daily-lab.json")
    parser.add_argument("--revision", default="unknown")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    data = json.loads((root / args.manifest).read_text(encoding="utf-8"))
    result = inspect(data["entries"], revision=args.revision)
    output = (root / args.output).resolve()
    if not output.is_relative_to(root / "website" / "data"):
        parser.error("output must be under website/data")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["counts"], sort_keys=True))

if __name__ == "__main__":
    main()
