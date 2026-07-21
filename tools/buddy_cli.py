#!/usr/bin/env python3
"""Buddy local CLI for the owner laptop."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUNDLED_NODE_BIN = Path("/Users/mamas/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin")
BUNDLED_PNPM = Path("/Users/mamas/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/fallback/pnpm")
TEST_KIT = ROOT / "reports" / "buddy-free-local-test-kit.html"
WEBSITE_HOME = ROOT / "website" / "index.html"


def run(command: list[str], *, check: bool = True) -> int:
    env = {**os.environ, "PYTHONPYCACHEPREFIX": "/private/tmp/dreamco-buddy-cli-pycache"}
    if BUNDLED_NODE_BIN.exists():
        env["PATH"] = f"{BUNDLED_NODE_BIN}:{env.get('PATH', '')}"
    completed = subprocess.run(command, cwd=ROOT, env=env)
    if check and completed.returncode != 0:
        return completed.returncode
    return completed.returncode


def show_json(path: Path) -> int:
    if not path.exists():
        print(json.dumps({"ok": False, "error": f"Missing file: {path.relative_to(ROOT)}"}, indent=2))
        return 1
    print(path.read_text(encoding="utf-8"))
    return 0


def open_file(path: Path) -> int:
    if not path.exists():
        print(f"Missing file: {path}")
        return 1
    return run(["open", str(path)], check=False)


def dashboard() -> int:
    if not BUNDLED_PNPM.exists():
        print("Bundled pnpm was not found. Run: buddy setup")
        return 1
    return run([str(BUNDLED_PNPM), "run", "dev"], check=False)


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="buddy",
        description="Buddy local-first CLI for DreamCo repository work, free testing, and guarded autonomy.",
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("setup", help="Regenerate laptop setup, safety checks, and test evidence.")
    sub.add_parser("status", help="Show background runner status.")
    sub.add_parser("test", help="Run the free/local test kit checks.")
    sub.add_parser("once", help="Run one cheap local sweep.")
    sub.add_parser("full", help="Run one guarded aggressive local sweep.")
    sub.add_parser("start", help="Start guarded background mode.")
    sub.add_parser("stop", help="Stop guarded background mode.")
    sub.add_parser("dashboard", help="Start the local dashboard dev server.")
    sub.add_parser("open-test-kit", help="Open the free/local test kit HTML file.")
    sub.add_parser("open-website", help="Open the static website home page.")
    sub.add_parser("free-report", help="Print the free/local test kit JSON report.")
    sub.add_parser("autonomy-report", help="Print the governed autonomy JSON report.")

    args = parser.parse_args()
    command = args.command or "status"

    if command == "setup":
        return run(["python3", "tools/setup_buddy_laptop.py"])
    if command == "status":
        return run(["python3", "tools/local_buddy_runner.py", "--status"])
    if command == "test":
        return run(["python3", "tools/generate_buddy_free_local_test_kit.py", "--check"])
    if command == "once":
        return run(["python3", "tools/local_buddy_runner.py", "--profile", "cheap"])
    if command == "full":
        return run(["python3", "tools/local_buddy_runner.py", "--profile", "aggressive"])
    if command == "start":
        return run(["python3", "tools/local_buddy_runner.py", "--profile", "aggressive", "--daemon-start", "--sleep-minutes", "60"])
    if command == "stop":
        return run(["python3", "tools/local_buddy_runner.py", "--stop"])
    if command == "dashboard":
        return dashboard()
    if command == "open-test-kit":
        return open_file(TEST_KIT)
    if command == "open-website":
        return open_file(WEBSITE_HOME)
    if command == "free-report":
        return show_json(ROOT / "reports" / "buddy_free_local_test_kit.json")
    if command == "autonomy-report":
        return show_json(ROOT / "config" / "generated" / "buddy_autonomous_everything.json")

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
