#!/usr/bin/env python3
"""Build ChatGPT-teacher authoring work orders from rights-cleared source bundles.

This creates requests only. It never downloads source material, invents summaries,
approves rights, or trains Buddy.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

QUEUE_SCHEMA = "dreamco.buddy_source_study_queue.v1"
BUNDLE_SCHEMA = "dreamco.authorized_source_bundle.v1"
PROMPT_PATH = "buddy/bootcamp/prompts/buddy-university-teacher-authoring.md"
GUIDE_SCHEMA_PATH = "config/buddy-source-study-guide.schema.json"
REQUIRED_PERMISSIONS = ("study_permission", "summary_derivative_permission", "evaluation_permission")


def asset_key(item: dict[str, Any]) -> str:
    raw = "|".join(str(item.get(key, "")) for key in ("source_type", "source_id", "revision"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def build_work_orders(queue: dict[str, Any], bundles_dir: Path) -> dict[str, Any]:
    if queue.get("schema") != QUEUE_SCHEMA:
        raise ValueError("unsupported source study queue schema")
    orders = []
    for item in queue.get("queue", []):
        key = asset_key(item)
        order = {
            "asset_key": key,
            "source_type": item.get("source_type"),
            "source_id": item.get("source_id"),
            "url": item.get("url"),
            "revision": item.get("revision"),
            "status": None,
            "blocked_reasons": [],
            "teacher": "ChatGPT/GPT-6",
            "student": "Buddy",
            "prompt_path": PROMPT_PATH,
            "guide_schema_path": GUIDE_SCHEMA_PATH,
            "output_path": f"data/buddy-study-guides/{key}.json",
            "truth_boundary": "A work order is not a summary, study attempt, training example, or mastery result.",
        }
        if item.get("status") != "guide_authoring_eligible":
            order["status"] = "blocked_rights_pending"
            order["blocked_reasons"].append(
                "source is not explicitly rights-cleared for study, derivative summary and evaluation"
            )
            orders.append(order)
            continue
        manifest_path = bundles_dir / f"{key}.manifest.json"
        content_path = bundles_dir / f"{key}.content.md"
        if not manifest_path.is_file() or not content_path.is_file():
            order["status"] = "blocked_source_bundle_missing"
            order["blocked_reasons"].append(
                "full authorized source bundle is missing; metadata is not lesson content"
            )
            orders.append(order)
            continue
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            order["status"] = "blocked_bundle_manifest_invalid"
            order["blocked_reasons"].append(f"bundle manifest cannot be read: {exc}")
            orders.append(order)
            continue
        if manifest.get("schema") != BUNDLE_SCHEMA:
            order["blocked_reasons"].append("unsupported authorized source bundle schema")
        source = manifest.get("source") if isinstance(manifest.get("source"), dict) else {}
        for field in ("source_type", "source_id", "url", "revision"):
            if source.get(field) != item.get(field):
                order["blocked_reasons"].append(f"bundle source {field} does not match the queued source")
        rights = manifest.get("rights") if isinstance(manifest.get("rights"), dict) else {}
        for permission in REQUIRED_PERMISSIONS:
            if rights.get(permission) is not True:
                order["blocked_reasons"].append(f"bundle is missing explicit {permission}")
        if rights.get("evidence_ref") != item.get("rights_evidence_ref"):
            order["blocked_reasons"].append("bundle rights evidence does not match the source queue")
        content_bytes = content_path.read_bytes()
        content_hash = hashlib.sha256(content_bytes).hexdigest()
        if manifest.get("content_sha256") != content_hash:
            order["blocked_reasons"].append("source bundle content hash mismatch")
        if len(content_bytes.strip()) < 500:
            order["blocked_reasons"].append("source bundle is too short for a source-grounded guide")
        if order["blocked_reasons"]:
            order["status"] = "blocked_bundle_validation_failed"
        else:
            order["status"] = "ready_for_teacher_authoring"
            order["bundle_manifest_path"] = str(manifest_path)
            order["source_content_path"] = str(content_path)
            order["content_sha256"] = content_hash
            order["rights_evidence_ref"] = rights["evidence_ref"]
            order["instructions"] = [
                "Read the complete source bundle and its exact locators.",
                "Use the teacher-authoring prompt to extract the strongest knowledge and create an original detailed guide.",
                "Include prerequisites, concept map, worked examples, exercises, knowledge checks, answer key and capstone.",
                "For occupation/venture sources, research task-specific software, agent capabilities, commercial pathways and human approval boundaries.",
                "Set review.status to needs_review; never self-approve the guide.",
                "Record user-designated ownership of original DreamCo expression and preserve all upstream rights and attribution.",
            ]
        orders.append(order)
    counts: dict[str, int] = {}
    for order in orders:
        counts[order["status"]] = counts.get(order["status"], 0) + 1
    return {
        "schema": "dreamco.buddy_teacher_authoring_queue.v1",
        "teacher": "ChatGPT/GPT-6",
        "student": "Buddy",
        "source_count": len(orders),
        "counts": counts,
        "work_orders": orders,
        "truth_boundary": "Only ready_for_teacher_authoring work orders contain a verified full source bundle. No summaries are generated by this planner.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-queue", required=True)
    parser.add_argument("--bundles-dir", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    queue = json.loads(Path(args.source_queue).read_text(encoding="utf-8"))
    result = build_work_orders(queue, Path(args.bundles_dir))
    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"source_count": result["source_count"], "counts": result["counts"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
