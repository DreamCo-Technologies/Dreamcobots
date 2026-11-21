#!/usr/bin/env python3
"""Refresh interdependent repository inventories in a deterministic dependency order."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, *args]
    print("+ " + " ".join(command), flush=True)
    return subprocess.run(command, cwd=ROOT, text=True, check=check)


def main() -> int:
    # Downstream inventories consume the outputs of the earlier generators.
    run("tools/audit_actions_health.py")
    run("tools/build_actions_prospectus.py")
    run("tools/audit_pages_features.py")

    # The file prospectus indexes its own generated shards. Iterate to a
    # bounded fixed point rather than accepting a stale second-order index.
    for attempt in range(1, 4):
        run("tools/build_file_prospectus.py")
        result = run("tools/build_file_prospectus.py", "--check", check=False)
        if result.returncode == 0:
            print(f"File prospectus converged after {attempt} generation pass(es).")
            break
    else:
        raise SystemExit("File prospectus did not converge after three passes.")

    # File-prospectus generation can change source inventories consumed by the
    # public run cards. Rebuild Actions cards after that convergence, then verify.
    run("tools/build_actions_prospectus.py")
    # Recheck all derived outputs after the final generator has completed.
    run("tools/build_actions_prospectus.py", "--check", "--check-buttons")
    run("tools/audit_pages_features.py", "--check", "--check-regressions")
    print("Repository evidence inventories are current for this checkout.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
