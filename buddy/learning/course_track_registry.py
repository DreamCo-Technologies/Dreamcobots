"""Registry-backed Buddy course lessons routed through the shared study scheduler.

This module exposes original DreamCo curriculum as queued study resources. It
never downloads course media, ingests transcripts, trains weights, or awards
mastery. Completion is recorded only by the evidence workflow.
"""
from __future__ import annotations

import hashlib
import json
import re
from functools import lru_cache
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Any

from buddy.learning.study_resource_scheduler import Capability, Resource, choose_next, study_plan

ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT / "config/buddy-course-track-registry.json"
DEFAULT_CROSSWALK = ROOT / "config/generated/masterbot-55-domain-crosswalk.json"
DEFAULT_MASTERBOTS = ROOT / "config/masterbot-65-registry.json"


@dataclass(frozen=True)
class CourseLesson:
    resource_id: int
    lesson_id: str
    track_id: str
    title: str
    category: str
    objective: str
    practice: str
    assessment: str
    benchmark: str
    source_url: str
    guide_path: str
    rights_mode: str
    delivery: str
    content_status: str = "authored"
    division_targets: tuple[str, ...] = ()
    masterbot_targets: tuple[str, ...] = ()
    capability_tags: tuple[str, ...] = ()
    tool_tags: tuple[str, ...] = ()
    agent_tags: tuple[str, ...] = ()
    learning_modes: tuple[str, ...] = ()
    implementation_steps: tuple[str, ...] = ()
    buddy_demo: str = ""
    source_video_id: str = ""
    video_categories: tuple[str, ...] = ()
    learner_visible: bool = True
    review_status: str = "approved"
    training_eligibility: str = "internal_sandbox_practice_only"
    exercise_ids: tuple[str, ...] = ()
    project_ids: tuple[str, ...] = ()
    assessment_ids: tuple[str, ...] = ()
    retraining_policy_id: str = ""


def _read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _stable_id(track_id: str, lesson_id: str) -> int:
    digest = hashlib.sha256(f"{track_id}:{lesson_id}".encode("utf-8")).digest()
    return (int.from_bytes(digest[:8], "big") & 0x7FFFFFFFFFFFFFFF) or 1


