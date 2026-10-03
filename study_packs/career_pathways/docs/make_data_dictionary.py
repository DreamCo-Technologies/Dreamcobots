"""Writes docs/data_dictionary.json and docs/DATA_DICTIONARY.md (field-level documentation of every output file).
Edit the descriptions here; tests/test_build.py::test_data_dictionary_covers_every_output_field checks the result against
the actual outputs (every field present on disk is documented; documented fields exist unless marked Optional)."""
import json, pathlib

HERE = pathlib.Path(__file__).resolve().parent

MAJOR = {  # shared by data/majors_selected.json[] and plan.json
    "asset_id": "Stable asset id, edu-<initials>-<CIP code>; also the gate candidate_id.",
    "cip": "CIP 2020 program code (NN.NNNN), from the O*NET Education CIP-to-O*NET-SOC crosswalk.",
    "title": "CIP 2020 program title (crosswalk data, CC BY 4.0).",
    "tier": "authored (27 majors with DreamCo-original outline topics and practice tasks) or generated (template output, not individually reviewed).",
    "occupations": "All O*NET-SOC occupations linked to this CIP code in the crosswalk.",
    "occupations[].soc": "O*NET-SOC 2019 code (NN-NNNN.NN).",
    "occupations[].title": "O*NET occupation title (O*NET 31.0, CC BY 4.0).",
    "occupations[].job_zone": "O*NET Job Zone 1-5 (integer), or null if O*NET has no Job Zone rating.",
    "top_knowledge": "Unweighted comparison list: top 8 O*NET knowledge elements as [element name, mean importance 1-5 (Scale IM), 2 decimals] over all linked occupations. Kept for comparison; the outline does not use it.",
    "top_skills": "Unweighted comparison list: top 6 O*NET 31.0 Essential Skills as [element name, mean importance] over all linked occupations.",
    "top_knowledge_entry_weighted": "Top 8 knowledge elements as [element name, entry-weighted mean importance] using knowledge_weighting.weights. The outline is built from this list.",
    "top_skills_entry_weighted": "Top 6 Essential Skills as [element name, entry-weighted mean importance] using knowledge_weighting.weights.",
    "knowledge_weighting": "How the entry-weighted lists were computed.",
    "knowledge_weighting.method": "Plain-language rule (build.WEIGHTING_METHOD): targets weight 2; other Job Zone 4/5 (or target-zone) occupations weight 1; managerial, faculty, All Other and other-zone occupations weight 0.",
    "knowledge_weighting.weights": "Map of O*NET-SOC code to weight (1 or 2). Occupations with weight 0 are omitted.",
    "knowledge_weighting.weights.<key>": "Weight of one occupation (key = O*NET-SOC code): 2 = entry target, 1 = other role-appropriate linked occupation.",
    "knowledge_weighting.note": "States that top_knowledge/top_skills are the unweighted comparison lists.",
    "entry_targets": "1-3 entry-level target occupations shown in Year 4 and used as weight-2 occupations.",
    "entry_targets[].soc": "O*NET-SOC code of the target.",
    "entry_targets[].title": "O*NET occupation title of the target.",
    "entry_targets[].job_zone": "Job Zone of the target (integer or null).",
    "entry_target_basis": "Text explaining which rule picked the targets (e.g. Job Zone 4 non-managerial links in crosswalk order, or a fallback).",
    "entry_target_review": "Review status of the targets.",
    "entry_target_review.type": "override (authored/target_overrides.json changed the rule output), reviewed_without_change, or rule_only_not_reviewed (generated tier).",
    "entry_target_review.reason": "Optional: why the override was made (type override).",
    "entry_target_review.rule_output": "Optional: O*NET-SOC codes the rule would have picked (type override).",
    "entry_target_review.targets": "Optional: O*NET-SOC codes after the override (type override).",
    "entry_target_review.note": "Optional: reviewer note (reviewed_without_change) or the rule-only caveat (rule_only_not_reviewed).",
    "outline_elements": "Which knowledge and skill elements the 4-year outline places in which year, and which it skips.",
    "outline_elements.rule": "Plain-language placement rule (English Language to Year 1 general education; cross-cutting elements skipped unless kept; Year 2 = first 3 core elements; Year 3 = next core elements by target importance).",
    "outline_elements.year1_knowledge": "Knowledge element names placed in Year 1.",
    "outline_elements.year1_skills": "Essential Skills placed in Year 1 (first 3 of the weighted skills list).",
    "outline_elements.year2_knowledge": "Knowledge element names placed in Year 2.",
    "outline_elements.year3_knowledge": "Knowledge element names placed in Year 3.",
    "outline_elements.year3_knowledge_added_from_targets": "Knowledge elements added to Year 3 from the entry targets' own ratings (importance >= 2.5) because fewer than 2 core elements remained.",
    "outline_elements.year3_skills": "Essential Skills placed in Year 3 (skills 4-6 of the weighted list).",
    "outline_elements.skipped_knowledge": "Top weighted knowledge elements the outline deliberately does not cover.",
    "outline_elements.skipped_knowledge[].element": "O*NET knowledge element name.",
    "outline_elements.skipped_knowledge[].reason": "Why it is skipped (cross-cutting general-workplace knowledge such as Customer and Personal Service, Administration and Management, Education and Training, or no room in the outline). The plan text shows the same reason.",
    "practice_task_ids": "practice_id values of this major's practice tasks (see data/practice_tasks.json).",
    "quality_flags": "Automatic plausibility checks. Generated tier: actionable flags, automatic actions and notes; authored tier: informational only (flags is empty).",
    "quality_flags.method": "The rules used.",
    "quality_flags.method.supervisory_tasks": "Supervisory/managerial pattern rule (build.SUPERVISORY_RULE).",
    "quality_flags.method.field_fit": "Optional: generated tier: field-fit rule (build.FIELD_FIT_RULE), see target_plausibility.",
    "quality_flags.method.topical_overlap": "Optional: authored tier: the earlier title-overlap heuristic, kept for reference (retired for the generated tier in v5).",
    "quality_flags.flag_count": "Number of entries in flags.",
    "quality_flags.flags": "Actionable flags needing a human decision; empty if none.",
    "quality_flags.flags[].flag": "better_field_match_available (a kept .00 target has field fit 0 and a linked alternative fits >= build.FIT_FLAG_MIN_BEST) or supervisory_task_kept.",
    "quality_flags.flags[].onet_soc_code": "better_field_match_available: the kept entry target.",
    "quality_flags.flags[].occupation_title": "better_field_match_available: title of the kept entry target.",
    "quality_flags.flags[].fit": "better_field_match_available: field fit of the kept target (0).",
    "quality_flags.flags[].suggested_soc": "better_field_match_available: best-fitting linked occupation that is not a target.",
    "quality_flags.flags[].suggested_title": "better_field_match_available: its O*NET title.",
    "quality_flags.flags[].suggested_fit": "better_field_match_available: its field fit.",
    "quality_flags.flags[].count": "Optional: supervisory_task_kept: number of practice tasks.",
    "quality_flags.flags[].practice_ids": "Optional: supervisory_task_kept: practice_ids that still cite a supervisory task.",
    "quality_flags.flags[].detail": "Short explanation of the flag.",
    "quality_flags.actions": "Generated tier: changes the checks made automatically (no human decision needed).",
    "quality_flags.actions[].action": "target_dropped, target_added or supervisory_tasks_dropped.",
    "quality_flags.actions[].onet_soc_code": "Optional: target_dropped / target_added: the occupation.",
    "quality_flags.actions[].occupation_title": "Optional: target_dropped / target_added: its title.",
    "quality_flags.actions[].count": "Optional: supervisory_tasks_dropped: number of tasks skipped.",
    "quality_flags.actions[].onet_task_ids": "Optional: supervisory_tasks_dropped: O*NET Task IDs skipped as supervisory/managerial.",
    "quality_flags.actions[].detail": "Why the change was made.",
    "quality_flags.notes": "Generated tier: context that needs no action.",
    "quality_flags.notes[].note": "entry_target_not_job_zone_4 or entry_target_fallback.",
    "quality_flags.notes[].job_zones": "Optional: entry_target_not_job_zone_4: Job Zones of the entry targets.",
    "quality_flags.notes[].detail": "Explanation.",
    "quality_flags.retired_checks": "Generated tier: checks removed since the previous release and why (v4 low_title_overlap).",
    "quality_flags.informational": "Authored tier only: observations that are not flags.",
    "quality_flags.informational.supervisory_task_cited": "Authored practice_ids whose cited O*NET task is supervisory; the authored scenario was written for that and kept.",
    "quality_flags.note": "Authored tier only: explains why the checks are informational for reviewed majors.",
    "target_plausibility": "Generated tier: field-fit check of the rule's entry targets (null for the authored tier, whose targets were reviewed).",
    "target_plausibility.method": "build.FIELD_FIT_RULE: TF-IDF cosine between the CIP title's field terms (stemmed, stop words removed) and each occupation's O*NET title, description and task statements; drop and flag thresholds.",
    "target_plausibility.cip_field_terms": "Stemmed field terms of the CIP title used for the fit.",
    "target_plausibility.rule_targets": "O*NET-SOC codes the Job Zone rule picked before the check.",
    "target_plausibility.final_targets": "O*NET-SOC codes after the check (= entry_targets).",
    "target_plausibility.fit": "Map of O*NET-SOC code to field fit (0-1) for the same-tier candidate pool and the rule targets.",
    "target_plausibility.fit.<key>": "Field fit of one occupation (key = O*NET-SOC code).",
    "target_plausibility.dropped": "Rule targets removed as clearly implausible (fit 0, specialty code whose base .00 occupation also has fit 0, series fit below build.FIT_SERIES_KEEP, and better-fitting linked occupations exist).",
    "target_plausibility.dropped[].soc": "Dropped occupation.", "target_plausibility.dropped[].title": "Its title.",
    "target_plausibility.dropped[].fit": "Its field fit (0).", "target_plausibility.dropped[].base_soc": "Base .00 occupation of the specialty.",
    "target_plausibility.dropped[].base_title": "Title of the base occupation.", "target_plausibility.dropped[].base_fit": "Field fit of the base occupation (0).",
    "target_plausibility.dropped[].series_fit": "Fit with the titles of the program's 4-digit CIP series (below build.FIT_SERIES_KEEP).",
    "target_plausibility.dropped[].reason": "Why it was dropped.",
    "target_plausibility.added": "Fallback targets added in the rule's ranking order (fit > 0) to keep the target count.",
    "target_plausibility.added[].soc": "Added occupation.", "target_plausibility.added[].title": "Its title.", "target_plausibility.added[].fit": "Its field fit.",
    "target_plausibility.flags": "better_field_match_available flags (same objects as quality_flags.flags).",
    "target_plausibility.flags[].flag": "better_field_match_available.", "target_plausibility.flags[].onet_soc_code": "Kept target.",
    "target_plausibility.flags[].occupation_title": "Its title.", "target_plausibility.flags[].fit": "Its fit (0).",
    "target_plausibility.flags[].suggested_soc": "Suggested alternative.", "target_plausibility.flags[].suggested_title": "Its title.",
    "target_plausibility.flags[].suggested_fit": "Its fit.", "target_plausibility.flags[].detail": "Explanation.",
}

