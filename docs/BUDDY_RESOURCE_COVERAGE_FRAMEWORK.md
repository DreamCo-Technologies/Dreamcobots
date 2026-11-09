# Buddy Resource Coverage Framework

**Status:** `catalogued` documentation framework  
**Primary repository:** `DreamCo-Technologies/Dreamcobots`  
**Purpose:** Ensure Buddy research, learning, engineering, benchmarking, and reporting cover the full DreamCo resource landscape—not only embodied AI.

## Authority and freshness

This document is a coverage crosswalk, not a replacement for the machine-readable registries.

- Resource inventory authority: `config/buddy/resource-registry.json` (`dreamco.buddy.resource_registry.v1`).
- Resource-map explanation: `docs/BUDDY_RESOURCE_MAP.md`.
- Study-resource source inspected: `config/buddy-study-resources-101-200.json`.
- Model category source inspected: `shared/ai-models.ts` (`AI_MODEL_CATEGORIES`).
- Project constraints and evidence rules: `docs/DREAMCO_BUDDY_MASTER_CODEX_DIRECTIVE.md`.

The resource map says its last scan was **2026-10-05**. Treat its connection states and counts as a dated inventory snapshot, not live verification. Re-scan before reporting a provider, secret, workflow, deployment, license, or integration as currently available. The study set is named `101-200` and contains 94 resource rows in the inspected file; do not infer that every number in the range is populated.

## 1. Machine-readable resource-registry categories

The inspected registry contains 23 resource records across these 12 categories:

| Registry category | Count | Coverage responsibility |
|---|---:|---|
| `model_provider` | 4 | Provider contracts, adapters, authentication, routing, policy, cost, latency, and availability |
| `workforce` | 2 | Human/agent ownership, specialist lanes, review responsibilities, and handoffs |
| `model_catalog` | 2 | Model discovery, metadata, versioning, terms, capability and suitability |
| `dataset` | 1 | Study packs, provenance, licensing, splits, curation, and data quality |
| `benchmark` | 1 | Task suites, scorecards, reproducibility, baselines, and regression gates |
| `repo_tool` | 2 | Local RAG, training tools, generators, developer utilities, and testable interfaces |
| `compute` | 2 | GitHub Actions, local/GPU/edge compute, cloud execution, budgets, and capacity |
| `surface` | 2 | GitHub Pages, user-facing surfaces, discussions, and command-center traceability |
| `code` | 4 | Primary and sibling repositories, reusable code, OSS review, and migration |
| `github_platform` | 1 | GitHub API scopes, Apps, Packages, Copilot, permissions, and platform limits |
| `secret_inventory` | 1 | Secret names, ownership, presence checks, rotation, and safe secret handling |
| `terms_constraint` | 1 | Provider terms, training restrictions, data retention, licenses, and permitted use |

### Registry records to keep covered

`xai_grok_api`, `grok_teammate_fleet`, `openai_adapter`, `local_open_model_route`, `huggingface_hub`, `study_packs`, `benchmark_runner`, `local_rag`, `github_actions`, `github_pages`, `gcp_workload_identity`, `copilot_agents`, `local_training_toolchain`, `azure_foundry`, `sibling_repositories`, `github_discussions`, `github_models`, `github_token_scope_gaps`, `starred_oss_blocked`, `starred_oss_permissive`, `starred_oss_unclear_license`, `stripe_and_github_key_secrets`, and `xai_outputs_for_training`.

Do not collapse distinct connection states. Preserve the registry's meanings: `connected`, `contract_only`, `needs_secret`, `needs_owner_decision`, `blocked_by_license`, and `retired_upstream`. A listed resource is not automatically an executable integration.

## 2. Study-resource category coverage

The inspected study-resource set contains 94 rows and the following 71 distinct category labels. Keep the original labels in source data; normalize only in derived indexes so no category is silently lost.

- AI
- AI education
- AI engineering
- AI governance
- API design
- API development
- API engineering
- API standards
- API testing
- C++ testing
- CS education
- Java testing
- JavaScript runtime
- ML education
- ML practice
- NLP
- Node.js
- Python
- Python testing
- TLS
- TLS security
- algorithms
- analytics
- analytics engineering
- application monitoring
- backend
- backend architecture
- browser automation
- browser engineering
- browser testing
- cloud native education
- code quality
- computer vision
- data engineering
- data format
- data science
- data systems
- data validation
- database
- databases
- deep learning
- dependency security
- event streaming
- machine learning
- mathematics
- meta-learning
- open source
- privacy
- programming education
- reinforcement learning
- search
- secure development
- security
- security analysis
- security controls
- security knowledge
- security taxonomy
- software licensing
- software security
- software signing
- software supply chain
- static analysis
- statistics
- systems
- systems/cloud
- technical education
- transformers
- web development
- web performance
- web security
- workflow orchestration

