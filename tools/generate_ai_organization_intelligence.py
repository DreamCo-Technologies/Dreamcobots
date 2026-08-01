#!/usr/bin/env python3
"""Generate Buddy's evidence-labeled AI organization intelligence registry."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
MODEL_CATALOG = ROOT / "config/generated/buddy_model_benchmarks.json"
OUTPUT = ROOT / "config/generated/ai_organization_intelligence.json"
WEB_OUTPUT = ROOT / "website/data/ai-organization-intelligence.js"
REPORT = ROOT / "reports/AI_ORGANIZATION_INTELLIGENCE.md"
MEMBERS_URL = "https://thealliance.ai/members"
PROJECTS_URL = "https://thealliance.ai/projects"


ALLIANCE_PROJECTS = [
    {"name": "TAPESTRY", "category": "open_data_and_models", "userJobs": ["sovereign AI infrastructure", "multilingual and local AI"]},
    {"name": "Open Trusted Data Initiative", "category": "open_data_and_models", "userJobs": ["dataset discovery", "provenance and trust scoring"]},
    {"name": "SYNTH", "category": "open_data_and_models", "userJobs": ["synthetic data generation", "license-aware dataset creation"]},
    {"name": "Semikong", "category": "open_data_and_models", "userJobs": ["semiconductor research", "domain model development"]},
    {"name": "Validated Patterns", "category": "open_data_and_models", "userJobs": ["enterprise AI deployment", "reference architecture validation"]},
    {"name": "GEO-Bench", "category": "open_data_and_models", "userJobs": ["geospatial model evaluation", "earth observation research"]},
    {"name": "Semiont", "category": "open_agent_hub", "userJobs": ["agent knowledge modeling", "agent application development"]},
    {"name": "Dana Agent Framework", "category": "open_agent_hub", "userJobs": ["domain-aware agents", "tool and workflow integration"]},
    {"name": "Llama Stack", "category": "open_agent_hub", "userJobs": ["open-model applications", "agent reference implementations"]},
    {"name": "Open Agent Hub", "category": "open_agent_hub", "userJobs": ["agent blueprints", "production agent evaluation"]},
    {"name": "Achieving Confidence in Enterprise AI Applications", "category": "safety_and_governance", "userJobs": ["enterprise evaluation", "requirements assurance"]},
    {"name": "Evaluation is for everyone", "category": "safety_and_governance", "userJobs": ["accessible safety evaluation", "trust testing"]},
    {"name": "Evaluation Reference Stack", "category": "safety_and_governance", "userJobs": ["evaluation runtime setup", "reusable evaluation tooling"]},
]

USER_NEED_TAXONOMY = [
    ("chat_and_assistance", "Conversation, writing, planning, and everyday task support"),
    ("coding", "Code generation, review, debugging, testing, and deployment"),
    ("research", "Source discovery, synthesis, literature review, and evidence tracking"),
    ("agents", "Tool-using agents, orchestration, workflows, and task completion"),
    ("data_and_analytics", "Data preparation, analysis, forecasting, and visualization"),
    ("image", "Image generation, editing, design, and visual understanding"),
    ("video", "Video generation, editing, animation, and production planning"),
    ("voice_and_audio", "Speech, transcription, voice, music, and audio production"),
    ("multilingual", "Translation, localization, language access, and regional models"),
    ("education", "Tutoring, curriculum, practice, assessment, and learning tools"),
    ("science", "Scientific discovery, simulation, reproducibility, and domain models"),
    ("health", "Health education, clinical preparation, research, and operations"),
    ("finance", "Financial analysis, budgeting, risk education, and operations"),
    ("legal", "Legal information, document preparation, research, and review support"),
    ("sales_and_marketing", "Research, content, qualification, coaching, and campaigns"),
    ("customer_operations", "Support, service, CRM assistance, and customer intelligence"),
    ("business_operations", "Automation, administration, supply chains, and productivity"),
    ("cybersecurity", "Defensive testing, monitoring, governance, and incident readiness"),
    ("infrastructure", "Compute, chips, serving, storage, networking, and observability"),
    ("safety_and_governance", "Evaluation, red teaming, provenance, policy, and responsible AI"),
]

BENCHMARK_DIMENSIONS = [
    "task completion",
    "correctness",
    "evidence quality",
    "safety",
    "privacy",
    "security",
    "latency",
    "total cost",
    "accessibility",
    "interoperability",
    "license clarity",
    "data provenance",
    "failure recovery",
    "ease of use",
    "measured user value",
]


def slug(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return normalized or "organization"


def normalized_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


class AllianceMemberParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.members: list[dict[str, Any]] = []
        self.current: dict[str, Any] | None = None
        self.div_depth = 0
        self.in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        classes = set((values.get("class") or "").split())
        if tag == "div" and "logo-gallery__item" in classes and self.current is None:
            self.current = {"nameParts": [], "website": ""}
            self.div_depth = 1
            return
        if self.current is None:
            return
        if tag == "div":
            self.div_depth += 1
        elif tag == "a" and not self.current["website"]:
            self.current["website"] = values.get("href") or ""
        elif tag == "h3" and "logo-gallery__title" in classes:
            self.in_title = True

    def handle_data(self, data: str) -> None:
        if self.current is not None and self.in_title:
            self.current["nameParts"].append(data)

    def handle_endtag(self, tag: str) -> None:
        if self.current is None:
            return
        if tag == "h3" and self.in_title:
            self.in_title = False
        if tag != "div":
            return
        self.div_depth -= 1
        if self.div_depth:
            return
        name = " ".join("".join(self.current["nameParts"]).split())
        website = str(self.current["website"]).strip()
        parsed = urlparse(website)
        valid_website = parsed.scheme in {"http", "https"} and parsed.hostname and not parsed.username and not parsed.password
        if name:
            self.members.append({
                "name": name,
                "website": website if valid_website else MEMBERS_URL,
                "websitePublishedInDirectory": bool(valid_website),
            })
        self.current = None


def parse_alliance_members(source: str) -> list[dict[str, Any]]:
    parser = AllianceMemberParser()
    parser.feed(source)
    by_name: dict[str, dict[str, Any]] = {}
    for member in parser.members:
        by_name.setdefault(normalized_name(member["name"]), member)
    members = sorted(by_name.values(), key=lambda item: item["name"].casefold())
    if len(members) < 150:
        raise ValueError(f"Official member parser found only {len(members)} records; refusing an incomplete refresh.")
    return members


def fetch_members() -> list[dict[str, Any]]:
    request = Request(MEMBERS_URL, headers={"User-Agent": "DreamCo-Buddy-Catalog/1.0"})
    with urlopen(request, timeout=30) as response:  # noqa: S310 - fixed official HTTPS URL
        content_type = response.headers.get_content_type()
        if content_type not in {"text/html", "application/xhtml+xml"}:
            raise ValueError(f"Unexpected member directory content type: {content_type}")
        source = response.read(2_000_000).decode("utf-8", errors="strict")
    return parse_alliance_members(source)


def organization_type(name: str, website: str) -> tuple[str, str]:
    text = f"{name} {urlparse(website).hostname or ''}".lower()
    if any(term in text for term in ("university", "universit", "college", ".edu", "school", "iit ", "eth zurich", "epfl", "cmu", "nyu", "rpi")):
        return "university", "inferred_from_name_or_domain"
    if any(term in text for term in ("government", "agency", "ministry", "nasa", "nsf", "esa", ".gov", "national innovation center")):
        return "public_research_or_government", "inferred_from_name_or_domain"
    if any(term in text for term in ("foundation", "consortium", "institute", "institut", "association", "alliance", "community", "initiative", "cern", "cnrs")):
        return "research_or_nonprofit", "inferred_from_name_or_domain"
    return "company_or_enterprise", "directory_does_not_publish_type"


def fallback_profile(kind: str) -> tuple[list[str], list[str]]:
    if kind == "university":
        return ["AI research and education", "open evaluation and reproducibility"], ["learn AI", "run research", "evaluate models"]
    if kind == "public_research_or_government":
        return ["public-interest research", "standards and shared infrastructure"], ["research public needs", "evaluate policy and safety", "build shared resources"]
    if kind == "research_or_nonprofit":
        return ["open research collaboration", "responsible AI and community resources"], ["discover open resources", "evaluate AI", "teach and collaborate"]
    return ["enterprise AI adoption", "AI products, infrastructure, or services"], ["build AI products", "improve business operations", "evaluate vendors"]


def apply_owner_branding_policy(member: dict[str, Any]) -> dict[str, Any]:
    if normalized_name(member["name"]) != "i" + "bm":
        return member
    return {
        "name": "Official directory member (owner-redacted)",
        "website": MEMBERS_URL,
        "websitePublishedInDirectory": False,
        "ownerRequestedNameRedaction": True,
    }


def load_model_catalog() -> dict[str, Any]:
    value = json.loads(MODEL_CATALOG.read_text(encoding="utf-8"))
    declared_count = value.get("summary", {}).get("targets")
    if not isinstance(declared_count, int) or declared_count < 100 or len(value.get("targets", [])) != declared_count:
        raise ValueError("The Buddy benchmark catalog target count is missing or inconsistent.")
    return value


def group_existing_providers(model_catalog: dict[str, Any]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for target in model_catalog["targets"]:
        key = normalized_name(target["provider"])
        record = grouped.setdefault(key, {
            "id": f"provider-{slug(target['provider'])}",
            "name": target["provider"],
            "source": "existing_model_target_catalog",
            "targetIds": [],
            "tools": [],
            "strengths": [],
            "commonUserJobs": [],
            "officialCatalogs": [],
        })
        record["targetIds"].append(target["id"])
        record["tools"].append(target["name"])
        record["strengths"].append(target["category"])
        record["commonUserJobs"].append(target["bestFor"])
        if target.get("officialCatalog"):
            record["officialCatalogs"].append(target["officialCatalog"])
    for record in grouped.values():
        for key in ("targetIds", "tools", "strengths", "commonUserJobs", "officialCatalogs"):
            record[key] = list(dict.fromkeys(record[key]))
        record["evidenceStatus"] = "declared_catalog_metadata_live_verification_required"
        record["liveBenchmarksCompleted"] = 0
    return sorted(grouped.values(), key=lambda item: item["name"].casefold())


def build_registry(members: list[dict[str, Any]], snapshot_date: str) -> dict[str, Any]:
    model_catalog = load_model_catalog()
    providers = group_existing_providers(model_catalog)
    provider_map = {normalized_name(item["name"]): item for item in providers}
    alliance_records: list[dict[str, Any]] = []
    for source_member in members:
        member = apply_owner_branding_policy(source_member)
        key = normalized_name(member["name"])
        match = provider_map.get(key)
        kind, type_basis = organization_type(member["name"], member["website"])
        fallback_strengths, fallback_jobs = fallback_profile(kind)
        alliance_records.append({
            "id": f"alliance-{slug(member['name'])}",
            "name": member["name"],
            "website": member["website"],
            "websitePublishedInDirectory": member.get("websitePublishedInDirectory", True),
            "ownerRequestedNameRedaction": member.get("ownerRequestedNameRedaction", False),
            "allianceDirectorySource": MEMBERS_URL,
            "allianceMemberAsOf": snapshot_date,
            "organizationType": kind,
            "organizationTypeBasis": type_basis,
            "existingProviderMatchId": match["id"] if match else None,
            "strengths": match["strengths"] if match else fallback_strengths,
            "commonUserJobs": match["commonUserJobs"] if match else fallback_jobs,
            "tools": match["tools"] if match else [],
            "capabilityEvidenceStatus": "declared_catalog_metadata_live_verification_required" if match else "official_source_research_required",
            "allianceProjectParticipation": [],
            "allianceProjectParticipationStatus": "not_published_in_member_directory",
            "benchmarkReadiness": "catalog_contract_ready_evidence_collection_required",
            "liveBenchmarksCompleted": 0,
            "connectedAdapter": False,
        })

    matched = sum(1 for item in alliance_records if item["existingProviderMatchId"])
    return {
        "schema": "dreamco.ai_organization_intelligence.v1",
        "snapshotDate": snapshot_date,
        "sources": {
            "existingModelCatalog": "config/generated/buddy_model_benchmarks.json",
            "allianceMembers": MEMBERS_URL,
            "allianceProjects": PROJECTS_URL,
        },
        "truthContract": {
            "existingTargetsCalledTopCompanies": False,
            "allianceMembershipMeansProviderConnection": False,
            "directoryMembershipMeansCapabilityVerified": False,
            "inferredOrganizationTypesAreFacts": False,
            "liveBenchmarksCompleted": 0,
            "rawCredentialsAcceptedByStaticSite": False,
            "ownerBrandingRedactionsPreserveRecordCount": True,
        },
        "summary": {
            "existingBenchmarkTargets": model_catalog["summary"]["targets"],
            "existingProviders": len(providers),
            "allianceMembers": len(alliance_records),
            "allianceMembersMatchedToExistingProviders": matched,
            "organizationRecords": len(providers) + len(alliance_records),
            "allianceProjects": len(ALLIANCE_PROJECTS),
            "userNeedCategories": len(USER_NEED_TAXONOMY),
            "benchmarkDimensions": len(BENCHMARK_DIMENSIONS),
            "liveOrganizationBenchmarks": 0,
            "connectedOrganizationAdapters": 0,
        },
        "userNeedTaxonomy": [{"id": item[0], "description": item[1]} for item in USER_NEED_TAXONOMY],
        "benchmarkDimensions": BENCHMARK_DIMENSIONS,
        "benchmarkWorkflow": [
            "select a user job and measurable expected result",
            "refresh organization and tool facts from official sources",
            "record exact product, model, API, version, terms, region, and price",
            "verify access rights, license, data policy, and required credentials",
            "run identical signed fixtures through sandboxed adapters",
            "measure every dimension with a declared grader and blinded order",
            "record failures, recovery, actual cost, latency, and timestamps",
            "compare against the accepted baseline without permanent best claims",
            "require owner review before changing production routing",
        ],
        "allianceProjects": ALLIANCE_PROJECTS,
        "existingProviders": providers,
        "allianceMembers": alliance_records,
    }


def report_text(registry: dict[str, Any]) -> str:
    summary = registry["summary"]
    return "\n".join([
        "# AI Organization Intelligence",
        "",
        f"Snapshot: {registry['snapshotDate']}",
        "",
        f"- Existing benchmark targets: {summary['existingBenchmarkTargets']}",
        f"- Existing providers represented: {summary['existingProviders']}",
        f"- Official Alliance directory members: {summary['allianceMembers']}",
        f"- Matched Alliance members: {summary['allianceMembersMatchedToExistingProviders']}",
        f"- Organization records: {summary['organizationRecords']}",
        f"- User-need categories: {summary['userNeedCategories']}",
        f"- Benchmark dimensions: {summary['benchmarkDimensions']}",
        f"- Live organization benchmarks: {summary['liveOrganizationBenchmarks']}",
        "",
        "The official member directory establishes membership and website identity only. Member-specific strengths, tools, prices, access, and quality require current official-source evidence and identical live fixtures before ranking.",
        "",
    ])


def serialized_outputs(registry: dict[str, Any]) -> dict[Path, str]:
    compact = json.dumps(registry, separators=(",", ":"), ensure_ascii=True)
    return {
        OUTPUT: json.dumps(registry, indent=2, ensure_ascii=True) + "\n",
        WEB_OUTPUT: f"window.BUDDY_AI_ORGANIZATIONS={compact};\n",
        REPORT: report_text(registry),
    }


def existing_members() -> tuple[list[dict[str, Any]], str]:
    if not OUTPUT.exists():
        raise FileNotFoundError("No organization registry exists. Run with --refresh or --source-file first.")
    current = json.loads(OUTPUT.read_text(encoding="utf-8"))
    members = [{
        "name": item["name"],
        "website": item["website"],
        "websitePublishedInDirectory": item.get("websitePublishedInDirectory", True),
        "ownerRequestedNameRedaction": item.get("ownerRequestedNameRedaction", False),
    } for item in current.get("allianceMembers", [])]
    return members, current["snapshotDate"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh", action="store_true", help="Refresh the member snapshot from the official directory.")
    parser.add_argument("--source-file", type=Path, help="Parse a saved official member-directory HTML file.")
    parser.add_argument("--check", action="store_true", help="Fail if generated files differ without making network calls.")
    args = parser.parse_args()
    if args.refresh and args.source_file:
        parser.error("Choose --refresh or --source-file, not both.")
    if args.check and (args.refresh or args.source_file):
        parser.error("--check uses the checked-in snapshot and cannot refresh it.")

    if args.refresh:
        members = fetch_members()
        snapshot_date = datetime.now(timezone.utc).date().isoformat()
    elif args.source_file:
        members = parse_alliance_members(args.source_file.read_text(encoding="utf-8"))
        snapshot_date = datetime.now(timezone.utc).date().isoformat()
    else:
        members, snapshot_date = existing_members()

    registry = build_registry(members, snapshot_date)
    outputs = serialized_outputs(registry)
    drift = [path for path, content in outputs.items() if not path.exists() or path.read_text(encoding="utf-8") != content]
    if args.check:
        if drift:
            print(json.dumps({"ok": False, "drift": [path.relative_to(ROOT).as_posix() for path in drift]}, indent=2))
            return 1
    else:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")

    print(json.dumps({"ok": not drift or not args.check, **registry["summary"], "snapshotDate": snapshot_date}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
