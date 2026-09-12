#!/usr/bin/env python3
"""Build the public-safe investor/operator Actions prospectus."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
contract = json.loads((ROOT / "config/actions-control-prospectus.json").read_text())
health = json.loads((ROOT / "website/data/actions-health-report.json").read_text())

rows = []
for workflow in health.get("findings", []):
    controls = workflow.get("controls", {})
    evidence = "static_checks_passed" if workflow.get("static_status") == "static_checks_passed" else "blocked"
    rows.append({
        "workflow": workflow["workflow"],
        "name": workflow["display_name"],
        "goal": workflow.get("goal", "repository operations"),
        "purpose": workflow["purpose"],
        "what_happens": workflow.get("what_happens", []),
        "outputs": workflow.get("outputs", []),
        "benchmark_commands": workflow.get("benchmark_commands", []),
        "triggers": workflow.get("triggers", []),
        "github_url": workflow.get("github_url"),
        "static_status": evidence,
        "runtime_status": workflow.get("runtime_status", "unknown_until_run_evidence_loaded"),
        "errors": workflow.get("errors", []),
        "warnings": workflow.get("warnings", []),
        "runner_jobs": controls.get("runner_jobs", 0),
        "controls": controls,
        "upgrades": workflow.get("upgrades", []),
        "possible_duplicate": workflow.get("possible_duplicate", False),
        "duplicate_candidate_group": workflow.get("duplicate_candidate_group"),
        "possible_duplicates": workflow.get("possible_duplicates", []),
        "progress": "configured" if evidence == "static_checks_passed" else "blocked",
        "investor_note": "Static configuration is inspectable. Operational evidence is required before claiming workflow health, product readiness, or model mastery.",
    })

controls = [{**item, "progress": "configured", "workflow_count": len(rows)} for item in contract["controls"]]
summary = {
    **health.get("summary", {}),
    "control_areas": len(controls),
    "declared_goals": sorted({row["goal"] for row in rows}),
    "benchmarked_workflows": sum(bool(row["benchmark_commands"]) for row in rows),
}
out = {
    "schema": "dreamco.actions_prospectus.v2",
    "generated_from": ["config/actions-control-prospectus.json", "website/data/actions-health-report.json"],
    "summary": summary,
    "controls": controls,
    "duplicate_candidate_groups": health.get("duplicate_candidate_groups", []),
    "workflows": rows,
    "progress_model": contract["progress_model"],
    "truth_boundary": "This prospectus explains intent and static evidence. GitHub run results, retained artifacts, benchmarks, and production observations are required to prove operation. Duplicate candidates are never deleted automatically.",
}
repository_output = ROOT / "config/generated/actions-prospectus.json"
repository_output.parent.mkdir(parents=True, exist_ok=True)
repository_output.write_text(json.dumps(out, indent=2) + "\n")
public_output = ROOT / "website/data/actions-prospectus.json"
public_output.parent.mkdir(parents=True, exist_ok=True)
public_out = {key: value for key, value in out.items() if key != "workflows"}
public_out["workflow_catalog_url"] = "data/actions-health-report.json"
public_out["workflow_count"] = len(rows)
public_output.write_text(json.dumps(public_out, separators=(",", ":")) + "\n")
print(f"Generated Actions prospectus: {len(rows)} workflows, {len(controls)} controls, {summary.get('possible_duplicate_groups', 0)} possible duplicate groups")