## 3. AI model catalog categories

The inspected `AI_MODEL_CATEGORIES` list has 20 categories:

- General Chat
- Coding
- Research
- Writing & Content
- Image Generation
- Video & Audio
- Business & CRM
- Data & Analytics
- Autonomous Agents
- Customer Support
- Marketing & SEO
- Finance & Trading
- Healthcare AI
- Legal & Compliance
- Education
- Voice & Speech
- Translation
- Robotics & IoT
- Security
- No-Code/Low-Code

Model listings are catalog metadata, not proof of a current provider integration, current price, available entitlement, or benchmarked capability. Verify each claim against current provider documentation and runtime evidence before surfacing it as available.

## 4. Cross-cutting research and capability families

These families organize discovery across the source categories above. They supplement—not replace—the source labels.

1. **Models and intelligence:** foundation and small models, multimodal models, reasoning, coding, memory, knowledge graphs, model selection, distillation, fine-tuning, and world models.
2. **Perception and embodied systems:** computer vision, camera perception, object/scene understanding, gesture and sign recognition, pose estimation, body-language cues, spatial reasoning, navigation, robotics, IoT, and human-robot interaction.
3. **Speech and communication:** speech recognition and synthesis, audio understanding, translation, turn-taking, multimodal grounding, accessibility, and clarification.
4. **Agents and automation:** planning, tool use, multi-agent coordination, browser/computer use, workflow orchestration, retries, recovery, and approval-gated execution.
5. **Software engineering:** programming languages, frontend/backend, APIs, application architecture, testing, debugging, code generation, static analysis, and reverse engineering.
6. **Data and knowledge:** data ingestion, quality, databases, streaming, analytics, RAG, hybrid/vector search, embeddings, retrieval, knowledge extraction, and provenance.
7. **Learning and education:** curricula, courses, study packs, datasets, synthetic data, SFT/DPO/LoRA, training recipes, evaluation, bootcamps, and learner progress.
8. **Security, privacy, and governance:** identity, authorization, secrets, threat modeling, secure development, safety, prompt-injection defense, licensing, terms, retention, and audit.
9. **Cloud, compute, and infrastructure:** local execution, GPUs, edge devices, AWS/Azure/GCP, CI/CD, containers, distributed systems, storage, monitoring, and cost controls.
10. **Business and operations:** business workflows, CRM, customer support, finance, marketing, SEO, commerce, sales, real estate, revenue operations, and opportunity research.
11. **Product and experience:** UX/UI, accessibility, design systems, no-code/low-code, websites, mobile applications, customer journeys, and product analytics.
12. **Science and emerging technology:** mathematics, statistics, scientific computing, simulation, digital twins, materials/manufacturing, physical AI, and robotics.
13. **DreamCo platform operations:** repository health, bot/division registries, certification, benchmarks, GitHub Pages, Command Center, observability, release management, incident response, and continuous improvement.

## 5. Evidence and capability lifecycle

Every research item and resulting Buddy capability must distinguish these stages:

- `catalogued`: source or capability is indexed with provenance and category.
- `implemented`: repository code or a governed integration exists.
- `sandbox_verified`: isolated execution passed, with reproducible evidence.
- `benchmark_verified`: a defined benchmark passed against a recorded baseline.
- `regression_verified`: repeatable regression checks passed.
- `production_verified`: real production behavior was verified with operational evidence.

Never promote a capability based on a paper abstract, README, model card, demo video, generated code, or successful API listing alone. Do not claim model training, deployment, live integration, or production readiness without direct evidence.

For each research/resource record, capture where applicable:
- source URL, publisher/maintainer, publication or release date, and retrieval date;
- original category label(s), resource ID, repository/path, and owner lane;
- license/provider terms and permitted use, including training-data restrictions;
- evidence type, reproducibility, benchmark/task, hardware, dependencies, and known limitations;
- Buddy capability mapping, current evidence status, open gaps, and next safe experiment;
- decision: monitor, study, sandbox, benchmark, integrate after approval, blocked, or retire.

## 6. Daily coverage protocol

For each reporting cycle:

1. Load the current resource registry, study-resource catalogs, model categories, bot/division manifests, relevant Markdown documentation, and sibling-repository inventories.
2. Reconcile category labels and resource IDs; flag undocumented, duplicate, stale, unowned, or unmapped entries rather than deleting them.
3. Search for meaningful new work across every category. Prioritize primary papers, official documentation, maintained repositories, datasets, benchmarks, standards, and reproducible demonstrations.
4. Record both positive findings and categories with no material update. A category is not “covered” merely because it was mentioned.
5. Separate demonstrated results, independently reproduced results, promising proposals, and speculation.
6. Recommend bounded experiments with acceptance criteria, compute/cost estimates, safety controls, and rollback.
7. Update documentation and dashboards only through reviewable changes. Do not silently alter production behavior, incur spend, train on restricted data, deploy, or merge without the required approval and verification.

