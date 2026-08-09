#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP_BOTS = ROOT / "App_bots"
GATE = ROOT / "config" / "live-revenue-gate.json"
BUSINESS = ROOT / "config" / "generated" / "bot-business-owner-curriculum.json"
SANDBOX = ROOT / "config" / "generated" / "bot-sandbox-curriculum.json"
OUT = ROOT / "config" / "generated" / "live-revenue-readiness.json"


def canonical_bots() -> list[tuple[str, str]]:
    rows = []
    for path in sorted(APP_BOTS.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        division = payload.get("division") or path.stem
        for bot in payload.get("bots", []):
            if bot.get("slug"):
                rows.append((bot["slug"], division))
    return rows


def ensure_generated(path: Path, command: list[str]) -> None:
    if path.exists():
        return
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> int:
    gate = json.loads(GATE.read_text(encoding="utf-8"))
    ensure_generated(BUSINESS, [sys.executable, "tools/build_bot_business_owner_curriculum.py"])
    ensure_generated(SANDBOX, [sys.executable, "tools/build_bot_sandbox_curriculum.py"])

    business_by = {
        b["slug"]: b
        for b in json.loads(BUSINESS.read_text(encoding="utf-8")).get("bots", [])
    }
    sandbox_by = {
        b["slug"]: b
        for b in json.loads(SANDBOX.read_text(encoding="utf-8")).get("bots", [])
    }

    rows = []
    for slug, division in canonical_bots():
        checks = {
            "canonical_bot": True,
            "business_curriculum": slug in business_by,
            "sandbox_curriculum": slug in sandbox_by,
            "runtime_capability_evidence": False,
            "applicable_universal_tests_pass": False,
            "business_simulation_pass": False,
            "stripe_test_suite_pass": False,
            "security_privacy_pass": False,
            "system_release_health_pass": False,
            "owner_live_enable": False,
        }
        technical_planning = checks["business_curriculum"] and checks["sandbox_curriculum"]
        state = "tests_in_progress" if technical_planning else "sandbox_only"
        rows.append({
            "slug": slug,
            "division": division,
            "state": state,
            "checks": checks,
            "live_checkout_allowed": False,
            "verified_live_revenue_usd": 0,
            "blockers": [k for k, v in checks.items() if not v],
        })

    payload = {
        "schema": "dreamco.live_revenue_readiness.generated.v1",
        "bot_count": len(rows),
        "live_enabled_count": 0,
        "eligible_pending_owner_count": 0,
        "bots": rows,
        "required_gates": gate["required_gates"],
        "truth_boundary": gate["truth_rule"],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "ok": True,
        "bots": len(rows),
        "live_enabled": 0,
        "output": str(OUT.relative_to(ROOT)),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
