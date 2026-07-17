#!/usr/bin/env python3
"""Run Buddy maintenance locally so GitHub Actions can stay cheap.

This runner is intentionally conservative: it executes repository report,
scan, and test commands that are safe on the owner laptop. It does not send
outreach, move money, trade, mutate credentials, deploy production, or bypass
platform billing.
"""

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONFIG_FILE = ROOT / "config" / "local_buddy_runner.json"
REPORT_FILE = ROOT / "reports" / "local_buddy_runner_report.json"
LOG_DIR = ROOT / "logs" / "local_buddy_runner"
PID_FILE = ROOT / ".local_buddy_runner.pid"
STDOUT_LOG_FILE = LOG_DIR / "local_buddy_runner.out"


COMMANDS: dict[str, list[str]] = {
    "report:24-hour-scaling": ["python3", "tools/generate_24_hour_scaling_report.py"],
    "check:24-hour-scaling": ["python3", "tools/generate_24_hour_scaling_report.py", "--check"],
    "report:buddy-codex-cheap-ops": ["python3", "tools/generate_buddy_codex_cheap_ops.py"],
    "check:buddy-codex-cheap-ops": ["python3", "tools/generate_buddy_codex_cheap_ops.py", "--check"],
    "report:buddy-24-hour-package": ["python3", "tools/generate_buddy_24_hour_client_package.py"],
    "check:buddy-24-hour-package": ["python3", "tools/generate_buddy_24_hour_client_package.py", "--check"],
    "report:ai-agent-model-library": ["python3", "tools/generate_buddy_ai_agent_model_library.py"],
    "check:ai-agent-model-library": ["python3", "tools/generate_buddy_ai_agent_model_library.py", "--check"],
    "report:google-ai-studio": ["python3", "tools/generate_google_ai_studio_frontend_factory.py"],
    "check:google-ai-studio": ["python3", "tools/generate_google_ai_studio_frontend_factory.py", "--check"],
    "report:app-foundry": ["python3", "tools/generate_app_foundry_readiness.py"],
    "check:app-foundry": ["python3", "tools/generate_app_foundry_readiness.py", "--check"],
    "report:commerce-publishing": ["python3", "tools/generate_buddy_commerce_publishing_os.py"],
    "check:commerce-publishing": ["python3", "tools/generate_buddy_commerce_publishing_os.py", "--check"],
    "report:trust-search": ["python3", "tools/generate_buddy_trust_search_os.py"],
    "check:trust-search": ["python3", "tools/generate_buddy_trust_search_os.py", "--check"],
    "report:bot-founder-store": ["python3", "tools/generate_bot_founder_app_store.py"],
    "check:bot-founder-store": ["python3", "tools/generate_bot_founder_app_store.py", "--check"],
    "report:revenue-practice": ["python3", "tools/generate_bot_autonomous_revenue_practice.py"],
    "check:revenue-practice": ["python3", "tools/generate_bot_autonomous_revenue_practice.py", "--check"],
    "report:specialized-knowledge": ["python3", "tools/generate_specialized_bot_knowledge.py"],
    "check:specialized-knowledge": ["python3", "tools/generate_specialized_bot_knowledge.py", "--check"],
    "report:bot-owner-settings": ["python3", "tools/generate_bot_owner_settings_report.py"],
    "check:bot-owner-settings": ["python3", "tools/generate_bot_owner_settings_report.py", "--check"],
    "report:storage": ["python3", "tools/storage_guard.py"],
    "report:stripe-rescue": ["python3", "tools/stripe_revenue_rescue.py"],
    "report:contract-discovery": ["python3", "tools/generate_bot_contract_discovery_report.py"],
    "check:contract-discovery": ["python3", "tools/generate_bot_contract_discovery_report.py", "--check"],
    "report:people-job-qualification": ["python3", "tools/generate_people_job_qualification_report.py"],
    "check:people-job-qualification": ["python3", "tools/generate_people_job_qualification_report.py", "--check"],
    "scan:local-imports": ["python3", "tools/local_import_audit.py"],
    "check:buddy-bot-connections": ["python3", "tools/buddy_bot_connection_guard.py"],
    "github-cost-saver": ["python3", "tools/run_github_cost_saver.py"],
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path, fallback: Any) -> Any:
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def load_config() -> dict[str, Any]:
    return read_json(CONFIG_FILE, {})


