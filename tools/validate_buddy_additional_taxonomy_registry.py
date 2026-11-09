#!/usr/bin/env python3
"""Validate additional Buddy taxonomy systems against their source registries."""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config"
REGISTRY_PATH = CONFIG / "buddy/additional-taxonomy-system-registry.json"
MIRROR_PATH = ROOT / "website/data/additional-taxonomy-system-registry.json"

def load(path: str):
    with (ROOT / path).open(encoding="utf-8") as handle:
        return json.load(handle)

def fail(message: str) -> None:
    raise SystemExit(f"Buddy additional taxonomy registry: FAIL: {message}")

def slug(value: str) -> str:
    import re
    return re.sub(r"^_+|_+$", "", re.sub(r"[^a-z0-9]+", "_", str(value).lower()))

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate without modifying files")
    parser.parse_args()

    registry = load("config/buddy/additional-taxonomy-system-registry.json")
    mirror = json.loads(MIRROR_PATH.read_text(encoding="utf-8"))
    if mirror != registry:
        fail("GitHub Pages additional-taxonomy data mirror is stale")
    if registry.get("schema") != "dreamco.buddy.additional_taxonomy_system_registry.v1":
        fail("unexpected or missing schema identifier")

    expected = {}
    def add(group, labels, source_files, ids_for, count_for=None, status_for=None):
        bucket = expected.setdefault(group, {})
        for label in labels:
            bucket[str(label)] = {
                "ids": set(ids_for(label)),
                "count": (count_for(label) if count_for else 1),
                "files": set(source_files),
                "status": (status_for(label) if status_for else None),
            }

    opportunity_path = "config/buddy-opportunity-resource-registry.json"
    opportunity = load(opportunity_path)["resources"]
    add("opportunity_category", {x["category"] for x in opportunity}, [opportunity_path],
        lambda c: [x["id"] for x in opportunity if x["category"] == c],
        lambda c: sum(x["category"] == c for x in opportunity))

    web_paths = ["config/buddy-web-source-registry.json", "config/buddy-web-source-registry-set-02.json"]
    web_sources = [x for path in web_paths for x in load(path)["sources"]]
    web_domains = {domain for source in web_sources for domain in source.get("domains", [])}
    add("web_source_domain", web_domains, web_paths,
        lambda d: [x["id"] for x in web_sources if d in x.get("domains", [])],
        lambda d: sum(d in x.get("domains", []) for x in web_sources))

    connection_path = "config/buddy-universal-connection-catalog.json"
    connections = load(connection_path)["connections"]
    add("connection_area", {x["area"] for x in connections}, [connection_path],
        lambda a: [x["id"] for x in connections if x["area"] == a],
        lambda a: sum(x["area"] == a for x in connections))

    learning_path = "config/buddy-learning-source-adapters.json"
    learning_sources = load(learning_path)["sources"]
    add("learning_adapter_category", {x["category"] for x in learning_sources}, [learning_path],
        lambda c: [x["id"] for x in learning_sources if x["category"] == c],
        lambda c: sum(x["category"] == c for x in learning_sources))

    study_family_path = "config/buddy-study-resource-policy.json"
    study_families = load(study_family_path)["resource_families"]
    add("study_resource_family", study_families.keys(), [study_family_path], lambda x: [slug(x)])

    repository_learning_path = "config/unified-repository-learning-registry.json"
    tracked_domains = load(repository_learning_path)["tracked_domains"]
    add("repository_learning_domain", tracked_domains, [repository_learning_path], lambda x: [slug(x)])

    matrix_path = "config/500-model-full-matrix-prospectus.json"
    matrix = load(matrix_path)
    for group, key in [
        ("model_matrix_dimension", "dimensions"),
        ("model_matrix_axis", "matrix_axes"),
        ("model_matrix_status", "statuses"),
        ("model_matrix_section", "prospectus_sections"),
    ]:
        add(group, matrix[key], [matrix_path], lambda x: [slug(x)])

    bootcamp_path = "config/buddy-1000-source-bootcamp.json"
    add("bootcamp_lifecycle_stage", load(bootcamp_path)["learning_lifecycle"], [bootcamp_path], lambda x: [slug(x)])

    universal_path = "config/universal-capability-domains.json"
    add("universal_capability_domain", load(universal_path)["domains"], [universal_path], lambda x: [slug(x)])

    superbot_path = "config/superbot-capability-taxonomy.json"
    superbot_domains = load(superbot_path)["capability_domains"]
    add("superbot_capability_domain", superbot_domains.keys(), [superbot_path], lambda x: [slug(x)],
        lambda x: 1)

    software_path = "config/universal_software_capability_taxonomy.json"
    software = load(software_path)
    add("software_capability_category", [x["name"] for x in software["categories"]], [software_path],
        lambda name: [next(x["id"] for x in software["categories"] if x["name"] == name)])
    add("software_productivity_dimension", software["productivity_dimensions"], [software_path], lambda x: [slug(x)])
    add("software_evidence_state", software["evidence_states"], [software_path], lambda x: [slug(x)])

    tool_catalog_path = "config/buddy_tool_skill_catalog.json"
    tool_catalog = load(tool_catalog_path)
    add("buddy_tool", [x["name"] for x in tool_catalog["tools"]], [tool_catalog_path],
        lambda name: [next(x["id"] for x in tool_catalog["tools"] if x["name"] == name)])
    add("buddy_skill", [x["name"] for x in tool_catalog["skills"]], [tool_catalog_path],
        lambda name: [next(x["id"] for x in tool_catalog["skills"] if x["name"] == name)])

    hf_path = "config/huggingface-capability-packs.json"
    hf_packs = load(hf_path)["packs"]
    add("hf_capability_pack", [x["id"] for x in hf_packs], [hf_path], lambda x: [x])

    government_sources_path = "config/global-government-source-adapters.json"
    government_sources = load(government_sources_path)["sources"]
    add("government_source_adapter", [x["id"] for x in government_sources], [government_sources_path], lambda x: [x])

    navigator_path = "config/buddy-211-government-service-navigator.json"
    navigator = load(navigator_path)
    for group, key in [
        ("211_service_domain", "service_domains"),
        ("211_user_journey_stage", "user_journey"),
        ("211_source_priority", "source_priority"),
        ("211_service_capability", "capabilities"),
        ("211_application_assistance_level", "application_assistance_levels"),
        ("211_prohibited_autonomy_action", "never_autonomous"),
        ("211_benchmark_dimension", "benchmark_dimensions"),
    ]:
        add(group, navigator[key], [navigator_path], lambda x: [slug(x)])

    seed_path = "config/new-divisions-seed.json"
    proposed_path = "config/proposed-10-divisions.json"
    seed_names = set(load(seed_path)["divisions"].keys())
    proposed_divisions = load(proposed_path)["divisions"]
    proposed_names = {x["id"] for x in proposed_divisions}
    if seed_names != proposed_names:
        fail("new-division seed and proposed-10 registry names disagree")
    add("proposed_division", proposed_names, [seed_path, proposed_path], lambda x: [x],
        status_for=lambda x: "proposed_not_canonical")

    government_catalog_path = "config/global-government-discovered-catalog.json"
    government_catalog = load(government_catalog_path)
    government_types = ["jurisdictions", "departments", "programs", "services", "jobs", "fiscal_sources"]
    add("government_catalog_type", government_types, [government_catalog_path], lambda x: [x],
        lambda x: len(government_catalog.get(x, [])))

    systems = registry.get("systems")
    if not isinstance(systems, list):
        fail("systems must be an array")
    ids = [x.get("id") for x in systems]
    if any(not x for x in ids) or len(ids) != len(set(ids)):
        fail("subsystem IDs must be present and unique")
    actual = {(x.get("group"), x.get("category")): x for x in systems}
    expected_keys = {(group, category) for group, values in expected.items() for category in values}
    if set(actual) != expected_keys:
        fail(f"category mismatch; missing={sorted(expected_keys-set(actual))}; extra={sorted(set(actual)-expected_keys)}")

    required_profile = {"mission", "inputs", "outputs", "permissions", "safety_controls", "metrics", "acceptance_criteria", "dependencies"}
    profiles = registry.get("contract_profiles", {})
    for group, categories in expected.items():
        profile = profiles.get(group)
        if not profile or required_profile - set(profile):
            fail(f"missing or incomplete contract profile for {group}")
        for category, expected_item in categories.items():
            item = actual[(group, category)]
            if item.get("lifecycle_status") != "catalogued" or item.get("implementation_status") != "not_implemented" or item.get("verification_status") != "not_verified":
                fail(f"{group}/{category} has an unsupported evidence state")
            if item.get("contract_profile") != group or not item.get("mission"):
                fail(f"{group}/{category} is missing its own mission or contract profile")
            if set(item.get("source_resource_ids", [])) != expected_item["ids"]:
                fail(f"{group}/{category} source IDs are stale")
            if set(item.get("source_files", [])) != expected_item["files"]:
                fail(f"{group}/{category} source file references are stale")
            if item.get("source_item_count") != expected_item["count"]:
                fail(f"{group}/{category} source item count is stale")
            if group == "superbot_capability_domain" and item.get("example_count") != len(superbot_domains[category].get("examples", [])):
                fail(f"{group}/{category} example count is stale")
            if expected_item["status"] and item.get("reconciliation_status") != expected_item["status"]:
                fail(f"{group}/{category} reconciliation status is stale")

    counts = Counter(x["group"] for x in systems)
    if dict(counts) != registry.get("counts", {}).get("groups"):
        fail("group counts are stale")
    if len(systems) != registry.get("counts", {}).get("total"):
        fail("total system count is stale")

    docs_path = ROOT / "docs/BUDDY_ADDITIONAL_TAXONOMY_SYSTEMS.md"
    docs = docs_path.read_text(encoding="utf-8")
    doc_ids = set(__import__("re").findall(r"\*\*Subsystem ID:\*\* `([^`]+)`", docs))
    if len(doc_ids) != len(systems) or doc_ids != set(ids):
        fail("additional taxonomy documentation sections do not match the registry IDs")

    print(f"Buddy additional taxonomy registry: PASS ({len(systems)} systems across {len(expected)} groups)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
