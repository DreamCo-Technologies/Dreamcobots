#!/usr/bin/env python3
"""Build discovery-only Hugging Face taxonomy routes for all canonical MasterBots."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTERBOTS = ROOT / "config/masterbot-65-registry.json"
CROSSWALK = ROOT / "config/generated/masterbot-55-domain-crosswalk.json"
HF_PACKS = ROOT / "config/hf-capability-download-map.json"
TASKS = ROOT / "config/huggingface-task-taxonomy.json"
POLICY = ROOT / "config/buddy-dataset-routing-policy.json"
OUTPUT = ROOT / "config/generated/division-huggingface-taxonomy-map.json"

BASE_PACKS = ["pack.instruct", "pack.reason", "pack.safety"]
PACK_KEYWORDS = {
    "pack.code": ["code", "cyber", "automation", "agents", "infra", "integration", "simulation", "security", "ai", "software"],
    "pack.embed": ["data", "knowledge", "research", "resource", "market", "finance", "customer", "cust intel", "discovery", "global", "education", "legal", "real estate", "science"],
    "pack.rerank": ["market", "retail", "product", "customer", "resource", "discovery", "search", "decision", "sales", "trade"],
    "pack.vision": ["vision", "arts", "construction", "production", "agriculture", "real estate", "planetary", "simulation", "food", "maintenance", "transport", "design"],
    "pack.speech": ["voice", "content", "social", "influence", "human", "education", "arts", "audio"],
    "pack.translate": ["global", "world", "trade", "market", "education", "language", "international"],
    "pack.summarize": ["content", "research", "knowledge", "legal", "admin", "strategy", "education", "pro services", "document", "science"],
}
PACK_TASKS = {
    "pack.instruct": ["text-generation", "text2text-generation"],
    "pack.code": ["text-generation", "text2text-generation", "fill-mask"],
    "pack.reason": ["question-answering", "text-generation", "table-question-answering"],
    "pack.embed": ["sentence-similarity", "feature-extraction"],
    "pack.rerank": ["zero-shot-classification", "text-classification"],
    "pack.vision": ["image-classification", "object-detection", "image-segmentation", "image-to-image"],
    "pack.speech": ["automatic-speech-recognition", "audio-classification", "text-to-speech"],
    "pack.translate": ["translation"],
    "pack.summarize": ["summarization"],
    "pack.safety": ["text-classification", "zero-shot-classification"],
}


def norm(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(value).casefold()).strip()


def git_blob_sha(text: str) -> str:
    raw = text.encode("utf-8")
    return hashlib.sha1(f"blob {len(raw)}\0".encode("ascii") + raw).hexdigest()


def build_map(masterbots: dict, crosswalk: dict, hf_packs: dict, taxonomy: dict,
              policy: dict, source_blob_shas: dict) -> dict:
    bots = masterbots.get("divisions")
    masterbot_rows = crosswalk.get("masterbots")
    domain_rows = crosswalk.get("domains")
    packs = hf_packs.get("packs")
    tasks = taxonomy.get("task_families")
    if not isinstance(bots, list) or len(bots) != masterbots.get("canonical_count"):
        raise ValueError("canonical MasterBot registry count is invalid")
    if len(bots) != 65 or not isinstance(masterbot_rows, list) or len(masterbot_rows) != 65:
        raise ValueError("expected 65 MasterBots and 65 crosswalk rows")
    if not isinstance(domain_rows, list) or len(domain_rows) != 55:
        raise ValueError("expected 55 domain divisions in the reviewed crosswalk")
    if not isinstance(packs, list) or not isinstance(tasks, list):
        raise ValueError("Hugging Face pack and task taxonomy arrays are required")

    pack_ids = {item.get("id") for item in packs}
    task_ids = {item.get("id") for item in tasks}
    if not set(BASE_PACKS).issubset(pack_ids):
        raise ValueError("shared foundation capability packs are missing")
    if set(PACK_TASKS) - pack_ids:
        raise ValueError("PACK_TASKS references unknown capability packs")
    if any(task not in task_ids for values in PACK_TASKS.values() for task in values):
        raise ValueError("a candidate pipeline tag is missing from the task taxonomy")

    rows_by_id = {row.get("masterbot_id"): row for row in masterbot_rows}
    if len(rows_by_id) != 65 or any(bot.get("id") not in rows_by_id for bot in bots):
        raise ValueError("crosswalk MasterBot IDs do not match canonical registry")

    routes = []
    for bot in bots:
        row = rows_by_id[bot["id"]]
        name = bot["name"]
        slug = re.sub(r"[^a-z0-9]+", "-", name.casefold()).strip("-")
        domain_name = row.get("primary_domain_name")
        domain_id = row.get("primary_domain_id")
        mapping_status = row.get("mapping_status", "unresolved")
        terms = [name, re.sub(r"^dream", "", name, flags=re.I)]
        if domain_name and mapping_status == "proposed_exact_name_match":
            terms.append(domain_name)
        terms = list(dict.fromkeys(term.strip() for term in terms if term and term.strip()))
        haystack = norm(" ".join(terms))
        selected = list(BASE_PACKS)
        for pack_id, hints in PACK_KEYWORDS.items():
            if any(norm(hint) in haystack for hint in hints):
                selected.append(pack_id)
        selected = list(dict.fromkeys(selected))
        candidate_tasks = list(dict.fromkeys(
            task for pack_id in selected for task in PACK_TASKS.get(pack_id, [])
        ))
        routes.append({
            "masterbot_id": bot["id"],
            "masterbot_name": name,
            "lane_id": f"hf-discovery-lane-{bot['id']:03d}",
            "subject_terms": terms,
            "search_queries": [
                f"{terms[-1]} dataset",
                f"{terms[-1]} machine learning",
                f"{terms[-1]} benchmark"
            ],
            "domain_crosswalk": {
                "domain_id": domain_id,
                "domain_name": domain_name,
                "mapping_status": mapping_status,
                "owner_review_required": True,
                "owner_approval": row.get("owner_approval")
            },
            "capability_pack_ids": selected,
            "candidate_pipeline_tags": candidate_tasks,
            "rights_status": "UNVERIFIED_DISCOVERY_ONLY",
            "training_approved": False
        })

    counts = crosswalk.get("counts", {})
    if counts.get("masterbots") != 65 or counts.get("domain_divisions") != 55:
        raise ValueError("crosswalk summary counts are inconsistent")
    if len({row["lane_id"] for row in routes}) != 65:
        raise ValueError("every MasterBot must have a unique discovery lane")
    return {
        "schema": "dreamco.division_huggingface_taxonomy_map.v1",
        "status": "discovery_only_requires_owner_and_rights_review",
        "source_of_truth": "config/masterbot-65-registry.json",
        "counts": {
            "masterbots": len(routes),
            "domain_divisions": len(domain_rows),
            "proposed_exact_name_matches": counts.get("proposed_exact_name_matches"),
            "unresolved_masterbots": counts.get("unresolved_masterbots"),
            "task_families": len(tasks),
            "capability_packs": len(packs)
        },
        "source_blob_shas": source_blob_shas,
        "hub_metadata_dimensions": {
            "datasets": taxonomy.get("dataset_discovery_dimensions", []),
            "models": taxonomy.get("model_discovery_dimensions", [])
        },
        "routes": routes,
        "rights_policy": policy.get("hard_gates", {}),
        "truth": (
            "This is a subject and task discovery map only. It does not approve ownership, "
            "dataset use, training, redistribution, model certification, or deployment. "
            "Unresolved MasterBot-to-domain mappings remain unresolved."
        )
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    paths = {
        "masterbot_registry": MASTERBOTS,
        "domain_crosswalk": CROSSWALK,
        "hf_capability_packs": HF_PACKS,
        "hf_task_taxonomy": TASKS,
        "dataset_routing_policy": POLICY
    }
    source_texts = {key: path.read_text(encoding="utf-8") for key, path in paths.items()}
    source_docs = {key: json.loads(value) for key, value in source_texts.items()}
    source_hashes = {key: git_blob_sha(value) for key, value in source_texts.items()}
    payload = build_map(
        source_docs["masterbot_registry"], source_docs["domain_crosswalk"],
        source_docs["hf_capability_packs"], source_docs["hf_task_taxonomy"],
        source_docs["dataset_routing_policy"], source_hashes
    )
    encoded = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != encoded:
            raise SystemExit("Hugging Face division taxonomy map is stale; regenerate it")
    else:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(encoded, encoding="utf-8")
    print(json.dumps({"ok": True, **payload["counts"], "training_approved": False}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
