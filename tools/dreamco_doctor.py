#!/usr/bin/env python3
"""Safe local DreamCo environment doctor.

Checks prerequisites and repository identity without changing the machine.
It is intentionally read-only so Buddy can use it as a bounded preflight.
"""
from __future__ import annotations
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def run(cmd):
    try:
        p = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, timeout=10)
        value = (p.stdout or p.stderr).strip().splitlines()
        return p.returncode == 0, value[0] if value else ""
    except Exception as exc:
        return False, str(exc)

def check_command(name, args):
    if not shutil.which(name):
        return {"status":"missing", "detail":f"{name} not found"}
    ok, out = run(args)
    return {"status":"ok" if ok else "error", "detail":out}

def main():
    checks = {
        "git": check_command("git", ["git", "--version"]),
        "node": check_command("node", ["node", "--version"]),
        "npm": check_command("npm", ["npm", "--version"]),
        "python": {"status":"ok", "detail":sys.version.split()[0]},
        "docker": check_command("docker", ["docker", "--version"]),
        "gh": check_command("gh", ["gh", "--version"]),
    }
    ok, remote = run(["git", "remote", "get-url", "origin"])
    checks["github_remote"] = {"status":"ok" if ok else "missing", "detail":remote}
    ok, branch = run(["git", "branch", "--show-current"])
    checks["branch"] = {"status":"ok" if ok else "error", "detail":branch}
    ok, sha = run(["git", "rev-parse", "HEAD"])
    checks["commit"] = {"status":"ok" if ok else "error", "detail":sha}
    ok, status = run(["git", "status", "--porcelain"])
    checks["working_tree"] = {"status":"clean" if ok and not status else "changes", "detail":status}

    required = ["git", "node", "npm", "python", "github_remote", "branch", "commit"]
    failed = [k for k in required if checks[k]["status"] not in {"ok", "clean"}]
    report = {"schema_version":1,"repository":"DreamCo-Technologies/Dreamcobots","root":str(ROOT),"checks":checks,"ready_for_local_development":not failed,"blocking_checks":failed}
    print(json.dumps(report, indent=2))
    return 1 if failed else 0

if __name__ == "__main__":
    raise SystemExit(main())
