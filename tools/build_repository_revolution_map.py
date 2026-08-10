#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "website" / "data" / "repository-revamp-map.json"
REPORT = ROOT / "reports" / "REPOSITORY_REVAMP_MAP.md"

SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "dist", "coverage", "__pycache__", ".pytest_cache", ".next"}

CATEGORY_DEFS: dict[str, dict[str, str]] = {
    "actions_ci": {"label":"Actions / CI","owner":"Buttons and automatic checks that build, test, secure, deploy, and diagnose DreamCo.","user":"The reliability machinery behind Buddy.","investor":"Repeatable operating controls that reduce key-person and release risk.","engineer":"Workflow orchestration, CI policies, release gates, and evidence artifacts.","focus":"make automation self-explaining, deterministic, fast, secure, and repairable"},
    "server_runtime": {"label":"Server / Runtime","owner":"The backend brain that receives requests, routes work, applies rules, and returns results.","user":"Where Buddy turns requests into controlled actions and answers.","investor":"Core execution IP and reusable platform logic.","engineer":"Typed runtime modules, route handlers, policies, adapters, and orchestration services.","focus":"make runtime behavior modular, typed, observable, resilient, and adapter-friendly"},
    "client_ui": {"label":"Client / Product UI","owner":"The main application screens people use to operate DreamCo.","user":"The controls, pages, forms, chat, and feedback that make Buddy usable.","investor":"The product surface where technical capability becomes adoption and retention.","engineer":"React/UI composition, state, accessibility, API integration, and error states.","focus":"make every workflow obvious, accessible, responsive, testable, and low-friction"},
    "public_website": {"label":"Public Website","owner":"The simple browser-facing DreamCo experience and public status/prospectus pages.","user":"A lightweight way to explore Buddy, data controls, bots, tests, and product concepts.","investor":"A transparent product and evidence showcase.","engineer":"Static/PWA pages, generated data, client scripts, navigation, and deployment assets.","focus":"make public claims truthful, fast, accessible, searchable, and evidence-linked"},
    "bot_fleet": {"label":"Bots / Fleet","owner":"DreamCo's specialist workforce organized behind master bots.","user":"Skills Buddy can assemble instead of forcing users to pick hundreds of bots.","investor":"A reusable capability catalog and orchestration moat rather than a simple chatbot list.","engineer":"Data-driven profiles, capability contracts, routing identities, master groups, aliases, and sub-bot teams.","focus":"consolidate overlap, preserve capabilities, improve routing, prove usefulness, and reduce permanent-bot sprawl"},
    "config_data": {"label":"Config / Registries / Data","owner":"The rulebooks and catalogs that tell DreamCo what exists and how systems should behave.","user":"The settings and structured knowledge behind consistent Buddy behavior.","investor":"Portable product knowledge separated from hard-coded implementation.","engineer":"Schemas, registries, generated evidence, policies, source catalogs, and configuration truth.","focus":"make configuration validated, versioned, deduplicated, traceable, portable, and easy to regenerate"},
    "tools_generators": {"label":"Tools / Generators","owner":"Utilities that build catalogs, reports, checks, and repair plans automatically.","user":"Automation that keeps Buddy organized without manual maintenance.","investor":"Operational leverage and reduced maintenance cost.","engineer":"Deterministic generators, linters, auditors, migration tools, and evidence builders.","focus":"make tools idempotent, deterministic, composable, testable, documented, and safe to rerun"},
    "tests_evals": {"label":"Tests / Evaluations","owner":"Proof that important parts work as intended before calling them ready.","user":"Protection against Buddy getting worse after updates.","investor":"Evidence discipline and regression control.","engineer":"Unit, integration, E2E, policy, benchmark, security, and regression suites.","focus":"maximize meaningful coverage, minimize flakes, measure real outcomes, and expose failures clearly"},
    "docs_prospectus": {"label":"Docs / Prospectus","owner":"Plain-English explanations of DreamCo, how to use it, and what is actually ready.","user":"Help, onboarding, examples, and product expectations.","investor":"Thesis, architecture, traction evidence, risks, roadmap, and differentiation.","engineer":"Architecture decisions, runbooks, interfaces, examples, conventions, and contribution guidance.","focus":"make documentation audience-aware, current, source-linked, actionable, and automatically checked for drift"},
    "security_governance": {"label":"Security / Governance","owner":"Rules that stop DreamCo from doing unsafe, unauthorized, or unreviewed things.","user":"Privacy, permissions, consent, safety, and control.","investor":"Risk reduction and enterprise-readiness foundations.","engineer":"Threat models, authorization, secrets, auditability, approval gates, provenance, and policy enforcement.","focus":"apply least privilege, defense in depth, explicit approvals, audit trails, and secure defaults"},
    "ai_models": {"label":"AI / Models / Intelligence","owner":"How Buddy chooses and evaluates AI models and reasoning strategies.","user":"Better answers without requiring users to understand model brands.","investor":"Model-agnostic leverage and reduced provider lock-in.","engineer":"Routing, evals, provider adapters, context policy, fallbacks, local models, and benchmark evidence.","focus":"choose models by measured task fit, preserve fallbacks, control cost, and prevent provider lock-in"},
    "integrations": {"label":"Integrations / APIs","owner":"Connections that let Buddy work with external services when the user authorizes them.","user":"Bring permitted app data and actions into one assistant.","investor":"Distribution and ecosystem expansion without rebuilding every service.","engineer":"OAuth, API contracts, webhooks, retries, idempotency, rate limits, secrets, mocks, and connector health.","focus":"make every connector permissioned, replaceable, tested, observable, and failure-tolerant"},
    "business_revenue": {"label":"Business / Revenue","owner":"Systems that turn capabilities into useful offers, pricing, customers, and measurable revenue experiments.","user":"Clear products and services rather than a confusing technology pile.","investor":"Business model, unit economics, demand evidence, and monetization pathways.","engineer":"Entitlements, billing boundaries, analytics, experiments, and revenue attribution.","focus":"connect technical capability to user value, pricing evidence, measurable economics, and truthful revenue attribution"},
    "deployment_infra": {"label":"Deployment / Infrastructure","owner":"How DreamCo gets built, hosted, updated, monitored, and rolled back.","user":"Availability, speed, and reliable updates.","investor":"Scalability and operational maturity.","engineer":"Build artifacts, environments, hosting, secrets, rollouts, caching, observability, and rollback.","focus":"make deployment reproducible, portable, observable, cost-aware, and easy to roll back"},
    "assets_media": {"label":"Assets / Media / Other","owner":"Supporting files, media, examples, and uncategorized repository resources.","user":"Visuals, samples, and supporting product material.","investor":"Brand and demonstration assets when rights and provenance are clear.","engineer":"Static resources, fixtures, media provenance, generated outputs, and miscellaneous supporting files.","focus":"keep assets traceable, optimized, rights-aware, deduplicated, searchable, and correctly referenced"},
}

