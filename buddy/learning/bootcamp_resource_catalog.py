"""Categorize repository resources and build user-selected bootcamp plans."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[2]
POLICY = json.loads((ROOT / "config/buddy-bootcamp-resource-policy.json").read_text(encoding="utf-8"))
CATEGORIES = {row["id"]: row["label"] for row in POLICY["categories"]}


def _category_for(host: str, source_lists: list[str], explicit: str | None = None) -> tuple[str, str]:
    if explicit:
        return explicit, "resource_registry"
    haystack = (host + " " + " ".join(source_lists)).lower()
    if any(token in haystack for token in ("huggingface", "hugging-face", "dataset", "training", "lora", "model")):
        return "datasets_and_training" if any(token in haystack for token in ("dataset", "training", "lora")) else "ai_models_and_providers", "source_metadata"
    if any(token in haystack for token in ("github.com", "gitlab.com", "codeberg.org", "repository", "repo", "source_code", "open_source")):
        return "code_repositories_and_tools", "host_or_source_metadata"
    if any(token in haystack for token in (".gov", ".mil", "government", "america_gov", "public_data")):
        return "government_and_public_data", "host_or_source_metadata"
    if any(token in haystack for token in ("wikipedia", "wikimedia", "arxiv", "research", ".edu", "university", "study_resources", "bootcamp", "curriculum")):
        return "research_and_education", "host_or_source_metadata"
    if any(token in haystack for token in ("health", "medical", "clinic", "hospital", "wellness", "cdc", "fda")):
        return "health_and_wellness", "host_or_source_metadata"
    if any(token in haystack for token in ("security", "owasp", "cisa", "mitre", "privacy", "nvd")):
        return "security_and_privacy", "host_or_source_metadata"
    if any(token in haystack for token in ("finance", "bank", "treasury", "sec.gov", "business", "market", "economic")):
        return "business_and_finance", "host_or_source_metadata"
    if any(token in haystack for token in ("music", "video", "media", "creator", "design", "image", "audio")):
        return "creative_and_media", "host_or_source_metadata"
    if any(token in haystack for token in ("211", "food_pantry", "community", "local_resource", "housing", "workforce")):
        return "local_and_community_resources", "host_or_source_metadata"
    if any(token in haystack for token in ("docs.", "developer", "api", "documentation", "reference", "standard")):
        return "general_learning_and_reference", "host_or_source_metadata"
    return "other_needs_review", "fallback_review_required"


def build_catalog(connection_catalog: dict[str, Any], resource_registry: dict[str, Any]) -> dict[str, Any]:
    entries: dict[str, dict[str, Any]] = {}
    for item in connection_catalog.get("resources", []):
        host = str(item.get("host") or "").lower()
        if not host:
            continue
        rid = str(item.get("id") or "resource:" + host)
        category, evidence = _category_for(host, list(item.get("source_lists") or []))
        entries[rid] = {
            "id": rid,
            "name": host,
            "url": item.get("primary_url"),
            "category": category,
            "category_label": CATEGORIES[category],
            "category_evidence": evidence,
            "resource_kind": "external_reference",
            "source_lists": sorted(set(item.get("source_lists") or [])),
            "connection_status": item.get("connection_status", "connection_request_required"),
            "rights_status": "unknown",
            "training_allowed": False,
            "live_verified": False,
            "selection_available": True,
        }

    for item in resource_registry.get("resources", []):
        rid = item.get("id")
        if not isinstance(rid, str) or not rid:
            continue
        category_aliases = {
            "model_provider": "ai_models_and_providers", "model_catalog": "ai_models_and_providers",
            "compute": "ai_models_and_providers", "dataset": "datasets_and_training",
            "benchmark": "benchmarks_and_evaluation", "github_platform": "code_repositories_and_tools",
            "repo_tool": "code_repositories_and_tools", "code": "code_repositories_and_tools",
            "secret_inventory": "security_and_privacy", "terms_constraint": "security_and_privacy",
            "workforce": "research_and_education",
        }
        explicit_category = item.get("category")
        category = explicit_category if explicit_category in CATEGORIES else category_aliases.get(explicit_category, "other_needs_review")
        url = item.get("source_url") or next((
            ref for ref in item.get("wired_into", [])
            if isinstance(ref, str) and ref.startswith("https://")
        ), None)
        if not url:
            url = "https://github.com/DreamCo-Technologies/Dreamcobots"
        entries["registry:" + rid] = {
            "id": "registry:" + rid,
            "name": item["name"],
            "url": url,
            "category": category,
            "category_label": CATEGORIES[category],
            "category_evidence": "resource_registry",
            "resource_kind": item.get("category", "governed_resource"),
            "source_lists": ["config/buddy/resource-registry.json"],
            "connection_status": item.get("connection_status", "unknown"),
            "rights_status": "review_required" if item.get("connection_status") == "blocked_by_license" else "unknown",
            "training_allowed": False,
            "live_verified": item.get("connection_status") == "connected",
            "selection_available": True,
            "blocker": item.get("blocker"),
            "gives_buddy": item.get("gives_buddy"),
        }

    rea = POLICY["rea_reference"]
    entries[rea["id"]] = {
        "id": rea["id"],
        "name": rea["name"],
        "url": rea["url"],
        "category": "code_repositories_and_tools",
        "category_label": CATEGORIES["code_repositories_and_tools"],
        "category_evidence": "official_repository_reference",
        "resource_kind": "external_open_source_tool",
        "source_lists": ["config/buddy-bootcamp-resource-policy.json"],
        "connection_status": rea["connection_status"],
        "rights_status": rea["license_status"],
        "training_allowed": False,
        "live_verified": False,
        "selection_available": True,
        "capabilities": ["static repository analysis", "website behavior analysis", "application and binary analysis via external adapters"],
        "setup_reference": rea["url"],
        "safety_boundary": "Do not install or run the external tool until the owner reviews its current code, release, license, dependencies, security, and target authorization.",
    }

    rows = sorted(entries.values(), key=lambda row: (row["category_label"].lower(), row["name"].lower(), row["id"]))
    category_counts = {key: sum(row["category"] == key for row in rows) for key in CATEGORIES}
    return {
        "schema": "dreamco.buddy_bootcamp_resource_catalog.v1",
        "resource_count": len(rows),
        "category_count": len(CATEGORIES),
        "category_counts": category_counts,
        "categories": [{"id": key, "label": label, "count": category_counts[key]} for key, label in CATEGORIES.items()],
        "resources": rows,
        "selection_truth": "Resources can be selected for an individual bootcamp plan. Selection does not connect an account, fetch private data, execute a tool, or authorize training.",
        "training_default": "disabled_until_source_rights_consent_and_training_review_pass",
    }


def build_bootcamp_plan(catalog: dict[str, Any], goals: list[str], resource_ids: list[str],
                        benchmark_ids: list[str] | None = None) -> dict[str, Any]:
    if not isinstance(goals, list) or not goals or any(not isinstance(goal, str) or not goal.strip() for goal in goals):
        raise ValueError("select at least one non-empty learning goal")
    resources = {row["id"]: row for row in catalog["resources"]}
    if not isinstance(resource_ids, list) or any(rid not in resources for rid in resource_ids):
        raise ValueError("selected resource ids must exist in the bootcamp resource catalog")
    selected = list(dict.fromkeys(resource_ids))
    return {
        "schema": "dreamco.buddy_bootcamp_user_plan.v1",
        "goals": [goal.strip() for goal in goals],
        "selected_resources": [{"id": rid, "name": resources[rid]["name"], "url": resources[rid]["url"],
                                 "category": resources[rid]["category"],
                                 "connection_status": resources[rid]["connection_status"]} for rid in selected],
        "benchmark_ids": list(dict.fromkeys(benchmark_ids or [])),
        "learning_stages": ["goal_intake", "capability_gap_review", "selected_source_review",
                            "original_lesson_and_practice", "sandbox_benchmark", "holdout_and_regression_review"],
        "training_enabled": False,
        "external_actions_enabled": False,
        "user_namespace": "local_browser_export_only",
        "truth_boundary": "This export records choices. It does not fetch sources, connect accounts, execute training, or prove mastery.",
    }


def build_reconstruction_plan(target_url: str, selected_resource_ids: list[str], catalog: dict[str, Any],
                              *, owner_authorized: bool, clean_room: bool,
                              rea_reviewed: bool = False,
                              customization_choices: list[str] | None = None,
                              original_differentiator: str = "") -> dict[str, Any]:
    parsed = urlparse(target_url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("target must be an HTTPS URL without embedded credentials")
    resources = {row["id"]: row for row in catalog["resources"]}
    if any(rid not in resources for rid in selected_resource_ids):
        raise ValueError("selected resource ids must exist in the bootcamp resource catalog")
    rea_selected = "project:rea_reverse_engineer_anything" in selected_resource_ids
    allowed_customizations = {
        "user_interface", "workflow", "target_audience", "accessibility", "security_privacy",
        "integrations", "performance_cost", "original_features",
    }
    choices = list(dict.fromkeys(customization_choices or []))
    invalid_choices = set(choices) - allowed_customizations
    if invalid_choices:
        raise ValueError(f"unknown customization choices: {sorted(invalid_choices)}")
    differentiator = " ".join(original_differentiator.split())
    customization_complete = len(choices) >= 2 and len(differentiator) >= 30
    status = "ready_for_authorized_review" if (owner_authorized is True and clean_room is True
                                                and rea_reviewed is True and rea_selected
                                                and customization_complete) else "blocked"
    blockers = []
    if owner_authorized is not True:
        blockers.append("target_owner_authorization_required")
    if clean_room is not True:
        blockers.append("clean_room_reimplementation_required")
    if not rea_selected:
        blockers.append("select_REA_resource_to_include_its_reference_workflow")
    if rea_reviewed is not True:
        blockers.append("review_REA_current_code_license_dependencies_and_security")
    if not customization_complete:
        blockers.append("add_two_or_more_distinct_customizations_and_an_original_differentiator")
    return {
        "schema": "dreamco.clean_room_reconstruction_plan.v1",
        "target_url": target_url,
        "analysis_tool_id": "project:rea_reverse_engineer_anything" if rea_selected else None,
        "status": status,
        "blockers": blockers,
        "customization": {
            "required": True,
            "selected_changes": choices,
            "original_differentiator": differentiator,
            "minimum_distinct_changes": 2,
            "customization_complete": customization_complete,
        },
        "stages": ["confirm_scope_and_rights", "inspect_authorized_artifacts_or_observed_behavior",
                   "record_evidence_and_uncertainty", "write_independent_behavior_spec",
                   "implement_original_code", "compare_against_owner_provided_fixtures",
                   "security_license_and_regression_review"],
        "prohibited": ["copying proprietary source or assets", "bypassing access controls or DRM",
                       "using stolen credentials or private user data", "claiming compatibility without test evidence"],
        "execution_started": False,
        "source_code_copied": False,
        "truth_boundary": "This is a plan only. It neither clones nor runs the target or REA.",
    }


def build_default_catalog() -> dict[str, Any]:
    connections = json.loads((ROOT / "website/data/buddy-resource-connection-catalog.json").read_text(encoding="utf-8"))
    registry = json.loads((ROOT / "config/buddy/resource-registry.json").read_text(encoding="utf-8"))
    return build_catalog(connections, registry)
