#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CURRICULUM = ROOT / "config" / "generated" / "bot-sandbox-curriculum.json"
PROGRAM = ROOT / "config" / "bot-universal-sandbox-skill-gap-program.json"
FLEET_E2E = ROOT / "website" / "data" / "bot-fleet-e2e.json"
CAPABILITY_SHARDS = ROOT / "website" / "data" / "bot-capability-tests"
OUT = ROOT / "config" / "generated" / "all-bot-sandbox-campaign.json"
REPORT = ROOT / "reports" / "ALL_BOT_SANDBOX_CAMPAIGN.md"

EVIDENCE_SOURCES = [
    ROOT / "config" / "generated" / "bots.catalog.json",
    ROOT / "config" / "generated" / "buddy_fleet_quality_program.json",
    ROOT / "config" / "generated" / "bot-division-placement-audit.json",
    ROOT / "config" / "generated" / "bot-accounting-placement-audit.json",
    ROOT / "config" / "generated" / "model-mastery-gap-report.json",
    FLEET_E2E,
]


def load(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def stable_id(*parts: str) -> str:
    return hashlib.sha256(":".join(parts).encode()).hexdigest()[:20]


def normalize(value: str) -> str:
    return " ".join(str(value).strip().lower().split())


def e2e_capability_index() -> dict[tuple[str, str], dict]:
    index: dict[tuple[str, str], dict] = {}
    if not CAPABILITY_SHARDS.exists():
        return index
    for path in sorted(CAPABILITY_SHARDS.glob("*.json")):
        payload = load(path, {})
        for profile in payload.get("profiles", []):
            slug = str(profile.get("slug", "")).strip()
            if not slug:
                continue
            for row in profile.get("capabilityTests", []):
                capability = str(row.get("capability", "")).strip()
                if capability:
                    index[(slug, normalize(capability))] = {
                        **row,
                        "evidence_file": str(path.relative_to(ROOT)),
                    }
    return index


def evidence_index() -> dict:
    index = {}
    for path in EVIDENCE_SOURCES:
        if path.exists():
            index[str(path.relative_to(ROOT))] = load(path, {})
    index["e2e_capabilities"] = e2e_capability_index()
    return index


def capability_state(bot: dict, capability: str, evidence: dict) -> tuple[str, list[str]]:
    proofs: list[str] = []
    e2e = evidence.get("e2e_capabilities", {})
    e2e_row = e2e.get((bot["slug"], normalize(capability)))
    if e2e_row:
        proofs.append(f"{e2e_row['evidence_file']}#{e2e_row.get('testId')}")
        if e2e_row.get("status") == "sandbox_contract_passed":
            return "passing", proofs
        proofs.extend(str(item) for item in (e2e_row.get("failures") or []))
        return "gap_found", proofs

    fleet_quality = evidence.get("config/generated/buddy_fleet_quality_program.json", {})
    for row in fleet_quality.get("bots", []):
        if row.get("bot_id") != bot["slug"]:
            continue
        for cap in row.get("benchmark_plan", {}).get("capabilities", []):
            if normalize(cap.get("name", "")) == normalize(capability):
                status = cap.get("repository_contract_status")
                if status == "passed":
                    proofs.append(cap.get("repository_evidence") or "fleet-quality repository contract")
                    return "passing", proofs
                proofs.append(f"fleet-quality status={status}")
                return "gap_found", proofs
    return "fixture_ready", proofs


def main() -> int:
    curriculum = load(CURRICULUM, {})
    program = load(PROGRAM, {})
    evidence = evidence_index()
    if curriculum.get("bot_count") != 1051:
        raise SystemExit(f"Expected 1051 canonical bots in sandbox curriculum, found {curriculum.get('bot_count')}")

    bots_out = []
    gaps = []
    passing = fixture_ready = 0
    for bot in curriculum.get("bots", []):
        capability_rows = []
        for cap in bot.get("capability_tests", []):
            capability = cap["capability"]
            state, proofs = capability_state(bot, capability, evidence)
            if state == "passing":
                passing += 1
            else:
                fixture_ready += 1
            gap_id = None
            if state != "passing":
                gap_id = f"gap-{stable_id(bot['slug'], capability)}"
                gaps.append({
                    "gap_id": gap_id,
                    "bot_slug": bot["slug"],
                    "division": bot["division"],
                    "capability_or_metric": capability,
                    "baseline": state,
                    "target": "passing sandbox fixture with regression evidence",
                    "competitor_or_reference": "DreamCo canonical capability contract and applicable task-specific benchmark",
                    "evidence": proofs,
                    "root_cause_hypothesis": "Executable task-specific evidence is missing, failed, or incomplete.",
                    "candidate_improvements": ["run focused failed capability fixture", "repair shared runtime if reused across bots", "add tool/model route fixture when applicable"],
                    "shared_infrastructure_candidate": True,
                    "owner": bot["division"],
                    "priority": "high" if state == "gap_found" else "normal",
                    "effort": "unknown_until_fixture",
                    "risk": "sandbox_only",
                    "test_to_close_gap": f"sandbox::{bot['slug']}::{capability}",
                    "status": "active_gap_worker_assigned",
                    "worker": {
                        "type": "task_scoped_benchmark_worker",
                        "execution_mode": "sandbox",
                        "live_external_actions": False,
                        "paid_model_calls": False,
                        "single_writer_owner": bot["division"],
                        "repair_retest_cycle": ["repair candidate", "focused capability retest", "bot retest", "fleet retest"],
                    },
                })
            capability_rows.append({
                "capability": capability,
                "state": state,
                "dimensions": cap.get("dimensions", []),
                "evidence": proofs,
                "gap_id": gap_id,
            })

        bot_state = "passing" if capability_rows and all(row["state"] == "passing" for row in capability_rows) else "running_gap_campaign"
        bots_out.append({
            "slug": bot["slug"],
            "display_name": bot.get("display_name"),
            "division": bot["division"],
            "category": bot.get("category"),
            "sandbox_state": bot_state,
            "execution_mode": "sandbox",
            "live_external_actions": False,
            "declared_capability_count": bot.get("declared_capability_count", 0),
            "capabilities": capability_rows,
            "active_gap_count": sum(row["state"] != "passing" for row in capability_rows),
        })

    max_parallel = int(program["builder_handoff"]["maximum_parallel_lanes"])
    e2e_summary = evidence.get("website/data/bot-fleet-e2e.json", {}).get("summary", {})
    sandbox_contract_complete = (
        e2e_summary.get("profilesTested") == 1051
        and e2e_summary.get("failed") == 0
        and e2e_summary.get("allDeclaredCapabilitiesTested") is True
        and e2e_summary.get("sandboxCapabilityTestsFailed") == 0
        and passing == curriculum.get("declared_capability_count")
        and not gaps
    )
    payload = {
        "schema": "dreamco.all_bot_sandbox_campaign.v2",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "execution_mode": "sandbox",
        "canonical_bot_count": len(bots_out),
        "all_bots_have_active_sandbox_record": len(bots_out) == 1051,
        "declared_capability_count": sum(bot["declared_capability_count"] for bot in bots_out),
        "passing_capability_count": passing,
        "fixture_ready_or_gap_capability_count": fixture_ready,
        "active_gap_count": len(gaps),
        "maximum_parallel_gap_workers": max_parallel,
        "sandbox_contract_complete": sandbox_contract_complete,
        "e2e_fleet_summary": e2e_summary,
        "live_external_actions_executed": 0,
        "paid_model_calls_executed": 0,
        "shared_fix_first": True,
        "bots": bots_out,
        "gaps": gaps,
        "truth_boundary": "Repository-controlled fleet E2E is the primary per-capability sandbox evidence. Missing or failed executable evidence becomes an active gap; passing is never inferred from generation alone."
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# All Bot Sandbox Campaign\n\n"
        f"- Canonical bots in sandbox: **{payload['canonical_bot_count']}**\n"
        f"- Declared capabilities: **{payload['declared_capability_count']}**\n"
        f"- Passing capability contracts: **{payload['passing_capability_count']}**\n"
        f"- Active capability gaps/fixture work: **{payload['active_gap_count']}**\n"
        f"- Sandbox contract complete: **{payload['sandbox_contract_complete']}**\n"
        f"- Maximum parallel gap workers: **{payload['maximum_parallel_gap_workers']}**\n"
        f"- Live external actions: **{payload['live_external_actions_executed']}**\n"
        f"- Paid model calls: **{payload['paid_model_calls_executed']}**\n\n"
        "Failed capabilities stay assigned to repair/retest workers until executable evidence passes.\n",
        encoding="utf-8",
    )
    print(json.dumps({k: payload[k] for k in ["canonical_bot_count","declared_capability_count","passing_capability_count","active_gap_count","sandbox_contract_complete","maximum_parallel_gap_workers"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