TASK = {  # shared by data/practice_tasks.json tasks[] and plan.json practice_tasks[]
    "practice_id": "Stable id <CIP>-P<n>.",
    "cip_code": "CIP code of the major.",
    "tier": "authored or generated (same as the major).",
    "onet_soc_code": "Occupation whose task is cited.",
    "occupation_title": "O*NET title of that occupation.",
    "onet_task_id": "O*NET 31.0 Task ID (integer) from Task Statements; resolves to a task of onet_soc_code.",
    "onet_task_type": "O*NET task type (Core or Supplemental), or null.",
    "onet_task_url": "O*NET OnLine page of the occupation.",
    "onet_task_statement": "Generated tier only: the O*NET task statement quoted verbatim (USDOL/ETA, CC BY 4.0).",
    "onet_task_statement_note": "Generated tier only: attribution and licence note for the quoted statement.",
    "supervisory_task": "Generated tier only: true if the quoted statement matches the supervisory/managerial rule (always false in this release; such tasks are dropped).",
    "format": "Authored tier only: exercise format (e.g. written plan, calculation, case analysis).",
    "task_intent": "Authored tier only: DreamCo paraphrase of the cited task's purpose (original wording).",
    "task_intent_note": "Authored tier only: says task_intent is not O*NET text.",
    "label": "Item label: 'DreamCo-original practice prompt' (authored) or the generated-template label.",
    "authorship": "Who wrote the item (AI author; human review status).",
    "ownership_class": "Item-level ownership class: synthetic_generated_by_dreamco (authored) or open_license_with_conditions (generated, contains O*NET text).",
    "prompt": "Exercise prompt shown to the learner.",
    "rubric": "3 scoring criteria.",
    "rubric[].criterion": "Criterion name.",
    "rubric[].description": "What full marks require.",
    "rubric[].points": "Maximum points for the criterion (2).",
    "reference_answer_outline": "Reference answer as outline bullet strings.",
    "license": "Item-level licence block (build.item_license).",
    "license.content_class": "What the item contains (DreamCo-original text referencing O*NET ids, or quoted O*NET text plus a DreamCo template layer).",
    "license.ownership_class": "Same as the item's ownership_class.",
    "license.contains_third_party_text": "true if the item reproduces O*NET text (generated tier).",
    "license.license": "Generated: CC BY 4.0. Authored: DreamCo-original (commercial terms pending owner decision).",
    "license.license_url": "Generated only: CC BY 4.0 licence URL.",
    "license.attribution": "Generated only: O*NET/USDOL attribution text.",
    "license.modification_notice": "Generated only: the 'DreamCo has modified...' notice describing what was added.",
    "license.trademark_notice": "Generated only: O*NET trademark notice.",
    "license.dreamco_layer": "Generated only: the DreamCo template fields of the item.",
    "license.dreamco_layer.fields": "Field names that are DreamCo template output.",
    "license.dreamco_layer.authorship": "Authorship of the template layer.",
    "license.dreamco_layer.commercial_terms": "DreamCo commercial terms (not set; pending the owner's decision).",
    "license.authorship": "Authored only: authorship of the item.",
    "license.commercial_terms": "Authored only: DreamCo commercial terms (not set; pending the owner's decision).",
    "license.third_party_references": "Authored only: the O*NET identifiers the item references (not text) and their licence.",
    "license.third_party_references.fields": "Field names holding O*NET identifiers or titles.",
    "license.third_party_references.license": "CC BY 4.0.",
    "license.third_party_references.license_url": "CC BY 4.0 licence URL.",
    "license.third_party_references.attribution": "O*NET/USDOL attribution text.",
    "license.third_party_references.trademark_notice": "O*NET trademark notice.",
}


