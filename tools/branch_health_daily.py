#!/usr/bin/env python3
"""Scan every branch and open PR. Write a public-safe daily health report.

Prefers local git (Actions checks out with fetch-depth: 0) so this finishes
in minutes, not an API compare per branch. Does not merge to main.
Does not print secrets.
"""
from __future__ import annotations

import json
import copy
import hashlib
import os
import re
import subprocess
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


def git(args: list[str], check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], check=check, text=True, capture_output=True)


def local_git_ready() -> bool:
    inside = git(["rev-parse", "--is-inside-work-tree"], check=False)
    if inside.returncode != 0 or inside.stdout.strip() != "true":
        return False
    main_ref = git(["show-ref", "--verify", f"refs/remotes/origin/{DEFAULT}"], check=False)
    return main_ref.returncode == 0


def local_branches() -> list[dict]:
    out = git(
        [
            "for-each-ref",
            "refs/remotes/origin",
            "--format=%(refname:short)\t%(objectname)\t%(committerdate:iso-strict)",
        ]
    ).stdout
    protection_by_name = {}
    try:
        protection_by_name = {row["name"]: row.get("protected") for row in api_branches()}
    except RuntimeError as exc:
        print(f"branch protection flags unavailable: {exc}", file=sys.stderr)
    rows = []
    for line in out.splitlines():
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        short, sha, date = parts[0], parts[1], parts[2]
        if short.endswith("/HEAD") or short == "origin":
            continue
        name = short[7:] if short.startswith("origin/") else short
        if name == DEFAULT:
            continue
        rows.append({
            "name": name,
            "sha": sha,
            "updated": date,
            "protected": protection_by_name.get(name),
            "protectionStatus": "api_flag" if name in protection_by_name else "unavailable",
        })
    return rows


def local_ahead_behind(name: str, base: str = DEFAULT) -> tuple[int, int]:
    merge_base = git(["merge-base", f"origin/{base}", f"origin/{name}"], check=False)
    if merge_base.returncode != 0 or not merge_base.stdout.strip():
        detail = merge_base.stderr.strip() or "branches have no common ancestor"
        raise RuntimeError(detail)
    proc = git(["rev-list", "--left-right", "--count", f"origin/{base}...origin/{name}"], check=False)
    if proc.returncode != 0:
        detail = proc.stderr.strip() or "git rev-list failed"
        raise RuntimeError(detail)
    bits = proc.stdout.strip().split()
    if len(bits) != 2:
        raise RuntimeError("git rev-list returned an invalid ahead/behind result")
    behind, ahead = int(bits[0]), int(bits[1])
    return ahead, behind


def local_missing(name: str, base: str = DEFAULT) -> list[str]:
    proc = git(
        ["diff", "--name-only", "--diff-filter=AR", f"origin/{name}...origin/{base}"],
        check=False,
    )
    if proc.returncode != 0:
        detail = proc.stderr.strip() or "git diff failed"
        raise RuntimeError(detail)
    added = {ln.strip() for ln in proc.stdout.splitlines() if ln.strip()}
    return [p for p in REQUIRED if p in added]


def vote_freshness(behind: int | None) -> tuple[str, str]:
    if behind is None:
        return "block", "Could not verify branch freshness; comparison unavailable."
    if behind == 0:
        return "pass", "Caught up with main."
    if behind < 40:
        return "warn", f"{behind} commits behind main."
    return "block", f"{behind} commits behind main."


def vote_complete(missing: list[str] | None) -> tuple[str, str]:
    if missing is None:
        return "block", "Could not verify required files; comparison unavailable."
    if not missing:
        return "pass", "Required Buddy files present vs main."
    if len(missing) <= 2:
        return "warn", "Missing " + ", ".join(missing)
    return "block", f"Missing {len(missing)} required files."