def _rows(track: dict, data: dict, root: Path = ROOT, *, include_blueprint: bool = False) -> list[dict]:
    parser = track["parser"]
    if parser == "dreamco_division_specialist":
        from buddy.learning.division_curriculum_builder import build_division_curricula
        catalog = build_division_curricula(root)
        return [lesson for course in catalog["artifacts"] for lesson in course["lessons"]]
    if parser == "universal_library_curriculum":
        ecosystem_data = _read(root / "config/library_ecosystems.json")
        rows = []
        registry_urls = {
            "python": "https://pypi.org/",
            "javascript": "https://www.npmjs.com/",
            "java": "https://central.sonatype.com/",
            "dotnet": "https://www.nuget.org/",
            "rust": "https://crates.io/",
            "go": "https://pkg.go.dev/",
            "ruby": "https://rubygems.org/",
            "php": "https://packagist.org/",
            "dart": "https://pub.dev/",
            "swift": "https://swift.org/",
            "objective-c": "https://cocoapods.org/",
            "cpp": "https://conan.io/center",
            "r": "https://cran.r-project.org/",
            "julia": "https://julialang.org/",
            "perl": "https://www.cpan.org/",
            "lua": "https://luarocks.org/",
            "haskell": "https://hackage.haskell.org/",
            "elixir": "https://hex.pm/",
            "nim": "https://nimble.directory/",
            "ocaml": "https://opam.ocaml.org/",
            "racket": "https://pkgs.racket-lang.org/",
            "conda": "https://conda-forge.org/",
            "docker": "https://hub.docker.com/",
            "terraform": "https://registry.terraform.io/",
            "helm": "https://artifacthub.io/",
            "github-actions": "https://github.com/marketplace?type=actions",
            "raku": "https://raku.land/",
            "d": "https://code.dlang.org/",
            "crystal": "https://shardbox.org/",
            "elm": "https://package.elm-lang.org/",
            "clojure": "https://clojars.org/",
            "matlab": "https://www.mathworks.com/matlabcentral/fileexchange/",
            "powershell": "https://www.powershellgallery.com/",
            "solidity": "https://www.npmjs.com/",
            "move": "https://github.com/",
            "embedded": "https://registry.platformio.org/",
            "game-engines": "https://godotengine.org/asset-library/",
            "ml-model-tools": "https://huggingface.co/docs",
        }
        for ecosystem in ecosystem_data.get("ecosystems", []):
            ecosystem_id = str(ecosystem.get("id", "")).strip()
            if not ecosystem_id:
                continue
            rows.append({
                "id": f"ecosystem-discovery-{ecosystem_id}",
                "title": f"{ecosystem_id.replace('-', ' ').title()} library ecosystem discovery",
                "objective": (
                    f"Discover and normalize authoritative libraries, frameworks, SDKs and developer tools "
                    f"for {ecosystem_id}. Languages: {', '.join(ecosystem.get('languages', []))}. "
                    f"Registry targets: {', '.join(ecosystem.get('registries', []))}. "
                    "Candidate discovery is not proof of package verification or guide completeness."
                ),
                "practice": (
                    "Create a bounded, rate-limited registry inventory; deduplicate package identities; "
                    "capture exact versions, source URLs, maintenance metadata and license evidence; "
                    "queue original guide authoring without executing downloaded code."
                ),
                "assessment": (
                    "Verify registry provenance, candidate deduplication, version pinning, item-level rights, "
                    "guide schema, sandbox tests, relevant benchmark, unseen holdout and regression evidence."
                ),
                "benchmark": "Universal library discovery and guide evidence acceptance suite.",
                "source_url": registry_urls.get(ecosystem_id, "https://github.com/"),
            })
        from buddy.learning.universal_library_registry import load_approved_guides
        for approved_guide in load_approved_guides(root):
            guide = approved_guide.document
            library = guide.get("library", {})
            rows.append({
                "id": f"library-guide-{approved_guide.canonical_id}",
                "title": f"Study {approved_guide.name}",
                "objective": "; ".join(guide.get("learning_map", {}).get("objectives", [])),
                "practice": "Complete the guide exercises and original capstone in an isolated sandbox.",
                "assessment": "Pass the guide's targeted benchmark, unseen holdout and regression checks.",
                "benchmark": guide.get("evaluation", {}).get("target_benchmark", "library-specific benchmark"),
                "source_url": library.get("official_homepage", "https://github.com/"),
                "guide_path": approved_guide.path.relative_to(root).as_posix(),
            })
        seed_catalog_path = data.get("seed_catalog", "data/buddy-library-seed-catalog.json")
        seed_catalog_file = root / seed_catalog_path
        if seed_catalog_file.exists():
            seed_catalog = _read(seed_catalog_file)
            for candidate in seed_catalog.get("candidates", []):
                if candidate.get("status") != "seed_candidate_unverified":
                    continue
                candidate_id = str(candidate.get("id", "")).strip()
                candidate_name = str(candidate.get("name", "")).strip()
                if not candidate_id or not candidate_name:
                    continue
                categories = ", ".join(candidate.get("categories", []))
                rows.append({
                    "id": f"candidate-discovery-{candidate_id}",
                    "title": f"Discover and verify {candidate_name}",
                    "objective": (
                        f"Verify the identity and purpose of the {candidate_name} candidate from {categories}. "
                        "Find first-party documentation, determine whether it is a library, framework, SDK, API, "
                        "runtime, platform or concept, pin an exact version, review maintenance and license terms, "
                        "then author an original guide with relevant O*NET, Hugging Face and benchmark crosswalks."
                    ),
                    "practice": (
                        "Use approved metadata-only registry discovery and first-party documentation. "
                        "Do not download package source, execute code, fetch model weights or datasets, "
                        "or infer evaluation/training permission. Create a review-required guide draft."
                    ),
                    "assessment": (
                        "Pass canonical identity, official source, version, API inventory coverage, license/terms, "
                        "security, exercises, relevant O*NET/Hugging Face mapping, task-matched benchmark, holdout "
                        "and regression review. Candidate discovery alone is not mastery."
                    ),
                    "benchmark": "Library candidate provenance and study-guide evidence benchmark.",
                    "source_url": "",  # Internal DreamCo lesson; provenance stays in the seed catalog.
                    "rights_mode": "metadata_discovery_only_no_download_no_execution",
                })
        return rows
    if parser == "benchmark_guides":
        task_registry = _read(root / "config/buddy-benchmark-task-registry.json")
        programs = data.get("programs", [])
        tasks = task_registry.get("tasks", [])
        rows = []
        for program in programs:
            benchmark_id = str(program.get("id", "")).strip()
            title = str(program.get("name", "")).strip()
            if not benchmark_id or not title:
                continue
            rows.append({
                "id": f"program-{benchmark_id}",
                "title": f"Benchmark guide: {title}",
                "objective": (
                    f"Author an original, reproducible guide for benchmark program {title}. "
                    "Document task scope, provenance, workload, baselines, scoring, thresholds, "
                    "reproducibility, holdouts, safety and evidence."
                ),
                "practice": (
                    "Link the canonical generator and check command; define representative and adversarial "
                    "cases, immutable artifacts, exact versions, scoring, failure analysis and remediation. "
                    "Do not invent scores or mark the benchmark measured."
                ),
                "assessment": (
                    "Run the suite in an isolated environment, validate its evidence schema, verify holdout "
                    "separation, and require independent review before claiming capability."
                ),
                "benchmark": "Benchmark guide and evidence acceptance suite.",
                "source_url": "https://github.com/DreamCo-Technologies/Dreamcobots/tree/main/benchmarks",
                "content_status": "authoring_backlog",
            })
        for task in tasks:
            task_name = str(task).strip()
            if not task_name:
                continue
            rows.append({
                "id": f"task-{re.sub(r'[^a-z0-9]+', '-', task_name.lower()).strip('-')}",
                "title": f"Benchmark task guide: {task_name}",
                "objective": f"Author deterministic, adversarial and unseen-transfer benchmark tasks for {task_name}.",
                "practice": (
                    "Define input/output contracts, expected behavior, negative cases, scoring rubric, "
                    "permissions, reproducible fixtures and immutable run evidence."
                ),
                "assessment": (
                    "Verify deterministic execution, contamination-safe holdout, explicit failure rubric, "
                    "safety boundaries and regression evidence before a result can be measured."
                ),
                "benchmark": "Task-specific benchmark guide acceptance suite.",
                "source_url": "https://github.com/DreamCo-Technologies/Dreamcobots/tree/main/benchmarks",
                "content_status": "authoring_backlog",
            })
        return rows
    if parser == "workforce_entrepreneurship":
        rows = []
        for path in data.get("training_paths", []):
            track_id = str(path.get("id", "")).strip()
            track_title = str(path.get("title", "")).strip()
            for index, subject in enumerate(path.get("subjects", []), start=1):
                subject = str(subject).strip()
                if not track_id or not track_title or not subject:
                    continue
                rows.append({
                    "id": f"{track_id}-{index:03d}",
                    "title": f"{track_title}: {subject}",
                    "objective": (
                        f"Author an original, source-grounded task playbook for {subject} "
                        f"within the {track_title} pathway. This catalog record is an authoring "
                        "assignment, not a completed lesson or verified professional guidance."
                    ),
                    "practice": (
                        "Build the full 18-section task playbook: define the task, inputs/outputs, "
                        "workflow, decisions, current tools, APIs, permissions, automation boundaries, "
                        "human approvals, acceptance tests, failure recovery, security, costs, credentials, "
                        "customer/employer value, portfolio artifact and legitimate work/revenue pathway."
                    ),
                    "assessment": (
                        "Require primary-source verification, current eligibility and jurisdiction checks "
                        "where relevant, privacy/permission review, realistic cost analysis, human review, "
                        "and an independent task-specific acceptance test before the playbook is approved."
                    ),
                    "benchmark": "Revenue/workforce task-playbook evidence acceptance suite.",
                    "source_url": track.get("source_url", "https://www.usa.gov/"),
                    "content_status": "authoring_backlog",
                })
        return rows
    if parser == "tolkien":
        return [
            *[{"id": row["id"], "title": row["id"].replace("-", " ").title(),
               "objective": "; ".join(row.get("lessons", [])),
               "practice": row.get("practice", ""),
               "assessment": "Complete the original exercise with citations, item-level rights review and independent assessment."}
              for row in data.get("curriculum", [])],
            *[{"id": row["id"], "title": row["title"], "objective": row["outcome"],
               "practice": row["lab"], "assessment": row["assessment"]}
              for row in data.get("extended_study_path", [])],
        ]
    if parser == "lessons":
        return [
            {"id": row["id"], "title": row["title"], "objective": row["outcome"],
             "practice": row["lab"], "assessment": row["assessment"]}
            for row in data.get("lessons", [])
        ]
    if parser == "modules":
        return [
            {"id": row["id"], "title": row["title"], "objective": row["objective"],
             "practice": row["practice"], "assessment": row["rubric"], "benchmark": row["benchmark"]}
            for row in data.get("modules", [])
        ]
    if parser == "onet":
        rows = []
        for row in data.get("subject_inventory", []):
            name = str(row.get("name", ""))
            normalized_name = name.casefold()
            worker_requirement_tags = (
                ["worker requirements", "education training experience", "licensing entry requirements"]
                if any(term in normalized_name for term in ("education", "training and experience", "licensing", "entry requirements"))
                else []
            )
            rows.append({
                "id": row["id"],
                "title": name,
                "objective": f"Understand the O*NET subject {name} and apply its occupational evidence without inferring qualification or authority.",
                "practice": "Build an original subject guide, connect relevant tasks and tools, and classify AI/human responsibilities.",
                "assessment": "Pass a source-grounded subject assessment and task-specific suitability review.",
                "content_status": "authoring_backlog",
                "capability_tags": worker_requirement_tags,
            })
        task_index_path = track.get("task_index_path")
        task_index_file = root / task_index_path if task_index_path else None
        if task_index_file and task_index_file.is_file():
            task_index = _read(task_index_file)
            # Do not route unverified or release-drifted task rows as authoritative lessons.
            if task_index.get("inventory", {}).get("complete") is True:
                source_url = task_index.get("source", {}).get("official_download_url") or track["source_url"]
                for task in task_index.get("tasks", []):
                    occupation_code = str(task.get("occupation_code", "")).strip()
                    task_id = str(task.get("task_id", "")).strip()
                    statement = str(task.get("task_statement", "")).strip()
                    if not occupation_code or not task_id or not statement:
                        continue
                    occupation = str(task.get("occupation_title", "")).strip() or occupation_code
                    rows.append({
                        "id": f"onet-task-{occupation_code}-{task_id}",
                        "title": f"{occupation}: {statement}",
                        "objective": (
                            f"Understand and safely perform the O*NET task '{statement}' for {occupation} "
                            f"using release {task.get('onet_release', 'unverified')}; distinguish assistive, "
                            "bounded automation, human-supervised and physical work."
                        ),
                        "practice": (
                            "Create an original step-by-step workflow, identify prerequisites and tools, "
                            "simulate the task in a safe environment, document failure recovery and define "
                            "human approval points. Research current commercial, open-source and local tools."
                        ),
                        "assessment": (
                            "Complete a task-specific practical assessment, safety and credential-boundary "
                            "review, unseen assessment on an independent task, benchmark and reviewer sign-off; reading the "
                            "task statement alone is not evidence of competence."
                        ),
                        "benchmark": "O*NET task-specific workflow, safety, tool-use and unseen-transfer benchmark.",
                        "source_url": source_url,
                        "guide_path": track["guide"],
                        "content_status": "authoring_backlog",
                        "rights_mode": track["rights"],
                    })
        return rows
    if parser == "huggingface":
        return [
            {"id": row["id"], "title": row["id"].replace("-", " ").title(),
             "objective": row.get("description", ""),
             "practice": f"Build a small original sandbox exercise for the {row.get('family', 'unclassified')} task family; inspect model and dataset cards before use.",
             "assessment": "Complete a task-specific benchmark, rights review and independent holdout."}
            for row in data.get("task_families", [])
        ]
    if parser == "freecodecamp_video_catalog":
        inventory = data.get("inventory") or {}
        videos = data.get("videos") or []
        if int(data.get("video_count", -1)) != len(videos):
            raise ValueError("freeCodeCamp video catalog count does not match its video rows")
        if int(inventory.get("observed_entry_count", -1)) != len(videos):
            raise ValueError("freeCodeCamp observed inventory count does not match video rows")
        routing_path = root / "config/freecodecamp-division-routing-overrides.json"
        routing = _read(routing_path) if routing_path.is_file() else {}
        if routing.get("schema") not in {None, "dreamco.freecodecamp_specialist_learning_overrides.v1"}:
            raise ValueError("unsupported freeCodeCamp specialist routing override schema")
        overrides = {str(item.get("video_id")): item for item in routing.get("entries", [])}
        rules = routing.get("routing_rules", [])
        rows = []
        for row in videos:
            searchable = f"{row.get('title', '')} {row.get('description', '')}".casefold()
            row_categories = {str(value).casefold() for value in row.get("categories", [])}
            matched_rules = [
                candidate for candidate in rules
                if (
                    any(str(term).casefold() in searchable for term in candidate.get("match_title_terms", []))
                    or bool(row_categories.intersection(str(value).casefold() for value in candidate.get("match_categories", [])))
                )
            ]
            overlay: dict[str, Any] = {}
            for candidate in matched_rules:
                for key, value in candidate.items():
                    if key in {"division_targets", "masterbot_targets", "capability_tags", "tool_tags", "agent_tags"}:
                        overlay[key] = list(dict.fromkeys([*overlay.get(key, []), *value]))
                    elif key not in {"match_title_terms", "match_categories"}:
                        overlay[key] = value
            overlay.update(overrides.get(str(row.get("video_id")), {}))
            if row_categories == {"other_or_unclassified"} and not overlay.get("division_targets"):
                overlay["division_targets"] = ["DreamEducation", "CommandCore"]
                overlay["masterbot_targets"] = ["DreamEducation", "CommandCore", "DreamDiscovery"]
                overlay["capability_tags"] = ["source-classification", "course-taxonomy", "rights-review"]
                overlay["tool_tags"] = ["video-metadata-catalog", "course-taxonomy", "review-queue"]
                overlay["agent_tags"] = ["course-curator", "rights-reviewer", "division-router"]
            rows.append({
                "id": f"fcc-video-{row['video_id']}",
                "title": row["title"],
                "objective": (overlay.get("objective") if include_blueprint else None) or row.get("description") or "Metadata-only reference; a title and public video URL are not course content.",
                "practice": (overlay.get("practice") if include_blueprint else None) or "Verify item-level study, summary and evaluation permissions before authoring a lesson.",
                "assessment": (overlay.get("assessment") if include_blueprint else None) or "Do not mark studied or mastered from public metadata; require an authorized source and independent assessment.",
                "benchmark": (overlay.get("benchmark") if include_blueprint else None) or "FreeCodeCamp metadata inventory integrity checks; no study or mastery claim.",
                "source_url": row["url"],
                "source_video_id": str(row["video_id"]),
                "video_categories": sorted(row_categories),
                "content_status": "metadata_only",
                "division_targets": overlay.get("division_targets", []),
                "masterbot_targets": overlay.get("masterbot_targets", []),
                "capability_tags": overlay.get("capability_tags", []),
                "tool_tags": overlay.get("tool_tags", []),
                "agent_tags": overlay.get("agent_tags", []),
                "implementation_steps": overlay.get("implementation_steps", []) if include_blueprint else [],
                "buddy_demo": overlay.get("buddy_demo", "") if include_blueprint else "",
                "rights_mode": "metadata_only_until_item_level_permissions",
            })
        return rows
    if parser == "freecodecamp_specialist_learning_paths":
        metadata_rows = _rows({"parser": "freecodecamp_video_catalog"}, data, root, include_blueprint=True)
        overrides = _read(root / "config/freecodecamp-division-routing-overrides.json")
        curated_ids = {str(item.get("video_id")) for item in overrides.get("entries", [])}
        rows = []
        for row in metadata_rows:
            # Unclassified records belong to the dedicated rights/classification triage lane.
            if "source-classification" in row.get("capability_tags", []):
                continue
            implementation_steps = list(row.get("implementation_steps") or [])
            buddy_demo = str(row.get("buddy_demo") or "")
            curated = str(row.get("source_video_id")) in curated_ids
            if not curated:
                implementation_steps = [
                    "Verify the source-video ID, public URL, title, channel, category tags, and catalog provenance.",
                    "Confirm separate item-level permission for study, transcript use, derivative summaries, and evaluation; block unknown rights.",
                    "Obtain an authorized transcript or equivalent source. If none is available, retain metadata-only status and do not infer lesson content.",
                    "Write an original chapter-by-chapter explanation, learning objectives, prerequisites, glossary, and verified examples from the authorized source.",
                    "Create at least three original exercises, a practical project, test plan, and independent knowledge assessment.",
                    "Map the verified concepts to the canonical division and MasterBot targets; record uncertainty and request human review.",
                    "Run sandbox exercises, task-matched benchmarks, unseen holdout, and regression checks before study-ready status.",
                    "Record source hashes, rights evidence, reviewer approval, and the exact guide revision before enabling study."
                ]
                buddy_demo = (
                    "Buddy demonstrates the rights-gated authoring workflow: verify the source, separate known metadata from unknown lesson content, "
                    "draft an original guide only from authorized material, create exercises and assessments, and request review without claiming "
                    "to have watched or learned the video."
                )
                row["objective"] = (
                    "Create a complete original DreamCo study guide for this specialist-routed source after item-level study, derivative-summary, "
                    "and evaluation permissions are verified. Public metadata alone is not lesson content."
                )
                row["practice"] = (
                    "Follow the rights-gated authoring steps, build original examples and projects from the authorized source, and keep the item "
                    "in the authoring backlog until a reviewer approves the guide."
                )
                row["assessment"] = (
                    "Require source and rights provenance, chapter-level coverage, original exercises, project tests, independent holdout, "
                    "regression evidence, and human review; never award mastery from metadata."
                )
                row["benchmark"] = "Original specialist study-guide acceptance, rights, holdout, and regression suite."
            rows.append({
                **row,
                "id": f"fcc-specialist-path-{row['source_video_id']}",
                "title": (
                    f"DreamCo implementation path: {row['title']}" if curated
                    else f"DreamCo original guide authoring task: {row['title']}"
                ),
                "content_status": "original_implementation_brief" if curated else "authoring_backlog",
                "rights_mode": (
                    "original_dreamco_learning_path_video_metadata_reference_only" if curated
                    else "metadata_only_until_item_level_permissions"
                ),
                "implementation_steps": implementation_steps,
                "buddy_demo": buddy_demo,
                "learning_modes": list(row.get("learning_modes") or [
                    "plain_language_explanation", "visual_concept_map", "worked_example",
                    "interactive_sandbox", "guided_pair_programming", "flashcards",
                    "retrieval_quiz", "spaced_repetition", "voice_walkthrough",
                    "code_review", "scenario_simulation", "portfolio_capstone",
                    "guided_authoring", "independent_assessment", "human_review"
                ]),
            })
        return rows
    if parser == "freecodecamp_metadata_triage":
        metadata_rows = _rows({"parser": "freecodecamp_video_catalog"}, data, root)
        source_by_id = {
            str(video["video_id"]): video for video in data.get("videos", [])
        }
        routing = _read(root / "config/freecodecamp-division-routing-overrides.json")
        explicit_ids = {str(item.get("video_id")) for item in routing.get("entries", [])}
        rules = routing.get("routing_rules", [])
        rows = []
        for row in metadata_rows:
            source = source_by_id.get(row["source_video_id"], {})
            categories = {str(value).casefold() for value in source.get("categories", [])}
            searchable = f"{source.get('title', '')} {source.get('description', '')}".casefold()
            has_specialist_route = row["source_video_id"] in explicit_ids or any(
                any(str(term).casefold() in searchable for term in rule.get("match_title_terms", []))
                or bool(categories.intersection(str(value).casefold() for value in rule.get("match_categories", [])))
                for rule in rules
            )
            if categories != {"other_or_unclassified"} or has_specialist_route:
                continue
            rows.append({
                **row,
                "id": f"fcc-metadata-triage-{row['source_video_id']}",
                "title": f"FreeCodeCamp classification review: {row['title']}",
                "objective": "Classify this source safely from public metadata and route it for human review; do not infer lesson content from the title or URL.",
                "practice": "Inspect the public title, channel, description, date, and category labels. Seek authorized source material before writing any lesson or summary.",
                "assessment": "The item remains metadata-only until its subject, canonical division, source rights, and an original guide are independently reviewed.",
                "benchmark": "Every unclassified record has an explicit triage owner, a provenance trail, and a reviewed routing decision or remains unclassified.",
                "content_status": "metadata_only",
                "rights_mode": "metadata_only_until_item_level_permissions",
                "division_targets": ["DreamEducation", "CommandCore"],
                "masterbot_targets": ["DreamEducation", "CommandCore", "DreamDiscovery"],
                "capability_tags": ["source-classification", "course-taxonomy", "rights-review", "division-routing"],
                "tool_tags": ["video-metadata-catalog", "course-taxonomy", "review-queue"],
                "learning_modes": ["metadata_review", "guided_classification", "rights_check", "human_review"],
                "agent_tags": ["course-curator", "rights-reviewer", "division-router"],
                "implementation_steps": [
                    "Confirm the source-video ID, public URL, channel, title, description, and catalog provenance.",
                    "Review available category labels and identify what is known versus unknown from metadata alone.",
                    "Search for an authorized transcript, official documentation, or permissioned source before making content claims.",
                    "Draft candidate subject tags and division/MasterBot owners with confidence and supporting evidence.",
                    "Check the proposed owners against the canonical 55-domain crosswalk and 65-MasterBot registry.",
                    "Request human approval for the classification and any proposed specialist route.",
                    "If authorized learning material exists, create a separate original DreamCo guide with exercises and assessments.",
                    "Keep the record metadata-only until rights, guide quality, and routing approval are recorded."
                ],
                "buddy_demo": "Buddy demonstrates metadata triage, separates known facts from assumptions, proposes a canonical owner, checks source rights, and requests human approval without claiming to teach the video."
            })
        return rows
    if parser == "huggingface_learning_map":
        courses = [
            {"id": row["id"], "title": row["title"], "objective": row["topics"],
             "practice": "Complete the official course activities where available and create an original DreamCo transfer project.",
             "assessment": row["assessment"], "benchmark": "Course-specific independent benchmark."}
            for row in data.get("official_courses", [])
        ]
        modules = [
            {"id": row["id"], "title": row["title"], "objective": row["objective"],
             "practice": row["practice"], "assessment": row["assessment"], "benchmark": row["benchmark"]}
            for row in data.get("ecosystem_modules", [])
        ]
        return courses + modules
    if parser == "freecodecamp":
        inventory = data.get("official_platform_inventory", {})
        certs = [
            {"id": row["id"], "title": row["name"],
             "objective": "; ".join(row.get("skills", [])) or f"Complete the {row['name']} learning path.",
             "practice": "Complete original exercises and projects aligned to the official learning outcomes.",
             "assessment": "Complete official requirements where authorized plus an independent DreamCo transfer task."}
            for row in inventory.get("core_certifications", [])
        ]
        additional = [
            {"id": row["id"], "title": row["name"],
             "objective": f"Study the {row.get('level', 'specialist')} {row.get('language', 'technology')} learning path.",
             "practice": "Complete original language or specialist exercises and a practical artifact.",
             "assessment": "Complete an independent language or technology assessment and reviewer rubric."}
            for row in inventory.get("additional_certifications", [])
        ]
        primitives = [
            {"id": f"fcc-primitive-{name}", "title": name.replace("_", " ").title(),
             "objective": f"Understand the freeCodeCamp {name.replace('_', ' ')} learning primitive and its place in a complete course.",
             "practice": "Build an original example of this learning format and map it to a measurable outcome.",
             "assessment": "Verify the format has objectives, practice, feedback and a completion criterion."}
            for name in inventory.get("curriculum_primitives", [])
        ]
        legacy = [{
            "id": "fcc-legacy-curriculum-inventory",
            "title": "Legacy freeCodeCamp curriculum inventory",
            "objective": str(inventory.get("legacy_certifications", "Discover and retain versioned legacy curricula.")),
            "practice": "Catalog legacy certifications by version and preserve historical requirements separately from current v9 pathways.",
            "assessment": "Verify each legacy source has a version, source link and non-substitution note.",
        }]
        phases = [
            {"id": row["id"], "title": row["id"].replace("-", " ").title(),
             "objective": "; ".join(row.get("focus", [])),
             "practice": "Complete original practical exercises and a capstone.",
             "assessment": "; ".join(row.get("exit_evidence", []))}
            for row in data.get("study_sequence", [])
        ]
        videos = [
            {"id": f"video-track-{name}", "title": name.replace("_", " ").title(),
             "objective": f"Build a complete original study path for the {name.replace('_', ' ')} video subject area.",
             "practice": "Refresh official video metadata; create a detailed guide only when authorized transcript or equivalent source evidence is available.",
             "assessment": "Verify unique video inventory, rights state, detailed guide coverage, practice and independent assessment."}
            for name in data.get("video_learning_tracks", [])
        ]
        return certs + additional + primitives + legacy + phases + videos
    raise ValueError(f"unsupported course track parser: {parser}")


