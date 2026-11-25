# Buddy O*NET Full Content Model and Task Playbook Standard

**Canonical config:** `config/buddy-onet-content-model-curriculum.json`  
**Status:** Full subject taxonomy and task-guide contract defined; source refresh and per-task authoring remain evidence-gated.

## Full O*NET subject coverage

Buddy's occupational curriculum covers all six top-level O*NET content-model areas:

1. **Worker Characteristics:** abilities, career interests, career types, specific interest areas, work values and work styles.
2. **Worker Requirements:** essential and transferable skills, software skills, knowledge and education.
3. **Experience Requirements:** training and experience, job zones, licensing and entry requirements.
4. **Occupational Requirements:** general, intermediate and detailed work activities, work context and organizational context.
5. **Occupation-Specific Information:** occupation titles/descriptions, alternate titles, tasks, task categories and ratings, emerging tasks, technology skills and tools used.
6. **Workforce Characteristics:** labor-market information and occupational outlook.

The curriculum also includes task-to-detailed-work-activity relationships, related occupations, content-model reference data, scale anchors, occupation metadata and data-collection methodology.

## Official data refresh

The current O*NET 31.0 production release (August 2026) reports 1,016 occupation records, 18,838 task statements, 165,780 task ratings, 338 emerging tasks, 74,702 work-activity rows and 305,389 work-context rows. It also includes software skills (31,821), essential skills (18,200), transferable skills (45,500), knowledge (60,060), abilities (94,640), education (11,495), training/experience (26,812), job zones (923), alternate job titles (54,269), reported titles (8,189), related occupations (18,460), task-to-DWA links (24,087), and additional scale, metadata and content-model reference files. The machine-readable file inventory and counts are in `config/buddy-onet-content-model-curriculum.json`. These are release-specific snapshot counts; refresh and verify every file and hash on each O*NET release. The O*NET 31.0 database is CC BY 4.0: preserve attribution to O*NET and the U.S. Department of Labor, link the license, and indicate changes.

Official sources:
- [O*NET Database](https://www.onetcenter.org/database.html)
- [O*NET Content Model](https://www.onetcenter.org/content.html)
- [O*NET 31.0 Content Model Reference](https://www.onetcenter.org/dictionary/31.0/json/content_model_reference.html)

## AI capability and safety classification

Every task statement receives its own suitability classification:
- AI assistive: research, explanation, drafting, calculation or recommendation with human verification.
- Bounded automation: approved digital execution with least privilege, validation, audit and rollback.
- Human-supervised or regulated: qualified human judgment, approval or professional sign-off remains mandatory.
- Physical or sensor-dependent: a chat agent alone cannot perform the real-world work.
- Not assessed: insufficient evidence; autonomous execution is blocked.

Do not claim that AI can perform all occupations merely because their task statements are catalogued. Task-by-task evidence, hardware, tools, safety controls, licenses and human authority determine the permitted role.

## Division delivery

Shared O*NET literacy is available to all 55 canonical divisions and 65 MasterBot lanes. Specialist task routing follows the reviewed crosswalk; unresolved ownership remains in the review queue. Each task guide must preserve its O*NET release, occupation code, task ID, source hash, division mapping, tool requirements, safety context, AI suitability class, human approvals, simulation, benchmark and provenance.

## Required task guide

Each task receives an original detailed guide, prerequisite and knowledge map, professional tool comparison, workflow, worked example, practice simulation, answer key, failure recovery, human handoffs, lawful revenue/job pathway where applicable, acceptance tests and independent benchmark. Reading a task statement or generating a plan is not evidence of competence, authorization or job qualification.


## Internal task-level study queue

Buddy now has a compact task-index contract at `data/onet/onet-task-index.json`. The scheduled/manual workflow at `.github/workflows/buddy-onet-task-index-refresh.yml` discovers the official current task-statements export, records the release, source URL, SHA-256 digest and attribution, and proposes the refreshed index through a reviewable pull request.

When the verified index is present, `buddy.learning.course_track_registry` exposes one shared study assignment for each unique occupation/task pair to all 55 canonical divisions and 65 MasterBot lanes. A missing index leaves the 31 subject-level foundation lessons available; it does not silently claim that the full task catalog has been loaded.

**Completion boundary:** the task index is not a set of completed detailed guides. Every task still needs original task-specific instruction, tool research, a workflow, practice simulation, AI/human suitability classification, credential and safety review, acceptance tests, an unseen assessment and reviewer evidence. The index is public O*NET metadata, not a certification, license or proof of Buddy's occupational competence. Unknown or changed O*NET releases remain review-required until the reference inventory is reconciled.
