#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WATCH = ROOT / "config" / "generated" / "government-needs-spending-watch.json"
CFG = json.loads((ROOT / "config" / "buddy-government-operating-system.json").read_text(encoding="utf-8"))
OUT = ROOT / "config" / "generated" / "government-signal-gap-backlog.json"


def stable(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def main() -> int:
    watch = json.loads(WATCH.read_text(encoding="utf-8")) if WATCH.exists() else {"signals": [], "generated_at": None}
    rows = []
    for signal in watch.get("signals", []):
        identity = "|".join(str(signal.get(key, "")) for key in ["signal_type", "agency", "department", "title", "number", "solicitation_number", "fiscal_year"])
        rows.append({
            "gap_id": f"government-signal:{stable(identity)}",
            "signal": signal,
            "status": "needs_analysis",
            "parallel_roles": CFG["gap_team"],
            "required_analysis": [
                "verify current authoritative source",
                "identify actual government need or spending context",
                "separate active opportunity from historical spending",
                "map applicable government department/program/job/service",
                "map DreamCo and user capabilities",
                "identify capability gaps",
                "identify contract grant subcontract partnership or public-service route where applicable",
                "build requirements/compliance matrix where applicable",
                "estimate delivery effort cost and human oversight",
                "build sandbox prototype or benchmark fixture",
                "security privacy accessibility and legal/compliance review",
                "measure public value and business value",
                "retest before any live action"
            ],
            "live_action_allowed": False,
            "closure_rule": "Close only when the signal is verified, dispositioned, and any proposed solution has evidence or is explicitly rejected with reason."
        })
    payload = {
        "schema": "dreamco.government_signal_gap_backlog.v1",
        "source_generated_at": watch.get("generated_at"),
        "signal_count": len(watch.get("signals", [])),
        "gap_count": len(rows),
        "gaps": rows,
        "truth_boundary": "A government spending or opportunity signal starts analysis; it does not prove a need, a procurement path, eligibility, or a revenue outcome."
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "signals": payload["signal_count"], "gaps": len(rows), "output": str(OUT.relative_to(ROOT))}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
