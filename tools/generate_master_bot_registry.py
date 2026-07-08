#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
DIVISIONS_PATH = REPO_ROOT / "config" / "divisions.json"
BOTS_DIR = REPO_ROOT / "bots"
MASTER_REGISTRY_PATH = REPO_ROOT / "config" / "master_bot_registry.json"
CONTROL_TOWER_CATALOG_PATH = REPO_ROOT / "dreamco-control-tower" / "config" / "generated" / "bots.catalog.json"
BLUEPRINT_SCHEMA_PATH = REPO_ROOT / "config" / "bot_blueprint_schema.json"
STORAGE_POLICY_PATH = REPO_ROOT / "config" / "local_first_storage_policy.json"

HIGH_RISK_DIVISIONS = {
    "DreamFinance",
    "DreamEntFinance",
    "DreamCrypto",
    "DreamPayments",
    "DreamLoans",
    "DreamLegal",
    "DreamHealth",
    "DreamCyber",
    "DreamMilitary",
    "DreamProtection",
}

HIGH_RISK_TERMS = {
    "payment",
    "payout",
    "billing",
    "stripe",
    "invoice",
    "trading",
    "trade",
    "crypto",
    "wallet",
    "loan",
    "credit",
    "underwriting",
    "tax",
    "legal",
    "compliance",
    "clinical",
    "health",
    "medical",
    "security",
    "vulnerability",
    "defense",
    "military",
    "campaign",
    "ad",
    "outreach",
    "email",
    "lead",
}

MONEY_TERMS = {
    "payment",
    "payout",
    "billing",
    "invoice",
    "stripe",
    "subscription",
    "checkout",
    "campaign",
    "ad",
    "trading",
    "trade",
    "loan",
    "credit",
    "wallet",
    "crypto",
    "token",
    "cashflow",
    "revenue",
}

OUTREACH_TERMS = {"email", "sms", "outreach", "lead", "crm", "campaign", "social", "ad"}


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower().strip()).strip("-")


def snake(value: str) -> str:
    return slugify(value).replace("-", "_")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def load_divisions() -> list[dict[str, Any]]:
    return load_json(DIVISIONS_PATH)["divisions"]


def load_profiles() -> list[dict[str, Any]]:
    profiles: list[dict[str, Any]] = []
    for profile_path in sorted(BOTS_DIR.glob("*/bot_profile.json")):
        profile = load_json(profile_path)
        slug = str(profile.get("slug") or profile_path.parent.name).strip()
        profile["slug"] = slug
        profile["id"] = snake(slug)
        profile["displayName"] = profile.get("displayName") or slug.replace("-", " ").title()
        profile["profile_path"] = str(profile_path.relative_to(REPO_ROOT))
        profile["repo_path"] = f"./bots/{profile_path.parent.name}"
        profiles.append(profile)
    return profiles


def risk_for(profile: dict[str, Any]) -> str:
    division = str(profile.get("division") or "")
    text = " ".join(
        [
            str(profile.get("slug") or ""),
            str(profile.get("displayName") or ""),
            str(profile.get("category") or ""),
            str(profile.get("description") or ""),
            " ".join(str(item) for item in profile.get("capabilities") or []),
        ]
    ).lower()
    if division in HIGH_RISK_DIVISIONS or any(term in text for term in HIGH_RISK_TERMS):
        return "high"
    if profile.get("revenueModel") or profile.get("priceRange"):
        return "medium"
    return "low"


def capability_object(profile: dict[str, Any], value: str) -> dict[str, Any]:
    intent = slugify(value) or "core"
    text = f"{intent} {profile.get('category', '')} {profile.get('division', '')}".lower()
    risk = "high" if any(term in text for term in HIGH_RISK_TERMS) else risk_for(profile)
    spends_money = any(term in text for term in MONEY_TERMS)
    external_outreach = any(term in text for term in OUTREACH_TERMS)
    revenue_generating = bool(profile.get("revenueModel") or profile.get("priceRange") or spends_money)
    approval_required = risk in {"medium", "high"} or spends_money or external_outreach or revenue_generating
    return {
        "intent": intent,
        "label": str(value),
        "enabled": True,
        "risk_level": risk,
        "approval_required": approval_required,
        "division": profile.get("division"),
        "revenue_generating": revenue_generating,
        "spends_money": spends_money,
        "external_outreach": external_outreach,
    }