def pre(prefix, d):
    return {f"{prefix}{k}": v for k, v in d.items()}


def subtree(prefix, d):
    return {k: v for k, v in d.items()}


PLAN_LICENSE = {
    "license": "Plan-level licence and attribution block (build.plan_license).",
    "license.summary": "One-line summary of the plan's mixed licensing.",
    "license.license_url": "CC BY 4.0 licence URL (O*NET-derived content).",
    "license.attribution": "O*NET 31.0 Database and Crosswalk attribution text.",
    "license.required_notices": "Notices that must accompany the O*NET-derived content (database, trademark, modification, crosswalk).",
    "license.dreamco_commercial_terms": "DreamCo commercial terms for its own layer (not set; pending the owner's decision).",
    "license.per_item_licensing": "Pointer: each practice task carries its own licence block.",
    "license.components": "Field groups of this file with their licence.",
    "license.components[].fields": "Field names (paths) the component covers.",
    "license.components[].content_class": "What the fields contain.",
    "license.components[].ownership_class": "Ownership class of the component.",
    "license.components[].license": "Licence of the component.",
    "license.components[].license_url": "Optional: licence URL (CC BY 4.0 components).",
    "license.components[].authorship": "Optional: authorship (DreamCo components).",
}

FILES = {}
FILES["data/majors_selected.json"] = {
    "format": "JSON array, one object per included major (1,044)", "description": "Selection and machine data for every major.",
    "fields": pre("[].", MAJOR)}