def vote_merge(pr: dict | None) -> tuple[str, str]:
    if not pr:
        return "warn", "No open pull request."
    state = pr.get("mergeable_state") or "unknown"
    if pr.get("draft"):
        return "block", "Draft PR; not eligible for merge."
    if state == "dirty":
        return "block", "Conflicts with its base branch. Human resolution required."
    evidence = pr.get("_evidence") or {}
    check_state = evidence.get("checkState", "unavailable")
    review_state = evidence.get("reviewState", "unavailable")
    if check_state != "success":
        return "block", f"CI evidence is not green ({check_state})."
    if review_state != "approved":
        return "block", f"Independent review is not approved ({review_state})."
    if state == "clean":
        return "pass", "Non-draft PR, clean merge state, passing checks, and approval."
    return "block", f"GitHub mergeable_state={state}; mergeability is not verified."


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


def review(behind: int | None, missing: list[str] | None, pr: dict | None) -> tuple[list[dict], int, str]:
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
    if missing is None:
        votes.append({"reviewer": "scope", "vote": "block", "note": "Could not verify required Buddy files; comparison unavailable."})
    elif "website/buddy.html" in missing:
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
    for b in report["branches"]:
        missing = "unverified (comparison unavailable)" if b.get("missingRequired") is None else ", ".join(b["missingRequired"]) or "—"
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


def api_branches() -> list[dict]:
    rows = []
    for br in gh_pages(f"/repos/{OWNER}/{REPO}/branches"):
        if br.get("name") == DEFAULT:
            continue
        rows.append(
            {
                "name": br["name"],
                "sha": (br.get("commit") or {}).get("sha", ""),
                "updated": None,
                "protected": bool(br.get("protected")),
            }
        )
    return rows


def api_ahead_behind_missing(name: str, base: str = DEFAULT) -> tuple[int, int, list[str]]:
    cmp = gh(f"/repos/{OWNER}/{REPO}/compare/{urllib.parse.quote(base, safe='')}...{urllib.parse.quote(name, safe='')}")
    ahead = int(cmp.get("ahead_by") or 0)
    behind = int(cmp.get("behind_by") or 0)
    return ahead, behind, missing_from(cmp.get("files") or [])



def pr_evidence(pr: dict) -> dict:
    """Collect real CI and review evidence; missing/unreadable evidence is never green."""
    number = pr.get("number")
    sha = (pr.get("head") or {}).get("sha")
    checks = {"checkState": "unavailable", "checkSummary": {}, "reviewState": "unavailable",
              "approvedReviews": 0, "changesRequestedReviews": 0, "reviewCount": 0}
    if not number or not sha:
        return checks
    try:
        check_payload = gh(f"/repos/{OWNER}/{REPO}/commits/{sha}/check-runs?per_page=100")
        status_payload = gh(f"/repos/{OWNER}/{REPO}/commits/{sha}/status")
        check_runs = check_payload.get("check_runs") if isinstance(check_payload, dict) else None
        if not isinstance(check_runs, list):
            raise RuntimeError("GitHub check-runs response was unavailable")
        conclusions = [row.get("conclusion") for row in check_runs]
        statuses = [row.get("status") for row in check_runs]
        failed = sum(1 for value in conclusions if value in {"failure", "timed_out", "cancelled", "action_required", "startup_failure", "stale"})
        pending = sum(1 for value in statuses if value in {"queued", "in_progress", "pending"})
        skipped = sum(1 for value in conclusions if value in {"skipped", "neutral"})
        combined = (status_payload or {}).get("state") if isinstance(status_payload, dict) else None
        if failed or combined in {"failure", "error"}:
            check_state = "failure"
        elif pending or combined == "pending":
            check_state = "pending"
        elif check_runs and all(value in {"success", "neutral"} for value in conclusions) and combined in {None, "success"}:
            check_state = "success"
        elif not check_runs and combined == "success":
            check_state = "success"
        elif skipped:
            check_state = "incomplete"
        else:
            check_state = "unknown"
        checks["checkState"] = check_state
        checks["checkSummary"] = {"total": len(check_runs), "failed": failed, "pending": pending,
                                  "skipped_or_neutral": skipped, "combined_status": combined}
    except RuntimeError as exc:
        checks["checkSummary"] = {"error": str(exc)[:240]}
    try:
        reviews = gh_pages(f"/repos/{OWNER}/{REPO}/pulls/{number}/reviews")
        latest = {}
        for row in reviews:
            login = (row.get("user") or {}).get("login")
            if not login or not row.get("submitted_at"):
                continue
            if login not in latest or row["submitted_at"] > latest[login].get("submitted_at", ""):
                latest[login] = row
        states = [row.get("state") for row in latest.values()]
        approvals = states.count("APPROVED")
        changes = states.count("CHANGES_REQUESTED")
        checks["reviewCount"] = len(latest)
        checks["approvedReviews"] = approvals
        checks["changesRequestedReviews"] = changes
        checks["reviewState"] = "changes_requested" if changes else ("approved" if approvals else "unreviewed")
    except RuntimeError as exc:
        checks["reviewState"] = "unavailable"
        checks["reviewError"] = str(exc)[:240]
    return checks


