"""
Debug Bot — Automated debugging assistant for the self-healing system.

Invoked by the Self Healing System workflow when the DreamCo Master System
workflow fails. Inspects recent logs and reports common failure causes.

Also orchestrates the Repo Validation Bot to surface structural issues
across all bots in the repository.
"""

from __future__ import annotations

import importlib.util
import os
import sys

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _load_bot(filename: str, module_name: str):
    """Load a standalone bot module by file path, bypassing package conflicts."""
    path = os.path.join(os.path.dirname(__file__), "..", "bots", filename)
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _run_repo_validation() -> str:
    """
    Run the Repo Validation Bot and return a status string.

    Returns ``"OK"`` when every bot passes, ``"ISSUES_FOUND"`` otherwise.
    """
    print("\n--- Repo Validation Bot ---")
    try:
        if _REPO_ROOT not in sys.path:
            sys.path.insert(0, _REPO_ROOT)
        from bots.repo_validation_bot import RepoValidationBot  # noqa: PLC0415

        bot = RepoValidationBot(repo_root=_REPO_ROOT)
        report = bot.run()
        if report.all_passed:
            return "OK"
        print(f"⚠️  Repo validation: {report.failed} bot(s) have structural issues.")
        return "ISSUES_FOUND"
    except Exception as exc:
        print(f"❌ Repo Validation Bot error: {exc}")
        return "ERROR"


def run_debug() -> str:
    """Perform automated debug inspection and return a status message."""
    print("=== DreamCo Debug Bot — Auto-Repair Attempt ===")

    checks = []

    # Check that required pipeline bot files are loadable and contain expected functions
    bot_checks = [
        ("lead_bot.py", "_dbg_lead_bot", "run_leads"),
        ("outreach_bot.py", "_dbg_outreach_bot", "send_message"),
        ("sales_bot.py", "_dbg_sales_bot", "close_sales"),
        ("real_estate_bot.py", "_dbg_real_estate_bot", "find_deals"),
    ]

    sys.path.insert(0, _REPO_ROOT)

    for filename, module_name, func_name in bot_checks:
        bot_label = f"bots/{os.path.splitext(filename)[0]}.{func_name}"
        try:
            module = _load_bot(filename, module_name)
            if hasattr(module, func_name):
                checks.append(f"✅ {bot_label} — OK")
            else:
                checks.append(f"❌ {bot_label} — missing function")
        except Exception as exc:
            checks.append(f"❌ bots/{filename} — error: {exc}")

    for check in checks:
        print(check)

    # Run the Repo Validation Bot for comprehensive structural checks
    validation_status = _run_repo_validation()

    failed = [c for c in checks if c.startswith("❌")]
    if failed or validation_status != "OK":
        issues = len(failed)
        if validation_status != "OK":
            issues += 1
        print(f"\n⚠️  {issues} issue group(s) detected. Manual review required.")
        return "REPAIR_NEEDED"

    print("\n✅ All checks passed — system appears healthy.")
    return "OK"


if __name__ == "__main__":
    result = run_debug()
    sys.exit(0 if result == "OK" else 1)
