#!/usr/bin/env python3
"""Discover public GitHub and Hugging Face learning resources.

Metadata-first only: no cloning, media downloads, training, or rights grants.
"""
from __future__ import annotations

import argparse
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/buddy-open-source-bootcamp.json"
DEFAULT_OUT = ROOT / "artifacts/buddy-bootcamp-discovery"


def request_json(url: str, token: str | None = None) -> Any:
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "DreamCo-Buddy-Bootcamp-Discovery/1.0"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=25) as response:
        return json.loads(response.read().decode("utf-8"))


def license_status(spdx: str | None) -> str:
    if not spdx or str(spdx).upper() in {"NOASSERTION", "OTHER"}:
        return "rights_pending"
    return "license_review_required"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def github_repo(repo: str, token: str | None) -> dict[str, Any]:
    data = request_json(f"https://api.github.com/repos/{repo}", token)
    lic = (data.get("license") or {}).get("spdx_id")
    return {
        "source_type": "github_repository", "source_id": data.get("full_name"),
        "url": data.get("html_url"), "description": data.get("description"),
        "default_branch": data.get("default_branch"), "revision": data.get("default_branch"),
        "updated_at": data.get("updated_at"), "stars": data.get("stargazers_count"),
        "license_spdx": lic, "rights_state": license_status(lic),
        "archived": data.get("archived", False), "topics": data.get("topics", []),
        "discovered_at": now(),
    }


def github_search(topic: str, limit: int, token: str | None) -> list[dict[str, Any]]:
    query = urllib.parse.urlencode({"q": f"topic:{topic} stars:>25", "sort": "stars", "order": "desc", "per_page": limit})
    data = request_json(f"https://api.github.com/search/repositories?{query}", token)
    rows = []
    for item in data.get("items", []):
        lic = (item.get("license") or {}).get("spdx_id")
        rows.append({
            "source_type": "github_repository", "source_id": item.get("full_name"),
            "url": item.get("html_url"), "description": item.get("description"),
            "default_branch": item.get("default_branch"), "revision": item.get("default_branch"),
            "updated_at": item.get("updated_at"), "stars": item.get("stargazers_count"),
            "license_spdx": lic, "rights_state": license_status(lic),
            "archived": item.get("archived", False), "topics": item.get("topics", []),
            "discovery_topic": topic, "discovered_at": now(),
        })
    return rows


def hf_search(kind: str, term: str, limit: int) -> list[dict[str, Any]]:
    query = urllib.parse.urlencode({"search": term, "limit": limit})
    data = request_json(f"https://huggingface.co/api/{kind}?{query}")
    rows = []
    for item in data if isinstance(data, list) else []:
        card = item.get("cardData") or {}
        tags = item.get("tags") or []
        license_value = card.get("license")
        if not license_value and isinstance(tags, list):
            license_value = next((x.split(":", 1)[1] for x in tags if isinstance(x, str) and x.startswith("license:")), None)
        repo_type = kind[:-1] if kind.endswith("s") else kind
        rows.append({
            "source_type": f"huggingface_{repo_type}", "source_id": item.get("id"),
            "url": f"https://huggingface.co/{item.get('id')}",
            "revision": item.get("sha"), "pipeline_tag": item.get("pipeline_tag"),
            "tags": tags, "license": license_value,
            "rights_state": license_status(license_value),
            "downloads": item.get("downloads"), "likes": item.get("likes"),
            "last_modified": item.get("lastModified"), "discovered_at": now(),
        })
    return rows


