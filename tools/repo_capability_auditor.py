#!/usr/bin/env python3
"""Inventory DreamCo repositories and produce a capability-oriented report.

The auditor is intentionally read-only: it never copies code or changes another
repository. It provides evidence for safe capability-level promotion into the
canonical Dreamcobots repository.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import PurePosixPath

REPOS = [
    "DreamCo-Technologies/Dreamcobots",
    "DreamCo-Technologies/DreamCo-Command-Center",
    "DreamCo-Technologies/Dreamco",
    "DreamCo-Technologies/Ai-bots",
    "DreamCo-Technologies/demo-repository",
    "ireanjordan24/Dreamcobots-Grok-Revolutionary",
    "ireanjordan24/dreamcobots",
    "ireanjordan24/codespaces-react",
]

PATTERNS: dict[str, tuple[str, ...]] = {
    "benchmarks": ("benchmark", "eval", "score", "gap", "capability"),
    "orchestration": ("orchestr", "workflow", "agent", "control", "command"),
    "bot_fleet": ("bot", "bots", "fleet", "agent"),
    "github": ("github", "actions", "workflow", ".github"),
    "ui": ("client", "components", "pages", "tsx", "swiftui", "html", "css"),
    "apple": ("xcode", "swift", "swiftui", "xcworkspace", "entitlements"),
    "security": ("auth", "permission", "policy", "security", "secret"),
    "media": ("media", "video", "audio", "image", "transcri"),
    "data": ("database", "schema", "sql", "index", "telemetry", "analytics"),
    "migration": ("migration", "migrate", "safety", "rollback"),
    "dev_environment": ("devcontainer", ".replit", "codespaces", "vite", "xcodeproj"),
}


def gh_api(path: str):
    token = os.environ.get("GH_TOKEN")
    if token:
        cmd = ["gh", "api", path]
    else:
        cmd = ["gh", "api", path]
    p = subprocess.run(cmd, text=True, capture_output=True, check=False)
    if p.returncode:
        raise RuntimeError(p.stderr.strip() or path)
    return json.loads(p.stdout)


def classify(path: str) -> set[str]:
    p = path.lower()
    return {name for name, needles in PATTERNS.items() if any(n in p for n in needles)}


def main() -> int:
    report = {"canonical": REPOS[0], "repositories": [], "capabilities": {}, "promotion_candidates": []}
    capability_sources: dict[str, list[str]] = defaultdict(list)

    for repo in REPOS:
        try:
            meta = gh_api(f"repos/{repo}")
            branch = meta.get("default_branch", "main")
            tree_data = gh_api(f"repos/{repo}/git/trees/{branch}?recursive=1")
            tree = tree_data.get("tree", [])
            paths = [x.get("path", "") for x in tree if x.get("type") == "blob"]
            caps = set()
            examples: dict[str, list[str]] = defaultdict(list)
            for path in paths:
                for cap in classify(path):
                    caps.add(cap)
                    if len(examples[cap]) < 8:
                        examples[cap].append(path)
            entry = {
                "repo": repo,
                "visibility": meta.get("visibility"),
                "default_branch": branch,
                "size_kb": meta.get("size"),
                "file_count": len(paths),
                "tree_truncated": bool(tree_data.get("truncated")),
                "capabilities": sorted(caps),
                "examples": {k: v for k, v in sorted(examples.items())},
            }
            report["repositories"].append(entry)
            for cap in caps:
                capability_sources[cap].append(repo)
        except Exception as exc:
            report["repositories"].append({"repo": repo, "error": str(exc)})

    report["capabilities"] = {k: sorted(v) for k, v in sorted(capability_sources.items())}
    canonical_caps = set(next((r.get("capabilities", []) for r in report["repositories"] if r.get("repo") == REPOS[0]), []))
    for cap, sources in sorted(capability_sources.items()):
        noncanonical = [r for r in sources if r != REPOS[0]]
        if noncanonical and cap not in canonical_caps:
            report["promotion_candidates"].append({"capability": cap, "sources": noncanonical, "reason": "capability not detected in canonical path inventory"})

    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