def bot_blueprint(profile: dict[str, Any], risk: str) -> dict[str, Any]:
    return {
        "schema": "bot_blueprint.v1",
        "schema_ref": str(BLUEPRINT_SCHEMA_PATH.relative_to(REPO_ROOT)),
        "identity": {
            "id": profile["id"],
            "slug": profile["slug"],
            "displayName": profile["displayName"],
            "division": profile.get("division"),
            "profile_path": profile["profile_path"],
        },
        "runtime": {
            "entrypoints": ["bot.py", "main.py", "index.js"],
            "heartbeat_required": True,
            "default_mode": "assist",
            "max_autonomy_mode": "semi-autonomous" if risk == "low" else "assist",
        },
        "governance": {
            "risk_level": risk,
            "approval_required_for_revenue": True,
            "approval_required_for_spend": True,
            "approval_required_for_external_outreach": True,
            "requires_human_review_before_deployment": True,
            "enterprise_ai_review_status": "not_submitted_to_enterprise_ai",
            "enterprise_ai_approval_claim": False,
        },
        "storage": {
            "policy_ref": str(STORAGE_POLICY_PATH.relative_to(REPO_ROOT)),
            "mode": "local-first",
            "default_store": "local_encrypted_sqlite_or_jsonl",
            "cloud_sync": "opt-in-after-approval",
            "secret_storage": "environment_or_os_keychain_only",
        },
    }


def build_storage_policy(generated_at: str) -> dict[str, Any]:
    return {
        "schema": "local_first_storage_policy.v1",
        "updated_at": generated_at,
        "purpose": "Default persistence policy for DreamCo bots before any cloud or paid automation is enabled.",
        "defaults": {
            "storage_mode": "local-first",
            "cloud_sync": "disabled_by_default",
            "secrets": "never_commit_tokens_or_api_keys; use environment variables or OS keychain",
            "pii": "minimize_collection; encrypt_at_rest; redact_from_logs",
            "financial_data": "read_only_until_human_approval; no autonomous transfers or purchases",
            "audit_logs": "append_only_local_log_with_timestamp_actor_action_result",
            "retention": "keep only what the bot needs; user-controlled deletion required",
        },
        "approval_gates": [
            "external_outreach",
            "paid_campaigns",
            "billing_changes",
            "payouts_or_transfers",
            "credential_changes",
            "cloud_sync_enablement",
            "production_deployment",
        ],
        "required_controls": [
            "human_review_before_money_movement",
            "human_review_before_external_messages",
            "rate_limits_for_all_network_calls",
            "denylist_for_secrets_in_logs",
            "rollback_plan_for_generated_changes",
        ],
    }


def build_blueprint_schema(generated_at: str) -> dict[str, Any]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://dreamco.local/schemas/bot_blueprint.v1.json",
        "title": "DreamCo Bot Blueprint",
        "description": "Governed bot blueprint required for every DreamCo bot before autonomous or revenue workflows can run.",
        "type": "object",
        "additionalProperties": True,
        "required": ["schema", "identity", "runtime", "governance", "storage"],
        "properties": {
            "schema": {"const": "bot_blueprint.v1"},
            "schema_ref": {"type": "string"},
            "identity": {
                "type": "object",
                "required": ["id", "slug", "displayName", "division", "profile_path"],
                "properties": {
                    "id": {"type": "string", "minLength": 1},
                    "slug": {"type": "string", "minLength": 1},
                    "displayName": {"type": "string", "minLength": 1},
                    "division": {"type": "string", "minLength": 1},
                    "profile_path": {"type": "string", "pattern": "^bots/.+/bot_profile\\.json$"},
                },
            },
            "runtime": {
                "type": "object",
                "required": ["heartbeat_required", "default_mode", "max_autonomy_mode"],
                "properties": {
                    "entrypoints": {"type": "array", "items": {"type": "string"}},
                    "heartbeat_required": {"type": "boolean"},
                    "default_mode": {"enum": ["manual", "assist", "semi-autonomous", "autonomous"]},
                    "max_autonomy_mode": {"enum": ["manual", "assist", "semi-autonomous", "autonomous"]},
                },
            },
            "governance": {
                "type": "object",
                "required": [
                    "risk_level",
                    "approval_required_for_revenue",
                    "approval_required_for_spend",
                    "approval_required_for_external_outreach",
                    "requires_human_review_before_deployment",
                    "enterprise_ai_review_status",
                    "enterprise_ai_approval_claim",
                ],
                "properties": {
                    "risk_level": {"enum": ["low", "medium", "high"]},
                    "approval_required_for_revenue": {"type": "boolean"},
                    "approval_required_for_spend": {"type": "boolean"},
                    "approval_required_for_external_outreach": {"type": "boolean"},
                    "requires_human_review_before_deployment": {"type": "boolean"},
                    "enterprise_ai_review_status": {"type": "string"},
                    "enterprise_ai_approval_claim": {"type": "boolean"},
                },
            },
            "storage": {
                "type": "object",
                "required": ["policy_ref", "mode", "default_store", "cloud_sync", "secret_storage"],
                "properties": {
                    "policy_ref": {"type": "string"},
                    "mode": {"const": "local-first"},
                    "default_store": {"type": "string"},
                    "cloud_sync": {"type": "string"},
                    "secret_storage": {"type": "string"},
                },
            },
        },
        "generated_at": generated_at,
    }


