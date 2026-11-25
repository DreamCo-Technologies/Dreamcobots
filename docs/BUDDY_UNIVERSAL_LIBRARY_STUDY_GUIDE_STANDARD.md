# Buddy Universal Library and Framework Study System

## Mission

Buddy should learn software libraries and developer platforms inside DreamCo rather than defaulting to a general-purpose model call. This system creates a durable, version-pinned, source-backed curriculum for every discoverable library, framework, SDK, API, runtime, database, protocol, CLI and developer tool across supported ecosystems.

The phrase "every library in the world" is implemented as a continuously refreshed discovery objective, not an impossible one-time completeness claim. Package registries, official documentation indexes, source repositories, standards bodies and vendor catalogs change constantly. DreamCo must show what it has discovered, what it has verified, what remains missing, and when each record was last checked.

## How Buddy should answer before routing externally

1. Search approved DreamCo study guides and internal examples.
2. Search the pinned API inventory and known limitations for the requested version.
3. Search internal sandbox labs, benchmark history and regression evidence.
4. Check the O*NET, Hugging Face, benchmark and division crosswalks.
5. If a gap remains, create a gap record and identify first-party documentation, official release notes, standards and authoritative source repositories.
6. Propose a source-backed original guide and exercises. External model assistance may be used as a research aid only when needed; it does not substitute for verified internal knowledge.
7. Require review and evidence before marking the capability mastered.

Internal-first does not mean never refreshing. A guide becomes stale when the upstream API, version, security posture or support status changes. Buddy must detect that condition and queue a targeted update.

## What every guide must cover

Use `config/buddy-library-study-guide.schema.json` as the machine-readable contract. Every guide must identify:

- Canonical package/project identity, ecosystem, artifact type, official home, documentation, repository, license, pinned version and maintenance state.
- Prerequisites, mental models, learning objectives, terminology and concept dependencies.
- A complete API/symbol/feature inventory for the pinned version, or an explicit partial/unknown status. Do not label an inventory complete without a reproducible enumeration method.
- Official tutorials, examples, migration notes, changelogs and deprecation notices.
- Common use cases, production patterns, advanced and specialist applications, cross-domain integrations and clearly labeled experimental ideas.
- Architecture patterns, tradeoffs, performance and cost considerations, scaling limits and failure modes.
- Security, privacy, supply-chain risks, safe defaults, secrets handling and sandbox requirements.
- Installation, configuration, compatibility, testing, debugging, observability and maintenance.
- Original worked examples, at least three graded exercises, project capstones, acceptance criteria, test plans, debugging playbooks and answer explanations.
- O*NET tasks and skills, Hugging Face task families where applicable, relevant benchmark suites, DreamCo divisions, MasterBot lanes and revenue playbooks where justified.
- Provenance, source revision, review date, rights status, guide status and evidence run identifiers.

A study guide should explain how the software is used in practice—not merely repeat its README. Cover both beginner workflows and specialist capabilities. Include negative knowledge: when not to use the library, what it cannot do, where it fails, and what alternatives are appropriate.

## The "everything humans have tried" requirement

No catalog can truthfully promise to enumerate every experiment ever attempted. Buddy should approximate broad coverage through evidence-backed research:

1. Official examples and tutorials.
2. Maintainer documentation, release notes, migration guides and issue discussions.
3. Reputable production case studies and architecture references.
4. Peer-reviewed papers, technical reports and reproducible public repositories.
5. Community patterns, clearly labeled by evidence quality and version relevance.
6. DreamCo's own original experiments, kept separate from established practice.

For each use case, record the source, version, prerequisites, implementation pattern, outcome evidence, tradeoffs and confidence. Do not turn an unverified anecdote into a recommended production pattern.

## Novel-use research lab

Every guide may propose new combinations and workflows. Each proposal must state a falsifiable hypothesis, expected benefit, baseline, implementation plan, threat model, legal/rights review, sandbox constraints, metrics, ablation or comparison, holdout and regression plan. Label it `hypothesis` until reproduced. Never describe an idea as proven merely because it sounds innovative.

Useful discovery prompts include:

- Can this library reduce latency, memory, cost, or operational complexity in an existing DreamCo workflow?
- Can two libraries be composed to solve a task neither handles well alone?
- Can the same capability be implemented locally or offline?
- Can a workflow be made more accessible, secure, observable, fault tolerant or energy efficient?
- Can an existing API be used in a new domain without violating its license, terms, privacy or safety constraints?
- What is the simplest benchmark that could disprove the proposed benefit?

## Crosswalk requirements

### Hugging Face

