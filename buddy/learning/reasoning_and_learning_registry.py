#!/usr/bin/env python3
"""Discover, select, test, and package reasoning techniques + learning strategies."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
REASONING_PATH = HERE / "reasoning_techniques_catalog.json"
LEARNING_PATH = HERE / "learning_strategies_catalog.json"


@dataclass(frozen=True)
class CatalogItem:
    kind: str  # reasoning | learning
    id: str
    name: str
    family: str
    summary: str
    sell_tier: str
    status: str
    raw: dict[str, Any]


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_reasoning() -> list[CatalogItem]:
    data = _load(REASONING_PATH)
    items = []
    for row in data.get("techniques", []):
        items.append(
            CatalogItem(
                kind="reasoning",
                id=row["id"],
                name=row["name"],
                family=row.get("family", ""),
                summary=row.get("summary", ""),
                sell_tier=row.get("sell_tier", "free"),
                status=row.get("status", "catalogued"),
                raw=row,
            )
        )
    return items


def load_learning() -> list[CatalogItem]:
    data = _load(LEARNING_PATH)
    items = []
    for row in data.get("strategies", []):
        items.append(
            CatalogItem(
                kind="learning",
                id=row["id"],
                name=row["name"],
                family=row.get("family", ""),
                summary=row.get("summary", ""),
                sell_tier=row.get("sell_tier", "free"),
                status=row.get("status", "catalogued"),
                raw=row,
            )
        )
    return items


def discover_all() -> dict[str, list[CatalogItem]]:
    return {"reasoning": load_reasoning(), "learning": load_learning()}


def search(query: str, limit: int = 10) -> list[CatalogItem]:
    q = query.lower().strip()
    tokens = [t for t in re.split(r"\W+", q) if t]
    scored: list[tuple[int, CatalogItem]] = []
    for item in load_reasoning() + load_learning():
        blob = " ".join(
            [
                item.id,
                item.name,
                item.family,
                item.summary,
                " ".join(item.raw.get("when_to_use", []) if isinstance(item.raw.get("when_to_use"), list) else []),
                " ".join(item.raw.get("signals", []) if isinstance(item.raw.get("signals"), list) else []),
            ]
        ).lower()
        score = sum(1 for t in tokens if t in blob)
        if score:
            scored.append((score, item))
    scored.sort(key=lambda x: (-x[0], x[1].name))
    return [item for _, item in scored[:limit]]


def select_for_task(task_text: str) -> dict[str, Any]:
    """Heuristic selector: map task language to techniques + strategies."""
    t = task_text.lower()
    reasoning_ids: list[str] = []
    learning_ids: list[str] = []

    rules = [
        (("debug", "ci", "fail", "error"), ["evidence_first", "react", "self_critique"], ["error_analysis", "failure_memory"]),
        (("deal", "risk", "invest", "score"), ["rubric_scoring", "counterfactual", "devil_advocate"], ["benchmark_driven"]),
        (("write", "content", "post", "brand"), ["self_critique", "constitutional", "metaphor_compression"], ["contrastive", "human_in_the_loop"]),
        (("plan", "architect", "system", "design"), ["plan_and_solve", "tree_of_thoughts", "first_principles"], ["multi_perspective", "curriculum_learning"]),
        (("learn", "train", "improve", "master"), ["least_to_most", "self_consistency"], ["deliberate_practice", "spaced_repetition", "continuous_learning_cycle"]),
        (("secure", "abuse", "red team", "threat"), ["red_team", "constitutional", "devil_advocate"], ["error_analysis"]),
        (("route", "workflow", "orchestr"), ["workflow_learning", "plan_and_solve"], ["meta_learning", "imitation_learning"]),
    ]

    for keys, rids, lids in rules:
        if any(k in t for k in keys):
            reasoning_ids.extend(rids)
            learning_ids.extend(lids)

    if not reasoning_ids:
        reasoning_ids = ["chain_of_thought", "plan_and_solve", "evidence_first"]
    if not learning_ids:
        learning_ids = ["error_analysis", "continuous_learning_cycle"]

    # de-dupe preserve order
    def uniq(xs: list[str]) -> list[str]:
        seen = set()
        out = []
        for x in xs:
            if x not in seen:
                seen.add(x)
                out.append(x)
        return out

    reasoning_ids = uniq(reasoning_ids)
    learning_ids = uniq(learning_ids)

    r_map = {i.id: i for i in load_reasoning()}
    l_map = {i.id: i for i in load_learning()}

    return {
        "task": task_text,
        "reasoning": [r_map[i].raw for i in reasoning_ids if i in r_map],
        "learning": [l_map[i].raw for i in learning_ids if i in l_map],
    }


LP_FAMILY_STRATEGIES = "LP-STRATEGIES"
LP_MANIFEST_SCHEMA = "dreamco.lp.manifest.v1"
# Three distinct gates. Never collapse these in exports.
GATE_BOOTCAMP_GRADUATION = "bootcamp_graduation"
GATE_MARKETPLACE_LISTING = "marketplace_listing"
GATE_PATH_D_ALLOWLIST = "path_d_allowlist"


def learning_catalog_meta() -> dict[str, Any]:
    """Return catalog version + truth boundary from learning_strategies_catalog.json."""
    data = _load(LEARNING_PATH)
    return {
        "schema": data.get("schema", "dreamco.learning_strategies.v1"),
        "version": data.get("version", "0.0.0"),
        "truth_boundary": data.get("truth_boundary", ""),
    }


def export_lp_strategies_manifest(*, write_path: Path | None = None) -> dict[str, Any]:
    """Emit versioned LP-STRATEGIES catalog manifest (catalog_sku only).

    Bootcamp graduation != marketplace listing != Path D allowlist approval.
    This export flips none of those gates and makes no sellable/live claim.
    """
    meta = learning_catalog_meta()
    strategy_ids = [i.id for i in load_learning()]
    version = str(meta["version"])
    manifest: dict[str, Any] = {
        "schema": LP_MANIFEST_SCHEMA,
        "sku": f"{LP_FAMILY_STRATEGIES}-v{version}",
        "family": LP_FAMILY_STRATEGIES,
        "version": version,
        "title": "Buddy Learning Strategies Package",
        "source_refs": [
            "buddy/learning/learning_strategies_catalog.json",
            "buddy/bootcamp/buddy_bootcamp.yaml",
            "buddy/learning/reasoning_and_learning_registry.py",
        ],
        "strategy_ids": strategy_ids,
        "strategy_count": len(strategy_ids),
        "bootcamp_tracks": [],
        "truth_boundary": meta.get("truth_boundary") or None,
        "marketplace_status": "catalog_sku",
        "gates": {
            GATE_BOOTCAMP_GRADUATION: False,
            GATE_MARKETPLACE_LISTING: False,
            GATE_PATH_D_ALLOWLIST: False,
            "note": "Three distinct gates; this export flips none of them",
        },
        "graduation_evidence": {
            "native_passes": 0,
            "holdout_passed": False,
            "regression_passed": False,
            "repeated_signature_stable": False,
            "eligible_for_mastery": False,
            "structure_tests": "required",
            "note": "Catalog export only; not Bootcamp-graduated, not listed, not allowlisted",
        },
        "claims": {
            "sellable": False,
            "live": False,
            "production_mastery": False,
            "path_d_allowlist_write": False,
        },
    }
    if write_path is not None:
        write_path = Path(write_path)
        write_path.parent.mkdir(parents=True, exist_ok=True)
        write_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def marketplace_packs() -> list[dict[str, Any]]:
    """Group catalog items into sellable packs (honest catalog SKUs)."""
    reasoning = load_reasoning()
    learning = load_learning()
    tiers = ["free", "pro", "enterprise", "elite"]
    packs = []
    for tier in tiers:
        r = [i for i in reasoning if i.sell_tier == tier]
        l = [i for i in learning if i.sell_tier == tier]
        packs.append(
            {
                "sku": f"dreamco-reasoning-learning-{tier}",
                "tier": tier,
                "title": f"DreamCo Reasoning & Learning Pack ({tier})",
                "reasoning_count": len(r),
                "learning_count": len(l),
                "reasoning_ids": [i.id for i in r],
                "learning_ids": [i.id for i in l],
                "price_hint": {
                    "free": "$0",
                    "pro": "$99/mo",
                    "enterprise": "$499/mo",
                    "elite": "$999/mo",
                }.get(tier, "contact"),
                "includes": [
                    "Catalog access",
                    "Sandbox test prompts",
                    "Selector API (local)",
                    "No claim of automatic production mastery",
                ],
            }
        )
    packs.append(
        {
            "sku": "dreamco-reasoning-learning-complete",
            "tier": "elite",
            "title": "Complete Reasoning + Learning Library",
            "reasoning_count": len(reasoning),
            "learning_count": len(learning),
            "reasoning_ids": [i.id for i in reasoning],
            "learning_ids": [i.id for i in learning],
            "price_hint": "$999/mo",
            "includes": [
                "All techniques",
                "All strategies",
                "Discovery search",
                "Task selector",
                "Regression-friendly unit tests",
            ],
        }
    )
    return packs


def run_structure_tests() -> list[str]:
    """Return list of failure messages; empty means pass."""
    failures: list[str] = []
    r = load_reasoning()
    l = load_learning()
    if len(r) < 15:
        failures.append(f"expected ≥15 reasoning techniques, got {len(r)}")
    if len(l) < 15:
        failures.append(f"expected ≥15 learning strategies, got {len(l)}")

    r_ids = [i.id for i in r]
    l_ids = [i.id for i in l]
    if len(r_ids) != len(set(r_ids)):
        failures.append("duplicate reasoning ids")
    if len(l_ids) != len(set(l_ids)):
        failures.append("duplicate learning ids")

    for item in r:
        if not item.raw.get("test_prompt"):
            failures.append(f"reasoning {item.id} missing test_prompt")
        if item.sell_tier not in {"free", "pro", "enterprise", "elite"}:
            failures.append(f"reasoning {item.id} bad sell_tier")

    for item in l:
        if not item.raw.get("test"):
            failures.append(f"learning {item.id} missing test")
        if item.sell_tier not in {"free", "pro", "enterprise", "elite"}:
            failures.append(f"learning {item.id} bad sell_tier")

    # selector smoke
    sel = select_for_task("debug failing CI workflow")
    if not sel["reasoning"]:
        failures.append("selector returned no reasoning for CI debug")
    if not sel["learning"]:
        failures.append("selector returned no learning for CI debug")

    # search smoke
    hits = search("evidence failure")
    if not hits:
        failures.append("search returned no hits for evidence failure")

    packs = marketplace_packs()
    if len(packs) < 5:
        failures.append("marketplace packs incomplete")

    lp = export_lp_strategies_manifest()
    if lp.get("sku") != f"{LP_FAMILY_STRATEGIES}-v{learning_catalog_meta()['version']}":
        failures.append("LP sku mismatch")
    if lp.get("marketplace_status") != "catalog_sku":
        failures.append("LP marketplace_status must remain catalog_sku")
    if any(lp["claims"].get(k) for k in ("sellable", "live", "path_d_allowlist_write")):
        failures.append("LP export must not claim sellable/live/Path D")
    if any(lp["gates"].get(g) for g in (GATE_BOOTCAMP_GRADUATION, GATE_MARKETPLACE_LISTING, GATE_PATH_D_ALLOWLIST)):
        failures.append("LP export must leave all three gates false")
    if lp.get("strategy_ids") != l_ids:
        failures.append("LP strategy_ids must match learning catalog")

    return failures


def main() -> int:
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "discover":
        data = discover_all()
        print(json.dumps({
            "reasoning": len(data["reasoning"]),
            "learning": len(data["learning"]),
            "reasoning_ids": [i.id for i in data["reasoning"]],
            "learning_ids": [i.id for i in data["learning"]],
        }, indent=2))
        return 0

    if len(sys.argv) > 1 and sys.argv[1] == "search":
        q = " ".join(sys.argv[2:]) or "plan"
        hits = search(q)
        print(json.dumps([{"kind": h.kind, "id": h.id, "name": h.name} for h in hits], indent=2))
        return 0

    if len(sys.argv) > 1 and sys.argv[1] == "select":
        task = " ".join(sys.argv[2:]) or "plan a system"
        print(json.dumps(select_for_task(task), indent=2))
        return 0

    if len(sys.argv) > 1 and sys.argv[1] == "sell":
        print(json.dumps(marketplace_packs(), indent=2))
        return 0

    if len(sys.argv) > 1 and sys.argv[1] == "lp-export":
        if len(sys.argv) > 2 and sys.argv[2] == "--write":
            dest = Path(sys.argv[3]) if len(sys.argv) > 3 else HERE / "exports" / "LP-STRATEGIES.manifest.json"
            manifest = export_lp_strategies_manifest(write_path=dest)
            print(json.dumps({"wrote": str(dest), "sku": manifest["sku"]}, indent=2))
            return 0
        print(json.dumps(export_lp_strategies_manifest(), indent=2))
        return 0

    # default: test
    failures = run_structure_tests()
    if failures:
        print(json.dumps({"ok": False, "failures": failures}, indent=2))
        return 1
    data = discover_all()
    print(json.dumps({
        "ok": True,
        "reasoning": len(data["reasoning"]),
        "learning": len(data["learning"]),
        "packs": len(marketplace_packs()),
        "lp_sku": export_lp_strategies_manifest()["sku"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
