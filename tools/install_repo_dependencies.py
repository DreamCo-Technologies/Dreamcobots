#!/usr/bin/env python3
"""Install all repository Node and Python dependencies."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

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
    """Return True when *path* belongs to an excluded directory tree."""
    return any(part in SKIP_DIRS for part in path.parts)


def find_package_json_dirs(root: Path) -> list[Path]:
    """Return package directories that contain package.json."""
    dirs: list[Path] = []
    for manifest in sorted(root.rglob("package.json")):
        if should_skip(manifest):
            continue
        dirs.append(manifest.parent)
    return dirs


def find_requirements_files(root: Path) -> list[Path]:
    """Return all requirements*.txt files in the repository."""
    files: list[Path] = []
    for file_path in sorted(root.rglob("requirements*.txt")):
        if should_skip(file_path):
            continue
        files.append(file_path)
    return files


def run_cmd(cmd: list[str], cwd: Path, dry_run: bool) -> None:
    """Run command in cwd and stream output."""
    command_text = " ".join(cmd)
    print(f"\n▶ {command_text}  (cwd={cwd})")
    if dry_run:
        return
    subprocess.run(cmd, cwd=str(cwd), check=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Install all Node and Python dependencies across the repository.",
    )
    parser.add_argument(
        "--root",
        default=None,
        help="Repository root (defaults to project root).",
    )
    parser.add_argument(
        "--python-only",
        action="store_true",
        help="Install only Python dependencies.",
    )
    parser.add_argument(
        "--node-only",
        action="store_true",
        help="Install only Node dependencies.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print commands without executing them.",
    )
    args = parser.parse_args()

    if args.python_only and args.node_only:
        print("ERROR: --python-only and --node-only cannot be combined.", file=sys.stderr)
        return 2

    script_dir = Path(__file__).resolve().parent
    root = Path(args.root).resolve() if args.root else script_dir.parent
    install_node = not args.python_only
    install_python = not args.node_only

    print(f"Repository root: {root}")

    try:
        if install_node:
            package_dirs = find_package_json_dirs(root)
            print(f"Discovered {len(package_dirs)} package.json locations.")
            for package_dir in package_dirs:
                run_cmd(["npm", "install"], cwd=package_dir, dry_run=args.dry_run)

        if install_python:
            requirements_files = find_requirements_files(root)
            print(f"Discovered {len(requirements_files)} requirements files.")
            for requirements_file in requirements_files:
                run_cmd(
                    [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)],
                    cwd=root,
                    dry_run=args.dry_run,
                )
    except subprocess.CalledProcessError as exc:
        print(f"\nDependency installation failed with exit code {exc.returncode}.", file=sys.stderr)
        return exc.returncode

    print("\n✅ Repository dependency bootstrap complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