UPGRADE_PILLARS = [
    ("plain_language", "Add a plain-English explanation of purpose, owner, inputs, outputs, and when to use it."),
    ("machine_contract", "Add or tighten a machine-readable contract/schema so tools can validate behavior."),
    ("stable_identity", "Give important objects stable IDs, versions, aliases, and migration rules."),
    ("input_validation", "Validate inputs early with helpful errors and bounded limits."),
    ("output_schema", "Make outputs structured, predictable, and easy for other systems to consume."),
    ("failure_design", "Define expected failure modes, first-root-cause reporting, retries, and safe fallbacks."),
    ("observability", "Add traces, structured logs, metrics, run IDs, evidence links, and health signals."),
    ("unit_tests", "Add focused deterministic tests for core logic and edge cases."),
    ("regression_tests", "Lock important repaired behavior into regression tests so it cannot silently return."),
    ("security", "Threat-model the surface and apply secure defaults, dependency checks, and secret protections."),
    ("privacy", "Classify data, limit purpose/retention, minimize exposure, and preserve user control."),
    ("permissions", "Use least privilege and explicit approval boundaries for consequential actions."),
    ("provenance", "Record source, version, timestamp, rights/license, and evidence lineage for important data/results."),
    ("accessibility", "Make the experience understandable and usable across devices, abilities, and input methods."),
    ("performance", "Measure latency/throughput/resource use and prevent meaningful performance regressions."),
    ("cost_efficiency", "Measure marginal cost and choose cheaper equivalent paths where quality remains acceptable."),
    ("local_first", "Support offline/local or graceful degraded operation where practical instead of assuming a network/provider."),
    ("interoperability", "Use documented open interfaces and common formats so the component works with other systems."),
    ("portability", "Make data/config/runtime easy to move between hosting, models, storage, or projects."),
    ("docs_examples", "Add real examples, quickstarts, failure examples, and copy-paste-safe usage guidance."),
    ("onboarding", "Reduce steps needed for a new owner/user/developer to get the first successful outcome."),
    ("feature_flags", "Put risky/new behavior behind explicit flags, modes, or staged rollout controls."),
    ("rollback", "Define how to undo a change quickly and preserve the last known-good state."),
    ("export_delete", "Ensure user-controlled information can be exported, corrected, detached, and deleted where applicable."),
    ("customization", "Expose safe user/developer customization without requiring core-code forks."),
    ("extension_points", "Create documented adapters/hooks/plugins so new projects can reuse the component."),
    ("evaluations", "Benchmark correctness, quality, latency, cost, reliability, and task success with comparable fixtures."),
    ("deduplicate_merge", "Detect overlapping code/bots/registries and consolidate behind shared masters/interfaces while preserving aliases."),
    ("deprecation_migration", "Give obsolete paths a measured deprecation and migration plan instead of leaving permanent dead weight."),
    ("value_metrics", "Tie the component to user value, adoption, reliability, developer productivity, or business evidence rather than feature count alone."),
]