FILES["data/practice_tasks.json"] = {
    "format": "JSON object", "description": "All practice tasks of all majors with per-item licensing.",
    "fields": {
        "label": "File-level label; says licensing is per item (authored items DreamCo-original, generated items contain O*NET text).",
        "label_note": "Explains the mixed label.",
        "note": "Earlier file-level note, kept unchanged.",
        "ownership_class": "Most restrictive valid policy class among the items (open_license_with_conditions); each item keeps its own ownership_class.",
        "ownership_class_rule": "How the file-level class is chosen (restrictiveness order; the policy file lists classes without ranking them).",
        "ownership_classes": "Ownership class by tier.",
        "ownership_classes.authored": "synthetic_generated_by_dreamco.",
        "ownership_classes.generated": "open_license_with_conditions (quoted O*NET text, CC BY 4.0).",
        "authorship": "Authorship by tier.",
        "authorship.authored": "Authorship of authored items.",
        "authorship.generated": "Authorship of generated items.",
        "license": "File-level licence block for the O*NET content.",
        "license.third_party": "Name of the third-party source (O*NET 31.0, USDOL/ETA).",
        "license.license_url": "CC BY 4.0 licence URL.",
        "license.attribution": "O*NET attribution text.",
        "license.required_notices": "Notices that must accompany the O*NET content.",
        "license.dreamco_commercial_terms": "DreamCo commercial terms (not set; pending the owner's decision).",
        "created_at": "Release build timestamp, ISO 8601 with UTC offset (fixed per release for reproducible builds).",
        "onet_version": "Pinned O*NET database version (31.0).",
        "tier_counts": "Number of tasks per tier.",
        "tier_counts.authored": "Authored tasks (162).",
        "tier_counts.generated": "Generated tasks.",
        "tasks": "List of practice task items.",
        **pre("tasks[].", TASK)}}
FILES["data/major_to_onet.csv"] = {
    "format": "CSV with header", "description": "One row per CIP-to-O*NET link of an included major (crosswalk data, CC BY 4.0).",
    "fields": {"cip_code": "CIP 2020 code.", "cip_title": "CIP 2020 title.", "onet_soc_code": "Linked O*NET-SOC code.",
               "occupation_title": "O*NET occupation title."}}
FILES["data/coverage.csv"] = {
    "format": "CSV with header", "description": "Every CIP code in the crosswalk with its inclusion decision.",
    "fields": {"cip_code": "CIP 2020 code.", "cip_title": "CIP 2020 title.", "status": "included or excluded.",
               "tier": "authored, generated, or empty when excluded.", "reason": "Why the code was included or excluded (authored/coverage_rules.json)."}}
FILES["study_plans/<stem>/plan.json"] = {
    "format": "JSON object", "description": "Machine layer of one plan (stem = <CIP>_<title slug>); same content as the markdown plan.",
    "fields": {**MAJOR, "label": "Plan label (DreamCo study plan, tier).", "authorship": "Authorship of the DreamCo layer.",
               "created_at": "Release build timestamp, ISO 8601 with UTC offset.",
               "practice_tasks": "This major's practice task items (same objects as data/practice_tasks.json).",
               **pre("practice_tasks[].", TASK), **PLAN_LICENSE}}
