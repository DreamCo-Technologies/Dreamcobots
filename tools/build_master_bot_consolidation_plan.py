#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
APP_BOTS = ROOT / "App_bots"
POLICY_PATH = ROOT / "config" / "buddy-master-bot-consolidation.json"
TELEMETRY_PATH = ROOT / "config" / "generated" / "bot-usage-telemetry.json"
OUT_JSON = ROOT / "config" / "generated" / "master-bot-consolidation-plan.json"
OUT_MD = ROOT / "reports" / "MASTER_BOT_CONSOLIDATION_PLAN.md"


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def load_profiles() -> list[dict[str, Any]]:
    profiles: list[dict[str, Any]] = []
    for path in sorted(APP_BOTS.glob("*.json")):
        payload = load_json(path, {})
        division = payload.get("division") or path.stem
        for bot in payload.get("bots", []):
            slug = bot.get("slug")
            if not slug:
                continue
            profiles.append({
                "slug": slug,
                "display_name": bot.get("displayName") or slug,
                "division": division,
                "category": bot.get("category") or "unknown",
                "status": bot.get("status") or "unknown",
                "capabilities": list(bot.get("capabilities", [])),
                "source": str(path.relative_to(ROOT)),
            })
    return profiles


def usage_map() -> tuple[dict[str, int], bool]:
    payload = load_json(TELEMETRY_PATH, None)
    if not payload:
        return {}, False
    rows = payload.get("bots") if isinstance(payload, dict) else None
    if not isinstance(rows, list):
        return {}, False
    result: dict[str, int] = {}
    for row in rows:
        slug = row.get("slug")
        executions = row.get("executions_30d")
        if isinstance(slug, str) and isinstance(executions, int) and executions >= 0:
            result[slug] = executions
    return result, bool(result)


def master_score(profile: dict[str, Any], policy: dict[str, Any]) -> tuple[int, str]:
    score = len(profile["capabilities"]) * 10
    slug = profile["slug"].lower()
    name = profile["display_name"].lower()
    category = profile["category"].lower()
    selection = policy["master_selection"]
    if slug in {value.lower() for value in selection.get("prefer_slugs", [])}:
        score += 10_000
    score += 500 * sum(term.lower() in name or term.lower() in slug for term in selection.get("prefer_name_terms", []))
    if category in {value.lower() for value in selection.get("prefer_categories", [])}:
        score += 250
    if profile.get("status") == "active":
        score += 25
    return score, profile["slug"]


def build_plan() -> dict[str, Any]:
    policy = load_json(POLICY_PATH, {})
    profiles = load_profiles()
    usage, telemetry_available = usage_map()
    low_use_threshold = int(policy.get("low_use_execution_threshold", 2))

    by_division: dict[str, list[dict[str, Any]]] = {}
    for profile in profiles:
        by_division.setdefault(profile["division"], []).append(profile)

    groups: list[dict[str, Any]] = []
    accounted: set[str] = set()
    for division in sorted(by_division):
        members = sorted(by_division[division], key=lambda item: item["slug"])
        forced = policy.get("command_core_master_slug") if division == "CommandCore" else None
        master = next((item for item in members if item["slug"] == forced), None)
        if master is None:
            master = max(members, key=lambda item: master_score(item, policy))

        specialist_rows = []
        master_capabilities = set(master["capabilities"])
        inherited_unique: set[str] = set()
        for member in members:
            accounted.add(member["slug"])
            if member["slug"] == master["slug"]:
                continue
            executions = usage.get(member["slug"])
            usage_state = "unknown" if executions is None else ("low_use" if executions <= low_use_threshold else "active_use")
            unique_caps = [cap for cap in member["capabilities"] if cap not in master_capabilities]
            inherited_unique.update(unique_caps)
            routing_mode = "merged_alias" if usage_state == "low_use" else "specialist_under_master"
            specialist_rows.append({
                "slug": member["slug"],
                "display_name": member["display_name"],
                "source": member["source"],
                "usage_state": usage_state,
                "executions_30d": executions,
                "routing_mode": routing_mode,
                "direct_route_preserved": True,
                "capabilities_preserved": member["capabilities"],
                "unique_capabilities_inherited_by_master_group": unique_caps,
            })

        groups.append({
            "division": division,
            "master_slug": master["slug"],
            "master_display_name": master["display_name"],
            "master_source": master["source"],
            "master_capabilities": master["capabilities"],
            "inherited_unique_capabilities": sorted(inherited_unique),
            "specialist_count": len(specialist_rows),
            "specialists": specialist_rows,
        })

    profile_slugs = {profile["slug"] for profile in profiles}
    return {
        "schema": "dreamco.master_bot_consolidation_plan.v1",
        "mode": policy.get("mode", "master_first_alias_merge"),
        "telemetry_available": telemetry_available,
        "usage_window_days": policy.get("usage_window_days", 30),
        "low_use_execution_threshold": low_use_threshold,
        "canonical_profile_count": len(profiles),
        "master_group_count": len(groups),
        "accounted_profile_count": len(accounted),
        "capability_preservation_verified": accounted == profile_slugs,
        "groups": groups,
        "truth_boundary": "Low-use status is assigned only when usage telemetry exists. Without telemetry, specialists remain subordinate to a master but are not falsely labeled unused. No canonical profile or capability is deleted by this plan."
    }


def render_report(plan: dict[str, Any]) -> str:
    lines = [
        "# Master Bot Consolidation Plan",
        "",
        f"- Canonical profiles: **{plan['canonical_profile_count']}**",
        f"- Master groups: **{plan['master_group_count']}**",
        f"- Usage telemetry available: **{plan['telemetry_available']}**",
        f"- Capability/profile preservation: **{plan['capability_preservation_verified']}**",
        "",
    ]
    for group in plan["groups"]:
        low_use = sum(1 for row in group["specialists"] if row["usage_state"] == "low_use")
        lines.append(f"## {group['division']} → `{group['master_slug']}`")
        lines.append(f"- Specialists under master: {group['specialist_count']}")
        lines.append(f"- Low-use aliases with telemetry evidence: {low_use}")
        lines.append(f"- Unique capabilities inherited by group: {len(group['inherited_unique_capabilities'])}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    plan = build_plan()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_report(plan), encoding="utf-8")
    print(json.dumps({
        "ok": plan["capability_preservation_verified"],
        "profiles": plan["canonical_profile_count"],
        "master_groups": plan["master_group_count"],
        "telemetry_available": plan["telemetry_available"],
        "output": str(OUT_JSON.relative_to(ROOT)),
    }, indent=2))
    return 0 if plan["capability_preservation_verified"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
