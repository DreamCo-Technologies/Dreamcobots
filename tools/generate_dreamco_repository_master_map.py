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
SKIP = {".git", ".pytest_cache", "node_modules", "dist", "__pycache__", ".vercel", ".wrangler", "playwright-report", "test-results", "tmp", "logs"}
SKIP_FILES = {
    OUT.relative_to(ROOT).as_posix(),
    GENERATED.relative_to(ROOT).as_posix(),
}


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


def build_payload(root: Path) -> dict:
    rows = []
    for p in sorted(root.rglob("*")):
        relative = p.relative_to(root)
        if (
            not p.is_file()
            or any(part in SKIP for part in relative.parts)
            or relative.as_posix() in SKIP_FILES
        ):
            continue
        rel = relative.as_posix()
        k = kind(relative)
        rows.append({"path": rel, "kind": k, "suite": suite(k), "bytes": p.stat().st_size})
    counts = Counter(r["kind"] for r in rows)
    workflow_paths = [r["path"] for r in rows if r["kind"] == "action"]
    page_paths = [r["path"] for r in rows if r["kind"] == "pages_asset"]
    test_paths = [r["path"] for r in rows if r["kind"] == "test"]
    digest = hashlib.sha256("\n".join(f"{r['path']}:{r['bytes']}" for r in rows).encode()).hexdigest()
    return {
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


def build_public_payload(payload: dict) -> dict:
    """Keep the Pages payload small while retaining the full audit copy in config."""
    return {
        "schema": payload["schema"],
        "evidence_only": payload["evidence_only"],
        "scan_digest": payload["scan_digest"],
        "summary": payload["summary"],
        "connections": payload["connections"],
        "full_inventory": "config/generated/repository-master-map.json",
        "truth_boundary": "The public map is a compact summary. File-level inventory remains repository evidence and does not prove runtime readiness.",
    }


def main() -> None:
    payload = build_payload(ROOT)
    public_payload = build_public_payload(payload)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    GENERATED.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(public_payload, separators=(",", ":"), sort_keys=True) + "\n", encoding="utf-8")
    GENERATED.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Scanned {payload['summary']['files_scanned']} repository files; generated {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
