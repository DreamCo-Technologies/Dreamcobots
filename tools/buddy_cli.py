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
SITE_STATUS = ROOT / "website" / "data" / "buddy-site-status.json"
STUDIO_STATUS = ROOT / "config" / "generated" / "buddy_multimodal_studio.json"
CONNECTIONS_STATUS = ROOT / "website" / "data" / "buddy-connection-catalog.json"


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
    sub.add_parser("open-website", help="Open the local Buddy website file.")
    sub.add_parser("open-studio", help="Open the local Creative Studio file.")
    sub.add_parser("open-connections", help="Open the local app connections workbench.")
    args = parser.parse_args()

    commands = {
        "site-check": lambda: run(["python3", "tools/build_buddy_public_site.py", "--check"]),
        "site-report": lambda: show_json(SITE_STATUS),
        "studio-check": lambda: run(["python3", "tools/generate_buddy_multimodal_studio.py", "--check"]),
        "studio-report": lambda: show_json(STUDIO_STATUS),
        "connections-check": lambda: run(["python3", "tools/generate_buddy_connection_catalog.py", "--check"]),
        "connections-report": lambda: show_json(CONNECTIONS_STATUS),
        "open-website": lambda: open_file(WEBSITE_HOME),
        "open-studio": lambda: open_file(STUDIO_HOME),
        "open-connections": lambda: open_file(CONNECTIONS_HOME),
    }
    return commands[args.command]()


if __name__ == "__main__":
    raise SystemExit(main())
