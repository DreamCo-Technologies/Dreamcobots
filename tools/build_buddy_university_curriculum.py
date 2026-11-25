#!/usr/bin/env python3
"""Build a living cross-disciplinary university curriculum for every DreamCo division.

The output connects Hugging Face task tags, freeCodeCamp tracks, O*NET tasks,
and wider academic/professional domains. It records uncertain mappings instead
of pretending every topic is already covered or approved for model training.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

STOP = {"and", "or", "the", "of", "for", "to", "with", "in", "on", "a", "an", "from", "by", "when", "where", "how", "use", "using", "support", "systems", "system", "work", "operations"}
FCC_DIVISION_CROSSWALK = {
    "computer_science_and_fundamentals": ["DreamCodeLab", "DreamAIInfra", "DreamEducation"],
    "html_css_and_accessibility": ["DreamCodeLab", "DreamArts", "DreamContent"],
    "javascript_and_typescript": ["DreamCodeLab", "DreamAutomation", "DreamAIInfra"],
    "frontend_and_ui_frameworks": ["DreamCodeLab", "DreamArts", "DreamContent"],
    "backend_and_apis": ["DreamCodeLab", "DreamData", "DreamAIInfra", "DreamCyber"],
    "python_and_automation": ["DreamCodeLab", "DreamAutomation", "DreamData", "DreamAIInfra"],
    "java_and_jvm": ["DreamCodeLab", "DreamAutomation", "DreamAIInfra"],
    "c_cpp_and_systems": ["DreamCodeLab", "DreamAIInfra", "DreamRobotics", "DreamProduction"],
    "databases_and_sql": ["DreamData", "DreamCodeLab", "DreamAIInfra"],
    "data_engineering": ["DreamData", "DreamCodeLab", "DreamAIInfra"],
    "data_science_and_visualization": ["DreamData", "DreamScience", "DreamFinance", "DreamDecision"],
    "mathematics_and_statistics": ["DreamScience", "DreamFinance", "DreamData", "DreamDecision"],
    "machine_learning_and_deep_learning": ["DreamAIInfra", "DreamData", "DreamScience", "DreamRobotics"],
    "generative_ai_and_llms": ["DreamAIInfra", "DreamAgents", "DreamContent"],
    "ai_agents_and_mcp": ["DreamAgents", "DreamAIInfra", "DreamAutomation", "CommandCore"],
    "cybersecurity_and_privacy": ["DreamCyber", "DreamAIInfra", "DreamData", "DreamLegal"],
    "linux_networking_and_it": ["DreamAIInfra", "DreamCyber", "DreamAutomation", "DreamOps"],
    "cloud_devops_and_ci_cd": ["DreamAIInfra", "DreamAutomation", "DreamCodeLab", "DreamOps"],
    "mobile_and_cross_platform": ["DreamCodeLab", "DreamContent", "DreamAutomation"],
    "game_development": ["GameTitan", "DreamArts", "DreamCodeLab", "DreamProduction"],
    "career_and_interview_skills": ["DreamEducation", "DreamAdmin", "DreamSalesPro", "DreamProServices"],
    "software_architecture_and_testing": ["DreamCodeLab", "DreamAIInfra", "DreamAutomation", "DreamDecision"],
    "design_ux_and_product": ["DreamArts", "DreamContent", "DreamCodeLab", "DreamCustIntel"],
    "other_or_unclassified": ["DreamEducation", "CommandCore"],
}
ALIASES = {
    "DreamAIInfra": {"ai", "artificial-intelligence", "machine-learning", "deep-learning", "llm", "llms", "model", "models", "inference", "training", "gpu", "transformer", "embedding", "agent", "agents", "multimodal"},
    "DreamAgents": {"agent", "agents", "autonomous", "orchestration", "tool-use", "mcp", "multi-agent"},
    "DreamCodeLab": {"code", "coding", "programming", "software", "developer", "development", "computer-science", "algorithm", "frontend", "backend", "web", "mobile", "api", "testing"},
    "DreamData": {"data", "dataset", "datasets", "database", "sql", "analytics", "statistics", "visualization", "warehouse", "etl", "bi"},
    "DreamCyber": {"cybersecurity", "security", "privacy", "cryptography", "forensics", "penetration-testing", "network"},
    "DreamEducation": {"education", "learning", "teaching", "curriculum", "assessment", "tutoring", "language-learning"},
    "DreamScience": {"science", "scientific", "physics", "chemistry", "biology", "genomics", "astronomy", "mathematics", "research"},
    "DreamHealth": {"health", "healthcare", "medical", "clinical", "mental-health", "nutrition", "public-health", "pharmacy"},
    "DreamFinance": {"finance", "financial", "accounting", "banking", "insurance", "tax", "budget", "credit"},
    "DreamRealEstate": {"real-estate", "property", "housing", "construction", "architecture", "appraisal"},
    "DreamSalesPro": {"sales", "selling", "customer", "crm", "lead", "prospecting", "negotiation", "account-management"},
    "DreamMarket": {"marketing", "advertising", "seo", "brand", "market-research", "growth"},
    "DreamBizLaunch": {"business", "entrepreneurship", "startup", "small-business", "management", "strategy", "pricing"},
    "DreamAffiliate": {"affiliate", "ecommerce", "e-commerce", "marketplace", "subscription", "digital-product"},
    "DreamContent": {"content", "writing", "journalism", "text", "translation", "summarization", "video", "audio", "image"},
    "DreamArts": {"art", "arts", "music", "design", "animation", "photography", "creative", "film"},
    "DreamProduction": {"manufacturing", "production", "industrial", "quality", "supply-chain"},
    "DreamConstruction": {"construction", "carpentry", "hvac", "plumbing", "electrical", "welding", "building"},
    "DreamAgriculture": {"agriculture", "farming", "crop", "livestock", "forestry", "food"},
    "DreamTransport": {"transportation", "logistics", "fleet", "aviation", "automotive", "routing"},
    "DreamPlanetary": {"climate", "earth-science", "geospatial", "weather", "environment", "oceanography", "geology", "space"},
    "DreamLegal": {"law", "legal", "compliance", "regulation", "policy"},
    "DreamAdmin": {"administration", "administrative", "office", "records", "scheduling", "documents"},
    "DreamAutomation": {"automation", "workflow", "integration", "robotics", "rpa"},
    "DreamSocial": {"social", "sociology", "psychology", "community", "nonprofit", "homelessness", "veteran", "benefits"},
    "DreamMilitary": {"military", "veteran", "defense"},
    "DreamFood": {"food", "nutrition", "culinary", "hospitality"},
    "DreamPersonalCare": {"fitness", "strength", "exercise", "wellness", "personal-care", "sports"},
    "DreamTrade": {"trading", "crypto", "cryptocurrency", "investment", "markets"},
    "DreamDecision": {"decision", "forecasting", "planning", "optimization", "risk", "evaluation"},
    "DreamGlobal": {"international", "global", "language", "translation", "geography"},
    "DreamProServices": {"professional-services", "consulting", "freelance", "remote-work", "service-business", "career"},
    "DreamEmpire": {"portfolio", "enterprise", "leadership", "governance", "executive"},
    "DreamSaaS": {"saas", "software-as-a-service", "cloud", "platform", "subscription"},
    "DreamRobotics": {"robotics", "robot", "autonomous-driving", "drones", "embedded-systems"},
}

def tokens(value: str) -> set[str]:
    text = re.sub(r"([a-z])([A-Z])", r"\1 \2", value)
    return {x.lower() for x in re.findall(r"[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*", text) if x.lower() not in STOP and len(x) > 1}

def division_profiles(source: str) -> list[dict[str, Any]]:
    pattern = re.compile(r"^  ([A-Za-z][A-Za-z0-9]+): \{\n([\s\S]*?)^  \},?$", re.MULTILINE)
    rows = []
    for match in pattern.finditer(source):
        name, body = match.group(1), match.group(2)
        def scalar(key: str) -> str:
            found = re.search(rf'^\s*{re.escape(key)}:\s*"((?:[^"\\]|\\.)*)"', body, re.MULTILINE)
            return bytes(found.group(1), "utf-8").decode("unicode_escape") if found else ""
        def array(key: str) -> list[str]:
            found = re.search(rf'^\s*{re.escape(key)}:\s*\[([\s\S]*?)\]', body, re.MULTILINE)
            return re.findall(r'"((?:[^"\\]|\\.)*)"', found.group(1)) if found else []
        row = {"division": name, "purpose": scalar("purpose"), "outcome": scalar("outcome"),
               "boundary": scalar("boundary"), "serves": array("serves"), "focus_areas": array("focusAreas")}
        if all(row[k] for k in ("purpose", "outcome", "boundary")) and row["focus_areas"]:
            rows.append(row)
    if len(rows) != 55 or len({x["division"] for x in rows}) != 55:
        raise ValueError(f"Expected 55 complete canonical domain profiles; found {len(rows)}")
    return rows

def score_subject(term: str, profile: dict[str, Any]) -> int:
    words = tokens(term)
    body = " ".join([profile["division"], profile["purpose"], profile["outcome"], *profile["focus_areas"], *profile["serves"]])
    overlap = words & tokens(body)
    aliases = ALIASES.get(profile["division"], set())
    alias_hits = words & aliases
    return len(overlap) + 3 * len(alias_hits)

def suggest_divisions(term: str, profiles: list[dict[str, Any]], limit: int = 4) -> list[dict[str, Any]]:
    scored = sorted(((score_subject(term, row), row["division"]) for row in profiles), reverse=True)
    positive = [(score, name) for score, name in scored if score > 0]
    if not positive:
        return [{"division": "DreamEducation", "score": 0, "mapping_status": "unclassified_shared_review"},
                {"division": "CommandCore", "score": 0, "mapping_status": "unclassified_shared_review"}]
    return [{"division": name, "score": score, "mapping_status": "suggested_requires_owner_review"}
            for score, name in positive[:limit]]


AGENT_CAPABILITY_CATALOG = {
    "research_and_intelligence": ["source discovery", "web research", "public-record research", "source verification", "citation management", "competitive intelligence", "document extraction", "OCR", "RAG", "knowledge graphs"],
    "software_and_platform_engineering": ["Python", "JavaScript/TypeScript", "Java", "C/C++", "SQL", "Git", "GitHub", "Docker", "Kubernetes", "Linux", "CI/CD", "API design", "testing", "observability"],
    "ai_and_data": ["PyTorch", "TensorFlow", "scikit-learn", "Hugging Face", "Jupyter", "MLflow", "Airflow", "dbt", "Spark", "DuckDB", "PostgreSQL", "vector databases", "model evaluation", "fine-tuning", "inference optimization"],
    "office_and_business_operations": ["spreadsheets", "documents", "presentations", "email", "calendar", "forms", "e-signature", "accounting", "ERP", "inventory", "procurement", "contract lifecycle"],
    "sales_and_customer_success": ["CRM", "lead enrichment", "sales engagement", "CPQ", "proposal automation", "customer support", "ticketing", "knowledge base", "call analytics"],
    "marketing_and_commerce": ["CMS", "SEO", "analytics", "tag management", "email marketing", "social publishing", "ad platforms", "e-commerce storefronts", "product feeds", "affiliate tracking", "payments", "subscription billing"],
    "design_and_media": ["Figma", "Canva", "Adobe Creative Cloud", "video editing", "audio editing", "3D/CAD", "prototyping", "accessibility testing", "digital asset management"],
    "automation_and_integration": ["workflow orchestration", "webhooks", "OAuth", "MCP servers", "RPA", "iPaaS", "message queues", "schedulers", "secrets vaults", "event-driven systems"],
    "security_and_governance": ["IAM", "SSO", "least privilege", "vulnerability scanning", "SAST/DAST", "SIEM", "DLP", "audit logging", "privacy impact assessment", "backup and recovery"],
    "delivery_and_management": ["Agile", "Scrum", "Kanban", "roadmapping", "project portfolio management", "SLA/SLO", "quality management", "risk registers", "change management"],
    "field_and_physical_operations": ["scheduling", "dispatch", "routing", "work orders", "asset maintenance", "safety checklists", "IoT/SCADA awareness", "CAD/BIM", "quality inspection"]
}
def build(profiles: list[dict[str, Any]], hf: dict[str, Any], fcc: dict[str, Any],
          onet: dict[str, Any], taxonomy: dict[str, Any], college: dict[str, Any] | None = None,
          fcc_catalog: dict[str, Any] | None = None) -> dict[str, Any]:
    college = college or {}
    college_domains = college.get("knowledge_domains", college.get("domains", []))
    source_families = college.get("source_families", [])
    academic_structure = college.get("academic_structure", {})
    instructional_model = college.get("instructional_model", {})
    names = {row["division"] for row in profiles}
    hf_terms = sorted(set(taxonomy.get("subject_terms", [])) | set(hf.get("discovery", {}).get("hugging_face_subjects", [])))
    subject_rows = []
    division_hf: dict[str, list[str]] = defaultdict(list)
    for term in hf_terms:
        routes = suggest_divisions(term, profiles)
        subject_rows.append({"subject": term, "routes": routes, "mapping_status": routes[0]["mapping_status"]})
        for route in routes:
            division_hf[route["division"]].append(term)

    fcc_phases = fcc.get("study_sequence", [])
    video_tracks = fcc.get("video_learning_tracks", [])
    platform_inventory = fcc.get("official_platform_inventory", {})
    fcc_rows = []
    division_fcc: dict[str, list[str]] = defaultdict(list)
    all_fcc_tracks = list(fcc.get("specialist_track_details", []))
    for certification in fcc.get("official_platform_inventory", {}).get("core_certifications", []) + fcc.get("official_platform_inventory", {}).get("additional_certifications", []):
        all_fcc_tracks.append({**certification, "id": certification.get("id"), "related_divisions": certification.get("divisions", [])})
    for track in all_fcc_tracks:
        source_related = track.get("related_divisions", [])
        related = []
        for source_division in source_related:
            if source_division in names:
                related.append(source_division)
            related.extend(FCC_DIVISION_CROSSWALK.get(source_division, []))
        related.extend(FCC_DIVISION_CROSSWALK.get(str(track.get("id")), []))
        related = sorted({x for x in related if x in names})
        status = "curated_crosswalk_requires_owner_review" if related else "unclassified_shared_review"
        if not related:
            related = ["DreamEducation", "CommandCore"]
        fcc_rows.append({"track_id": track.get("id"), "name": track.get("name"),
                         "division_ids": related, "mapping_status": status,
                         "learning_outcomes": track.get("learning_outcomes", []),
                         "capstone": track.get("capstone"),
                         "required_before_mastery": track.get("required_before_mastery", [])})
        for division in related:
            division_fcc[division].append(str(track.get("id")))

    fcc_video_rows = []
    division_fcc_videos: dict[str, list[str]] = defaultdict(list)
    for category in video_tracks:
        related = sorted({x for x in FCC_DIVISION_CROSSWALK.get(str(category), []) if x in names})
        status = "curated_crosswalk_requires_owner_review" if related else "unclassified_shared_review"
        if not related:
            related = ["DreamEducation", "CommandCore"]
        fcc_video_rows.append({"category": category, "division_ids": related, "mapping_status": status})
        for division in related:
            division_fcc_videos[division].append(str(category))

    division_college: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for domain in college_domains:
        domain_terms = " ".join([domain.get("id", ""), domain.get("name", ""), domain.get("scope", ""), *domain.get("tracks", [])])
        routes = suggest_divisions(domain_terms, profiles, limit=6)
        for route in routes:
            division_college[route["division"]].append({"domain_id": domain.get("id"), "name": domain.get("name"),
                "mapping_status": route["mapping_status"], "score": route["score"]})

    division_source_families: dict[str, list[str]] = defaultdict(list)
    source_family_routes = []
    for family in source_families:
        family_terms = " ".join([family.get("id", ""), family.get("scope", ""), family.get("source", "")])
        routes = suggest_divisions(family_terms, profiles, limit=6)
        route_names = [row["division"] for row in routes]
        source_family_routes.append({"source_family_id": family.get("id"), "routes": routes})
        for division in route_names:
            division_source_families[division].append(str(family.get("id")))

    division_tasks: dict[str, list[str]] = defaultdict(list)
    division_videos: dict[str, list[str]] = defaultdict(list)
    video_rows = []
    if fcc_catalog is not None:
        if fcc_catalog.get("schema") != "dreamco.freecodecamp_catalog.v1":
            raise ValueError("unsupported freeCodeCamp channel catalog schema")
        for video in fcc_catalog.get("videos", []):
            category_ids = video.get("categories", [])
            routes = sorted({division for category in category_ids for division in FCC_DIVISION_CROSSWALK.get(category, []) if division in names})
            status = "curated_category_crosswalk_requires_owner_review" if routes else "unclassified_shared_review"
            if not routes:
                routes = ["DreamEducation", "CommandCore"]
            video_id = str(video.get("video_id", ""))
            video_rows.append({"video_id": video_id, "title": video.get("title"), "url": video.get("url"),
                               "category_ids": category_ids, "division_ids": routes, "mapping_status": status,
                               "rights_status": video.get("rights_status", "review_required"),
                               "learning_status": video.get("learning_status", "not_studied")})
            for division in routes:
                division_videos[division].append(video_id)
    task_rows = []
    occupations = onet.get("occupations", [])
    for occupation in occupations:
        code = str(occupation.get("occupation_code", ""))
        title = str(occupation.get("occupation_title", ""))
        for task in occupation.get("tasks", []):
            task_id = str(task.get("task_id", ""))
            statement = str(task.get("task", ""))
            routes = suggest_divisions(title + " " + statement, profiles)
            route_names = [x["division"] for x in routes]
            status = "suggested_requires_owner_review"
            if routes[0]["score"] == 0:
                route_names = ["DreamEducation", "DreamProServices", "CommandCore"]
                status = "unclassified_shared_review"
            task_ref = f"{code}:{task_id}"
            playbook = next((x for x in occupation.get("task_playbooks", []) if str(x.get("task_id")) == task_id), {})
            brief = playbook.get("guide_authoring_brief", {})
            task_rows.append({"task_ref": task_ref, "occupation_code": code, "occupation_title": title,
                              "task_id": task_id, "task": statement, "division_ids": route_names,
                              "mapping_status": status, "task_specific_software_categories": brief.get("software_categories_to_assess", []),
                              "agent_capabilities_to_assess": brief.get("agent_capabilities_to_assess", []),
                              "detailed_guide_requirements": brief.get("must_include", []),
                              "commercial_pathway": playbook.get("commercial_pathway", {}),
                              "community_pathway": playbook.get("community_pathway", {})})
            for division in route_names:
                division_tasks[division].append(task_ref)

    divisions = []
    for profile in profiles:
        name = profile["division"]
        divisions.append({
            **profile,
            "curriculum_status": "ready_for_source_guide_assignment_not_proof_of_training",
            "shared_core": ["learning-to-learn-and-source-literacy", "mathematics-and-data-literacy",
                            "digital-and-computing-literacy", "communication-and-documentation",
                            "critical-thinking-and-evidence", "privacy-security-and-safety",
                            "professional-ethics-and-human-oversight", "project-management-and-quality",
                            "AI-literacy-and-agent-collaboration", "research-reproducibility-and-citation"],
            "hugging_face_subjects": sorted(set(division_hf[name])),
            "freecodecamp_tracks": sorted(set(division_fcc[name])),
            "freecodecamp_video_subject_categories": sorted(set(division_fcc_videos[name])),
            "college_domains": sorted(division_college[name], key=lambda x: (-x["score"], x["domain_id"] or "")),
            "source_families": sorted(set(division_source_families[name])),
            "agent_capability_catalog": college.get("agent_capability_matrix", AGENT_CAPABILITY_CATALOG),
            "onet_task_refs": sorted(set(division_tasks[name])),
            "daily_target": {"lessons": 5, "order": ["prerequisites", "new_concept", "worked_example",
                "deliberate_practice", "retrieval_or_capstone"], "only_count_verified_guides_and_recorded_attempts": True},
            "weekly_review": {"assess_each_eligible_source": True, "include_unseen_transfer": True,
                "record_score_and_remediation": True, "mastery_requires_independent_capstone": True},
            "agentic_occupation_playbooks": {"required_sections": 26, "status": "generate_per_occupation_task_and_venture"},
        })

    return {
        "schema": "dreamco.buddy_university_learning_map.v1",
        "status": "generated_crosswalk_suggestions_owner_review_and_source_guides_required",
        "coverage": {
            "domain_divisions": len(divisions), "hugging_face_subject_terms": len(hf_terms),
            "hugging_face_subjects_with_suggested_routes": sum(bool(x["routes"]) for x in subject_rows),
            "freecodecamp_tracks": len(fcc_rows), "freecodecamp_certification_phases": len(fcc_phases),
            "freecodecamp_video_subject_categories": len(video_tracks), "freecodecamp_channel_videos": len(video_rows),
            "freecodecamp_channel_inventory_status": (fcc_catalog or {}).get("inventory_status", "not_supplied"),
            "college_domains": len(college_domains), "source_families": len(source_families), "onet_occupations": len(occupations),
            "onet_task_statements": len(task_rows), "onet_tasks_with_division_routes": sum(bool(x["division_ids"]) for x in task_rows),
            "divisions_with_hf_subjects": sum(bool(x["hugging_face_subjects"]) for x in divisions),
            "divisions_with_freecodecamp_tracks": sum(bool(x["freecodecamp_tracks"]) for x in divisions),
            "divisions_with_freecodecamp_video_categories": sum(bool(x["freecodecamp_video_subject_categories"]) for x in divisions),
            "divisions_with_college_domains": sum(bool(x["college_domains"]) for x in divisions),
            "divisions_with_source_families": sum(bool(x["source_families"]) for x in divisions),
            "divisions_with_onet_tasks": sum(bool(x["onet_task_refs"]) for x in divisions),
        },
        "source_inventory": {
            "hugging_face": {"source": "live Hub model/dataset tags plus configured seeds", "subject_terms": len(hf_terms),
                             "boundary": "not an exhaustive inventory of every Hub repo, model, dataset, Space or discipline"},
            "freecodecamp": {"source": "canonical roadmap and official curriculum inventory", "tracks": len(fcc_rows),
                             "certification_phases": fcc_phases, "video_subject_categories": video_tracks,
                             "official_platform_inventory": platform_inventory,
                             "channel_inventory_status": (fcc_catalog or {}).get("inventory_status", "not_supplied"),
                             "channel_inventory": (fcc_catalog or {}).get("inventory", {}),
                             "boundary": "track roadmap; refresh the official curriculum and channel inventory before claiming every lesson/video is ingested"},
            "onet": {"source": onet.get("source", {}), "occupations": len(occupations), "tasks": len(task_rows),
                     "boundary": onet.get("inventory", {}).get("coverage_warning", "source coverage not independently established")},
        },
        "hugging_face_subject_routes": subject_rows,
        "freecodecamp_track_routes": fcc_rows,
        "freecodecamp_certification_phases": fcc_phases,
        "freecodecamp_video_subject_categories": video_tracks,
        "freecodecamp_video_category_routes": fcc_video_rows,
        "freecodecamp_channel_video_routes": video_rows,
        "academic_structure": academic_structure,
        "instructional_model": instructional_model,
        "college_domain_routes": [{"domain_id":x.get("id"),"name":x.get("name"),"scope":x.get("scope"),"routes":suggest_divisions(" ".join([x.get("id",""),x.get("name",""),x.get("scope",""),*x.get("tracks",[])]),profiles,limit=6)} for x in college_domains],
        "university_curriculum": {"title": college.get("title"), "knowledge_domains": college_domains,
            "shared_core": college.get("shared_core", {}), "academic_structure": academic_structure,
            "instructional_model": instructional_model, "scope_policy": college.get("scope_policy", {})},
        "source_family_routes": source_family_routes,
        "agent_capability_catalog": college.get("agent_capability_matrix", AGENT_CAPABILITY_CATALOG),
        "onet_task_routes": task_rows,
        "divisions": divisions,
        "unclassified_subjects": [x for x in subject_rows if x["mapping_status"] == "unclassified_shared_review"],
        "mapping_policy": {"all_algorithmic_routes_are_suggestions": True, "owner_approval_required_before_domain_specific_promotion": True,
                           "unknown_topics_stay_in_shared_review_queue": True},
        "training_policy": {"five_lessons_per_day_target_per_division": True, "weekly_assessment_per_eligible_source": True,
                            "study_and_retrieval_are_not_weight_training": True, "no_weight_training_without_asset_level_permission": True},
        "truth_boundary": "This artifact maps source inventories and learning routes. It does not prove a source guide exists, Buddy studied it, Buddy changed model weights, or a division achieved mastery."
    }

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--division-source", required=True)
    parser.add_argument("--huggingface-taxonomy", required=True)
    parser.add_argument("--bootcamp-config", required=True)
    parser.add_argument("--freecodecamp-roadmap", required=True)
    parser.add_argument("--onet-curricula", required=True)
    parser.add_argument("--university-curriculum", required=True)
    parser.add_argument("--freecodecamp-catalog")
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()
    read = lambda value: json.loads(Path(value).read_text(encoding="utf-8"))
    profiles = division_profiles(Path(args.division_source).read_text(encoding="utf-8"))
    fcc_catalog = read(args.freecodecamp_catalog) if args.freecodecamp_catalog else None
    result = build(profiles, read(args.huggingface_taxonomy), read(args.freecodecamp_roadmap),
                   read(args.onet_curricula), read(args.bootcamp_config), read(args.university_curriculum), fcc_catalog)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "buddy-university-learning-map.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    lines = ["# DreamCo Buddy University learning map", "",
             f"- Domain divisions: {result['coverage']['domain_divisions']}",
             f"- Hugging Face subject tags: {result['coverage']['hugging_face_subject_terms']}",
             f"- freeCodeCamp specialist tracks: {result['coverage']['freecodecamp_tracks']}",
             f"- freeCodeCamp certification phases: {result['coverage']['freecodecamp_certification_phases']}",
             f"- freeCodeCamp video subject categories: {result['coverage']['freecodecamp_video_subject_categories']}",
             f"- O*NET occupations: {result['coverage']['onet_occupations']}",
             f"- O*NET tasks: {result['coverage']['onet_task_statements']}", "",
             "Mappings are suggestions pending owner review. Source discovery is not guide creation, study, training or mastery."]
    (out / "buddy-university-learning-map.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(result["coverage"], indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
