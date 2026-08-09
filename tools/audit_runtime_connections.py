#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "website" / "data" / "buddy-connection-catalog.json"
EVIDENCE = ROOT / "config" / "runtime-connection-evidence.json"
OUT = ROOT / "config" / "generated" / "runtime-connection-readiness.json"
REPORT = ROOT / "reports" / "RUNTIME_CONNECTION_READINESS.md"


def main() -> int:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    evidence_doc = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    evidence_by = {row.get("connection_id"): row for row in evidence_doc.get("evidence", []) if row.get("connection_id")}

    rows = []
    for profile in catalog.get("platform_profiles", []):
        cid = profile.get("id")
        evidence = evidence_by.get(cid)
        if evidence and evidence.get("status") == "runtime_verified":
            state = "runtime_verified"
        elif evidence and evidence.get("status") == "sandbox_verified":
            state = "sandbox_verified"
        elif evidence and evidence.get("status") in {"blocked", "revoked"}:
            state = evidence.get("status")
        else:
            auth = profile.get("auth_method")
            auth_row = next((x for x in catalog.get("auth_methods", []) if x.get("id") == auth), None)
            auth_status = (auth_row or {}).get("status")
            if auth_status == "adapter_ready":
                state = "adapter_ready"
            elif auth_status in {"user_handoff", "configuration_required"}:
                state = "credentials_required"
            else:
                state = "declared"
        rows.append({
            "connection_id": cid,
            "label": profile.get("label"),
            "contract": profile.get("contract"),
            "auth_method": profile.get("auth_method"),
            "state": state,
            "runtime_verified": state == "runtime_verified",
            "evidence_reference": (evidence or {}).get("evidence_reference"),
            "tested_at": (evidence or {}).get("tested_at"),
        })

    verified = sum(1 for r in rows if r["runtime_verified"])
    payload = {
        "schema": "dreamco.runtime_connection_readiness.v1",
        "connection_count": len(rows),
        "runtime_verified_count": verified,
        "all_declared_runtime_connections_verified": bool(rows) and verified == len(rows),
        "connections": rows,
        "truth_boundary": evidence_doc["truth_rule"],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Runtime Connection Readiness",
        "",
        f"- Declared platform connections: **{len(rows)}**",
        f"- Runtime verified: **{verified}**",
        f"- All verified: **{'yes' if payload['all_declared_runtime_connections_verified'] else 'no'}**",
        "",
        "| Connection | State | Auth | Runtime evidence |",
        "| --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(f"| {row['label']} | {row['state']} | {row['auth_method']} | {row['evidence_reference'] or 'none'} |")
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps({"ok": True, "connections": len(rows), "runtime_verified": verified, "all_verified": payload["all_declared_runtime_connections_verified"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
