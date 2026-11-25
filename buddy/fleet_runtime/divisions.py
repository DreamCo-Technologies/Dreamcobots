"""Division manifests and division-level smoke tests.

A division manifest is generated from the bot manifests (App_bots/*.json,
seed data, teammate lanes). Its smoke test runs a small, deterministic set of
the division's own bots end to end through the shared runtime (offline): one
bot per engine present in the division, preferring bots that are allowed to
run. A division passes only if every selected bot passes its generic and
fixture smoke.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from .contract import load_fixtures
from .smoke import fixture_smoke, generic_smoke

ENGINE_ORDER = ("analysis", "classification", "drafting", "workflow")


def build_division_manifests(collection: dict[str, Any], seed_divisions: dict[str, int] | None = None) -> dict[str, Any]:
    by_div: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for bot in collection["bots"]:
        by_div[bot["division"]].append(bot)
    divisions = []
    for name in sorted(by_div):
        bots = sorted(by_div[name], key=lambda b: b["slug"])
        engines = Counter(b["engine"] for b in bots)
        policy = Counter(b.get("run", "spec_only") for b in bots)
        smoke: list[str] = []
        for engine in ENGINE_ORDER:
            candidates = [b for b in bots if b["engine"] == engine]
            allowed = [b for b in candidates if b.get("run") == "allowed"]
            pick = (allowed or candidates)[:1]
            smoke += [b["slug"] for b in pick]
        sources = sorted({s.split("#")[0] for b in bots for s in b["sources"] if s.startswith(("App_bots/", "config/bots/teammate-lanes.json"))})
        if seed_divisions and name in seed_divisions:
            sources.append("server/seed-bots.ts")
        runnable = policy.get("allowed", 0)
        owner_routes = Counter(
            (b.get("primary_domain_owner") or b.get("division"), b.get("primary_masterbot_id"))
            for b in bots
        )
        owner_route_rows = [
            {"primary_domain_owner": owner, "primary_masterbot_id": masterbot_id, "bots": count}
            for (owner, masterbot_id), count in sorted(owner_routes.items(), key=lambda item: str(item[0]))
        ]
        unique_owners = {row["primary_domain_owner"] for row in owner_route_rows}
        portfolios = {b.get("supplemental_portfolio") for b in bots if b.get("supplemental_portfolio")}
        divisions_shared_groups = {b.get("shared_workforce_group") for b in bots if b.get("shared_workforce_group")}
        divisions.append({
            "name": name,
            "primary_domain_owner": next(iter(unique_owners)) if len(unique_owners) == 1 else None,
            "primary_masterbot_id": owner_route_rows[0]["primary_masterbot_id"] if len(owner_route_rows) == 1 else None,
            "owner_routes": owner_route_rows,
            "supplemental_portfolio": next(iter(portfolios)) if len(portfolios) == 1 else None,
            "shared_workforce_group": next(iter(divisions_shared_groups)) if len(divisions_shared_groups) == 1 else None,
            "owner_approval_required": True,
            "shared_platform_masterbot_ids": list(range(46, 66)),
            "bots": len(bots),
            "engines": {e: engines[e] for e in sorted(engines)},
            "run_policy": {k: policy[k] for k in sorted(policy)},
            "seed_bots": (seed_divisions or {}).get(name, 0),
            "sources": sources or ["bots/*.md (no division manifest source)"],
            "smoke_bots": smoke,
            "triggerable": runnable > 0 and name != "UNASSIGNED",
            "blocked_reason": None if runnable > 0 and name != "UNASSIGNED" else (
                "no division source: bots here are Markdown-only specs" if name == "UNASSIGNED"
                else "every bot in this division is money/destructive/spec-only"),
            "description": f"{name}: {len(bots)} bots across " + ", ".join(f"{engines[e]} {e}" for e in sorted(engines)) + ".",
        })
    return {
        "schema": "dreamco.division_manifests.v1",
        "generator": "tools/generate_bot_manifests.py",
        "policy": "Generated from the bot manifests. smoke_bots = one bot per engine present (preferring runnable bots); the division smoke passes only if all of them pass offline.",
        "divisions": divisions,
    }


def division_smoke(executor: Any, division: dict[str, Any], fixtures: dict[str, Any] | None = None) -> dict[str, Any]:
    fixtures = load_fixtures()["fixtures"] if fixtures is None else fixtures
    results = []
    for slug in division["smoke_bots"]:
        if executor.bots.get(slug, {}).get("engine") == "unmapped":
            results.append({"bot": slug, "passed": False, "status": "unmapped", "failures": ["engine unmapped"]})
            continue
        generic = generic_smoke(executor, slug)
        fixture = fixtures.get(slug)
        fx = fixture_smoke(executor, slug, fixture) if fixture else None
        passed = generic["passed"] and (fx is None or fx["passed"])
        results.append({"bot": slug, "passed": passed, "fixture": bool(fx),
                        "failures": generic["failures"] + ((fx or {}).get("failures") or [])})
    ran = [r for r in results if r.get("status") != "unmapped"]
    return {"division": division["name"], "ran": len(ran), "passed": bool(ran) and all(r["passed"] for r in ran),
            "results": results}
