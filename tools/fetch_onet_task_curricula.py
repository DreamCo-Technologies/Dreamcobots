#!/usr/bin/env python3
"""Fetch the current official O*NET JSON tables and build enriched occupation curricula.

The source page is parsed at runtime; no stale release URL is hard-coded.
Required tables cover tasks, occupation data, skills, knowledge, abilities,
software skills, work activities/context/styles and education/training.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse
from typing import Any

from build_onet_task_curricula import build, pick

SOURCE_PAGE = "https://www.onetcenter.org/database.html"
USER_AGENT = "DreamCo-Buddy-Bootcamp/1.1 (O*NET attribution preserved)"

REQUIRED_TABLES = {
    "task_statements": 10000,
    "occupation_data": 900,
    "essential_skills": 10000,
    "transferable_skills": 20000,
    "knowledge": 50000,
    "abilities": 80000,
    "software_skills": 20000,
    "work_activities": 50000,
    "work_context": 200000,
    "work_styles": 20000,
    "education": 8000,
    "training_and_experience": 20000,
    "job_zones": 800,
    "content_model_reference": 2500,
}
OPTIONAL_TABLES = [
    "task_ratings", "job_titles", "related_occupations", "scales_reference",
    "tasks_to_dwas", "gwas_to_iwas_to_dwas", "task_categories",
    "career_interest_types", "specific_interest_areas",
    "education_categories", "training_and_experience_categories",
    "work_context_categories", "work_styles_to_work_activities",
    "work_styles_to_work_context", "essential_skills_to_work_activities",
    "essential_skills_to_work_context", "transferable_skills_to_work_activities",
    "transferable_skills_to_work_context", "abilities_to_work_activities",
    "abilities_to_work_context",
]
PROFILE_TABLES = {
    "essential_skills": "essential_skills",
    "transferable_skills": "transferable_skills",
    "knowledge": "knowledge",
    "abilities": "abilities",
    "software_skills": "software_skills",
    "work_activities": "work_activities",
    "work_context": "work_context",
    "work_styles": "work_styles",
    "education": "education",
    "training_and_experience": "training_and_experience",
    "job_titles": "alternate_titles",
    "related_occupations": "related_occupations",
    "career_interest_types": "career_interests",
    "specific_interest_areas": "specific_interests",
}


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


def fetch_source_page() -> tuple[DownloadLinkParser, str]:
    request = urllib.request.Request(SOURCE_PAGE, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        html = response.read().decode("utf-8", errors="replace")
    parser = DownloadLinkParser()
    parser.feed(html)
    page_text = " ".join(parser.page_text)
    match = re.search(r"O\*NET\s*(?:®|&reg;)?\s*([0-9]+\.[0-9]+)\s*Database", page_text, re.I)
    version = match.group(1) if match else "current-release-version-unparsed"
    return parser, version


def resolve_link(link: str) -> str:
    return urljoin(SOURCE_PAGE, link)


def discover_json_links(parser: DownloadLinkParser) -> dict[str, str]:
    found: dict[str, str] = {}
    for link in parser.links:
        parsed = urlparse(link)
        path = parsed.path.lower()
        if "/dl_files/database/" not in path or not path.endswith(".json"):
            continue
        name = Path(path).name[:-5]
        if name not in found:
            found[name] = resolve_link(link)
    return found


def fetch_json_table(url: str, *, timeout: int = 180) -> bytes:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def read_table_rows(path: Path) -> list[dict[str, str]]:
    document = json.loads(path.read_text(encoding="utf-8-sig"))
    def locate(value: Any) -> list[dict[str, Any]]:
        if isinstance(value, list):
            if value and all(isinstance(item, dict) for item in value):
                return value
            for item in value:
                found = locate(item)
                if found:
                    return found
        elif isinstance(value, dict):
            for key in ("data", "rows", "records", "items", "results"):
                if key in value:
                    found = locate(value[key])
                    if found:
                        return found
            for child in value.values():
                found = locate(child)
                if found:
                    return found
        return []
    records = locate(document)
    return [{str(key): "" if value is None else str(value) for key, value in row.items()} for row in records]


def compact_record(row: dict[str, str], table: str) -> dict[str, Any]:
    keys = (
        "element_id", "element_name", "scale_id", "scale_name", "data_value",
        "n", "standard_error", "lower_ci_bound", "upper_ci_bound",
        "recommend_suppress", "not_relevant", "date_updated", "domain_source",
        "workplace_example", "hot_technology", "in_demand", "category",
        "percentage", "job_zone", "job_zone_description", "alternate_title",
        "related_onetsoc_code", "related_title", "relatedness_tier",
        "short_title", "description", "title",
    )
    normalized = {
        str(key).strip().lower().replace(" ", "_").replace("-", "_"): value
        for key, value in row.items()
    }
    record = {key: normalized[key] for key in keys if key in normalized and normalized[key] != ""}
    record["source_table"] = table
    return record


def enrich_occupations(result: dict[str, Any], exports: dict[str, list[dict[str, str]]],
                       file_manifest: dict[str, dict[str, Any]]) -> dict[str, Any]:
    occupations = result.get("occupations", [])
    by_code = {row.get("occupation_code"): row for row in occupations}
    task_index: dict[tuple[str, str], dict[str, Any]] = {}
    for occupation in occupations:
        occupation.setdefault("profile", {
            "essential_skills": [], "transferable_skills": [], "knowledge": [],
            "abilities": [], "software_skills": [], "work_activities": [],
            "work_context": [], "work_styles": [], "education": [],
            "training_and_experience": [], "alternate_titles": [],
            "related_occupations": [], "career_interests": [],
            "specific_interests": [],
        })
        for task in occupation.get("tasks", []):
            task_index[(occupation.get("occupation_code"), task.get("task_id"))] = task

    for table, target in PROFILE_TABLES.items():
        for row in exports.get(table, []):
            code = pick(row, "O*NET-SOC Code", "O*NET SOC Code", "onetsoc_code", "occupation code")
            occupation = by_code.get(code)
            if not occupation:
                continue
            if table == "occupation_data":
                description = pick(row, "Description", "occupation description", "definition")
                if description:
                    occupation["description"] = description
                continue
            if table == "job_titles":
                pass
            occupation["profile"][target].append(compact_record(row, table))

    for row in exports.get("occupation_data", []):
        code = pick(row, "O*NET-SOC Code", "O*NET SOC Code", "onetsoc_code", "occupation code")
        occupation = by_code.get(code)
        if occupation:
            occupation["description"] = pick(row, "Description", "occupation description", "definition") or occupation.get("description", "")
            occupation["occupation_data"] = compact_record(row, "occupation_data")

    for row in exports.get("job_zones", []):
        code = pick(row, "O*NET-SOC Code", "onetsoc_code", "occupation code")
        occupation = by_code.get(code)
        if occupation:
            occupation["job_zone"] = compact_record(row, "job_zones")

    for row in exports.get("task_ratings", []):
        code = pick(row, "O*NET-SOC Code", "onetsoc_code", "occupation code")
        task_id = pick(row, "Task ID", "task id")
        task = task_index.get((code, task_id))
        if task:
            task.setdefault("ratings", []).append(compact_record(row, "task_ratings"))

    for occupation in occupations:
        profile = occupation["profile"]
        occupation["profile_counts"] = {key: len(value) for key, value in profile.items()}
        occupation["profile"]["software_skill_examples"] = [
            row.get("workplace_example") for row in profile["software_skills"] if row.get("workplace_example")
        ]
        occupation["profile"]["hot_technologies"] = [
            row.get("workplace_example") for row in profile["software_skills"]
            if row.get("workplace_example") and row.get("hot_technology", "").upper() == "Y"
        ]
        occupation["profile"]["in_demand_software"] = [
            row.get("workplace_example") for row in profile["software_skills"]
            if row.get("workplace_example") and row.get("in_demand", "").upper() == "Y"
        ]
        for playbook in occupation.get("task_playbooks", []):
            playbook["occupation_profile_ref"] = occupation.get("occupation_code")
            playbook["occupation_profile_counts"] = occupation.get("profile_counts", {})
            playbook["guide_authoring_brief"]["official_software_examples"] = profile["software_skill_examples"][:25]
            playbook["guide_authoring_brief"]["official_hot_technologies"] = profile["hot_technologies"][:25]
            playbook["guide_authoring_brief"]["official_in_demand_software"] = profile["in_demand_software"][:25]
            playbook["guide_authoring_brief"]["official_skills_and_knowledge"] = {
                "essential_skills": profile["essential_skills"][:20],
                "transferable_skills": profile["transferable_skills"][:20],
                "knowledge": profile["knowledge"][:20],
                "abilities": profile["abilities"][:20],
            }
    result["source"]["license"] = "Creative Commons Attribution 4.0 International. Attribute O*NET 31.0 Database and the U.S. Department of Labor, Employment and Training Administration; link the license and disclose changes."
    result["source"]["data_files"] = file_manifest
    result["inventory"]["occupation_profiles_enriched"] = sum(bool(row.get("profile_counts")) for row in occupations)
    result["inventory"]["profile_record_counts"] = {
        table: sum(len(row.get("profile", {}).get(target, [])) for row in occupations)
        for table, target in PROFILE_TABLES.items()
    }
    result["inventory"]["source_table_counts"] = {
        table: len(rows) for table, rows in exports.items()
    }
    return result


def fetch_current_exports(out: Path) -> tuple[dict[str, list[dict[str, str]]], str, dict[str, dict[str, Any]]]:
    parser, version = fetch_source_page()
    links = discover_json_links(parser)
    desired = set(REQUIRED_TABLES) | set(OPTIONAL_TABLES)
    missing_required = sorted(set(REQUIRED_TABLES) - set(links))
    if missing_required:
        raise RuntimeError(
            "Official O*NET page did not expose required JSON files: " + ", ".join(missing_required)
        )
    exports: dict[str, list[dict[str, str]]] = {}
    manifest: dict[str, dict[str, Any]] = {}
    for table in sorted(desired):
        url = links.get(table)
        if not url:
            manifest[table] = {"status": "not_published_on_current_page"}
            continue
        payload = fetch_json_table(url)
        file_path = out / f"onet-{table}.json"
        file_path.write_bytes(payload)
        rows = read_rows(file_path)
        exports[table] = rows
        manifest[table] = {
            "status": "downloaded",
            "url": url,
            "filename": file_path.name,
            "sha256": hashlib.sha256(payload).hexdigest(),
            "bytes": len(payload),
            "rows": len(rows),
            "version": version,
        }
    return exports, version, manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--minimum-task-count", type=int, default=10000)
    parser.add_argument("--minimum-occupation-count", type=int, default=900)
    args = parser.parse_args()
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    exports, version, manifest = fetch_current_exports(out)
    tasks = exports.get("task_statements", [])
    result = build(tasks, version)
    result["source"]["official_url"] = SOURCE_PAGE
    result["inventory"]["download_bytes"] = sum(item.get("bytes", 0) for item in manifest.values())
    result = enrich_occupations(result, exports, manifest)
    coverage = {
        "minimum_task_count": args.minimum_task_count,
        "minimum_occupation_count": args.minimum_occupation_count,
        "task_count_passed": result["inventory"]["task_statements"] >= args.minimum_task_count,
        "occupation_count_passed": result["inventory"]["occupations"] >= args.minimum_occupation_count,
        "required_tables_present": all(manifest.get(name, {}).get("status") == "downloaded" for name in REQUIRED_TABLES),
        "required_table_counts": {name: manifest.get(name, {}).get("rows", 0) for name in REQUIRED_TABLES},
        "passed": False,
    }
    coverage["passed"] = coverage["task_count_passed"] and coverage["occupation_count_passed"] and coverage["required_tables_present"]
    result["inventory"]["coverage_check"] = coverage
    if not coverage["passed"]:
        raise SystemExit("Incomplete O*NET 31.0 inventory: task, occupation or required profile-table coverage check failed.")
    (out / "onet-task-curricula.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    summary = [
        "# O*NET occupation, competency and task curricula", "",
        f"- O*NET release: {version}",
        f"- Occupations: {result['inventory']['occupations']}",
        f"- Task statements: {result['inventory']['task_statements']}",
        f"- Enriched occupation profiles: {result['inventory']['occupation_profiles_enriched']}",
        f"- Software skill records: {result['inventory']['profile_record_counts'].get('software_skills', 0)}",
        f"- Knowledge records: {result['inventory']['profile_record_counts'].get('knowledge', 0)}",
        f"- Ability records: {result['inventory']['profile_record_counts'].get('abilities', 0)}",
        f"- Official source: {SOURCE_PAGE}",
        "- License: CC BY 4.0; attribution and change disclosure preserved.",
        "- Every task has a professional tool and agentic workflow guide brief; exact software examples are linked from official occupation profiles.",
        "- Learning plans are not professional credentials or authorization to perform regulated work.",
    ]
    (out / "onet-task-curricula.md").write_text("\n".join(summary) + "\n", encoding="utf-8")
    print(json.dumps(result["inventory"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
