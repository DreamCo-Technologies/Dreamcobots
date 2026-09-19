#!/usr/bin/env python3
"""Scan every branch and open PR. Write a public-safe daily health report.

Does not merge to main. Does not print secrets.
"""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

OWNER = os.environ.get("GITHUB_REPOSITORY_OWNER", "DreamCo-Technologies")
REPO = os.environ.get("GITHUB_REPOSITORY", "DreamCo-Technologies/Dreamcobots").split("/")[-1]
API = "https://api.github.com"
TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
DEFAULT = "main"
REQUIRED = [
    "website/buddy.html",
    "website/index.html",
    "website/nav.js",
    "website/connections.html",
    "website/wiring.html",
    "website/desks.css",
    ".github/workflows/pages.yml",
    "AGENTS.md",
    "README.md",
]
MONEY_RE = re.compile(r"stripe|payment|money os|dreampayments|payout", re.I)


def gh(path: str, method: str = "GET", body: dict | None = None) -> object:
    url = API + path
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    req.add_header("User-Agent", "dreamco-branch-health")
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    if body is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=60) as res:
            raw = res.read().decode()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode()[:300]
        raise RuntimeError(f"GitHub {exc.code} {path}: {detail}") from exc


def gh_pages(path: str) -> list:
    out = []
    for page in range(1, 8):
        sep = "&" if "?" in path else "?"
        chunk = gh(f"{path}{sep}per_page=100&page={page}")
        if not isinstance(chunk, list):
            break
        out.extend(chunk)
        if len(chunk) < 100:
            break
    return out


def vote_freshness(behind: int) -> tuple[str, str]:
    if behind == 0:
        return "pass", "Caught up with main."
    if behind < 40:
        return "warn", f"{behind} commits behind main."
    return "block", f"{behind} commits behind main."


def vote_complete(missing: list[str]) -> tuple[str, str]:
    if not missing:
        return "pass", "Required Buddy files present vs main."
    if len(missing) <= 2:
        return "warn", "Missing " + ", ".join(missing)
    return "block", f"Missing {len(missing)} required files."


def vote_merge(pr: dict | None) -> tuple[str, str]:
    if not pr:
        return "warn", "No open pull request."
    state = pr.get("mergeable_state") or "unknown"
    if state == "dirty":
        return "block", "Conflicts with main. Conflict team required."
    if state == "clean":
        return "pass", "PR mergeable_state=clean."
    return "warn", f"PR mergeable_state={state}."


def score_votes(votes: list[dict]) -> tuple[int, str]:
    score = 100
    status = "healthy"
    for v in votes:
        if v["vote"] == "warn":
            score -= 10
            status = "watch" if status == "healthy" else status
        if v["vote"] == "block":
            score -= 22
            status = "blocked"
    return max(0, score), status


def review(behind: int, missing: list[str], pr: dict | None) -> tuple[list[dict], int, str]:
    votes = []
    f_v, f_n = vote_freshness(behind)
    votes.append({"reviewer": "freshness", "vote": f_v, "note": f_n})
    c_v, c_n = vote_complete(missing)
    votes.append({"reviewer": "completeness", "vote": c_v, "note": c_n})
    m_v, m_n = vote_merge(pr)
    votes.append({"reviewer": "merge", "vote": m_v, "note": m_n})
    title = (pr or {}).get("title") or ""
    if MONEY_RE.search(title):
        votes.append({"reviewer": "safety", "vote": "block", "note": "Money/Stripe path. No auto-edit."})
    else:
        votes.append({"reviewer": "safety", "vote": "pass", "note": "No payment-surface auto-edit."})
    if "website/buddy.html" in missing:
        votes.append({"reviewer": "scope", "vote": "block", "note": "Would drop original Buddy chat."})
    elif "website/wiring.html" in missing:
        votes.append({"reviewer": "scope", "vote": "warn", "note": "Predates the wiring map."})
    else:
        votes.append({"reviewer": "scope", "vote": "pass", "note": "Original Buddy home is intact."})
    score, status = score_votes(votes)
    return votes, score, status


def missing_from(files: list | None) -> list[str]:
    added = {f.get("filename") for f in files or [] if f.get("status") in ("added", "renamed")}
    return [p for p in REQUIRED if p in added]


def markdown_report(report: dict) -> str:
    lines = [
        f"# Daily branch health — {report['scannedAt'][:10]}",
        "",
        f"Branches **{report['branchCount']}** · open PRs **{report['prOpen']}** · healthy **{report['healthy']}** · watch **{report['watch']}** · blocked **{report['blocked']}** · conflicts **{report['dirty']}**.",
        "",
        "Review team: Freshness, Completeness, Mergeability, Safety, Scope.",
        "Conflict team never force-merges `main` and skips money/Stripe PRs.",
        "",
        "| Branch | Score | Status | Ahead | Behind | PR | Missing |",
        "|---|---:|---|---:|---:|---|---|",
    ]
    for b in report["branches"][:80]:
        missing = ", ".join(b["missingRequired"]) or "—"
        pr = f"#{b['prNumber']}" if b.get("prNumber") else "—"
        lines.append(
            f"| `{b['name']}` | {b['score']} | {b['status']} | {b['ahead']} | {b['behind']} | {pr} | {missing} |"
        )
    if report.get("conflictActions"):
        lines += ["", "## Conflict queue", ""]
        for c in report["conflictActions"]:
            lines.append(f"- #{c['prNumber']} {c['title']} — `{c['action']}`: {c['detail']}")
    lines += ["", report.get("note", "")]
    return "\n".join(lines) + "\n"