## 7. Coverage completeness checks

A future automated validator should fail or warn when:
- a registry resource has no category mapping or source/provenance;
- a study resource category is absent from the derived coverage index;
- a model category has no research/availability policy;
- a capability claim has no evidence status or evidence pointer;
- a research result has no date, source, limitation, or next-step disposition;
- a blocked/retired/owner-decision resource is represented as available;
- generated catalog or GitHub Pages output differs from its source registry;
- a documentation update contradicts the master directive or resource registry.

Suggested initial validation targets (to be implemented and tested separately):
- all 23 resource-registry IDs represented;
- all 12 registry categories represented;
- all 94 study-resource rows represented, preserving all 71 distinct labels;
- all 20 AI model categories represented;
- every new research item tagged to at least one category and one Buddy capability or explicit “monitor only” disposition.

**Current limitation:** this document records the categories observed in the inspected source files. It does not claim that every repository, every Markdown file, every division, every bot, every external resource, or every sibling-repository asset has already been audited. Expand the crosswalk as those authoritative inventories are inspected.



# 8. Dedicated category sections and Buddy subsystem boundaries

The requirement is one category → one section → one separately accountable subsystem. No category below is merely a tag under a broad umbrella. Similar categories may share infrastructure, but they must not be collapsed into one registry identity, backlog, test suite, or status. For example, `database` and `databases` remain distinct source labels until an explicit, reviewed alias decision is recorded.


## Registry-category systems

Each category below has its own named Buddy subsystem boundary. These are **architecture specifications**, not claims that each subsystem is already implemented or running. Each subsystem must have its own registry identity, owner, interface, tests, telemetry, documentation, and evidence status. Shared platform services may be reused, but category ownership and acceptance criteria remain separate.

### REG-01 — benchmark

- **Subsystem ID:** `buddy_benchmark_system`
- **Mission:** Evaluation and certification.
- **Inputs:** Versioned tasks, datasets, baselines, scoring rubrics, run artifacts.
- **Outputs:** Comparable scores, pass/fail gates, regression reports.
- **Control and measures:** Reproducibility, validity, coverage, false-pass rate. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### REG-02 — code

- **Subsystem ID:** `buddy_code_system`
- **Mission:** Reusable software and repository assets.
- **Inputs:** Source files, dependency manifests, ownership, licenses, tests.
- **Outputs:** Reviewed code modules, integration proposals, SBOM and test evidence.
- **Control and measures:** Test pass rate, vulnerabilities, maintainability, license compliance. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### REG-03 — compute

- **Subsystem ID:** `buddy_compute_system`
- **Mission:** Execution capacity and runtime environments.
- **Inputs:** Runner inventory, workload profile, budgets, secrets references.
- **Outputs:** Scheduled or on-demand execution with resource and cost telemetry.
- **Control and measures:** Availability, queue time, latency, utilization, spend. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### REG-04 — dataset

- **Subsystem ID:** `buddy_dataset_system`
- **Mission:** Governed learning and evaluation data.
- **Inputs:** Dataset metadata, provenance, license, schema, splits, consent/terms.
- **Outputs:** Validated, versioned datasets and data cards.
- **Control and measures:** Coverage, quality, leakage, freshness, license compliance. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### REG-05 — github_platform

- **Subsystem ID:** `buddy_github_platform_system`
- **Mission:** GitHub platform capabilities and permission boundaries.
- **Inputs:** API scopes, app installation state, org settings, audit events.
- **Outputs:** Least-privilege integration plan and verified platform actions.
- **Control and measures:** Permission coverage, action success, auditability, scope violations. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### REG-06 — model_catalog

- **Subsystem ID:** `buddy_model_catalog_system`
- **Mission:** Model discovery and capability metadata.
- **Inputs:** Provider/model identifiers, versions, context limits, modalities, terms.
- **Outputs:** Searchable model cards and eligibility decisions.
- **Control and measures:** Metadata freshness, route suitability, evaluation coverage. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### REG-07 — model_provider

- **Subsystem ID:** `buddy_model_provider_system`
- **Mission:** Governed access to external or local inference providers.
- **Inputs:** Adapter contracts, runtime health, secret references, policy and terms.
- **Outputs:** Approved inference calls, normalized responses, usage/cost records.
- **Control and measures:** Availability, latency, quality, cost, policy compliance. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### REG-08 — repo_tool

