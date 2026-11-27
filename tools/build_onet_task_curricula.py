#!/usr/bin/env python3
"""Build occupation/task learning paths from official O*NET JSON or tabular exports."""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

SOFTWARE_CAPABILITY_CATEGORIES = [
    "industry-specific line-of-business systems", "CRM and customer success platforms",
    "ERP and business management", "accounting, payroll and tax software",
    "project, portfolio and work management", "scheduling, dispatch and workforce management",
    "document, records and knowledge management", "spreadsheets, databases and BI",
    "data integration, ETL and workflow automation", "communications, collaboration and contact centers",
    "sales enablement, marketing automation and ecommerce", "procurement, inventory and supply chain",
    "CAD, BIM, GIS and technical design where relevant", "simulation, digital twins and specialist engineering tools",
    "development environments, source control, testing and CI/CD where relevant",
    "cloud, infrastructure, monitoring and observability where relevant",
    "cybersecurity, identity, secrets and endpoint protection",
    "AI assistants, agent frameworks, retrieval and model evaluation",
    "image, audio, video and content production where relevant",
    "mobile, field-service and offline-first applications",
    "accessibility, localization and assistive technology",
    "compliance, audit, risk and quality management",
    "payments, billing, subscriptions and financial operations",
    "customer portals, help desks and ticketing",
    "reporting, analytics, forecasting and decision support",
    "backup, disaster recovery and business continuity"
]

AGENT_CAPABILITIES = [
    "research and source verification", "task decomposition and prerequisite planning",
    "browser and computer-use interaction within approved scopes", "API and connector integration",
    "structured data extraction and validation", "document, spreadsheet and presentation authoring",
    "CRM updates and customer communication drafting", "calendar, scheduling and dispatch support",
    "code generation, debugging and test execution in authorized sandboxes",
    "workflow automation, event handling, retries and rollback",
    "data analysis, forecasting and dashboard creation", "proposal, quote and statement-of-work preparation",
    "inventory, procurement and supplier comparison", "quality assurance and acceptance-test execution",
    "multimodal interpretation of authorized images, audio and video",
    "knowledge-base retrieval, citation and version tracking", "risk detection and exception escalation",
    "progress reporting, audit logs and evidence capture", "multi-agent delegation with bounded tool permissions",
    "human approval handoff for consequential actions"
]



def _normalized_json_key(value: Any) -> str:
    text = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", str(value))
    return " ".join(text.casefold().replace("_", " ").replace("-", " ").split())


def flatten_records(value: Any) -> list[dict[str, Any]]:
    """Find O*NET task records in JSON despite wrapper-key casing differences."""
    if isinstance(value, list):
        records = [item for item in value if isinstance(item, dict)]
        if records and any(
            any("task" in _normalized_json_key(key) for key in row)
            for row in records
        ):
            return records
        result: list[dict[str, Any]] = []
        for item in value:
            result.extend(flatten_records(item))
        return result
    if isinstance(value, dict):
        preferred = {"row", "task statements", "task statements data", "task", "data"}
        for key, nested in value.items():
            if _normalized_json_key(key) in preferred:
                found = flatten_records(nested)
                if found:
                    return found
        for nested in value.values():
            if isinstance(nested, (dict, list)):
                found = flatten_records(nested)
                if found and any(
                    any("task" in _normalized_json_key(key) for key in row)
                    for row in found
                ):
                    return found
    return []


def read_rows(path: Path) -> list[dict[str, str]]:
    if path.suffix.lower() == ".json":
        document = json.loads(path.read_text(encoding="utf-8-sig"))
        records = flatten_records(document)
        return [{str(key): "" if value is None else str(value) for key, value in row.items()} for row in records]
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        sample = handle.read(4096)
        handle.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters="\\t,;")
        except csv.Error:
            dialect = csv.excel_tab
        return list(csv.DictReader(handle, dialect=dialect))


def pick(row: dict[str, str], *names: str) -> str:
    def normalize_key(value: str) -> str:
        return re.sub(r"[^a-z0-9]+", "", str(value).casefold())

    normalized = {
        normalize_key(key): str(value or "").strip()
        for key, value in row.items()
    }
    for name in names:
        value = normalized.get(normalize_key(name))
        if value:
            return value
    return ""


