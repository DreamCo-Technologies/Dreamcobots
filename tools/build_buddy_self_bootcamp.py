#!/usr/bin/env python3
"""Build Buddy's division-specific curriculum map and self-authoring bootcamp plan.

This creates a verifiable plan and coverage ledger. It does not pretend to have
authored source guides or trained Buddy; those require a connected authoring/model runtime.
"""
from __future__ import annotations
import argparse, json, re
from pathlib import Path
from typing import Any

def division_records(source: str) -> list[dict[str,Any]]:
    pattern = re.compile(r"^  ([A-Za-z][A-Za-z0-9]+): \{\n([\s\S]*?)^  \},?$", re.MULTILINE)
    rows=[]
    for match in pattern.finditer(source):
        name,body=match.group(1),match.group(2)
        if not all(key in body for key in ("purpose:", "focusAreas:", "serves:", "outcome:", "boundary:")):
            continue
        def quoted(key: str) -> str:
            found=re.search(rf'^    {key}: "([^"]*)"',body,re.MULTILINE)
            return found.group(1) if found else ""
        def array(key: str) -> list[str]:
            found=re.search(rf"^    {key}: \[(.*?)\]",body,re.MULTILINE|re.DOTALL)
            return re.findall(r'"([^"]+)"',found.group(1)) if found else []
        rows.append({"division":name,"purpose":quoted("purpose"),"focus_areas":array("focusAreas"),
                     "serves":array("serves"),"outcome":quoted("outcome"),"boundary":quoted("boundary")})
    if len(rows)!=55 or len({x["division"] for x in rows})!=55:
        raise ValueError(f"Expected 55 unique complete domain divisions; found {len(rows)}")
    return rows

def division_names(source: str) -> list[str]:
    return [row["division"] for row in division_records(source)]


def normalize_tokens(value: str) -> set[str]:
    return {token for token in re.findall(r"[a-z0-9]+",value.lower()) if len(token)>2}

ALIASES={"ai":"artificial intelligence","ml":"machine learning","llm":"large language model",
    "web":"web development","ecommerce":"e commerce","crm":"customer relationship management",
    "ux":"user experience","ui":"user interface","devops":"development operations",
    "hr":"human resources","it":"information technology","seo":"search engine optimization"}

FOUNDATION_SUBJECTS=["ai","agents","automation","business","communication","data","ethics","evaluation",
    "finance","information-security","law","marketing","operations","privacy","project-management","research","sales","software-engineering","statistics","writing"]

TOOL_CAPABILITY_FAMILIES={
 "research_and_knowledge":["web research","source verification","citation management","knowledge graphs","RAG","vector search","document parsing","OCR"],
 "software_and_platform_engineering":["Python","JavaScript/TypeScript","Java","C/C++","SQL","Git","GitHub","Docker","Kubernetes","Linux","CI/CD","API design","testing","observability"],
 "ai_and_data":["PyTorch","TensorFlow","scikit-learn","Hugging Face","Jupyter","MLflow","Airflow","dbt","Spark","DuckDB","PostgreSQL","vector databases","model evaluation","fine-tuning","inference optimization"],
 "office_and_business_operations":["spreadsheets","documents","presentations","email","calendar","forms","e-signature","accounting","ERP","inventory","procurement","contract lifecycle"],
 "sales_and_customer_success":["CRM","lead enrichment","sales engagement","CPQ","proposal automation","customer support","ticketing","knowledge base","call analytics"],
 "marketing_and_commerce":["CMS","SEO","analytics","tag management","email marketing","social publishing","ad platforms","e-commerce storefronts","product feeds","affiliate tracking","payments","subscription billing"],
 "design_and_media":["Figma","Canva","Adobe Creative Cloud","video editing","audio editing","3D/CAD","prototyping","accessibility testing","digital asset management"],
 "automation_and_integration":["workflow orchestration","webhooks","OAuth","MCP servers","RPA","iPaaS","message queues","schedulers","secrets vaults","event-driven systems"],
 "security_and_governance":["IAM","SSO","least privilege","vulnerability scanning","SAST/DAST","SIEM","DLP","audit logging","privacy impact assessment","backup and recovery"],
 "delivery_and_management":["Agile","Scrum","Kanban","roadmapping","project portfolio management","SLA/SLO","quality management","risk registers","change management"],
 "field_and_physical_operations":["scheduling","dispatch","routing","work orders","asset maintenance","safety checklists","IoT/SCADA awareness","CAD/BIM","quality inspection"]
}