- **Subsystem ID:** `buddy_repo_tool_system`
- **Mission:** Developer, learning, retrieval, and training utilities.
- **Inputs:** Tool contracts, code, dependencies, CLI/API inputs, tests.
- **Outputs:** Versioned tool outputs and reproducible execution artifacts.
- **Control and measures:** Correctness, reliability, test coverage, runtime and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### REG-09 — secret_inventory

- **Subsystem ID:** `buddy_secret_inventory_system`
- **Mission:** Secret lifecycle and access governance.
- **Inputs:** Secret names, owning service, vault reference, rotation metadata (never values).
- **Outputs:** Presence/health attestations and remediation tasks.
- **Control and measures:** Exposure incidents, rotation age, least privilege, missing-secret rate. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### REG-10 — surface

- **Subsystem ID:** `buddy_surface_system`
- **Mission:** User-facing and operator-facing product surfaces.
- **Inputs:** Page/app routes, content data, auth policy, telemetry, accessibility checks.
- **Outputs:** Published, traceable views of verified system state.
- **Control and measures:** Uptime, accessibility, freshness, broken links, user task success. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### REG-11 — terms_constraint

- **Subsystem ID:** `buddy_terms_constraint_system`
- **Mission:** Legal, contractual, and licensing guardrails.
- **Inputs:** Provider terms, OSS licenses, dataset permissions, usage restrictions.
- **Outputs:** Allow/deny decisions and documented compliance conditions.
- **Control and measures:** Unapproved use count, license coverage, policy exceptions. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### REG-12 — workforce

- **Subsystem ID:** `buddy_workforce_system`
- **Mission:** Human and specialist-agent ownership model.
- **Inputs:** Capability lanes, owners, responsibilities, permissions, escalation paths.
- **Outputs:** Assigned work, review evidence, handoffs, accountability records.
- **Control and measures:** Ownership coverage, review latency, completion quality, escalation rate. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.


## Study-resource category systems

Each category below has its own named Buddy subsystem boundary. These are **architecture specifications**, not claims that each subsystem is already implemented or running. Each subsystem must have its own registry identity, owner, interface, tests, telemetry, documentation, and evidence status. Shared platform services may be reused, but category ownership and acceptance criteria remain separate.

### STUDY-01 — AI

- **Subsystem ID:** `buddy_ai_system`
- **Mission:** AI capability research, practice, and controlled execution.
- **Inputs:** Curated AI resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-02 — AI education

- **Subsystem ID:** `buddy_ai_education_system`
- **Mission:** AI education capability research, practice, and controlled execution.
- **Inputs:** Curated AI education resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-03 — AI engineering

- **Subsystem ID:** `buddy_ai_engineering_system`
- **Mission:** AI engineering capability research, practice, and controlled execution.
- **Inputs:** Curated AI engineering resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-04 — AI governance

- **Subsystem ID:** `buddy_ai_governance_system`
- **Mission:** AI governance capability research, practice, and controlled execution.
- **Inputs:** Curated AI governance resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-05 — API design

- **Subsystem ID:** `buddy_api_design_system`
- **Mission:** API design capability research, practice, and controlled execution.
- **Inputs:** Curated API design resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-06 — API development

- **Subsystem ID:** `buddy_api_development_system`
- **Mission:** API development capability research, practice, and controlled execution.
- **Inputs:** Curated API development resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-07 — API engineering

- **Subsystem ID:** `buddy_api_engineering_system`
- **Mission:** API engineering capability research, practice, and controlled execution.
- **Inputs:** Curated API engineering resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-08 — API standards

- **Subsystem ID:** `buddy_api_standards_system`
- **Mission:** API standards capability research, practice, and controlled execution.
- **Inputs:** Curated API standards resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-09 — API testing

- **Subsystem ID:** `buddy_api_testing_system`
- **Mission:** API testing capability research, practice, and controlled execution.
- **Inputs:** Curated API testing resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-10 — C++ testing

- **Subsystem ID:** `buddy_c_testing_system`
- **Mission:** C++ testing capability research, practice, and controlled execution.
- **Inputs:** Curated C++ testing resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-11 — CS education

- **Subsystem ID:** `buddy_cs_education_system`
- **Mission:** CS education capability research, practice, and controlled execution.
- **Inputs:** Curated CS education resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-12 — Java testing

- **Subsystem ID:** `buddy_java_testing_system`
- **Mission:** Java testing capability research, practice, and controlled execution.
- **Inputs:** Curated Java testing resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-13 — JavaScript runtime