def load_subjects(config: dict[str, Any], taxonomy_file: str | None) -> tuple[list[str], str, int]:
    seed = set(config["discovery"].get("hugging_face_subjects", []))
    if not taxonomy_file:
        return sorted(seed), "configured_seed_taxonomy_only", 0
    path = Path(taxonomy_file)
    if not path.is_file():
        return sorted(seed), "configured_seed_taxonomy_fallback_missing_file", 0
    doc = json.loads(path.read_text(encoding="utf-8"))
    dynamic = {str(x).strip().lower().replace(" ", "-") for x in doc.get("subject_terms", []) if str(x).strip()}
    if not dynamic:
        return sorted(seed), "configured_seed_taxonomy_fallback_empty_live_taxonomy", 0
    return sorted(seed | dynamic), "live_taxonomy_plus_configured_seeds", len(dynamic)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT))
    parser.add_argument("--hf-limit-per-subject", type=int, default=20)
    parser.add_argument("--github-limit-per-topic", type=int, default=10)
    parser.add_argument("--taxonomy-file", default=None, help="Live Hugging Face subject taxonomy JSON")
    args = parser.parse_args()
    if args.hf_limit_per_subject < 1 or args.github_limit_per_topic < 1:
        parser.error("discovery limits must be positive")
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    subjects, taxonomy_status, dynamic_count = load_subjects(config, args.taxonomy_file)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    records: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []

    seen: set[str] = set()
    for seed in config["discovery"]["github_seed_repositories"]:
        repo = seed["repo"]
        if repo in seen:
            continue
        seen.add(repo)
        try:
            row = github_repo(repo, token)
            row["seed_subjects"] = seed.get("subjects", [])
            records.append(row)
        except (urllib.error.URLError, TimeoutError, ValueError, KeyError) as exc:
            errors.append({"source": f"github:{repo}", "error": str(exc)})
        time.sleep(0.15)

    for topic in config["discovery"]["github_search_topics"]:
        try:
            records.extend(github_search(topic, args.github_limit_per_topic, token))
        except (urllib.error.URLError, TimeoutError, ValueError, KeyError) as exc:
            errors.append({"source": f"github-topic:{topic}", "error": str(exc)})
        time.sleep(0.2)

    for subject in subjects:
        for kind in config["discovery"]["hugging_face_hub_types"]:
            try:
                for row in hf_search(kind, subject, args.hf_limit_per_subject):
                    row["discovery_subject"] = subject
                    records.append(row)
            except (urllib.error.URLError, TimeoutError, ValueError, KeyError) as exc:
                errors.append({"source": f"hf:{kind}:{subject}", "error": str(exc)})
            time.sleep(0.1)

    unique: dict[tuple[str, str], dict[str, Any]] = {}
    for row in records:
        key = (str(row.get("source_type")), str(row.get("source_id")))
        if key[1]:
            if key not in unique:
                unique[key] = row
            else:
                old = unique[key]
                old["discovery_subjects"] = sorted(set(old.get("discovery_subjects", [old.get("discovery_subject")]) + [row.get("discovery_subject")]) - {None})
    final = {
        "schema": "dreamco.buddy_bootcamp_discovery_snapshot.v1",
        "generated_at": now(),
        "discovery_scope": {
            "hf_subject_count": len(subjects), "hf_seed_subject_count": len(config["discovery"]["hugging_face_subjects"]),
            "hf_dynamic_taxonomy_count": dynamic_count, "hf_dynamic_taxonomy_status": taxonomy_status,
            "hf_artifact_types": config["discovery"]["hugging_face_hub_types"],
            "github_seed_count": len(seen), "github_topics_searched": len(config["discovery"]["github_search_topics"]),
        },
        "counts": {
            "discovered_unique": len(unique), "hugging_face_subjects_searched": len(subjects),
            "rights_pending_or_review": sum(r["rights_state"] != "approved" for r in unique.values()),
            "errors": len(errors),
        },
        "resources": list(unique.values()), "errors": errors,
        "truth_boundary": "Discovery metadata is not a detailed summary, rights approval, training authorization, or mastery evidence. Search results are bounded per subject and are not an exhaustive inventory of the Hub.",
    }
    (out_dir / "discovery-snapshot.json").write_text(json.dumps(final, indent=2) + "\n", encoding="utf-8")
    summary = [
        "# Buddy Bootcamp weekly discovery", "", f"- Generated: {final['generated_at']}",
        f"- Hugging Face subjects searched: {len(subjects)} ({taxonomy_status})",
        f"- Dynamic Hugging Face terms loaded: {dynamic_count}",
        f"- Unique resources discovered: {len(unique)}",
        f"- Rights review required: {final['counts']['rights_pending_or_review']}",
        f"- Discovery errors: {len(errors)}", "",
        "This run discovers bounded metadata samples only. It does not download source media, create full guides, or train Buddy.",
    ]
    (out_dir / "summary.md").write_text("\n".join(summary) + "\n", encoding="utf-8")
    print(json.dumps(final["counts"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
