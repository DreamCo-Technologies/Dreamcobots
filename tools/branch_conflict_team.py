#!/usr/bin/env python3
"""Conflict team: update-from-main, or merge main into a resolution branch.

Never force-pushes. Never merges to main. Skips money/Stripe PRs.
Max 5 resolution attempts per run.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request

OWNER = os.environ.get("GITHUB_REPOSITORY_OWNER", "DreamCo-Technologies")
REPO = os.environ.get("GITHUB_REPOSITORY", "DreamCo-Technologies/Dreamcobots").split("/")[-1]
API = "https://api.github.com"
TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
DEFAULT = "main"
MAX_ATTEMPTS = int(os.environ.get("CONFLICT_TEAM_LIMIT", "5"))
MONEY_RE = re.compile(r"stripe|payment|money os|dreampayments|payout", re.I)
PROTECTED_MAIN = {
    "website/buddy.html",
    "website/index.html",
    "website/wiring.html",
    "website/desks.css",
    "website/nav.js",
}


def gh(path: str, method: str = "GET", body: dict | None = None) -> object:
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(API + path, data=data, method=method)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    req.add_header("User-Agent", "dreamco-conflict-team")
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    if body is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=60) as res:
            raw = res.read().decode()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode()[:400]
        raise RuntimeError(f"GitHub {exc.code} {path}: {detail}") from exc


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=check, text=True, capture_output=True)


def dirty_prs() -> list[dict]:
    out = []
    for page in range(1, 6):
        chunk = gh(f"/repos/{OWNER}/{REPO}/pulls?state=open&per_page=100&page={page}")
        if not isinstance(chunk, list) or not chunk:
            break
        for pr in chunk:
            full = gh(f"/repos/{OWNER}/{REPO}/pulls/{pr['number']}")
            if full.get("mergeable_state") == "dirty":
                out.append(full)
        if len(chunk) < 100:
            break
    return out


def try_update(number: int) -> str:
    try:
        gh(f"/repos/{OWNER}/{REPO}/pulls/{number}/update-branch", method="PUT")
        return "updated"
    except RuntimeError as exc:
        if "409" in str(exc) or "422" in str(exc) or "merge conflict" in str(exc).lower():
            return "conflict"
        return f"error:{exc}"


def conflicted_files() -> list[str]:
    proc = run(["git", "diff", "--name-only", "--diff-filter=U"], check=False)
    return [ln.strip() for ln in proc.stdout.splitlines() if ln.strip()]


def resolve_local(pr: dict) -> tuple[bool, str]:
    """Merge main into a copy of the PR branch. Prefer main for original Buddy files."""
    number = pr["number"]
    head = pr["head"]["ref"]
    sha = pr["head"]["sha"]
    files = gh(f"/repos/{OWNER}/{REPO}/pulls/{number}/files?per_page=100")
    pr_paths = {f["filename"] for f in files} if isinstance(files, list) else set()

    branch = f"dreamco/conflict-resolve/{number}"
    run(["git", "fetch", "origin", DEFAULT, f"+refs/heads/{head}:refs/remotes/origin/{head}"], check=False)
    run(["git", "checkout", "-B", branch, sha])
    merge = run(["git", "merge", f"origin/{DEFAULT}", "--no-edit"], check=False)
    if merge.returncode == 0:
        run(["git", "push", "-u", "origin", branch])
        return True, "Merged main with no remaining conflicts."

    leftover = []
    for path in conflicted_files():
        if path in PROTECTED_MAIN:
            run(["git", "checkout", "--theirs", "--", path], check=False)
            run(["git", "add", "--", path], check=False)
        elif path in pr_paths:
            run(["git", "checkout", "--ours", "--", path], check=False)
            run(["git", "add", "--", path], check=False)
        else:
            run(["git", "checkout", "--theirs", "--", path], check=False)
            run(["git", "add", "--", path], check=False)
        leftover = conflicted_files()
        if len(leftover) > 12:
            run(["git", "merge", "--abort"], check=False)
            return False, f"Too many remaining conflicts ({len(leftover)})."

    leftover = conflicted_files()
    if leftover:
        run(["git", "merge", "--abort"], check=False)
        return False, "Still conflicted: " + ", ".join(leftover[:12])

    run(["git", "commit", "--no-edit"], check=False)
    run(["git", "push", "-u", "origin", branch])
    return True, "Resolved with Buddy-home-from-main, PR-unique files kept."


def open_resolution_pr(pr: dict, detail: str) -> None:
    number = pr["number"]
    title = f"Conflict team: resolve #{number} against main"
    body = (
        f"Prepared by the Buddy conflict team for #{number}.\n\n"
        f"{detail}\n\n"
        "This branch is `main` merged into a copy of the original PR head.\n"
        "Original Buddy chat (`website/buddy.html`) is taken from main when it conflicted.\n"
        "Does **not** auto-merge. Review, then merge this or the original PR."
    )
    try:
        created = gh(
            f"/repos/{OWNER}/{REPO}/pulls",
            method="POST",
            body={
                "title": title,
                "head": f"dreamco/conflict-resolve/{number}",
                "base": DEFAULT,
                "body": body,
            },
        )
        url = created.get("html_url", "")
        gh(
            f"/repos/{OWNER}/{REPO}/issues/{number}/comments",
            method="POST",
            body={"body": f"Conflict team prepared a resolution PR: {url}. It does not merge itself."},
        )
    except RuntimeError as exc:
        print(f"open PR skip #{number}: {exc}", file=sys.stderr)


def main() -> int:
    if not TOKEN:
        print("No GITHUB_TOKEN; conflict team cannot write.", file=sys.stderr)
        return 0
    start_ref = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], check=False).stdout.strip() or DEFAULT
    queue = dirty_prs()
    print(f"dirty PRs: {len(queue)}")
    attempts = 0
    actions = []
    try:
        for pr in queue:
            title = pr.get("title") or ""
            number = pr["number"]
            if MONEY_RE.search(title):
                actions.append({"pr": number, "action": "skipped_money"})
                continue
            if attempts >= MAX_ATTEMPTS:
                actions.append({"pr": number, "action": "deferred"})
                continue
            attempts += 1
            status = try_update(number)
            if status == "updated":
                gh(
                    f"/repos/{OWNER}/{REPO}/issues/{number}/comments",
                    method="POST",
                    body={"body": "Conflict team updated this branch from main (no remaining GitHub-reported conflict)."},
                )
                actions.append({"pr": number, "action": "updated"})
                continue
            ok, detail = resolve_local(pr)
            if ok:
                open_resolution_pr(pr, detail)
                actions.append({"pr": number, "action": "resolution_pr", "detail": detail})
            else:
                gh(
                    f"/repos/{OWNER}/{REPO}/issues/{number}/comments",
                    method="POST",
                    body={"body": f"Conflict team could not auto-resolve: {detail}"},
                )
                actions.append({"pr": number, "action": "needs_human", "detail": detail})
    finally:
        run(["git", "merge", "--abort"], check=False)
        run(["git", "checkout", "-f", start_ref], check=False)
    os.makedirs("reports", exist_ok=True)
    with open("reports/conflict-team-last.json", "w", encoding="utf-8") as fh:
        json.dump({"actions": actions}, fh, indent=2)
    print(json.dumps(actions, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