def category_for(path: Path) -> str:
    rel = path.relative_to(ROOT)
    parts = rel.parts
    first = parts[0] if parts else path.name
    low = str(rel).lower()
    if first == ".github": return "actions_ci"
    if first in {"App_bots", "bots", "original-bots"}: return "bot_fleet"
    if first == "server":
        if any(word in low for word in ["model", "ai-", "openai", "provider"]): return "ai_models"
        if any(word in low for word in ["stripe", "payment", "revenue", "sales"]): return "business_revenue"
        if any(word in low for word in ["oauth", "connector", "integration", "adapter"]): return "integrations"
        if any(word in low for word in ["security", "approval", "policy", "auth"]): return "security_governance"
        return "server_runtime"
    if first == "client": return "client_ui"
    if first == "website": return "public_website"
    if first in {"config", "shared"}: return "config_data"
    if first in {"tools", "script", "scripts"}: return "tools_generators"
    if first == "tests" or path.name.startswith("test_") or ".test." in path.name: return "tests_evals"
    if first in {"docs"} or path.suffix.lower() in {".md", ".mdx", ".rst"}: return "docs_prospectus"
    if first in {"attached_assets", "assets", "public"} or path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".mp3", ".wav", ".mp4", ".mov"}: return "assets_media"
    if path.name in {"package.json", "package-lock.json", "tsconfig.json", "vite.config.ts", "Dockerfile", "vercel.json"}: return "deployment_infra"
    if any(word in low for word in ["security", "guardrail", "governance", "approval"]): return "security_governance"
    if any(word in low for word in ["model", "openai", "anthropic", "llm"]): return "ai_models"
    if any(word in low for word in ["stripe", "revenue", "pricing", "business"]): return "business_revenue"
    if any(word in low for word in ["connector", "integration", "oauth", "api"]): return "integrations"
    return "assets_media"


def file_kind(path: Path) -> str:
    if path.is_dir(): return "directory"
    ext = path.suffix.lower().lstrip(".")
    return ext or "file"