- **Subsystem ID:** `buddy_javascript_runtime_system`
- **Mission:** JavaScript runtime capability research, practice, and controlled execution.
- **Inputs:** Curated JavaScript runtime resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-14 — ML education

- **Subsystem ID:** `buddy_ml_education_system`
- **Mission:** ML education capability research, practice, and controlled execution.
- **Inputs:** Curated ML education resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-15 — ML practice

- **Subsystem ID:** `buddy_ml_practice_system`
- **Mission:** ML practice capability research, practice, and controlled execution.
- **Inputs:** Curated ML practice resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-16 — NLP

- **Subsystem ID:** `buddy_nlp_system`
- **Mission:** NLP capability research, practice, and controlled execution.
- **Inputs:** Curated NLP resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-17 — Node.js

- **Subsystem ID:** `buddy_node_js_system`
- **Mission:** Node.js capability research, practice, and controlled execution.
- **Inputs:** Curated Node.js resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-18 — Python

- **Subsystem ID:** `buddy_python_system`
- **Mission:** Python capability research, practice, and controlled execution.
- **Inputs:** Curated Python resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-19 — Python testing

- **Subsystem ID:** `buddy_python_testing_system`
- **Mission:** Python testing capability research, practice, and controlled execution.
- **Inputs:** Curated Python testing resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-20 — TLS

- **Subsystem ID:** `buddy_tls_system`
- **Mission:** TLS capability research, practice, and controlled execution.
- **Inputs:** Curated TLS resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-21 — TLS security

- **Subsystem ID:** `buddy_tls_security_system`
- **Mission:** TLS security capability research, practice, and controlled execution.
- **Inputs:** Curated TLS security resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-22 — algorithms

- **Subsystem ID:** `buddy_algorithms_system`
- **Mission:** algorithms capability research, practice, and controlled execution.
- **Inputs:** Curated algorithms resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-23 — analytics

- **Subsystem ID:** `buddy_analytics_system`
- **Mission:** analytics capability research, practice, and controlled execution.
- **Inputs:** Curated analytics resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-24 — analytics engineering

- **Subsystem ID:** `buddy_analytics_engineering_system`
- **Mission:** analytics engineering capability research, practice, and controlled execution.
- **Inputs:** Curated analytics engineering resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-25 — application monitoring

- **Subsystem ID:** `buddy_application_monitoring_system`
- **Mission:** application monitoring capability research, practice, and controlled execution.
- **Inputs:** Curated application monitoring resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-26 — backend

- **Subsystem ID:** `buddy_backend_system`
- **Mission:** backend capability research, practice, and controlled execution.
- **Inputs:** Curated backend resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-27 — backend architecture

- **Subsystem ID:** `buddy_backend_architecture_system`
- **Mission:** backend architecture capability research, practice, and controlled execution.
- **Inputs:** Curated backend architecture resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-28 — browser automation

- **Subsystem ID:** `buddy_browser_automation_system`
- **Mission:** browser automation capability research, practice, and controlled execution.
- **Inputs:** Curated browser automation resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-29 — browser engineering

- **Subsystem ID:** `buddy_browser_engineering_system`
- **Mission:** browser engineering capability research, practice, and controlled execution.
- **Inputs:** Curated browser engineering resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-30 — browser testing

- **Subsystem ID:** `buddy_browser_testing_system`
- **Mission:** browser testing capability research, practice, and controlled execution.
- **Inputs:** Curated browser testing resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-31 — cloud native education

- **Subsystem ID:** `buddy_cloud_native_education_system`
- **Mission:** cloud native education capability research, practice, and controlled execution.
- **Inputs:** Curated cloud native education resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-32 — code quality

- **Subsystem ID:** `buddy_code_quality_system`
- **Mission:** code quality capability research, practice, and controlled execution.
- **Inputs:** Curated code quality resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-33 — computer vision

- **Subsystem ID:** `buddy_computer_vision_system`
- **Mission:** computer vision capability research, practice, and controlled execution.
- **Inputs:** Curated computer vision resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-34 — data engineering

- **Subsystem ID:** `buddy_data_engineering_system`
- **Mission:** data engineering capability research, practice, and controlled execution.
- **Inputs:** Curated data engineering resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-35 — data format

- **Subsystem ID:** `buddy_data_format_system`
- **Mission:** data format capability research, practice, and controlled execution.
- **Inputs:** Curated data format resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-36 — data science

- **Subsystem ID:** `buddy_data_science_system`
- **Mission:** data science capability research, practice, and controlled execution.
- **Inputs:** Curated data science resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-37 — data systems

- **Subsystem ID:** `buddy_data_systems_system`
- **Mission:** data systems capability research, practice, and controlled execution.
- **Inputs:** Curated data systems resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-38 — data validation