def build_registry(generated_at: str) -> tuple[dict[str, Any], dict[str, Any]]:
    divisions = load_divisions()
    profiles = load_profiles()
    division_names = {division["name"] for division in divisions}
    unknown = sorted({profile.get("division") for profile in profiles if profile.get("division") not in division_names})
    if unknown:
        raise ValueError(f"Unknown divisions in bot profiles: {unknown}")

    counts = Counter(profile["division"] for profile in profiles)
    risk_counts: Counter[str] = Counter()
    by_division: dict[str, list[dict[str, Any]]] = defaultdict(list)
    bots: list[dict[str, Any]] = []
    catalog_bots: list[dict[str, Any]] = []

    for profile in profiles:
        risk = risk_for(profile)
        risk_counts[risk] += 1
        raw_caps = [str(cap) for cap in profile.get("capabilities") or [] if str(cap).strip()]
        if not raw_caps:
            raw_caps = [f"{profile['displayName']} core workflow"]
        caps = [capability_object(profile, cap) for cap in raw_caps]
        blueprint = bot_blueprint(profile, risk)
        monetization_enabled = bool(profile.get("revenueModel") or profile.get("priceRange"))
        approval_required = True if monetization_enabled or risk in {"medium", "high"} else any(cap["approval_required"] for cap in caps)
        bot = {
            "id": profile["id"],
            "slug": profile["slug"],
            "name": profile["displayName"],
            "division": profile.get("division"),
            "category": profile.get("category") or profile.get("division"),
            "status": profile.get("status") or "active",
            "version": str(profile.get("version") or "1.0"),
            "tier": str(profile.get("tier") or "standard").upper(),
            "description": profile.get("description") or f"{profile['displayName']} ({profile.get('division')})",
            "repoPath": profile["repo_path"],
            "profile_path": profile["profile_path"],
            "monetization": {
                "enabled": monetization_enabled,
                "revenue_model": profile.get("revenueModel"),
                "price_range": profile.get("priceRange"),
                "approval_required_before_activation": True,
            },
            "safety": {
                "risk_level": risk,
                "approval_required": approval_required,
                "autonomous_cash_enabled": False,
                "human_approval_required_for_money_movement": True,
                "human_approval_required_for_external_outreach": True,
                "enterprise_ai_approval_claim": False,
                "enterprise_ai_review_status": "not_submitted_to_enterprise_ai",
            },
            "capabilities": caps,
            "blueprint": blueprint,
        }
        bots.append(bot)
        by_division[profile["division"]].append(bot)
        catalog_bots.append(
            {
                "bot_id": bot["id"],
                "slug": bot["slug"],
                "name": bot["name"],
                "repoName": "Dreamcobots",
                "repoPath": bot["repoPath"],
                "profilePath": bot["profile_path"],
                "status": bot["status"],
                "tier": bot["tier"],
                "category": bot["division"],
                "description": bot["description"],
                "price_usd": 0,
                "priceRange": bot["monetization"]["price_range"],
                "revenueModel": bot["monetization"]["revenue_model"],
                "features": [cap["intent"] for cap in caps],
                "lastHeartbeat": None,
                "lastUpdate": None,
                "pendingPRs": 0,
                "governance": {
                    "risk_level": risk,
                    "approval_required": approval_required,
                    "monetization_enabled": monetization_enabled,
                    "autonomous_cash_enabled": False,
                    "local_first_storage_policy": str(STORAGE_POLICY_PATH.relative_to(REPO_ROOT)),
                    "blueprint_schema": str(BLUEPRINT_SCHEMA_PATH.relative_to(REPO_ROOT)),
                    "enterprise_ai_approval_claim": False,
                    "enterprise_ai_review_status": "not_submitted_to_enterprise_ai",
                },
            }
        )

    division_payload = []
    for division in divisions:
        division_payload.append(
            {
                **division,
                "bot_count": counts[division["name"]],
                "governance": {
                    "autonomous_cash_enabled": False,
                    "human_approval_required_for_revenue_actions": True,
                    "local_first_storage_policy": str(STORAGE_POLICY_PATH.relative_to(REPO_ROOT)),
                },
            }
        )

    registry = {
        "schema": "master_bot_registry.v2",
        "updated_at": generated_at,
        "generated_from": ["config/divisions.json", "bots/*/bot_profile.json"],
        "repository": "DreamCo-Technologies/Dreamcobots",
        "summary": {
            "division_count": len(divisions),
            "bot_count": len(bots),
            "risk_counts": dict(sorted(risk_counts.items())),
            "autonomous_cash_enabled": False,
            "enterprise_ai_approval_claim": False,
            "enterprise_ai_review_status": "not_submitted_to_enterprise_ai",
        },
        "autonomy_policy": {
            "default_mode": "assist",
            "max_default_mode": "semi-autonomous_for_low_risk_only",
            "autonomous_cash_enabled": False,
            "human_approval_required_for_money_movement": True,
            "human_approval_required_for_paid_campaigns": True,
            "human_approval_required_for_external_outreach": True,
            "human_approval_required_for_high_risk_domains": True,
        },
        "local_first_storage_policy": str(STORAGE_POLICY_PATH.relative_to(REPO_ROOT)),
        "bot_blueprint_schema": str(BLUEPRINT_SCHEMA_PATH.relative_to(REPO_ROOT)),
        "divisions": division_payload,
        "bots": bots,
    }

    catalog = {
        "schema": "generated.control_tower_bots.v2",
        "generated_from": "config/master_bot_registry.json",
        "generated_at": generated_at,
        "editable": False,
        "summary": registry["summary"],
        "local_first_storage_policy": str(STORAGE_POLICY_PATH.relative_to(REPO_ROOT)),
        "bot_blueprint_schema": str(BLUEPRINT_SCHEMA_PATH.relative_to(REPO_ROOT)),
        "divisions": [
            {
                "id": division["id"],
                "name": division["name"],
                "route": division["route"],
                "mission": division["mission"],
                "bot_count": counts[division["name"]],
            }
            for division in divisions
        ],
        "bots": catalog_bots,
    }
    return registry, catalog


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate DreamCo master bot registry and control tower catalog.")
    parser.add_argument("--check", action="store_true", help="Validate generated output matches files on disk.")
    args = parser.parse_args()

    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    if MASTER_REGISTRY_PATH.exists():
        try:
            generated_at = load_json(MASTER_REGISTRY_PATH).get("updated_at") or generated_at
        except Exception:
            pass

    storage_policy = build_storage_policy(generated_at)
    blueprint_schema = build_blueprint_schema(generated_at)
    registry, catalog = build_registry(generated_at)

    outputs = {
        STORAGE_POLICY_PATH: storage_policy,
        BLUEPRINT_SCHEMA_PATH: blueprint_schema,
        MASTER_REGISTRY_PATH: registry,
        CONTROL_TOWER_CATALOG_PATH: catalog,
    }

    if args.check:
        mismatches = []
        for path, payload in outputs.items():
            expected = json.dumps(payload, indent=2, sort_keys=False) + "\n"
            actual = path.read_text(encoding="utf-8") if path.exists() else None
            if actual != expected:
                mismatches.append(str(path.relative_to(REPO_ROOT)))
        if mismatches:
            print("Generated files are out of date:")
            for item in mismatches:
                print(f" - {item}")
            return 1
        print("Generated registry artifacts are up to date.")
        return 0

    for path, payload in outputs.items():
        write_json(path, payload)
    print(
        f"Generated {len(registry['bots'])} bots across {len(registry['divisions'])} divisions "
        f"into {MASTER_REGISTRY_PATH.relative_to(REPO_ROOT)} and {CONTROL_TOWER_CATALOG_PATH.relative_to(REPO_ROOT)}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
