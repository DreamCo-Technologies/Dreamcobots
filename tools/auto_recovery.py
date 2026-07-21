#!/usr/bin/env python3
"""
Dreamcobots — CI Auto-Recovery Tool
=====================================

Diagnoses common CI failures and attempts automated fixes.

Checks performed
----------------
1. Python version compatibility (requires 3.8+)
2. Missing or out-of-date pip dependencies (from requirements.txt)
3. Bot framework compliance violations (runs check_bot_framework.py)
4. Uncommitted changes in the working tree (informational)

Usage
-----
    python tools/auto_recovery.py [--requirements FILE] [--repo-root DIR]
                                  [--log-file FILE] [--webhook-url URL]

Exit codes
----------
0 — All checks passed (or all fixable issues were resolved).
1 — One or more issues require manual intervention.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MIN_PYTHON = (3, 8)
RECOVERY_LOG_DEFAULT = "ci_recovery.log"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _utcnow() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def _run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    """Run *cmd* and return the completed process (never raises on non-zero)."""
    return subprocess.run(cmd, capture_output=True, text=True, **kwargs)


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def check_python_version() -> dict:
    """Verify the running Python meets the minimum version requirement."""
    current = sys.version_info[:2]
    ok = current >= MIN_PYTHON
    return {
        "check": "python_version",
        "status": "ok" if ok else "fail",
        "detail": (
            f"Python {current[0]}.{current[1]} detected"
            if ok
            else (
                f"Python {current[0]}.{current[1]} is below the minimum "
                f"{MIN_PYTHON[0]}.{MIN_PYTHON[1]}"
            )
        ),
        "fix_applied": False,
        "manual_action": None if ok else (
            f"Upgrade to Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]} or later."
        ),
    }


def check_dependencies(requirements_file: Path) -> dict:
    """
    Ensure all packages listed in *requirements_file* are importable / installed.

    If any are missing the function attempts ``pip install -r <file>`` as an
    automatic fix and re-checks.
    """
    if not requirements_file.exists():
        return {
            "check": "dependencies",
            "status": "skip",
            "detail": f"{requirements_file} not found — skipping dependency check.",
            "fix_applied": False,
            "manual_action": None,
        }

    result = _run(
        [sys.executable, "-m", "pip", "check"],
    )
    issues = result.stdout.strip() + result.stderr.strip()

    if result.returncode == 0:
        return {
            "check": "dependencies",
            "status": "ok",
            "detail": "All installed packages are compatible.",
            "fix_applied": False,
            "manual_action": None,
        }

    # Attempt automatic fix
    fix_result = _run(
        [sys.executable, "-m", "pip", "install", "-r", str(requirements_file),
         "--quiet", "--disable-pip-version-check"],
    )
    if fix_result.returncode == 0:
        return {
            "check": "dependencies",
            "status": "ok",
            "detail": f"Dependency issues detected and resolved via pip install -r {requirements_file.name}.",
            "fix_applied": True,
            "manual_action": None,
        }

    return {
        "check": "dependencies",
        "status": "fail",
        "detail": (
            f"pip check reported issues and automatic fix failed.\n"
            f"pip check output: {issues}\n"
            f"pip install stderr: {fix_result.stderr.strip()}"
        ),
        "fix_applied": False,
        "manual_action": f"Run: pip install -r {requirements_file.name} and resolve any conflicts manually.",
    }


def check_framework_compliance(repo_root: Path) -> dict:
    """
    Run tools/check_bot_framework.py and report any violations.

    Violations require manual intervention (adding the framework marker to
    non-compliant bot files).
    """
    checker = repo_root / "tools" / "check_bot_framework.py"
    if not checker.exists():
        return {
            "check": "framework_compliance",
            "status": "skip",
            "detail": "tools/check_bot_framework.py not found — skipping.",
            "fix_applied": False,
            "manual_action": None,
        }

    result = _run([sys.executable, str(checker), "--path", str(repo_root)])
    ok = result.returncode == 0
    return {
        "check": "framework_compliance",
        "status": "ok" if ok else "fail",
        "detail": result.stdout.strip() or result.stderr.strip(),
        "fix_applied": False,
        "manual_action": (
            None if ok else (
                "Add 'GLOBAL AI SOURCES FLOW' compliance marker to each listed file. "
                "See CONTRIBUTING.md for details."
            )
        ),
    }


def check_uncommitted_changes(repo_root: Path) -> dict:
    """Report uncommitted changes (informational — not treated as a failure)."""
    result = _run(["git", "status", "--porcelain"], cwd=str(repo_root))
    changed_files = [l for l in result.stdout.splitlines() if l.strip()]
    if not changed_files:
        return {
            "check": "uncommitted_changes",
            "status": "ok",
            "detail": "Working tree is clean.",
            "fix_applied": False,
            "manual_action": None,
        }
    return {
        "check": "uncommitted_changes",
        "status": "warn",
        "detail": f"{len(changed_files)} uncommitted file(s): {', '.join(f.strip() for f in changed_files[:5])}{'...' if len(changed_files) > 5 else ''}",
        "fix_applied": False,
        "manual_action": "Review and commit or revert unexpected changes.",
    }


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def write_log(results: list[dict], log_file: Path) -> None:
    """Append a JSON-formatted recovery report to *log_file*."""
    entry = {
        "timestamp": _utcnow(),
        "python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "results": results,
    }
    log_file.parent.mkdir(parents=True, exist_ok=True)
    with log_file.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")
    print(f"[auto_recovery] Recovery log written to: {log_file}")


# ---------------------------------------------------------------------------
# Notifications
# ---------------------------------------------------------------------------

def send_webhook(webhook_url: str, results: list[dict]) -> None:
    """POST a JSON summary of recovery results to *webhook_url*."""
    failures = [r for r in results if r["status"] == "fail"]
    payload = json.dumps(
        {
            "timestamp": _utcnow(),
            "repository": "Dreamcobots",
            "recovery_summary": {
                "total_checks": len(results),
                "passed": sum(1 for r in results if r["status"] == "ok"),
                "warnings": sum(1 for r in results if r["status"] == "warn"),
                "failures": len(failures),
                "fixes_applied": sum(1 for r in results if r.get("fix_applied")),
            },
            "failed_checks": failures,
        }
    ).encode()

    req = urllib.request.Request(
        webhook_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            print(f"[auto_recovery] Webhook notification sent (HTTP {resp.status}).")
    except (urllib.error.URLError, OSError) as exc:
        print(f"[auto_recovery] Webhook notification failed: {exc}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Reporter
# ---------------------------------------------------------------------------

def print_report(results: list[dict]) -> None:
    """Print a human-readable summary to stdout."""
    icons = {"ok": "✅", "fail": "❌", "warn": "⚠️ ", "skip": "⏭️ "}
    print()
    print("=" * 60)
    print("  Dreamcobots — CI Auto-Recovery Report")
    print(f"  {_utcnow()}")
    print("=" * 60)
    for r in results:
        icon = icons.get(r["status"], "?")
        print(f"\n{icon}  [{r['check'].upper()}]")
        print(f"   Status : {r['status'].upper()}")
        for line in r["detail"].splitlines():
            print(f"   {line}")
        if r.get("fix_applied"):
            print("   🔧  Automatic fix was applied.")
        if r.get("manual_action"):
            print(f"   👉  Manual action required: {r['manual_action']}")
    print()
    failures = [r for r in results if r["status"] == "fail"]
    if failures:
        print(f"❌  {len(failures)} check(s) require manual intervention.")
    else:
        print("✅  All checks passed (or were automatically resolved).")
    print("=" * 60)
    print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Diagnose and auto-recover common CI failures in Dreamcobots.",
    )
    parser.add_argument(
        "--repo-root",
        default=None,
        help="Repository root directory (default: auto-detected from script location).",
    )
    parser.add_argument(
        "--requirements",
        default=None,
        help="Path to requirements.txt (default: <repo-root>/requirements.txt).",
    )
    parser.add_argument(
        "--log-file",
        default=None,
        help=f"Path to the recovery log file (default: <repo-root>/{RECOVERY_LOG_DEFAULT}).",
    )
    parser.add_argument(
        "--webhook-url",
        default=None,
        help="Optional webhook URL to POST recovery results to.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve() if args.repo_root else Path(__file__).resolve().parent.parent
    requirements_file = Path(args.requirements).resolve() if args.requirements else repo_root / "requirements.txt"
    log_file = Path(args.log_file).resolve() if args.log_file else repo_root / RECOVERY_LOG_DEFAULT

    print(f"[auto_recovery] Running diagnostics in: {repo_root}")

    results = [
        check_python_version(),
        check_dependencies(requirements_file),
        check_framework_compliance(repo_root),
        check_uncommitted_changes(repo_root),
    ]

    print_report(results)
    write_log(results, log_file)

    if args.webhook_url:
        send_webhook(args.webhook_url, results)

    failures = [r for r in results if r["status"] == "fail"]
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
