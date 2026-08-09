#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP_BOTS = ROOT / "App_bots"
AGENTS = ROOT / ".github" / "agents"
PROGRAM = ROOT / "config" / "bot-accounting-placement-program.json"
PLACEMENT = ROOT / "config" / "generated" / "bot-division-placement-audit.json"
OUT = ROOT / "config" / "generated" / "bot-accounting-placement-audit.json"
REPORT = ROOT / "reports" / "BOT_ACCOUNTING_PLACEMENT_AUDIT.md"

FRONTMATTER_NAME = re.compile(r"^name:\s*(.+)$", re.M)


def main() -> int:
    program = json.loads(PROGRAM.read_text(encoding="utf-8"))
    subprocess.run([sys.executable, "tools/audit_bot_division_placement.py"], cwd=ROOT, check=True)
    placement = json.loads(PLACEMENT.read_text(encoding="utf-8"))

    bots = []
    slugs = defaultdict(list)
    category_counts = Counter()
    division_counts = Counter()
    declared_total_mismatches = []
    metadata_errors = []

    for path in sorted(APP_BOTS.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        division = payload.get("division") or path.stem
        rows = payload.get("bots", [])
        declared_total = payload.get("total")
        if declared_total != len(rows):
            declared_total_mismatches.append({"file": str(path.relative_to(ROOT)), "declared": declared_total, "actual": len(rows)})
        for bot in rows:
            slug = str(bot.get("slug", "")).strip()
            category = str(bot.get("category", "")).strip()
            slugs[slug].append(division)
            division_counts[division] += 1
            category_counts[category or "__missing__"] += 1
            missing = []
            for field in program["required_bot_fields"]:
                value = bot.get(field)
                if value is None or value == "" or value == []:
                    missing.append(field)
            if missing:
                metadata_errors.append({"slug": slug or None, "division": division, "missing": missing, "source": str(path.relative_to(ROOT))})
            bots.append({"slug": slug, "division": division, "category": category, "source": str(path.relative_to(ROOT))})

    duplicate_slugs = [{"slug": slug, "divisions": ds} for slug, ds in sorted(slugs.items()) if slug and len(ds) > 1]
    blank_slugs = sum(1 for b in bots if not b["slug"])
    blank_categories = sum(1 for b in bots if not b["category"])

    specialist_agents = []
    expected_agents = program["specialist_agents"]
    discovered_agent_files = sorted(p.name for p in AGENTS.glob("*.agent.md")) if AGENTS.exists() else []
    unowned_agents = []
    missing_expected_agents = []
    for filename in discovered_agent_files:
        path = AGENTS / filename
        text = path.read_text(encoding="utf-8", errors="replace")
        match = FRONTMATTER_NAME.search(text)
        owner = expected_agents.get(filename)
        if not owner:
            unowned_agents.append(filename)
        specialist_agents.append({"file": filename, "name": match.group(1).strip() if match else filename, "owner_division": owner, "source": str(path.relative_to(ROOT))})
    for filename in expected_agents:
        if filename not in discovered_agent_files:
            missing_expected_agents.append(filename)

    status_counts = placement.get("status_counts", {})
    move_candidates = [r for r in placement.get("bots", []) if r.get("status") == "move_candidate"]
    cross_division_review = [r for r in placement.get("bots", []) if r.get("status") == "review_cross_division"]

    baseline = program["canonical_fleet"]
    blockers = []
    if len(bots) != baseline["profiles"]:
        blockers.append(f"canonical fleet count {len(bots)} != expected {baseline['profiles']}")
    if len(division_counts) != baseline["divisions"]:
        blockers.append(f"division count {len(division_counts)} != expected {baseline['divisions']}")
    if duplicate_slugs:
        blockers.append(f"duplicate slugs: {len(duplicate_slugs)}")
    if declared_total_mismatches:
        blockers.append(f"division declared-total mismatches: {len(declared_total_mismatches)}")
    if metadata_errors:
        blockers.append(f"bots with missing required metadata: {len(metadata_errors)}")
    if blank_slugs:
        blockers.append(f"blank slugs: {blank_slugs}")
    if blank_categories:
        blockers.append(f"blank categories: {blank_categories}")
    if unowned_agents:
        blockers.append(f"unowned specialist agents: {len(unowned_agents)}")
    if missing_expected_agents:
        blockers.append(f"missing expected specialist agents: {len(missing_expected_agents)}")

    payload = {
        "schema": "dreamco.bot_accounting_placement_audit.v1",
        "canonical_bot_count": len(bots),
        "division_count": len(division_counts),
        "category_count": len(category_counts),
        "specialist_agent_count": len(specialist_agents),
        "total_accounted_software_workers": len(bots) + len(specialist_agents),
        "division_counts": dict(sorted(division_counts.items())),
        "category_counts": dict(sorted(category_counts.items(), key=lambda kv: (-kv[1], kv[0]))),
        "placement_status_counts": status_counts,
        "move_candidate_count": len(move_candidates),
        "cross_division_review_count": len(cross_division_review),
        "move_candidates": move_candidates,
        "cross_division_review": cross_division_review,
        "duplicate_slugs": duplicate_slugs,
        "declared_total_mismatches": declared_total_mismatches,
        "metadata_errors": metadata_errors,
        "specialist_agents": specialist_agents,
        "unowned_specialist_agents": unowned_agents,
        "missing_expected_specialist_agents": missing_expected_agents,
        "release_blockers": blockers,
        "accounting_complete": not blockers,
        "truth_boundary": program["truth_rule"],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Bot Accounting & Placement Audit", "",
        f"- Canonical bots: **{len(bots)}**",
        f"- Divisions: **{len(division_counts)}**",
        f"- Categories: **{len(category_counts)}**",
        f"- Specialist agents outside fixed fleet: **{len(specialist_agents)}**",
        f"- Total accounted software workers: **{len(bots) + len(specialist_agents)}**",
        f"- Placement move candidates: **{len(move_candidates)}**",
        f"- Cross-division review: **{len(cross_division_review)}**",
        f"- Release blockers: **{len(blockers)}**", "",
        "## Division counts", "",
    ]
    for division, count in sorted(division_counts.items()):
        lines.append(f"- {division}: {count}")
    lines += ["", "## Category counts", ""]
    for category, count in sorted(category_counts.items(), key=lambda kv: (-kv[1], kv[0])):
        lines.append(f"- `{category}`: {count}")
    lines += ["", "## Specialist agents", ""]
    for agent in specialist_agents:
        lines.append(f"- {agent['name']} → {agent['owner_division'] or 'UNOWNED'}")
    if blockers:
        lines += ["", "## Release blockers", ""] + [f"- {x}" for x in blockers]
    if move_candidates:
        lines += ["", "## High-confidence move candidates", ""]
        for row in move_candidates:
            lines.append(f"- `{row['slug']}`: {row['current_division']} → {row['recommended_primary']} ({row['current_score']} → {row['recommended_score']})")
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps({
        "ok": not blockers,
        "canonical_bots": len(bots),
        "divisions": len(division_counts),
        "categories": len(category_counts),
        "specialist_agents": len(specialist_agents),
        "move_candidates": len(move_candidates),
        "cross_division_review": len(cross_division_review),
        "release_blockers": blockers,
        "output": str(OUT.relative_to(ROOT)),
        "report": str(REPORT.relative_to(ROOT)),
    }, indent=2))
    return 0 if not blockers else 1


if __name__ == "__main__":
    raise SystemExit(main())
