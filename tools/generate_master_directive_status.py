#!/usr/bin/env python3
"""Turn the owner directive into an evidence-limited command-center backlog."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIRECTIVE = ROOT / "docs" / "DREAMCO_BUDDY_MASTER_CODEX_DIRECTIVE.md"
OUT = ROOT / "website" / "data" / "master-directive-status.json"

STATUS_ORDER = (
    "catalogued",
    "implemented",
    "sandbox_verified",
    "benchmark_verified",
    "regression_verified",
    "production_verified",
)
HEADING = re.compile(r"^# (\d+)\.\s+(.+?)\s*$", re.MULTILINE)
HIGH_PRIORITY = {
    4, 5, 6, 7, 8, 9, 10, 55, 56, 57, 60, 61, 124, 245, 246, 248,
    249, 257, 258, 260, 262, 264, 267, 268, 269, 310, 311,
}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def repository_inventory() -> dict[str, object]:
    ignored = {".git", "node_modules", "dist", ".venv", "__pycache__"}
    files = [
        p for p in ROOT.rglob("*")
        if p.is_file() and p != OUT and not ignored.intersection(p.parts)
    ]
    suffixes = Counter(p.suffix.lower() or "[none]" for p in files)
    return {
        "files_scanned": len(files),
        "python_files": suffixes[".py"],
        "javascript_files": suffixes[".js"] + suffixes[".mjs"] + suffixes[".cjs"],
        "typescript_files": suffixes[".ts"] + suffixes[".tsx"],
        "html_files": suffixes[".html"],
        "markdown_files": suffixes[".md"],
        "workflow_files": len(list((ROOT / ".github" / "workflows").glob("*.yml"))),
        "test_files": sum(1 for p in files if "tests" in p.parts),
        "public_pages": len(list((ROOT / "website").glob("*.html"))),
        "top_level_directories": sorted(p.name for p in ROOT.iterdir() if p.is_dir() and not p.name.startswith(".")),
    }


def evidence_for(section: int) -> list[str]:
    mapping = {
        4: ["tools/generate_master_directive_status.py", "website/data/master-directive-status.json"],
        5: ["website/data/master-directive-status.json"],
        6: ["website/master-build.html", "website/master-build.js"],
        7: ["website/master-build.html", ".github/workflows/deploy-buddy-pages.yml"],
        8: ["tests/master-directive-status.test.mjs"],
        243: ["website/master-build.html"],
        245: ["tools/generate_master_directive_status.py"],
        249: ["website/master-build.html", "tests/master-directive-status.test.mjs"],
        257: ["docs/DREAMCO_BUDDY_MASTER_CODEX_DIRECTIVE.md"],
        258: ["website/data/master-directive-status.json"],
        260: ["website/data/master-directive-status.json"],
        268: ["tools/generate_master_directive_status.py", "tests/master-directive-status.test.mjs"],
        310: ["website/master-build.html"],
        311: ["website/master-build.html", "website/data/master-directive-status.json"],
    }
    return [item for item in mapping.get(section, []) if (ROOT / item).exists()]


def build() -> dict[str, object]:
    text = DIRECTIVE.read_text(encoding="utf-8")
    matches = list(HEADING.finditer(text))
    items = []
    for index, match in enumerate(matches):
        section = int(match.group(1))
        title = match.group(2).strip().replace("\u00a0", " ")
        body_end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[match.end():body_end]
        evidence = evidence_for(section)
        status = "implemented" if evidence else "catalogued"
        items.append({
            "id": f"directive-{section:03d}",
            "section": section,
            "title": title,
            "priority": "critical" if section in HIGH_PRIORITY else ("high" if section <= 65 else "normal"),
            "status": status,
            "evidence_refs": evidence,
            "acceptance_excerpt": " ".join(line.strip(" -") for line in body.splitlines() if line.strip())[:280],
            "next_status": STATUS_ORDER[STATUS_ORDER.index(status) + 1] if status != STATUS_ORDER[-1] else None,
        })
    counts = Counter(item["status"] for item in items)
    return {
        "schema": "dreamco.master_directive_status.v1",
        "source": rel(DIRECTIVE),
        "source_sha256": hashlib.sha256(DIRECTIVE.read_bytes()).hexdigest(),
        "repository": "DreamCo-Technologies/Dreamcobots",
        "default_branch": "main",
        "evidence_taxonomy": list(STATUS_ORDER),
        "summary": {
            "directive_sections": len(items),
            "status_counts": {status: counts.get(status, 0) for status in STATUS_ORDER},
            "critical_items": sum(item["priority"] == "critical" for item in items),
            "truth": "Statuses describe only evidence committed in this repository. Catalogued is not implemented; implemented is not runtime, benchmark, regression, or production verification.",
        },
        "repository_audit": repository_inventory(),
        "items": items,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.check:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != rendered:
            print(f"stale generated artifact: {rel(OUT)}")
            return 1
    else:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(rendered, encoding="utf-8")
    print(json.dumps({"ok": True, "sections": len(payload["items"]), "output": rel(OUT)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