FILES["study_plans/<stem>/provenance.json"] = {
    "format": "JSON object (schemas/data_package_asset_provenance.schema.json)", "description": "Provenance record read by the license gate.",
    "fields": {
        "schema": "Schema id.", "asset_id": "Asset id.", "title": "Asset title.", "capability_id": "career-pathway-study-plan.",
        "evidence_id": "Provenance record id (provenance:<asset_id>).", "source_type": "Source type per the evidence-provenance schema.",
        "source_reference": "Primary source URL.", "retrieved_at": "Date the O*NET files were downloaded (ISO 8601 calendar date; time not recorded).",
        "content_version": "Versions of the sources and the build.", "license_or_usage_basis": "Licence basis text.",
        "transformation": "Transformation type per the evidence-provenance schema.", "evaluator_version": "Build tool and sha256.",
        "integrity_hash": "sha256 of the markdown plan (sha256:<hex>).", "ownership_class": "Asset ownership class.",
        "owner": "Owner (DreamCo).", "creator": "Who produced the asset.", "attribution_text": "Attribution text for the plan.",
        "review_status": "Human review status.", "human_review": "Human review details (none yet).", "notes": "Free-text notes.",
        "asset_files": "Files of the asset with hashes.", "asset_files[].path": "Path relative to the pack root.",
        "asset_files[].sha256": "sha256 of the file.", "asset_files[].bytes": "File size in bytes.",
        "sources": "Third-party sources used.", "sources[].source_id": "Source id.", "sources[].title": "Source title.",
        "sources[].publisher": "Publisher (USDOL/ETA).", "sources[].url": "Download URL.", "sources[].version": "Source version.",
        "sources[].retrieved_at": "Download date (ISO 8601 calendar date).", "sources[].sha256": "Optional: sha256 of a single-file source.",
        "sources[].files": "Pinned files of the source.", "sources[].files[].name": "File name under raw/.",
        "sources[].files[].url": "File URL.", "sources[].files[].sha256": "sha256 pinned in raw/SOURCES.md.",
        "sources[].license": "CC BY 4.0.", "sources[].license_url": "Licence URL.", "sources[].ownership_class": "Ownership class of the source.",
        "sources[].commercial_use_allowed": "Licence allows commercial use (true).", "sources[].redistribution_allowed": "Licence allows redistribution (true).",
        "sources[].ai_training_allowed": "Licence allows AI training use (true).", "sources[].attribution_required": "Attribution required (true).",
        "sources[].share_alike_required": "Share-alike required (false).", "sources[].required_notices": "Notices the licence requires.",
        "sources[].restrictions": "Restrictions (trademark, endorsement).",
        "derived_components": "DreamCo-derived parts of the asset.", "derived_components[].component": "Component name.",
        "derived_components[].description": "What the component is and how it was derived.",
        "derived_components[].ownership_class": "Ownership class (practice_tasks: per tier).",
        "derived_components[].derivation_type": "Derivation type.", "derived_components[].derived_from": "Inputs of the component.",
        "transformation_history": "Processing steps.", "transformation_history[].step": "Step description.",
        "transformation_history[].tool": "Tool used.", "transformation_history[].tool_version": "Tool version or sha256.",
        "transformation_history[].inputs": "Inputs of the step."}}
FILES["study_plans/<stem>/asset.json"] = {
    "format": "JSON object (schemas/data_package_synthesis_asset.schema.json, plus evidence_root)", "description": "Plan 5.2 synthesis asset record.",
    "fields": {
        "schema": "Schema id.", "asset_id": "Asset id.", "title": "Asset title.", "capability_ids": "Capabilities served.",
        "created_at": "Release build timestamp, ISO 8601 with UTC offset.", "generator_version": "Build tool and sha256.",
        "integrity_hash": "sha256 of the markdown plan.", "ownership_class": "Asset ownership class.",
        "attribution_required": "Attribution required (true).", "commercial_redistribution_allowed": "Licence allows commercial redistribution.",
        "share_alike_required": "Share-alike required (false).", "perspectives_used": "Synthesis perspectives used.",
        "source_refs": "Pinned sources.", "source_refs[].source_id": "Source id.", "source_refs[].version": "Source version.",
        "source_refs[].perspective": "Perspective the source provides.", "source_refs[].pinned_by": "How the version is pinned (sha256 in raw/SOURCES.md).",
        "human_layer": "Human-readable layer.", "human_layer.path": "Markdown plan path.", "human_layer.format": "markdown.",
        "human_layer.sha256": "sha256 of the markdown.", "human_layer.elements": "Sections of the markdown.",
        "machine_layer": "Machine layer.", "machine_layer.path": "plan.json path.", "machine_layer.format": "json.",
        "machine_layer.sha256": "sha256 of plan.json.", "machine_layer.elements": "Top-level fields of plan.json.",
        "dreamco_analysis": "DreamCo's assessment of the sources.", "dreamco_analysis.agree": "What the sources support.",
        "dreamco_analysis.improve": "What DreamCo adds or changes (weighting, outline, practice tasks).",
        "dreamco_analysis.reject": "What DreamCo does not take from the sources.", "dreamco_analysis.still_need_test": "Open questions needing evidence.",
        "validation_evidence_ids": "Evidence ids by kind; each id <kind>:<asset_id>:<run> resolves to <evidence_root>/<kind>/<asset_id>/<run>.json.",
        "validation_evidence_ids.regression": "Regression evidence ids (authored tier): every passing run, -01 to -04 (append-only).", "validation_evidence_ids.holdout": "Holdout evidence ids (empty until a human grades the holdout kit).",
        "validation_evidence_ids.benchmark": "Benchmark evidence ids (none).", "validation_evidence_ids.sandbox": "Sandbox evidence ids (none).",
        "evidence_root": "Repo-relative directory the evidence ids resolve under: study_packs/career_pathways/data/dreamco_knowledge/evidence (the gate resolves it with --repo-root).",
        "notes": "Free-text notes."}}
