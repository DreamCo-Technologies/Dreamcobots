#!/usr/bin/env python3
"""Small local CLI for the Buddy website and Creative Studio."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WEBSITE_HOME = ROOT / "website" / "buddy.html"
STUDIO_HOME = ROOT / "website" / "studio.html"
CONNECTIONS_HOME = ROOT / "website" / "connections.html"
MODEL_LAB_HOME = ROOT / "website" / "models.html"
SITE_STATUS = ROOT / "website" / "data" / "buddy-site-status.json"
STUDIO_STATUS = ROOT / "config" / "generated" / "buddy_multimodal_studio.json"
CONNECTIONS_STATUS = ROOT / "website" / "data" / "buddy-connection-catalog.json"
MODEL_BENCHMARK_STATUS = ROOT / "config" / "generated" / "buddy_model_benchmarks.json"


def run(command: list[str]) -> int:
    return subprocess.run(command, cwd=ROOT, check=False).returncode


def show_json(path: Path) -> int:
    if not path.exists():
        print(json.dumps({"ok": False, "error": f"Missing file: {path.relative_to(ROOT)}"}, indent=2))
        return 1
    print(path.read_text(encoding="utf-8"))
    return 0


def open_file(path: Path) -> int:
    if not path.exists():
        print(f"Missing file: {path.relative_to(ROOT)}")
        return 1
    return run(["open", str(path)])


def check_benchmark() -> int:
    if not MODEL_BENCHMARK_STATUS.exists():
        print(json.dumps({"ok": False, "error": "Generate the model benchmark catalog first."}, indent=2))
        return 1
    payload = json.loads(MODEL_BENCHMARK_STATUS.read_text(encoding="utf-8"))
    targets = payload.get("targets", [])
    suites = payload.get("suites", [])
    valid = len(targets) == 100 and len(suites) >= 1 and all(
        target.get("catalogReady") is True
        and target.get("liveEvidenceStatus") == "not_run"
        and target.get("liveScore") is None
        for target in targets
    )
    print(json.dumps({"ok": valid, **payload.get("summary", {})}, indent=2))
    return 0 if valid else 1


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="buddy",
        description="Buddy local website, deployment preflight, and Creative Studio controls.",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("site-check", help="Validate the public website before deployment.")
    sub.add_parser("site-report", help="Print the generated public site status.")
    sub.add_parser("studio-check", help="Validate the Creative Studio registry.")
    sub.add_parser("studio-report", help="Print the Creative Studio registry.")
    sub.add_parser("connections-check", help="Validate the app connection registry.")
    sub.add_parser("connections-report", help="Print the public connection catalog.")
    sub.add_parser("benchmark-check", help="Validate the 100-target model benchmark registry.")
    sub.add_parser("benchmark-report", help="Print the generated model benchmark catalog.")
    sub.add_parser("open-website", help="Open the local Buddy website file.")
    sub.add_parser("open-studio", help="Open the local Creative Studio file.")
    sub.add_parser("open-connections", help="Open the local app connections workbench.")
    sub.add_parser("open-model-lab", help="Open the model benchmark lab.")
    local = sub.add_parser("local-start", help="Run Buddy through the approval-gated laptop bridge.")
    local.add_argument("--port", type=int, default=8765)
    local.add_argument("--no-open", action="store_true", help="Do not open Buddy automatically.")
    args = parser.parse_args()

    commands = {
        "site-check": lambda: run(["python3", "tools/build_buddy_public_site.py", "--check"]),
        "site-report": lambda: show_json(SITE_STATUS),
        "studio-check": lambda: run(["python3", "tools/generate_buddy_multimodal_studio.py", "--check"]),
        "studio-report": lambda: show_json(STUDIO_STATUS),
        "connections-check": lambda: run(["python3", "tools/generate_buddy_connection_catalog.py", "--check"]),
        "connections-report": lambda: show_json(CONNECTIONS_STATUS),
        "benchmark-check": check_benchmark,
        "benchmark-report": lambda: show_json(MODEL_BENCHMARK_STATUS),
        "open-website": lambda: open_file(WEBSITE_HOME),
        "open-studio": lambda: open_file(STUDIO_HOME),
        "open-connections": lambda: open_file(CONNECTIONS_HOME),
        "open-model-lab": lambda: open_file(MODEL_LAB_HOME),
        "local-start": lambda: run([
            "python3", "tools/buddy_local_bridge.py", "--port", str(args.port),
            *([] if args.no_open else ["--open"]),
        ]),
    }
    return commands[args.command]()


if __name__ == "__main__":
    raise SystemExit(main())
