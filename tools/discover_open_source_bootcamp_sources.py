#!/usr/bin/env python3
"""Discover public GitHub and Hugging Face learning resources.

Discovery is metadata-first. It does not clone repositories, download media,
train models, or grant rights. Unknown licenses remain review-only/blocked.
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
    if not spdx or spdx.upper() in {"NOASSERTION", "OTHER"}:
        return "rights_pending"
    return "license_review_required"


def github_repo(repo: str, token: str | None) -> dict[str, Any]:
    data = request_json(f"https://api.github.com/repos/{repo}", token)
    lic = (data.get("license") or {}).get("spdx_id")
    return {
        "source_type": "github_repository", "source_id": data.get("full_name"),
        "url": data.get("html_url"), "description": data.get("description"),
        "default_branch": data.get("default_branch"), "updated_at": data.get("updated_at"),
        "stars": data.get("stargazers_count"), "license_spdx": lic,
        "rights_state": license_status(lic), "archived": data.get("archived", False),
        "topics": data.get("topics", []), "discovered_at": now(),
    }


def github_search(topic: str, limit: int, token: str | None) -> list[dict[str, Any]]:
    query = urllib.parse.urlencode({"q": f"topic:{topic} stars:>25", "sort": "stars", "order": "desc", "per_page": limit})
    data = request_json(f"https://api.github.com/search/repositories?{query}", token)
    rows = []
    for item in data.get("items", []):
        lic = (item.get("license") or {}).get("spdx_id")
        rows.append({"source_type":"github_repository","source_id":item.get("full_name"),
            "url":item.get("html_url"),"description":item.get("description"),
            "default_branch":item.get("default_branch"),"updated_at":item.get("updated_at"),
            "stars":item.get("stargazers_count"),"license_spdx":lic,
            "rights_state":license_status(lic),"archived":item.get("archived",False),
            "topics":item.get("topics",[]),"discovery_topic":topic,"discovered_at":now()})
    return rows


def hf_search(kind: str, term: str, limit: int) -> list[dict[str, Any]]:
    query = urllib.parse.urlencode({"search": term, "limit": limit})
    data = request_json(f"https://huggingface.co/api/{kind}?{query}")
    rows = []
    for item in data if isinstance(data, list) else []:
        card = item.get("cardData") or {}
        lic = card.get("license") or (item.get("tags") or [])
        if isinstance(lic, list):
            lic = next((x.split(":", 1)[1] for x in lic if x.startswith("license:")), None)
        rows.append({
            "source_type": f"huggingface_{kind[:-1] if kind.endswith('s') else kind}",
            "source_id": item.get("id"), "url": f"https://huggingface.co/{item.get('id')}",
            "pipeline_tag": item.get("pipeline_tag"), "tags": item.get("tags", []),
            "license": lic, "rights_state": license_status(lic),
            "downloads": item.get("downloads"), "likes": item.get("likes"),
            "last_modified": item.get("lastModified"), "discovered_at": now(),
        })
    return rows


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT))
    parser.add_argument("--hf-limit-per-subject", type=int, default=20)
    parser.add_argument("--github-limit-per-topic", type=int, default=10)
    args = parser.parse_args()
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
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
            for row in github_search(topic, args.github_limit_per_topic, token):
                records.append(row)
        except (urllib.error.URLError, TimeoutError, ValueError, KeyError) as exc:
            errors.append({"source": f"github-topic:{topic}", "error": str(exc)})
        time.sleep(0.2)

    for subject in config["discovery"]["hugging_face_subjects"]:
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
        if key[1] and key not in unique:
            unique[key] = row
    final = {
        "schema": "dreamco.buddy_bootcamp_discovery_snapshot.v1",
        "generated_at": now(),
        "discovery_scope": {"hf_subject_count": len(config["discovery"]["hugging_face_subjects"]),
                            "hf_artifact_types": config["discovery"]["hugging_face_hub_types"],
                            "github_seed_count": len(seen)},
        "counts": {"discovered_unique": len(unique), "rights_pending_or_review": sum(r["rights_state"] != "approved" for r in unique.values()),
                   "errors": len(errors)},
        "resources": list(unique.values()), "errors": errors,
        "truth_boundary": "Discovery metadata is not a summary, rights approval, training authorization, or mastery evidence."
    }
    (out_dir / "discovery-snapshot.json").write_text(json.dumps(final, indent=2) + "\n", encoding="utf-8")
    summary = ["# Buddy Bootcamp weekly discovery", "", f"- Generated: {final['generated_at']}",
               f"- Unique resources discovered: {len(unique)}", f"- Rights review required: {final['counts']['rights_pending_or_review']}",
               f"- Discovery errors: {len(errors)}", "",
               "This run discovers metadata only. It does not download source media, create full guides, or train Buddy."]
    (out_dir / "summary.md").write_text("\n".join(summary) + "\n", encoding="utf-8")
    print(json.dumps(final["counts"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
