"""Daily approval list from commits, open pull requests, and open issues.

Approve only safe, small, non-draft pull requests. Actions-failure issues are
watch items. A listed approval is a recommendation, not a merge.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "DAILY_APPROVAL_LIST.md"
BLOCKED = {9575, 469, 8701, 8702, 3682, 467, 8847, 5123, 12441}


def _run(args: list[str]) -> str:
    try:
        return subprocess.check_output(args, cwd=ROOT, text=True, stderr=subprocess.DEVNULL)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""


def build() -> dict:
    commits = [line for line in _run(["git", "log", "--oneline", "-30"]).splitlines() if line]
    prs = json.loads(_run(["gh", "pr", "list", "--state", "open", "--limit", "40", "--json", "number,title,isDraft"]) or "[]")
    issues = json.loads(_run(["gh", "issue", "list", "--state", "open", "--limit", "40", "--json", "number,title"]) or "[]")
    approve = [pr for pr in prs if not pr.get("isDraft") and pr["number"] not in BLOCKED and "Career pathways" not in pr["title"]]
    hold = [pr for pr in prs if pr not in approve]
    watch = [issue for issue in issues if issue["title"].startswith("Actions run")]
    return {"commits": commits, "approve": approve, "hold": hold, "watch": watch}


def render(report: dict) -> str:
    lines = ["# Daily approval list", "", "Recommendations only. Nothing here is merged.", ""]
    lines.append("## Recent commits")
    lines.extend(f"- {row}" for row in report["commits"][:15])
    lines.extend(["", "## Consider"])
    lines.extend(f"- #{row['number']} {row['title']}" for row in report["approve"][:20])
    if not report["approve"]:
        lines.append("- none")
    lines.extend(["", "## Hold"])
    lines.extend(f"- #{row['number']} {row['title']}" for row in report["hold"][:20])
    if not report["hold"]:
        lines.append("- none")
    lines.extend(["", "## Issue watch"])
    lines.append(f"- {len(report['watch'])} Actions failure issues. Do not treat these as product approvals.")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    report = build()
    text = render(report)
    if args.write:
        OUT.write_text(text, encoding="utf-8")
    print(json.dumps({"commits": len(report["commits"]), "approve": len(report["approve"]), "hold": len(report["hold"]), "watch": len(report["watch"])}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
