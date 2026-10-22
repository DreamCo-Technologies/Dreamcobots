#!/usr/bin/env python3
"""Reconcile catalogs and publish evidence-backed production readiness truth."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "config/generated/bots.catalog.json"
MANIFESTS = ROOT / "config/bots/division-manifests.generated.json"
READINESS = ROOT / "config/generated/bot-production-readiness.json"
COMMAND = ROOT / "website/data/command-center/divisions.json"
BOOTCAMP = ROOT / "config/buddy-professional-bootcamp.json"
ADAPTERS = ROOT / "config/buddy-student-adapter-registry.json"
HISTORY = ROOT / "config/generated/sandbox-24h-history.json"
OUT = ROOT / "config/generated/production-evidence-ledger.json"
WEB = ROOT / "website/data/production-evidence-ledger.json"
REPORT = ROOT / "reports/PRODUCTION_EVIDENCE_LEDGER.md"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build() -> dict:
    catalog, manifests, readiness, command = map(load, (CATALOG, MANIFESTS, READINESS, COMMAND))
    bootcamp, adapters = load(BOOTCAMP), load(ADAPTERS)
    history = load(HISTORY) if HISTORY.exists() else {"summary": {}}
    canonical = {row["name"]: row for row in catalog["divisions"]}
    supplemental = {row["name"]: row for row in catalog["supplemental_divisions"]}
    real = canonical | supplemental
    manifest_names = {row["name"] for row in manifests["divisions"]}
    readiness_names = {row["division"] for row in readiness["divisions"]}
    command_names = {row["name"] for row in command["items"]}
    pseudo = sorted((manifest_names | readiness_names) - set(real))

    weight_ok = bool(adapters.get("truth", {}).get("trained_weights_exist"))
    gesture_ok = bool(bootcamp.get("truth", {}).get("gesture_camera_adapter_connected"))
    deployment_count = int(bootcamp.get("truth", {}).get("professional_deployments_verified", 0))
    soak = history.get("summary", {})
    soak_ok = bool(soak.get("complete") is True and soak.get("status") == "passed_24h")
    global_gates = [
        {"id": "real_model_weights", "passed": weight_ok, "evidence": "config/buddy-student-adapter-registry.json", "requires": "Artifact files with SHA-256 hashes, model card, training run, provenance, and evaluation scorecard."},
        {"id": "gesture_hardware", "passed": gesture_ok, "evidence": "config/buddy-professional-bootcamp.json", "requires": "Permissioned camera/device adapter, physical-device identifier, calibration receipt, consent state, and passing gesture test."},
        {"id": "sandbox_24h", "passed": soak_ok, "evidence": "config/generated/sandbox-24h-history.json", "requires": "At least 24 successful ticks across at least 24 real elapsed hours, with zero failed ticks."},
        {"id": "professional_deployment", "passed": deployment_count > 0, "evidence": "config/buddy-professional-bootcamp.json", "requires": "A versioned deployment receipt with environment, release SHA, health checks, rollback, telemetry, and owner acceptance."},
    ]
    divisions = []
    for name, row in sorted(real.items()):
        tier = "canonical" if name in canonical else "supplemental"
        local = [
            {"id": "catalog_record", "passed": True},
            {"id": "division_manifest", "passed": name in manifest_names},
            {"id": "production_readiness_record", "passed": name in readiness_names},
            {"id": "pages_command_record", "passed": name in command_names if tier == "canonical" else True, "note": "Supplemental divisions are published through this ledger and fleet catalog." if tier == "supplemental" else "Canonical command-center record required."},
            {"id": "shared_runtime_route", "passed": True},
            {"id": "verified_external_runtime", "passed": False},
            {"id": "authentication_and_authorization", "passed": False},
            {"id": "deployment_telemetry_and_rollback", "passed": False},
        ]
        blockers = [gate["id"] for gate in local if not gate["passed"]] + [gate["id"] for gate in global_gates if not gate["passed"]]
        divisions.append({
            "name": name, "tier": tier, "profiles": int(row.get("profile_count", 0)),
            "source": row.get("source"), "production_ready": not blockers,
            "status": "production_ready" if not blockers else "evidence_required",
            "gates": local, "blockers": blockers,
        })
    return {
        "schema": "dreamco.production_evidence_ledger.v1",
        "truth_rule": "A catalog entry, shared runtime route, plan, or passing repository test is not production evidence. Every required gate must carry its own current receipt.",
        "summary": {
            "canonical_divisions": len(canonical), "supplemental_divisions": len(supplemental),
            "real_divisions": len(real), "catalog_profiles": int(catalog["summary"]["combined_routable_profiles"]),
            "production_ready_divisions": sum(row["production_ready"] for row in divisions),
            "trained_weight_artifacts": int(bootcamp.get("truth", {}).get("trained_weight_artifacts", 0)),
            "gesture_hardware_verified": gesture_ok, "professional_deployments_verified": deployment_count,
            "soak_24h_verified": soak_ok, "catalogs_reconciled": set(real) <= manifest_names and set(real) <= readiness_names,
        },
        "catalog_reconciliation": [
            {"source": "config/generated/bots.catalog.json", "scope": "canonical", "divisions": len(canonical)},
            {"source": "config/generated/bots.catalog.json#supplemental_divisions", "scope": "supplemental", "divisions": len(supplemental)},
            {"source": "config/bots/division-manifests.generated.json", "scope": "real divisions plus routing buckets", "records": len(manifests["divisions"])},
            {"source": "config/generated/bot-production-readiness.json", "scope": "real divisions plus exclusion bucket", "records": len(readiness["divisions"])},
            {"source": "website/data/command-center/divisions.json", "scope": "canonical", "divisions": len(command["items"])},
        ],
        "non_division_buckets": [{"name": name, "reason": "routing or exclusion bucket; not counted as a business division"} for name in pseudo],
        "global_gates": global_gates, "soak_progress": soak,
        "divisions": divisions,
    }


def report(data: dict) -> str:
    s = data["summary"]
    lines = [
        "# Production evidence ledger", "",
        "> Repository truth only. Missing evidence remains red; no plan or catalog label is promoted into a deployment claim.", "",
        f"- Real divisions: **{s['real_divisions']}** ({s['canonical_divisions']} canonical + {s['supplemental_divisions']} supplemental)",
        f"- Routable profiles: **{s['catalog_profiles']}**", f"- Production-ready divisions: **{s['production_ready_divisions']}**",
        f"- Trained weight artifacts: **{s['trained_weight_artifacts']}**", f"- Gesture hardware verified: **{str(s['gesture_hardware_verified']).lower()}**",
        f"- 24-hour soak verified: **{str(s['soak_24h_verified']).lower()}**", f"- Professional deployments verified: **{s['professional_deployments_verified']}**", "",
        "## Global evidence gates", "", "| Gate | Status | Required evidence |", "|---|---|---|",
    ]
    for gate in data["global_gates"]:
        lines.append(f"| {gate['id']} | {'PASS' if gate['passed'] else 'EVIDENCE REQUIRED'} | {gate['requires']} |")
    lines += ["", "## Division matrix", "", "| Division | Scope | Profiles | Status |", "|---|---:|---:|---|"]
    for row in data["divisions"]:
        lines.append(f"| {row['name']} | {row['tier']} | {row['profiles']} | {row['status']} |")
    lines += ["", "## Reconciliation notes", ""]
    for row in data["non_division_buckets"]:
        lines.append(f"- `{row['name']}` — {row['reason']}.")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    data = build()
    payload = json.dumps(data, indent=2) + "\n"
    outputs = {OUT: payload, WEB: payload, REPORT: report(data)}
    if args.check:
        stale = [str(path.relative_to(ROOT)) for path, value in outputs.items() if not path.exists() or path.read_text(encoding="utf-8") != value]
        if stale:
            raise SystemExit("stale production evidence outputs: " + ", ".join(stale))
    else:
        for path, value in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(value, encoding="utf-8")
    print(json.dumps(data["summary"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
