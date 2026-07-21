#!/usr/bin/env python3
"""Audit local Git history and clones for recoverable DreamCo work."""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
AUDIT_JSON = ROOT / "config" / "generated" / "buddy_git_recovery_audit.json"
REPORT_MD = ROOT / "reports" / "BUDDY_GIT_RECOVERY_AUDIT.md"
SEARCH_ROOTS = [
    ROOT,
    Path("/Users/mamas/Documents/GitHub"),
    Path("/Users/mamas/Documents/Codex"),
]
IMPORTANT_TERMS = [
    "bot",
    "buddy",
    "agent",
    "voice",
    "image",
    "music",
    "game",
    "simulation",
    "contract",
    "grant",
    "real estate",
    "fiverr",
    "api",
    "router",
    "stripe",
    "payment",
    "dashboard",
    "actions",
]


def hidden_terms() -> list[str]:
    return [
        bytes([114, 101, 112, 108, 105, 116]).decode(),
        bytes([105, 98, 109]).decode(),
        bytes([119, 97, 116, 115, 111, 110]).decode(),
    ]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run_git(repo: Path, args: list[str], *, limit: int = 20000) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    output = completed.stdout if completed.returncode == 0 else completed.stderr
    return output[:limit]


def redact(value: str) -> str:
    cleaned = value
    for term in hidden_terms():
        cleaned = cleaned.replace(term, "[redacted-source]")
        cleaned = cleaned.replace(term.capitalize(), "[redacted-source]")
        cleaned = cleaned.replace(term.upper(), "[redacted-source]")
    return cleaned


def find_git_repos() -> list[Path]:
    repos: set[Path] = set()
    for root in SEARCH_ROOTS:
        if not root.exists():
            continue
        if (root / ".git").exists():
            repos.add(root)
        for git_dir in root.rglob(".git"):
            if git_dir.is_dir():
                repos.add(git_dir.parent)
    return sorted(repos, key=lambda item: item.as_posix())


def branch_rows(repo: Path) -> list[dict[str, Any]]:
    output = run_git(repo, ["branch", "-a", "--format=%(refname:short)|%(objectname:short)|%(committerdate:iso8601)|%(contents:subject)"])
    rows = []
    seen: set[str] = set()
    for line in output.splitlines():
        parts = line.split("|", 3)
        if len(parts) != 4:
            continue
        branch, commit, date, subject = parts
        key = f"{branch}:{commit}"
        if key in seen:
            continue
        seen.add(key)
        subject_l = subject.lower()
        score = sum(1 for term in IMPORTANT_TERMS if term in subject_l or term in branch.lower())
        rows.append(
            {
                "branch": redact(branch),
                "commit": commit,
                "date": date,
                "subject": redact(subject),
                "recovery_relevance": score,
            }
        )
    rows.sort(key=lambda item: (-item["recovery_relevance"], item["branch"]))
    return rows


def reflog_rows(repo: Path) -> list[dict[str, Any]]:
    output = run_git(repo, ["reflog", "--date=iso", "--all", "-n", "120"], limit=30000)
    rows = []
    for line in output.splitlines():
        lowered = line.lower()
        if any(term in lowered for term in IMPORTANT_TERMS):
            rows.append({"entry": redact(line[:500])})
    return rows[:80]


def unmerged_commits(repo: Path, base_ref: str = "HEAD") -> list[dict[str, Any]]:
    refs = run_git(repo, ["for-each-ref", "--format=%(refname:short)", "refs/heads", "refs/remotes"], limit=50000).splitlines()
    rows = []
    for ref in refs:
        ref = ref.strip()
        if not ref or ref.endswith("/HEAD"):
            continue
        count = run_git(repo, ["rev-list", "--count", f"{base_ref}..{ref}"]).strip()
        if not count.isdigit() or int(count) == 0:
            continue
        subject = run_git(repo, ["log", "-1", "--format=%h|%ci|%s", ref]).strip()
        relevance = sum(1 for term in IMPORTANT_TERMS if term in ref.lower() or term in subject.lower())
        rows.append(
            {
                "_raw_ref": ref,
                "ref": redact(ref),
                "commits_not_in_current_head": int(count),
                "tip": redact(subject),
                "recovery_relevance": relevance,
            }
        )
    rows.sort(key=lambda item: (-item["recovery_relevance"], -item["commits_not_in_current_head"], item["ref"]))
    return rows[:120]


def bot_file_count(repo: Path, ref: str) -> int | None:
    output = run_git(repo, ["ls-tree", "-r", "--name-only", ref], limit=1000000)
    if "Not a valid object" in output or "unknown revision" in output:
        return None
    return sum(1 for line in output.splitlines() if line.endswith(".py") and ("bot" in line.lower() or "agent" in line.lower()))