@lru_cache(maxsize=4)
def load_course_lessons(root: Path = ROOT) -> list[CourseLesson]:
    registry = _read(root / "config/buddy-course-track-registry.json")
    if registry.get("schema") != "dreamco.buddy_course_track_registry.v1":
        raise ValueError("unsupported Buddy course-track registry schema")
    crosswalk = _read(root / "config/generated/masterbot-55-domain-crosswalk.json")
    masterbots = _read(root / "config/masterbot-65-registry.json")
    if len(crosswalk.get("domains", [])) != 55 or len(masterbots.get("divisions", [])) != 65:
        raise ValueError("course-track routing requires the canonical 55-domain and 65-MasterBot registries")
    allowed_domains = {str(row.get("domain_name")) for row in crosswalk.get("domains", [])}
    allowed_masterbots = {str(row.get("name")) for row in masterbots.get("divisions", [])}
    lessons: list[CourseLesson] = []
    seen: set[str] = set()
    resource_ids: set[int] = set()
    for track in registry.get("tracks", []):
        data = _read(root / track["source"])
        for row in _rows(track, data, root):
            lesson_id = str(row.get("id", "")).strip()
            title = str(row.get("title", "")).strip()
            if not lesson_id or not title:
                raise ValueError(f"track {track['id']} contains a lesson without a stable ID/title")
            key = f"{track['id']}:{lesson_id}"
            if key in seen:
                raise ValueError(f"duplicate course lesson ID: {key}")
            seen.add(key)
            rid = _stable_id(track["id"], lesson_id)
            if rid in resource_ids:
                raise ValueError("stable course resource ID collision")
            resource_ids.add(rid)
            division_targets = tuple(str(value) for value in row.get("division_targets", []))
            masterbot_targets = tuple(str(value) for value in row.get("masterbot_targets", []))
            if not set(division_targets).issubset(allowed_domains):
                raise ValueError(f"course {key} references unknown canonical divisions: {sorted(set(division_targets) - allowed_domains)}")
            if not set(masterbot_targets).issubset(allowed_masterbots):
                raise ValueError(f"course {key} references unknown MasterBot lanes: {sorted(set(masterbot_targets) - allowed_masterbots)}")
            lessons.append(CourseLesson(
                resource_id=rid,
                lesson_id=lesson_id,
                track_id=track["id"],
                title=title,
                category=str(row.get("category") or track["category"]),
                objective=str(row.get("objective", "")).strip(),
                practice=str(row.get("practice", "")).strip(),
                assessment=str(row.get("assessment", "")).strip(),
                benchmark=str(row.get("benchmark", "independent task and regression suite")).strip(),
                source_url=str(row.get("source_url") or track["source_url"]),
                guide_path=str(row.get("guide_path") or track["guide"]),
                rights_mode=str(row.get("rights_mode") or track["rights"]),
                delivery=track["delivery"],
                content_status=str(row.get("content_status", "authored")),
                division_targets=division_targets,
                masterbot_targets=masterbot_targets,
                capability_tags=tuple(str(value) for value in row.get("capability_tags", [])),
                tool_tags=tuple(str(value) for value in row.get("tool_tags", [])),
                agent_tags=tuple(str(value) for value in row.get("agent_tags", [])),
                learning_modes=tuple(str(value) for value in row.get("learning_modes", [])),
                implementation_steps=tuple(str(value) for value in row.get("implementation_steps", [])),
                buddy_demo=str(row.get("buddy_demo", "")),
                source_video_id=str(row.get("source_video_id", "")),
                video_categories=tuple(str(value) for value in row.get("video_categories", [])),
                learner_visible=bool(row.get("learner_visible", track.get("learner_visible", not bool(row.get("source_url") or track.get("source_url"))))),
                review_status=str(row.get("review_status", "approved")),
                training_eligibility=str(row.get("training_eligibility", "internal_sandbox_practice_only")),
                exercise_ids=tuple(str(value) for value in row.get("exercise_ids", [])),
                project_ids=tuple(str(value) for value in row.get("project_ids", [])),
                assessment_ids=tuple(str(value) for value in row.get("assessment_ids", [])),
                retraining_policy_id=str(row.get("retraining_policy_id", "")),
            ))
    return lessons