Map applicable libraries to Hugging Face task families, model/dataset/Space workflows, Transformers, Datasets, Tokenizers, Evaluate, PEFT, TRL, Accelerate, Hub APIs and relevant deployment/inference tooling. A non-ML library should be marked not applicable rather than forced into an artificial mapping. Model, dataset and Space rights are item-specific.

### O*NET

Map a library to concrete work activities, tasks, knowledge, skills, abilities, technology skills and occupations from the pinned O*NET release. Do not infer that an occupation is fully automatable from a software library or task mapping. Professional licensing, human accountability, safety and jurisdiction-specific requirements remain separate.

### Benchmarks

Select an existing benchmark only when its task and scoring actually match the capability. Record benchmark version, dataset/split provenance, metric, baseline, target, holdout, leakage controls, run ID and regressions. If no suitable benchmark exists, define an original task suite and rubric rather than claiming a score on an unrelated benchmark.

### DreamCo

All 55 canonical divisions and 65 MasterBot lanes can access shared foundation material. Specialty recommendations and execution ownership must follow the reviewed crosswalk. Do not create new divisions or silently reassign specialist ownership because a library appears relevant.

## Rights, security and trust

Public documentation visibility does not automatically grant rights to copy, redistribute, summarize, scrape, download, evaluate on, or train on the material. Record the relevant permissions separately. Prefer original explanations and original exercises with links and attribution.

Treat package code, notebooks, datasets, model files, build scripts, issue comments and user-submitted snippets as untrusted. Inspect provenance and licenses; pin revisions and hashes; disable dataset scripts by default; use isolated, least-privilege sandboxes; block network and filesystem access unless explicitly approved; redact secrets; and require explicit user approval for downloads, gated access, paid compute and model-weight training. No guide may contain credentials or private keys.

## Lifecycle and evidence states

- `discovered`: a candidate exists, but metadata is not yet verified.
- `metadata_verified`: identity, source, ecosystem and version are checked.
- `source_reviewed`: first-party documentation, license and terms are reviewed.
- `guide_drafted`: an original guide meets the structural contract.
- `guide_reviewed`: a human or approved reviewer checks accuracy and provenance.
- `sandbox_passed`: original examples and exercises pass in an isolated environment.
- `benchmark_passed`: the target benchmark meets its declared threshold.
- `holdout_passed`: an unseen assessment passes without leakage.
- `regression_passed`: existing capabilities remain within guardrails.
- `mastered`: all required evidence exists and promotion criteria are met.
- `stale`: upstream changes require review.
- `blocked`: rights, security, source quality or other requirements prevent progress.

Reading a guide is not mastery. Every promoted capability must retain model/version, guide revision, test and benchmark run IDs, holdout evidence, regression results and reviewer information. A later regression reopens the capability.

## Completion dashboard requirements

The dashboard should report, by ecosystem and DreamCo division:

- Discovered candidates and registry coverage date.
- Verified libraries, guide coverage and API inventory completeness.
- Guides needing review, stale guides and blocked items.
- Exercises and sandbox pass rates.
- Benchmark/holdout/regression coverage and mastery evidence.
- O*NET/Hugging Face/benchmark/division crosswalk coverage.
- Open innovation hypotheses and reproduced results.
- Rights status and missing permissions.

Never collapse these into one misleading "percent complete" number. Distinguish catalog coverage, guide completeness, study completion and demonstrated mastery.

## Operational next steps

1. Enumerate registries incrementally with rate limits and cached cursors.
2. Normalize package identity across forks, renamed projects and duplicate distributions.
3. Generate candidate records and prioritize by DreamCo usage, security exposure, benchmark gaps and O*NET task relevance.
4. Author guides in small reviewable batches.
5. Add deterministic validators and CI checks for schema, provenance, stale versions, rights, crosswalks and evidence.
6. Connect the registry to Buddy's internal retrieval and study scheduler.
7. Publish only validated internal knowledge; retain unknowns and partial coverage honestly.


## Runtime adapter and existing ecosystem catalog

The first production-facing adapter is `buddy.learning.universal_library_registry`. It provides:

- `search_internal_library_knowledge(query)`: searches only DreamCo-owned, approved, rights-eligible guide files in `data/buddy-library-study-guides/`.
- `record_library_knowledge_gap(query)`: appends a local JSONL gap event. It does not call an external model, fetch a website or start a download.
- `library_coverage_report()`: reports ecosystem lanes, approved guide count and recorded gaps without claiming worldwide completeness.
- `tools/buddy_library_knowledge.py`: CLI for `search`, `record-gap` and `report`.

The existing `config/library_ecosystems.json` is the extensible discovery-lane catalog. The shared `buddy.learning.course_track_registry` now emits an initial discovery lesson for each listed ecosystem, making those lessons available through the existing shared 55-domain / 65-MasterBot queue. These are discovery assignments, not individual package records and not completed study guides.