def explanation_for(path: Path, category: str) -> str:
    label = CATEGORY_DEFS[category]["label"]
    if path.is_dir():
        return f"Repository area for {label.lower()} work. Its contents should share the same contracts, tests, documentation, and upgrade rules instead of behaving like unrelated files."
    ext = path.suffix.lower()
    role = {
        ".py":"Python implementation/tool",
        ".ts":"TypeScript implementation/contract",
        ".tsx":"React/TypeScript product component",
        ".js":"JavaScript runtime/browser module",
        ".mjs":"JavaScript module/tool",
        ".json":"structured registry/config/evidence file",
        ".yml":"automation/configuration file",
        ".yaml":"automation/configuration file",
        ".md":"documentation/prospectus file",
        ".html":"browser page",
        ".css":"visual styling file",
        ".sql":"database/query definition",
    }.get(ext, "supporting repository file")
    return f"{role} in the {label} category. Review its callers/references before changing it; upgrades should preserve compatible behavior or provide a migration path."


def file_specific_upgrades(path: Path, category: str) -> list[str]:
    base = [
        "Confirm this file still has at least one current consumer/reference; mark orphaned files for review instead of silently keeping dead code.",
        "Add or verify tests/evidence proportional to the file's runtime importance.",
        "Link the file to a plain-English purpose and owning system so future developers know why it exists.",
        "Check for duplicate functionality elsewhere and route shared behavior through one canonical implementation when practical.",
        "Record a migration/rollback path before breaking public routes, schemas, bot slugs, or generated-data formats."
    ]
    if category == "actions_ci": base[0] = "Verify every referenced action version, script, file, permission, and generated artifact against the current repository."
    elif category == "bot_fleet": base[0] = "Verify the bot has unique value, measurable demand/evidence, a master route, and a reversible merge path if it overlaps another bot."
    elif category == "config_data": base[0] = "Verify schema, provenance, source-of-truth ownership, generation path, and drift checks for this data/config file."
    elif category == "tests_evals": base[0] = "Verify the test measures a meaningful contract and fails for the bug/behavior it is supposed to protect."
    return base


def iter_files() -> list[Path]:
    rows: list[Path] = []
    for root, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        root_path = Path(root)
        for name in files:
            path = root_path / name
            try:
                path.relative_to(ROOT)
            except ValueError:
                continue
            rows.append(path)
    return sorted(rows, key=lambda p: str(p.relative_to(ROOT)).lower())


def build_upgrade_packs() -> list[dict[str, Any]]:
    packs=[]
    for cid, meta in CATEGORY_DEFS.items():
        upgrades=[]
        for index, (uid, instruction) in enumerate(UPGRADE_PILLARS, 1):
            upgrades.append({
                "number": index,
                "id": uid,
                "upgrade": f"For {meta['label']}: {instruction}",
                "category_focus": meta["focus"],
                "acceptance": f"Evidence exists showing the {uid.replace('_',' ')} upgrade is implemented or intentionally not applicable for this category."
            })
        packs.append({"id":cid, **meta, "upgrade_count":len(upgrades), "upgrades":upgrades})
    return packs


def load_bots() -> list[dict[str, Any]]:
    bots=[]
    for path in sorted((ROOT/"App_bots").glob("*.json")):
        try: payload=json.loads(path.read_text(encoding="utf-8"))
        except Exception: continue
        division=payload.get("division") or path.stem
        for bot in payload.get("bots",[]):
            slug=bot.get("slug")
            if not slug: continue
            bots.append({
                "slug":slug,
                "name":bot.get("displayName") or slug,
                "division":division,
                "category":bot.get("category") or "unknown",
                "description":bot.get("description") or "No description recorded.",
                "capability_count":len(bot.get("capabilities",[]) or []),
                "source":str(path.relative_to(ROOT)),
                "status":bot.get("status") or "unknown",
            })
    return bots


def choose_masters(bots: list[dict[str, Any]]) -> dict[str,str]:
    grouped=defaultdict(list)
    for bot in bots: grouped[bot["division"]].append(bot)
    masters={}
    for division,rows in grouped.items():
        preferred=next((b for b in rows if b["slug"] in {"dreambot","buddy-bot"}),None)
        winner=preferred or max(rows,key=lambda b:(b["capability_count"],b["slug"]))
        masters[division]=winner["slug"]
    return masters