FILES["study_plans/<stem>/candidate.json"] = {
    "format": "JSON object (gate candidate input)", "description": "Catalog candidate record read by the license gate.",
    "fields": {"candidate_id": "Same as asset_id.", "asset_id": "Asset id.", "title": "Candidate title.", "description": "Short description of the asset.",
               "category": "Catalog category.", "data_types": "Data types (markdown).", "rights_basis": "Rights basis text.",
               "ownership_class": "Ownership class.", "commercial_use_allowed": "Licence allows commercial use.",
               "redistribution_allowed": "Licence allows redistribution.", "rights_declarations": "Rights per content type.",
               "rights_declarations.onet_content": "Rights of the O*NET content.", "rights_declarations.dreamco_original_synthesis": "Rights of the DreamCo layer.",
               "flags": "Candidate flags read by the gate (none).", "provenance_path": "Relative path to provenance.json.",
               "asset_path": "Relative path to asset.json.", "scorecard_score": "Dataset scorecard score (null: never set by the build).",
               "owner_approval": "Owner approval record (null: never set by the build).", "owner_approval_status": "pending."}}
FILES["study_plans/<stem>/license_gate.json"] = {
    "format": "JSON object written by tools/license_provenance_gate.py (schemas/data_package_license_gate.schema.json)", "description": "Gate result for one asset version.",
    "fields": {"schema": "Schema id.", "gate_version": "Gate tool version.", "asset_id": "Asset id.",
               "evaluated_at": "Gate run time (ISO 8601 with offset). Volatile: excluded from the regression hash.",
               "outcome": "Gate outcome (e.g. approved_for_private_use).", "rights_ceiling": "Highest outcome the rights allow.",
               "failed_checks": "Ids of failed checks.", "warnings": "Warnings.", "truth_boundary": "What the gate result does and does not claim.",
               "checks": "Individual checks.", "checks[].id": "Check id.", "checks[].status": "pass, warn or fail.",
               "checks[].scope": "rights or release.", "checks[].outcome_cap": "Outcome cap a failure imposes, or null.", "checks[].reasons": "Reasons.",
               "inputs": "Input files with hashes.", "inputs.<key>": "Input path or sha256 (target, candidate, provenance, asset record, repo_root).",
               "sale_requirements": "Requirements for approved_for_sale.", "sale_requirements.owner_approval_present": "Owner approval present (false).",
               "sale_requirements.scorecard_minimum": "Scorecard minimum for sale.", "sale_requirements.scorecard_score": "Scorecard score (null).",
               "policy_refs": "Policy and schema files the gate used.", **{f"policy_refs.{k}": f"Path of the {k.replace('_', ' ')} policy/schema file." for k in
               ["asset_provenance_schema", "evidence_provenance", "hard_failures", "license_gate_schema", "ownership_classes", "package_manifest_schema",
                "plan", "release_artifacts", "scorecard_tiers", "synthesis_asset_schema", "test_family"]}}}
REC_COMMON = {
    "evidence_id": "<kind>:<asset_id>:<YYYYMMDD-NN>; resolves to <evidence_root>/<kind>/<asset_id>/<run>.json.",
    "capability_id": "career-pathway-study-plan.", "source_type": "Evidence-provenance source type.",
    "source_reference": "integrity_hash of the asset version evaluated (older runs evaluated older versions).", "retrieved_at": "Run time, ISO 8601 with offset (not part of any hash).",
    "content_version": "Evaluated asset version and baseline/kit.", "license_or_usage_basis": "Licence basis of the evaluation output.",
    "transformation": "original_evaluation.", "evaluator_version": "Evaluator script and sha256.",
    "integrity_hash": "sha256:<hex> of the results file at results_path.", "results_path": "Results file path relative to the pack root.",
    "evidence_root": "Optional: repo-relative evidence root (absent in records written before v4).", "split": "Item set evaluated.", "n_items": "Number of items.",
    "metric": "Metric definition.", "score": "Metric value (0-1).", "threshold": "Pass threshold.", "passed": "score >= threshold and the extra conditions in metric.",
    "grader": "Who or what graded."}
