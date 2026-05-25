#!/usr/bin/env python3
"""Validate environment and lockfile consistency for hermetic setup."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def read_trimmed(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Check hermetic environment pins.")
    parser.add_argument("--root", default=None, help="Repository root.")
    parser.add_argument(
        "--python-version",
        default="3.11",
        help="Expected value in .python-version.",
    )
    parser.add_argument(
        "--node-version",
        default="20",
        help="Expected value in .nvmrc and package.json engines node major.",
    )
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    root = Path(args.root).resolve() if args.root else script_dir.parent

    errors: list[str] = []

    python_version_file = root / ".python-version"
    nvmrc_file = root / ".nvmrc"
    uv_lock = root / "uv.lock"
    package_json = root / "package.json"

    if not python_version_file.exists():
        errors.append("Missing .python-version")
    else:
        value = read_trimmed(python_version_file)
        if value != args.python_version:
            errors.append(
                f".python-version mismatch: expected '{args.python_version}', got '{value}'"
            )

    if not nvmrc_file.exists():
        errors.append("Missing .nvmrc")
    else:
        value = read_trimmed(nvmrc_file).lstrip("v")
        if value != args.node_version:
            errors.append(f".nvmrc mismatch: expected '{args.node_version}', got '{value}'")

    if not uv_lock.exists():
        errors.append("Missing uv.lock")

    if not package_json.exists():
        errors.append("Missing package.json")
    else:
        manifest = json.loads(package_json.read_text(encoding="utf-8"))
        engine = str((manifest.get("engines") or {}).get("node", "")).strip()
        if not engine:
            errors.append("package.json engines.node missing")
        else:
            expected_major = re.escape(args.node_version)
            if not re.search(expected_major, engine):
                errors.append(
                    f"package.json engines.node does not match major '{args.node_version}': '{engine}'"
                )

    if errors:
        print("Hermetic consistency check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Hermetic consistency check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