def map_subjects(record:dict[str,Any],subjects:list[str])->tuple[list[str],list[str]]:
    description=" ".join([record["division"],record.get("purpose",""),record.get("outcome",""),*record.get("focus_areas",[]),*record.get("serves",[])])
    normalized=description.lower()
    for short,long in ALIASES.items():
        normalized=re.sub(rf"\b{short}\b",long,normalized)
    tokens=normalize_tokens(normalized)
    ranked=[]
    for subject in subjects:
        stokens=normalize_tokens(subject.replace("-"," "))
        score=len(tokens & stokens)
        if subject in FOUNDATION_SUBJECTS:
            score=max(score,1)
        if score:
            ranked.append((score,subject))
    ranked.sort(key=lambda item:(-item[0],item[1]))
    matched=[subject for _,subject in ranked]
    selected=sorted(set(FOUNDATION_SUBJECTS).intersection(subjects) | set(matched[:40]))
    return selected,matched

def build(divisions:list[Any], hf:dict[str,Any], onet:dict[str,Any], queue:dict[str,Any], workforce:dict[str,Any], government:dict[str,Any], college:dict[str,Any]|None=None, freecodecamp:dict[str,Any]|None=None)->dict[str,Any]:
    records=divisions
    if records and isinstance(records[0],str):
        records=[{"division":name,"purpose":"","focus_areas":[],"serves":[],"outcome":"","boundary":""} for name in records]
    subjects=sorted(set(hf.get("subject_terms",[])))
    tasks=int(onet.get("inventory",{}).get("task_statements",0))
    occupations=int(onet.get("inventory",{}).get("occupations",0))
    sources=queue.get("counts",{})
    tracks=workforce.get("training_paths",[])
    gov_tracks=government.get("official_sources",[])
    college=college or {}
    freecodecamp=freecodecamp or {}
    college_domains=college.get("knowledge_domains",college.get("domains",[]))
    fcc_certifications=freecodecamp.get("official_platform_inventory",{}).get("core_certifications",[])+freecodecamp.get("official_platform_inventory",{}).get("additional_certifications",[])
    rows=[]
    for record in records:
        name=record["division"]
        relevant,matched=map_subjects(record,subjects)
        division_id=name.lower()
        fcc_paths=[]
        for item in fcc_certifications:
            fcc_text=" ".join([item.get("name",""),*item.get("skills",[]),*item.get("divisions",[])])
            overlap=sorted(record_tokens & normalize_tokens(fcc_text))
            if overlap:
                fcc_paths.append({"id":item.get("id"),"name":item.get("name"),"skills":item.get("skills",[]),"matched_terms":overlap})
        college_matches=[]
        record_text=" ".join([name,record.get("purpose",""),record.get("outcome",""),*record.get("focus_areas",[])])
        record_tokens=normalize_tokens(record_text)
        for domain in college_domains:
            domain_text=" ".join([domain.get("id",""),domain.get("name",""),domain.get("scope",""),*domain.get("tracks",[])])
            overlap=sorted(record_tokens & normalize_tokens(domain_text))
            if overlap:
                college_matches.append({"domain":domain.get("id"),"name":domain.get("name"),"matched_terms":overlap})
        rows.append({
          "division":name,"division_purpose":record.get("purpose"),"focus_areas":record.get("focus_areas",[]),
          "curriculum_status":"planned_not_yet_authored",
          "hugging_face_subject_taxonomy_count":len(subjects),
          "hugging_face_subjects":relevant,"matched_hugging_face_subjects":matched,
          "shared_foundation_subjects":sorted(set(FOUNDATION_SUBJECTS).intersection(subjects)),
          "freecodecamp_learning_paths":{"catalog_status":freecodecamp.get("scope",{}).get("coverage_status","not_loaded"),
            "matched_certifications":fcc_paths,"video_tracks":freecodecamp.get("video_learning_tracks",[]),
            "all_public_video_inventory_required":True,"do_not_claim_all_videos_until_unique_video_id_inventory_verified":True},
          "college_curriculum":{"matched_domains":college_matches,"all_college_domains_available_as_cross_discipline_electives":True},
          "onet_task_mapping":{"source":"O*NET","occupations_in_current_import":occupations,
            "task_statements_in_current_import":tasks,"status":"awaiting_verified_O*NET_import" if not tasks else "inventory_available_task_to_division_mapping_pending",
            "mapping_policy":"match task statement, occupation, work activities, skills, knowledge, abilities and technology to this division purpose/focus; human-review ambiguous matches",
            "must_not_assign_every_occupation_to_every_division":True},
          "autonomous_agent_capability_curriculum":{
            "common_operating_cycle":["discover","intake","research","plan","design","build_or_execute_in_sandbox","verify","deliver_for_approval","monitor","improve"],
            "tool_capability_families":TOOL_CAPABILITY_FAMILIES,
            "task_specific_tool_selection":"Select only tools relevant to the task; record tool/version, cost, required permissions, data handled, alternatives, integration method, test evidence and human approval boundary.",
            "required_operating_skills":["domain knowledge","workflow decomposition","tool selection","API and file handling","structured data","quality assurance","security and privacy","cost/time estimation","documentation","customer communication","failure recovery","escalation"]
          },
          "commercial_and_career_paths":{"shared_tracks":[x.get("id") for x in tracks],
            "government_and_workforce_sources":[x.get("id") for x in gov_tracks],
            "sales_rep_for_relevant_tasks":True,"verified_offer_and_capability_required":True,
            "credential_and_license_gate":True,"human_approval_before_contact_or_bid":True},
          "daily_plan":{"target_lessons":5,"schedule":"daily","only_publish_lessons_with_verified_source_guides":True},
          "weekly_assessment":{"required":True,"assess_each_eligible_source_at_least_weekly":True,
            "must_include_retrieval_practice_project_transfer_and_safety":True,"mastery_requires_practical_evidence":True},
          "guide_requirements":["executive summary","detailed original explanation","prerequisites and learning objectives",
            "source/chapter/section map","concept graph and glossary","software/tool capability map",
            "step-by-step workflows and worked examples","code/configuration examples where appropriate",
            "failure modes, debugging, security, privacy, performance and cost","at least three original exercises",
            "one end-to-end capstone with acceptance tests","knowledge checks and answer key",
            "source citations, revision and license","independent practice evidence and reviewer status"],
          "community_service":{"include_homelessness_veterans_and_benefits_pathways":True,
            "partner_led_and_consent_based":True,"never_promise_benefits_or_awards":True}
        })
    return {
      "schema":"dreamco.buddy_self_authoring_bootcamp.v2",
      "status":"curriculum_map_generated_source_guides_and_model_study_not_yet_executed",
      "coverage":{"domain_divisions":len(rows),"hugging_face_subject_terms":len(subjects),
        "hugging_face_subject_matches":sum(len(x["matched_hugging_face_subjects"]) for x in rows),
        "college_domains_loaded":len(college_domains),"freecodecamp_certifications_loaded":len(fcc_certifications),
        "divisions_with_at_least_one_hugging_face_match":sum(bool(x["matched_hugging_face_subjects"]) for x in rows),
        "onet_occupations":occupations,"onet_task_statements":tasks,
        "source_discovered":sources.get("discovered",0),"source_guide_authoring_eligible":sources.get("guide_authoring_eligible",0),
        "source_rights_pending":sources.get("rights_pending",0)},
      "divisions":rows,
      "buddy_ai_college":{"college_curriculum_source":"config/buddy-college-curriculum.json","college_domains":college_domains,
        "freecodecamp_source":"config/freecodecamp-complete-learning-path.json","freecodecamp_certifications":fcc_certifications,
        "teacher":"ChatGPT teacher/research and curriculum designer; Buddy is the learner and must demonstrate independent competence.",
        "student":"Buddy and its 65 MasterBot capability routes; division mapping is explicit and shared-platform routes remain cross-cutting.",
        "program_design":"stackable learning paths from foundations to specialist, professional practice, advanced systems engineering and capstone levels",
        "competency_levels":["orientation","foundations","practitioner","advanced","professional_simulation","independent_capstone"],
        "teaching_methods":["retrieval practice","worked examples","Socratic questioning","guided labs","deliberate practice","project-based learning","peer/model critique","red-team exercises","spaced repetition","transfer tasks","oral defense"],
        "assessment_methods":["diagnostic pretest","low-stakes quizzes","code or artifact review","sandbox practical","timed scenario","independent capstone","blind rubric grading","delayed retention test","cross-division transfer test"],
        "quality_bar":"benchmark against current reputable open curricula and official vendor documentation; measure topic coverage, depth, recency, practical performance, accessibility, safety, and cost rather than marketing claims",
        "bootcamp_builder_loop":{"trigger":"after each weekly learning cycle and on material source or taxonomy change",
          "steps":["inventory new and changed resources and source revisions","expand uncovered subjects from live Hugging Face tags, repositories and official documentation","verify provenance, license, permissions and security","author detailed original summaries and guides with citations","extract concepts, prerequisites, skills, tools, workflows, risks and practical tasks","map each guide to relevant divisions and specialist capability routes","generate adaptive paths, lessons, labs, projects and capstones","assess Buddy with source-specific and unseen transfer tasks","record evidence, confidence, gaps, remediation and regressions","have Buddy propose the next curriculum version","independent validation and human governance before publishing"]}},
      "truth_boundary":"This is a curriculum architecture and authoring plan. It is not proof that all guides exist, Buddy studied them, model weights changed, or mastery was achieved."
    }


