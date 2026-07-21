#!/usr/bin/env python3
"""Generate Buddy creator-studio, model-choice, and restored bot-family bridge files."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


BOT_FAMILIES = [
    {
        "id": "fiverr_bots",
        "label": "Fiverr and freelance business bots",
        "paths": ["Fiverr_bots", "bots/fiverr_bot"],
        "buddy_jobs": [
            "gig package builder",
            "buyer persona mapper",
            "proposal writer",
            "pricing optimizer",
            "client follow-up planner",
            "portfolio builder",
            "delivery checklist generator",
        ],
        "approval_required": ["sending messages", "placing bids", "changing public gig listings", "collecting payment"],
    },
    {
        "id": "real_estate_bots",
        "label": "Real estate, rental, foreclosure, and property bots",
        "paths": ["Real_Estate_bots", "bots/real_estate_bot", "bots/foreclosure_finder_bot", "bots/home_buyer_bot"],
        "buddy_jobs": [
            "deal analyzer",
            "cash-flow simulator",
            "property valuation packet",
            "renovation estimate packet",
            "rental comparison",
            "foreclosure research packet",
            "buyer checklist",
        ],
        "approval_required": ["contacting owners", "submitting offers", "signing documents", "financial advice", "regulated screening"],
    },
    {
        "id": "government_contract_bots",
        "label": "Government contract, grant, and procurement bots",
        "paths": ["Government_Contract_bots", "bots/government_contract_grant_bot"],
        "buddy_jobs": [
            "contract opportunity scanner",
            "grant fit checklist",
            "capability statement draft",
            "proposal compliance matrix",
            "past performance packet",
            "bid/no-bid rubric",
        ],
        "approval_required": ["submitting bids", "certifying facts", "using official accounts", "binding signatures"],
    },
    {
        "id": "business_bots",
        "label": "Business launch, operations, and professional service bots",
        "paths": ["Business_bots", "BusinessLaunchPad", "Business_Launch_Pad", "bots/business_plan_bot"],
        "buddy_jobs": [
            "business plan draft",
            "LLC launch checklist",
            "expense tracker",
            "vendor comparison",
            "KPI dashboard",
            "pricing strategy",
            "contract packet draft",
        ],
        "approval_required": ["legal filings", "tax claims", "vendor contracts", "payroll changes"],
    },
    {
        "id": "marketing_bots",
        "label": "Marketing, lead generation, SEO, and content bots",
        "paths": ["Marketing_bots", "bots/lead_generator_bot", "bots/social_media_manager_bot"],
        "buddy_jobs": [
            "landing page draft",
            "SEO task packet",
            "campaign brief",
            "ad copy variants",
            "lead magnet outline",
            "review response draft",
            "social content calendar",
        ],
        "approval_required": ["sending outreach", "posting publicly", "ad spend", "endorsement claims"],
    },
    {
        "id": "occupational_bots",
        "label": "Career, jobs, side hustle, and occupational bots",
        "paths": ["Occupational_bots", "bots/job_application_bot", "bots/resume_builder_bot"],
        "buddy_jobs": [
            "resume packet",
            "cover letter draft",
            "job fit checklist",
            "salary negotiation prep",
            "skills gap plan",
            "relocation comparison",
        ],
        "approval_required": ["submitting applications", "background checks", "people lookup", "employment decisions"],
    },
    {
        "id": "creative_and_app_bots",
        "label": "Creative, app, game, music, video, and simulation bots",
        "paths": ["original-bots/app-category-python/App_bots", "bots/app_builder_bot", "bots/creative_studio_bot"],
        "buddy_jobs": [
            "music video production packet",
            "kids learning video packet",
            "college course module",
            "video game design doc",
            "3D simulation brief",
            "voice and image consent checklist",
            "export/deploy plan",
        ],
        "approval_required": ["voice/likeness cloning", "minor-related media", "public publishing", "paid asset licensing"],
    },
]


MODEL_CHOICES = [
    {
        "id": "openai",
        "provider": "OpenAI",
        "modalities": ["text", "code", "vision", "image", "realtime_voice", "tools"],
        "best_for": ["coding", "debugging", "agent tools", "image generation", "multimodal Buddy chat"],
        "watchouts": ["verify current model IDs and prices before production", "use budget caps for paid calls"],
        "docs": "https://platform.openai.com/docs/models",
    },
    {
        "id": "google_gemini",
        "provider": "Google Gemini",
        "modalities": ["text", "code", "vision", "audio", "video", "long_context"],
        "best_for": ["course building", "long documents", "video understanding", "budget Flash-class routing"],
        "watchouts": ["verify current model IDs in AI Studio before production", "privacy review before uploading client media"],
        "docs": "https://ai.google.dev/gemini-api/docs/models",
    },
    {
        "id": "anthropic_claude",
        "provider": "Anthropic Claude",
        "modalities": ["text", "code", "vision", "long_context", "computer_use"],
        "best_for": ["careful reasoning", "long-form review", "policy/safety review", "complex refactors"],
        "watchouts": ["tool execution must be explicitly wired", "current model IDs and rate limits change"],
        "docs": "https://docs.anthropic.com/en/docs/about-claude/models",
    },
    {
        "id": "meta_llama",
        "provider": "Meta Llama",
        "modalities": ["text", "code", "open_weight"],
        "best_for": ["local/private tasks", "low-cost experiments", "self-hosted assistants"],
        "watchouts": ["hosting and safety evals required before client use"],
        "docs": "https://llama.meta.com/docs/",
    },
    {
        "id": "mistral",
        "provider": "Mistral AI",
        "modalities": ["text", "code", "multilingual", "open_weight"],
        "best_for": ["fast drafts", "European language workflows", "cost-aware agents"],
        "watchouts": ["verify model availability before routing"],
        "docs": "https://docs.mistral.ai/getting-started/models/",
    },
    {
        "id": "deepseek",
        "provider": "DeepSeek",
        "modalities": ["text", "code", "reasoning"],
        "best_for": ["coding drafts", "math-like reasoning", "low-cost code comparison"],
        "watchouts": ["production fixes still need tests and review"],
        "docs": "https://api-docs.deepseek.com/",
    },
    {
        "id": "qwen",
        "provider": "Qwen",
        "modalities": ["text", "code", "vision", "open_weight"],
        "best_for": ["multilingual apps", "open model experiments", "coding alternatives"],
        "watchouts": ["route through approved host only"],
        "docs": "https://qwen.readthedocs.io/",
    },
    {
        "id": "huggingface",
        "provider": "Hugging Face",
        "modalities": ["open_models", "datasets", "embeddings", "vision", "audio"],
        "best_for": ["model discovery", "dataset cards", "local experiments", "specialized models"],
        "watchouts": ["check license and commercial use rights per model/dataset"],
        "docs": "https://huggingface.co/docs",
    },
    {
        "id": "stability",
        "provider": "Stability AI",
        "modalities": ["image", "3d_assets"],
        "best_for": ["image variants", "textures", "game concept assets"],
        "watchouts": ["rights-sensitive likeness rules still apply"],
        "docs": "https://platform.stability.ai/docs",
    },
    {
        "id": "runway",
        "provider": "Runway",
        "modalities": ["video", "image", "creative_media"],
        "best_for": ["video storyboards", "music video concepts", "short creative clips"],
        "watchouts": ["public publishing and likeness use require approval"],
        "docs": "https://docs.dev.runwayml.com/",
    },
    {
        "id": "elevenlabs_optional",
        "provider": "ElevenLabs optional",
        "modalities": ["voice", "tts", "dubbing"],
        "best_for": ["voiceover", "narration", "audio localization"],
        "watchouts": ["not required for Buddy local voice; real-person cloning requires explicit written consent"],
        "docs": "https://elevenlabs.io/docs",
    },
    {
        "id": "local_browser",
        "provider": "DreamCo Local",
        "modalities": ["browser_tts", "local_svg_image", "offline_packet_generation"],
        "best_for": ["free tests", "kids demos", "local previews", "no-key fallback"],
        "watchouts": ["not a full AI provider; use as offline fallback and preview layer"],
        "docs": "reports/ORIGINAL_CODE_RECOVERY.md",
    },
]


CREATOR_STUDIO = {
    "schema": "dreamco.buddy_creator_studio.v1",
    "mission": "Let Buddy help users build games, 3D simulations, college courses, kids learning projects, music videos, apps, websites, and bot businesses with model choice, consent checks, and sandbox-first workflows.",
    "default_mode": "sandbox_first_owner_approval_for_publish_or_paid_actions",
    "workflows": [
        {
            "id": "college_3d_simulation_course",
            "label": "College 3D Simulation Course Builder",
            "outputs": ["syllabus", "module map", "lesson plan", "3D scene spec", "assessment rubric", "starter code", "accessibility checklist"],
            "engines": ["Three.js", "React Three Fiber", "Unity export plan", "WebXR optional", "physics sandbox"],
            "buddy_steps": [
                "collect learning objectives",
                "choose age/college level",
                "generate 3D concept map",
                "build browser prototype",
                "create quiz/lab/rubric",
                "run accessibility and safety review",
                "package for LMS or website",
            ],
        },
        {
            "id": "kids_voice_image_game_builder",
            "label": "Kids Voice/Image Game Builder",
            "outputs": ["guardian consent checklist", "kid-safe game design doc", "character sheet", "voice preference packet", "image asset plan", "playable prototype checklist"],
            "engines": ["Three.js", "Phaser", "Canvas", "local browser speech synthesis", "local SVG fallback"],
            "buddy_steps": [
                "collect parent/guardian approval requirements",
                "avoid real-person cloning unless consent proof exists",
                "create age-safe mechanics",
                "generate local preview assets",
                "test controls on desktop/mobile",
                "prepare export and share packet",
            ],
        },
        {
            "id": "music_video_and_simulation_studio",
            "label": "Music Video And Simulation Studio",
            "outputs": ["concept", "script", "shot list", "storyboard", "asset list", "voice rights packet", "video generation prompt pack", "edit timeline"],
            "engines": ["Runway optional", "local storyboard", "image model choice", "voice model choice", "browser preview"],
            "buddy_steps": [
                "collect rights-safe concept",
                "block artist/celebrity imitation",
                "draft scenes and prompts",
                "generate or request assets",
                "assemble review checklist",
                "prepare export plan",
            ],
        },
        {
            "id": "game_app_store_builder",
            "label": "Game/App Store Builder",
            "outputs": ["game design doc", "prototype route", "asset manifest", "monetization plan", "store listing draft", "test checklist"],
            "engines": ["Phaser", "Three.js", "Vite", "PWA", "Capacitor export plan"],
            "buddy_steps": [
                "define genre and platform",
                "create prototype",
                "wire local save/settings",
                "run playtest checklist",
                "draft store listing",
                "gate publishing behind approval",
            ],
        },
    ],
    "guardrails": [
        "No cloning real voices, faces, likenesses, or images without explicit written consent.",
        "No minor voice or likeness cloning.",
        "Always label AI-generated or AI-edited media.",
        "Public publishing, paid model calls, app store submissions, customer outreach, and payment actions require owner approval.",
        "Kids and education content must include age range, safety level, accessibility review, and parent/teacher notes.",
    ],
}


def count_files(paths: list[str], suffixes: tuple[str, ...]) -> int:
    count = 0
    for raw_path in paths:
        path = ROOT / raw_path
        if not path.exists():
            continue
        count += sum(1 for item in path.rglob("*") if item.is_file() and item.name.endswith(suffixes))
    return count


def load_issue_summary() -> dict:
    path = ROOT / "config/github_goal_consolidation.json"
    if not path.exists():
        return {"issues": [], "pull_requests": []}
    data = json.loads(path.read_text())
    return {
        "pull_requests": [
            {
                "number": pr.get("number"),
                "title": pr.get("title"),
                "decision": pr.get("decision"),
                "still_needed": pr.get("still_needed", []),
            }
            for pr in data.get("pull_requests", [])[:10]
        ],
        "issues": [
            {
                "number": issue.get("number"),
                "title": issue.get("title"),
                "decision": issue.get("decision"),
                "still_needed": issue.get("still_needed", []),
            }
            for issue in data.get("issues", [])[:10]
        ],
    }


def main() -> None:
    generated_at = datetime.now(timezone.utc).isoformat()
    family_records = []
    for family in BOT_FAMILIES:
        family_records.append({
            **family,
            "file_count": count_files(family["paths"], (".py", ".json", ".md", ".ts", ".tsx", ".js", ".jsx")),
            "python_count": count_files(family["paths"], (".py",)),
            "profile_count": count_files(family["paths"], ("bot_profile.json",)),
            "buddy_status": "connected_to_buddy_capability_bridge",
        })

    bridge = {
        "schema": "dreamco.buddy_restored_bot_family_bridge.v1",
        "generated_at": generated_at,
        "mission": "Make every restored original bot family discoverable by Buddy and route task requests to the right restored code tree.",
        "source": "Recovered from earlier DreamCo repository history and current recovery branch.",
        "totals": {
            "families": len(family_records),
            "files": sum(item["file_count"] for item in family_records),
            "python_files": sum(item["python_count"] for item in family_records),
            "bot_profiles": sum(item["profile_count"] for item in family_records),
        },
        "families": family_records,
        "github_issue_goal_bridge": load_issue_summary(),
    }

    model_registry = {
        "schema": "dreamco.buddy_user_model_choice_registry.v1",
        "generated_at": generated_at,
        "mission": "Let users choose the AI provider/model family Buddy uses, while Buddy explains strengths, weaknesses, cost posture, and safety gates.",
        "currentness_policy": "Provider model IDs, availability, pricing, and rate limits change often. Verify official docs before production routing.",
        "selection_modes": ["user_choice", "buddy_recommended", "budget_first", "quality_first", "privacy_first", "creative_media", "coding_debugging"],
        "default_choice": "buddy_recommended",
        "choices": MODEL_CHOICES,
    }

    config_dir = ROOT / "config"
    report_dir = ROOT / "reports"
    config_dir.mkdir(exist_ok=True)
    report_dir.mkdir(exist_ok=True)
    (config_dir / "buddy_creator_studio.json").write_text(json.dumps(CREATOR_STUDIO | {"generated_at": generated_at}, indent=2) + "\n")
    (config_dir / "buddy_user_model_choice_registry.json").write_text(json.dumps(model_registry, indent=2) + "\n")
    (config_dir / "buddy_restored_bot_family_bridge.json").write_text(json.dumps(bridge, indent=2) + "\n")

    report_lines = [
        "# Buddy Creator, Model Choice, And Restored Bot Bridge",
        "",
        f"Generated: {generated_at}",
        "",
        "## Restored Bot Families Connected To Buddy",
        "",
    ]
    for family in family_records:
        report_lines.append(f"- {family['label']}: {family['file_count']} files, {family['python_count']} Python files, {family['profile_count']} profiles.")
    report_lines += [
        "",
        "## Creator Studio Workflows",
        "",
    ]
    for workflow in CREATOR_STUDIO["workflows"]:
        report_lines.append(f"- {workflow['label']}: {', '.join(workflow['outputs'][:4])}.")
    report_lines += [
        "",
        "## Model Choice",
        "",
        f"- Choices available: {len(MODEL_CHOICES)}",
        "- Default: Buddy recommends the safest and cheapest capable route, but users can choose another configured provider.",
        "- Paid calls, publishing, training, cloning, outreach, and live money actions stay behind approval gates.",
        "",
        "## Issue/PR Goal Bridge",
        "",
    ]
    issue_summary = load_issue_summary()
    for issue in issue_summary["issues"][:5]:
        report_lines.append(f"- Issue #{issue['number']} {issue['title']}: {issue['decision']}.")
    for pr in issue_summary["pull_requests"][:5]:
        report_lines.append(f"- PR #{pr['number']} {pr['title']}: {pr['decision']}.")
    report_lines.append("")
    (report_dir / "BUDDY_CREATOR_MODEL_BRIDGE.md").write_text("\n".join(report_lines))
    print(json.dumps({"ok": True, "families": len(family_records), "model_choices": len(MODEL_CHOICES)}, indent=2))


if __name__ == "__main__":
    main()
