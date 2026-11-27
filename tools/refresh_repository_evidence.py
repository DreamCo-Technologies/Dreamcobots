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


def converge_prospectuses(max_attempts: int = 5) -> int:
    """Converge the mutually-referencing file and Actions prospectuses."""
    for attempt in range(1, max_attempts + 1):
        # Either generator can affect the other's inputs. Generate both, then
        # verify both without writes; repeat until they reach a fixed point.
        run("tools/build_file_prospectus.py")
        run("tools/build_actions_prospectus.py")
        file_check = run("tools/build_file_prospectus.py", "--check", check=False)
        actions_check = run(
            "tools/build_actions_prospectus.py", "--check", "--check-buttons", check=False
        )
        if file_check.returncode == 0 and actions_check.returncode == 0:
            print(f"File and Actions prospectuses converged after {attempt} pass(es).")
            return attempt
    raise SystemExit(
        f"Repository prospectuses did not converge after {max_attempts} passes."
    )


def main() -> int:
    run("tools/audit_actions_health.py")
    run("tools/audit_pages_features.py")
    converge_prospectuses()
    run("tools/audit_pages_features.py", "--check", "--check-regressions")
    print("Repository evidence inventories are current for this checkout.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