def upsert_issue(body: str, title: str = "Daily branch health") -> None:
    found = gh(
        "/search/issues?q="
        + urllib.parse.quote(f"repo:{OWNER}/{REPO} is:issue is:open in:title Daily branch health")
    )
    items = found.get("items") if isinstance(found, dict) else []
    existing = next((i for i in items or [] if i.get("title") == title), None)
    if existing:
        gh(f"/repos/{OWNER}/{REPO}/issues/{existing['number']}", method="PATCH", body={"body": body})
        return
    gh(f"/repos/{OWNER}/{REPO}/issues", method="POST", body={"title": title, "body": body})


def main() -> int:
    branches = gh_pages(f"/repos/{OWNER}/{REPO}/branches")
    prs = gh_pages(f"/repos/{OWNER}/{REPO}/pulls?state=open")
    pr_by_ref = {}
    for pr in prs:
        try:
            full = gh(f"/repos/{OWNER}/{REPO}/pulls/{pr['number']}")
        except RuntimeError:
            full = pr
        pr_by_ref[full["head"]["ref"]] = full

    records = []
    conflicts = []
    for br in branches:
        name = br["name"]
        if name == DEFAULT:
            continue
        pr = pr_by_ref.get(name)
        ahead = behind = 0
        missing: list[str] = []
        try:
            cmp = gh(
                f"/repos/{OWNER}/{REPO}/compare/{urllib.parse.quote(name, safe='')}...{DEFAULT}"
            )
            behind = int(cmp.get("ahead_by") or 0)
            ahead = int(cmp.get("behind_by") or 0)
            missing = missing_from(cmp.get("files") or [])
        except RuntimeError as exc:
            print(f"compare skip {name}: {exc}", file=sys.stderr)

        votes, score, status = review(behind, missing, pr)
        rec = {
            "name": name,
            "sha": br.get("commit", {}).get("sha", ""),
            "protected": bool(br.get("protected")),
            "updated": (pr or {}).get("updated_at"),
            "ahead": ahead,
            "behind": behind,
            "missingRequired": missing,
            "prNumber": (pr or {}).get("number"),
            "prTitle": (pr or {}).get("title"),
            "prUrl": (pr or {}).get("html_url"),
            "mergeable": (pr or {}).get("mergeable"),
            "mergeableState": (pr or {}).get("mergeable_state"),
            "moneySensitive": bool(MONEY_RE.search((pr or {}).get("title") or "")),
            "votes": votes,
            "score": score,
            "status": status,
        }
        records.append(rec)
        if pr and pr.get("mergeable_state") == "dirty":
            money = rec["moneySensitive"]
            conflicts.append(
                {
                    "prNumber": pr["number"],
                    "title": pr["title"],
                    "url": pr["html_url"],
                    "state": pr.get("mergeable_state"),
                    "action": "skipped_money" if money else "needs_human",
                    "detail": "Money path. No auto-edit."
                    if money
                    else "Conflicts. Conflict team may update-from-main or open a resolution PR.",
                }
            )

    records.sort(key=lambda r: (r["score"], r["name"]))
    report = {
        "scannedAt": datetime.now(timezone.utc).isoformat(),
        "owner": OWNER,
        "repo": REPO,
        "defaultBranch": DEFAULT,
        "branchCount": len(branches),
        "prOpen": len(prs),
        "dirty": len(conflicts),
        "healthy": sum(1 for r in records if r["status"] == "healthy"),
        "watch": sum(1 for r in records if r["status"] == "watch"),
        "blocked": sum(1 for r in records if r["status"] == "blocked"),
        "branches": records,
        "conflictActions": conflicts,
        "note": "Inventory is not mastery. Auto-merge to main is off.",
    }

    os.makedirs("reports", exist_ok=True)
    os.makedirs("website/data", exist_ok=True)
    with open("reports/branch-health-daily.json", "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)
    with open("website/data/branch-health.json", "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)
    md = markdown_report(report)
    with open("reports/branch-health-daily.md", "w", encoding="utf-8") as fh:
        fh.write(md)
    print(md)
    if os.environ.get("BRANCH_HEALTH_UPSERT_ISSUE") == "1":
        try:
            upsert_issue(md)
        except RuntimeError as exc:
            print(f"issue skip: {exc}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
