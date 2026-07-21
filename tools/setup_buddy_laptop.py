#!/usr/bin/env python3
"""Prepare Buddy for local laptop use without requiring paid cloud services."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONFIG_FILE = ROOT / "config" / "buddy_laptop_install.json"
SAFETY_FILE = ROOT / "config" / "buddy_laptop_safety.json"
REPORT_FILE = ROOT / "reports" / "buddy_laptop_install_report.json"
README_FILE = ROOT / "docs" / "BUDDY_LAPTOP_SETUP.md"
SAFETY_README_FILE = ROOT / "docs" / "BUDDY_LAPTOP_SAFETY.md"
BUNDLED_NODE = Path("/Users/mamas/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node")
BUNDLED_PNPM = Path("/Users/mamas/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/fallback/pnpm")
BUNDLED_NODE_PATH = str(BUNDLED_NODE.parent)
BUNDLED_DASHBOARD_COMMAND = f"PATH={BUNDLED_NODE_PATH}:$PATH {BUNDLED_PNPM} run dev"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run(command: list[str], timeout: int = 60) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
            env={**os.environ, "PYTHONPYCACHEPREFIX": "/private/tmp/dreamco-laptop-pycache"},
        )
        return {
            "command": command,
            "ok": completed.returncode == 0,
            "returncode": completed.returncode,
            "output_tail": completed.stdout[-4000:],
        }
    except Exception as exc:  # pragma: no cover - defensive local installer report
        return {"command": command, "ok": False, "error": str(exc)}


def build_config() -> dict[str, Any]:
    return {
        "schema": "dreamco.buddy_laptop_install.v1",
        "generated_at": utc_now(),
        "mission": "Run Buddy on this laptop as the local-first command center for DreamCo bots, code, tests, dashboards, and safe task preparation.",
        "repo": str(ROOT),
        "branch": "codex/recover-buddy-after-import",
        "start_commands": {
            "one_safe_sweep": "python3 tools/local_buddy_runner.py --profile cheap",
            "aggressive_sweep": "python3 tools/local_buddy_runner.py --profile aggressive",
            "background_start": "python3 tools/local_buddy_runner.py --profile aggressive --daemon-start --sleep-minutes 60",
            "status": "python3 tools/local_buddy_runner.py --status",
            "stop": "python3 tools/local_buddy_runner.py --stop",
            "dashboard": BUNDLED_DASHBOARD_COMMAND,
        },
        "safe_local_capabilities": [
            "scan and summarize the whole repository",
            "coordinate all registered bots through Buddy",
            "run generated bot smoke tests",
            "run local TypeScript/build/Python/JSON checks",
            "generate readiness, capability, source-fusion, cost, storage, and revenue-practice reports",
            "prepare app, website, game, course, simulation, workflow, API, webhook, image, voice, and bot-builder packets",
            "prepare safe commits and pull request packets",
            "create repair plans for failed checks",
            "store only useful reports, test evidence, approvals, and reusable fix recipes",
        ],
        "approval_required": [
            "paid model calls",
            "GitHub pushes or pull-request changes",
            "production deploys",
            "secrets or credential changes",
            "money movement, trading, refunds, subscriptions, or customer charges",
            "customer outreach, social posting, robocalls, or app-store/domain submissions",
            "legal, medical, financial, credit, employment, tenant, identity, or public-safety decisions",
            "destructive file operations or overwriting user work",
        ],
        "status_files": {
            "laptop_safety": "config/buddy_laptop_safety.json",
            "runner_report": "reports/local_buddy_runner_report.json",
            "runner_log": "logs/local_buddy_runner/local_buddy_runner.out",
            "bot_readiness": "config/generated/bot_end_to_end_readiness/index.json",
            "smoke_results": "reports/generated_bot_smoke_results.json",
            "unified_workforce": "config/buddy_unified_bot_workforce.json",
            "source_fusion": "config/generated/buddy_source_fusion_report.json",
        },
    }


def write_readme(config: dict[str, Any]) -> None:
    lines = [
        "# Buddy Laptop Setup",
        "",
        "Buddy is configured to run on this laptop as a local-first DreamCo command center.",
        "",
        "## Start Buddy",
        "",
        "- One safe sweep: `python3 tools/local_buddy_runner.py --profile cheap`",
        "- Full local sweep: `python3 tools/local_buddy_runner.py --profile aggressive`",
        "- Background mode: `python3 tools/local_buddy_runner.py --profile aggressive --daemon-start --sleep-minutes 60`",
        "- Status: `python3 tools/local_buddy_runner.py --status`",
        "- Stop: `python3 tools/local_buddy_runner.py --stop`",
        f"- Dashboard: `{BUNDLED_DASHBOARD_COMMAND}`",
        "",
        "## What Buddy Can Do Locally",
        "",
    ]
    for item in config["safe_local_capabilities"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Approval Required", ""])
    for item in config["approval_required"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Safety",
            "",
            f"- Safety policy: `{SAFETY_FILE.relative_to(ROOT)}`",
            f"- Safety guide: `{SAFETY_README_FILE.relative_to(ROOT)}`",
            "- Buddy can prepare signup, app-access, and secret setup packets, but live submission or access changes require approval.",
            "- Raw secret values must stay out of repository files, reports, logs, screenshots, and messages.",
            "",
            "## Key Status Files",
            "",
        ]
    )
    for label, path in config["status_files"].items():
        lines.append(f"- {label}: `{path}`")
    README_FILE.parent.mkdir(parents=True, exist_ok=True)
    README_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    config = build_config()
    CONFIG_FILE.write_text(json.dumps(config, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_readme(config)
    checks = [
        {"name": "python", "path": shutil.which("python3")},
        {"name": "git", "path": shutil.which("git")},
        {"name": "node", "path": shutil.which("node")},
        {"name": "pnpm", "path": shutil.which("pnpm")},
        {"name": "bundled_node", "path": str(BUNDLED_NODE) if BUNDLED_NODE.exists() else None},
        {"name": "bundled_pnpm", "path": str(BUNDLED_PNPM) if BUNDLED_PNPM.exists() else None},
    ]
    commands = [
        run([sys.executable, "tools/local_buddy_runner.py", "--status"]),
        run([sys.executable, "-m", "json.tool", str(SAFETY_FILE.relative_to(ROOT))]),
        run([sys.executable, "tools/generate_bot_end_to_end_readiness.py"]),
        run([sys.executable, "tools/run_generated_bot_smoke.py"]),
    ]
    report = {
        "schema": "dreamco.buddy_laptop_install_report.v1",
        "generated_at": utc_now(),
        "config_file": str(CONFIG_FILE.relative_to(ROOT)),
        "safety_file": str(SAFETY_FILE.relative_to(ROOT)),
        "readme_file": str(README_FILE.relative_to(ROOT)),
        "safety_readme_file": str(SAFETY_README_FILE.relative_to(ROOT)),
        "binary_checks": checks,
        "command_checks": commands,
        "ready": all(item.get("ok") for item in commands),
    }
    REPORT_FILE.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"ready": report["ready"], "config": report["config_file"], "readme": report["readme_file"]}, indent=2))
    return 0 if report["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
