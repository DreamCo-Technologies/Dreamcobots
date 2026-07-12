#!/usr/bin/env python3
"""Generate build libraries and per-bot integration contracts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "config" / "master_bot_registry.json"
OUTPUT_DIR = ROOT / "config" / "generated" / "system_libraries"

LIBRARY_SPECS = {
    "tools": {
        "schema": "dreamco.tool_library.v1",
        "factory": "Tool Builder",
        "icon": "🔧",
        "description": "Typed, permission-aware tools with tests and audit metadata.",
    },
    "apis": {
        "schema": "dreamco.api_library.v1",
        "factory": "API Builder",
        "icon": "🔌",
        "description": "Versioned per-bot APIs with schemas, rate limits, and approval gates.",
    },
    "webhooks": {
        "schema": "dreamco.webhook_library.v1",
        "factory": "Webhook Builder",
        "icon": "🪝",
        "description": "Signed, idempotent per-bot event contracts with queued processing.",
    },
    "workflows": {
        "schema": "dreamco.workflow_library.v1",
        "factory": "Workflow Builder",
        "icon": "🔁",
        "description": "Reusable validation and delivery workflows with least privilege.",
    },
    "skills": {
        "schema": "dreamco.skill_library.v1",
        "factory": "Skill Builder",
        "icon": "🧠",
        "description": "Versioned multi-step skills with inputs, outputs, evidence, and tests.",
    },
    "sandboxes": {
        "schema": "dreamco.sandbox_library.v1",
        "factory": "Sandbox Builder",
        "icon": "🧪",
        "description": "Isolated test environments with fixtures, limits, and no live money movement.",
    },
}

BUILDERS = [
    {
        "id": "full-bot-system",
        "name": "Full Bot System Builder",
        "icon": "🤖",
        "outputs": ["profile", "blueprint", "tool", "api", "webhook", "workflow", "skill", "sandbox", "tests"],
        "approval": "pull_request_required",
    },
    *[
        {
            "id": f"{name}-builder",
            "name": spec["factory"],
            "icon": spec["icon"],
            "outputs": [name[:-1] if name.endswith("s") else name, "schema", "tests", "documentation"],
            "approval": "pull_request_required",
        }
        for name, spec in LIBRARY_SPECS.items()
    ],
]


def _bot_entry(bot: dict[str, Any], library: str) -> dict[str, Any]:
    slug = bot["slug"]
    common = {
        "id": f"{slug}:{library}",
        "bot_id": slug,
        "legacy_registry_id": bot["id"],
        "bot_slug": slug,
        "bot_name": bot["name"],
        "emoji": bot["emoji"],
        "division": bot["division"],
        "version": "1.0.0",
        "status": "generated",
        "owner": "DreamCo Technologies",
    }
    if library == "apis":
        return {
            **common,
            "base_path": f"/api/v1/bots/{slug}",
            "operations": [
                {"method": "GET", "path": "/status", "approval_required": False},
                {"method": "GET", "path": "/capabilities", "approval_required": False},
                {"method": "POST", "path": "/execute", "approval_required": True},
            ],
            "controls": ["authenticated", "schema_validated", "rate_limited", "retry_after_aware", "audited"],
        }
    if library == "webhooks":
        return {
            **common,
            "path": f"/webhooks/v1/bots/{slug}",
            "events": ["bot.started", "bot.completed", "bot.failed", "approval.requested"],
            "controls": [
                "hmac_sha256_signature",
                "constant_time_compare",
                "delivery_id_deduplication",
                "event_allowlist",
                "respond_within_10_seconds",
                "asynchronous_processing",
            ],
        }
    if library == "workflows":
        return {
            **common,
            "workflow": f"validate-{slug}",
            "trigger": "workflow_call",
            "permissions": {"contents": "read"},
            "stages": ["validate_profile", "unit_test", "sandbox_test", "security_scan", "review_packet"],
        }
    if library == "skills":
        return {
            **common,
            "skill": f"operate-{slug}",
            "inputs": ["goal", "constraints", "evidence"],
            "outputs": ["result", "evidence_log", "approval_requests"],
            "steps": ["plan", "validate", "execute_in_sandbox", "evaluate", "request_review"],
        }
    if library == "sandboxes":
        return {
            **common,
            "sandbox": f"{slug}-sandbox",
            "network": "deny_by_default",
            "secrets": "test_values_only",
            "money_movement": "disabled",
            "checks": ["deterministic_fixtures", "resource_limits", "timeout", "output_validation", "cleanup"],
        }
    return {
        **common,
        "tool": f"{slug}-toolkit",
        "capabilities": [item["intent"] for item in bot["capabilities"]],
        "controls": ["typed_inputs", "typed_outputs", "least_privilege", "audit_log", "unit_tests"],
    }


def build_outputs(registry: dict[str, Any]) -> dict[Path, dict[str, Any]]:
    generated_at = registry["updated_at"]
    bots = registry["bots"]
    outputs: dict[Path, dict[str, Any]] = {}
    summaries = []

    for name, spec in LIBRARY_SPECS.items():
        entries = [_bot_entry(bot, name) for bot in bots]
        payload = {
            "schema": spec["schema"],
            "generated_at": generated_at,
            "generated_from": str(REGISTRY_PATH.relative_to(ROOT)),
            "library": name,
            "factory": spec["factory"],
            "description": spec["description"],
            "count": len(entries),
            "entries": entries,
        }
        outputs[OUTPUT_DIR / f"{name}.json"] = payload
        summaries.append(
            {
                "id": name,
                "name": f"{name.title()} Library",
                "icon": spec["icon"],
                "count": len(entries),
                "description": spec["description"],
                "path": f"config/generated/system_libraries/{name}.json",
            }
        )

    outputs[OUTPUT_DIR / "index.json"] = {
        "schema": "dreamco.system_library_index.v1",
        "generated_at": generated_at,
        "bot_count": len(bots),
        "builders": BUILDERS,
        "libraries": summaries,
        "coverage": {
            "bots_with_tools": len(bots),
            "bots_with_apis": len(bots),
            "bots_with_webhooks": len(bots),
            "bots_with_workflows": len(bots),
            "bots_with_skills": len(bots),
            "bots_with_sandboxes": len(bots),
        },
        "security_baseline": {
            "github_actions": [
                "least_privilege_permissions",
                "immutable_action_references_recommended",
                "untrusted_input_isolated",
            ],
            "apis": [
                "authenticated_requests",
                "conditional_gets",
                "serial_mutations",
                "rate_limit_backoff",
            ],
            "webhooks": [
                "hmac_sha256",
                "delivery_id_deduplication",
                "event_allowlist",
                "fast_ack_then_queue",
            ],
        },
    }
    return outputs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    outputs = build_outputs(registry)

    if args.check:
        stale = []
        for path, payload in outputs.items():
            expected = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
            if not path.exists() or path.read_text(encoding="utf-8") != expected:
                stale.append(str(path.relative_to(ROOT)))
        if stale:
            print("System libraries are stale:")
            for path in stale:
                print(f" - {path}")
            return 1
        print(f"All six libraries cover {len(registry['bots'])} bots.")
        return 0

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for path, payload in outputs.items():
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Generated six system libraries for {len(registry['bots'])} bots.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
