#!/usr/bin/env python3
"""
Ensure every canonical DreamCo bot has the files and metadata needed for
production *profile* readiness (catalog + markdown + checklist).

Truth boundary (from AGENTS.md):
  A filled profile is NOT proof of live runtime production.
  production_ready stays false until adapters, sandbox, auth, and telemetry pass.

What this tool does:
  1. Scan App_bots/*.json (canonical fleet)
  2. Ensure required + recommended fields on every bot
  3. Fix declared `total` vs actual length
  4. Generate missing bots/<slug>.md specialty profiles
  5. Write reports/BOT_PRODUCTION_READINESS.md + config/generated/bot-production-readiness.json

Usage:
  python3 tools/ensure_bots_production_ready.py           # apply fixes
  python3 tools/ensure_bots_production_ready.py --check   # audit only (exit 1 if gaps)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP_BOTS = ROOT / "App_bots"
BOTS_MD = ROOT / "bots"
OUT_JSON = ROOT / "config" / "generated" / "bot-production-readiness.json"
OUT_MD = ROOT / "reports" / "BOT_PRODUCTION_READINESS.md"

REQUIRED_FIELDS = [
    "slug",
    "displayName",
    "category",
    "description",
    "capabilities",
    "status",
]

RECOMMENDED_FIELDS = [
    "tier",
    "revenueModel",
    "targetUsers",
    "priceRange",
]

# Extended production profile pack (filled with safe defaults when missing)
PRODUCTION_PACK_DEFAULTS = {
    "toolsNeeded": [
        "Approved model adapter",
        "Sandbox test harness",
        "Owner approval gate for external actions",
        "Audit / evidence logger",
    ],
    "benchmarks": [
        {"label": "Sandbox capability pass rate", "target": "100% declared caps", "current": "profile-only"},
        {"label": "Time to first useful packet", "target": "< 60s", "current": "unmeasured"},
        {"label": "Approval boundary compliance", "target": "100%", "current": "policy-declared"},
    ],
    "learningPlan": [
        "Ingest approved outcome evidence from sandbox runs",
        "Refine routing keywords and capability tags",
        "Track which recommendations users accept",
    ],
    "tasks": [
        {
            "id": "pr1",
            "title": "Pass sandbox capability checks",
            "status": "todo",
            "priority": "High",
        },
        {
            "id": "pr2",
            "title": "Configure required adapters",
            "status": "todo",
            "priority": "High",
        },
        {
            "id": "pr3",
            "title": "Record deployment telemetry evidence",
            "status": "todo",
            "priority": "Medium",
        },
    ],
    "production": {
        "production_ready": False,
        "production_gate": (
            "implement or configure adapters, pass sandbox checks, "
            "add authentication, and verify deployment telemetry"
        ),
        "standalone_native_runtime": "shared_worker_not_standalone",
        "external_integrations": "configuration_required",
        "checklist": [
            "profile_schema_valid",
            "markdown_profile_present",
            "sandbox_test_defined",
            "adapter_configured",
            "auth_scoped",
            "telemetry_verified",
        ],
        "checklist_status": {
            "profile_schema_valid": True,
            "markdown_profile_present": False,
            "sandbox_test_defined": False,
            "adapter_configured": False,
            "auth_scoped": False,
            "telemetry_verified": False,
        },
    },
}


def slugify(value: str) -> str:
    s = value.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-") or "unnamed-bot"


def default_system_prompt(bot: dict, division: str) -> str:
    name = bot.get("displayName") or bot.get("slug") or "DreamCo Bot"
    desc = bot.get("description") or "Specialized DreamCo fleet agent."
    caps = bot.get("capabilities") or []
    cap_line = "; ".join(str(c) for c in caps[:8])
    return (
        f"You are {name}, a specialized AI bot in the DreamCo Empire OS "
        f"{division} division. {desc} "
        f"Core capabilities: {cap_line}. "
        "Operate with precision, provide actionable intelligence, and generate "
        "measurable results. Be concise, data-driven, and focused on ROI. "
        "Never claim live external actions completed unless evidence and "
        "owner approval exist. Prefer sandbox and synthetic data by default."
    )


def ensure_bot_fields(bot: dict, division: str) -> list[str]:
    """Mutate bot in place; return list of field names that were filled."""
    filled: list[str] = []

    if not bot.get("slug"):
        bot["slug"] = slugify(str(bot.get("displayName") or "unnamed-bot"))
        filled.append("slug")

    if not bot.get("displayName"):
        bot["displayName"] = str(bot["slug"]).replace("-", " ").title()
        filled.append("displayName")

    if not bot.get("category"):
        bot["category"] = "general"
        filled.append("category")

    if not bot.get("description"):
        bot["description"] = (
            f"{bot['displayName']} specialist in the {division} division."
        )
        filled.append("description")

    caps = bot.get("capabilities")
    if not isinstance(caps, list) or len(caps) == 0:
        bot["capabilities"] = [
            "Task planning",
            "Evidence-aware recommendations",
            "Sandbox-safe execution planning",
            "Approval boundary respect",
        ]
        filled.append("capabilities")

    if not bot.get("status"):
        bot["status"] = "active"
        filled.append("status")

    # Recommended commercial fields
    if not bot.get("tier"):
        bot["tier"] = "pro"
        filled.append("tier")
    if not bot.get("revenueModel"):
        bot["revenueModel"] = "SaaS subscription"
        filled.append("revenueModel")
    if not bot.get("targetUsers"):
        bot["targetUsers"] = f"{division} operators and analysts"
        filled.append("targetUsers")
    if not bot.get("priceRange"):
        bot["priceRange"] = "$99/mo"
        filled.append("priceRange")

    # Production pack
    for key, default in PRODUCTION_PACK_DEFAULTS.items():
        if key == "production":
            continue
        if key not in bot or bot[key] in (None, "", []):
            bot[key] = json.loads(json.dumps(default))  # deep copy
            filled.append(key)

    prod = bot.get("production")
    if not isinstance(prod, dict):
        bot["production"] = json.loads(json.dumps(PRODUCTION_PACK_DEFAULTS["production"]))
        filled.append("production")
    else:
        base = json.loads(json.dumps(PRODUCTION_PACK_DEFAULTS["production"]))
        for k, v in base.items():
            if k not in prod:
                prod[k] = v
                filled.append(f"production.{k}")
        # Never auto-claim production_ready true
        prod["production_ready"] = bool(prod.get("production_ready")) and all(
            [
                prod.get("checklist_status", {}).get("adapter_configured"),
                prod.get("checklist_status", {}).get("sandbox_test_defined"),
                prod.get("checklist_status", {}).get("auth_scoped"),
                prod.get("checklist_status", {}).get("telemetry_verified"),
            ]
        )

    if not bot.get("systemPrompt"):
        bot["systemPrompt"] = default_system_prompt(bot, division)
        filled.append("systemPrompt")

    if not bot.get("sample_test_prompt"):
        name = bot.get("displayName") or bot["slug"]
        cap_line = "; ".join(str(c) for c in (bot.get("capabilities") or [])[:8])
        bot["sample_test_prompt"] = (
            f"Test every declared capability for {name} in sandbox mode: {cap_line}. "
            "Use synthetic data, record separate evidence for each capability, "
            "and stop before any live external action."
        )
        filled.append("sample_test_prompt")

    return filled


def render_markdown(bot: dict, division: str) -> str:
    name = bot.get("displayName") or bot["slug"]
    tier = str(bot.get("tier") or "pro").upper()
    price = bot.get("priceRange") or "N/A"
    desc = bot.get("description") or ""
    caps = bot.get("capabilities") or []
    tools = bot.get("toolsNeeded") or []
    learn = bot.get("learningPlan") or []
    tasks = bot.get("tasks") or []
    prompt = bot.get("systemPrompt") or default_system_prompt(bot, division)
    prod = bot.get("production") or {}

    lines = [
        f"# {name}",
        "",
        f"> **Division:** {division} | **Tier:** {tier} | **Price:** {price}",
        f"> **Status:** {bot.get('status', 'active')} | "
        f"**Production ready:** {prod.get('production_ready', False)}",
        "",
        "## Description",
        desc,
        "",
        "## Capabilities",
    ]
    for c in caps:
        lines.append(f"- {c}")
    lines += ["", "## Tools needed"]
    for t in tools:
        lines.append(f"- {t}")
    lines += ["", "## Learning plan"]
    for item in learn:
        lines.append(f"- {item}")
    lines += ["", "## Tasks"]
    for task in tasks:
        if isinstance(task, dict):
            lines.append(
                f"- [{task.get('status', 'todo')}] {task.get('title', task.get('id', 'task'))} "
                f"({task.get('priority', 'Medium')})"
            )
        else:
            lines.append(f"- {task}")
    lines += [
        "",
        "## Revenue Model",
        str(bot.get("revenueModel") or "SaaS subscription"),
        "",
        "## Target Users",
        str(bot.get("targetUsers") or "DreamCo users"),
        "",
        "## System Prompt",
        "```",
        prompt[:1200],
        "```",
        "",
        "## Sample sandbox test",
        str(bot.get("sample_test_prompt") or ""),
        "",
        "## Production gate",
        str(prod.get("production_gate") or PRODUCTION_PACK_DEFAULTS["production"]["production_gate"]),
        "",
        "---",
        "*Generated/updated by tools/ensure_bots_production_ready.py — "
        "profile completeness only; runtime production requires evidence.*",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="Audit only; do not write files. Exit 1 if gaps remain.",
    )
    args = parser.parse_args()
    apply = not args.check

    if not APP_BOTS.is_dir():
        print("App_bots/ not found", file=sys.stderr)
        return 2

    BOTS_MD.mkdir(parents=True, exist_ok=True)

    stats = {
        "divisions": 0,
        "bots": 0,
        "fields_filled": 0,
        "markdown_created": 0,
        "markdown_updated": 0,
        "totals_fixed": 0,
        "missing_required_before": 0,
        "production_ready_true": 0,
    }
    per_bot_gaps: list[dict] = []
    division_summaries: list[dict] = []

    for path in sorted(APP_BOTS.glob("*.json")):
        raw = path.read_text(encoding="utf-8")
        payload = json.loads(raw)
        division = payload.get("division") or path.stem
        bots = payload.get("bots")
        if not isinstance(bots, list):
            continue

        stats["divisions"] += 1
        changed = False
        div_filled = 0

        for bot in bots:
            if not isinstance(bot, dict):
                continue
            stats["bots"] += 1

            missing_req = [
                f
                for f in REQUIRED_FIELDS
                if bot.get(f) is None or bot.get(f) == "" or bot.get(f) == []
            ]
            if missing_req:
                stats["missing_required_before"] += 1

            filled = ensure_bot_fields(bot, division)
            if filled:
                changed = True
                stats["fields_filled"] += len(filled)
                div_filled += len(filled)
                per_bot_gaps.append(
                    {
                        "slug": bot.get("slug"),
                        "division": division,
                        "filled": filled,
                        "had_missing_required": bool(missing_req),
                    }
                )

            slug = bot["slug"]
            md_path = BOTS_MD / f"{slug}.md"
            md_body = render_markdown(bot, division)

            # Track markdown checklist
            prod = bot.setdefault("production", {})
            cs = prod.setdefault("checklist_status", {})
            if md_path.exists():
                cs["markdown_profile_present"] = True
                if apply:
                    # Refresh generated sections only if file is short/generated
                    existing = md_path.read_text(encoding="utf-8", errors="replace")
                    if (
                        "Generated by DreamCo" in existing
                        or "ensure_bots_production_ready" in existing
                        or len(existing) < 400
                    ):
                        md_path.write_text(md_body, encoding="utf-8")
                        stats["markdown_updated"] += 1
                        changed = True
            else:
                cs["markdown_profile_present"] = False
                if apply:
                    md_path.write_text(md_body, encoding="utf-8")
                    cs["markdown_profile_present"] = True
                    stats["markdown_created"] += 1
                    changed = True
                else:
                    per_bot_gaps.append(
                        {
                            "slug": slug,
                            "division": division,
                            "filled": ["markdown_missing"],
                            "had_missing_required": False,
                        }
                    )

            cs["profile_schema_valid"] = all(
                bot.get(f) not in (None, "", []) for f in REQUIRED_FIELDS
            )
            if prod.get("production_ready"):
                stats["production_ready_true"] += 1

        # Fix total
        if payload.get("total") != len(bots):
            if apply:
                payload["total"] = len(bots)
                changed = True
                stats["totals_fixed"] += 1

        if apply and changed:
            path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

        division_summaries.append(
            {
                "division": division,
                "bots": len(bots),
                "fields_filled": div_filled,
                "file": str(path.relative_to(ROOT)),
            }
        )

    report = {
        "schema": "dreamco.bot_production_readiness.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": "check" if args.check else "apply",
        "stats": stats,
        "divisions": division_summaries,
        "sample_gaps": per_bot_gaps[:100],
        "truth_boundary": (
            "Profile completeness is not runtime production. "
            "production_ready requires adapter + sandbox + auth + telemetry evidence."
        ),
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Bot Production Readiness",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Mode: **{report['mode']}**",
        "",
        "## Summary",
        "",
        f"- Divisions scanned: **{stats['divisions']}**",
        f"- Bots scanned: **{stats['bots']}**",
        f"- Fields filled: **{stats['fields_filled']}**",
        f"- Markdown profiles created: **{stats['markdown_created']}**",
        f"- Markdown profiles updated: **{stats['markdown_updated']}**",
        f"- Division totals fixed: **{stats['totals_fixed']}**",
        f"- Bots missing required fields (before fill): **{stats['missing_required_before']}**",
        f"- Bots marked production_ready=true: **{stats['production_ready_true']}**",
        "",
        "## Required profile fields",
        "",
        ", ".join(f"`{f}`" for f in REQUIRED_FIELDS),
        "",
        "## Production pack added when missing",
        "",
        "`toolsNeeded`, `benchmarks`, `learningPlan`, `tasks`, `systemPrompt`, "
        "`sample_test_prompt`, `production` checklist",
        "",
        "## Truth boundary",
        "",
        report["truth_boundary"],
        "",
        "## Division counts",
        "",
    ]
    for d in division_summaries:
        lines.append(f"- **{d['division']}**: {d['bots']} bots ({d['file']})")
    lines.append("")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps({"ok": True, **stats, "report": str(OUT_MD.relative_to(ROOT))}, indent=2))

    if args.check and (
        stats["missing_required_before"]
        or stats["markdown_created"]
        or any("markdown_missing" in g.get("filled", []) for g in per_bot_gaps)
    ):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
