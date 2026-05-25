#!/usr/bin/env python3
"""Validate repository dependencies against DreamCo dependency policy."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

SKIP_DIRS: frozenset[str] = frozenset(
    {
        ".git",
        ".venv",
        "__pycache__",
        "coverage",
        "dist",
        "node_modules",
        "venv",
    }
)


def should_skip(path: Path) -> bool:
    return any(part in SKIP_DIRS for part in path.parts)


def normalize_name(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name.strip().lower())


def requirement_name(line: str) -> str | None:
    stripped = line.split("#", 1)[0].strip()
    if not stripped or stripped.startswith("-"):
        return None
    name = re.split(r"[<>=!~;\[]", stripped, maxsplit=1)[0].strip()
    if not name:
        return None
    return normalize_name(name)


def find_package_json_files(root: Path) -> list[Path]:
    return [
        p
        for p in sorted(root.rglob("package.json"))
        if p.is_file() and not should_skip(p)
    ]


def find_requirements_files(root: Path) -> list[Path]:
    return [
        p
        for p in sorted(root.rglob("requirements*.txt"))
        if p.is_file() and not should_skip(p)
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description="Check dependency policy compliance.")
    parser.add_argument(
        "--root",
        default=None,
        help="Repository root (defaults to project root).",
    )
    parser.add_argument(
        "--policy",
        default="tools/dependency_policy.json",
        help="Dependency policy JSON path.",
    )
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    root = Path(args.root).resolve() if args.root else script_dir.parent
    policy_path = Path(args.policy)
    if not policy_path.is_absolute():
        policy_path = root / policy_path
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    banned_python = {
        normalize_name(name) for name in policy.get("banned_packages", {}).get("python", [])
    }
    banned_node = {
        normalize_name(name) for name in policy.get("banned_packages", {}).get("node", [])
    }

    violations: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    for package_json in find_package_json_files(root):
        rel = str(package_json.relative_to(root))
        try:
            manifest = json.loads(package_json.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            violations.append(
                {"file": rel, "type": "invalid_json", "message": str(exc)}
            )
            continue
        for section in ("dependencies", "devDependencies"):
            for dep_name, dep_version in (manifest.get(section, {}) or {}).items():
                dep_norm = normalize_name(dep_name)
                if dep_norm in banned_node:
                    violations.append(
                        {
                            "file": rel,
                            "type": "banned_node_package",
                            "package": dep_name,
                            "version": dep_version,
                        }
                    )
                if "http://" in str(dep_version):
                    warnings.append(
                        {
                            "file": rel,
                            "type": "unapproved_registry_reference",
                            "package": dep_name,
                            "version": dep_version,
                        }
                    )

    approved_python_indexes = tuple(
        policy.get("approved_python_indexes", ["https://pypi.org/simple"])
    )
    for req_file in find_requirements_files(root):
        rel = str(req_file.relative_to(root))
        for line in req_file.read_text(encoding="utf-8").splitlines():
            stripped = line.split("#", 1)[0].strip()
            if not stripped:
                continue
            req_name = requirement_name(stripped)
            if req_name and req_name in banned_python:
                violations.append(
                    {
                        "file": rel,
                        "type": "banned_python_package",
                        "package": req_name,
                        "line": stripped,
                    }
                )
            if "http://" in stripped or "https://" in stripped:
                if not any(index in stripped for index in approved_python_indexes):
                    violations.append(
                        {
                            "file": rel,
                            "type": "unapproved_python_index",
                            "line": stripped,
                        }
                    )

    if warnings:
        print("Dependency policy warnings:")
        print(json.dumps(warnings, indent=2))
    if violations:
        print("Dependency policy violations:")
        print(json.dumps(violations, indent=2))
        return 1

    print("Dependency policy check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