def run_command(name: str, timeout: int, dry_run: bool) -> dict[str, Any]:
    command = COMMANDS.get(name)
    started = time.monotonic()
    record: dict[str, Any] = {
        "name": name,
        "command": command,
        "started_at": utc_now(),
        "timeout_seconds": timeout,
        "dry_run": dry_run,
    }
    if command is None:
        record.update({"status": "skipped", "error": "unknown command"})
        return record
    if dry_run:
        record.update({"status": "planned", "returncode": None, "duration_seconds": 0})
        return record

    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
            env={**os.environ, "PYTHONPYCACHEPREFIX": "/private/tmp/dreamco-pycache"},
        )
        output = completed.stdout[-8000:]
        record.update(
            {
                "status": "pass" if completed.returncode == 0 else "fail",
                "returncode": completed.returncode,
                "duration_seconds": round(time.monotonic() - started, 2),
                "output_tail": output,
            }
        )
    except subprocess.TimeoutExpired as exc:
        record.update(
            {
                "status": "timeout",
                "returncode": None,
                "duration_seconds": round(time.monotonic() - started, 2),
                "output_tail": (exc.stdout or "")[-8000:] if isinstance(exc.stdout, str) else "",
            }
        )
    return record


def run_profile(profile: str, dry_run: bool = False, max_command_seconds: int | None = None) -> dict[str, Any]:
    config = load_config()
    profile_config = config.get("profiles", {}).get(profile)
    if not profile_config:
        raise SystemExit(f"Unknown local Buddy profile: {profile}")

    timeout = int(max_command_seconds or profile_config.get("max_command_seconds") or 120)
    commands = list(profile_config.get("commands", []))
    results = [run_command(name, timeout, dry_run) for name in commands]
    summary = {
        "commands": len(results),
        "passed": sum(1 for item in results if item["status"] == "pass"),
        "failed": sum(1 for item in results if item["status"] == "fail"),
        "timed_out": sum(1 for item in results if item["status"] == "timeout"),
        "skipped": sum(1 for item in results if item["status"] == "skipped"),
        "planned": sum(1 for item in results if item["status"] == "planned"),
    }
    return {
        "schema": "dreamco.local_buddy_runner_report.v1",
        "generated_at": utc_now(),
        "profile": profile,
        "description": profile_config.get("description", ""),
        "dry_run": dry_run,
        "summary": summary,
        "cost_policy": config.get("cost_policy", {}),
        "hard_limits": config.get("hard_limits", []),
        "results": results,
    }


def write_report(report: dict[str, Any]) -> None:
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    (LOG_DIR / f"{stamp}-{report['profile']}.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def process_is_running(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def read_pid() -> int | None:
    if not PID_FILE.exists():
        return None
    try:
        return int(PID_FILE.read_text(encoding="utf-8").strip())
    except ValueError:
        return None


def runner_status() -> dict[str, Any]:
    pid = read_pid()
    running = bool(pid and process_is_running(pid))
    report = read_json(REPORT_FILE, {})
    return {
        "schema": "dreamco.local_buddy_runner_status.v1",
        "checked_at": utc_now(),
        "running": running,
        "pid": pid if running else None,
        "pid_file": str(PID_FILE.relative_to(ROOT)),
        "stdout_log": str(STDOUT_LOG_FILE.relative_to(ROOT)),
        "latest_report": str(REPORT_FILE.relative_to(ROOT)) if REPORT_FILE.exists() else None,
        "latest_profile": report.get("profile"),
        "latest_generated_at": report.get("generated_at"),
        "latest_summary": report.get("summary", {}),
    }


def start_daemon(profile: str, sleep_minutes: float, max_command_seconds: int | None) -> dict[str, Any]:
    existing_pid = read_pid()
    if existing_pid and process_is_running(existing_pid):
        return {
            **runner_status(),
            "started": False,
            "message": "Local Buddy runner is already running.",
        }

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        str(Path(__file__).relative_to(ROOT)),
        "--profile",
        profile,
        "--forever",
        "--sleep-minutes",
        str(sleep_minutes),
    ]
    if max_command_seconds:
        command.extend(["--max-command-seconds", str(max_command_seconds)])

    stdout_handle = STDOUT_LOG_FILE.open("a", encoding="utf-8")
    stdout_handle.write(f"\n[{utc_now()}] starting {' '.join(command)}\n")
    stdout_handle.flush()
    process = subprocess.Popen(
        command,
        cwd=ROOT,
        stdout=stdout_handle,
        stderr=subprocess.STDOUT,
        start_new_session=True,
        env={**os.environ, "PYTHONPYCACHEPREFIX": "/private/tmp/dreamco-pycache"},
    )
    PID_FILE.write_text(str(process.pid), encoding="utf-8")
    return {
        **runner_status(),
        "started": True,
        "profile": profile,
        "sleep_minutes": sleep_minutes,
        "message": "Local Buddy runner started.",
    }


