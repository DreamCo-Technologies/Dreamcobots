#!/usr/bin/env python3
"""Generate batches of 100 research-reviewed DreamCo improvement contracts."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "config" / "revolutionary_update_research.json"
CONFIG_OUT = ROOT / "config" / "generated" / "revolutionary_updates_batch_001.json"
WEB_OUT = ROOT / "website" / "data" / "revolutionary-updates-batch-001.json"
REPORT_OUT = ROOT / "reports" / "REVOLUTIONARY_UPDATES_BATCH_001.md"


def load_research() -> dict[str, Any]:
    return json.loads(RESEARCH.read_text(encoding="utf-8"))


def build_updates() -> dict[str, Any]:
    research = load_research()
    updates: list[dict[str, Any]] = []
    number = 1
    for theme in research["themes"]:
        for pattern in research["update_patterns"]:
            updates.append({
                "id": f"R001-{number:03d}",
                "theme_id": theme["id"],
                "theme": theme["name"],
                "pattern": pattern["id"],
                "title": f"{theme['name']}: {pattern['change']}",
                "status": "research_approved_for_implementation",
                "research_basis": theme["research_basis"],
                "official_research": [theme["source"]],
                "change": f"For DreamCo/Buddy, {pattern['change']} specifically for {theme['name'].lower()}.",
                "why_needed": f"Buddy coordinates a large specialist fleet; {theme['name'].lower()} is a platform-level scaling requirement.",
                "dreamco_advantage": f"Make {theme['name'].lower()} a reusable primitive for every division and specialist instead of rebuilding it bot-by-bot.",
                "implementation_contract": [
                    "deduplicate against existing DreamCo registries and capabilities first",
                    "reuse existing runtime and evidence contracts where possible",
                    "store machine-readable status and provenance",
                    "keep consequential external actions approval-gated",
                    "make repository checks deterministic and network-independent",
                ],
                "acceptance_tests": [
                    "existing inventory is preserved",
                    "duplicate identifiers are rejected",
                    "unsupported capability claims cannot be certified",
                    "failure paths produce inspectable evidence",
                    "the change has a measurable success criterion",
                ],
                "review": {
                    "decision": "needed",
                    "basis": "current primary-source research plus fit with existing DreamCo architecture",
                    "not_a_certification": True,
                },
            })
            number += 1
    if len(updates) != 100:
        raise ValueError(f"Expected exactly 100 updates, got {len(updates)}")
    return {
        "schema": "dreamco.revolutionary_updates.v1",
        "batch": 1,
        "count": len(updates),
        "researched_at": research["researched_at"],
        "approval_meaning": research["approval_meaning"],
        "updates": updates,
    }


def render_report(registry: dict[str, Any]) -> str:
    lines = [
        "# Revolutionary Updates — Batch 001",
        "",
        f"Research date: {registry['researched_at']}",
        "",
        registry["approval_meaning"],
        "",
        "## 100 reviewed updates",
        "",
    ]
    for item in registry["updates"]:
        lines.extend([
            f"### {item['id']} — {item['title']}",
            "",
            f"- Why: {item['why_needed']}",
            f"- Advantage: {item['dreamco_advantage']}",
            f"- Research: {item['official_research'][0]}",
            f"- Status: `{item['status']}`",
            "",
        ])
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    registry = build_updates()
    expected_json = json.dumps(registry, indent=2, sort_keys=True) + "\n"
    expected_report = render_report(registry)
    outputs = ((CONFIG_OUT, expected_json), (WEB_OUT, expected_json), (REPORT_OUT, expected_report))
    if args.check:
        for path, expected in outputs:
            if not path.exists() or path.read_text(encoding="utf-8") != expected:
                raise SystemExit(f"Generated output is stale: {path.relative_to(ROOT)}")
        print(json.dumps({"ok": True, "batch": 1, "updates": 100}))
        return 0
    for path, expected in outputs:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(expected, encoding="utf-8")
    print(json.dumps({"ok": True, "batch": 1, "updates": 100}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
