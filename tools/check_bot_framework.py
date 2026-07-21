#!/usr/bin/env python3
"""
Dreamcobots — Bot Framework Compliance Checker
===============================================

Static analysis tool that verifies every Python bot file in the repository
references the GLOBAL AI SOURCES FLOW framework.

Usage
-----
    python tools/check_bot_framework.py [--strict] [--path PATH]

Options
-------
--strict   Exit with code 1 if any violations are found (default: True).
--path     Root directory to scan (default: repository root).

Exit codes
----------
0 — All scanned files are compliant.
1 — One or more files are non-compliant (in strict mode).
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Directories whose Python files are checked for framework compliance.
BOT_DIRS: tuple[str, ...] = (
    "bots",
    "Business_bots",
    "App_bots",
    "Marketing_bots",
    "Occupational_bots",
    "Real_Estate_bots",
    "Fiverr_bots",
    "automation-tools",
    "education-tools",
    "healthcare-tools",
    "analytics-elites",
    "real-estate-tools",
    "compliance-tools",
)

# Files that are not bot implementations and should be skipped.
EXCLUDED_FILES: frozenset[str] = frozenset(
    {
        "__init__.py",
        "tiers.py",
        "registry.py",
        "billing_system.py",
        "token_manager.py",
        "subscription_manager.py",
        # Shared utility modules — not bot implementations
        "logger.py",
        "error_handler.py",
    }
)

# A compliant file must contain AT LEAST ONE of these markers.
COMPLIANCE_MARKERS: tuple[str, ...] = (
    "GlobalAISourcesFlow",
    "global_ai_sources_flow",
    "GLOBAL AI SOURCES FLOW",
)


# ---------------------------------------------------------------------------
# Scanner
# ---------------------------------------------------------------------------

def is_bot_file(path: Path) -> bool:
    """Return True if *path* should be checked for framework compliance."""
    return (
        path.suffix == ".py"
        and path.name not in EXCLUDED_FILES
        and not path.name.startswith("test_")
    )


def file_is_compliant(path: Path) -> bool:
    """Return True if *path* contains at least one compliance marker."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return False
    return any(marker in text for marker in COMPLIANCE_MARKERS)


def scan_directory(root: Path) -> tuple[list[Path], list[Path]]:
    """
    Recursively scan *root* for bot Python files.

    Returns
    -------
    compliant : list[Path]
        Files that satisfy the framework requirement.
    violations : list[Path]
        Files that do NOT reference the framework.
    """
    compliant: list[Path] = []
    violations: list[Path] = []

    for bot_dir_name in BOT_DIRS:
        bot_dir = root / bot_dir_name
        if not bot_dir.exists():
            continue
        for py_file in sorted(bot_dir.rglob("*.py")):
            if not is_bot_file(py_file):
                continue
            if file_is_compliant(py_file):
                compliant.append(py_file)
            else:
                violations.append(py_file)

    return compliant, violations


# ---------------------------------------------------------------------------
# Reporter
# ---------------------------------------------------------------------------

def report(
    compliant: list[Path],
    violations: list[Path],
    root: Path,
) -> None:
    """Print a human-readable compliance report to stdout."""
    total = len(compliant) + len(violations)

    print("=" * 60)
    print("DreamCObots Bot Framework Compliance Report")
    print("=" * 60)
    print(f"Root : {root}")
    print(f"Files scanned : {total}")
    print(f"Compliant     : {len(compliant)}")
    print(f"Violations    : {len(violations)}")
    print()

    if compliant:
        print("✅  COMPLIANT FILES")
        for p in compliant:
            print(f"   {p.relative_to(root)}")
        print()

    if violations:
        print("❌  VIOLATIONS — files missing a reference to GlobalAISourcesFlow")
        for p in violations:
            print(f"   {p.relative_to(root)}")
        print()
        print(
            "Each listed file must import and use GlobalAISourcesFlow from the\n"
            "'framework' package.  See CONTRIBUTING.md for details."
        )
    else:
        print("All scanned bot files comply with the GLOBAL AI SOURCES FLOW framework.")

    print("=" * 60)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Check that all DreamCo bot files reference the GLOBAL AI SOURCES FLOW framework.",
    )
    parser.add_argument(
        "--path",
        default=None,
        help="Root directory to scan (default: repository root, detected automatically).",
    )
    parser.add_argument(
        "--no-strict",
        action="store_true",
        default=False,
        help="Do not exit with code 1 on violations (strict mode is on by default).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    # Determine repository root: the directory containing this script's parent.
    if args.path:
        root = Path(args.path).resolve()
    else:
        root = Path(__file__).resolve().parent.parent

    compliant, violations = scan_directory(root)
    report(compliant, violations, root)

    strict = not args.no_strict
    if violations and strict:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