Before a guide can be searched internally, the adapter checks its core structure, version, official HTTPS home, source provenance, learning objectives, API coverage declaration, use cases, practice exercises, evaluation plan and explicit rights fields. Approved guides with gated or unknown documentation access, or without an approved derivative-summary basis and reviewed evidence state, are rejected.

### Current runtime boundary

The adapter does not yet crawl package registries or automatically author guides. Registry discovery must be a separately scheduled, rate-limited process with per-provider pagination, cache/cursor persistence, package deduplication, source/version/license metadata, and an explicit opt-in network mode. It must never execute downloaded packages. External research is a gap-resolution step, not the default Buddy response path.


## Opt-in public registry metadata discovery

The opt-in metadata-only provider adapter is `buddy.learning.library_registry_discovery.search_public_registry`, configured by `config/buddy-library-registry-adapters.json`. Initial providers cover npm, crates.io, NuGet, RubyGems, Packagist, Hugging Face model metadata, Hugging Face dataset metadata, and exact-name PyPI metadata lookup.

The CLI requires the explicit `discover PROVIDER QUERY --allow-network` flag for one network request. Requests use HTTPS host allowlists, bounded response sizes, bounded timeouts and a fixed user agent. Pagination is caller-controlled and one page is requested per invocation. Results are normalized candidate metadata only, with license/source review pending and download, execution, evaluation and training permissions false or pending.

This is not exhaustive registry crawling: query APIs are ranked/search interfaces, not proof of full package inventory. PyPI support is exact-name lookup rather than global enumeration. Additional ecosystem providers and verified pagination/cursor workflows must be added as their official APIs and terms are reviewed. Do not infer a package's license from a search result; fetch and review authoritative metadata and source terms in a separate governed step.


## Guide authoring workflow

`tools/create_buddy_library_guide_draft.py` creates a structured, original DreamCo guide skeleton from a discovered candidate's canonical ID, name, ecosystem and official HTTPS documentation URLs. It never downloads or executes the library. It writes `review_required`, unknown API coverage, unknown documentation access, and pending evaluation/training/download permissions. It refuses to overwrite an existing guide. The generator is a starting point for research, not an AI-generated assertion that a library has been fully studied.

The first seeded example is `data/buddy-library-study-guides/python-requests.json`, pinned to Requests 2.34.2. It contains an original learning map, partial API inventory, established and experimental use cases, security guidance, exercises, capstones, debugging playbook, benchmark goals, and initial O*NET skill / DreamCo division crosswalks. It remains `review_required`; Buddy's internal search intentionally does not surface it until a reviewer approves it and all rights/evidence gates pass.


## Existing DreamCo library mastery seed inventory

The repository's existing `server/seed-buddy-bot.ts` contains a "Complete Library Mastery Curriculum" spanning 37 technology categories. `tools/build_buddy_library_seed_catalog.py` parses that source into `data/buddy-library-seed-catalog.json`: 536 raw entries deduplicated to 531 candidate records. Every candidate is explicitly marked unverified, with unknown version/license/documentation and no download, execution, evaluation or training permission.

All 531 candidates are now included as discovery lessons in the shared course registry, alongside the 38 ecosystem discovery lanes. These assignments require Buddy to verify whether each item is actually a library, framework, SDK, runtime, platform, API or concept; find official sources; pin a version; review rights; and create an original guide. They are not 531 completed study guides. The seed catalog is a useful starting inventory, not a complete map of every software library in the world.


Approved guides must include `latest_version_checked_at`. The internal retrieval adapter applies the curriculum freshness window (30 days by default) and excludes overdue guides even if their stored status still says `approved_for_study`. Coverage reporting counts these separately as stale-by-age so old documentation cannot silently remain Buddy's current answer.


When a query has no approved guide, internal search also checks the 531-entry seed catalog and may return candidate names/categories. These are explicitly labeled `seed_candidate_unverified`, never as guides or answers. Buddy can then open a gap and use the permissioned metadata discovery workflow to find official sources.


## Ecosystem adapter coverage

`config/buddy-library-ecosystem-adapter-coverage.json` records the actual state of all 38 ecosystem lanes. At this stage, eight ecosystem lanes have query or exact-lookup adapters (npm, crates.io, NuGet, RubyGems, Packagist, exact-name PyPI, and Hugging Face model/dataset metadata, with npm also used for Solidity SDK discovery). Thirty lanes remain manual first-party catalog review. The coverage report exposes these counts rather than implying all registries are automated. Each manual lane remains a scheduled discovery task until an official, terms-reviewed adapter is implemented.