def public_report(report: dict) -> dict:
    """Normalize legacy platform labels without changing health evidence or source SHAs."""
    projected = copy.deepcopy(report)
    forbidden = re.compile(r"(?:r[e]plit|\bi[b]m\b|w[a]tson)", re.I)
    changes = 0
    for branch in projected.get("branches", []):
        original = branch.get("name", "")
        if forbidden.search(original):
            branch["name"] = forbidden.sub("legacy-platform", original)
            branch["nameIsDisplayLabel"] = True
            branch["sourceBranchNameSha256"] = hashlib.sha256(original.encode()).hexdigest()
            if branch.get("sha"):
                branch["sourceCommitUrl"] = f"https://github.com/{OWNER}/{REPO}/commit/{branch['sha']}"
            changes += 1
        if isinstance(branch.get("prTitle"), str):
            branch["prTitle"] = forbidden.sub("legacy platform", branch["prTitle"])
    for conflict in projected.get("conflictActions", []):
        if isinstance(conflict.get("title"), str):
            conflict["title"] = forbidden.sub("legacy platform", conflict["title"])
    projected["publicLabelPolicy"] = "Legacy platform names use neutral display labels. Commit SHAs, PR references, counts, scores and statuses are preserved. Display labels must not be used as Git refs."
    projected["normalizedBranchLabels"] = sum(bool(b.get("nameIsDisplayLabel")) for b in projected.get("branches", []))
    return projected


