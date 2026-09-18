#!/usr/bin/env python3
"""Create a Grok twin profile for every canonical App_bots slug.

A twin is a model-route overlay, not a second 1,051-count fleet and not a
trained frontier checkpoint.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "App_bots"
OUT = ROOT / "config" / "generated" / "grok-bot-twins.json"
REPORT = ROOT / "reports" / "GROK_BOT_TWINS.md"
STUDY = ROOT / "config" / "huggingface-two-week-study.json"
STUDY_OUT = ROOT / "config" / "generated" / "huggingface-two-week-study.json"
STUDY_MD = ROOT / "reports" / "HUGGINGFACE_TWO_WEEK_STUDY.md"


def load_bots() -> list[dict]:
    rows: list[dict] = []
    for path in sorted(APP.glob("*.json")):
        if path.name.startswith("masterbots"):
            continue
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        division = doc.get("division") or path.stem
        for bot in doc.get("bots", []) if isinstance(doc, dict) else []:
            if not isinstance(bot, dict):
                continue
            slug = str(bot.get("slug") or "").strip()
            if not slug:
                continue
            rows.append({
                "source_slug": slug,
                "grok_slug": f"grok-{slug}"[:140],
                "display_name": f"Grok {bot.get('displayName') or slug}",
                "division": division,
                "tier": bot.get("tier", "pro"),
                "mission": str(bot.get("description") or bot.get("mission") or "")[:500],
                "capabilities": list(bot.get("capabilities") or [])[:20],
                "model_route": "xai/grok-best-available",
                "quality_policy": "Prefer latest Grok frontier route for this bot's job. Cost is a tie-breaker only.",
                "autonomy_ceiling": "sandbox_execute",
                "live_money_outreach": False,
                "canonical_counted": False,
            })
    return rows


def main() -> int:
    twins = load_bots()
    payload = {
        "schema": "dreamco.grok_bot_twins.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "twin_count": len(twins),
        "canonical_baseline_preserved": 1051,
        "model_route": "xai/grok-best-available",
        "truth_boundary": "Twins are Grok-routed specialists for existing bots. They do not add to the 1,051 count and do not prove a new trained model.",
        "twins": twins,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Grok Bot Twins",
        "",
        f"- Twins generated: **{len(twins)}**",
        "- Route: `xai/grok-best-available`",
        "- Canonical 1,051 count unchanged.",
        "",
        "| Grok slug | Source | Division |",
        "| --- | --- | --- |",
    ]
    for row in twins[:200]:
        lines.append(f"| `{row['grok_slug']}` | `{row['source_slug']}` | {row['division']} |")
    if len(twins) > 200:
        lines.append(f"| … | {len(twins) - 200} more | … |")
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    study = json.loads(STUDY.read_text(encoding="utf-8"))
    STUDY_OUT.write_text(json.dumps(study, indent=2) + "\n", encoding="utf-8")
    study_lines = [
        "# Hugging Face Two-Week Study",
        "",
        study["goal"],
        "",
        "## Truth",
    ]
    for key, value in study["truth"].items():
        study_lines.append(f"- `{key}`: **{value}**")
    study_lines += ["", "## Calendar", "", "| Day | Focus |", "| --- | --- |"]
    for day in study["days"]:
        study_lines.append(f"| {day['day']} | {day['focus']} |")
    study_lines += ["", "Teacher: `" + study["teacher_route"] + "`", "", "Student shortlist:"]
    for item in study["student_shortlist"]:
        study_lines.append(f"- `{item}`")
    STUDY_MD.write_text("\n".join(study_lines) + "\n", encoding="utf-8")
    print(json.dumps({"twins": len(twins), "study_days": study["window_days"], "frontier_parity_proven": False}, indent=2))
    return 0 if twins else 1


if __name__ == "__main__":
    raise SystemExit(main())
