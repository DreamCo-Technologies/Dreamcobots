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
SONG_TEST = ROOT / "reports" / "buddy-song-voice-image-test.html"
WEBSITE_HOME = ROOT / "website" / "index.html"
STUDIO_HOME = ROOT / "website" / "studio.html"


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
    sub.add_parser("song-test", help="Generate the local song, voice, and image test packet.")
    sub.add_parser("open-song-test", help="Open the local song, voice, and image test page.")
    sub.add_parser("open-website", help="Open the static website home page.")
    sub.add_parser("free-report", help="Print the free/local test kit JSON report.")
    sub.add_parser("autonomy-report", help="Print the governed autonomy JSON report.")
    route_parser = sub.add_parser("route", help="Route a task through Buddy's free-first API router.")
    route_parser.add_argument("task", nargs="?", default="general_chat")
    route_parser.add_argument("--mode", choices=["free_first", "local_only", "premium_optional", "quality_first"], default="free_first")
    sub.add_parser("router-refresh", help="Regenerate the professional API router and free model library.")
    sub.add_parser("free-models", help="Print the free model/task library JSON.")
    sub.add_parser("native-coverage", help="Regenerate Buddy's repo-native bot coverage map.")
    sub.add_parser("native-report", help="Print Buddy's repo-native bot coverage JSON.")
    sub.add_parser("bot-sprint", help="Regenerate Buddy's ASAP bot completion sprint queue.")
    sub.add_parser("bot-sprint-report", help="Print Buddy's ASAP bot completion sprint JSON.")
    sub.add_parser("site-sync", help="Sync Buddy generated report data into the static website build.")
    sub.add_parser("site-report", help="Print the static website Buddy status JSON.")
    sub.add_parser("studio-refresh", help="Regenerate Buddy Creative Studio registry and report.")
    sub.add_parser("studio-report", help="Print the Buddy Creative Studio registry.")
    sub.add_parser("open-studio", help="Open the local Buddy Creative Studio page.")
    innovate_parser = sub.add_parser("innovate", help="Compare six designs for a Buddy objective.")
    innovate_parser.add_argument("objective")
    innovate_parser.add_argument("--audience", default="DreamCo user")
    innovate_parser.add_argument("--mode", choices=["balanced", "bold", "trusted", "lean"], default="balanced")
    innovate_parser.add_argument("--tag", action="append", default=[])
    innovate_parser.add_argument("--constraint", action="append", default=[])
    sub.add_parser("innovation-refresh", help="Regenerate Buddy's innovation engine registry.")
    sub.add_parser("innovation-report", help="Print Buddy's innovation engine registry.")
    sub.add_parser("history-audit", help="Scan local Git clones, branches, and reflogs for recoverable work.")
    sub.add_parser("history-report", help="Print Buddy's Git recovery audit JSON.")

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
    if command == "song-test":
        return run(["python3", "tools/generate_buddy_song_voice_image_test.py"])
    if command == "open-song-test":
        return open_file(SONG_TEST)
    if command == "open-website":
        return open_file(WEBSITE_HOME)
    if command == "free-report":
        return show_json(ROOT / "reports" / "buddy_free_local_test_kit.json")
    if command == "autonomy-report":
        return show_json(ROOT / "config" / "generated" / "buddy_autonomous_everything.json")
    if command == "route":
        return run(["python3", "tools/buddy_api_router.py", args.task, "--mode", args.mode])
    if command == "router-refresh":
        return run(["python3", "tools/generate_buddy_professional_api_router.py"])
    if command == "free-models":
        return show_json(ROOT / "config" / "generated" / "buddy_free_model_task_library.json")
    if command == "native-coverage":
        return run(["python3", "tools/generate_buddy_native_bot_coverage.py"])
    if command == "native-report":
        return show_json(ROOT / "config" / "generated" / "buddy_native_bot_coverage.json")
    if command == "bot-sprint":
        return run(["python3", "tools/generate_buddy_bot_completion_sprint.py"])
    if command == "bot-sprint-report":
        return show_json(ROOT / "config" / "generated" / "buddy_bot_completion_sprint.json")
    if command == "site-sync":
        return run(["python3", "tools/sync_buddy_website_build.py"])
    if command == "site-report":
        return show_json(ROOT / "website" / "data" / "buddy-site-status.json")
    if command == "studio-refresh":
        return run(["python3", "tools/generate_buddy_multimodal_studio.py"])
    if command == "studio-report":
        return show_json(ROOT / "config" / "generated" / "buddy_multimodal_studio.json")
    if command == "open-studio":
        return open_file(STUDIO_HOME)
    if command == "innovate":
        invocation = [
            "python3",
            "tools/buddy_innovation_loop.py",
            args.objective,
            "--audience",
            args.audience,
            "--mode",
            args.mode,
        ]
        for tag in args.tag:
            invocation.extend(["--tag", tag])
        for constraint in args.constraint:
            invocation.extend(["--constraint", constraint])
        return run(invocation)
    if command == "innovation-refresh":
        return run(["python3", "tools/generate_buddy_innovation_registry.py"])
    if command == "innovation-report":
        return show_json(ROOT / "config" / "generated" / "buddy_innovation_engine.json")
    if command == "history-audit":
        return run(["python3", "tools/generate_buddy_git_recovery_audit.py"])
    if command == "history-report":
        return show_json(ROOT / "config" / "generated" / "buddy_git_recovery_audit.json")

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
