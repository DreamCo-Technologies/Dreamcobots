#!/usr/bin/env python3
"""Compare the repository with what the pages can honestly say."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKIP = {".git", "node_modules", "dist", "logs"}


def _plans() -> list[dict]:
    rows = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in SKIP for part in path.relative_to(ROOT).parts):
            continue
        name = path.name.lower()
        if "plan" not in name and "roadmap" not in name:
            continue
        if path.stat().st_size > 2_000_000:
            continue
        relative = path.relative_to(ROOT).as_posix()
        kind = "code" if path.suffix == ".py" and "def " in path.read_text(encoding="utf-8", errors="ignore") else "document"
        rows.append({"path": relative, "kind": kind, "folder": relative.split("/", 1)[0]})
    return sorted(rows, key=lambda row: row["path"])


def scan() -> dict:
    catalog = json.loads((ROOT / "website/data/original-bots.json").read_text(encoding="utf-8"))
    markdown = [path for path in (ROOT / "bots").glob("*.md") if path.is_file()]
    pages = [path.relative_to(ROOT / "website").as_posix() for path in (ROOT / "website").glob("*.html")]
    plans = _plans()
    spec = importlib.util.spec_from_file_location("plan_status_for_have", ROOT / "buddy/frontier/plan_status.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    phases = module.status()
    mismatches = []
    if catalog.get("count") != len(markdown):
        mismatches.append(
            f"The original-bot catalog lists {catalog.get('count')} bots. The bots folder has {len(markdown)} markdown files. Those are not the same set."
        )
    foundation = phases["phases"][0]["because"]
    if "13 gates" in foundation:
        mismatches.append("The frontier plan still says 13 gates.")
    claims = (ROOT / "website/timecapsule.html").read_text(encoding="utf-8")
    unverified = []
    if "monthly revenue" in claims:
        unverified.append("timecapsule.html states monthly revenue. This scan found no ledger for that number.")
    return {
        "markdown_bots": len(markdown),
        "catalog_bots": catalog.get("count"),
        "html_pages": len(pages),
        "plans": plans,
        "plan_documents": sum(1 for row in plans if row["kind"] == "document"),
        "plan_code": sum(1 for row in plans if row["kind"] == "code"),
        "mismatches": mismatches,
        "unverified_claims": unverified,
        "files_moved": False,
        "frontier_ready": False,
    }


if __name__ == "__main__":
    made = scan()
    assert made["markdown_bots"] > made["catalog_bots"]
    assert made["mismatches"]
    assert made["frontier_ready"] is False
    assert made["files_moved"] is False
    print(json.dumps({"markdown_bots": made["markdown_bots"], "catalog_bots": made["catalog_bots"], "plans": len(made["plans"]), "mismatches": len(made["mismatches"])}))
