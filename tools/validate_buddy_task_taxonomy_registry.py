#!/usr/bin/env python3
"""Validate Buddy task and Markdown taxonomy systems against source registries."""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "config/buddy/task-taxonomy-system-registry.json"
MIRROR = ROOT / "website/data/task-taxonomy-system-registry.json"

def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

def slug(value: str) -> str:
    return re.sub(r"^_+|_+$", "", re.sub(r"[^a-z0-9]+", "_", str(value).lower()))

def fail(message: str) -> None:
    raise SystemExit(f"Buddy task taxonomy registry: FAIL: {message}")

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    registry = load("config/buddy/task-taxonomy-system-registry.json")
    mirror = json.loads(MIRROR.read_text(encoding="utf-8"))
    if registry != mirror:
        fail("GitHub Pages task-taxonomy mirror is stale")
    if registry.get("schema") != "dreamco.buddy.task_taxonomy_system_registry.v1":
        fail("unexpected schema")

    expected = {}
    def add(group, values, source, id_for=lambda x: slug(x), count_for=lambda x: 1):
        expected[group] = {
            str(value): {"ids": {id_for(value)}, "count": count_for(value), "files": {source}}
            for value in values
        }

    sandbox_path = "config/universal-human-ai-software-task-sandbox.json"
    sandbox = load(sandbox_path)
    for group, key in [
        ("task_action", "task_actions"),
        ("task_domain", "domains"),
        ("user_context", "user_contexts"),
        ("task_complexity", "complexity"),
        ("task_modality", "modalities"),
        ("execution_environment", "environments"),
        ("task_quality_dimension", "quality_dimensions"),
        ("business_client_scenario", "special_business_client_scenarios"),
        ("personal_task_scenario", "special_personal_scenarios"),
    ]:
        add(group, sandbox[key], sandbox_path)

    markdown_path = "config/buddy/markdown-implementation-gap-policy.json"
    markdown = load(markdown_path)
    add("markdown_gap_status", markdown["status_policy"].keys(), markdown_path)
    add("markdown_reference_path_root", markdown["path_roots"].keys(), markdown_path)

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

    required = {"mission", "inputs", "outputs", "permissions", "safety_controls", "metrics", "acceptance_criteria", "dependencies"}
    profiles = registry.get("contract_profiles", {})
    for group, values in expected.items():
        if required - set(profiles.get(group, {})):
            fail(f"contract profile incomplete for {group}")
        for category, source in values.items():
            item = actual[(group, category)]
            if item.get("contract_profile") != group or not item.get("mission"):
                fail(f"{group}/{category} lacks its own mission/profile")
            if item.get("lifecycle_status") != "catalogued" or item.get("implementation_status") != "not_implemented" or item.get("verification_status") != "not_verified":
                fail(f"{group}/{category} has unsupported evidence state")
            if set(item.get("source_resource_ids", [])) != source["ids"]:
                fail(f"{group}/{category} source IDs are stale")
            if set(item.get("source_files", [])) != source["files"]:
                fail(f"{group}/{category} source files are stale")
            if item.get("source_item_count") != source["count"]:
                fail(f"{group}/{category} source count is stale")

    counts = Counter(x["group"] for x in systems)
    if dict(counts) != registry.get("counts", {}).get("groups") or len(systems) != registry.get("counts", {}).get("total"):
        fail("summary counts are stale")

    docs = (ROOT / "docs/BUDDY_TASK_AND_MARKDOWN_TAXONOMY_SYSTEMS.md").read_text(encoding="utf-8")
    doc_ids = set(re.findall(r"\*\*Subsystem ID:\*\* `([^`]+)`", docs))
    if len(doc_ids) != len(systems) or doc_ids != set(ids):
        fail("task/Markdown taxonomy documentation does not match registry IDs")

    page_script = (ROOT / "website/category-systems.js").read_text(encoding="utf-8")
    if "data/task-taxonomy-system-registry.json" not in page_script:
        fail("category systems dashboard does not load task-taxonomy registry")
    print(f"Buddy task taxonomy registry: PASS ({len(systems)} systems across {len(expected)} groups)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
