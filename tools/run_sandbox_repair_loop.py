#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "config" / "sandbox-repair-loop.json"
E2E = ROOT / "website" / "data" / "bot-fleet-e2e.json"
SHARDS = ROOT / "website" / "data" / "bot-capability-tests"
OUT = ROOT / "config" / "generated" / "sandbox-repair-loop-report.json"
REPORT = ROOT / "reports" / "SANDBOX_REPAIR_LOOP.md"


def load(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def success(summary: dict) -> bool:
    return (
        summary.get("profilesTested") == 1051
        and summary.get("failed") == 0
        and summary.get("allDeclaredCapabilitiesTested") is True
        and summary.get("sandboxCapabilityTestsFailed") == 0
        and summary.get("sandboxCapabilityTestsPassed") == summary.get("declaredCapabilitiesTested")
        and summary.get("repositoryControlledFlowComplete") is True
    )


def extract_failures() -> list[dict]:
    failures: list[dict] = []
    if not SHARDS.exists():
        return failures
    for path in sorted(SHARDS.glob("*.json")):
        data = load(path, {})
        division = data.get("division") or path.stem
        for profile in data.get("profiles", []):
            for row in profile.get("capabilityTests", []):
                if row.get("status") != "failed":
                    continue
                failures.append({
                    "division": division,
                    "bot_slug": profile.get("slug"),
                    "capability": row.get("capability"),
                    "test_id": row.get("testId"),
                    "failures": row.get("failures", []),
                    "evidence_file": str(path.relative_to(ROOT)),
                })
    return failures


def run(command: list[str], *, allow_failure: bool = False) -> dict:
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    result = {
        "command": command,
        "returncode": completed.returncode,
        "stdout_tail": completed.stdout[-4000:],
        "stderr_tail": completed.stderr[-4000:],
    }
    if completed.returncode and not allow_failure:
        raise RuntimeError(f"Command failed ({completed.returncode}): {' '.join(command)}\n{completed.stderr[-2000:]}")
    return result


def refresh_evidence(round_log: list[dict]) -> dict:
    round_log.append(run(["npx", "tsx", "tools/generate_bot_fleet_catalog.ts"]))
    # E2E intentionally may return non-zero while exposing exact capability failures.
    round_log.append(run(["node", "--import", "tsx", "tools/run_bot_fleet_e2e.ts"], allow_failure=True))
    round_log.append(run(["python3", "tools/build_bot_sandbox_curriculum.py"]))
    round_log.append(run(["python3", "tools/run_all_bot_sandbox_campaign.py"]))
    return load(E2E, {}).get("summary", {})


def attempt_bounded_repairs(round_log: list[dict]) -> None:
    # Known deterministic compatibility migration only; arbitrary semantic edits are forbidden here.
    round_log.append(run(["python3", "tools/migrate_zod4_compat.py"], allow_failure=True))
    round_log.append(run(["npm", "run", "check"], allow_failure=True))
    round_log.append(run(["npx", "tsx", "tools/generate_bot_fleet_catalog.ts"], allow_failure=True))
    round_log.append(run(["npx", "tsx", "tools/generate_buddy_fleet_quality_program.ts"], allow_failure=True))


def write_report(payload: dict) -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    unresolved = payload.get("unresolved_failures", [])
    lines = [
        "# Sandbox Repair Loop",
        "",
        f"- Status: **{payload['status']}**",
        f"- Rounds executed: **{payload['rounds_executed']}**",
        f"- Starting failed capabilities: **{payload['starting_failed_capabilities']}**",
        f"- Ending failed capabilities: **{payload['ending_failed_capabilities']}**",
        f"- All declared capability contracts passing: **{payload['all_capabilities_complete']}**",
        "",
        "## Rule",
        "",
        "Test → isolate failure → bounded repair → focused evidence refresh → bot/fleet retest. Unknown or unsafe gaps stay red; tests are never weakened to manufacture a pass.",
        "",
    ]
    if unresolved:
        lines.extend(["## Unresolved capability queue", ""])
        for row in unresolved[:100]:
            lines.append(f"- `{row.get('bot_slug')}` → **{row.get('capability')}**: {', '.join(row.get('failures') or ['failure evidence recorded'])}")
        if len(unresolved) > 100:
            lines.append(f"- …and {len(unresolved) - 100} more in the JSON evidence artifact.")
    REPORT.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-rounds", type=int)
    args = parser.parse_args()
    policy = load(POLICY, {})
    max_rounds = args.max_rounds or int(policy.get("max_rounds_per_run", 8))
    max_rounds = max(1, min(max_rounds, 12))
    no_progress_limit = int(policy.get("stop_after_no_progress_rounds", 2))

    rounds: list[dict] = []
    starting_failures: int | None = None
    best_failures: int | None = None
    no_progress = 0
    final_summary: dict = {}
    unresolved: list[dict] = []

    for round_number in range(1, max_rounds + 1):
        command_log: list[dict] = []
        summary = refresh_evidence(command_log)
        failures = extract_failures()
        failed_count = len(failures)
        if starting_failures is None:
            starting_failures = failed_count
        rounds.append({
            "round": round_number,
            "phase": "test",
            "summary": summary,
            "failed_capabilities": failed_count,
            "commands": command_log,
        })
        final_summary = summary
        unresolved = failures

        if success(summary):
            payload = {
                "schema": "dreamco.sandbox_repair_loop_report.v1",
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "status": "all_declared_capability_contracts_passing",
                "rounds_executed": round_number,
                "starting_failed_capabilities": starting_failures or 0,
                "ending_failed_capabilities": 0,
                "all_capabilities_complete": True,
                "final_summary": summary,
                "rounds": rounds,
                "unresolved_failures": [],
                "truth_boundary": "Complete means the repository-controlled declared capability contract passed for the tested revision. Deeper live/provider/domain benchmarks remain separately scoped."
            }
            write_report(payload)
            print(json.dumps({"ok": True, "rounds": round_number, "failed_capabilities": 0}, indent=2))
            return 0

        if best_failures is None or failed_count < best_failures:
            best_failures = failed_count
            no_progress = 0
        else:
            no_progress += 1
        if no_progress >= no_progress_limit:
            break

        repair_log: list[dict] = []
        attempt_bounded_repairs(repair_log)
        rounds.append({
            "round": round_number,
            "phase": "repair",
            "failed_capabilities_before_repair": failed_count,
            "repair_scope": "known deterministic shared repairs only",
            "commands": repair_log,
        })

    final_failures = len(unresolved)
    payload = {
        "schema": "dreamco.sandbox_repair_loop_report.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "blocked_unresolved_capability_gaps",
        "rounds_executed": len([row for row in rounds if row.get("phase") == "test"]),
        "starting_failed_capabilities": starting_failures or 0,
        "ending_failed_capabilities": final_failures,
        "all_capabilities_complete": False,
        "final_summary": final_summary,
        "rounds": rounds,
        "unresolved_failures": unresolved,
        "next_action": "Keep unresolved gaps assigned to task-scoped workers; add a test-backed candidate repair, then rerun this loop. Do not weaken the failing acceptance contract.",
        "truth_boundary": "The loop stops red instead of spinning when bounded automatic repair cannot safely reduce the failing capability count."
    }
    write_report(payload)
    print(json.dumps({"ok": False, "failed_capabilities": final_failures, "status": payload["status"]}, indent=2))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