- **Subsystem ID:** `buddy_data_validation_system`
- **Mission:** data validation capability research, practice, and controlled execution.
- **Inputs:** Curated data validation resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-39 — database

- **Subsystem ID:** `buddy_database_system`
- **Mission:** database capability research, practice, and controlled execution.
- **Inputs:** Curated database resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-40 — databases

- **Subsystem ID:** `buddy_databases_system`
- **Mission:** databases capability research, practice, and controlled execution.
- **Inputs:** Curated databases resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-41 — deep learning

- **Subsystem ID:** `buddy_deep_learning_system`
- **Mission:** deep learning capability research, practice, and controlled execution.
- **Inputs:** Curated deep learning resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-42 — dependency security

- **Subsystem ID:** `buddy_dependency_security_system`
- **Mission:** dependency security capability research, practice, and controlled execution.
- **Inputs:** Curated dependency security resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-43 — event streaming

- **Subsystem ID:** `buddy_event_streaming_system`
- **Mission:** event streaming capability research, practice, and controlled execution.
- **Inputs:** Curated event streaming resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-44 — machine learning

- **Subsystem ID:** `buddy_machine_learning_system`
- **Mission:** machine learning capability research, practice, and controlled execution.
- **Inputs:** Curated machine learning resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-45 — mathematics

- **Subsystem ID:** `buddy_mathematics_system`
- **Mission:** mathematics capability research, practice, and controlled execution.
- **Inputs:** Curated mathematics resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-46 — meta-learning

- **Subsystem ID:** `buddy_meta_learning_system`
- **Mission:** meta-learning capability research, practice, and controlled execution.
- **Inputs:** Curated meta-learning resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-47 — open source

- **Subsystem ID:** `buddy_open_source_system`
- **Mission:** open source capability research, practice, and controlled execution.
- **Inputs:** Curated open source resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-48 — privacy

- **Subsystem ID:** `buddy_privacy_system`
- **Mission:** privacy capability research, practice, and controlled execution.
- **Inputs:** Curated privacy resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-49 — programming education

- **Subsystem ID:** `buddy_programming_education_system`
- **Mission:** programming education capability research, practice, and controlled execution.
- **Inputs:** Curated programming education resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-50 — reinforcement learning

- **Subsystem ID:** `buddy_reinforcement_learning_system`
- **Mission:** reinforcement learning capability research, practice, and controlled execution.
- **Inputs:** Curated reinforcement learning resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-51 — search

- **Subsystem ID:** `buddy_search_system`
- **Mission:** search capability research, practice, and controlled execution.
- **Inputs:** Curated search resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-52 — secure development

- **Subsystem ID:** `buddy_secure_development_system`
- **Mission:** secure development capability research, practice, and controlled execution.
- **Inputs:** Curated secure development resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-53 — security

- **Subsystem ID:** `buddy_security_system`
- **Mission:** security capability research, practice, and controlled execution.
- **Inputs:** Curated security resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-54 — security analysis

- **Subsystem ID:** `buddy_security_analysis_system`
- **Mission:** security analysis capability research, practice, and controlled execution.
- **Inputs:** Curated security analysis resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-55 — security controls

- **Subsystem ID:** `buddy_security_controls_system`
- **Mission:** security controls capability research, practice, and controlled execution.
- **Inputs:** Curated security controls resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-56 — security knowledge

- **Subsystem ID:** `buddy_security_knowledge_system`
- **Mission:** security knowledge capability research, practice, and controlled execution.
- **Inputs:** Curated security knowledge resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-57 — security taxonomy

- **Subsystem ID:** `buddy_security_taxonomy_system`
- **Mission:** security taxonomy capability research, practice, and controlled execution.
- **Inputs:** Curated security taxonomy resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-58 — software licensing

- **Subsystem ID:** `buddy_software_licensing_system`
- **Mission:** software licensing capability research, practice, and controlled execution.
- **Inputs:** Curated software licensing resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-59 — software security

- **Subsystem ID:** `buddy_software_security_system`
- **Mission:** software security capability research, practice, and controlled execution.
- **Inputs:** Curated software security resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-60 — software signing

- **Subsystem ID:** `buddy_software_signing_system`
- **Mission:** software signing capability research, practice, and controlled execution.
- **Inputs:** Curated software signing resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-61 — software supply chain

- **Subsystem ID:** `buddy_software_supply_chain_system`
- **Mission:** software supply chain capability research, practice, and controlled execution.
- **Inputs:** Curated software supply chain resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-62 — static analysis

- **Subsystem ID:** `buddy_static_analysis_system`
- **Mission:** static analysis capability research, practice, and controlled execution.
- **Inputs:** Curated static analysis resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-63 — statistics

