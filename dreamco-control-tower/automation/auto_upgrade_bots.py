"""
DreamCo Control Tower — Auto-Upgrade Automation Script
========================================================
Entry-point automation script that wires together the full Control Tower
upgrade pipeline:

  1. Load bots and repos from config.
  2. Check system activity and apply intelligent scheduling.
  3. Sync each repo with GitHub (fetch PR counts, issue counts, workflow status).
  4. Run the auto-upgrader on every registered bot.
  5. Print a summary report.

Usage
-----
    python automation/auto_upgrade_bots.py

Scheduled (off-peak only) mode:
    python automation/auto_upgrade_bots.py --scheduled

Force run regardless of schedule:
    python automation/auto_upgrade_bots.py --force

Environment Variables
---------------------
    GITHUB_TOKEN   — Personal access token (required for GitHub API calls).
    REPO_ROOT      — Filesystem root of the cloned Dreamcobots repo
                     (defaults to the parent of this script's directory).
    RUN_TESTS      — Set to ``"0"`` to skip test execution.
    DRY_RUN        — Set to ``"1"`` to skip git and PR operations.
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timezone

# Make sibling modules importable when run as a script
_BACKEND = os.path.join(os.path.dirname(__file__), "..", "backend")
sys.path.insert(0, _BACKEND)

from bot_manager import BotManager
from repo_manager import RepoManager, GitHubClient
from auto_upgrader import AutoUpgrader

# ---------------------------------------------------------------------------
# Scheduling helpers
# ---------------------------------------------------------------------------

#: Off-peak window: 22:00–06:00 UTC.  Upgrades run automatically only within
#: this window unless ``--force`` / ``DRY_RUN`` is set.
OFF_PEAK_START = 22
OFF_PEAK_END = 6


def is_off_peak() -> bool:
    """Return ``True`` if the current UTC hour is within the off-peak window."""
    hour = datetime.now(timezone.utc).hour
    if OFF_PEAK_START > OFF_PEAK_END:
        return hour >= OFF_PEAK_START or hour < OFF_PEAK_END
    return OFF_PEAK_START <= hour < OFF_PEAK_END


def main(scheduled: bool = False, force: bool = False) -> None:
    """Run the full auto-upgrade pipeline.

    Parameters
    ----------
    scheduled:
        When ``True``, skip the run if the current time is outside the
        off-peak window (unless *force* is also ``True``).
    force:
        Override scheduling constraints and always run.
    """
    # ------------------------------------------------------------------ config
    config_dir = os.path.join(os.path.dirname(__file__), "..", "config")
    bots_config = os.path.join(config_dir, "bots.json")
    repos_config = os.path.join(config_dir, "repos.json")

    repo_root = os.environ.get("REPO_ROOT", os.path.join(os.path.dirname(__file__), "..", ".."))
    run_tests = os.environ.get("RUN_TESTS", "1") != "0"
    dry_run = os.environ.get("DRY_RUN", "0") == "1"

    print("=" * 60)
    print("DreamCo Control Tower — Auto-Upgrade Pipeline")
    print("=" * 60)

    # ------------------------------------------------------------ scheduling
    off_peak = is_off_peak()
    current_hour = datetime.now(timezone.utc).strftime("%H:%M UTC")
    print(f"  Current time  : {current_hour}  ({'off-peak ✅' if off_peak else 'peak ⚠️'})")

    if scheduled and not off_peak and not force:
        print(
            "\n⏭️  Scheduled mode: skipping — not in off-peak window "
            f"({OFF_PEAK_START:02d}:00–{OFF_PEAK_END:02d}:00 UTC)."
        )
        print("   Use --force to override.")
        return

    if not off_peak:
        print("⚠️  Running during peak hours — consider scheduling upgrades off-peak.")

    print(f"  Repo root     : {repo_root}")
    print(f"  Run tests     : {run_tests}")
    print(f"  Dry run       : {dry_run}")
    print(f"  Force         : {force}")
    print()

    # ----------------------------------------------------------------- managers
    bm = BotManager(config_path=bots_config)
    client = GitHubClient()
    rm = RepoManager(config_path=repos_config, github_client=client)

    print(f"Registered bots  : {bm.total_bots()}")
    print(f"Monitored repos  : {len(rm.list_repos())}")
    print()

    # ------------------------------------------------------------------ sync repos
    print("Syncing repositories with GitHub…")
    sync_results = rm.sync_all()
    for name, result in sync_results.items():
        if "error" in result:
            print(f"  ⚠️  {name}: {result['error']}")
        else:
            prs = result.get("openPRs", "?")
            issues = result.get("openIssues", "?")
            print(f"  ✅  {name}: {prs} open PRs, {issues} open issues")
    print()

    # ----------------------------------------------------------------- upgrade bots
    if dry_run:
        print("DRY RUN — skipping git pull / PR creation.")
        bots = bm.list_bots()
        for bot in bots:
            print(f"  🤖  Would upgrade: {bot['name']} ({bot.get('repoPath', '?')})")
        print()
        print("Dry-run complete.  No changes were made.")
        return

    upgrader = AutoUpgrader(
        bot_manager=bm,
        repo_manager=rm,
        repo_root=repo_root,
        run_tests=run_tests,
    )

    print("Running auto-upgrade on all bots…")
    results = upgrader.upgrade_all()

    ok = 0
    resolved = 0
    errors = 0
    for name, result in results.items():
        status = result.get("status", "error")
        if status == "ok":
            ok += 1
            print(f"  ✅  {name}: updated successfully")
        elif status == "conflict_resolved":
            resolved += 1
            print(f"  🔧  {name}: conflict auto-resolved")
        else:
            errors += 1
            detail = result.get("detail") or result.get("pull", {}).get("stderr", "")
            print(f"  ❌  {name}: error — {detail[:80] if detail else 'unknown'}")
    print()

    # ------------------------------------------------------------------- summary
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"  Bots upgraded      : {ok}")
    print(f"  Conflicts resolved : {resolved}")
    print(f"  Errors             : {errors}")
    print(f"  Off-peak run       : {'yes' if off_peak else 'no'}")
    print()
    print("Upgrade pipeline complete.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="DreamCo Control Tower — Auto-Upgrade Pipeline"
    )
    parser.add_argument(
        "--scheduled",
        action="store_true",
        help="Only run during the off-peak window (22:00–06:00 UTC).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Run regardless of scheduling constraints.",
    )
    args = parser.parse_args()
    main(scheduled=args.scheduled, force=args.force)
