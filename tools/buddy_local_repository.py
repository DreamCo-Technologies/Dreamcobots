#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "config" / "offline-buddy-repository-engine.json"
LOCAL = ROOT / ".buddy-local"


def run(command: list[str], log_name: str, allow_failure: bool = False) -> int:
    logs = LOCAL / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    path = logs / log_name
    started = datetime.now(timezone.utc).isoformat()
    with path.open("w", encoding="utf-8") as handle:
        handle.write(f"started={started}\ncommand={json.dumps(command)}\n\n")
        proc = subprocess.run(command, cwd=ROOT, stdout=handle, stderr=subprocess.STDOUT, text=True)
        handle.write(f"\nexit_code={proc.returncode}\n")
    if proc.returncode and not allow_failure:
        print(f"FAILED: {' '.join(command)} — see {path.relative_to(ROOT)}", file=sys.stderr)
    return proc.returncode


def init_dirs() -> None:
    cfg = json.loads(CFG.read_text(encoding="utf-8"))
    for rel in cfg["offline_directories"].values():
        (ROOT / rel).mkdir(parents=True, exist_ok=True)


def status() -> dict:
    init_dirs()
    git = shutil.which("git") is not None
    node = shutil.which("node") is not None
    npm = shutil.which("npm") is not None
    python = shutil.which("python3") is not None or shutil.which("python") is not None
    result = {
        "schema": "dreamco.local_repository_status.v1",
        "root": str(ROOT),
        "offline_ready": python,
        "tools": {"git": git, "node": node, "npm": npm, "python": python},
        "github_required_for_core": False,
        "network_required_for_core": False,
        "time": datetime.now(timezone.utc).isoformat(),
    }
    if git:
        proc = subprocess.run(["git", "status", "--short"], cwd=ROOT, capture_output=True, text=True)
        result["git_changes"] = [line for line in proc.stdout.splitlines() if line.strip()]
    return result


def local_check() -> int:
    init_dirs()
    commands = [
        ([sys.executable, "tools/audit_actions_health.py"], "actions-health.log"),
        ([sys.executable, "tools/build_full_potential_sandbox_catalog.py"], "full-potential-sandbox.log"),
        ([sys.executable, "tools/build_bot_sandbox_curriculum.py"], "bot-sandbox-curriculum.log"),
        ([sys.executable, "tools/build_council_bot_career_paths.py"], "career-paths.log"),
        ([sys.executable, "tools/audit_bot_division_placement.py"], "division-placement.log"),
        ([sys.executable, "tools/dreamco_generator_factory.py", "registry"], "generator-registry.log"),
    ]
    failed = []
    for command, log_name in commands:
        code = run(command, log_name, allow_failure=True)
        if code:
            failed.append({"command": command, "exit_code": code, "log": f".buddy-local/logs/{log_name}"})
    if shutil.which("node") and (ROOT / "node_modules").exists():
        code = run(["node", "--import", "tsx", "--test", "tests/buddy-resource-sandbox.test.ts"], "resource-sandbox-test.log", allow_failure=True)
        if code:
            failed.append({"command": ["node", "--import", "tsx", "--test", "tests/buddy-resource-sandbox.test.ts"], "exit_code": code, "log": ".buddy-local/logs/resource-sandbox-test.log"})
    report = {
        "ok": not failed,
        "failed": failed,
        "note": "Node-based checks are skipped when node_modules is unavailable; run install when dependencies are available.",
    }
    (LOCAL / "state" / "last-check.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if not failed else 1


def diagnose() -> int:
    init_dirs()
    state = LOCAL / "state" / "last-check.json"
    if not state.exists():
        local_check()
    data = json.loads(state.read_text(encoding="utf-8"))
    issues = []
    for failure in data.get("failed", []):
        issues.append({
            "type": "local_check_failure",
            "command": failure.get("command"),
            "log": failure.get("log"),
            "repair_status": "needs_root_cause_review",
        })
    output = {"ok": not issues, "issues": issues, "repair_rule": "Fix the first root cause and rerun the smallest failing command before broader checks."}
    (LOCAL / "state" / "diagnosis.json").write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2))
    return 0


def repair_plan() -> int:
    diagnose_path = LOCAL / "state" / "diagnosis.json"
    if not diagnose_path.exists():
        diagnose()
    diagnosis = json.loads(diagnose_path.read_text(encoding="utf-8"))
    plan = {
        "schema": "dreamco.local_repair_plan.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "issues": [],
        "automatic_repairs_applied": [],
        "review_required": [],
    }
    # Safe deterministic repair: required evidence directories.
    init_dirs()
    plan["automatic_repairs_applied"].append("ensured .buddy-local evidence/work/release/sync directories exist")
    for issue in diagnosis.get("issues", []):
        plan["issues"].append({
            **issue,
            "steps": ["open referenced log", "identify first meaningful error", "locate canonical owner", "prepare smallest repair", "add regression test if defect", "rerun focused command"],
        })
        plan["review_required"].append(issue.get("command"))
    path = LOCAL / "issues" / f"repair-plan-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    path.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "plan": str(path.relative_to(ROOT)), "review_required": len(plan["review_required"])}, indent=2))
    return 0


def package_release(name: str) -> int:
    init_dirs()
    release_dir = LOCAL / "releases" / name
    release_dir.mkdir(parents=True, exist_ok=True)
    files = [
        "config/generated/dreamco-generator-registry.json",
        "config/generated/full-potential-sandbox-catalog.json",
        "config/generated/bot-sandbox-curriculum.json",
        "config/generated/council-bot-career-paths.json",
        "reports/ACTIONS_HEALTH_REPORT.md",
        "reports/BOT_DIVISION_PLACEMENT_AUDIT.md",
    ]
    manifest = []
    for rel in files:
        src = ROOT / rel
        if not src.exists():
            continue
        dst = release_dir / rel.replace("/", "__")
        shutil.copy2(src, dst)
        digest = hashlib.sha256(dst.read_bytes()).hexdigest()
        manifest.append({"source": rel, "file": dst.name, "sha256": digest, "bytes": dst.stat().st_size})
    (release_dir / "manifest.json").write_text(json.dumps({"name": name, "generated_at": datetime.now(timezone.utc).isoformat(), "files": manifest}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "release": str(release_dir.relative_to(ROOT)), "files": len(manifest)}, indent=2))
    return 0


def queue_sync(note: str) -> int:
    init_dirs()
    path = LOCAL / "sync-queue" / f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    path.write_text(json.dumps({"created_at": datetime.now(timezone.utc).isoformat(), "note": note, "status": "queued_offline", "requires_network_and_permission": True}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "queued": str(path.relative_to(ROOT))}, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Offline-first Buddy repository control engine")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init")
    sub.add_parser("status")
    sub.add_parser("check")
    sub.add_parser("diagnose")
    sub.add_parser("repair-plan")
    release = sub.add_parser("release-bundle")
    release.add_argument("name")
    sync = sub.add_parser("queue-sync")
    sync.add_argument("note")
    args = parser.parse_args()

    if args.command == "init":
        init_dirs(); print(json.dumps({"ok": True, "root": str(ROOT), "local": str(LOCAL.relative_to(ROOT))}, indent=2)); return 0
    if args.command == "status":
        print(json.dumps(status(), indent=2)); return 0
    if args.command == "check": return local_check()
    if args.command == "diagnose": return diagnose()
    if args.command == "repair-plan": return repair_plan()
    if args.command == "release-bundle": return package_release(args.name)
    if args.command == "queue-sync": return queue_sync(args.note)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
