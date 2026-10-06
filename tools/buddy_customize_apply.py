#!/usr/bin/env python3
"""Apply one `/buddy customize` request (dispatched by the Buddy command router).

Re-reads the command text from the GitHub API (never from workflow inputs), re-checks
that its author is a Buddy operator, then hands it to the allowlist validators:

- bot / division targets -> ``python3 -m buddy.fleet_runtime customize --issue-body-file F --apply``
- ``file:<path>`` targets -> ``python3 tools/build_file_prospectus.py customize --issue-body-file F --apply``

The validators only ever write config/bots/customizations.json or
config/files/prospectus-overrides.json. The workflow commits those to a new branch and
opens a PR; nothing is pushed to the default branch and nothing is merged.

Exit codes: 0 applied (files changed), 3 rejected by validation/authorization, 1 error.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import tools.buddy_control_plane as bcp  # noqa: E402

TARGET_LINE_RE = re.compile(r"^/buddy customize (\S+)\s*$", re.MULTILINE)
ALLOWED_OUTPUTS = {"config/bots/customizations.json", "config/files/prospectus-overrides.json"}


def fetch_text(api: bcp.GitHubAPI, issue: int, comment: int) -> tuple[str, str]:
    """Return (author_login, command_text)."""
    if comment:
        status, data = api.get(f"repos/{api.repo}/issues/comments/{comment}")
        if status != 200 or not isinstance(data, dict):
            raise RuntimeError(f"could not read comment {comment} (HTTP {status})")
        if not str(data.get("issue_url", "")).endswith(f"/issues/{issue}"):
            raise RuntimeError("comment does not belong to the dispatched issue")
        return str((data.get("user") or {}).get("login", "")), str(data.get("body") or "")
    status, data = api.get(f"repos/{api.repo}/issues/{issue}")
    if status != 200 or not isinstance(data, dict):
        raise RuntimeError(f"could not read issue {issue} (HTTP {status})")
    title = str(data.get("title") or "")
    body = str(data.get("body") or "")
    return str((data.get("user") or {}).get("login", "")), body if body.lstrip().startswith("/buddy customize") else title + "\n\n" + body


def plan(registry: dict, author: str, text: str) -> tuple[str, list[str]]:
    """Return (target, validator argv). Raises bcp.CommandError when the request is not acceptable."""
    if author.casefold() not in {o.casefold() for o in registry.get("operators", [])}:
        raise bcp.CommandError("the author of the customize request is not a Buddy operator")
    targets = TARGET_LINE_RE.findall(text.replace("\r\n", "\n"))
    if len(targets) != 1:
        raise bcp.CommandError("the request must contain exactly one '/buddy customize <target>' line")
    target = targets[0]
    if not bcp.CUSTOMIZE_TARGET_RE.match(target) or ".." in target:
        raise bcp.CommandError("invalid customize target")
    bcp.check_customize_body(text)
    if target.startswith("file:"):
        return target, [sys.executable, "tools/build_file_prospectus.py", "customize", "--issue-body-file"]
    return target, [sys.executable, "-m", "buddy.fleet_runtime", "customize", "--issue-body-file"]


def changed_files() -> list[str]:
    out = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    return sorted(line[3:] for line in out.splitlines() if line.strip())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--issue", required=True)
    parser.add_argument("--comment", default="0")
    parser.add_argument("--out", type=Path, required=True, help="JSON result for the workflow")
    args = parser.parse_args(argv)
    if not re.fullmatch(r"[0-9]{1,7}", args.issue) or not re.fullmatch(r"[0-9]{1,15}", args.comment):
        print("::error::invalid issue/comment input")
        return 1
    registry = bcp.load_registry()
    api = bcp.GitHubAPI(os.environ.get("GITHUB_REPOSITORY") or registry["repository"], os.environ.get("GH_TOKEN"))
    result: dict = {"issue": int(args.issue), "status": "rejected", "reasons": [], "changed": []}
    try:
        author, text = fetch_text(api, int(args.issue), int(args.comment))
        target, argv_ = plan(registry, author, text)
        result["target"] = target
        perm = api.permission(author)
        if perm not in bcp.WRITE_PERMISSIONS:
            raise bcp.CommandError("the author of the customize request does not have write permission")
    except bcp.CommandError as exc:
        result["reasons"] = [str(exc)]
        args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result))
        return 3
    body_file = Path(os.environ.get("RUNNER_TEMP", "/tmp")) / f"buddy-customize-{args.issue}.md"
    body_file.write_text(text, encoding="utf-8")
    proc = subprocess.run(argv_ + [str(body_file), "--apply"], cwd=ROOT, capture_output=True, text=True, check=False)
    output = (proc.stdout + proc.stderr).strip()
    if proc.returncode != 0:
        result["reasons"] = [line for line in output.splitlines() if line.strip()][-10:] or [f"validator exit {proc.returncode}"]
        args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result))
        return 3
    changed = changed_files()
    unexpected = [p for p in changed if p not in ALLOWED_OUTPUTS]
    if unexpected:
        result.update(status="error", reasons=[f"validator touched unexpected files: {unexpected}"])
        args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result))
        return 1
    result.update(status="applied" if changed else "no_change", changed=changed, validator_output=output[-2000:])
    args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
