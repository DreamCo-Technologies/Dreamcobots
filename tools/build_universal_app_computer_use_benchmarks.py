#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CFG = json.loads((ROOT / "config" / "universal-app-computer-use-expansion.json").read_text(encoding="utf-8"))
OUT = ROOT / "config" / "generated" / "universal-app-computer-use-benchmarks.json"
GAPS = ROOT / "config" / "generated" / "universal-app-computer-use-gap-workers.json"


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def main() -> int:
    cases = []
    workers = []
    for domain, intents in CFG["domains"].items():
        for intent in intents:
            cid = f"digital-intent:{domain}:{slug(intent)}"
            cases.append({
                "case_id": cid,
                "domain": domain,
                "intent": intent,
                "dimensions": CFG["benchmark_dimensions"],
                "status": "planned_not_run",
                "required_overlays": ["happy_path", "negative", "boundary", "malformed_input", "permission", "privacy", "security", "recovery", "speed", "accuracy", "cost", "accessibility", "observability"],
            })
            workers.append({
                "worker_id": f"gap-{slug(cid)}",
                "case_id": cid,
                "parallel_roles": CFG["gap_team"],
                "required_outputs": ["baseline", "repository capability mapping", "competitor/platform comparison where applicable", "gap evidence", "build proposal", "sandbox tests", "before/after benchmark", "runtime evidence"],
                "status": "sandbox_backlog",
                "live_allowed": False,
            })
    payload = {
        "schema": "dreamco.universal_app_computer_use_benchmarks.v1",
        "domain_count": len(CFG["domains"]),
        "benchmark_case_count": len(cases),
        "cases": cases,
        "source_classes": CFG["source_classes"],
        "truth_boundary": CFG["truth_rule"],
    }
    gap_payload = {
        "schema": "dreamco.universal_app_computer_use_gap_workers.v1",
        "worker_count": len(workers),
        "workers": workers,
        "truth_boundary": "Every digital-intent benchmark receives a parallel gap-closing path; runtime success must be proven separately.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    GAPS.write_text(json.dumps(gap_payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "domains": len(CFG["domains"]), "cases": len(cases), "gap_workers": len(workers), "output": str(OUT.relative_to(ROOT))}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