FILES["data/dreamco_knowledge/evidence/regression/<asset_id>/<run>.json"] = {
    "format": "JSON object (config/evidence_provenance_schema.json fields)", "description": "Regression evidence record (written by regression.py after the final build).",
    "fields": dict(REC_COMMON)}
FILES["data/dreamco_knowledge/evidence/regression/<asset_id>/<run>.results.json"] = {
    "format": "JSON object; deterministic (no run timestamp)", "description": "Regression results: current build vs the previous release (git baseline).",
    "fields": {"schema": "Schema id.", "asset_id": "Asset id.", "cip": "CIP code.", "run_id": "Run id YYYYMMDD-NN.",
               "baseline": "Baseline release.", "baseline.git_ref": "Full commit sha of the baseline.", "baseline.repo_path": "Pack path in the repo.",
               "baseline.files": "sha256 of baseline inputs.", "baseline.files.<key>": "sha256 of one baseline input (the gate file as canonical JSON without evaluated_at).",
               "current": "Current build.", "current.asset_integrity_hash": "integrity_hash of the current plan.",
               "current.files": "sha256 of current inputs; matches the files on disk.", "current.files.<key>": "sha256 of one current input (the gate file as canonical JSON without evaluated_at).",
               "evaluator_version": "regression.py and sha256.", "metric": "Metric definition.", "threshold": "Pass threshold (1.0).",
               "n_items": "Number of compared items.", "n_ok": "Items preserved, changed with a documented reason, or improved.",
               "score": "n_ok / n_items.", "current_onet_5gram_hits": "5-word O*NET text runs found in the current plan (must be 0).", "passed": "Pass result.",
               "counts_by_kind_and_status": "Item counts by kind and status.", "counts_by_kind_and_status.<key>": "Counts for one item kind.",
               "counts_by_kind_and_status.<key>.<key>": "Count for one status (preserved, changed_with_reason, improved, unexplained_change, fail).",
               "items": "Compared items.", "items[].kind": "Item kind (linked_occupation, knowledge_value, skill_value, entry_target, practice_citation, citation_valid, gate_check, gate_outcome, onet_text_leakage).",
               "items[].key": "Item key (e.g. O*NET-SOC code, element, practice_id, check id).", "items[].status": "Comparison status.",
               "items[].reason": "Documented reason for changed_with_reason (authored/release_changes.json or target_overrides.json).",
               "items[].detail": "Kind-specific detail.", "items[].detail.baseline": "Baseline value.", "items[].detail.current": "Current value.",
               "items[].detail.baseline.onet_soc_code": "Baseline cited occupation.", "items[].detail.baseline.onet_task_id": "Baseline cited task.",
               "items[].detail.current.onet_soc_code": "Current cited occupation.", "items[].detail.current.onet_task_id": "Current cited task.",
               "items[].detail.baseline_position": "Baseline rank position.", "items[].detail.current_position": "Current rank position.",
               "items[].detail.baseline_rank_value": "Optional: baseline value of a ranked element.", "items[].detail.current_rank_value": "Optional: current value of a ranked element.",
               "items[].detail.baseline_rights_ceiling": "Baseline gate rights ceiling.", "items[].detail.current_rights_ceiling": "Current gate rights ceiling.",
               "items[].detail.baseline_5gram_hits": "O*NET 5-gram hits in the baseline plan.", "items[].detail.current_5gram_hits": "O*NET 5-gram hits in the current plan.",
               "items[].detail.baseline_examples": "Example baseline hits.", "items[].detail.current_examples": "Example current hits.",
               "items[].detail.onet_soc_code": "Cited occupation.", "items[].detail.onet_task_id": "Cited task.",
               "items[].detail.occupation_linked": "Cited occupation is linked to the major.", "items[].detail.task_belongs_to_occupation": "Task belongs to the cited occupation.",
               "not_compared": "What is deliberately not compared, and why.", "determinism": "Why the file is reproducible byte for byte.",
               "run_at": "Optional: run time; only in the 20261002-01/-02 results files, written before results were made deterministic (kept unchanged; evidence is append-only)."}}
FILES["evidence/holdout_kit/items.json"] = {
    "format": "JSON object (grader-facing; reveals nothing about the key)", "description": "The 16 blind holdout items (kit v2, rubric discrimination).",
    "fields": {"kit": "Kit name and version.", "created_at": "When the kit was drawn, ISO 8601 with offset.", "n_items": "Number of items (16).",
               "items": "Items in Q01-Q16 order (shuffled at draw time).", "items[].item_id": "Blind id Q01-Q16.",
               "items[].major": "Major title and CIP code.", "items[].prompt": "Scenario prompt written for the kit only.",
               "items[].candidate_answer": "Candidate answer to grade: five labelled points.", "items[].rubric": "3 criteria.",
               "items[].rubric[].criterion": "Criterion name.", "items[].rubric[].description": "What full marks require.", "items[].rubric[].points": "Maximum points (2)."}}
