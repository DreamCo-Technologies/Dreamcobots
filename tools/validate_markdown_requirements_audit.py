#!/usr/bin/env python3
"""Validate per-file Markdown audit checklists against tracked repository files."""
from __future__ import annotations
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "config/markdown-requirements-audit.json"
PAGES = ROOT / "website/data/markdown-requirements-audit.json"
VALID_STATES = {"pending", "in_progress", "complete", "blocked"}
AUDIT_STATES = {"not_started", "in_progress", "completed", "blocked"}

def fail(message: str) -> None:
    raise SystemExit(f"Markdown requirements audit: FAIL: {message}")

def main() -> int:
    try:
        manifest = json.loads(SOURCE.read_text(encoding="utf-8"))
        pages = json.loads(PAGES.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"could not parse source or Pages JSON: {exc}")
    if manifest != pages:
        fail("website/data copy is not byte-for-byte equivalent to config source after JSON parsing")
    if manifest.get("schema") != "dreamco.markdown_requirements_audit.v1":
        fail("unexpected schema")
    criteria = manifest.get("criteria", [])
    criteria_ids = [item.get("id") for item in criteria]
    if not criteria_ids or len(criteria_ids) != len(set(criteria_ids)):
        fail("criteria IDs must be present and unique")
    try:
        tracked = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode().split("\0")
    except Exception as exc:
        fail(f"git ls-files failed: {exc}")
    expected = {path for path in tracked if path.lower().endswith(".md")}
    items = manifest.get("items", [])
    paths = [item.get("path") for item in items]
    if len(paths) != len(set(paths)):
        fail("Markdown paths must be unique")
    actual = set(paths)
    if actual != expected:
        fail(f"inventory mismatch: missing={sorted(expected-actual)[:12]} extra={sorted(actual-expected)[:12]}")
    evidence_states = {"pending", "in_progress", "complete", "blocked"}
    for item in items:
        if item.get("audit_state") not in AUDIT_STATES:
            fail(f"{item.get('path')} has invalid audit_state")
        checks = item.get("checklist", {})
        if set(checks) != set(criteria_ids):
            fail(f"{item.get('path')} checklist does not match current criteria")
        if any(value not in evidence_states for value in checks.values()):
            fail(f"{item.get('path')} has an invalid checklist value")
        if any(value == "complete" for value in checks.values()) and not item.get("evidence"):
            fail(f"{item.get('path')} has completed checks without evidence")
        if item.get("audit_state") == "completed":
            if not all(value == "complete" for value in checks.values()):
                fail(f"{item.get('path')} marked completed with unfinished checks")
            if not item.get("reviewer") or not item.get("reviewed_at"):
                fail(f"{item.get('path')} completed without reviewer and review date")
    counts = {"markdown_files": len(items), "completed": 0, "in_progress": 0, "not_started": 0, "blocked": 0}
    for item in items:
        counts[item["audit_state"]] += 1
    if manifest.get("counts") != counts:
        fail(f"summary counts are stale: expected {counts}")
    print(f"Markdown requirements audit: PASS ({len(items)} files; {counts['not_started']} not started)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
