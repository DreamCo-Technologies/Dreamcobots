#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROGRAM = ROOT / "config" / "full-system-operational-certification.json"
OUT = ROOT / "config" / "generated" / "full-system-operational-certification.json"
REPORT = ROOT / "reports" / "FULL_SYSTEM_OPERATIONAL_CERTIFICATION.md"

SOURCES = {
    "verification": ROOT / "tmp" / "dreamco-verification" / "latest.json",
    "speed_accuracy": ROOT / "config" / "generated" / "system-speed-accuracy-benchmarks.json",
    "runtime_smoke": ROOT / "config" / "generated" / "production-runtime-smoke.json",
    "connections": ROOT / "config" / "generated" / "runtime-connection-readiness.json",
    "code_trust": ROOT / "config" / "generated" / "trusted-code-delivery-audit.json",
    "bot_accounting": ROOT / "config" / "generated" / "bot-accounting-placement-audit.json",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def main() -> int:
    program = json.loads(PROGRAM.read_text(encoding="utf-8"))
    docs = {name: load(path) for name, path in SOURCES.items()}
    blockers = []
    missing_evidence = [name for name, path in SOURCES.items() if not path.exists()]
    if missing_evidence:
        blockers.extend(f"missing evidence:{name}" for name in missing_evidence)

    verification = docs["verification"]
    speed = docs["speed_accuracy"]
    smoke = docs["runtime_smoke"]
    connections = docs["connections"]
    trust = docs["code_trust"]
    accounting = docs["bot_accounting"]

    checks = {
        "production_verification": verification.get("productionReady") is True,
        "speed_accuracy": speed.get("ok") is True,
        "production_runtime_smoke": smoke.get("passed") is True,
        "trusted_code_static_audit": not trust.get("release_blockers", ["missing"]),
        "bot_accounting": accounting.get("accounting_complete") is True,
    }
    for name, passed in checks.items():
        if not passed:
            blockers.append(name)

    core_operational_certified = not blockers
    all_connections_verified = connections.get("all_declared_runtime_connections_verified") is True
    if core_operational_certified and all_connections_verified:
        status = "certified"
    elif core_operational_certified:
        status = "core_certified_external_connection_gaps"
    else:
        status = "blocked"

    payload = {
        "schema": "dreamco.full_system_operational_certification.generated.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "core_operational_certified": core_operational_certified,
        "all_declared_runtime_connections_verified": all_connections_verified,
        "fully_operational_and_connected_claim_allowed": core_operational_certified and all_connections_verified,
        "checks": checks,
        "release_blockers": sorted(set(blockers)),
        "connection_summary": {
            "declared": connections.get("connection_count", 0),
            "runtime_verified": connections.get("runtime_verified_count", 0),
        },
        "speed_summary": {
            "passed": speed.get("speed_passed", 0),
            "total": speed.get("speed_total", 0),
        },
        "accuracy_summary": {
            "passed": speed.get("accuracy_passed", 0),
            "total": speed.get("accuracy_total", 0),
        },
        "runtime_summary": {
            "startup_seconds": smoke.get("startup_seconds"),
            "health_latency_ms": smoke.get("health_latency_ms"),
        },
        "verification_summary": verification.get("totals", {}),
        "truth_boundary": program["truth_rule"],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Full System Operational Certification",
        "",
        f"Status: **{status}**",
        f"Core operationally certified: **{core_operational_certified}**",
        f"All declared runtime connections verified: **{all_connections_verified}**",
        f"Fully operational + connected claim allowed: **{payload['fully_operational_and_connected_claim_allowed']}**",
        "",
        "## Evidence",
        "",
    ]
    for name, passed in checks.items():
        lines.append(f"- {name}: {'PASS' if passed else 'FAIL'}")
    lines += [
        f"- Speed: {payload['speed_summary']['passed']}/{payload['speed_summary']['total']}",
        f"- Accuracy: {payload['accuracy_summary']['passed']}/{payload['accuracy_summary']['total']}",
        f"- Runtime connections: {payload['connection_summary']['runtime_verified']}/{payload['connection_summary']['declared']}",
        f"- Startup seconds: {payload['runtime_summary']['startup_seconds']}",
        f"- Health latency ms: {payload['runtime_summary']['health_latency_ms']}",
    ]
    if blockers:
        lines += ["", "## Blockers", ""] + [f"- {b}" for b in sorted(set(blockers))]
    lines += ["", "> This certification is commit- and environment-specific. External integrations require current authorized runtime evidence."]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps({"status": status, "core_operational_certified": core_operational_certified, "all_connections_verified": all_connections_verified, "blockers": sorted(set(blockers))}, indent=2))
    return 0 if core_operational_certified else 1


if __name__ == "__main__":
    raise SystemExit(main())