FILES["evidence/holdout_kit/grading_sheet.csv"] = {
    "format": "CSV with header; blank until the grader fills it in", "description": "Grading sheet, one row per item.",
    "fields": {"item_id": "Blind id Q01-Q16 (do not edit).", "major": "Major of the item (do not edit).",
               "criterion_1": "Name of criterion 1 (do not edit).", "score_1": "Grader score 0-2.",
               "criterion_2": "Name of criterion 2.", "score_2": "Grader score 0-2.", "criterion_3": "Name of criterion 3.", "score_3": "Grader score 0-2.",
               "factually_correct": "yes, no or unsure.", "comments": "Free-text comments.", "grader": "Grader name.",
               "graded_at": "When graded, ISO 8601 with offset."}}
# Not produced yet (no human grades exist): documented for score_holdout.py --finalize output.
FILES["data/dreamco_knowledge/evidence/holdout/<asset_id>/<run>.json"] = {
    "format": "JSON object (config/evidence_provenance_schema.json fields); NOT PRODUCED YET", "description": "Holdout evidence record written by score_holdout.py --finalize after the grader declares grading final.",
    "fields": {**REC_COMMON, "source_type": "human_evaluation.", "split": "blind_holdout_v2_rubric_discrimination.", "grader": "Human grader name(s) from the sheet."}}
FILES["data/dreamco_knowledge/evidence/holdout/<asset_id>/<run>.results.json"] = {
    "format": "JSON object; NOT PRODUCED YET", "description": "Holdout results for one asset.",
    "fields": {"schema": "Schema id.", "asset_id": "Asset id.", "run_id": "Run id.", "kit": "Kit name.", "kit_created_at": "When the kit was drawn.",
               "key_sha256": "sha256 of the private key (matches KEY_COMMITMENT.txt).", "items_json_sha256": "sha256 of items.json (matches KEY_COMMITMENT.txt).",
               "grading_sheet_sha256": "sha256 of the filled-in sheet.", "graders": "Grader names.",
               "declared_final": "Grader and time from GRADING_FINAL.txt.", "asset_integrity_hash": "integrity_hash of the asset graded.",
               "metric": "Metric definition.", "threshold": "Agreement threshold (0.8).", "n_items": "Items of this asset in the kit.",
               "score": "Per-asset agreement: fraction of criterion scores inside the accepted band.",
               "passed": "Kit discrimination passed AND agreement >= 0.8 AND no full-strength item judged factually incorrect.",
               "kit_discrimination": "Kit-level pass rule: detection rate >= 0.8 and mean gap >= 1.0 (all-equal scores fail).",
               "full_strength_judged_incorrect": "Full-strength items of this asset the grader judged factually incorrect.",
               "items[]": "Per-item type, human scores, expected scores, agreement and comments (revealed only after grading is final).",
               "limitations": "Limits of this evidence (single owner-grader, few items, builder-written answers)."}}
OTHER = {
    "study_plans/<stem>.md": "Human layer: the markdown study plan (sections listed in asset.json human_layer.elements; generated plans include a Quality flags section).",
    "evidence/pytest.txt": "Verbatim pytest -v output of the release build.",
    "evidence/gate_summary.txt": "Gate outcome counts over all plans.",
    "evidence/MANIFEST.txt": "sha256 of the pack's files at release.",
    "evidence/holdout_kit/items.md": "Same items as items.json, formatted for reading.",
    "evidence/holdout_kit/README.md": "Grader instructions, pass rule, and the note on replacing the v1 kit.",
    "evidence/holdout_kit/KEY_COMMITMENT.txt": "sha256 of the private answer key (which contains a 256-bit nonce) and of items.json; the key itself is kept outside the repository.",
}


def main():
    out = {"schema": "dreamco.edu_career_pathways.data_dictionary.v1",
           "conventions": {"timestamps": "created_at, evaluated_at, retrieved_at of evidence records and graded_at are ISO 8601 date-times with UTC offset; source retrieved_at values in provenance.json are calendar dates (the download time was not recorded).",
                           "paths": "a.b = key b inside object a; a[] = each element of list a; <key> = a data-dependent map key.",
                           "optional": "Descriptions starting with 'Optional' are fields that appear only in some records."},
           "files": FILES, "other_files": OTHER}
    (HERE / "data_dictionary.json").write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    L = ["# Data dictionary", "", "Generated from `docs/make_data_dictionary.py` (machine-readable copy: `docs/data_dictionary.json`).", ""]
    L += [f"- **{k}**: {v}" for k, v in out["conventions"].items()] + [""]
    for pat, spec in FILES.items():
        L += [f"## `{pat}`", "", f"{spec['description']} Format: {spec['format']}.", "", "| Field | Description |", "|---|---|"]
        L += [f"| `{f}` | {d.replace('|', '/')} |" for f, d in spec["fields"].items()] + [""]
    L += ["## Other files", ""] + [f"- `{k}`: {v}" for k, v in OTHER.items()] + [""]
    (HERE / "DATA_DICTIONARY.md").write_text("\n".join(L))


if __name__ == "__main__":
    main()