def stop_daemon() -> dict[str, Any]:
    pid = read_pid()
    if not pid or not process_is_running(pid):
        if PID_FILE.exists():
            PID_FILE.unlink()
        return {
            **runner_status(),
            "stopped": False,
            "message": "Local Buddy runner was not running.",
        }

    os.kill(pid, signal.SIGTERM)
    for _ in range(20):
        if not process_is_running(pid):
            break
        time.sleep(0.25)
    if process_is_running(pid):
        os.kill(pid, signal.SIGKILL)
    if PID_FILE.exists():
        PID_FILE.unlink()
    return {
        **runner_status(),
        "stopped": True,
        "message": "Local Buddy runner stopped.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Buddy locally instead of spending GitHub Actions minutes.")
    parser.add_argument("--profile", choices=["cheap", "aggressive"], default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--forever", action="store_true", help="Repeat until stopped with --stop or Ctrl+C.")
    parser.add_argument("--daemon-start", action="store_true", help="Start a background local runner and return immediately.")
    parser.add_argument("--stop", action="store_true", help="Stop the background local runner.")
    parser.add_argument("--status", action="store_true", help="Show background local runner status.")
    parser.add_argument("--loop-hours", type=float, default=0, help="Repeat the profile for this many hours.")
    parser.add_argument("--sleep-minutes", type=float, default=60, help="Delay between loop cycles.")
    parser.add_argument("--max-command-seconds", type=int, default=None)
    args = parser.parse_args()

    config = load_config()
    profile = args.profile or config.get("default_profile", "cheap")

    if args.status:
        print(json.dumps(runner_status(), indent=2, sort_keys=True))
        return 0
    if args.stop:
        print(json.dumps(stop_daemon(), indent=2, sort_keys=True))
        return 0
    if args.daemon_start:
        print(json.dumps(start_daemon(profile, args.sleep_minutes, args.max_command_seconds), indent=2, sort_keys=True))
        return 0

    started = time.monotonic()
    deadline = started + max(args.loop_hours, 0) * 3600
    cycles = []

    while True:
        report = run_profile(profile, dry_run=args.dry_run, max_command_seconds=args.max_command_seconds)
        write_report(report)
        cycles.append(report["summary"])
        print(
            "local_buddy profile={profile} commands={commands} passed={passed} failed={failed} timed_out={timed_out} report={report}".format(
                profile=profile,
                commands=report["summary"]["commands"],
                passed=report["summary"]["passed"],
                failed=report["summary"]["failed"],
                timed_out=report["summary"]["timed_out"],
                report=REPORT_FILE.relative_to(ROOT),
            )
        )
        if not args.forever and (args.loop_hours <= 0 or time.monotonic() >= deadline):
            break
        try:
            time.sleep(max(args.sleep_minutes, 1) * 60)
        except KeyboardInterrupt:
            break

    return 0 if all(cycle["failed"] == 0 and cycle["timed_out"] == 0 for cycle in cycles) else 1


if __name__ == "__main__":
    raise SystemExit(main())