- **Subsystem ID:** `buddy_statistics_system`
- **Mission:** statistics capability research, practice, and controlled execution.
- **Inputs:** Curated statistics resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-64 — systems

- **Subsystem ID:** `buddy_systems_system`
- **Mission:** systems capability research, practice, and controlled execution.
- **Inputs:** Curated systems resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-65 — systems/cloud

- **Subsystem ID:** `buddy_systems_cloud_system`
- **Mission:** systems/cloud capability research, practice, and controlled execution.
- **Inputs:** Curated systems/cloud resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-66 — technical education

- **Subsystem ID:** `buddy_technical_education_system`
- **Mission:** technical education capability research, practice, and controlled execution.
- **Inputs:** Curated technical education resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-67 — transformers

- **Subsystem ID:** `buddy_transformers_system`
- **Mission:** transformers capability research, practice, and controlled execution.
- **Inputs:** Curated transformers resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-68 — web development

- **Subsystem ID:** `buddy_web_development_system`
- **Mission:** web development capability research, practice, and controlled execution.
- **Inputs:** Curated web development resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-69 — web performance

- **Subsystem ID:** `buddy_web_performance_system`
- **Mission:** web performance capability research, practice, and controlled execution.
- **Inputs:** Curated web performance resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-70 — web security

- **Subsystem ID:** `buddy_web_security_system`
- **Mission:** web security capability research, practice, and controlled execution.
- **Inputs:** Curated web security resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-71 — workflow orchestration

- **Subsystem ID:** `buddy_workflow_orchestration_system`
- **Mission:** workflow orchestration capability research, practice, and controlled execution.
- **Inputs:** Curated workflow orchestration resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.


## AI model catalog category systems

Each category below has its own named Buddy subsystem boundary. These are **architecture specifications**, not claims that each subsystem is already implemented or running. Each subsystem must have its own registry identity, owner, interface, tests, telemetry, documentation, and evidence status. Shared platform services may be reused, but category ownership and acceptance criteria remain separate.

### MODEL-01 — General Chat

- **Subsystem ID:** `buddy_general_chat_system`
- **Mission:** General Chat capability research, practice, and controlled execution.
- **Inputs:** Curated General Chat resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### MODEL-02 — Coding

- **Subsystem ID:** `buddy_coding_system`
- **Mission:** Coding capability research, practice, and controlled execution.
- **Inputs:** Curated Coding resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### MODEL-03 — Research

- **Subsystem ID:** `buddy_research_system`
- **Mission:** Research capability research, practice, and controlled execution.
- **Inputs:** Curated Research resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### MODEL-04 — Writing & Content

- **Subsystem ID:** `buddy_writing_content_system`
- **Mission:** Writing & Content capability research, practice, and controlled execution.
- **Inputs:** Curated Writing & Content resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### MODEL-05 — Image Generation

- **Subsystem ID:** `buddy_image_generation_system`
- **Mission:** Image Generation capability research, practice, and controlled execution.
- **Inputs:** Curated Image Generation resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### MODEL-06 — Video & Audio

- **Subsystem ID:** `buddy_video_audio_system`
- **Mission:** Video & Audio capability research, practice, and controlled execution.
- **Inputs:** Curated Video & Audio resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### MODEL-07 — Business & CRM

- **Subsystem ID:** `buddy_business_crm_system`
- **Mission:** Business & CRM capability research, practice, and controlled execution.
- **Inputs:** Curated Business & CRM resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### MODEL-08 — Data & Analytics

- **Subsystem ID:** `buddy_data_analytics_system`
- **Mission:** Data & Analytics capability research, practice, and controlled execution.
- **Inputs:** Curated Data & Analytics resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### MODEL-09 — Autonomous Agents

- **Subsystem ID:** `buddy_autonomous_agents_system`
- **Mission:** Autonomous Agents capability research, practice, and controlled execution.
- **Inputs:** Curated Autonomous Agents resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### MODEL-10 — Customer Support

- **Subsystem ID:** `buddy_customer_support_system`
- **Mission:** Customer Support capability research, practice, and controlled execution.
- **Inputs:** Curated Customer Support resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### MODEL-11 — Marketing & SEO

- **Subsystem ID:** `buddy_marketing_seo_system`
- **Mission:** Marketing & SEO capability research, practice, and controlled execution.
- **Inputs:** Curated Marketing & SEO resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### MODEL-12 — Finance & Trading

- **Subsystem ID:** `buddy_finance_trading_system`
- **Mission:** Finance & Trading capability research, practice, and controlled execution.
- **Inputs:** Curated Finance & Trading resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### MODEL-13 — Healthcare AI

