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

    if not re.search(r'<script[^>]+src=["\'][^"\']*actions\.js', html, re.I):
        errors.append("actions.html does not load actions.js")
    if "id=\"actionsRoot\"" not in html and "id='actionsRoot'" not in html:
        warnings.append("actionsRoot host was not found; page may use another mount point")
    if "api.github.com" not in js:
        warnings.append("GitHub Actions API endpoint is not present in actions.js")
    if "Authorization" in js and "Bearer" in js:
        errors.append("actions.js appears to contain a client-side authorization header")
    if re.search(r"ghp_[A-Za-z0-9_]+|github_pat_[A-Za-z0-9_]+", js):
        errors.append("possible GitHub token embedded in actions.js")
    for required in ("refreshRuns", "renderRunCard", "renderWorkflowCard", "initialize"):
        if required not in js:
            errors.append(f"missing expected Actions runtime function: {required}")

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
