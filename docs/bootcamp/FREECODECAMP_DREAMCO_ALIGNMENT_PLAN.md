# DreamCo x freeCodeCamp: division, video, repository, and engineering alignment

**Snapshot date:** 2026-11-26  
**Repository:** `DreamCo-Technologies/Dreamcobots`  
**Purpose:** Use freeCodeCamp's public curriculum and engineering practices as a quality model for DreamCo without copying protected lesson content or claiming unverified capabilities.

## 1. What the current repository inventory says

This is an inventory snapshot, not a production certification.

| Area | Observed state | What it means |
|---|---:|---|
| Repository tree | 6,338 paths | Large enough to require generated inventories and ownership, not manual spot checks alone |
| MasterBot registry | 65 lanes | Canonical MasterBot target set |
| Domain crosswalk | 55 domains | 45 proposed exact-name matches and 10 unresolved domain mappings; owner approval remains separate |
| Division JSON files | 45 paths | Ten crosswalk domains have no `config/divisions/<domain>.json` file |
| Empty division JSON | `dreamcodelab.json` | A path exists but has no content |
| Division category profiles | 55 profiles | All 55 domains have curated learning-category profiles |
| freeCodeCamp video catalog | 1,740 rows | Catalog status is `partial`; upstream expected count is not proven |
| Unclassified video rows | 519 | These need a human-reviewed subject classification queue, not automatic assignment |
| Video subject taxonomy | 22 categories | Supports multi-label routing across domains |
| Specialist course artifacts | 0 rows | 960 specialist module slots are still unfilled (120 targets × 8 modules) |
| Open pull requests | 68 | Must be reviewed and reconciled; old base SHAs are not evidence of merge readiness |
| Open issues | 98 | Includes repeated CI incident issues that need root-cause deduplication |

The ten domain configuration files missing from the 55-domain crosswalk are:

- DreamAffiliate
- DreamAgency
- DreamFoundry
- DreamFranchise
- DreamIntegrations
- DreamLicensing
- DreamRobotics
- DreamSaaS
- DreamStreaming
- DreamTravel

The current crosswalk is explicitly proposed and requires owner review. Do not create ownership approvals by guessing from names or category similarities.

## 2. Use the current freeCodeCamp curriculum as the teaching pattern

The current freeCodeCamp v9 curriculum is organized as:

`Chapter → Module → Block → Challenge`

Blocks include:

- **Lecture:** concise explanations with interactive examples
- **Workshop:** guided, step-by-step project work
- **Lab:** independent problem solving and project completion
- **Review:** a focused recap of the module
- **Quiz:** knowledge checks

Apply this instructional pattern to DreamCo. Do not copy freeCodeCamp's lesson text, challenge wording, video transcripts, or course materials wholesale. Create original DreamCo lessons, exercises, projects, and assessment rubrics, citing the source and preserving the applicable license/rights requirements.

Official references:
- Curriculum and contribution guidance: https://contribute.freecodecamp.org/how-to-work-on-coding-challenges/
- Main curriculum monorepo: https://github.com/freeCodeCamp/freeCodeCamp
- Curriculum structure: https://github.com/freeCodeCamp/freeCodeCamp/blob/main/curriculum/structure/curriculum.json
- Demonstration/certification projects: https://github.com/freeCodeCamp/demo-projects
- Curriculum metadata API (early alpha): https://github.com/freeCodeCamp/curriculum-db
- Curriculum test helpers: https://github.com/freeCodeCamp/curriculum-helpers
- UI components: https://github.com/freeCodeCamp/ui
- Design system: https://github.com/freeCodeCamp/design
- Agent-ready project scaffolding: https://github.com/freeCodeCamp/agent-scaffold
- Official YouTube channel: https://www.youtube.com/@freecodecamp
- freeCodeCamp GitHub organization repositories: https://github.com/orgs/freeCodeCamp/repositories

The older standalone `freeCodeCamp/curriculum` repository is archived; use the curriculum in the current monorepo as the canonical curriculum source.

## 3. Build one authoritative source inventory

Create a versioned source registry for:

1. Every public video from the official freeCodeCamp channel.
2. Every public freeCodeCamp organization repository.
3. The current curriculum certification/module/challenge structure.
4. Official demo projects, tooling, UI/design systems, contributor guides, and infrastructure repositories.

Each video record should retain: immutable video ID, title, canonical URL, description, upload date, duration, source playlist, discovery timestamp, category tags, classification confidence, primary domain, secondary domains, MasterBot targets, related repositories, prerequisites, learning objectives, source/license review state, transcript permission state, original guide path, exercise IDs, capstone ID, and benchmark IDs.

Each repository record should retain: owner/name, URL, description, language, topics, default branch, archived state, last update, license, curriculum area, related videos, relevant directories, build/test commands, and review date.

Use the official YouTube Data API for an auditable full-channel inventory. The current catalog workflow uses metadata enumeration, but the committed snapshot is partial and the repository policy says a recent-upload RSS feed is not a full archive. Reconcile playlist totals, unique video IDs, unavailable/deleted entries, and pagination before marking the inventory complete. Do not infer completeness from the number of rows returned by one scrape.

