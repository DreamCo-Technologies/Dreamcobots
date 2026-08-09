#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "config" / "generated" / "open-source-ai-ecosystem-scan.json"
USER_AGENT = "DreamCo-Buddy-OpenSourceScout/1.0"


def get_json(url: str, headers: dict[str, str] | None = None) -> object:
    request_headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    if headers:
        request_headers.update(headers)
    req = urllib.request.Request(url, headers=request_headers)
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def hf_list(kind: str, limit: int = 100) -> list[dict]:
    query = urllib.parse.urlencode({"limit": limit, "sort": "lastModified", "direction": -1, "full": "true"})
    data = get_json(f"https://huggingface.co/api/{kind}?{query}")
    return data if isinstance(data, list) else []


def github_search(query: str, limit: int = 50) -> list[dict]:
    params = urllib.parse.urlencode({"q": query, "sort": "updated", "order": "desc", "per_page": min(limit, 100)})
    headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2026-03-10"}
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = get_json(f"https://api.github.com/search/repositories?{params}", headers=headers)
    if isinstance(data, dict) and isinstance(data.get("items"), list):
        return data["items"]
    return []


def normalize_hf(row: dict, kind: str) -> dict:
    tags = row.get("tags") if isinstance(row.get("tags"), list) else []
    card = row.get("cardData") if isinstance(row.get("cardData"), dict) else {}
    license_value = card.get("license") or next((tag.split(":", 1)[1] for tag in tags if isinstance(tag, str) and tag.startswith("license:")), None)
    return {
        "source": "huggingface",
        "kind": kind,
        "id": row.get("id") or row.get("modelId"),
        "last_modified": row.get("lastModified"),
        "downloads": row.get("downloads"),
        "likes": row.get("likes"),
        "pipeline_tag": row.get("pipeline_tag"),
        "library_name": row.get("library_name"),
        "license": license_value,
        "gated": row.get("gated"),
        "private": row.get("private", False),
        "tags": tags[:50],
        "adoption_status": "research_only",
        "license_review_required": True,
    }


def normalize_github(row: dict, query: str) -> dict:
    license_obj = row.get("license") if isinstance(row.get("license"), dict) else {}
    return {
        "source": "github",
        "kind": "repository",
        "id": row.get("full_name"),
        "query": query,
        "description": row.get("description"),
        "updated_at": row.get("updated_at"),
        "pushed_at": row.get("pushed_at"),
        "stars": row.get("stargazers_count"),
        "forks": row.get("forks_count"),
        "language": row.get("language"),
        "topics": row.get("topics") if isinstance(row.get("topics"), list) else [],
        "license": license_obj.get("spdx_id"),
        "archived": row.get("archived", False),
        "disabled": row.get("disabled", False),
        "adoption_status": "research_only",
        "license_review_required": True,
    }


def main() -> int:
    errors: list[dict] = []
    models: list[dict] = []
    datasets: list[dict] = []
    repos: list[dict] = []

    try:
        models = [normalize_hf(row, "model") for row in hf_list("models", 100) if isinstance(row, dict)]
    except Exception as exc:
        errors.append({"source": "huggingface_models", "error": str(exc)})
    time.sleep(0.2)
    try:
        datasets = [normalize_hf(row, "dataset") for row in hf_list("datasets", 100) if isinstance(row, dict)]
    except Exception as exc:
        errors.append({"source": "huggingface_datasets", "error": str(exc)})

    queries = [
        "topic:machine-learning stars:>100",
        "topic:llm stars:>100",
        "topic:ai-agents stars:>50",
        "topic:computer-vision stars:>100",
        "topic:speech-recognition stars:>50",
        "topic:robotics stars:>50",
        "topic:game-engine stars:>100",
        "topic:vector-database stars:>100",
        "topic:inference stars:>50",
    ]
    for query in queries:
        try:
            repos.extend(normalize_github(row, query) for row in github_search(query, 50) if isinstance(row, dict))
        except Exception as exc:
            errors.append({"source": "github", "query": query, "error": str(exc)})
        time.sleep(0.2)

    deduped = {}
    for row in repos:
        key = row.get("id")
        if key:
            deduped[key] = row
    repos = sorted(deduped.values(), key=lambda r: (r.get("updated_at") or "", r.get("stars") or 0), reverse=True)

    payload = {
        "schema": "dreamco.open_source_ai_ecosystem_scan.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "network_scan": True,
        "metadata_only": True,
        "counts": {"models": len(models), "datasets": len(datasets), "repositories": len(repos), "errors": len(errors)},
        "models": models,
        "datasets": datasets,
        "repositories": repos,
        "errors": errors,
        "adoption_pipeline": ["discover","record provenance/license","screen privacy/security","benchmark","compare cost/quality","approve adoption mode","sandbox integrate","retest fleet"],
        "truth_boundary": "This is a bounded metadata scan, not a complete census of all open-source AI. Discovery does not grant training, redistribution or commercial rights; each asset requires license/provenance review before use."
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": len(errors) == 0, **payload["counts"], "output": str(OUT.relative_to(ROOT))}, indent=2))
    # Discovery source outages should be visible but should not make core Buddy testing fail.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