def main() -> int:
    files=iter_files()
    top_level=sorted([p for p in ROOT.iterdir() if p.name not in SKIP_DIRS], key=lambda p:p.name.lower())
    packs=build_upgrade_packs()
    file_rows=[]
    counts=Counter()
    for path in files:
        category=category_for(path); counts[category]+=1
        file_rows.append({
            "path":str(path.relative_to(ROOT)),
            "kind":file_kind(path),
            "category":category,
            "explanation":explanation_for(path,category),
            "specific_upgrade_priorities":file_specific_upgrades(path,category),
            "upgrade_pack_reference":category,
        })
    root_rows=[]
    for path in top_level:
        category=category_for(path)
        meta=CATEGORY_DEFS[category]
        root_rows.append({
            "name":path.name,
            "kind":"directory" if path.is_dir() else "file",
            "category":category,
            "owner_explanation":meta["owner"],
            "user_explanation":meta["user"],
            "investor_explanation":meta["investor"],
            "engineer_explanation":meta["engineer"],
            "30_upgrade_pack_reference":category,
        })
    bots=load_bots(); masters=choose_masters(bots)
    for bot in bots:
        bot["master_slug"]=masters[bot["division"]]
        bot["architecture_role"]="division_master" if bot["slug"]==masters[bot["division"]] else "specialist_under_master"
        bot["merge_policy"]="preserve slug as alias if future evidence supports consolidation"
        bot["upgrade_pack_reference"]="bot_fleet"
    payload={
        "schema":"dreamco.repository_revolution_map.v1",
        "review_status":"recommended_design_and_upgrade_framework_not_a_certification",
        "repo":"DreamCo-Technologies/Dreamcobots",
        "root_item_count":len(root_rows),
        "file_count":len(file_rows),
        "bot_count":len(bots),
        "division_master_count":len(masters),
        "category_count":len(CATEGORY_DEFS),
        "upgrades_per_category":len(UPGRADE_PILLARS),
        "total_category_upgrade_contracts":len(CATEGORY_DEFS)*len(UPGRADE_PILLARS),
        "root_items":root_rows,
        "categories":packs,
        "files":file_rows,
        "bots":bots,
        "category_file_counts":dict(sorted(counts.items())),
        "truth_boundary":"An upgrade recommendation is a design review target, not proof it has already been implemented. File changes still require dependency-aware implementation and tests; bot merges remain reversible until routing/regression evidence passes."
    }
    OUT.parent.mkdir(parents=True,exist_ok=True); REPORT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2)+"\n",encoding="utf-8")
    lines=["# DreamCo Repository Revolution Map","",f"- Root items explained: **{len(root_rows)}**",f"- Files inventoried: **{len(file_rows)}**",f"- Bots inventoried: **{len(bots)}**",f"- Division masters selected: **{len(masters)}**",f"- Upgrade categories: **{len(CATEGORY_DEFS)}**",f"- Upgrades per category: **{len(UPGRADE_PILLARS)}**",f"- Category upgrade contracts: **{len(CATEGORY_DEFS)*len(UPGRADE_PILLARS)}**","","## Top-level repository items",""]
    for row in root_rows:
        lines += [f"### `{row['name']}`",f"- Category: **{CATEGORY_DEFS[row['category']]['label']}**",f"- Owner: {row['owner_explanation']}",f"- Engineer: {row['engineer_explanation']}",f"- Upgrade pack: `{row['30_upgrade_pack_reference']}` (30 upgrades)",""]
    REPORT.write_text("\n".join(lines),encoding="utf-8")
    print(json.dumps({"ok":True,"root_items":len(root_rows),"files":len(file_rows),"bots":len(bots),"categories":len(CATEGORY_DEFS),"upgrades_per_category":len(UPGRADE_PILLARS),"output":str(OUT.relative_to(ROOT))},indent=2))
    return 0

if __name__=="__main__": raise SystemExit(main())