The repository organization page lists hundreds of public repositories. Enumerate the complete public repository set by API pagination; classify all of them, then prioritize the repositories that contain curriculum, example projects, test tooling, design/UI, documentation, classroom, and infrastructure. Do not assume every repository is relevant to every DreamCo division.

## 4. Route every video to the correct division

Use the existing 22-category taxonomy and the 55 curated domain-category profiles as the first routing layer. Use the video title and public description only as discovery metadata. Do not treat title matching as proof that a video teaches every skill in a target division.

### Routing rules

1. Assign one **primary learning domain** based on the video's main subject.
2. Add **secondary domains** only when the content materially supports their capabilities.
3. Apply shared-foundation categories to the appropriate prerequisite curriculum, not as a substitute for a specialist route.
4. Attach the relevant MasterBot only after the canonical crosswalk and owner mapping have been reviewed.
5. Keep low-confidence, ambiguous, and unclassified records in a human triage queue.
6. Keep videos with no transcript rights in metadata-only status.
7. Link each video to original DreamCo exercises and projects; do not copy its transcript or reproduce its course.
8. Keep video discovery, lesson authorship, learner study, sandbox success, benchmark mastery, and model training as distinct states.

### Category-to-division map

The existing `config/freecodecamp-division-category-profiles.json` is the authoritative first-pass mapping from each domain to the relevant categories. The 22 categories are:

- Computer science and fundamentals
- HTML, CSS and accessibility
- JavaScript and TypeScript
- Frontend and UI frameworks
- Backend and APIs
- Python and automation
- Java and JVM
- C, C++ and systems
- Databases and SQL
- Data science and visualization
- Machine learning and deep learning
- Generative AI and LLMs
- AI agents and MCP
- Cybersecurity and privacy
- Linux, networking and IT
- Cloud, DevOps and CI/CD
- Mobile and cross-platform
- Game development
- Mathematics and statistics
- Career and interview skills
- Software architecture and testing
- Other or unclassified

The 519 currently unclassified rows must be triaged into this taxonomy by reviewing descriptions and official linked resources. Do not mass-assign all of them to a division based on generic keywords. The current generic triage route is a holding lane, not the final division map.

## 5. Finish the specialist curriculum for every division

The specialist-course readiness contract already defines eight required modules for every domain division and MasterBot:

1. Domain overview
2. Core skills and workflows
3. Tools, software, libraries, and integrations
4. Task-by-task playbooks
5. Safety, rights, licensing, and permissions
6. Sandbox labs
7. Assessment and answer key
8. Practical capstone and transfer task

There are 55 domain targets + 65 MasterBot targets = 120 targets. At eight modules each, the work inventory is **960 specialist module artifacts**. The current artifact manifest is empty, so none of these slots should be represented as complete.

Each module needs:
- At least three measurable learning objectives
- At least two original exercises
- A runnable sandbox or practical task
- An assessment rubric and answer key
- Dated citations and source provenance
- Item-level rights review
- Human instructional review
- An explicit link to the division capability contract and relevant code/tests

The shared 18-module foundation is useful, but it does not replace these 960 specialist modules.

## 6. Make Buddy actually learn from the Bootcamp

Use this evidence pipeline:

`Discover → Classify → Rights Review → Author Guide → Study → Exercise → Sandbox → Assess → Holdout → Regression → Review → Mastery Update`

Buddy should store:
- Source IDs and URLs
- Study session and completion evidence
- Original notes and their content hash
- Exercise results and sandbox logs
- Assessment scores and rubric versions
- Benchmark and holdout run IDs
- Reviewer approval and learning-state transitions

Buddy may update its retrieval index, lesson recommendations, spaced-repetition schedule, and capability-gap queue from authorized learning evidence. This is not model-weight training. Weight updates require separately approved training data, explicit rights, an actual training job, checkpoint hashes, reproducible evaluation, holdout results, and regression evidence.

The current source policy records the daily 55-domain / 275-lesson quota as `PLAN_ONLY_NOT_EXECUTED`; it must not be presented as completed study or model training.

## 7. Apply the same engineering quality bar to the whole repository

Every product area should use the same learning-to-production ladder:

`Specified → Implemented → Unit Tested → Integration Tested → E2E Tested → Benchmarked → Security Reviewed → Runtime Verified → Production Approved`

### Division code and bots
- Each capability must link to an implementation, executable test, runtime route, and benchmark.
- Replace description-generated fixtures with independent, hand-authored tests for critical capabilities.
- Validate dependencies, tool schemas, API permissions, rate limits, errors, secret handling, and rollback.
- Keep offline-tested, connected, verified, and production states distinct.

### CI/CD and Actions page
- Inventory every workflow by path, owner, trigger, permissions, dependencies, cadence, and intended output.
- Join each workflow to paginated run history, exact commit SHA, job/step outcome, timestamp, artifact, and freshness window.
- Distinguish static validity from actual runtime success; unknown, stale, skipped, cancelled, and never-run are not passing.
- Capture failed job logs, group incidents by root cause, avoid recursive monitoring, and prevent duplicate issue spam.
- Require fresh successful runtime evidence for critical workflows before production certification.

