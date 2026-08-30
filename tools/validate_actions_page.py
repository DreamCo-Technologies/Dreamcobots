#!/usr/bin/env python3
"""Static contract checks for DreamCo's Actions control-room page.

The validator intentionally checks the public page contract without making
network calls or requiring browser execution. It accepts both synchronous and
async JavaScript function declarations and reports every failed contract so CI
is actionable instead of failing on an opaque regex assumption.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "website" / "actions.html"
JS = ROOT / "website" / "actions.js"

REQUIRED_FUNCTIONS = (
    "latestEvidence",
    "renderProspectusCards",
    "showDetail",
    "render",
    "refreshRuns",
    "setupLocalCommands",
    "initialize",
)

REQUIRED_IDS = (
    "actions-search",
    "actions-status-filter",
    "actions-trigger-filter",
    "refresh-actions",
    "workflow-detail",
    "close-workflow-detail",
)


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    if not HTML.is_file():
        errors.append(f"missing Actions page: {HTML}")
    if not JS.is_file():
        errors.append(f"missing Actions runtime: {JS}")
    if errors:
        print("Actions page diagnostics")
        for item in errors:
            print(f"ERROR: {item}")
        return 1

    html = HTML.read_text(encoding="utf-8")
    js = JS.read_text(encoding="utf-8")

    # Match script tags by attribute order/whitespace rather than assuming a
    # particular formatting style.
    script_sources = re.findall(r"<script\b[^>]*\bsrc\s*=\s*['\"]([^'\"]+)['\"]", html, re.I)
    if not any(Path(src.split("?", 1)[0]).name == "actions.js" for src in script_sources):
        errors.append("actions.html does not load actions.js")

    for required_id in REQUIRED_IDS + ("workflow-list", "actions-control-cards"):
        if not re.search(rf"\bid\s*=\s*['\"]{re.escape(required_id)}['\"]", html):
            errors.append(f"missing Actions page control/host: {required_id}")

    if "https://api.github.com/" not in js:
        warnings.append("GitHub Actions API endpoint is not present in actions.js")

    # Never permit credentials in a public browser bundle.
    if re.search(r"\bAuthorization\s*:\s*['\"]?Bearer\b", js, re.I):
        errors.append("actions.js appears to contain a client-side bearer authorization header")
    if re.search(r"\b(?:ghp|github_pat)_[A-Za-z0-9_]+\b", js):
        errors.append("possible GitHub token embedded in actions.js")

    # Accept both `function name()` and `async function name()` declarations.
    for required in REQUIRED_FUNCTIONS:
        pattern = rf"\b(?:async\s+)?function\s+{re.escape(required)}\s*\("
        if not re.search(pattern, js):
            errors.append(f"missing expected Actions runtime function: {required}")

    # The browser surface must remain a read-only/trusted-boundary UI.
    safety_markers = (
        "does not execute arbitrary shell commands",
        "cannot execute arbitrary shell commands",
        "browser actions do not execute arbitrary shell commands",
    )
    if not any(marker in js for marker in safety_markers):
        errors.append("local command UI is missing its browser execution safety boundary")

    # Verify the runtime references every required DOM host before claiming the
    # page contract is complete. This catches accidental renames early.
    for required_id in REQUIRED_IDS:
        if f"byId('{required_id}')" not in js and f'byId("{required_id}")' not in js:
            warnings.append(f"runtime does not directly reference expected control: {required_id}")

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
