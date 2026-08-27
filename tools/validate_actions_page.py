#!/usr/bin/env python3
"""Static contract checks for DreamCo's Actions control-room page."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "website" / "actions.html"
JS = ROOT / "website" / "actions.js"


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    html = HTML.read_text(encoding="utf-8")
    js = JS.read_text(encoding="utf-8")

    # HTML/JS contract: these are the actual runtime entry points used by the
    # current Actions page. Keep this validator coupled to the public contract,
    # not to obsolete function names from an earlier implementation.
    if not re.search(r'<script[^>]+src=["\'][^"\']*actions\.js', html, re.I):
        errors.append("actions.html does not load actions.js")
    if 'id="workflow-list"' not in html and "id='workflow-list'" not in html:
        errors.append("workflow-list host was not found")
    if 'id="actions-control-cards"' not in html and "id='actions-control-cards'" not in html:
        errors.append("actions-control-cards host was not found")
    if "api.github.com" not in js:
        warnings.append("GitHub Actions API endpoint is not present in actions.js")
    if "Authorization" in js and "Bearer" in js:
        errors.append("actions.js appears to contain a client-side authorization header")
    if re.search(r"ghp_[A-Za-z0-9_]+|github_pat_[A-Za-z0-9_]+", js):
        errors.append("possible GitHub token embedded in actions.js")

    for required in (
        "latestEvidence",
        "renderProspectusCards",
        "showDetail",
        "render",
        "refreshRuns",
        "setupLocalCommands",
        "initialize",
    ):
        if not re.search(rf"function\s+{re.escape(required)}\s*\(", js):
            errors.append(f"missing expected Actions runtime function: {required}")

    for required_id in (
        "actions-search",
        "actions-status-filter",
        "actions-trigger-filter",
        "refresh-actions",
        "workflow-detail",
        "close-workflow-detail",
    ):
        if required_id not in html:
            errors.append(f"missing Actions page control: {required_id}")

    # The page must keep execution behind the trusted local/remote boundary.
    if "does not execute arbitrary shell commands" not in js:
        errors.append("local command UI is missing its browser execution safety boundary")

    print("Actions page diagnostics")
    print(f"HTML: {HTML}")
    print(f"JS:   {JS}")
    print(f"errors={len(errors)} warnings={len(warnings)}")
    for item in errors:
        print(f"ERROR: {item}")
    for item in warnings:
        print(f"WARN:  {item}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
