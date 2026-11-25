#!/usr/bin/env python3
"""Download the current public O*NET task-statements export and build curricula.

The official database files are public downloads. No O*NET API key is needed.
"""
from __future__ import annotations

import argparse
import json
import re
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

from build_onet_task_curricula import build, read_rows

SOURCE_PAGE = "https://www.onetcenter.org/database.html"
USER_AGENT = "DreamCo-Buddy-Bootcamp/1.0 (O*NET attribution preserved)"


class DownloadLinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []
        self.page_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "a":
            href = dict(attrs).get("href")
            if href:
                self.links.append(href)

    def handle_data(self, data: str) -> None:
        self.page_text.append(data)


def discover_json_links(parser: DownloadLinkParser) -> dict[str, str]:
    """Return exact JSON download links from the official O*NET database page."""
    discovered: dict[str, str] = {}
    for href in parser.links:
        path = href.split("?", 1)[0]
        if "/dl_files/database/" not in path:
            continue
        filename = path.rsplit("/", 1)[-1]
        if not filename.lower().endswith(".json"):
            continue
        key = filename[:-5]
        if key:
            discovered[key] = href
    return discovered


def read_table_rows(path: Path) -> list[dict[str, str]]:
    """Backward-compatible public name for the JSON/CSV/TSV row reader."""
    return read_rows(path)


def enrich_occupations(result: dict, exports: dict[str, list[dict]], manifest: dict) -> dict:
    """Attach official O*NET profile data, software examples, and task ratings.

    The function copies its input and preserves raw export provenance. It does not
    infer credentials, licenses, or permission to perform regulated work.
    """
    enriched = json.loads(json.dumps(result))
    occupation_data = {
        row.get("onetsoc_code"): row for row in exports.get("occupation_data", [])
        if row.get("onetsoc_code")
    }
    profile_sources = (
        "essential_skills", "transferable_skills", "knowledge", "abilities",
        "work_activities", "work_context", "work_styles", "education",
        "training_and_experience", "job_titles", "related_occupations",
        "career_interest_types", "specific_interest_areas",
    )
    for occupation in enriched.get("occupations", []):
        code = occupation.get("occupation_code")
        base = occupation_data.get(code, {})
        if base.get("title"):
            occupation["occupation_title"] = base["title"]
        if base.get("description"):
            occupation["description"] = base["description"]
        profile = {
            key: [row for row in exports.get(key, []) if row.get("onetsoc_code") == code]
            for key in profile_sources
        }
        software_rows = [row for row in exports.get("software_skills", []) if row.get("onetsoc_code") == code]
        software_examples = sorted({row.get("workplace_example", "").strip()
                                     for row in software_rows if row.get("workplace_example", "").strip()})
        hot_technologies = sorted({row.get("workplace_example", "").strip()
                                   for row in software_rows
                                   if row.get("workplace_example", "").strip()
                                   and str(row.get("hot_technology", "")).strip().upper() in {"Y", "YES", "TRUE", "1"}})
        profile["software_skill_examples"] = software_examples
        profile["hot_technologies"] = hot_technologies
        occupation["profile"] = profile
        job_zone = next((row for row in exports.get("job_zones", []) if row.get("onetsoc_code") == code), None)
        if job_zone:
            occupation["job_zone"] = job_zone
        ratings_by_task: dict[str, list[dict]] = {}
        for row in exports.get("task_ratings", []):
            if row.get("onetsoc_code") == code and row.get("task_id"):
                ratings_by_task.setdefault(row["task_id"], []).append(row)
        for task in occupation.get("tasks", []):
            task["ratings"] = ratings_by_task.get(task.get("task_id"), [])
        for playbook in occupation.get("task_playbooks", []):
            playbook["occupation_profile_ref"] = code
            brief = dict(playbook.get("guide_authoring_brief") or {})
            brief["official_software_examples"] = software_examples
            playbook["guide_authoring_brief"] = brief
            playbook["official_occupation_profile"] = dict(profile)
    enriched.setdefault("source", {})["license"] = (
        "Creative Commons Attribution 4.0 International; verify current O*NET license terms and preserve attribution."
    )
    enriched["source"]["export_manifest"] = manifest
    enriched.setdefault("inventory", {})["enriched_occupation_profiles"] = len(enriched.get("occupations", []))
    return enriched


def fetch_current_export() -> tuple[bytes, str, str]:
    request = urllib.request.Request(SOURCE_PAGE, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=45) as response:
        html = response.read().decode("utf-8", errors="replace")
    parser = DownloadLinkParser()
    parser.feed(html)
    discovered = discover_json_links(parser)
    href = discovered.get("task_statements")
    if not href:
        raise RuntimeError("Could not locate the official current O*NET task_statements.json link; refusing to use a stale guessed URL.")
    if href.startswith("/"):
        url = "https://www.onetcenter.org" + href
    elif href.startswith("http"):
        url = href
    else:
        url = "https://www.onetcenter.org/" + href.lstrip("./")
    text = " ".join(parser.page_text)
    match = re.search(r"O\*NET\s*(?:®|&reg;)?\s*([0-9]+\.[0-9]+)\s*Database", text, re.I)
    version = match.group(1) if match else "current-release-version-unparsed"
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=90) as response:
        payload = response.read()
    return payload, version, url


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--minimum-task-count", type=int, default=10000)
    args = parser.parse_args()
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    payload, version, source_url = fetch_current_export()
    raw_path = out / "onet-task-statements.json"
    raw_path.write_bytes(payload)
    rows = read_rows(raw_path)
    result = build(rows, version)
    result["source"]["official_download_url"] = source_url
    result["source"]["release_page"] = SOURCE_PAGE
    result["source"]["license"] = "Creative Commons Attribution 4.0 International; verify current O*NET license terms and preserve attribution."
    result["inventory"]["download_bytes"] = len(payload)
    result["inventory"]["coverage_check"] = {
        "minimum_task_count": args.minimum_task_count,
        "passed": result["inventory"]["task_statements"] >= args.minimum_task_count,
    }
    if result["inventory"]["task_statements"] < args.minimum_task_count:
        raise SystemExit(
            f"Incomplete O*NET task export: {result['inventory']['task_statements']} "
            f"tasks; expected at least {args.minimum_task_count}."
        )
    (out / "onet-task-curricula.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    summary = [
        "# O*NET occupation and task curricula", "",
        f"- O*NET release: {version}",
        f"- Occupations: {result['inventory']['occupations']}",
        f"- Task statements: {result['inventory']['task_statements']}",
        f"- Official export: {source_url}",
        "- Rights: O*NET database attribution and license terms must be preserved.",
        "- Each task is assigned a Buddy study/practice and supervised business/community pathway brief.",
        "- These are learning plans, not professional credentials or authorization to perform regulated work.",
    ]
    (out / "onet-task-curricula.md").write_text("\n".join(summary) + "\n", encoding="utf-8")
    print(json.dumps(result["inventory"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
