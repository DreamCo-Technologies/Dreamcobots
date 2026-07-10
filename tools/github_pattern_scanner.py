#!/usr/bin/env python3
"""Collect public GitHub repository signals without copying external code."""

from __future__ import annotations

import argparse
import json
import os
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "config" / "github_intelligence_queries.json"
DEFAULT_OUTPUT = ROOT / "reports" / "github_pattern_intelligence.json"
API_URL = "https://api.github.com/search/repositories"


def normalize_repository(item: dict[str, Any], query_id: str) -> dict[str, Any]:
    license_info = item.get("license") or {}
    return {
        "query_id": query_id,
        "full_name": item.get("full_name"),
        "html_url": item.get("html_url"),
        "description": item.get("description"),
        "stars": int(item.get("stargazers_count") or 0),
        "updated_at": item.get("updated_at"),
        "language": item.get("language"),
        "topics": item.get("topics") or [],
        "license": license_info.get("spdx_id"),
        "fork": bool(item.get("fork")),
    }


def scan(
    config: dict[str, Any],
    fetch_json: Callable[[str], dict[str, Any]],
) -> dict[str, Any]:
    findings = []
    for query in config["queries"]:
        url = f"{API_URL}?{urllib.parse.urlencode({'q': query['query'], 'sort': 'stars', 'order': 'desc', 'per_page': 10})}"
        payload = fetch_json(url)
        repositories = [
            normalize_repository(item, query["id"])
            for item in payload.get("items", [])
            if not item.get("fork")
        ]
        findings.append(
            {
                "id": query["id"],
                "purpose": query["purpose"],
                "query": query["query"],
                "repositories": repositories,
            }
        )
    return {
        "schema": "dreamco.github_pattern_intelligence.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "policy": config["policy"],
        "automatic_code_import": False,
        "findings": findings,
    }


def github_fetcher(token: str) -> Callable[[str], dict[str, Any]]:
    def fetch(url: str) -> dict[str, Any]:
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "dreamco-pattern-intelligence",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
        request = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(request, timeout=15) as response:
            payload = json.loads(response.read().decode("utf-8"))
        time.sleep(1)
        return payload

    return fetch


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    report = scan(config, github_fetcher(os.environ.get("GITHUB_TOKEN", "")))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    count = sum(len(item["repositories"]) for item in report["findings"])
    print(f"Recorded {count} public GitHub repository signals for review.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
