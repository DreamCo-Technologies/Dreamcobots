#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CFG = json.loads((ROOT / "config" / "buddy-211-government-service-navigator.json").read_text(encoding="utf-8"))
OUT = ROOT / "config" / "generated" / "buddy-211-government-service-benchmarks.json"
GAPS = ROOT / "config" / "generated" / "buddy-211-government-service-gap-workers.json"


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def main() -> int:
    cases = []
    workers = []
    journey = CFG["user_journey"]
    for domain in CFG["service_domains"]:
        for step in journey:
            cid = f"buddy211:{slug(domain)}:{slug(step)}"
            cases.append({
                "case_id": cid,
                "domain": domain,
                "step": step,
                "dimensions": CFG["benchmark_dimensions"],
                "status": "planned_not_run",
                "required_truth": ["current authoritative source", "correct jurisdiction", "published rule provenance", "human authority boundary"],
                "productivity_metrics": ["resident_minutes_saved", "staff_minutes_saved", "human_review_minutes", "rework_rate", "completion_rate", "error_rate"],
            })
            workers.append({
                "worker_id": f"gap-{slug(cid)}",
                "case_id": cid,
                "parallel_roles": [
                    "government-service researcher", "jurisdiction resolver", "qualification parser", "public-service UX bot",
                    "form/document QA bot", "accessibility/language bot", "privacy/security bot", "sandbox QA bot",
                    "government productivity analyst", "builder bot", "release reviewer"
                ],
                "required_outputs": [
                    "authoritative source evidence", "baseline user/staff workflow", "baseline time/error rate", "sandbox fixture",
                    "gap classification", "build/fix proposal", "before/after correctness", "before/after time saved", "human-review boundary", "runtime evidence"
                ],
                "live_allowed": False,
            })

    payload = {
        "schema": "dreamco.buddy_211_government_service_benchmarks.v1",
        "service_domain_count": len(CFG["service_domains"]),
        "journey_step_count": len(journey),
        "benchmark_case_count": len(cases),
        "cases": cases,
        "application_assistance_levels": CFG["application_assistance_levels"],
        "never_autonomous": CFG["never_autonomous"],
        "public_sector_goal": CFG["public_sector_goal"],
        "truth_boundary": CFG["truth_rule"],
    }
    gap_payload = {
        "schema": "dreamco.buddy_211_government_service_gap_workers.v1",
        "worker_count": len(workers),
        "workers": workers,
        "truth_boundary": "Every Buddy 211 benchmark case has a parallel gap-closing path; a worker assignment is not proof that the capability passes.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    GAPS.write_text(json.dumps(gap_payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "domains": payload["service_domain_count"], "cases": len(cases), "gap_workers": len(workers), "output": str(OUT.relative_to(ROOT))}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
