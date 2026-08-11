#!/usr/bin/env python3
"""Generate a conservative repository inventory for Buddy Pages and Actions.

This is an evidence catalog, not a claim that every discovered file is runnable.
Generated outputs are safe, deterministic summaries and preserve source files.
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "website" / "data" / "repository-master-map.json"
GENERATED = ROOT / "config" / "generated" / "repository-master-map.json"
SKIP = {".git", "node_modules", "dist", "__pycache__", ".vercel", ".wrangler", "playwright-report", "test-results", "tmp", "logs"}


def kind(p: Path) -> str:
    s = p.as_posix()
    if s.startswith(".github/workflows/"): return "action"
    if s.startswith("website/"): return "pages_asset"
    if s.startswith("tests/") or ".test." in p.name or ".spec." in p.name or p.name.startswith("test_"): return "test"
    if s.startswith("tools/"): return "tool"
    if s.startswith("bots/") or s.startswith("App_bots/") or s.startswith("original-bots/"): return "bot"
    if s.startswith("config/"): return "config"
    if s.startswith("server/"): return "backend"
    if s.startswith("client/"): return "frontend"
    if s.startswith("shared/"): return "shared_contract"
    if s.startswith("dreamco_platform/"): return "platform"
    if s.startswith("docs/") or p.suffix.lower() == ".md": return "documentation"
    return "repository_file"


def suite(k: str) -> str:
    return {
        "action": "actions",
        "pages_asset": "github-pages",
        "test": "benchmarks-and-tests",
        "tool": "tools",
        "bot": "bot-fleet",
        "backend": "backend",
        "frontend": "frontend",
        "shared_contract": "shared-contracts",
        "platform": "platform",
        "config": "configuration",
        "documentation": "documentation",
        "repository_file": "repository",
    }[k]


def main() -> None:
    rows = []
    for p in sorted(ROOT.rglob("*")):
        if not p.is_file() or any(part in SKIP for part in p.relative_to(ROOT).parts):
            continue
        rel = p.relative_to(ROOT).as_posix()
        k = kind(p)
        rows.append({"path": rel, "kind": k, "suite": suite(k), "bytes": p.stat().st_size})
    counts = Counter(r["kind"] for r in rows)
    workflow_paths = [r["path"] for r in rows if r["kind"] == "action"]
    page_paths = [r["path"] for r in rows if r["kind"] == "pages_asset"]
    test_paths = [r["path"] for r in rows if r["kind"] == "test"]
    digest = hashlib.sha256("\n".join(f"{r['path']}:{r['bytes']}" for r in rows).encode()).hexdigest()
    payload = {
        "schema": "dreamco.repository-master-map.v1",
        "evidence_only": True,
        "scan_digest": digest,
        "summary": {"files_scanned": len(rows), **dict(counts), "workflows": len(workflow_paths), "pages_assets": len(page_paths), "test_files": len(test_paths)},
        "connections": {
            "actions_to_repository": "workflow files are inventory-visible; execution evidence remains in GitHub Actions",
            "repository_to_pages": "website assets and generated data are publishable through Deploy Buddy Website",
            "backend_to_pages": "Pages is a public/static surface; backend execution remains separately bound",
            "tests_to_benchmarks": "test files are cataloged but passing evidence is required before mastery",
        },
        "workflow_files": workflow_paths,
        "page_assets": page_paths,
        "test_files": test_paths,
        "files": rows,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    GENERATED.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    OUT.write_text(text, encoding="utf-8")
    GENERATED.write_text(text, encoding="utf-8")
    print(f"Scanned {len(rows)} repository files; generated {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