### Pull-request review
- Anchor every review to the exact immutable PR head SHA.
- Use change-impact mapping to run the smallest relevant tests plus mandatory integration/security suites.
- Review security, correctness, tests, documentation, dependency changes, migrations, and deployment risk.
- Require independent verification of high-confidence findings and a human merge approval.
- Never auto-merge a PR merely because a generated checklist or summary says it is ready.

### Agents
- Every agent needs a versioned purpose, input/output schema, allowed tools, least-privilege permissions, timeout/retry policy, sandbox, failure modes, and tests.
- Validate tool use, prompt-injection handling, state/memory isolation, idempotency, approval gates, and audit logs.
- A markdown agent profile is a specification, not proof that an executable agent is deployed.

### Issues and incidents
- Use one incident record per root cause, with affected runs linked as evidence.
- Deduplicate repeated workflow failures; preserve original logs and run URLs.
- Separate defects, owner decisions, external blockers, and enhancements.
- Close an issue only after the fix is merged and the regression check passes.

### Pages, dashboards, and deployment
- Generate pages and indexes from canonical source data.
- Test all navigation routes, client-side script load order, accessibility, and mobile behavior.
- Validate built assets, deployment target, health endpoint, and rollback receipt.
- A successful GitHub check or Cloudflare notification alone does not certify every product surface.

## 8. Current engineering blockers to close

These open repository issues already record concrete acceptance gaps and should be used as the source of truth until refreshed audits replace them:

- [#18627 — 500-model benchmark runner](https://github.com/DreamCo-Technologies/Dreamcobots/issues/18627): 7,500 matrix rows, zero verified; execution runner is not implemented.
- [#18629 — Cloudflare Workers build failure](https://github.com/DreamCo-Technologies/Dreamcobots/issues/18629): failed build on PR #18628; underlying Cloudflare build log/cause was not available in the recorded evidence.
- [#18630 — folder audit failures](https://github.com/DreamCo-Technologies/Dreamcobots/issues/18630): recorded buddy, buddy_os, website, and runtime test/import failures; money_os untested; marketplace has no tests; systems is a placeholder; test isolation writes into the checkout.
- [#18631 — Actions runtime health](https://github.com/DreamCo-Technologies/Dreamcobots/issues/18631): 198 workflows were statically valid in the recorded report, but runtime status was unknown for all 198.
- [#18632 — per-bot benchmark/evidence](https://github.com/DreamCo-Technologies/Dreamcobots/issues/18632): recorded 1,232 offline-tested profiles, zero connected/verified/production, and missing per-bot benchmark/evidence receipts.

The current open PR #18638 is not mergeable against the current main snapshot. Rebase or rebuild it from the current main commit, rerun the full required checks, and merge only after the folder audit and deployment evidence pass.

## 9. Recommended execution order

1. **Baseline and truth inventory:** run the new video/division audit, refresh the 55-domain/65-MasterBot crosswalk, and establish one current SHA-linked baseline for all 6,338 repository paths.
2. **Repair folder-level failures and test isolation:** fix buddy, buddy_os, website, runtime; add real tests for money_os and marketplace; replace the systems placeholder with working code or explicitly defer it.
3. **Reconcile the ten missing division configs and the empty DreamCodeLab file:** obtain owner approval before mapping or creating division ownership; validate every file against the same schema.
4. **Complete the source inventories:** enumerate all official channel videos and all public freeCodeCamp repositories, reconcile pagination/counts, classify the 519 unclassified videos, and create a reviewed source-to-division map.
5. **Complete the 960 specialist curriculum artifacts:** author the eight modules for each domain and MasterBot target, then run content, rights, human-review, and exercise validation.
6. **Connect Buddy's study runtime:** execute authorized lessons, labs, assessments, holdouts, and spaced repetition; record evidence before changing mastery.
7. **Complete per-bot benchmarks and runtime receipts:** implement real benchmark runners and provider probes; keep unexecuted rows unverified.
8. **Repair Actions, PR review, agents, issues, Pages, and deployment:** measure actual runtime, deduplicate incidents, enforce least privilege, test each surface, and preserve human merge/deployment approval.
9. **Production certification:** run full-division tests, security scans, integration tests, 6-hour soak/learning verification where required, external sandbox probes, and rollback checks on one immutable release commit.

## 10. Acceptance rule

DreamCo is complete only when every canonical domain and MasterBot has:
- An owner-approved mapping
- A non-empty, schema-valid division contract
- An original specialist curriculum
- Executable capabilities and independent tests
- Real benchmark and regression evidence
- Verified runtime routes and required integration probes
- Fresh CI/CD and deployment receipts
- A Buddy learning record tied to the actual course and evidence

Until then, show the exact missing count and blocker. Never substitute a generated catalog, plan, dashboard, or green workflow for working software or real learning evidence.
