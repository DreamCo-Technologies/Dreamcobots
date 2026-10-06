#!/usr/bin/env python3
"""Generate Universal Bot Runtime Contract manifests for every DreamCo bot.

Sources (canonical, read-only):
  - App_bots/<Division>.json   division profiles (primary for 1,101 bots)
  - bots/*.md                  Markdown specs (adds md-only bots, fills gaps)
  - server/seed-bots.ts        seed data, cross-checked for division conflicts
  - config/generated/bots.catalog.json  external API candidates per bot

Output: config/bots/bot-manifests.generated.json (one bot per line, sorted,
no timestamps). ``--check`` fails when the committed file is stale.

Each bot is mapped to one shared engine (drafting / analysis / classification
/ workflow) by deterministic keyword scoring. Bots whose text gives no usable
signal stay ``engine: unmapped`` and are flagged, never forced into an engine.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from buddy.fleet_runtime.contract import TIER_BOILERPLATE, expand, validate_bot_manifest, validate_collection  # noqa: E402
from buddy.fleet_runtime.permissions import text_declares_live_action  # noqa: E402
from buddy.fleet_runtime.engines import tokens  # noqa: E402
from buddy.fleet_runtime.sources import load_sources  # noqa: E402

APP_BOTS = ROOT / "App_bots"
CATALOG = ROOT / "config" / "generated" / "bots.catalog.json"
OUT = ROOT / "config" / "bots" / "bot-manifests.generated.json"

MAX_CAPS = 12
MIN_SCORE = 2.0

# Keyword stems per engine (matched against engines.tokens() output, which
# lower-cases and strips simple suffixes). Weighted by where they appear.
ENGINE_KEYWORDS: dict[str, tuple[str, ...]] = {
    "drafting": (
        "write", "writer", "writ", "copy", "copywrit", "content", "draft", "blog", "article", "script", "story",
        "caption", "post", "newsletter", "proposal", "letter", "resume", "pitch", "press", "headline", "seo",
        "translat", "summar", "brief", "narrat", "speech", "lyric", "song", "podcast", "video", "ebook", "book",
        "course", "lesson", "tutor", "curriculum", "message", "reply", "respons", "template", "descript", "slogan",
        "ad", "creative", "chat", "chatbot", "explain", "essay", "document", "documentation", "grant",
        "pattern", "architectur", "design", "expert", "generat", "builder", "outline", "runbook", "note", "guide",
    ),
    "analysis": (
        "analytic", "analysi", "analyz", "analyzer", "data", "report", "dashboard", "metric", "forecast",
        "predict", "insight", "benchmark", "valuat", "pric", "calculat", "estimat", "statistic", "trend", "kpi",
        "roi", "revenue", "cost", "budget", "financ", "portfolio", "market", "research", "lookup", "search",
        "intelligence", "monitor", "track", "tracker", "measur", "score", "scor", "model", "simulat", "optimiz",
        "audit", "comparison", "compar", "index", "yield", "performance", "telemetry", "sensor", "usage",
    ),
    "classification": (
        "classif", "classifi", "triage", "rout", "router", "detect", "detection", "detector", "filter", "scan",
        "scanner", "screen", "moderat", "fraud", "sentiment", "categor", "tag", "match", "matcher", "recommend",
        "qualif", "lead", "spam", "threat", "anomaly", "risk", "identify", "verif", "verify", "label", "sort",
        "priorit", "segment", "intent", "compliance", "vulnerab", "phish", "malware", "inspect", "diagnos",
    ),
    "workflow": (
        "workflow", "automat", "automation", "schedul", "scheduler", "checklist", "onboard", "planner", "plan",
        "coordinat", "pipeline", "process", "task", "project", "booking", "book", "appointment", "maintenanc",
        "operation", "ops", "manag", "approval", "procure", "order", "inventory", "dispatch", "logistic",
        "shipping", "fulfil", "hr", "hiring", "recruit", "payroll", "invoice", "contract", "permit", "launch",
        "setup", "deploy", "migration", "event", "itinerar", "travel", "reminder", "calendar", "ticket", "support",
    ),
}
FIELD_WEIGHTS = {"name": 3.0, "slug": 2.0, "category": 2.0, "description": 1.5, "capabilities": 1.0}
ENGINE_PRIORITY = ("workflow", "analysis", "classification", "drafting")  # deterministic tie-break

TOOL_MAP = {
    "approved model adapter": "model_router",
    "sandbox test harness": "sandbox_harness",
    "owner approval gate for external actions": "approval_gate",
    "audit / evidence logger": "evidence_logger",
}

PROFILES: dict[str, Any] = {
    "model_router": {
        "offline_first": {
            "mode": "offline_first",
            "offline_fallback": "deterministic",
            "live_alias": "dreamco/auto",
            "live_requires": ["DREAMCO_FLEET_LIVE_MODEL=1", "OPENROUTER_API_KEY (server-side secret)"],
            "router_module": "buddy.fleet_runtime.router -> buddy.openrouter.gateway.BuddyGateway",
        },
        "offline_only": {
            "mode": "offline_only",
            "offline_fallback": "deterministic",
            "live_alias": "none",
            "live_requires": [],
            "router_module": "buddy.fleet_runtime.router",
        },
    },
    "io_schema": {
        "engine:analysis": {
            "input": {"type": "object", "properties": {"objective": {"type": "string"}, "input": {"type": "object", "properties": {
                "records": {"type": "array"}, "values": {"type": "array"}, "metric": {"type": "string"},
                "group_by": {"type": "string"}, "filters": {"type": "object"}, "query": {"type": "string"}, "top_n": {"type": "integer"}}}}},
            "output": {"type": "object", "required": ["status", "summary"], "properties": {
                "status": {"enum": ["ok", "needs_input"]}, "summary": {"type": "string"},
                "row_count": {"type": "integer"}, "numeric_fields": {"type": "object"}, "groups": {"type": "object"}, "top": {"type": "array"}}},
        },
        "engine:classification": {
            "input": {"type": "object", "properties": {"objective": {"type": "string"}, "input": {"type": "object", "properties": {
                "text": {"type": "string"}, "labels": {"type": "array"}}}}},
            "output": {"type": "object", "required": ["status", "summary"], "properties": {
                "status": {"enum": ["ok", "needs_input"]}, "summary": {"type": "string"}, "ranked": {"type": "array"},
                "confidence": {"type": "number"}, "escalate_to_human": {"type": "boolean"}}},
        },
        "engine:workflow": {
            "input": {"type": "object", "properties": {"objective": {"type": "string"}, "input": {"type": "object", "properties": {
                "steps": {"type": "array"}, "completed_steps": {"type": "array"}}}}},
            "output": {"type": "object", "required": ["status", "summary", "steps", "next_actions", "awaiting_owner_approval"], "properties": {
                "status": {"enum": ["ok"]}, "summary": {"type": "string"}, "steps": {"type": "array"},
                "next_actions": {"type": "array"}, "awaiting_owner_approval": {"type": "array"}}},
        },
        "engine:drafting": {
            "input": {"type": "object", "properties": {"objective": {"type": "string"}, "input": {"type": "object", "properties": {
                "audience": {"type": "string"}, "tone": {"type": "string"}}}}},
            "output": {"type": "object", "required": ["status", "summary", "draft_markdown", "generated_by"], "properties": {
                "status": {"enum": ["ok"]}, "summary": {"type": "string"}, "draft_markdown": {"type": "string", "minLength": 1},
                "generated_by": {"enum": ["offline_deterministic", "live_model"]}}},
        },
    },
    "error_handling": {
        "structured_v1": {
            "on_exception": "return status=error with error.type=exception; evidence record still written; never raise to caller",
            "on_invalid_input": "return status=invalid_input listing schema errors; engine not called",
            "on_permission_denied": "return status=approval_required; no action taken; owner approval needed",
            "on_guardrail_block": "return status=guardrail_blocked; output withheld",
        }
    },
    "tools": {
        "model_router": {"kind": "model", "provided_by": "buddy.fleet_runtime.router", "external": False},
        "sandbox_harness": {"kind": "test", "provided_by": "buddy.fleet_runtime.smoke", "external": False},
        "approval_gate": {"kind": "policy", "provided_by": "buddy.fleet_runtime.permissions", "external": False},
        "evidence_logger": {"kind": "evidence", "provided_by": "buddy.fleet_runtime.evidence", "external": False},
    },
}

SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,79}$")
DEFAULT_TOOLS = ["model_router", "sandbox_harness", "approval_gate", "evidence_logger"]
# Values every expanded manifest shares; buddy.fleet_runtime.contract.expand()
# fills them (with {slug}/{engine} substituted) so the committed file stays small.
DEFAULTS = {
    "tools": DEFAULT_TOOLS,
    "error_handling": "structured_v1",
    "approval_policy": "buddy_os/governance/approval_policy.yaml",
    "unit_test": "tests/test_fleet_runtime_executor.py",
    "smoke": "config/bots/smoke-fixtures.json#{slug}",
    "health": "website/data/fleet-runtime-status.json#{slug}",
    "pages_route": "fleet-runtime.html#bot-{slug}",
    "evidence": "evidence/fleet-runtime/{slug}.json",
}


def load_api_candidates() -> dict[str, list[str]]:
    if not CATALOG.exists():
        return {}
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    out = {}
    for bot in data.get("bots", []) + data.get("supplemental_bots", []):
        out[bot["identity"]["slug"]] = sorted(bot.get("api_candidate_names") or [])
    return out


def score_engines(fields: dict[str, str]) -> dict[str, float]:
    scores = {engine: 0.0 for engine in ENGINE_KEYWORDS}
    for field, text in fields.items():
        weight = FIELD_WEIGHTS[field]
        toks = tokens(text.replace("-", " "))
        for engine, keys in ENGINE_KEYWORDS.items():
            hits = sum(1 for tok in toks if tok in keys or any(tok.startswith(k) for k in keys if len(k) >= 5))
            scores[engine] += weight * hits
    return scores


def pick_engine(scores: dict[str, float]) -> tuple[str, float]:
    best = max(scores.values())
    total = sum(scores.values())
    if best < MIN_SCORE:
        return "unmapped", 0.0
    engine = next(e for e in ENGINE_PRIORITY if scores[e] == best)
    return engine, round(best / total, 3) if total else 0.0


MONEY_RE = re.compile(
    r"\b(payments?|payouts?|stripe|ach|wire transfers?|trading|trader|order execution|checkout|billing|refunds?|"
    r"withdrawals?|deposits?|disburse\w*|invoices? (?:send|collection)|live revenue|real money|paid ultimate)\b", re.I)
DESTRUCTIVE_RE = re.compile(r"\b(delete|deletion|deletes|purge|wipe|destroy|teardown|drop tables?)\b", re.I)


def run_policy(text: str, engine: str) -> str:
    """Whether the bot may get a working Run button. Money/delete stay blocked."""
    if engine == "unmapped":
        return "spec_only"
    if MONEY_RE.search(text):
        return "blocked_money"
    if DESTRUCTIVE_RE.search(text):
        return "blocked_destructive"
    return "allowed"


def build_manifest(slug: str, entry: dict[str, Any], api: dict[str, list[str]], known_divisions: set[str]) -> dict[str, Any]:
    app, md, lane = entry.get("app"), entry.get("md"), entry.get("lane")
    base = app or md or lane
    flags = set(entry["flags"])
    if lane:
        flags |= {"teammate_lane", "capabilities_derived_from_description"}
    if not SLUG_RE.match(slug):
        flags.add("invalid_slug")
    if app and md:
        if md["division"] and md["division"] != app["division"]:
            flags.add("division_conflict_md")
    elif md and not app and not lane:
        flags.add("md_only")
    division = (app or {}).get("division") or (md or {}).get("division") or (lane or {}).get("division") or ""
    if not division:
        flags.add("division_missing")
    elif division not in known_divisions:
        flags.add("division_unknown")
    seed_division = entry.get("seed_division")
    if seed_division and seed_division != division:
        flags.add("division_conflict_seed")
    raw_caps = list(dict.fromkeys(base["capabilities"] or (md or {}).get("capabilities", [])))
    caps = [c[:120] for c in raw_caps if c.strip().lower() not in TIER_BOILERPLATE]
    dropped = len(raw_caps) - len(caps)
    if not caps:
        flags.add("placeholder_no_specific_capabilities")
    description = (base.get("description") or "")[:300]
    if not description:
        flags.add("placeholder_no_description")
    scores = score_engines({
        "name": base.get("name", ""), "slug": slug, "category": base.get("category", ""),
        "description": description, "capabilities": " ; ".join(caps),
    })
    engine, confidence = pick_engine(scores)
    if engine == "unmapped" and caps:
        best = max(scores.values())
        if best > 0:
            # Weak but real signal: use the best-scoring engine, flagged.
            engine = next(e for e in ENGINE_PRIORITY if scores[e] == best)
            confidence = round(best / sum(scores.values()), 3)
            flags.add("engine_weak_signal")
        else:
            # No keyword signal at all: a checklist over the bot's declared
            # capabilities is the honest generic job; flagged for review.
            engine, confidence = "workflow", 0.0
            flags.add("engine_fallback_workflow")
    if engine == "unmapped":
        flags.add("engine_unmapped")
    elif confidence < 0.4 or "engine_weak_signal" in flags:
        flags.add("engine_low_confidence")
    tool_names = list(dict.fromkeys((app or {}).get("tools") or (md or {}).get("tools") or []))
    tool_ids = [TOOL_MAP.get(t.strip().lower(), "unresolved:" + re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")) for t in tool_names]
    live = text_declares_live_action(" ".join([base.get("name", ""), description, *caps]))
    claims = bool((app or {}).get("claims_production_ready") or (md or {}).get("claims_production_ready"))
    if claims:
        flags.add("claims_production_ready_without_evidence")
    policy = run_policy(" ".join([slug, base.get("name", ""), description, *caps]), engine)
    if policy.startswith("blocked"):
        flags.add("run_" + policy)
    entry_out: dict[str, Any] = {
        "run": policy,
        "slug": slug,
        "name": base.get("name") or slug,
        "division": division or "UNASSIGNED",
        "tier": (base.get("tier") or "").lower(),
        "engine": engine,
        "engine_confidence": confidence,
        "caps": len(caps),
        "tier_features_dropped": dropped,
        "ceiling": "plan_only" if live else "sandbox",
        "live": live,
        "bench": len((app or {}).get("benchmarks", [])),
        "sources": entry["sources"],
        "flags": sorted(flags),
    }
    if tool_ids != DEFAULT_TOOLS:
        entry_out["tools"] = tool_ids
    if api.get(slug):
        entry_out["api"] = api[slug]
    if claims:
        entry_out["claims_ready"] = True
    if seed_division and seed_division != division:
        entry_out["seed_division"] = seed_division
    if base.get("category"):
        entry_out["category"] = base["category"]
    return entry_out


def mark_duplicates(manifests: list[dict[str, Any]], entries: dict[str, Any]) -> None:
    by_desc: dict[str, list[dict[str, Any]]] = {}
    for m in manifests:
        src = entries[m["slug"]].get("app") or entries[m["slug"]].get("md") or {}
        key = re.sub(r"\W+", " ", (src.get("description") or "").lower()).strip()
        if len(key) > 20:
            by_desc.setdefault(key, []).append(m)
    by_name: dict[str, list[dict[str, Any]]] = {}
    for m in manifests:
        by_name.setdefault(m["name"].strip().lower(), []).append(m)
    for group in list(by_desc.values()) + list(by_name.values()):
        if len(group) > 1:
            for m in group:
                if "duplicate_profile" not in m["flags"]:
                    m["flags"] = sorted(set(m["flags"]) | {"duplicate_profile"})


def render(collection: dict[str, Any]) -> str:
    bots = collection["bots"]
    head = {k: v for k, v in collection.items() if k != "bots"}
    text = json.dumps(head, indent=2, sort_keys=True, ensure_ascii=False)
    lines = ",\n".join("    " + json.dumps(b, sort_keys=True, ensure_ascii=False, separators=(",", ":")) for b in bots)
    return text[:-2] + ',\n  "bots": [\n' + lines + "\n  ]\n}\n"


def build() -> dict[str, Any]:
    entries, inputs, folder_notes = load_sources()
    api = load_api_candidates()
    digest = hashlib.sha256()
    for path in inputs + [CATALOG, Path(__file__)]:
        if path.exists():
            digest.update(path.relative_to(ROOT).as_posix().encode())
            digest.update(path.read_bytes())
    known = {json.loads(p.read_text(encoding="utf-8")).get("division") for p in APP_BOTS.glob("*.json")}
    lanes_path = ROOT / "config" / "bots" / "teammate-lanes.json"
    if lanes_path.exists():
        known.add(json.loads(lanes_path.read_text(encoding="utf-8")).get("division", "GrokTeammates"))
    manifests = [build_manifest(slug, entries[slug], api, known) for slug in sorted(entries)]
    mark_duplicates(manifests, entries)
    engines: dict[str, int] = {}
    flags: dict[str, int] = {}
    for m in manifests:
        engines[m["engine"]] = engines.get(m["engine"], 0) + 1
        for f in m["flags"]:
            flags[f] = flags.get(f, 0) + 1
    return {
        "schema": "dreamco.bot_manifests.v1",
        "contract": "config/bots/bot-runtime-contract.schema.json",
        "generator": "tools/generate_bot_manifests.py",
        "source_digest": digest.hexdigest(),
        "truth_policy": "A manifest is configuration, not proof. Readiness is computed from tests and evidence by tools/fleet_runtime_audit.py.",
        "profiles": PROFILES,
        "defaults": DEFAULTS,
        "summary": {"bots": len(manifests), "by_engine": dict(sorted(engines.items())),
                    "flags": dict(sorted(flags.items())), "source_notes": folder_notes},
        "bots": manifests,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if the committed manifest file is stale")
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args(argv)
    collection = build()
    errors = validate_collection(collection)
    for compact in collection["bots"]:
        errors.extend(validate_bot_manifest(expand(compact, collection, with_content=False)))
    if errors:
        print("Generated manifests violate the contract schema:\n- " + "\n- ".join(errors[:20]), file=sys.stderr)
        return 2
    text = render(collection)
    json.loads(text)  # render must stay valid JSON
    if args.check:
        current = args.out.read_text(encoding="utf-8") if args.out.exists() else ""
        if current != text:
            print(f"{args.out.relative_to(ROOT)} is stale. Run: python3 tools/generate_bot_manifests.py", file=sys.stderr)
            return 1
        print(json.dumps({"ok": True, **collection["summary"]}, indent=2))
        return 0
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(json.dumps({"written": args.out.relative_to(ROOT).as_posix(), **collection["summary"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
