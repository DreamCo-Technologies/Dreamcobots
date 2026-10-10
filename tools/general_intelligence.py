#!/usr/bin/env python3
"""Generate fail-closed evaluation Pages from real, validated repository artifacts."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from buddy_os.evaluation.evidence import assess, distill, promotion, verify_artifacts
from buddy_os.evaluation.review import POLICY, SECRET, digest

OUTPUT = ROOT / "website/data/general-intelligence.json"
MANIFEST = ROOT / "website/data/general-intelligence-manifest.json"
LEDGER = ROOT / "evidence/general-intelligence/ledger.json"
SUITES = ROOT / "config/general-intelligence/suites.json"


def registered(run, suites):
    for suite in suites["registered_suites"]:
        if suite.get("id") != run.get("suite_id") or suite.get("version") != run.get("suite_version"):
            continue
        if not suite.get("reviewer") or not suite.get("registered_at"):
            return False
        try:
            from datetime import datetime
            if datetime.fromisoformat(suite["registered_at"].replace("Z", "+00:00")) >= datetime.fromisoformat(run["timestamp"].replace("Z", "+00:00")):
                return False
            expected = {c["id"]: c for c in suite["cases"]}
            return (run["suite_hash"] == digest(suite) and set(run["expected_cases"]) == set(expected)
                    and all(c["fixture_hash"] == expected[c["id"]]["fixture_hash"]
                            and c["family"] == expected[c["id"]]["family"]
                            and c["split"] == expected[c["id"]]["split"] for c in run["cases"]))
        except (ValueError, TypeError, KeyError):
            return False
    return False


def build(root=ROOT):
    ledger = json.loads((root / "evidence/general-intelligence/ledger.json").read_text())
    suites = json.loads((root / "config/general-intelligence/suites.json").read_text())
    if ledger.get("schema") != "dreamco.general_intelligence_ledger.v1" or not isinstance(ledger.get("runs"), list):
        raise ValueError("Missing or invalid ledger; no readiness claim may be published")
    runs, lessons, results = [], [], {}
    ids = [r.get("id") for r in ledger["runs"]]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate run ids")
    for run in ledger["runs"]:
        if SECRET.search(json.dumps(run)):
            raise ValueError("Credential-like content in run metadata; publication blocked")
        result = assess(run)
        valid_artifacts = verify_artifacts(run, root / "evidence/general-intelligence")
        preregistered = registered(run, suites)
        baseline = next((r for r in ledger["runs"] if r.get("id") == run.get("baseline_id")), None)
        baseline_valid = baseline is not None and run.get("baseline_hash") == digest(baseline)
        if not valid_artifacts:
            result["errors"].append("Runtime artifacts missing or hash mismatch")
        if not preregistered:
            result["errors"].append("No matching preregistered suite")
        if not baseline_valid:
            result["errors"].append("Versioned baseline absent or hash mismatch")
        status = "verified" if result["eligible"] and valid_artifacts and preregistered and baseline_valid else result["status"]
        results[run["id"]] = status
        # Explicit public projection: private prompts, outputs, reviewer identities and
        # arbitrary artifact contents never get copied to GitHub Pages.
        runs.append({"id": run["id"], "capability": run.get("capability"), "status": status,
                     "hash": digest(run), "transfer": {"cases": sum(c.get("split") == "transfer" for c in run.get("cases", [])), "status": status},
                     "red_team": {k: run.get("red_team", {}).get(k) for k in POLICY["red_team"]},
                     "metrics": result.get("metrics"), "calibration": result.get("calibration"),
                     "errors": result["errors"], "suite_id": run.get("suite_id"), "subject": run.get("subject"),
                     "cost_usd": sum(c["cost_usd"] for c in run.get("cases", []) if isinstance(c, dict) and type(c.get("cost_usd")) in (float, int)),
                     "artifact_hashes": [a.get("sha256") for a in run.get("artifacts", []) if isinstance(a, dict)]})
        lesson = distill(run)
        lesson.pop("provenance")
        lessons.append(lesson)
    matrix = []
    for capability in POLICY["capabilities"]:
        matching = [r for r in runs if r["capability"] == capability["id"]]
        # A new failure invalidates an old successful status; no cherry-picking.
        status = matching[-1]["status"] if matching else "untested"
        matrix.append({**capability, "status": status, "run_ids": [r["id"] for r in matching],
                       "gap": "Human independent review still required" if status == "verified" else "No complete, reproducible, reviewed runtime evidence"})
    catalog = json.loads((root / "config/master_bot_registry.json").read_text())
    divisions = catalog.get("divisions", [])
    if isinstance(divisions, dict):
        divisions = list(divisions)
    sections = [{"id": title.lower().replace("/", "-").replace(" ", "-"), "title": title} for title in POLICY["sections"]]
    return {"schema": "dreamco.general_intelligence_public.v1", "framework_version": POLICY["version"],
            "source_hash": digest({"policy": POLICY, "suites": suites, "ledger": ledger,
                                   "implementation": {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                                                      for p in sorted(list(root.glob("buddy_os/evaluation/*.py")) + [root / "tools/general_intelligence.py", root / "tools/general_intelligence_bridge.py", root / "tools/buddy_local_bridge.py"]) }}),
            "status": "evidence_incomplete" if any(c["status"] != "reviewed" for c in matrix) else "human_claim_review_required",
            "claim": "No AGI or frontier claim. Framework checks are not model capability benchmarks.",
            "automatic_agi_claim": False, "automatic_frontier_claim": False,
            "matrix": matrix, "sections": sections, "runs": runs, "lessons": lessons,
            "public_benchmarks": POLICY["public_benchmarks"], "native_checks": suites["native_checks"],
            "autonomy": POLICY["autonomy"], "approval_actions": POLICY["approval_actions"],
            "red_team_categories": POLICY["red_team"],
            "division_coverage": {"source": "config/master_bot_registry.json", "declared_divisions": len(divisions), "verified": 0, "status": "untested"},
            "queue": {"status": "private_local_console_required", "actions": None},
            "long_horizon": {"status": "untested", "runs": []},
            "promotions": [], "benchmark_deltas": [], "reviewed_count": 0,
            "integrations": POLICY["native_sources"],
            "truth_boundaries": ["No private review queue is published.", "Unconfigured modalities are untested.", "Public benchmarks are disabled until pinned and license-reviewed.", "Unknown pretraining contamination cannot be ruled out.", "Orchestration never changes proprietary model weights."]}


def generate(check=False):
    data = build()
    manifest = {"schema": "dreamco.general_intelligence_pages_manifest.v1", "page": "general-intelligence.html",
                "script": "general-intelligence.js", "data": "data/general-intelligence.json",
                "status": data["status"], "source_hash": data["source_hash"], "sections": data["sections"],
                "source_files": ["config/general-intelligence/framework.json", "config/general-intelligence/suites.json", "evidence/general-intelligence/ledger.json"]}
    failures = []
    for path, payload in ((OUTPUT, data), (MANIFEST, manifest)):
        rendered = json.dumps(payload, indent=2, allow_nan=False) + "\n"
        if check:
            if not path.exists() or path.read_text() != rendered:
                failures.append(str(path.relative_to(ROOT)))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(rendered)
    if failures:
        raise ValueError("Stale evaluation Pages artifacts: " + ", ".join(failures))
    return {"status": data["status"], "capabilities": len(data["matrix"]), "verified": sum(c["status"] == "verified" for c in data["matrix"]), "runs": len(data["runs"])}


def native_checks(output):
    suites = json.loads(SUITES.read_text())
    results = []
    for suite in suites["native_checks"]:
        command = list(suite["command"])
        command[0] = sys.executable
        import time
        started = time.monotonic()
        try:
            proc = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=180)
            result = {"id": suite["id"], "scope": suite["scope"], "exit_code": proc.returncode,
                      "runtime_seconds": time.monotonic() - started, "log_hash": hashlib.sha256((proc.stdout + proc.stderr).encode()).hexdigest()}
        except subprocess.TimeoutExpired:
            result = {"id": suite["id"], "scope": suite["scope"], "exit_code": 124, "runtime_seconds": time.monotonic() - started}
        results.append(result)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({"scope": "framework_controls_only", "model_called": False, "results": results}, indent=2) + "\n")
    return all(r["exit_code"] == 0 for r in results)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--native", type=Path, help="Run repo-native framework checks and save measured results")
    parser.add_argument("--assess", type=Path, help="Validate a submitted run without executing models")
    args = parser.parse_args()
    if args.native:
        return 0 if native_checks(args.native) else 1
    if args.assess:
        result = assess(json.loads(args.assess.read_text()))
        print(json.dumps(result, indent=2, allow_nan=False))
        return 0 if result["eligible"] else 1
    print(json.dumps(generate(args.check)))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError, KeyError) as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(1)