def build(rows: list[dict[str, str]], version: str) -> dict[str, Any]:
    occupations: dict[str, dict[str, Any]] = defaultdict(
        lambda: {"occupation_code": "", "occupation_title": "", "tasks": []}
    )
    seen_tasks: set[tuple[str, str]] = set()
    for row in rows:
        code = pick(row, "O*NET-SOC Code", "O*NET SOC Code", "onetsoc_code", "occupation code")
        task_id = pick(row, "Task ID", "task id", "id")
        title = pick(row, "Task", "Task Statement", "task statement", "title")
        if not code or not task_id or not title or (code, task_id) in seen_tasks:
            continue
        seen_tasks.add((code, task_id))
        item = occupations[code]
        item["occupation_code"] = code
        item["occupation_title"] = pick(row, "Occupation Title", "Title") or item["occupation_title"]
        item["tasks"].append({
            "task_id": task_id, "task": title,
            "task_type": pick(row, "Task Type", "task type", "category") or "unspecified",
            "date": pick(row, "Date", "date"),
            "domain_source": pick(row, "Domain Source", "domain source"),
            "importance": pick(row, "Importance", "importance") or None,
        })
    output = []
    for code, item in sorted(occupations.items()):
        tasks = sorted(item["tasks"], key=lambda task: (task["task_type"] != "Core", task["task_id"]))
        item["task_count"] = len(tasks)
        item["learning_path"] = {
            "phase_1": "Understand occupation purpose, work context, knowledge, skills and tools using the official occupation profile.",
            "phase_2": "Study every listed core and supplemental task; identify prerequisites, safety requirements and quality standards.",
            "phase_3": "Practice with simulations and supervised projects; do not claim occupational competence from reading.",
            "phase_4": "Create an ethical service/business-development playbook only where a legitimate buyer and permitted scope exist.",
            "phase_5": "Complete independent assessment, portfolio evidence, references and any required credential or license checks.",
        }
        item["task_playbooks"] = [{
            "task_id": task["task_id"], "task": task["task"],
            "learning_summary_status": "not_yet_authored_by_buddy",
            "learning_summary_required": True, "practice_required": True,
            "guide_authoring_brief": {
                "must_explain": [
                    "purpose, customer problem and real-world context",
                    "prerequisite knowledge, skills, abilities and proficiency levels",
                    "complete workflow and every meaningful subtask from intake through closeout",
                    "inputs, outputs, data structures, records and handoffs",
                    "common, specialist and high-end software categories used in this occupation",
                    "current leading commercial tools, open-source alternatives and offline/local options",
                    "agent capabilities, tool permissions, automation boundaries and human handoffs",
                    "decision rules, exceptions, edge cases and escalation triggers",
                    "quality standards, safety controls, legal duties, licenses and credentials",
                    "privacy, security, retention, accessibility and records requirements",
                    "labor, time, material, compute, insurance and overhead cost drivers",
                    "buyer types, market demand evidence, competitors and procurement routes",
                    "service packaging, pricing, unit economics and realistic delivery capacity",
                    "sales discovery, qualification, CRM, proposals, negotiation and account care",
                    "delivery SOP, customer support, warranty, rework and continuous improvement",
                ],
                "software_categories_to_assess": SOFTWARE_CAPABILITY_CATEGORIES,
                "agent_capabilities_to_assess": AGENT_CAPABILITIES,
                "tool_research_rule": "For each relevant category, research current high-end commercial products, widely used professional tools, open-source alternatives, local/offline options, integrations, costs, license terms and security posture. Record verification date and official product links; do not invent adoption or recommend a tool solely because it is popular.",
                "must_include": [
                    "source-grounded detailed summary", "step-by-step workflow", "tool comparison matrix",
                    "worked examples", "beginner, intermediate and advanced exercises",
                    "sandbox simulation", "portfolio capstone", "acceptance tests and answer key",
                    "common failure scenarios and recovery", "official citations and rights evidence",
                ],
                "must_not_infer": ["licenses", "credentials", "buyer demand", "legal authority", "professional competence"],
            },
            "commercial_pathway": {
                "status": "research_required",
                "possible_buyer_types": ["consumer", "small business", "enterprise", "nonprofit", "government buyer", "prime contractor", "subcontractor"],
                "buyer_research": ["buyer pain and authority", "budget and procurement route", "competitor and incumbent analysis", "demand evidence and seasonality"],
                "offer": "Define only after buyer research, capability proof, legal scope, credential and insurance review.",
                "pricing_models_to_evaluate": ["hourly", "fixed fee", "retainer", "subscription", "usage-based", "project milestone", "cost-plus where lawful"],
                "unit_economics": ["labor and delivery time", "materials and software", "compute and API usage", "insurance and compliance", "sales acquisition cost", "support and rework", "tax and cash-flow timing"],
                "sales_sequence": [
                    "identify legitimate buyer", "confirm problem and authority", "qualify need and budget",
                    "research incumbent and procurement route", "define scope, exclusions and acceptance criteria",
                    "estimate fully burdened cost, working capital and delivery risk",
                    "prepare truthful capability evidence and proposal", "obtain human approval",
                    "deliver under contract", "measure quality, support, invoice and close out",
                ],
                "not_a_claim_of_qualification": True,
            },
            "community_pathway": {
                "status": "partner_review_required",
                "possible_beneficiaries": ["job seekers", "veterans", "people experiencing homelessness", "people receiving public benefits"],
                "safeguards": ["consent", "privacy", "no benefits eligibility promises", "licensed provider referral when required"],
            },
        } for task in tasks]
        output.append(item)
    return {
        "schema": "dreamco.onet_task_curricula.v1",
        "source": {
            "name": "O*NET Database Task Statements", "version": version,
            "official_url": "https://www.onetcenter.org/database.html", "attribution_required": True,
        },
        "inventory": {
            "input_rows": len(rows), "occupations": len(output),
            "task_statements": sum(item["task_count"] for item in output),
            "status": "built_from_supplied_official_export",
            "coverage_warning": "Completeness depends on the version and integrity of the supplied official O*NET export.",
        },
        "occupations": output,
        "truth_boundary": "These curricula are study and practice plans, not occupational certification, licenses, job placement, or proof that Buddy can perform the work safely.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Official O*NET Task Statements export")
    parser.add_argument("--version", required=True, help="O*NET database version, e.g. 31.0")
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()
    rows = read_rows(Path(args.input))
    result = build(rows, args.version)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "onet-task-curricula.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    summary = [
        "# O*NET occupation and task learning paths", "",
        f"- Database version: {args.version}",
        f"- Occupations: {result['inventory']['occupations']}",
        f"- Task statements: {result['inventory']['task_statements']}", "",
        "Each occupation receives a study path and every task receives a practice and supervised commercial/community pathway brief.",
        "Buddy must author and validate the detailed task guide before it can be marked complete.",
        "Reading or summarizing a task does not certify Buddy or a user to perform the work.",
    ]
    (out / "onet-task-curricula.md").write_text("\n".join(summary) + "\n", encoding="utf-8")
    print(json.dumps(result["inventory"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