def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--division-source",required=True); p.add_argument("--hf-taxonomy",required=True)
    p.add_argument("--onet",required=True); p.add_argument("--source-queue",required=True)
    p.add_argument("--workforce",required=True); p.add_argument("--government",required=True)
    p.add_argument("--college-curriculum"); p.add_argument("--freecodecamp-path")
    p.add_argument("--out-dir",required=True); a=p.parse_args()
    read=lambda x:json.loads(Path(x).read_text(encoding="utf-8"))
    names=division_records(Path(a.division_source).read_text(encoding="utf-8"))
    result=build(names,read(a.hf_taxonomy),read(a.onet),read(a.source_queue),read(a.workforce),read(a.government),read(a.college_curriculum) if a.college_curriculum else {},read(a.freecodecamp_path) if a.freecodecamp_path else {})
    out=Path(a.out_dir); out.mkdir(parents=True,exist_ok=True)
    (out/"buddy-self-authoring-bootcamp.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    (out/"buddy-division-names.json").write_text(json.dumps(names,indent=2)+"\n",encoding="utf-8")
    lines=["# Buddy self-authoring bootcamp","",f"- Domain divisions: {result['coverage']['domain_divisions']}",f"- Hugging Face task/subject terms: {result['coverage']['hugging_face_subject_terms']}",f"- O*NET occupations in import: {result['coverage']['onet_occupations']}",f"- O*NET task statements: {result['coverage']['onet_task_statements']}",f"- Sources discovered: {result['coverage']['source_discovered']}",f"- Rights-cleared guide candidates: {result['coverage']['source_guide_authoring_eligible']}","", "Buddy must author detailed guides, study them, pass weekly assessments, and propose the next bootcamp version. This plan is not evidence that those actions have run."]
    (out/"buddy-self-authoring-bootcamp.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps(result["coverage"],indent=2))
    return 0
if __name__=="__main__": raise SystemExit(main())