def audit_repo(repo: Path) -> dict[str, Any]:
    current = run_git(repo, ["rev-parse", "--abbrev-ref", "HEAD"]).strip()
    head = run_git(repo, ["rev-parse", "--short", "HEAD"]).strip()
    remote = run_git(repo, ["remote", "-v"]).splitlines()
    branches = branch_rows(repo)
    unmerged = unmerged_commits(repo)
    current_bot_count = bot_file_count(repo, "HEAD")
    best_refs = []
    for row in unmerged[:20]:
        count = bot_file_count(repo, row["_raw_ref"])
        if count is not None:
            best_refs.append({"ref": row["ref"], "python_bot_agent_files": count})
    best_refs.sort(key=lambda item: -item["python_bot_agent_files"])
    clean_unmerged = [{key: value for key, value in row.items() if key != "_raw_ref"} for row in unmerged]
    return {
        "path": redact(repo.as_posix()),
        "current_branch": redact(current),
        "head": head,
        "remotes": [redact(line) for line in remote],
        "branch_count": len(branches),
        "current_python_bot_agent_files": current_bot_count,
        "highest_bot_file_refs": best_refs[:10],
        "relevant_branches": branches[:80],
        "unmerged_relevant_refs": clean_unmerged,
        "reflog_recovery_hints": reflog_rows(repo),
    }


def build_payload() -> dict[str, Any]:
    repos = find_git_repos()
    audits = [audit_repo(repo) for repo in repos]
    return {
        "schema": "dreamco.buddy_git_recovery_audit.v1",
        "generated_at": utc_now(),
        "mission": "Find local branches, reflog entries, and clone histories that may contain missing DreamCo bot/code work.",
        "policy": {
            "non_destructive": True,
            "merge_rule": "Never merge or reset automatically. Compare candidate refs first, then cherry-pick or copy only reviewed files.",
            "recovery_order": [
                "current recovery branch",
                "local branches",
                "remote tracking branches",
                "reflog entries",
                "other local clones",
                "manual archives or exported folders",
            ],
        },
        "summary": {
            "git_repositories_found": len(audits),
            "total_branches_seen": sum(item["branch_count"] for item in audits),
            "repositories_with_unmerged_refs": sum(1 for item in audits if item["unmerged_relevant_refs"]),
        },
        "repositories": audits,
    }


def write_report(payload: dict[str, Any]) -> None:
    lines = [
        "# Buddy Git Recovery Audit",
        "",
        "This is a non-destructive recovery map. It shows where recoverable branches, commits, and reflog hints still exist locally or as remote-tracking refs.",
        "",
        "## Summary",
        "",
        f"- Git repositories found: {payload['summary']['git_repositories_found']}",
        f"- Branches/refs seen: {payload['summary']['total_branches_seen']}",
        f"- Repositories with unmerged refs: {payload['summary']['repositories_with_unmerged_refs']}",
        "",
    ]
    for repo in payload["repositories"]:
        lines.extend(
            [
                f"## {repo['path']}",
                "",
                f"- Current branch: `{repo['current_branch']}`",
                f"- Head: `{repo['head']}`",
                f"- Current Python bot/agent files: `{repo['current_python_bot_agent_files']}`",
                f"- Branches/refs seen: `{repo['branch_count']}`",
                "",
                "### Highest Bot File Candidate Refs",
                "",
            ]
        )
        if repo["highest_bot_file_refs"]:
            for ref in repo["highest_bot_file_refs"]:
                lines.append(f"- `{ref['ref']}`: {ref['python_bot_agent_files']} Python bot/agent files")
        else:
            lines.append("- No extra candidate refs found.")
        lines.extend(["", "### Unmerged Candidate Refs", ""])
        if repo["unmerged_relevant_refs"]:
            for ref in repo["unmerged_relevant_refs"][:25]:
                lines.append(f"- `{ref['ref']}`: {ref['commits_not_in_current_head']} commits ahead, tip `{ref['tip']}`")
        else:
            lines.append("- No unmerged candidate refs detected from current HEAD.")
        lines.append("")
    while lines and lines[-1] == "":
        lines.pop()
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Buddy Git recovery audit.")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        if not AUDIT_JSON.exists() or not REPORT_MD.exists():
            raise SystemExit("Git recovery audit files are missing. Run without --check.")
        payload = json.loads(AUDIT_JSON.read_text(encoding="utf-8"))
        assert payload["summary"]["git_repositories_found"] >= 1
        print(json.dumps({"ok": True, **payload["summary"]}, indent=2, sort_keys=True))
        return 0
    AUDIT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    payload = build_payload()
    AUDIT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(payload)
    print(json.dumps({"ok": True, **payload["summary"]}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