@lru_cache(maxsize=128)
def resources_for_division(division: str, root: Path = ROOT) -> list[Resource]:
    crosswalk = _read(root / "config/generated/masterbot-55-domain-crosswalk.json")
    names = {row.get("domain_name") for row in crosswalk.get("domains", [])}
    if division not in names:
        raise ValueError(f"unknown canonical division: {division}")
    return [
        Resource(id=lesson.resource_id, name=lesson.title, category=lesson.category, url=lesson.source_url,
                 methods=("review_original_dreamco_lesson", "practice_in_sandbox", "complete_exercises",
                          "complete_project", "complete_assessment", "run_independent_benchmark",
                          "record_evidence", "trigger_targeted_retraining"))
        for lesson in load_course_lessons(root)
        if lesson.content_status == "authored"
        and lesson.learner_visible
        and not lesson.source_url
        and (not lesson.division_targets or division in lesson.division_targets)
    ]


@lru_cache(maxsize=128)
def resources_for_masterbot(masterbot: str, root: Path = ROOT) -> list[Resource]:
    registry = _read(root / "config/masterbot-65-registry.json")
    names = {row.get("name") for row in registry.get("divisions", [])}
    if masterbot not in names:
        raise ValueError(f"unknown MasterBot lane: {masterbot}")
    return [
        Resource(id=lesson.resource_id, name=lesson.title, category=lesson.category, url=lesson.source_url,
                 methods=("study_original_dreamco_guide", "practice_in_sandbox", "complete_assessment",
                          "run_independent_benchmark", "record_evidence"))
        for lesson in load_course_lessons(root)
        if lesson.content_status == "authored"
        and lesson.learner_visible
        and not lesson.source_url
        and (not lesson.masterbot_targets or masterbot in lesson.masterbot_targets)
    ]


