#!/usr/bin/env python3
"""Discover public open-source learning repositories without executing their code.

The script creates a review queue only. It never clones, installs, runs, or trains on
newly discovered repositories. Promotion into a Bootcamp lesson is a separate gated step.
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(os.environ.get("BUDDY_DISCOVERY_OUTPUT", ROOT / "artifacts" / "buddy_bootcamp" / "repository-discovery.json"))
PER_QUERY = int(os.environ.get("BUDDY_DISCOVERY_PER_QUERY", "10"))
QUERIES = [
    "machine learning curriculum language:Python stars:>500",
    "llm training fine tuning evaluation language:Python stars:>200",
    "multimodal video understanding language:Python stars:>100",
    "audio speech understanding language:Python stars:>100",
    "music information retrieval language:Python stars:>50",
    "computer vision datasets benchmarks language:Python stars:>200",
    "reinforcement learning agents language:Python stars:>200",
    "retrieval augmented generation vector search language:Python stars:>200",
    "continual learning knowledge distillation language:Python stars:>50",
    "data engineering dataset versioning language:Python stars:>100",
    "programming language compiler education language:Python stars:>100",
    "robotics simulation embodied ai language:Python stars:>50"
]
HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": "DreamCo-Buddy-Bootcamp-Repository-Discovery"
}
TOKEN = os.environ.get("GITHUB_TOKEN")
if TOKEN:
    HEADERS["Authorization"] = f"Bearer {TOKEN}"

def fetch(query: str) -> dict:
    url = "https://api.github.com/search/repositories?" + urllib.parse.urlencode({
        "q": query, "sort": "updated", "order": "desc", "per_page": PER_QUERY
    })
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))

def main() -> int:
    seen: dict[str, dict] = {}
    errors = []
    for query in QUERIES:
        try:
            payload = fetch(query)
            for repo in payload.get("items", []):
                full_name = repo.get("full_name")
                if not full_name:
                    continue
                license_info = repo.get("license") or {}
                item = {
                    "repository": full_name,
                    "url": repo.get("html_url"),
                    "description": repo.get("description"),
                    "topics": repo.get("topics", []),
                    "language": repo.get("language"),
                    "stars": repo.get("stargazers_count", 0),
                    "forks": repo.get("forks_count", 0),
                    "open_issues": repo.get("open_issues_count", 0),
                    "default_branch": repo.get("default_branch"),
                    "last_pushed_at": repo.get("pushed_at"),
                    "archived": repo.get("archived", False),
                    "license_spdx": license_info.get("spdx_id", "NOASSERTION"),
                    "license_name": license_info.get("name"),
                    "discovered_by": [],
                    "review_state": "pending_human_review",
                    "execution_state": "not_cloned_not_executed",
                    "training_state": "not_authorized_not_started"
                }
                if full_name in seen:
                    seen[full_name]["discovered_by"].append(query)
                else:
                    item["discovered_by"] = [query]
                    seen[full_name] = item
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError) as exc:
            errors.append({"query": query, "error": str(exc)})
        time.sleep(1.0)

    records = sorted(seen.values(), key=lambda x: (x["archived"], x["license_spdx"] in ("NOASSERTION", "NONE"), -x["stars"], x["repository"].lower()))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "schema_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "GitHub repository search API",
        "queries": QUERIES,
        "unique_repositories": len(records),
        "records": records,
        "errors": errors,
        "limitations": [
            "Search results are discovery leads, not endorsements.",
            "A repository license does not grant rights to model weights, datasets, documentation, videos, music, or third-party assets.",
            "License absence or NOASSERTION requires quarantine and human review.",
            "No repository is cloned, installed, executed, or used for training by this script."
        ]
    }
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(OUT), "unique_repositories": len(records), "errors": len(errors)}, indent=2))
    return 0 if records else 1

if __name__ == "__main__":
    raise SystemExit(main())