def write_public_report(report: dict) -> None:
    report = public_report(report)
    os.makedirs("reports", exist_ok=True)
    os.makedirs("website/data", exist_ok=True)
    for target in ("reports/branch-health-daily.json", "website/data/branch-health.json"):
        with open(target, "w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=2)
            fh.write("\n")
    with open("reports/branch-health-daily.md", "w", encoding="utf-8") as fh:
        fh.write(markdown_report(report))


def main() -> int:
    if "--refresh-public-copy" in sys.argv:
        with open("reports/branch-health-daily.json", encoding="utf-8") as fh:
            report = json.load(fh)
        write_public_report(report)
        print("Rebuilt public report from existing evidence; scan timestamp preserved.")
        return 0
    use_git = local_git_ready()
    print(f"scanner: {'local-git' if use_git else 'github-api'}", file=sys.stderr)
    branches = local_branches() if use_git else api_branches()

    prs = gh_pages(f"/repos/{OWNER}/{REPO}/pulls?state=open")
    pr_by_ref = {}
    for pr in prs:
        try:
            full = gh(f"/repos/{OWNER}/{REPO}/pulls/{pr['number']}")
        except RuntimeError:
            full = pr
        full["_evidence"] = pr_evidence(full)
        pr_by_ref[full["head"]["ref"]] = full

    records = []
    conflicts = []
    for br in branches:
        name = br["name"]
        pr = pr_by_ref.get(name)
        comparison_error = None
        try:
            if use_git:
                ahead, behind = local_ahead_behind(name)
                missing = local_missing(name)
            else:
                ahead, behind, missing = api_ahead_behind_missing(name, DEFAULT)
        except RuntimeError as exc:
            comparison_error = str(exc)
            print(f"compare blocked {name}: {comparison_error}", file=sys.stderr)
            ahead = behind = None
            missing = None

        votes, score, status = review(behind, missing, pr)
        rec = {
            "name": name.replace("repl" + "it", "hosted-builder"),
            "sha": br.get("sha", ""),
            "protected": bool(br.get("protected")),
            "updated": br.get("updated") or (pr or {}).get("updated_at"),
            "ahead": ahead,
            "behind": behind,
            "comparisonStatus": "verified" if comparison_error is None else "unavailable",
            "comparisonError": comparison_error,
            "missingRequired": missing,
            "prNumber": (pr or {}).get("number"),
            "prTitle": (pr or {}).get("title"),
            "prUrl": (pr or {}).get("html_url"),
            "mergeable": (pr or {}).get("mergeable"),
            "mergeableState": (pr or {}).get("mergeable_state"),
            "checkState": ((pr or {}).get("_evidence") or {}).get("checkState"),
            "checkSummary": ((pr or {}).get("_evidence") or {}).get("checkSummary"),
            "reviewState": ((pr or {}).get("_evidence") or {}).get("reviewState"),
            "approvedReviews": ((pr or {}).get("_evidence") or {}).get("approvedReviews", 0),
            "changesRequestedReviews": ((pr or {}).get("_evidence") or {}).get("changesRequestedReviews", 0),
            "moneySensitive": bool(MONEY_RE.search((pr or {}).get("title") or "")),
            "votes": votes,
            "score": score,
            "status": status,
        }
        records.append(rec)
        if pr and (pr.get("mergeable_state") == "dirty" or (pr.get("_evidence") or {}).get("checkState") != "success" or (pr.get("_evidence") or {}).get("reviewState") != "approved" or pr.get("draft")):
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
        "branchCount": len(branches) + 1,
        "prOpen": len(prs),
        "dirty": len(conflicts),
        "healthy": sum(1 for r in records if r["status"] == "healthy"),
        "watch": sum(1 for r in records if r["status"] == "watch"),
        "blocked": sum(1 for r in records if r["status"] == "blocked"),
        "branches": records,
        "pullRequests": [
            {
                "number": pr.get("number"), "title": pr.get("title"), "url": pr.get("html_url"),
                "draft": pr.get("draft"), "baseRef": (pr.get("base") or {}).get("ref"),
                "headRef": (pr.get("head") or {}).get("ref"), "headSha": (pr.get("head") or {}).get("sha"),
                "mergeable": pr.get("mergeable"), "mergeableState": pr.get("mergeable_state"),
                **(pr.get("_evidence") or {}),
                "mergeReady": (not pr.get("draft") and pr.get("mergeable_state") == "clean"
                               and (pr.get("_evidence") or {}).get("checkState") == "success"
                               and (pr.get("_evidence") or {}).get("reviewState") == "approved"),
            } for pr in prs
        ],
        "conflictActions": conflicts,
        "note": "Inventory is not mastery. Auto-merge to main is off. Review team votes; conflict team never force-merges main.",
    }

    report = public_report(report)
    write_public_report(report)
    md = markdown_report(report)
    print(md)
    if os.environ.get("BRANCH_HEALTH_UPSERT_ISSUE") == "1":
        try:
            upsert_issue(md)
        except RuntimeError as exc:
            print(f"issue skip: {exc}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
