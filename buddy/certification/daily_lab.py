"""Daily evidence-first capability gap, deduplication and training-plan builder.

Never treats an unexecuted comparison as a frontier benchmark. Does not train,
download models, or ingest unlicensed third-party code.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from buddy.certification.engine import run_suite, validate_manifest

def normalized(value):
    return " ".join(str(value).lower().split())

def fingerprint(item):
    """Deduplicate equivalent descriptions within a domain, never by name alone."""
    basis = normalized(item["domain"]) + "|" + normalized(item["description"])
    return hashlib.sha256(basis.encode()).hexdigest()[:16]

def compare_and_plan(manifest, report):
    validate_manifest(manifest)
    by_id = {r["id"]: r for r in report["results"]}
    groups = {}
    for item in manifest["capabilities"]:
        groups.setdefault(fingerprint(item), []).append(item["id"])
    duplicates = [ids for ids in groups.values() if len(ids) > 1]
    plans = []
    for item in manifest["capabilities"]:
        outcome = by_id[item["id"]]
        observed = outcome["observed"]
        missing = []
        if not item["test_module"]:
            missing.append("Add a bounded executable unit/integration test module")
        if observed != "tested":
            missing.append("Pass repeatable local tests at a pinned commit")
        missing += [
            "Design independently authored held-out tasks and keep them out of training",
            "Record approved frontier model/version and identical comparison fixtures",
            "Run authorized frontier and Buddy baselines with measured cost, quality and safety",
            "Compare failures and group common root causes without copying restricted code",
            "Propose original implementation or permitted fine-tuning dataset with provenance",
            "Retest on holdout, security, regression and recovery checks",
            "Request human review before promotion or deployment",
        ]
        plans.append({
            "id": item["id"], "domain": item["domain"],
            "status": observed, "gap_count": len(missing), "gaps": missing,
            "reverse_engineering_scope": "Authorized public APIs, observable behavior, and permitted source only",
            "distillation_status": "not_started",
            "training_status": "not_started",
            "frontier_comparison_status": "not_run",
            "frontier_score": None, "buddy_score": None,
            "priority": "P0" if item["domain"] == "security" else "P1",
            "proposed_training_method": "retrieval_and_supervised_practice_first",
            "requires_license_review": True, "requires_owner_approval": True
        })
    return {"schema": "dreamco.daily_capability_gap_lab.v1",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "revision": report["revision"],
            "source": report["source"],
            "capability_count": len(plans),
            "duplicate_candidate_groups": duplicates,
            "deduplication_action": "review_only_no_deletions",
            "benchmark_status": "no_frontier_runs_performed",
            "training_status": "no_model_training_performed",
            "plans": plans}

def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--execute-local-tests", action="store_true")
    p.add_argument("--revision", default="unknown")
    args = p.parse_args(argv)
    root = Path(__file__).resolve().parents[2]
    manifest = json.loads((root / "config/buddy/capability-certification-goals.json").read_text())
    report = run_suite(manifest, repo_root=root, execute=args.execute_local_tests, revision=args.revision)
    gaps = compare_and_plan(manifest, report)
    out = root / "website/data"
    out.mkdir(parents=True, exist_ok=True)
    (out / "buddy-capability-certification.json").write_text(json.dumps(report, indent=2) + "\n")
    (out / "buddy-daily-capability-gaps.json").write_text(json.dumps(gaps, indent=2) + "\n")
    print(json.dumps({"capabilities": gaps["capability_count"],
                      "duplicate_groups": len(gaps["duplicate_candidate_groups"]),
                      "frontier_runs": 0, "trained_models": 0,
                      "local_failures": report["summary"]["failed"]}))
    return 1 if report["summary"]["failed"] else 0

if __name__ == "__main__":
    raise SystemExit(main())
