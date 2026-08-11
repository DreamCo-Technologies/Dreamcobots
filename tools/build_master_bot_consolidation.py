#!/usr/bin/env python3
"""Build a capability-preserving master-bot consolidation plan.

The planner never deletes bot profiles. It creates reversible alias-to-master
proposals using proven capability overlap and, when available, bounded usage
telemetry. Missing telemetry is treated as unknown rather than zero usage.
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BOT_DIR = ROOT / "App_bots"
POLICY_PATH = ROOT / "config" / "master_bot_consolidation_policy.json"
USAGE_PATH = ROOT / "config" / "generated" / "bot-usage-telemetry.json"
OUT = ROOT / "config" / "generated" / "master-bot-consolidation.json"
REPORT = ROOT / "reports" / "MASTER_BOT_CONSOLIDATION.md"

TIER_WEIGHT = {"elite": 4, "enterprise": 3, "pro": 2, "free": 1}


def norm(value: str) -> str:
    return " ".join(value.lower().replace("_", " ").replace("-", " ").split())


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def load_bots() -> list[dict[str, Any]]:
    bots: list[dict[str, Any]] = []
    for path in sorted(BOT_DIR.glob("*.json")):
        payload = load_json(path, {})
        division = payload.get("division") or path.stem
        for bot in payload.get("bots", []):
            slug = bot.get("slug")
            if not slug:
                continue
            bots.append({
                "slug": slug,
                "displayName": bot.get("displayName") or slug,
                "division": division,
                "tier": str(bot.get("tier") or "free").lower(),
                "category": bot.get("category") or "unknown",
                "capabilities": list(dict.fromkeys(bot.get("capabilities", []) or [])),
                "status": bot.get("status") or "unknown",
                "source": str(path.relative_to(ROOT)),
            })
    return bots


def capability_set(bot: dict[str, Any]) -> set[str]:
    return {norm(str(value)) for value in bot.get("capabilities", []) if norm(str(value))}


def overlap(a: dict[str, Any], b: dict[str, Any]) -> float:
    left, right = capability_set(a), capability_set(b)
    if not left or not right:
        return 0.0
    return len(left & right) / min(len(left), len(right))


def master_score(bot: dict[str, Any]) -> tuple[int, int, str]:
    return (TIER_WEIGHT.get(bot.get("tier", "free"), 0), len(capability_set(bot)), bot["slug"])


def load_usage() -> tuple[dict[str, int], bool]:
    payload = load_json(USAGE_PATH, None)
    if not isinstance(payload, dict):
        return {}, False
    records = payload.get("bots")
    window_days = payload.get("window_days")
    if not isinstance(records, list) or not isinstance(window_days, int):
        return {}, False
    usage: dict[str, int] = {}
    for row in records:
        if isinstance(row, dict) and isinstance(row.get("slug"), str) and isinstance(row.get("executions"), int):
            usage[row["slug"]] = row["executions"]
    return usage, True


def choose_division_masters(bots: list[dict[str, Any]]) -> dict[str, str]:
    by_division: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for bot in bots:
        by_division[bot["division"]].append(bot)
    return {
        division: max(items, key=master_score)["slug"]
        for division, items in by_division.items()
        if items
    }


def build_plan() -> dict[str, Any]:
    policy = load_json(POLICY_PATH, {})
    bots = load_bots()
    by_slug = {bot["slug"]: bot for bot in bots}
    masters = choose_division_masters(bots)
    usage, telemetry_available = load_usage()
    rare_threshold = int(policy.get("rare_use_threshold", 2))
    overlap_threshold = float(policy.get("minimum_capability_overlap_for_merge", 0.75))

    proposals: list[dict[str, Any]] = []
    for bot in sorted(bots, key=lambda item: item["slug"]):
        master_slug = masters.get(bot["division"])
        if not master_slug or master_slug == bot["slug"]:
            continue
        master = by_slug[master_slug]
        measured_overlap = overlap(bot, master)
        executions = usage.get(bot["slug"]) if telemetry_available else None
        low_use = telemetry_available and executions is not None and executions <= rare_threshold
        duplicate_like = measured_overlap >= overlap_threshold
        if not low_use and not duplicate_like:
            continue
        reasons = []
        if low_use:
            reasons.append(f"usage <= {rare_threshold} executions in measured window")
        if duplicate_like:
            reasons.append(f"capability overlap {measured_overlap:.2f} >= {overlap_threshold:.2f}")
        source_caps = capability_set(bot)
        master_caps = capability_set(master)
        additions = sorted(source_caps - master_caps)
        proposals.append({
            "alias_slug": bot["slug"],
            "master_slug": master_slug,
            "division": bot["division"],
            "category": bot["category"],
            "telemetry_available": telemetry_available,
            "executions": executions,
            "capability_overlap": round(measured_overlap, 4),
            "capability_additions_required": additions,
            "reason": reasons,
            "status": "ready_for_regression_testing" if not additions else "master_capability_union_required",
            "activation_mode": "reversible_alias",
            "original_profile_preserved": True,
        })

    return {
        "schema": "dreamco.master_bot_consolidation.plan.v1",
        "mode": policy.get("mode", "capability_preserving_alias_merge"),
        "fleet_profiles_scanned": len(bots),
        "divisions": len(masters),
        "division_masters": masters,
        "usage_telemetry_available": telemetry_available,
        "low_use_rule_active": telemetry_available,
        "proposal_count": len(proposals),
        "proposals": proposals,
        "truth_boundary": "This plan preserves every source profile. Low-use claims require telemetry; overlap-based merges require capability evidence; activation still requires routing and fleet regression tests.",
    }


def write_outputs(plan: dict[str, Any]) -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Master Bot Consolidation",
        "",
        f"- Fleet profiles scanned: **{plan['fleet_profiles_scanned']}**",
        f"- Division masters: **{plan['divisions']}**",
        f"- Usage telemetry available: **{plan['usage_telemetry_available']}**",
        f"- Merge proposals: **{plan['proposal_count']}**",
        "",
        "Specialist profiles are preserved as reversible aliases; capabilities must be unioned into the selected master before activation.",
        "",
    ]
    for row in plan["proposals"]:
        lines.append(
            f"- `{row['alias_slug']}` → `{row['master_slug']}` "
            f"(overlap {row['capability_overlap']:.2f}; {row['status']})"
        )
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    plan = build_plan()
    write_outputs(plan)
    print(json.dumps({
        "ok": True,
        "profiles": plan["fleet_profiles_scanned"],
        "division_masters": plan["divisions"],
        "proposals": plan["proposal_count"],
        "usage_telemetry_available": plan["usage_telemetry_available"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