def plan_next_for_division(
    division: str,
    gaps: Iterable[Capability],
    root: Path = ROOT,
    *,
    recent: set[int] | None = None,
) -> dict | None:
    resources = resources_for_division(division, root)
    gap_list = list(gaps)
    chosen = choose_next(resources, gap_list, recent=recent)
    if chosen is None:
        return None
    lesson = next(row for row in load_course_lessons(root) if row.resource_id == chosen.id)
    capability = next((gap for gap in gap_list if gap.category.lower() == lesson.category.lower()), gap_list[0] if gap_list else Capability(name=division, category=lesson.category))
    plan = study_plan(chosen, capability)
    plan.update({
        "division": division,
        "track_id": lesson.track_id,
        "lesson_id": lesson.lesson_id,
        "objective": lesson.objective,
        "practice": lesson.practice,
        "assessment": lesson.assessment,
        "benchmark": lesson.benchmark,
        "guide_path": lesson.guide_path,
        "rights_mode": lesson.rights_mode,
        "division_targets": list(lesson.division_targets),
        "masterbot_targets": list(lesson.masterbot_targets),
        "capability_tags": list(lesson.capability_tags),
        "tool_tags": list(lesson.tool_tags),
        "agent_tags": list(lesson.agent_tags),
        "learning_modes": list(lesson.learning_modes),
        "implementation_steps": list(lesson.implementation_steps),
        "buddy_demo": lesson.buddy_demo,
        "source_video_id": lesson.source_video_id,
        "review_status": lesson.review_status,
        "training_eligibility": lesson.training_eligibility,
        "exercise_ids": list(lesson.exercise_ids),
        "project_ids": list(lesson.project_ids),
        "assessment_ids": list(lesson.assessment_ids),
        "retraining_policy_id": lesson.retraining_policy_id,
        "completion_status": "queued_for_owner_review" if lesson.review_status != "approved" else "queued_not_studied",
        "mastery_awarded": False,
        "model_weight_training_authorized": False,
        "paid_compute_authorized": False,
    })
    return plan