- **Subsystem ID:** `buddy_healthcare_ai_system`
- **Mission:** Healthcare AI capability research, practice, and controlled execution.
- **Inputs:** Curated Healthcare AI resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### MODEL-14 — Legal & Compliance

- **Subsystem ID:** `buddy_legal_compliance_system`
- **Mission:** Legal & Compliance capability research, practice, and controlled execution.
- **Inputs:** Curated Legal & Compliance resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### MODEL-15 — Education

- **Subsystem ID:** `buddy_education_system`
- **Mission:** Education capability research, practice, and controlled execution.
- **Inputs:** Curated Education resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### MODEL-16 — Voice & Speech

- **Subsystem ID:** `buddy_voice_speech_system`
- **Mission:** Voice & Speech capability research, practice, and controlled execution.
- **Inputs:** Curated Voice & Speech resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### MODEL-17 — Translation

- **Subsystem ID:** `buddy_translation_system`
- **Mission:** Translation capability research, practice, and controlled execution.
- **Inputs:** Curated Translation resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### MODEL-18 — Robotics & IoT

- **Subsystem ID:** `buddy_robotics_iot_system`
- **Mission:** Robotics & IoT capability research, practice, and controlled execution.
- **Inputs:** Curated Robotics & IoT resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### MODEL-19 — Security

- **Subsystem ID:** `buddy_security_system`
- **Mission:** Security capability research, practice, and controlled execution.
- **Inputs:** Curated Security resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### MODEL-20 — No-Code/Low-Code

- **Subsystem ID:** `buddy_no_code_low_code_system`
- **Mission:** No-Code/Low-Code capability research, practice, and controlled execution.
- **Inputs:** Curated No-Code/Low-Code resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.


## 8.1 Required subsystem contract for every category

Every subsystem must eventually have a machine-readable record with:

1. Stable category ID and exact source label.
2. Dedicated purpose, owner lane, and accountable reviewer.
3. Input/output schema and versioned interface.
4. Resource and source provenance, including license/terms.
5. Permission boundary, secrets references (never secret values), budget limit, and emergency-stop behavior where execution is possible.
6. Unit and integration tests, category-specific benchmark/checklist, and regression tests.
7. Operational metrics, structured logs, failure handling, and Command Center visibility.
8. Evidence status using the six lifecycle values already defined in this document.
9. Dependencies and explicit links to other category systems; dependencies do not transfer ownership.
10. A documented retirement/migration process so categories are never silently deleted.

## 8.2 Category isolation and collaboration rules

- Each category owns its backlog, acceptance criteria, evidence ledger, and health status.
- Shared services (identity, policy, storage, event bus, model router, observability, and UI shell) are infrastructure only; they do not erase category boundaries.
- Cross-category workflows must declare their participating subsystem IDs, data contracts, permission checks, and failure/rollback behavior.
- Research-only categories must not gain execution permissions merely because an execution subsystem exists elsewhere.
- No subsystem may mark another subsystem verified on its behalf.
- Dashboard rollups must preserve per-category detail and show blocked, stale, unowned, or unverified states instead of hiding them.

## 8.3 Implementation sequence

1. Generate and validate the 12 registry-category subsystem records from the authoritative resource registry.
2. Generate 70 study-category subsystem records while preserving exact labels and the 94 source resource rows.
3. Generate 20 model-category subsystem records from the model catalog source.
4. Add dedicated schemas, tests, owner mapping, and dashboard panels in small reviewable changes.
5. Only then extend the same pattern to bot divisions, individual bots, sibling repositories, and any additional categories found in the full repository audit.

**Scope/evidence warning:** these sections define independent subsystem contracts and intended boundaries. They do not claim that 102 separate executable systems, APIs, agents, dashboards, or tests have already been built. Their implementation must proceed incrementally through evidence-gated PRs.


## 9. Machine-readable category-system registry and validation

The dedicated subsystem specifications are also stored in `config/buddy/category-system-registry.json`, schema `dreamco.buddy.category_system_registry.v1`. This file contains one record per category, with a stable subsystem ID, exact source label, source references, contract fields, lifecycle status, implementation status, and verification status. The catalog currently defines 103 records: 12 resource-registry categories, 71 study-resource categories, and 20 model categories.

Run `npm run buddy:category-systems` to validate the category-system registry against the authoritative source catalogs. The validator checks category completeness, source-row mapping, model category counts, unique subsystem IDs, required contract fields, lifecycle values, and summary counts. The test is `tests/test_buddy_category_system_registry.py`.

The validator is now committed in this feature branch. Its execution in the repository's full CI environment remains pending; a source-file re-fetch and static consistency checks are not a substitute for a successful test run.
