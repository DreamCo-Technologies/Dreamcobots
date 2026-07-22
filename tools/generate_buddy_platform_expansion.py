#!/usr/bin/env python3
"""Generate Buddy's governed platform registry and two 100-idea roadmaps."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dreamco_platform.customization import build_asset_catalog
from dreamco_platform.launch import StoreTarget


CONFIG_OUT = ROOT / "config" / "generated" / "buddy_platform_expansion.json"
WEB_OUT = ROOT / "website" / "data" / "buddy-platform-expansion.json"
REPORT_OUT = ROOT / "reports" / "BUDDY_PLATFORM_EXPANSION.md"


IMPLEMENTED_CAPABILITIES = [
    ("business_launchpad", "Business formation planning", "official_handoff_required", "dreamco_platform/launch/launchpad.py"),
    ("prototype_factory", "Prompt-to-prototype build plan", "local_build_ready", "dreamco_platform/launch/launchpad.py"),
    ("app_release_council", "Web and app-store release evidence council", "owner_submission_required", "dreamco_platform/launch/launchpad.py"),
    ("distribution_service", "Multi-device packaging and publishing service", "web_ready_native_review_required", "dreamco_platform/launch/distribution.py"),
    ("governed_lead_system", "Permission-gated lead discovery and follow-up", "sandbox_ready_external_adapters_required", "server/governed-leads.ts"),
    ("data_wallet", "Consent, portability, opt-out, and licensed-data controls", "local_core_ready", "dreamco_platform/privacy/data_wallet.py"),
    ("bill_subscription_manager", "Bill and subscription tracking", "owner_payment_required", "dreamco_platform/finance/subscriptions.py"),
    ("task_runner", "Concurrent and timed tasks up to 24 hours", "adapter_ready", "dreamco_platform/automation/task_runner.py"),
    ("creative_studio", "Games, courses, films, music, brands, and learning media", "local_prototype_ready", "dreamco_platform/creative/studio.py"),
    ("music_artist_studio", "Rights-aware artist development and original music packets", "local_core_ready", "dreamco_platform/creative/music.py"),
    ("logo_generator", "Editable original SVG logo concepts", "local_core_ready", "dreamco_platform/creative/branding.py"),
    ("ip_assistant", "Patent, trademark, and copyright search and draft packets", "official_filing_required", "dreamco_platform/legal_ip/assistant.py"),
    ("open_source_lab", "Read-only repository inspection and sandbox upgrade plans", "local_core_ready", "dreamco_platform/opensource/lab.py"),
    ("buddy_customization", "Traceable user-owned Buddy identity and personality", "local_core_ready", "dreamco_platform/customization/profile.py"),
    ("free_asset_presets", "Original voice-parameter and avatar presets", "renderer_required", "dreamco_platform/customization/profile.py"),
    ("bot_fleet", "Shared governed execution for every cataloged bot", "sandbox_certified", "server/fleet-runtime.ts"),
]

REVOLUTIONARY_THEMES = [
    ("personal_os", "personal operating system", "combine tasks, files, calendars, and approvals into one owner-controlled workspace"),
    ("business_launch", "business launch", "turn an idea into a formation, prototype, launch, and compliance checklist"),
    ("vibe_development", "vibe development", "convert plain language into reversible code changes with tests and live previews"),
    ("open_source", "open-source upgrades", "evaluate licensed repositories inside disposable sandboxes before adoption"),
    ("app_distribution", "app distribution", "prepare one evidence package for web, desktop, mobile, game, and custom stores"),
    ("creative_film", "film production", "coordinate screenplay, continuity, rights, accessibility, editing, and delivery"),
    ("music_artist", "music and artist development", "develop original work, rights records, releases, and audience experiments"),
    ("education", "education", "turn lessons and research into adaptive courses, games, simulations, and assessments"),
    ("simulation", "simulation", "model business, science, logistics, training, and operational decisions before acting"),
    ("privacy", "privacy", "give people a portable data wallet with granular consent, expiration, deletion, and opt-out"),
    ("data_value", "user-owned data value", "package only licensed nonsensitive data with transparent buyers and revocable permission"),
    ("finance", "personal finance operations", "organize bills, subscriptions, forecasts, alerts, and exact-action approvals"),
    ("ip_rights", "intellectual-property workflows", "connect source logs, clearance searches, rights manifests, and official filing handoffs"),
    ("accessibility", "accessibility", "generate captions, descriptions, keyboard paths, reading modes, and adaptation tests by default"),
    ("local_ai", "local AI", "route private or low-cost tasks to device models with measurable quality and energy budgets"),
    ("model_router", "model routing", "benchmark user-selected models by task, privacy, latency, quality, and cost"),
    ("trust", "trust and governance", "show provenance, permissions, uncertainty, checkpoints, and receipts for every consequential action"),
    ("marketplace", "capability marketplace", "let owners install, test, rate, revoke, and export licensed Buddy upgrades"),
    ("collaboration", "human and agent collaboration", "coordinate specialists through shared plans, debate, evidence, and final owner control"),
    ("device_fleet", "device continuity", "move an encrypted task state across owner-approved phones, computers, displays, and local devices"),
]

REVOLUTIONARY_PATTERNS = [
    ("copilot", "Build a guided copilot that can {outcome}.", "guided"),
    ("sandbox", "Create a no-side-effect sandbox that can {outcome}.", "sandbox"),
    ("evidence", "Attach an evidence ledger that proves how Buddy can {outcome}.", "evidence"),
    ("automation", "Add an approval-aware automation that can {outcome}.", "automation"),
    ("marketplace", "Package a portable capability that lets user-owned Buddy instances {outcome}.", "marketplace"),
]

COMPANION_THEMES = [
    ("morning", "morning planning", "help the user choose a realistic day without pressure"),
    ("focus", "focus sessions", "reduce a large goal to one calm next action"),
    ("learning", "learning", "remember preferred explanations and create low-stakes practice"),
    ("work", "work", "prepare context, drafts, and decisions while keeping the user in control"),
    ("money", "money goals", "surface lawful options, tradeoffs, and risks without promising earnings"),
    ("business", "business moments", "switch to clear professional language and preserve commitments"),
    ("creative", "creative blocks", "offer contrasting directions and save unfinished ideas without judgment"),
    ("family", "family coordination", "organize shared plans without exposing one person's private information"),
    ("home", "home routines", "track maintenance and recurring chores with gentle timing"),
    ("health", "well-being", "support routines while deferring diagnosis and urgent care to qualified humans"),
    ("travel", "travel", "prepare accessible plans, documents, budgets, and contingencies"),
    ("career", "career growth", "practice interviews, map skills, and record evidence of progress"),
    ("celebration", "celebrations", "notice milestones without manipulating engagement"),
    ("stress", "stressful moments", "slow down, summarize facts, and avoid adding urgency"),
    ("memory", "personal memory", "save only useful owner-approved facts with expiration and deletion controls"),
    ("communication", "communication", "adapt tone and slang while remaining truthful about being an AI"),
    ("access", "access needs", "adapt pace, format, contrast, captions, and input methods"),
    ("reflection", "reflection", "help the user review what worked and change what did not"),
    ("safety", "safety", "notice risky requests, explain boundaries, and find a constructive alternative"),
    ("goodbye", "handoffs and pauses", "save a clean checkpoint and make it easy to resume later"),
]

COMPANION_PATTERNS = [
    ("check_in", "Offer an optional check-in during {theme} that can {outcome}.", "opt_in"),
    ("preference", "Learn a revocable preference for {theme} to {outcome}.", "preference"),
    ("ritual", "Create a user-configured ritual for {theme} to {outcome}.", "ritual"),
    ("reflection", "Provide a private reflection view for {theme} to {outcome}.", "reflection"),
    ("handoff", "Prepare an owner-approved handoff for {theme} to {outcome}.", "handoff"),
]


def build_ideas(themes: list[tuple[str, str, str]], patterns: list[tuple[str, str, str]], prefix: str) -> list[dict]:
    ideas = []
    for theme_id, theme, outcome in themes:
        for pattern_id, template, kind in patterns:
            ideas.append({
                "id": f"{prefix}-{theme_id}-{pattern_id}",
                "theme": theme,
                "kind": kind,
                "idea": template.format(theme=theme, outcome=outcome),
                "status": "roadmap_not_implemented",
                "approval_default": "ask_first",
            })
    return ideas


def build_registry() -> dict:
    revolutionary = build_ideas(REVOLUTIONARY_THEMES, REVOLUTIONARY_PATTERNS, "innovation")
    companion = build_ideas(COMPANION_THEMES, COMPANION_PATTERNS, "companion")
    assert len(revolutionary) == 100 and len(companion) == 100
    return {
        "schema": "dreamco.buddy_platform_expansion.v1",
        "name": "Buddy Governed Capability Platform",
        "truth_contract": {
            "implemented": "Repository code and tests exist for the local or planning core.",
            "configuration_required": "A provider account, secret, deployed adapter, or official review is still required.",
            "roadmap_not_implemented": "An evaluated product idea, not a current capability claim.",
        },
        "implemented_capabilities": [
            {"id": capability_id, "name": name, "status": status, "evidence": evidence}
            for capability_id, name, status, evidence in IMPLEMENTED_CAPABILITIES
        ],
        "release_targets": [target.value for target in StoreTarget],
        "free_asset_catalog": build_asset_catalog(),
        "revolutionary_ideas": revolutionary,
        "companion_ideas": companion,
        "guardrails": [
            "ask before every consequential external action",
            "never claim guaranteed income, legal approval, store acceptance, or completed payment",
            "do not sell or license sensitive personal data or minor data",
            "make collection, training, sale, sharing, deletion, and export separate user choices",
            "use only self-owned adult voice and likeness with active consent and visible labeling",
            "keep professional language for business, legal, medical, financial, emergency, and government contexts",
            "inspect open-source code before execution and preserve license obligations",
            "limit one scheduled task to 24 hours and make long-running work cancellable",
        ],
        "counts": {
            "implemented_capability_contracts": len(IMPLEMENTED_CAPABILITIES),
            "release_targets": len(StoreTarget),
            "free_voice_presets": len(build_asset_catalog()["voices"]),
            "free_avatar_presets": len(build_asset_catalog()["avatars"]),
            "revolutionary_roadmap_ideas": len(revolutionary),
            "companion_roadmap_ideas": len(companion),
        },
    }


def report(registry: dict) -> str:
    lines = [
        "# Buddy Platform Expansion",
        "",
        "This registry distinguishes repository-controlled capability cores from official external actions and future product ideas.",
        "",
        "## Implemented Capability Contracts",
        "",
    ]
    lines.extend(
        f"- `{item['id']}`: {item['name']} (`{item['status']}`)"
        for item in registry["implemented_capabilities"]
    )
    lines.extend([
        "",
        "## Roadmap",
        "",
        f"- Revolutionary ideas: {registry['counts']['revolutionary_roadmap_ideas']}",
        f"- Best-friend experience ideas: {registry['counts']['companion_roadmap_ideas']}",
        "- Every roadmap item is explicitly marked `roadmap_not_implemented`.",
        "",
        "## Guardrails",
        "",
    ])
    lines.extend(f"- {item}" for item in registry["guardrails"])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    registry = build_registry()
    expected_json = json.dumps(registry, indent=2, sort_keys=True) + "\n"
    expected_report = report(registry)
    if args.check:
        for path, expected in ((CONFIG_OUT, expected_json), (WEB_OUT, expected_json), (REPORT_OUT, expected_report)):
            if not path.exists() or path.read_text(encoding="utf-8") != expected:
                raise SystemExit(f"Generated output is stale: {path.relative_to(ROOT)}")
        print(json.dumps({"ok": True, **registry["counts"]}, indent=2))
        return 0
    for path in (CONFIG_OUT, WEB_OUT, REPORT_OUT):
        path.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_OUT.write_text(expected_json, encoding="utf-8")
    WEB_OUT.write_text(expected_json, encoding="utf-8")
    REPORT_OUT.write_text(expected_report, encoding="utf-8")
    print(json.dumps({"ok": True, **registry["counts"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
