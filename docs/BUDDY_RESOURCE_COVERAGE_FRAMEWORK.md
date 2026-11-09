# Buddy Resource Coverage Framework

**Status:** `catalogued` documentation framework  
**Primary repository:** `DreamCo-Technologies/Dreamcobots`  
**Purpose:** Ensure Buddy research, learning, engineering, benchmarking, and reporting cover the full DreamCo resource landscape—not only embodied AI.

## Authority and freshness

This document is a coverage crosswalk, not a replacement for the machine-readable registries.

- Resource inventory authority: `config/buddy/resource-registry.json` (`dreamco.buddy.resource_registry.v1`).
- Resource-map explanation: `docs/BUDDY_RESOURCE_MAP.md`.
- Study-resource catalogs: discovered dynamically from `config/buddy-study-resources-*.json`; the file list shown below is a dated documentation snapshot, not a closed source list.
- Model category source inspected: `shared/ai-models.ts` (`AI_MODEL_CATEGORIES`).
- Project constraints and evidence rules: `docs/DREAMCO_BUDDY_MASTER_CODEX_DIRECTIVE.md`.

The resource map says its last scan was **2026-10-05**. Treat its connection states and counts as a dated inventory snapshot, not live verification. Re-scan before reporting a provider, secret, workflow, deployment, license, or integration as currently available. The `101-200` set and the other study catalogs are dated source snapshots. Current row, resource-ID, and category counts are derived by the validator from every discovered source file; no category or item count is a permanent limit. Continue scanning for additional resource catalogs.

## 1. Current machine-readable resource-registry categories

The current inspected registry contains resource records across its dynamically derived categories:

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

The following section is a snapshot of the study-resource category labels discovered in the inspected catalogs. Preserve every exact source label; similar labels are separate systems until an explicit, reviewed alias decision is recorded. New labels must be added automatically by the registry builder and must never be rejected because a previous count was reached.

- 3D learning environments
- AI
- AI applications
- AI coding
- AI education
- AI engineering
- AI evaluation
- AI feedback
- AI gateway
- AI governance
- AI inference
- AI interface
- AI observability
- AI orchestration
- AI performance
- AI quality testing
- AI research
- AI safety
- AI tooling
- AI video learning
- AI web apps
- AI/ML
- AI/cloud
- API design
- API development
- API engineering
- API invocation
- API security
- API standards
- API testing
- API-use evaluation
- Apple ML
- Apple Silicon AI
- Apple development
- Apple train
- C++ testing
- CI/CD
- CS curriculum
- CS education
- CS roadmap
- DevOps
- FT toolkit
- GPU/AI
- GitOps
- HCI
- HTTP
- HTTP standards
- Java backend
- Java testing
- JavaScript
- JavaScript runtime
- JavaScript standards
- JavaScript tooling
- Kubernetes
- LLM applications
- LLM engineering
- LLM evaluation
- LLM evaluation infrastructure
- LLM inference
- LLM observability
- LLM serving
- LLM testing
- Linux/security
- LoRA
- ML
- ML education
- ML engineering
- ML experiments
- ML lifecycle
- ML orchestration
- ML pedagogy
- ML practice
- ML research
- ML systems
- MLOps
- NLP
- NLP literature
- Node.js
- Python
- Python coding
- Python ecosystem
- Python testing
- Python web
- RAG
- RAG evaluation
- RAG/program
- RAG/search
- RL datasets
- RL environments
- RL research
- RLHF
- SQL
- SQL practice
- TLS
- TLS security
- US base
- US open weights
- abstract reasoning
- agent evaluation
- agent security
- agent state
- agent teams
- agents
- agents/automation
- algorithms
- alignment
- analytics
- analytics engineering
- application agents
- application monitoring
- application security
- architecture
- attack patterns
- authentication
- automation
- backend
- backend architecture
- benchmark tracking
- binary-feedback optimization
- browser agents
- browser automation
- browser engineering
- browser testing
- caching
- cleaned web corpus
- cloud
- cloud native
- cloud native education
- cloud/software
- code data
- code eval
- code language modeling
- code modeling
- code models
- code quality
- code-specialized modeling
- code-text retrieval
- coder student
- coding
- coding agents
- community
- competitive programming
- compiler optimization
- compiler systems
- complex instruction following
- computational linguistics
- computer architecture
- computer science
- computer security
- computer vision
- computer vision research
- computer-use agents
- consensus
- containers
- context
- cross-language
- cryptography
- cybersecurity
- data
- data analysis
- data caution
- data engineering
- data eval
- data format
- data science
- data structures
- data systems
- data validation
- data/ML
- data/model versioning
- database
- database systems
- database/cache
- databases
- deep learning
- deep learning practice
- deep reinforcement learning
- deep-learning research
- deep-learning textbook
- defensive security
- dependency security
- development
- direct preference optimization
- distributed AI
- distributed SQL
- distributed data
- distributed database
- distributed systems
- distributed training
- diverse language-model corpus composition
- education
- educational web data
- efficiency
- efficient FT
- efficient fine-tuning
- efficient learning
- efficient transformers
- embeddings
- encyclopedic text
- engineering
- enterprise browser agents
- enterprise catalog
- environments
- eval
- eval harness
- evaluation
- event streaming
- experiment tracking
- frontend
- frontier teacher
- game AI
- general assistants
- generalization
- graph databases
- graph reasoning
- group-relative optimization
- holistic evaluation
- hosted catalog
- hosted infer
- hosted run
- hub
- identity
- identity preference optimization
- image building
- incident response
- inference benchmarking
- inference optimization
- information retrieval
- infra
- infrastructure as code
- infrastructure programming
- instruction evolution
- instruction tuning
- instruction-following evaluation
- interactive tool reasoning
- internet standards
- iterative refinement
- language modeling
- language research
- language-model internals
- language-model training
- large artifacts
- large-model training
- licenses
- load balancing
- local AI
- local UX
- local infer
- local models
- local packs
- long-form language
- machine learning
- machine-learning research
- math programming
- mathematics
- meta-learning
- methods
- mobile agents
- model gateway
- model post-training
- model routing
- model storage
- model/data ecosystem
- modular reasoning
- multi-agent AI
- multi-agent RL
- multi-turn evaluation
- natural language processing
- network analysis
- networking
- networking/security
- news
- numerical computing
- observability
- occupations
- odds-ratio preference optimization
- on-device AI
- on-device ML
- open US stack
- open code corpus
- open conversational data
- open model research
- open source
- operating systems
- ops
- orchestration
- parallel computing
- parameter-efficient learning
- peer hub
- planned tool execution
- policy
- post-training
- pretrain data
- principle-guided self-critique
- privacy
- problem decomposition
- production ML
- program-aided reasoning
- program-assisted reasoning
- programmatic AI
- programming
- programming education
- proximal policy optimization
- proxy
- quant
- quantization
- real-time communications
- real-time web
- reason eval
- reasoning
- reasoning aggregation
- reasoning environments
- reasoning plans
- reasoning plus acting
- reasoning search
- reinforcement learning
- research
- research graphs
- research hub
- research index
- research literature
- research org
- reverse proxy
- router catalog
- safety methods
- safety ops
- safety org
- scale train
- search
- secrets management
- secure SDLC
- secure development
- security
- security analysis
- security controls
- security education
- security knowledge
- security research
- security taxonomy
- self-supervised tool use
- serve
- service mesh
- service networking
- serving
- serving efficiency
- shell
- small instruction dataset
- software education
- software engineering
- software licensing
- software security
- software signing
- software supply chain
- speech AI
- stateful tool agents
- static analysis
- statistics
- stream processing
- structured generation
- structured outputs
- subquestion decomposition
- synthetic dialogue
- synthetic instruction generation
- synthetic instruction synthesis
- systems
- systems engineering
- systems/cloud
- technical Q&A
- technical education
- test
- tokenization
- tokens
- tool agents
- tool use
- tool-assisted critique
- tool-augmented QA
- tools
- train
- training
- transformer concepts
- transformer research
- transformers
- transparent language-model corpus
- unsupervised learning
- vectors
- verbal reinforcement
- verifiable instruction following
- version control
- visual browser agents
- visual web interaction
- visualization
- web
- web agents
- web development
- web dialogue agents
- web framework
- web performance
- web security
- web server
- web standards
- web-agent trajectories
- workflow orchestration
- zero trust

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
- all currently discovered study-resource rows represented, preserving every distinct source label;
- all 20 AI model categories represented;
- every new research item tagged to at least one category and one Buddy capability or explicit “monitor only” disposition.

**Current limitation:** this document records the categories observed in the inspected source files. It does not claim that every repository, every Markdown file, every division, every bot, every external resource, or every sibling-repository asset has already been audited. Expand the crosswalk as those authoritative inventories are inspected.



# 8. Dedicated category sections and Buddy subsystem boundaries

The requirement is one category → one section → one separately accountable subsystem. No category below is merely a tag under a broad umbrella. Similar categories may share infrastructure, but they must not be collapsed into one registry identity, backlog, test suite, or status. For example, `database` and `databases` remain distinct source labels until an explicit, reviewed alias decision is recorded.


## Registry-category systems

Each category below has its own named Buddy subsystem boundary. These are **architecture specifications**, not claims that each subsystem is already implemented or running. Each subsystem must have its own registry identity, owner, interface, tests, telemetry, documentation, and evidence status. Shared platform services may be reused, but category ownership and acceptance criteria remain separate.

### REG-01 — benchmark

- **Subsystem ID:** `registry_benchmark`
- **Mission:** Evaluation and certification.
- **Inputs:** Versioned tasks, datasets, baselines, scoring rubrics, run artifacts.
- **Outputs:** Comparable scores, pass/fail gates, regression reports.
- **Control and measures:** Reproducibility, validity, coverage, false-pass rate. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### REG-02 — code

- **Subsystem ID:** `registry_code`
- **Mission:** Reusable software and repository assets.
- **Inputs:** Source files, dependency manifests, ownership, licenses, tests.
- **Outputs:** Reviewed code modules, integration proposals, SBOM and test evidence.
- **Control and measures:** Test pass rate, vulnerabilities, maintainability, license compliance. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### REG-03 — compute

- **Subsystem ID:** `registry_compute`
- **Mission:** Execution capacity and runtime environments.
- **Inputs:** Runner inventory, workload profile, budgets, secrets references.
- **Outputs:** Scheduled or on-demand execution with resource and cost telemetry.
- **Control and measures:** Availability, queue time, latency, utilization, spend. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### REG-04 — dataset

- **Subsystem ID:** `registry_dataset`
- **Mission:** Governed learning and evaluation data.
- **Inputs:** Dataset metadata, provenance, license, schema, splits, consent/terms.
- **Outputs:** Validated, versioned datasets and data cards.
- **Control and measures:** Coverage, quality, leakage, freshness, license compliance. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### REG-05 — github_platform

- **Subsystem ID:** `registry_github_platform`
- **Mission:** GitHub platform capabilities and permission boundaries.
- **Inputs:** API scopes, app installation state, org settings, audit events.
- **Outputs:** Least-privilege integration plan and verified platform actions.
- **Control and measures:** Permission coverage, action success, auditability, scope violations. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### REG-06 — model_catalog

- **Subsystem ID:** `registry_model_catalog`
- **Mission:** Model discovery and capability metadata.
- **Inputs:** Provider/model identifiers, versions, context limits, modalities, terms.
- **Outputs:** Searchable model cards and eligibility decisions.
- **Control and measures:** Metadata freshness, route suitability, evaluation coverage. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### REG-07 — model_provider

- **Subsystem ID:** `registry_model_provider`
- **Mission:** Governed access to external or local inference providers.
- **Inputs:** Adapter contracts, runtime health, secret references, policy and terms.
- **Outputs:** Approved inference calls, normalized responses, usage/cost records.
- **Control and measures:** Availability, latency, quality, cost, policy compliance. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### REG-08 — repo_tool

- **Subsystem ID:** `registry_repo_tool`
- **Mission:** Developer, learning, retrieval, and training utilities.
- **Inputs:** Tool contracts, code, dependencies, CLI/API inputs, tests.
- **Outputs:** Versioned tool outputs and reproducible execution artifacts.
- **Control and measures:** Correctness, reliability, test coverage, runtime and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### REG-09 — secret_inventory

- **Subsystem ID:** `registry_secret_inventory`
- **Mission:** Secret lifecycle and access governance.
- **Inputs:** Secret names, owning service, vault reference, rotation metadata (never values).
- **Outputs:** Presence/health attestations and remediation tasks.
- **Control and measures:** Exposure incidents, rotation age, least privilege, missing-secret rate. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### REG-10 — surface

- **Subsystem ID:** `registry_surface`
- **Mission:** User-facing and operator-facing product surfaces.
- **Inputs:** Page/app routes, content data, auth policy, telemetry, accessibility checks.
- **Outputs:** Published, traceable views of verified system state.
- **Control and measures:** Uptime, accessibility, freshness, broken links, user task success. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### REG-11 — terms_constraint

- **Subsystem ID:** `registry_terms_constraint`
- **Mission:** Legal, contractual, and licensing guardrails.
- **Inputs:** Provider terms, OSS licenses, dataset permissions, usage restrictions.
- **Outputs:** Allow/deny decisions and documented compliance conditions.
- **Control and measures:** Unapproved use count, license coverage, policy exceptions. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### REG-12 — workforce

- **Subsystem ID:** `registry_workforce`
- **Mission:** Human and specialist-agent ownership model.
- **Inputs:** Capability lanes, owners, responsibilities, permissions, escalation paths.
- **Outputs:** Assigned work, review evidence, handoffs, accountability records.
- **Control and measures:** Ownership coverage, review latency, completion quality, escalation rate. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.


## Study-resource category systems

Each category below has its own named Buddy subsystem boundary. These are **architecture specifications**, not claims that each subsystem is already implemented or running. Each subsystem must have its own registry identity, owner, interface, tests, telemetry, documentation, and evidence status. Shared platform services may be reused, but category ownership and acceptance criteria remain separate.

### STUDY-01 — AI

- **Subsystem ID:** `study_ai`
- **Mission:** AI capability research, practice, and controlled execution.
- **Inputs:** Curated AI resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-02 — AI education

- **Subsystem ID:** `study_ai_education`
- **Mission:** AI education capability research, practice, and controlled execution.
- **Inputs:** Curated AI education resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-03 — AI engineering

- **Subsystem ID:** `study_ai_engineering`
- **Mission:** AI engineering capability research, practice, and controlled execution.
- **Inputs:** Curated AI engineering resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-04 — AI governance

- **Subsystem ID:** `study_ai_governance`
- **Mission:** AI governance capability research, practice, and controlled execution.
- **Inputs:** Curated AI governance resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-05 — API design

- **Subsystem ID:** `study_api_design`
- **Mission:** API design capability research, practice, and controlled execution.
- **Inputs:** Curated API design resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-06 — API development

- **Subsystem ID:** `study_api_development`
- **Mission:** API development capability research, practice, and controlled execution.
- **Inputs:** Curated API development resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-07 — API engineering

- **Subsystem ID:** `study_api_engineering`
- **Mission:** API engineering capability research, practice, and controlled execution.
- **Inputs:** Curated API engineering resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-08 — API standards

- **Subsystem ID:** `study_api_standards`
- **Mission:** API standards capability research, practice, and controlled execution.
- **Inputs:** Curated API standards resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-09 — API testing

- **Subsystem ID:** `study_api_testing`
- **Mission:** API testing capability research, practice, and controlled execution.
- **Inputs:** Curated API testing resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-10 — C++ testing

- **Subsystem ID:** `study_c_testing`
- **Mission:** C++ testing capability research, practice, and controlled execution.
- **Inputs:** Curated C++ testing resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-11 — CS education

- **Subsystem ID:** `study_cs_education`
- **Mission:** CS education capability research, practice, and controlled execution.
- **Inputs:** Curated CS education resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-12 — Java testing

- **Subsystem ID:** `study_java_testing`
- **Mission:** Java testing capability research, practice, and controlled execution.
- **Inputs:** Curated Java testing resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-13 — JavaScript runtime

- **Subsystem ID:** `study_javascript_runtime`
- **Mission:** JavaScript runtime capability research, practice, and controlled execution.
- **Inputs:** Curated JavaScript runtime resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-14 — ML education

- **Subsystem ID:** `study_ml_education`
- **Mission:** ML education capability research, practice, and controlled execution.
- **Inputs:** Curated ML education resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-15 — ML practice

- **Subsystem ID:** `study_ml_practice`
- **Mission:** ML practice capability research, practice, and controlled execution.
- **Inputs:** Curated ML practice resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-16 — NLP

- **Subsystem ID:** `study_nlp`
- **Mission:** NLP capability research, practice, and controlled execution.
- **Inputs:** Curated NLP resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-17 — Node.js

- **Subsystem ID:** `study_node_js`
- **Mission:** Node.js capability research, practice, and controlled execution.
- **Inputs:** Curated Node.js resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-18 — Python

- **Subsystem ID:** `study_python`
- **Mission:** Python capability research, practice, and controlled execution.
- **Inputs:** Curated Python resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-19 — Python testing

- **Subsystem ID:** `study_python_testing`
- **Mission:** Python testing capability research, practice, and controlled execution.
- **Inputs:** Curated Python testing resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-20 — TLS

- **Subsystem ID:** `study_tls`
- **Mission:** TLS capability research, practice, and controlled execution.
- **Inputs:** Curated TLS resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-21 — TLS security

- **Subsystem ID:** `study_tls_security`
- **Mission:** TLS security capability research, practice, and controlled execution.
- **Inputs:** Curated TLS security resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-22 — algorithms

- **Subsystem ID:** `study_algorithms`
- **Mission:** algorithms capability research, practice, and controlled execution.
- **Inputs:** Curated algorithms resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-23 — analytics

- **Subsystem ID:** `study_analytics`
- **Mission:** analytics capability research, practice, and controlled execution.
- **Inputs:** Curated analytics resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-24 — analytics engineering

- **Subsystem ID:** `study_analytics_engineering`
- **Mission:** analytics engineering capability research, practice, and controlled execution.
- **Inputs:** Curated analytics engineering resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-25 — application monitoring

- **Subsystem ID:** `study_application_monitoring`
- **Mission:** application monitoring capability research, practice, and controlled execution.
- **Inputs:** Curated application monitoring resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-26 — backend

- **Subsystem ID:** `study_backend`
- **Mission:** backend capability research, practice, and controlled execution.
- **Inputs:** Curated backend resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-27 — backend architecture

- **Subsystem ID:** `study_backend_architecture`
- **Mission:** backend architecture capability research, practice, and controlled execution.
- **Inputs:** Curated backend architecture resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-28 — browser automation

- **Subsystem ID:** `study_browser_automation`
- **Mission:** browser automation capability research, practice, and controlled execution.
- **Inputs:** Curated browser automation resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-29 — browser engineering

- **Subsystem ID:** `study_browser_engineering`
- **Mission:** browser engineering capability research, practice, and controlled execution.
- **Inputs:** Curated browser engineering resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-30 — browser testing

- **Subsystem ID:** `study_browser_testing`
- **Mission:** browser testing capability research, practice, and controlled execution.
- **Inputs:** Curated browser testing resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-31 — cloud native education

- **Subsystem ID:** `study_cloud_native_education`
- **Mission:** cloud native education capability research, practice, and controlled execution.
- **Inputs:** Curated cloud native education resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-32 — code quality

- **Subsystem ID:** `study_code_quality`
- **Mission:** code quality capability research, practice, and controlled execution.
- **Inputs:** Curated code quality resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-33 — computer vision

- **Subsystem ID:** `study_computer_vision`
- **Mission:** computer vision capability research, practice, and controlled execution.
- **Inputs:** Curated computer vision resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-34 — data engineering

- **Subsystem ID:** `study_data_engineering`
- **Mission:** data engineering capability research, practice, and controlled execution.
- **Inputs:** Curated data engineering resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-35 — data format

- **Subsystem ID:** `study_data_format`
- **Mission:** data format capability research, practice, and controlled execution.
- **Inputs:** Curated data format resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-36 — data science

- **Subsystem ID:** `study_data_science`
- **Mission:** data science capability research, practice, and controlled execution.
- **Inputs:** Curated data science resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-37 — data systems

- **Subsystem ID:** `study_data_systems`
- **Mission:** data systems capability research, practice, and controlled execution.
- **Inputs:** Curated data systems resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-38 — data validation

- **Subsystem ID:** `study_data_validation`
- **Mission:** data validation capability research, practice, and controlled execution.
- **Inputs:** Curated data validation resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-39 — database

- **Subsystem ID:** `study_database`
- **Mission:** database capability research, practice, and controlled execution.
- **Inputs:** Curated database resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-40 — databases

- **Subsystem ID:** `study_databases`
- **Mission:** databases capability research, practice, and controlled execution.
- **Inputs:** Curated databases resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-41 — deep learning

- **Subsystem ID:** `study_deep_learning`
- **Mission:** deep learning capability research, practice, and controlled execution.
- **Inputs:** Curated deep learning resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-42 — dependency security

- **Subsystem ID:** `study_dependency_security`
- **Mission:** dependency security capability research, practice, and controlled execution.
- **Inputs:** Curated dependency security resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-43 — event streaming

- **Subsystem ID:** `study_event_streaming`
- **Mission:** event streaming capability research, practice, and controlled execution.
- **Inputs:** Curated event streaming resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-44 — machine learning

- **Subsystem ID:** `study_machine_learning`
- **Mission:** machine learning capability research, practice, and controlled execution.
- **Inputs:** Curated machine learning resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-45 — mathematics

- **Subsystem ID:** `study_mathematics`
- **Mission:** mathematics capability research, practice, and controlled execution.
- **Inputs:** Curated mathematics resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-46 — meta-learning

- **Subsystem ID:** `study_meta_learning`
- **Mission:** meta-learning capability research, practice, and controlled execution.
- **Inputs:** Curated meta-learning resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-47 — open source

- **Subsystem ID:** `study_open_source`
- **Mission:** open source capability research, practice, and controlled execution.
- **Inputs:** Curated open source resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-48 — privacy

- **Subsystem ID:** `study_privacy`
- **Mission:** privacy capability research, practice, and controlled execution.
- **Inputs:** Curated privacy resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-49 — programming education

- **Subsystem ID:** `study_programming_education`
- **Mission:** programming education capability research, practice, and controlled execution.
- **Inputs:** Curated programming education resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-50 — reinforcement learning

- **Subsystem ID:** `study_reinforcement_learning`
- **Mission:** reinforcement learning capability research, practice, and controlled execution.
- **Inputs:** Curated reinforcement learning resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-51 — search

- **Subsystem ID:** `study_search`
- **Mission:** search capability research, practice, and controlled execution.
- **Inputs:** Curated search resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-52 — secure development

- **Subsystem ID:** `study_secure_development`
- **Mission:** secure development capability research, practice, and controlled execution.
- **Inputs:** Curated secure development resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-53 — security

- **Subsystem ID:** `study_security`
- **Mission:** security capability research, practice, and controlled execution.
- **Inputs:** Curated security resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-54 — security analysis

- **Subsystem ID:** `study_security_analysis`
- **Mission:** security analysis capability research, practice, and controlled execution.
- **Inputs:** Curated security analysis resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-55 — security controls

- **Subsystem ID:** `study_security_controls`
- **Mission:** security controls capability research, practice, and controlled execution.
- **Inputs:** Curated security controls resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-56 — security knowledge

- **Subsystem ID:** `study_security_knowledge`
- **Mission:** security knowledge capability research, practice, and controlled execution.
- **Inputs:** Curated security knowledge resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-57 — security taxonomy

- **Subsystem ID:** `study_security_taxonomy`
- **Mission:** security taxonomy capability research, practice, and controlled execution.
- **Inputs:** Curated security taxonomy resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-58 — software licensing

- **Subsystem ID:** `study_software_licensing`
- **Mission:** software licensing capability research, practice, and controlled execution.
- **Inputs:** Curated software licensing resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-59 — software security

- **Subsystem ID:** `study_software_security`
- **Mission:** software security capability research, practice, and controlled execution.
- **Inputs:** Curated software security resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-60 — software signing

- **Subsystem ID:** `study_software_signing`
- **Mission:** software signing capability research, practice, and controlled execution.
- **Inputs:** Curated software signing resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-61 — software supply chain

- **Subsystem ID:** `study_software_supply_chain`
- **Mission:** software supply chain capability research, practice, and controlled execution.
- **Inputs:** Curated software supply chain resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-62 — static analysis

- **Subsystem ID:** `study_static_analysis`
- **Mission:** static analysis capability research, practice, and controlled execution.
- **Inputs:** Curated static analysis resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-63 — statistics

- **Subsystem ID:** `study_statistics`
- **Mission:** statistics capability research, practice, and controlled execution.
- **Inputs:** Curated statistics resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-64 — systems

- **Subsystem ID:** `study_systems`
- **Mission:** systems capability research, practice, and controlled execution.
- **Inputs:** Curated systems resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-65 — systems/cloud

- **Subsystem ID:** `study_systems_cloud`
- **Mission:** systems/cloud capability research, practice, and controlled execution.
- **Inputs:** Curated systems/cloud resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-66 — technical education

- **Subsystem ID:** `study_technical_education`
- **Mission:** technical education capability research, practice, and controlled execution.
- **Inputs:** Curated technical education resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-67 — transformers

- **Subsystem ID:** `study_transformers`
- **Mission:** transformers capability research, practice, and controlled execution.
- **Inputs:** Curated transformers resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-68 — web development

- **Subsystem ID:** `study_web_development`
- **Mission:** web development capability research, practice, and controlled execution.
- **Inputs:** Curated web development resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-69 — web performance

- **Subsystem ID:** `study_web_performance`
- **Mission:** web performance capability research, practice, and controlled execution.
- **Inputs:** Curated web performance resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-70 — web security

- **Subsystem ID:** `study_web_security`
- **Mission:** web security capability research, practice, and controlled execution.
- **Inputs:** Curated web security resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### STUDY-71 — workflow orchestration

- **Subsystem ID:** `study_workflow_orchestration`
- **Mission:** workflow orchestration capability research, practice, and controlled execution.
- **Inputs:** Curated workflow orchestration resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.


## AI model catalog category systems

Each category below has its own named Buddy subsystem boundary. These are **architecture specifications**, not claims that each subsystem is already implemented or running. Each subsystem must have its own registry identity, owner, interface, tests, telemetry, documentation, and evidence status. Shared platform services may be reused, but category ownership and acceptance criteria remain separate.

### MODEL-01 — General Chat

- **Subsystem ID:** `model_general_chat`
- **Mission:** General Chat capability research, practice, and controlled execution.
- **Inputs:** Curated General Chat resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### MODEL-02 — Coding

- **Subsystem ID:** `model_coding`
- **Mission:** Coding capability research, practice, and controlled execution.
- **Inputs:** Curated Coding resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### MODEL-03 — Research

- **Subsystem ID:** `model_research`
- **Mission:** Research capability research, practice, and controlled execution.
- **Inputs:** Curated Research resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### MODEL-04 — Writing & Content

- **Subsystem ID:** `model_writing_content`
- **Mission:** Writing & Content capability research, practice, and controlled execution.
- **Inputs:** Curated Writing & Content resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### MODEL-05 — Image Generation

- **Subsystem ID:** `model_image_generation`
- **Mission:** Image Generation capability research, practice, and controlled execution.
- **Inputs:** Curated Image Generation resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### MODEL-06 — Video & Audio

- **Subsystem ID:** `model_video_audio`
- **Mission:** Video & Audio capability research, practice, and controlled execution.
- **Inputs:** Curated Video & Audio resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### MODEL-07 — Business & CRM

- **Subsystem ID:** `model_business_crm`
- **Mission:** Business & CRM capability research, practice, and controlled execution.
- **Inputs:** Curated Business & CRM resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### MODEL-08 — Data & Analytics

- **Subsystem ID:** `model_data_analytics`
- **Mission:** Data & Analytics capability research, practice, and controlled execution.
- **Inputs:** Curated Data & Analytics resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### MODEL-09 — Autonomous Agents

- **Subsystem ID:** `model_autonomous_agents`
- **Mission:** Autonomous Agents capability research, practice, and controlled execution.
- **Inputs:** Curated Autonomous Agents resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### MODEL-10 — Customer Support

- **Subsystem ID:** `model_customer_support`
- **Mission:** Customer Support capability research, practice, and controlled execution.
- **Inputs:** Curated Customer Support resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### MODEL-11 — Marketing & SEO

- **Subsystem ID:** `model_marketing_seo`
- **Mission:** Marketing & SEO capability research, practice, and controlled execution.
- **Inputs:** Curated Marketing & SEO resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### MODEL-12 — Finance & Trading

- **Subsystem ID:** `model_finance_trading`
- **Mission:** Finance & Trading capability research, practice, and controlled execution.
- **Inputs:** Curated Finance & Trading resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### MODEL-13 — Healthcare AI

- **Subsystem ID:** `model_healthcare_ai`
- **Mission:** Healthcare AI capability research, practice, and controlled execution.
- **Inputs:** Curated Healthcare AI resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### MODEL-14 — Legal & Compliance

- **Subsystem ID:** `model_legal_compliance`
- **Mission:** Legal & Compliance capability research, practice, and controlled execution.
- **Inputs:** Curated Legal & Compliance resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### MODEL-15 — Education

- **Subsystem ID:** `model_education`
- **Mission:** Education capability research, practice, and controlled execution.
- **Inputs:** Curated Education resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### MODEL-16 — Voice & Speech

- **Subsystem ID:** `model_voice_speech`
- **Mission:** Voice & Speech capability research, practice, and controlled execution.
- **Inputs:** Curated Voice & Speech resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### MODEL-17 — Translation

- **Subsystem ID:** `model_translation`
- **Mission:** Translation capability research, practice, and controlled execution.
- **Inputs:** Curated Translation resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### MODEL-18 — Robotics & IoT

- **Subsystem ID:** `model_robotics_iot`
- **Mission:** Robotics & IoT capability research, practice, and controlled execution.
- **Inputs:** Curated Robotics & IoT resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### MODEL-19 — Security

- **Subsystem ID:** `model_security`
- **Mission:** Security capability research, practice, and controlled execution.
- **Inputs:** Curated Security resources, task definitions, versioned references, constraints, and evaluation examples.
- **Outputs:** Category-specific knowledge records, validated artifacts, experiment results, and actionable recommendations.
- **Control and measures:** Correctness, coverage, reproducibility, safety/compliance, freshness, and cost. Enforce access policy, provenance, human approval for consequential side effects, and a visible failure state.
- **Acceptance gate:** a category-specific contract, owner, unit/integration tests, benchmark or checklist, documented failure modes, and evidence links must exist before the subsystem advances beyond `catalogued`.

### MODEL-20 — No-Code/Low-Code

- **Subsystem ID:** `model_no_code_low_code`
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
2. Generate one study-category subsystem for every exact label found in all discovered study-resource catalogs, preserving every source resource row.
3. Generate 20 model-category subsystem records from the model catalog source.
4. Add dedicated schemas, tests, owner mapping, and dashboard panels in small reviewable changes.
5. Only then extend the same pattern to bot divisions, individual bots, sibling repositories, and any additional categories found in the full repository audit.

**Scope/evidence warning:** these sections define independent subsystem contracts and intended boundaries. They do not claim that 102 separate executable systems, APIs, agents, dashboards, or tests have already been built. Their implementation must proceed incrementally through evidence-gated PRs.


## 9. Machine-readable category-system registry and validation

The dedicated subsystem specifications are also stored in `config/buddy/category-system-registry.json`, schema `dreamco.buddy.category_system_registry.v1`. This file contains one record per category, with a stable subsystem ID, exact source label, source references, contract fields, lifecycle status, implementation status, and verification status. The current catalog record count and category breakdown are derived by the validator from the live resource registry, all matching study-resource files, model records, and the current division registry. Historical division inventories disagree; the validator computes unmatched division records from the current registry and placement audit without treating any previous count as canonical.

Run `npm run buddy:category-systems` to validate both category-system registries against their authoritative source catalogs and published Pages mirrors. The validator discovers every matching study-resource catalog, derives model categories from the current model records, and checks source-row mapping, unique subsystem IDs, division reconciliation against the current placement audit, required contract fields, lifecycle values, and dynamically derived summary counts. The test is `tests/test_buddy_category_system_registry.py`.

The validator is now committed in this feature branch. Its execution in the repository's full CI environment remains pending; a source-file re-fetch and static consistency checks are not a substitute for a successful test run.


## 10. Remaining study-resource category systems

The following additional source labels were found across the other study catalogs. Each is a separate Buddy subsystem and retains its exact category label; similar labels are not merged.

### STUDY-072 — 3D learning environments

- **Subsystem ID:** `study_3d_learning_environments`
- **Mission:** Dedicated study and research system for the exact source category "3D learning environments".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-073 — AI applications

- **Subsystem ID:** `study_ai_applications`
- **Mission:** Dedicated study and research system for the exact source category "AI applications".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-001-100.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-074 — AI coding

- **Subsystem ID:** `study_ai_coding`
- **Mission:** Dedicated study and research system for the exact source category "AI coding".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-075 — AI evaluation

- **Subsystem ID:** `study_ai_evaluation`
- **Mission:** Dedicated study and research system for the exact source category "AI evaluation".
- **Inputs:** 2 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-001-100.json`, `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-076 — AI feedback

- **Subsystem ID:** `study_ai_feedback`
- **Mission:** Dedicated study and research system for the exact source category "AI feedback".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-077 — AI gateway

- **Subsystem ID:** `study_ai_gateway`
- **Mission:** Dedicated study and research system for the exact source category "AI gateway".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-078 — AI inference

- **Subsystem ID:** `study_ai_inference`
- **Mission:** Dedicated study and research system for the exact source category "AI inference".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-079 — AI interface

- **Subsystem ID:** `study_ai_interface`
- **Mission:** Dedicated study and research system for the exact source category "AI interface".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-080 — AI observability

- **Subsystem ID:** `study_ai_observability`
- **Mission:** Dedicated study and research system for the exact source category "AI observability".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-081 — AI orchestration

- **Subsystem ID:** `study_ai_orchestration`
- **Mission:** Dedicated study and research system for the exact source category "AI orchestration".
- **Inputs:** 2 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-082 — AI performance

- **Subsystem ID:** `study_ai_performance`
- **Mission:** Dedicated study and research system for the exact source category "AI performance".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-083 — AI quality testing

- **Subsystem ID:** `study_ai_quality_testing`
- **Mission:** Dedicated study and research system for the exact source category "AI quality testing".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-084 — AI research

- **Subsystem ID:** `study_ai_research`
- **Mission:** Dedicated study and research system for the exact source category "AI research".
- **Inputs:** 3 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-001-100.json`, `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-085 — AI safety

- **Subsystem ID:** `study_ai_safety`
- **Mission:** Dedicated study and research system for the exact source category "AI safety".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-001-100.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-086 — AI tooling

- **Subsystem ID:** `study_ai_tooling`
- **Mission:** Dedicated study and research system for the exact source category "AI tooling".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-001-100.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-087 — AI video learning

- **Subsystem ID:** `study_ai_video_learning`
- **Mission:** Dedicated study and research system for the exact source category "AI video learning".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-001-100.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-088 — AI web apps

- **Subsystem ID:** `study_ai_web_apps`
- **Mission:** Dedicated study and research system for the exact source category "AI web apps".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-001-100.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-089 — AI/ML

- **Subsystem ID:** `study_ai_ml`
- **Mission:** Dedicated study and research system for the exact source category "AI/ML".
- **Inputs:** 2 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-001-100.json`, `config/buddy-study-resources-1001-1100-must-have.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-090 — AI/cloud

- **Subsystem ID:** `study_ai_cloud`
- **Mission:** Dedicated study and research system for the exact source category "AI/cloud".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-001-100.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-091 — API invocation

- **Subsystem ID:** `study_api_invocation`
- **Mission:** Dedicated study and research system for the exact source category "API invocation".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-092 — API security

- **Subsystem ID:** `study_api_security`
- **Mission:** Dedicated study and research system for the exact source category "API security".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-201-300.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-093 — API-use evaluation

- **Subsystem ID:** `study_api_use_evaluation`
- **Mission:** Dedicated study and research system for the exact source category "API-use evaluation".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-094 — Apple ML

- **Subsystem ID:** `study_apple_ml`
- **Mission:** Dedicated study and research system for the exact source category "Apple ML".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-001-100.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-095 — Apple Silicon AI

- **Subsystem ID:** `study_apple_silicon_ai`
- **Mission:** Dedicated study and research system for the exact source category "Apple Silicon AI".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-096 — Apple development

- **Subsystem ID:** `study_apple_development`
- **Mission:** Dedicated study and research system for the exact source category "Apple development".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-001-100.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-097 — Apple train

- **Subsystem ID:** `study_apple_train`
- **Mission:** Dedicated study and research system for the exact source category "Apple train".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-1001-1100-must-have.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-098 — CI/CD

- **Subsystem ID:** `study_ci_cd`
- **Mission:** Dedicated study and research system for the exact source category "CI/CD".
- **Inputs:** 4 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-001-100.json`, `config/buddy-study-resources-201-300.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-099 — CS curriculum

- **Subsystem ID:** `study_cs_curriculum`
- **Mission:** Dedicated study and research system for the exact source category "CS curriculum".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-201-300.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-100 — CS roadmap

- **Subsystem ID:** `study_cs_roadmap`
- **Mission:** Dedicated study and research system for the exact source category "CS roadmap".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-201-300.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-101 — DevOps

- **Subsystem ID:** `study_devops`
- **Mission:** Dedicated study and research system for the exact source category "DevOps".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-201-300.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-102 — FT toolkit

- **Subsystem ID:** `study_ft_toolkit`
- **Mission:** Dedicated study and research system for the exact source category "FT toolkit".
- **Inputs:** 2 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-1001-1100-must-have.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-103 — GPU/AI

- **Subsystem ID:** `study_gpu_ai`
- **Mission:** Dedicated study and research system for the exact source category "GPU/AI".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-001-100.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-104 — GitOps

- **Subsystem ID:** `study_gitops`
- **Mission:** Dedicated study and research system for the exact source category "GitOps".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-201-300.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-105 — HCI

- **Subsystem ID:** `study_hci`
- **Mission:** Dedicated study and research system for the exact source category "HCI".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-201-300.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-106 — HTTP

- **Subsystem ID:** `study_http`
- **Mission:** Dedicated study and research system for the exact source category "HTTP".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-201-300.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-107 — HTTP standards

- **Subsystem ID:** `study_http_standards`
- **Mission:** Dedicated study and research system for the exact source category "HTTP standards".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-201-300.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-108 — Java backend

- **Subsystem ID:** `study_java_backend`
- **Mission:** Dedicated study and research system for the exact source category "Java backend".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-001-100.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-109 — JavaScript

- **Subsystem ID:** `study_javascript`
- **Mission:** Dedicated study and research system for the exact source category "JavaScript".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-001-100.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-110 — JavaScript standards

- **Subsystem ID:** `study_javascript_standards`
- **Mission:** Dedicated study and research system for the exact source category "JavaScript standards".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-001-100.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-111 — JavaScript tooling

- **Subsystem ID:** `study_javascript_tooling`
- **Mission:** Dedicated study and research system for the exact source category "JavaScript tooling".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-001-100.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-112 — Kubernetes

- **Subsystem ID:** `study_kubernetes`
- **Mission:** Dedicated study and research system for the exact source category "Kubernetes".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-201-300.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-113 — LLM applications

- **Subsystem ID:** `study_llm_applications`
- **Mission:** Dedicated study and research system for the exact source category "LLM applications".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-114 — LLM engineering

- **Subsystem ID:** `study_llm_engineering`
- **Mission:** Dedicated study and research system for the exact source category "LLM engineering".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-115 — LLM evaluation

- **Subsystem ID:** `study_llm_evaluation`
- **Mission:** Dedicated study and research system for the exact source category "LLM evaluation".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-116 — LLM evaluation infrastructure

- **Subsystem ID:** `study_llm_evaluation_infrastructure`
- **Mission:** Dedicated study and research system for the exact source category "LLM evaluation infrastructure".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-117 — LLM inference

- **Subsystem ID:** `study_llm_inference`
- **Mission:** Dedicated study and research system for the exact source category "LLM inference".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-118 — LLM observability

- **Subsystem ID:** `study_llm_observability`
- **Mission:** Dedicated study and research system for the exact source category "LLM observability".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-119 — LLM serving

- **Subsystem ID:** `study_llm_serving`
- **Mission:** Dedicated study and research system for the exact source category "LLM serving".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-120 — LLM testing

- **Subsystem ID:** `study_llm_testing`
- **Mission:** Dedicated study and research system for the exact source category "LLM testing".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-121 — Linux/security

- **Subsystem ID:** `study_linux_security`
- **Mission:** Dedicated study and research system for the exact source category "Linux/security".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-201-300.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-122 — LoRA

- **Subsystem ID:** `study_lora`
- **Mission:** Dedicated study and research system for the exact source category "LoRA".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-1001-1100-must-have.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-123 — ML

- **Subsystem ID:** `study_ml`
- **Mission:** Dedicated study and research system for the exact source category "ML".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-001-100.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-124 — ML engineering

- **Subsystem ID:** `study_ml_engineering`
- **Mission:** Dedicated study and research system for the exact source category "ML engineering".
- **Inputs:** 2 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-125 — ML experiments

- **Subsystem ID:** `study_ml_experiments`
- **Mission:** Dedicated study and research system for the exact source category "ML experiments".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-001-100.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-126 — ML lifecycle

- **Subsystem ID:** `study_ml_lifecycle`
- **Mission:** Dedicated study and research system for the exact source category "ML lifecycle".
- **Inputs:** 2 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-001-100.json`, `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-127 — ML orchestration

- **Subsystem ID:** `study_ml_orchestration`
- **Mission:** Dedicated study and research system for the exact source category "ML orchestration".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-128 — ML pedagogy

- **Subsystem ID:** `study_ml_pedagogy`
- **Mission:** Dedicated study and research system for the exact source category "ML pedagogy".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-1001-1100-must-have.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-129 — ML research

- **Subsystem ID:** `study_ml_research`
- **Mission:** Dedicated study and research system for the exact source category "ML research".
- **Inputs:** 2 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-130 — ML systems

- **Subsystem ID:** `study_ml_systems`
- **Mission:** Dedicated study and research system for the exact source category "ML systems".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-001-100.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-131 — MLOps

- **Subsystem ID:** `study_mlops`
- **Mission:** Dedicated study and research system for the exact source category "MLOps".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-132 — NLP literature

- **Subsystem ID:** `study_nlp_literature`
- **Mission:** Dedicated study and research system for the exact source category "NLP literature".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-133 — Python coding

- **Subsystem ID:** `study_python_coding`
- **Mission:** Dedicated study and research system for the exact source category "Python coding".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-134 — Python ecosystem

- **Subsystem ID:** `study_python_ecosystem`
- **Mission:** Dedicated study and research system for the exact source category "Python ecosystem".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-001-100.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-135 — Python web

- **Subsystem ID:** `study_python_web`
- **Mission:** Dedicated study and research system for the exact source category "Python web".
- **Inputs:** 3 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-001-100.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-136 — RAG

- **Subsystem ID:** `study_rag`
- **Mission:** Dedicated study and research system for the exact source category "RAG".
- **Inputs:** 3 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-001-100.json`, `config/buddy-study-resources-401-500.json`, `config/buddy-study-resources-1001-1100-must-have.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-137 — RAG evaluation

- **Subsystem ID:** `study_rag_evaluation`
- **Mission:** Dedicated study and research system for the exact source category "RAG evaluation".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-138 — RAG/program

- **Subsystem ID:** `study_rag_program`
- **Mission:** Dedicated study and research system for the exact source category "RAG/program".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-1001-1100-must-have.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-139 — RAG/search

- **Subsystem ID:** `study_rag_search`
- **Mission:** Dedicated study and research system for the exact source category "RAG/search".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-140 — RL datasets

- **Subsystem ID:** `study_rl_datasets`
- **Mission:** Dedicated study and research system for the exact source category "RL datasets".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-141 — RL environments

- **Subsystem ID:** `study_rl_environments`
- **Mission:** Dedicated study and research system for the exact source category "RL environments".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-142 — RL research

- **Subsystem ID:** `study_rl_research`
- **Mission:** Dedicated study and research system for the exact source category "RL research".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-143 — RLHF

- **Subsystem ID:** `study_rlhf`
- **Mission:** Dedicated study and research system for the exact source category "RLHF".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-144 — SQL

- **Subsystem ID:** `study_sql`
- **Mission:** Dedicated study and research system for the exact source category "SQL".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-201-300.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-145 — SQL practice

- **Subsystem ID:** `study_sql_practice`
- **Mission:** Dedicated study and research system for the exact source category "SQL practice".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-201-300.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-146 — US base

- **Subsystem ID:** `study_us_base`
- **Mission:** Dedicated study and research system for the exact source category "US base".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-1001-1100-must-have.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-147 — US open weights

- **Subsystem ID:** `study_us_open_weights`
- **Mission:** Dedicated study and research system for the exact source category "US open weights".
- **Inputs:** 2 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-1001-1100-must-have.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-148 — abstract reasoning

- **Subsystem ID:** `study_abstract_reasoning`
- **Mission:** Dedicated study and research system for the exact source category "abstract reasoning".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-149 — agent evaluation

- **Subsystem ID:** `study_agent_evaluation`
- **Mission:** Dedicated study and research system for the exact source category "agent evaluation".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-150 — agent security

- **Subsystem ID:** `study_agent_security`
- **Mission:** Dedicated study and research system for the exact source category "agent security".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-151 — agent state

- **Subsystem ID:** `study_agent_state`
- **Mission:** Dedicated study and research system for the exact source category "agent state".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-152 — agent teams

- **Subsystem ID:** `study_agent_teams`
- **Mission:** Dedicated study and research system for the exact source category "agent teams".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-153 — agents

- **Subsystem ID:** `study_agents`
- **Mission:** Dedicated study and research system for the exact source category "agents".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-001-100.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-154 — agents/automation

- **Subsystem ID:** `study_agents_automation`
- **Mission:** Dedicated study and research system for the exact source category "agents/automation".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-001-100.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-155 — alignment

- **Subsystem ID:** `study_alignment`
- **Mission:** Dedicated study and research system for the exact source category "alignment".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-1001-1100-must-have.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-156 — application agents

- **Subsystem ID:** `study_application_agents`
- **Mission:** Dedicated study and research system for the exact source category "application agents".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-157 — application security

- **Subsystem ID:** `study_application_security`
- **Mission:** Dedicated study and research system for the exact source category "application security".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-201-300.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-158 — architecture

- **Subsystem ID:** `study_architecture`
- **Mission:** Dedicated study and research system for the exact source category "architecture".
- **Inputs:** 2 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-1001-1100-must-have.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-159 — attack patterns

- **Subsystem ID:** `study_attack_patterns`
- **Mission:** Dedicated study and research system for the exact source category "attack patterns".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-201-300.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-160 — authentication

- **Subsystem ID:** `study_authentication`
- **Mission:** Dedicated study and research system for the exact source category "authentication".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-201-300.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-161 — automation

- **Subsystem ID:** `study_automation`
- **Mission:** Dedicated study and research system for the exact source category "automation".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-201-300.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-162 — benchmark tracking

- **Subsystem ID:** `study_benchmark_tracking`
- **Mission:** Dedicated study and research system for the exact source category "benchmark tracking".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-163 — binary-feedback optimization

- **Subsystem ID:** `study_binary_feedback_optimization`
- **Mission:** Dedicated study and research system for the exact source category "binary-feedback optimization".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-164 — browser agents

- **Subsystem ID:** `study_browser_agents`
- **Mission:** Dedicated study and research system for the exact source category "browser agents".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-165 — caching

- **Subsystem ID:** `study_caching`
- **Mission:** Dedicated study and research system for the exact source category "caching".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-201-300.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-166 — cleaned web corpus

- **Subsystem ID:** `study_cleaned_web_corpus`
- **Mission:** Dedicated study and research system for the exact source category "cleaned web corpus".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-167 — cloud

- **Subsystem ID:** `study_cloud`
- **Mission:** Dedicated study and research system for the exact source category "cloud".
- **Inputs:** 2 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-001-100.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-168 — cloud native

- **Subsystem ID:** `study_cloud_native`
- **Mission:** Dedicated study and research system for the exact source category "cloud native".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-1001-1100-must-have.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-169 — cloud/software

- **Subsystem ID:** `study_cloud_software`
- **Mission:** Dedicated study and research system for the exact source category "cloud/software".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-001-100.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-170 — code data

- **Subsystem ID:** `study_code_data`
- **Mission:** Dedicated study and research system for the exact source category "code data".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-1001-1100-must-have.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-171 — code eval

- **Subsystem ID:** `study_code_eval`
- **Mission:** Dedicated study and research system for the exact source category "code eval".
- **Inputs:** 3 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-1001-1100-must-have.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-172 — code language modeling

- **Subsystem ID:** `study_code_language_modeling`
- **Mission:** Dedicated study and research system for the exact source category "code language modeling".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-173 — code modeling

- **Subsystem ID:** `study_code_modeling`
- **Mission:** Dedicated study and research system for the exact source category "code modeling".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-174 — code models

- **Subsystem ID:** `study_code_models`
- **Mission:** Dedicated study and research system for the exact source category "code models".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-1001-1100-must-have.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-175 — code-specialized modeling

- **Subsystem ID:** `study_code_specialized_modeling`
- **Mission:** Dedicated study and research system for the exact source category "code-specialized modeling".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-176 — code-text retrieval

- **Subsystem ID:** `study_code_text_retrieval`
- **Mission:** Dedicated study and research system for the exact source category "code-text retrieval".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-177 — coder student

- **Subsystem ID:** `study_coder_student`
- **Mission:** Dedicated study and research system for the exact source category "coder student".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-1001-1100-must-have.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-178 — coding

- **Subsystem ID:** `study_coding`
- **Mission:** Dedicated study and research system for the exact source category "coding".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-179 — coding agents

- **Subsystem ID:** `study_coding_agents`
- **Mission:** Dedicated study and research system for the exact source category "coding agents".
- **Inputs:** 2 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-180 — community

- **Subsystem ID:** `study_community`
- **Mission:** Dedicated study and research system for the exact source category "community".
- **Inputs:** 2 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-1001-1100-must-have.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-181 — competitive programming

- **Subsystem ID:** `study_competitive_programming`
- **Mission:** Dedicated study and research system for the exact source category "competitive programming".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-182 — compiler optimization

- **Subsystem ID:** `study_compiler_optimization`
- **Mission:** Dedicated study and research system for the exact source category "compiler optimization".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-183 — compiler systems

- **Subsystem ID:** `study_compiler_systems`
- **Mission:** Dedicated study and research system for the exact source category "compiler systems".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-201-300.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-184 — complex instruction following

- **Subsystem ID:** `study_complex_instruction_following`
- **Mission:** Dedicated study and research system for the exact source category "complex instruction following".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-185 — computational linguistics

- **Subsystem ID:** `study_computational_linguistics`
- **Mission:** Dedicated study and research system for the exact source category "computational linguistics".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-186 — computer architecture

- **Subsystem ID:** `study_computer_architecture`
- **Mission:** Dedicated study and research system for the exact source category "computer architecture".
- **Inputs:** 3 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-201-300.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-187 — computer science

- **Subsystem ID:** `study_computer_science`
- **Mission:** Dedicated study and research system for the exact source category "computer science".
- **Inputs:** 6 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-001-100.json`, `config/buddy-study-resources-201-300.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-188 — computer security

- **Subsystem ID:** `study_computer_security`
- **Mission:** Dedicated study and research system for the exact source category "computer security".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-201-300.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-189 — computer vision research

- **Subsystem ID:** `study_computer_vision_research`
- **Mission:** Dedicated study and research system for the exact source category "computer vision research".
- **Inputs:** 2 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-190 — computer-use agents

- **Subsystem ID:** `study_computer_use_agents`
- **Mission:** Dedicated study and research system for the exact source category "computer-use agents".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-191 — consensus

- **Subsystem ID:** `study_consensus`
- **Mission:** Dedicated study and research system for the exact source category "consensus".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-201-300.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-192 — containers

- **Subsystem ID:** `study_containers`
- **Mission:** Dedicated study and research system for the exact source category "containers".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-001-100.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-193 — context

- **Subsystem ID:** `study_context`
- **Mission:** Dedicated study and research system for the exact source category "context".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-1001-1100-must-have.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-194 — cross-language

- **Subsystem ID:** `study_cross_language`
- **Mission:** Dedicated study and research system for the exact source category "cross-language".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-201-300.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-195 — cryptography

- **Subsystem ID:** `study_cryptography`
- **Mission:** Dedicated study and research system for the exact source category "cryptography".
- **Inputs:** 2 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-201-300.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-196 — cybersecurity

- **Subsystem ID:** `study_cybersecurity`
- **Mission:** Dedicated study and research system for the exact source category "cybersecurity".
- **Inputs:** 2 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-201-300.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-197 — data

- **Subsystem ID:** `study_data`
- **Mission:** Dedicated study and research system for the exact source category "data".
- **Inputs:** 3 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-1001-1100-must-have.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-198 — data analysis

- **Subsystem ID:** `study_data_analysis`
- **Mission:** Dedicated study and research system for the exact source category "data analysis".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-001-100.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-199 — data caution

- **Subsystem ID:** `study_data_caution`
- **Mission:** Dedicated study and research system for the exact source category "data caution".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-1001-1100-must-have.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-200 — data eval

- **Subsystem ID:** `study_data_eval`
- **Mission:** Dedicated study and research system for the exact source category "data eval".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-1001-1100-must-have.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-201 — data structures

- **Subsystem ID:** `study_data_structures`
- **Mission:** Dedicated study and research system for the exact source category "data structures".
- **Inputs:** 2 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-201-300.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-202 — data/ML

- **Subsystem ID:** `study_data_ml`
- **Mission:** Dedicated study and research system for the exact source category "data/ML".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-001-100.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-203 — data/model versioning

- **Subsystem ID:** `study_data_model_versioning`
- **Mission:** Dedicated study and research system for the exact source category "data/model versioning".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-204 — database systems

- **Subsystem ID:** `study_database_systems`
- **Mission:** Dedicated study and research system for the exact source category "database systems".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-201-300.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-205 — database/cache

- **Subsystem ID:** `study_database_cache`
- **Mission:** Dedicated study and research system for the exact source category "database/cache".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-001-100.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-206 — deep learning practice

- **Subsystem ID:** `study_deep_learning_practice`
- **Mission:** Dedicated study and research system for the exact source category "deep learning practice".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-207 — deep reinforcement learning

- **Subsystem ID:** `study_deep_reinforcement_learning`
- **Mission:** Dedicated study and research system for the exact source category "deep reinforcement learning".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-208 — deep-learning research

- **Subsystem ID:** `study_deep_learning_research`
- **Mission:** Dedicated study and research system for the exact source category "deep-learning research".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-209 — deep-learning textbook

- **Subsystem ID:** `study_deep_learning_textbook`
- **Mission:** Dedicated study and research system for the exact source category "deep-learning textbook".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-210 — defensive security

- **Subsystem ID:** `study_defensive_security`
- **Mission:** Dedicated study and research system for the exact source category "defensive security".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-201-300.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-211 — development

- **Subsystem ID:** `study_development`
- **Mission:** Dedicated study and research system for the exact source category "development".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-001-100.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-212 — direct preference optimization

- **Subsystem ID:** `study_direct_preference_optimization`
- **Mission:** Dedicated study and research system for the exact source category "direct preference optimization".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-213 — distributed AI

- **Subsystem ID:** `study_distributed_ai`
- **Mission:** Dedicated study and research system for the exact source category "distributed AI".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-214 — distributed SQL

- **Subsystem ID:** `study_distributed_sql`
- **Mission:** Dedicated study and research system for the exact source category "distributed SQL".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-201-300.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-215 — distributed data

- **Subsystem ID:** `study_distributed_data`
- **Mission:** Dedicated study and research system for the exact source category "distributed data".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-201-300.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-216 — distributed database

- **Subsystem ID:** `study_distributed_database`
- **Mission:** Dedicated study and research system for the exact source category "distributed database".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-201-300.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-217 — distributed systems

- **Subsystem ID:** `study_distributed_systems`
- **Mission:** Dedicated study and research system for the exact source category "distributed systems".
- **Inputs:** 2 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-201-300.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-218 — distributed training

- **Subsystem ID:** `study_distributed_training`
- **Mission:** Dedicated study and research system for the exact source category "distributed training".
- **Inputs:** 2 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-219 — diverse language-model corpus composition

- **Subsystem ID:** `study_diverse_language_model_corpus_composition`
- **Mission:** Dedicated study and research system for the exact source category "diverse language-model corpus composition".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-220 — education

- **Subsystem ID:** `study_education`
- **Mission:** Dedicated study and research system for the exact source category "education".
- **Inputs:** 4 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-001-100.json`, `config/buddy-study-resources-1001-1100-must-have.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-221 — educational web data

- **Subsystem ID:** `study_educational_web_data`
- **Mission:** Dedicated study and research system for the exact source category "educational web data".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-222 — efficiency

- **Subsystem ID:** `study_efficiency`
- **Mission:** Dedicated study and research system for the exact source category "efficiency".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-1001-1100-must-have.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-223 — efficient FT

- **Subsystem ID:** `study_efficient_ft`
- **Mission:** Dedicated study and research system for the exact source category "efficient FT".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-1001-1100-must-have.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-224 — efficient fine-tuning

- **Subsystem ID:** `study_efficient_fine_tuning`
- **Mission:** Dedicated study and research system for the exact source category "efficient fine-tuning".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-225 — efficient learning

- **Subsystem ID:** `study_efficient_learning`
- **Mission:** Dedicated study and research system for the exact source category "efficient learning".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-226 — efficient transformers

- **Subsystem ID:** `study_efficient_transformers`
- **Mission:** Dedicated study and research system for the exact source category "efficient transformers".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-227 — embeddings

- **Subsystem ID:** `study_embeddings`
- **Mission:** Dedicated study and research system for the exact source category "embeddings".
- **Inputs:** 2 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`, `config/buddy-study-resources-1001-1100-must-have.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-228 — encyclopedic text

- **Subsystem ID:** `study_encyclopedic_text`
- **Mission:** Dedicated study and research system for the exact source category "encyclopedic text".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-229 — engineering

- **Subsystem ID:** `study_engineering`
- **Mission:** Dedicated study and research system for the exact source category "engineering".
- **Inputs:** 2 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-1001-1100-must-have.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-230 — enterprise browser agents

- **Subsystem ID:** `study_enterprise_browser_agents`
- **Mission:** Dedicated study and research system for the exact source category "enterprise browser agents".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-231 — enterprise catalog

- **Subsystem ID:** `study_enterprise_catalog`
- **Mission:** Dedicated study and research system for the exact source category "enterprise catalog".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-1001-1100-must-have.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-232 — environments

- **Subsystem ID:** `study_environments`
- **Mission:** Dedicated study and research system for the exact source category "environments".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-001-100.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-233 — eval

- **Subsystem ID:** `study_eval`
- **Mission:** Dedicated study and research system for the exact source category "eval".
- **Inputs:** 4 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-1001-1100-must-have.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-234 — eval harness

- **Subsystem ID:** `study_eval_harness`
- **Mission:** Dedicated study and research system for the exact source category "eval harness".
- **Inputs:** 2 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-1001-1100-must-have.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-235 — evaluation

- **Subsystem ID:** `study_evaluation`
- **Mission:** Dedicated study and research system for the exact source category "evaluation".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-236 — experiment tracking

- **Subsystem ID:** `study_experiment_tracking`
- **Mission:** Dedicated study and research system for the exact source category "experiment tracking".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-237 — frontend

- **Subsystem ID:** `study_frontend`
- **Mission:** Dedicated study and research system for the exact source category "frontend".
- **Inputs:** 3 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-001-100.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-238 — frontier teacher

- **Subsystem ID:** `study_frontier_teacher`
- **Mission:** Dedicated study and research system for the exact source category "frontier teacher".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-1001-1100-must-have.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-239 — game AI

- **Subsystem ID:** `study_game_ai`
- **Mission:** Dedicated study and research system for the exact source category "game AI".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-240 — general assistants

- **Subsystem ID:** `study_general_assistants`
- **Mission:** Dedicated study and research system for the exact source category "general assistants".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-241 — generalization

- **Subsystem ID:** `study_generalization`
- **Mission:** Dedicated study and research system for the exact source category "generalization".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-242 — graph databases

- **Subsystem ID:** `study_graph_databases`
- **Mission:** Dedicated study and research system for the exact source category "graph databases".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-201-300.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-243 — graph reasoning

- **Subsystem ID:** `study_graph_reasoning`
- **Mission:** Dedicated study and research system for the exact source category "graph reasoning".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-244 — group-relative optimization

- **Subsystem ID:** `study_group_relative_optimization`
- **Mission:** Dedicated study and research system for the exact source category "group-relative optimization".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-245 — holistic evaluation

- **Subsystem ID:** `study_holistic_evaluation`
- **Mission:** Dedicated study and research system for the exact source category "holistic evaluation".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-246 — hosted catalog

- **Subsystem ID:** `study_hosted_catalog`
- **Mission:** Dedicated study and research system for the exact source category "hosted catalog".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-1001-1100-must-have.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-247 — hosted infer

- **Subsystem ID:** `study_hosted_infer`
- **Mission:** Dedicated study and research system for the exact source category "hosted infer".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-1001-1100-must-have.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-248 — hosted run

- **Subsystem ID:** `study_hosted_run`
- **Mission:** Dedicated study and research system for the exact source category "hosted run".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-1001-1100-must-have.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-249 — hub

- **Subsystem ID:** `study_hub`
- **Mission:** Dedicated study and research system for the exact source category "hub".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-1001-1100-must-have.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-250 — identity

- **Subsystem ID:** `study_identity`
- **Mission:** Dedicated study and research system for the exact source category "identity".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-201-300.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-251 — identity preference optimization

- **Subsystem ID:** `study_identity_preference_optimization`
- **Mission:** Dedicated study and research system for the exact source category "identity preference optimization".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-252 — image building

- **Subsystem ID:** `study_image_building`
- **Mission:** Dedicated study and research system for the exact source category "image building".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-201-300.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-253 — incident response

- **Subsystem ID:** `study_incident_response`
- **Mission:** Dedicated study and research system for the exact source category "incident response".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-201-300.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-254 — inference benchmarking

- **Subsystem ID:** `study_inference_benchmarking`
- **Mission:** Dedicated study and research system for the exact source category "inference benchmarking".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-255 — inference optimization

- **Subsystem ID:** `study_inference_optimization`
- **Mission:** Dedicated study and research system for the exact source category "inference optimization".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-256 — information retrieval

- **Subsystem ID:** `study_information_retrieval`
- **Mission:** Dedicated study and research system for the exact source category "information retrieval".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-257 — infra

- **Subsystem ID:** `study_infra`
- **Mission:** Dedicated study and research system for the exact source category "infra".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-1001-1100-must-have.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-258 — infrastructure as code

- **Subsystem ID:** `study_infrastructure_as_code`
- **Mission:** Dedicated study and research system for the exact source category "infrastructure as code".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-201-300.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-259 — infrastructure programming

- **Subsystem ID:** `study_infrastructure_programming`
- **Mission:** Dedicated study and research system for the exact source category "infrastructure programming".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-201-300.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-260 — instruction evolution

- **Subsystem ID:** `study_instruction_evolution`
- **Mission:** Dedicated study and research system for the exact source category "instruction evolution".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-261 — instruction tuning

- **Subsystem ID:** `study_instruction_tuning`
- **Mission:** Dedicated study and research system for the exact source category "instruction tuning".
- **Inputs:** 2 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`, `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-262 — instruction-following evaluation

- **Subsystem ID:** `study_instruction_following_evaluation`
- **Mission:** Dedicated study and research system for the exact source category "instruction-following evaluation".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-263 — interactive tool reasoning

- **Subsystem ID:** `study_interactive_tool_reasoning`
- **Mission:** Dedicated study and research system for the exact source category "interactive tool reasoning".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-264 — internet standards

- **Subsystem ID:** `study_internet_standards`
- **Mission:** Dedicated study and research system for the exact source category "internet standards".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-001-100.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-265 — iterative refinement

- **Subsystem ID:** `study_iterative_refinement`
- **Mission:** Dedicated study and research system for the exact source category "iterative refinement".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-266 — language modeling

- **Subsystem ID:** `study_language_modeling`
- **Mission:** Dedicated study and research system for the exact source category "language modeling".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-267 — language research

- **Subsystem ID:** `study_language_research`
- **Mission:** Dedicated study and research system for the exact source category "language research".
- **Inputs:** 2 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-268 — language-model internals

- **Subsystem ID:** `study_language_model_internals`
- **Mission:** Dedicated study and research system for the exact source category "language-model internals".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-269 — language-model training

- **Subsystem ID:** `study_language_model_training`
- **Mission:** Dedicated study and research system for the exact source category "language-model training".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-270 — large artifacts

- **Subsystem ID:** `study_large_artifacts`
- **Mission:** Dedicated study and research system for the exact source category "large artifacts".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-271 — large-model training

- **Subsystem ID:** `study_large_model_training`
- **Mission:** Dedicated study and research system for the exact source category "large-model training".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-272 — licenses

- **Subsystem ID:** `study_licenses`
- **Mission:** Dedicated study and research system for the exact source category "licenses".
- **Inputs:** 3 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-1001-1100-must-have.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-273 — load balancing

- **Subsystem ID:** `study_load_balancing`
- **Mission:** Dedicated study and research system for the exact source category "load balancing".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-201-300.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-274 — local AI

- **Subsystem ID:** `study_local_ai`
- **Mission:** Dedicated study and research system for the exact source category "local AI".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-275 — local UX

- **Subsystem ID:** `study_local_ux`
- **Mission:** Dedicated study and research system for the exact source category "local UX".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-1001-1100-must-have.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-276 — local infer

- **Subsystem ID:** `study_local_infer`
- **Mission:** Dedicated study and research system for the exact source category "local infer".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-1001-1100-must-have.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-277 — local models

- **Subsystem ID:** `study_local_models`
- **Mission:** Dedicated study and research system for the exact source category "local models".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-278 — local packs

- **Subsystem ID:** `study_local_packs`
- **Mission:** Dedicated study and research system for the exact source category "local packs".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-1001-1100-must-have.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-279 — long-form language

- **Subsystem ID:** `study_long_form_language`
- **Mission:** Dedicated study and research system for the exact source category "long-form language".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-280 — machine-learning research

- **Subsystem ID:** `study_machine_learning_research`
- **Mission:** Dedicated study and research system for the exact source category "machine-learning research".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-281 — math programming

- **Subsystem ID:** `study_math_programming`
- **Mission:** Dedicated study and research system for the exact source category "math programming".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-201-300.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-282 — methods

- **Subsystem ID:** `study_methods`
- **Mission:** Dedicated study and research system for the exact source category "methods".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-1001-1100-must-have.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-283 — mobile agents

- **Subsystem ID:** `study_mobile_agents`
- **Mission:** Dedicated study and research system for the exact source category "mobile agents".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-284 — model gateway

- **Subsystem ID:** `study_model_gateway`
- **Mission:** Dedicated study and research system for the exact source category "model gateway".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-285 — model post-training

- **Subsystem ID:** `study_model_post_training`
- **Mission:** Dedicated study and research system for the exact source category "model post-training".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-286 — model routing

- **Subsystem ID:** `study_model_routing`
- **Mission:** Dedicated study and research system for the exact source category "model routing".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-287 — model storage

- **Subsystem ID:** `study_model_storage`
- **Mission:** Dedicated study and research system for the exact source category "model storage".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-288 — model/data ecosystem

- **Subsystem ID:** `study_model_data_ecosystem`
- **Mission:** Dedicated study and research system for the exact source category "model/data ecosystem".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-289 — modular reasoning

- **Subsystem ID:** `study_modular_reasoning`
- **Mission:** Dedicated study and research system for the exact source category "modular reasoning".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-290 — multi-agent AI

- **Subsystem ID:** `study_multi_agent_ai`
- **Mission:** Dedicated study and research system for the exact source category "multi-agent AI".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-291 — multi-agent RL

- **Subsystem ID:** `study_multi_agent_rl`
- **Mission:** Dedicated study and research system for the exact source category "multi-agent RL".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-292 — multi-turn evaluation

- **Subsystem ID:** `study_multi_turn_evaluation`
- **Mission:** Dedicated study and research system for the exact source category "multi-turn evaluation".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-293 — natural language processing

- **Subsystem ID:** `study_natural_language_processing`
- **Mission:** Dedicated study and research system for the exact source category "natural language processing".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-294 — network analysis

- **Subsystem ID:** `study_network_analysis`
- **Mission:** Dedicated study and research system for the exact source category "network analysis".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-201-300.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-295 — networking

- **Subsystem ID:** `study_networking`
- **Mission:** Dedicated study and research system for the exact source category "networking".
- **Inputs:** 5 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-001-100.json`, `config/buddy-study-resources-201-300.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-296 — networking/security

- **Subsystem ID:** `study_networking_security`
- **Mission:** Dedicated study and research system for the exact source category "networking/security".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-001-100.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-297 — news

- **Subsystem ID:** `study_news`
- **Mission:** Dedicated study and research system for the exact source category "news".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-1001-1100-must-have.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-298 — numerical computing

- **Subsystem ID:** `study_numerical_computing`
- **Mission:** Dedicated study and research system for the exact source category "numerical computing".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-001-100.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-299 — observability

- **Subsystem ID:** `study_observability`
- **Mission:** Dedicated study and research system for the exact source category "observability".
- **Inputs:** 3 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-1001-1100-must-have.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-300 — occupations

- **Subsystem ID:** `study_occupations`
- **Mission:** Dedicated study and research system for the exact source category "occupations".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-001-100.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-301 — odds-ratio preference optimization

- **Subsystem ID:** `study_odds_ratio_preference_optimization`
- **Mission:** Dedicated study and research system for the exact source category "odds-ratio preference optimization".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-302 — on-device AI

- **Subsystem ID:** `study_on_device_ai`
- **Mission:** Dedicated study and research system for the exact source category "on-device AI".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-001-100.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-303 — on-device ML

- **Subsystem ID:** `study_on_device_ml`
- **Mission:** Dedicated study and research system for the exact source category "on-device ML".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-001-100.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-304 — open US stack

- **Subsystem ID:** `study_open_us_stack`
- **Mission:** Dedicated study and research system for the exact source category "open US stack".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-1001-1100-must-have.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-305 — open code corpus

- **Subsystem ID:** `study_open_code_corpus`
- **Mission:** Dedicated study and research system for the exact source category "open code corpus".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-306 — open conversational data

- **Subsystem ID:** `study_open_conversational_data`
- **Mission:** Dedicated study and research system for the exact source category "open conversational data".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-307 — open model research

- **Subsystem ID:** `study_open_model_research`
- **Mission:** Dedicated study and research system for the exact source category "open model research".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-308 — operating systems

- **Subsystem ID:** `study_operating_systems`
- **Mission:** Dedicated study and research system for the exact source category "operating systems".
- **Inputs:** 3 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-201-300.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-309 — ops

- **Subsystem ID:** `study_ops`
- **Mission:** Dedicated study and research system for the exact source category "ops".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-1001-1100-must-have.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-310 — orchestration

- **Subsystem ID:** `study_orchestration`
- **Mission:** Dedicated study and research system for the exact source category "orchestration".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-001-100.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-311 — parallel computing

- **Subsystem ID:** `study_parallel_computing`
- **Mission:** Dedicated study and research system for the exact source category "parallel computing".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-201-300.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-312 — parameter-efficient learning

- **Subsystem ID:** `study_parameter_efficient_learning`
- **Mission:** Dedicated study and research system for the exact source category "parameter-efficient learning".
- **Inputs:** 2 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-313 — peer hub

- **Subsystem ID:** `study_peer_hub`
- **Mission:** Dedicated study and research system for the exact source category "peer hub".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-1001-1100-must-have.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-314 — planned tool execution

- **Subsystem ID:** `study_planned_tool_execution`
- **Mission:** Dedicated study and research system for the exact source category "planned tool execution".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-315 — policy

- **Subsystem ID:** `study_policy`
- **Mission:** Dedicated study and research system for the exact source category "policy".
- **Inputs:** 2 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-1001-1100-must-have.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-316 — post-training

- **Subsystem ID:** `study_post_training`
- **Mission:** Dedicated study and research system for the exact source category "post-training".
- **Inputs:** 2 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-317 — pretrain data

- **Subsystem ID:** `study_pretrain_data`
- **Mission:** Dedicated study and research system for the exact source category "pretrain data".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-1001-1100-must-have.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-318 — principle-guided self-critique

- **Subsystem ID:** `study_principle_guided_self_critique`
- **Mission:** Dedicated study and research system for the exact source category "principle-guided self-critique".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-319 — problem decomposition

- **Subsystem ID:** `study_problem_decomposition`
- **Mission:** Dedicated study and research system for the exact source category "problem decomposition".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-320 — production ML

- **Subsystem ID:** `study_production_ml`
- **Mission:** Dedicated study and research system for the exact source category "production ML".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-321 — program-aided reasoning

- **Subsystem ID:** `study_program_aided_reasoning`
- **Mission:** Dedicated study and research system for the exact source category "program-aided reasoning".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-322 — program-assisted reasoning

- **Subsystem ID:** `study_program_assisted_reasoning`
- **Mission:** Dedicated study and research system for the exact source category "program-assisted reasoning".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-323 — programmatic AI

- **Subsystem ID:** `study_programmatic_ai`
- **Mission:** Dedicated study and research system for the exact source category "programmatic AI".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-324 — programming

- **Subsystem ID:** `study_programming`
- **Mission:** Dedicated study and research system for the exact source category "programming".
- **Inputs:** 13 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-001-100.json`, `config/buddy-study-resources-201-300.json`, `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-325 — proximal policy optimization

- **Subsystem ID:** `study_proximal_policy_optimization`
- **Mission:** Dedicated study and research system for the exact source category "proximal policy optimization".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-326 — proxy

- **Subsystem ID:** `study_proxy`
- **Mission:** Dedicated study and research system for the exact source category "proxy".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-201-300.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-327 — quant

- **Subsystem ID:** `study_quant`
- **Mission:** Dedicated study and research system for the exact source category "quant".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-1001-1100-must-have.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-328 — quantization

- **Subsystem ID:** `study_quantization`
- **Mission:** Dedicated study and research system for the exact source category "quantization".
- **Inputs:** 4 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-329 — real-time communications

- **Subsystem ID:** `study_real_time_communications`
- **Mission:** Dedicated study and research system for the exact source category "real-time communications".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-201-300.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-330 — real-time web

- **Subsystem ID:** `study_real_time_web`
- **Mission:** Dedicated study and research system for the exact source category "real-time web".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-201-300.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-331 — reason eval

- **Subsystem ID:** `study_reason_eval`
- **Mission:** Dedicated study and research system for the exact source category "reason eval".
- **Inputs:** 2 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-1001-1100-must-have.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-332 — reasoning

- **Subsystem ID:** `study_reasoning`
- **Mission:** Dedicated study and research system for the exact source category "reasoning".
- **Inputs:** 2 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-333 — reasoning aggregation

- **Subsystem ID:** `study_reasoning_aggregation`
- **Mission:** Dedicated study and research system for the exact source category "reasoning aggregation".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-334 — reasoning environments

- **Subsystem ID:** `study_reasoning_environments`
- **Mission:** Dedicated study and research system for the exact source category "reasoning environments".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-335 — reasoning plans

- **Subsystem ID:** `study_reasoning_plans`
- **Mission:** Dedicated study and research system for the exact source category "reasoning plans".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-336 — reasoning plus acting

- **Subsystem ID:** `study_reasoning_plus_acting`
- **Mission:** Dedicated study and research system for the exact source category "reasoning plus acting".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-337 — reasoning search

- **Subsystem ID:** `study_reasoning_search`
- **Mission:** Dedicated study and research system for the exact source category "reasoning search".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-338 — research

- **Subsystem ID:** `study_research`
- **Mission:** Dedicated study and research system for the exact source category "research".
- **Inputs:** 5 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-001-100.json`, `config/buddy-study-resources-1001-1100-must-have.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-339 — research graphs

- **Subsystem ID:** `study_research_graphs`
- **Mission:** Dedicated study and research system for the exact source category "research graphs".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-340 — research hub

- **Subsystem ID:** `study_research_hub`
- **Mission:** Dedicated study and research system for the exact source category "research hub".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-1001-1100-must-have.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-341 — research index

- **Subsystem ID:** `study_research_index`
- **Mission:** Dedicated study and research system for the exact source category "research index".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-1001-1100-must-have.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-342 — research literature

- **Subsystem ID:** `study_research_literature`
- **Mission:** Dedicated study and research system for the exact source category "research literature".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-343 — research org

- **Subsystem ID:** `study_research_org`
- **Mission:** Dedicated study and research system for the exact source category "research org".
- **Inputs:** 2 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-1001-1100-must-have.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-344 — reverse proxy

- **Subsystem ID:** `study_reverse_proxy`
- **Mission:** Dedicated study and research system for the exact source category "reverse proxy".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-201-300.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-345 — router catalog

- **Subsystem ID:** `study_router_catalog`
- **Mission:** Dedicated study and research system for the exact source category "router catalog".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-1001-1100-must-have.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-346 — safety methods

- **Subsystem ID:** `study_safety_methods`
- **Mission:** Dedicated study and research system for the exact source category "safety methods".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-1001-1100-must-have.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-347 — safety ops

- **Subsystem ID:** `study_safety_ops`
- **Mission:** Dedicated study and research system for the exact source category "safety ops".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-1001-1100-must-have.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-348 — safety org

- **Subsystem ID:** `study_safety_org`
- **Mission:** Dedicated study and research system for the exact source category "safety org".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-1001-1100-must-have.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-349 — scale train

- **Subsystem ID:** `study_scale_train`
- **Mission:** Dedicated study and research system for the exact source category "scale train".
- **Inputs:** 2 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-1001-1100-must-have.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-350 — secrets management

- **Subsystem ID:** `study_secrets_management`
- **Mission:** Dedicated study and research system for the exact source category "secrets management".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-201-300.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-351 — secure SDLC

- **Subsystem ID:** `study_secure_sdlc`
- **Mission:** Dedicated study and research system for the exact source category "secure SDLC".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-201-300.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-352 — security education

- **Subsystem ID:** `study_security_education`
- **Mission:** Dedicated study and research system for the exact source category "security education".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-201-300.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-353 — security research

- **Subsystem ID:** `study_security_research`
- **Mission:** Dedicated study and research system for the exact source category "security research".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-201-300.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-354 — self-supervised tool use

- **Subsystem ID:** `study_self_supervised_tool_use`
- **Mission:** Dedicated study and research system for the exact source category "self-supervised tool use".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-355 — serve

- **Subsystem ID:** `study_serve`
- **Mission:** Dedicated study and research system for the exact source category "serve".
- **Inputs:** 2 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-1001-1100-must-have.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-356 — service mesh

- **Subsystem ID:** `study_service_mesh`
- **Mission:** Dedicated study and research system for the exact source category "service mesh".
- **Inputs:** 2 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-201-300.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-357 — service networking

- **Subsystem ID:** `study_service_networking`
- **Mission:** Dedicated study and research system for the exact source category "service networking".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-201-300.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-358 — serving

- **Subsystem ID:** `study_serving`
- **Mission:** Dedicated study and research system for the exact source category "serving".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-1001-1100-must-have.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-359 — serving efficiency

- **Subsystem ID:** `study_serving_efficiency`
- **Mission:** Dedicated study and research system for the exact source category "serving efficiency".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-360 — shell

- **Subsystem ID:** `study_shell`
- **Mission:** Dedicated study and research system for the exact source category "shell".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-001-100.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-361 — small instruction dataset

- **Subsystem ID:** `study_small_instruction_dataset`
- **Mission:** Dedicated study and research system for the exact source category "small instruction dataset".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-362 — software education

- **Subsystem ID:** `study_software_education`
- **Mission:** Dedicated study and research system for the exact source category "software education".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-001-100.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-363 — software engineering

- **Subsystem ID:** `study_software_engineering`
- **Mission:** Dedicated study and research system for the exact source category "software engineering".
- **Inputs:** 6 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-001-100.json`, `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-364 — speech AI

- **Subsystem ID:** `study_speech_ai`
- **Mission:** Dedicated study and research system for the exact source category "speech AI".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-001-100.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-365 — stateful tool agents

- **Subsystem ID:** `study_stateful_tool_agents`
- **Mission:** Dedicated study and research system for the exact source category "stateful tool agents".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-366 — stream processing

- **Subsystem ID:** `study_stream_processing`
- **Mission:** Dedicated study and research system for the exact source category "stream processing".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-201-300.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-367 — structured generation

- **Subsystem ID:** `study_structured_generation`
- **Mission:** Dedicated study and research system for the exact source category "structured generation".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-368 — structured outputs

- **Subsystem ID:** `study_structured_outputs`
- **Mission:** Dedicated study and research system for the exact source category "structured outputs".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-369 — subquestion decomposition

- **Subsystem ID:** `study_subquestion_decomposition`
- **Mission:** Dedicated study and research system for the exact source category "subquestion decomposition".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-370 — synthetic dialogue

- **Subsystem ID:** `study_synthetic_dialogue`
- **Mission:** Dedicated study and research system for the exact source category "synthetic dialogue".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-371 — synthetic instruction generation

- **Subsystem ID:** `study_synthetic_instruction_generation`
- **Mission:** Dedicated study and research system for the exact source category "synthetic instruction generation".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-372 — synthetic instruction synthesis

- **Subsystem ID:** `study_synthetic_instruction_synthesis`
- **Mission:** Dedicated study and research system for the exact source category "synthetic instruction synthesis".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-373 — systems engineering

- **Subsystem ID:** `study_systems_engineering`
- **Mission:** Dedicated study and research system for the exact source category "systems engineering".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-201-300.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-374 — technical Q&A

- **Subsystem ID:** `study_technical_q_a`
- **Mission:** Dedicated study and research system for the exact source category "technical Q&A".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-375 — test

- **Subsystem ID:** `study_test`
- **Mission:** Dedicated study and research system for the exact source category "test".
- **Inputs:** 3 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-1001-1100-must-have.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-376 — tokenization

- **Subsystem ID:** `study_tokenization`
- **Mission:** Dedicated study and research system for the exact source category "tokenization".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-377 — tokens

- **Subsystem ID:** `study_tokens`
- **Mission:** Dedicated study and research system for the exact source category "tokens".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-201-300.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-378 — tool agents

- **Subsystem ID:** `study_tool_agents`
- **Mission:** Dedicated study and research system for the exact source category "tool agents".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-379 — tool use

- **Subsystem ID:** `study_tool_use`
- **Mission:** Dedicated study and research system for the exact source category "tool use".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-380 — tool-assisted critique

- **Subsystem ID:** `study_tool_assisted_critique`
- **Mission:** Dedicated study and research system for the exact source category "tool-assisted critique".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-381 — tool-augmented QA

- **Subsystem ID:** `study_tool_augmented_qa`
- **Mission:** Dedicated study and research system for the exact source category "tool-augmented QA".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-382 — tools

- **Subsystem ID:** `study_tools`
- **Mission:** Dedicated study and research system for the exact source category "tools".
- **Inputs:** 2 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-1001-1100-must-have.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-383 — train

- **Subsystem ID:** `study_train`
- **Mission:** Dedicated study and research system for the exact source category "train".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-1001-1100-must-have.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-384 — training

- **Subsystem ID:** `study_training`
- **Mission:** Dedicated study and research system for the exact source category "training".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-1001-1100-must-have.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-385 — transformer concepts

- **Subsystem ID:** `study_transformer_concepts`
- **Mission:** Dedicated study and research system for the exact source category "transformer concepts".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-386 — transformer research

- **Subsystem ID:** `study_transformer_research`
- **Mission:** Dedicated study and research system for the exact source category "transformer research".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-387 — transparent language-model corpus

- **Subsystem ID:** `study_transparent_language_model_corpus`
- **Mission:** Dedicated study and research system for the exact source category "transparent language-model corpus".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-388 — unsupervised learning

- **Subsystem ID:** `study_unsupervised_learning`
- **Mission:** Dedicated study and research system for the exact source category "unsupervised learning".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-389 — vectors

- **Subsystem ID:** `study_vectors`
- **Mission:** Dedicated study and research system for the exact source category "vectors".
- **Inputs:** 7 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-1001-1100-must-have.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-390 — verbal reinforcement

- **Subsystem ID:** `study_verbal_reinforcement`
- **Mission:** Dedicated study and research system for the exact source category "verbal reinforcement".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-391 — verifiable instruction following

- **Subsystem ID:** `study_verifiable_instruction_following`
- **Mission:** Dedicated study and research system for the exact source category "verifiable instruction following".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-392 — version control

- **Subsystem ID:** `study_version_control`
- **Mission:** Dedicated study and research system for the exact source category "version control".
- **Inputs:** 2 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-001-100.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-393 — visual browser agents

- **Subsystem ID:** `study_visual_browser_agents`
- **Mission:** Dedicated study and research system for the exact source category "visual browser agents".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-394 — visual web interaction

- **Subsystem ID:** `study_visual_web_interaction`
- **Mission:** Dedicated study and research system for the exact source category "visual web interaction".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-395 — visualization

- **Subsystem ID:** `study_visualization`
- **Mission:** Dedicated study and research system for the exact source category "visualization".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-001-100.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-396 — web

- **Subsystem ID:** `study_web`
- **Mission:** Dedicated study and research system for the exact source category "web".
- **Inputs:** 2 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-001-100.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-397 — web agents

- **Subsystem ID:** `study_web_agents`
- **Mission:** Dedicated study and research system for the exact source category "web agents".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-401-500.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-398 — web dialogue agents

- **Subsystem ID:** `study_web_dialogue_agents`
- **Mission:** Dedicated study and research system for the exact source category "web dialogue agents".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-399 — web framework

- **Subsystem ID:** `study_web_framework`
- **Mission:** Dedicated study and research system for the exact source category "web framework".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-001-100.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-400 — web server

- **Subsystem ID:** `study_web_server`
- **Mission:** Dedicated study and research system for the exact source category "web server".
- **Inputs:** 3 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-201-300.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-401 — web standards

- **Subsystem ID:** `study_web_standards`
- **Mission:** Dedicated study and research system for the exact source category "web standards".
- **Inputs:** 2 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-001-100.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-402 — web-agent trajectories

- **Subsystem ID:** `study_web_agent_trajectories`
- **Mission:** Dedicated study and research system for the exact source category "web-agent trajectories".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-501-600.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.

### STUDY-403 — zero trust

- **Subsystem ID:** `study_zero_trust`
- **Mission:** Dedicated study and research system for the exact source category "zero trust".
- **Inputs:** 1 catalogued resource record(s), source provenance, license/terms, learning objectives, and category-specific tasks.
- **Outputs:** Category knowledge records, reproducible exercises, experiment plans, benchmark evidence, and documented gaps.
- **Source files:** `config/buddy-study-resources-201-300.json`.
- **Control and measures:** Verify source quality, freshness, license, reproducibility, and safe execution; track correctness, coverage, mastery, and cost where applicable.
- **Acceptance gate:** Dedicated interface, owner, tests, benchmark/checklist, failure modes, and evidence links before promotion beyond `catalogued`.


## 11. Dedicated division systems and unresolved division-count conflict

The repository contains a 65-entry candidate division registry in `config/masterbot-65-registry.json`. Other sources disagree: the README, rebuild plan, and placement audit state 45 divisions; the legacy lineage map states 46. The 65-entry registry contains the 45 names present in the 45-division audit plus 20 additional names. A separate Actions contract workflow also validates generation of 65 division runtime contracts, so the 65-entry registry is actively consumed by CI; the conflict still needs reconciliation with the 45/46-count documents. This is a source-of-truth conflict, not permission to silently expand or delete divisions. All 65 receive separate catalogued subsystem records, but the 20 entries present in the 65-entry registry but absent from the 45-division audit are marked `present_in_65_registry_not_in_45_audit` pending owner reconciliation.

### DIV-01 — DreamFinance

- **Subsystem ID:** `division_dreamfinance`
- **Registry identity:** `masterbot-65-registry.json` entry 1.
- **Reconciliation status:** `present_in_45_division_sources`.
- **Mission:** Dedicated division system owning its bot placement, capability contracts, specialist workforce, workflows, tools, benchmarks, lineage, and operational evidence.
- **Inputs:** Assigned bot profiles, capability records, task requests, division policies, and cross-division dependencies.
- **Outputs:** Division-owned capability plans, task routing, evidence records, workforce status, and dashboard health.
- **Control and measures:** Enforce least privilege, owner/reviewer assignment, cross-division handoff contracts, lifecycle lineage, and no-orphan rules; measure placement confidence, capability coverage, reliability, and benchmark results.
- **Acceptance gate:** Reconcile division identity, assign accountable owner, map bots and capabilities, define interfaces, add tests/benchmarks, and expose status before implementation promotion.
### DIV-02 — DreamRealEstate

- **Subsystem ID:** `division_dreamrealestate`
- **Registry identity:** `masterbot-65-registry.json` entry 2.
- **Reconciliation status:** `present_in_45_division_sources`.
- **Mission:** Dedicated division system owning its bot placement, capability contracts, specialist workforce, workflows, tools, benchmarks, lineage, and operational evidence.
- **Inputs:** Assigned bot profiles, capability records, task requests, division policies, and cross-division dependencies.
- **Outputs:** Division-owned capability plans, task routing, evidence records, workforce status, and dashboard health.
- **Control and measures:** Enforce least privilege, owner/reviewer assignment, cross-division handoff contracts, lifecycle lineage, and no-orphan rules; measure placement confidence, capability coverage, reliability, and benchmark results.
- **Acceptance gate:** Reconcile division identity, assign accountable owner, map bots and capabilities, define interfaces, add tests/benchmarks, and expose status before implementation promotion.
### DIV-03 — DreamSalesPro

- **Subsystem ID:** `division_dreamsalespro`
- **Registry identity:** `masterbot-65-registry.json` entry 3.
- **Reconciliation status:** `present_in_45_division_sources`.
- **Mission:** Dedicated division system owning its bot placement, capability contracts, specialist workforce, workflows, tools, benchmarks, lineage, and operational evidence.
- **Inputs:** Assigned bot profiles, capability records, task requests, division policies, and cross-division dependencies.
- **Outputs:** Division-owned capability plans, task routing, evidence records, workforce status, and dashboard health.
- **Control and measures:** Enforce least privilege, owner/reviewer assignment, cross-division handoff contracts, lifecycle lineage, and no-orphan rules; measure placement confidence, capability coverage, reliability, and benchmark results.
- **Acceptance gate:** Reconcile division identity, assign accountable owner, map bots and capabilities, define interfaces, add tests/benchmarks, and expose status before implementation promotion.
### DIV-04 — DreamAIInfra

- **Subsystem ID:** `division_dreamaiinfra`
- **Registry identity:** `masterbot-65-registry.json` entry 4.
- **Reconciliation status:** `present_in_45_division_sources`.
- **Mission:** Dedicated division system owning its bot placement, capability contracts, specialist workforce, workflows, tools, benchmarks, lineage, and operational evidence.
- **Inputs:** Assigned bot profiles, capability records, task requests, division policies, and cross-division dependencies.
- **Outputs:** Division-owned capability plans, task routing, evidence records, workforce status, and dashboard health.
- **Control and measures:** Enforce least privilege, owner/reviewer assignment, cross-division handoff contracts, lifecycle lineage, and no-orphan rules; measure placement confidence, capability coverage, reliability, and benchmark results.
- **Acceptance gate:** Reconcile division identity, assign accountable owner, map bots and capabilities, define interfaces, add tests/benchmarks, and expose status before implementation promotion.
### DIV-05 — DreamRetail

- **Subsystem ID:** `division_dreamretail`
- **Registry identity:** `masterbot-65-registry.json` entry 5.
- **Reconciliation status:** `present_in_45_division_sources`.
- **Mission:** Dedicated division system owning its bot placement, capability contracts, specialist workforce, workflows, tools, benchmarks, lineage, and operational evidence.
- **Inputs:** Assigned bot profiles, capability records, task requests, division policies, and cross-division dependencies.
- **Outputs:** Division-owned capability plans, task routing, evidence records, workforce status, and dashboard health.
- **Control and measures:** Enforce least privilege, owner/reviewer assignment, cross-division handoff contracts, lifecycle lineage, and no-orphan rules; measure placement confidence, capability coverage, reliability, and benchmark results.
- **Acceptance gate:** Reconcile division identity, assign accountable owner, map bots and capabilities, define interfaces, add tests/benchmarks, and expose status before implementation promotion.
### DIV-06 — DreamProServices

- **Subsystem ID:** `division_dreamproservices`
- **Registry identity:** `masterbot-65-registry.json` entry 6.
- **Reconciliation status:** `present_in_45_division_sources`.
- **Mission:** Dedicated division system owning its bot placement, capability contracts, specialist workforce, workflows, tools, benchmarks, lineage, and operational evidence.
- **Inputs:** Assigned bot profiles, capability records, task requests, division policies, and cross-division dependencies.
- **Outputs:** Division-owned capability plans, task routing, evidence records, workforce status, and dashboard health.
- **Control and measures:** Enforce least privilege, owner/reviewer assignment, cross-division handoff contracts, lifecycle lineage, and no-orphan rules; measure placement confidence, capability coverage, reliability, and benchmark results.
- **Acceptance gate:** Reconcile division identity, assign accountable owner, map bots and capabilities, define interfaces, add tests/benchmarks, and expose status before implementation promotion.
### DIV-07 — DreamData

- **Subsystem ID:** `division_dreamdata`
- **Registry identity:** `masterbot-65-registry.json` entry 7.
- **Reconciliation status:** `present_in_45_division_sources`.
- **Mission:** Dedicated division system owning its bot placement, capability contracts, specialist workforce, workflows, tools, benchmarks, lineage, and operational evidence.
- **Inputs:** Assigned bot profiles, capability records, task requests, division policies, and cross-division dependencies.
- **Outputs:** Division-owned capability plans, task routing, evidence records, workforce status, and dashboard health.
- **Control and measures:** Enforce least privilege, owner/reviewer assignment, cross-division handoff contracts, lifecycle lineage, and no-orphan rules; measure placement confidence, capability coverage, reliability, and benchmark results.
- **Acceptance gate:** Reconcile division identity, assign accountable owner, map bots and capabilities, define interfaces, add tests/benchmarks, and expose status before implementation promotion.
### DIV-08 — DreamGlobal

- **Subsystem ID:** `division_dreamglobal`
- **Registry identity:** `masterbot-65-registry.json` entry 8.
- **Reconciliation status:** `present_in_45_division_sources`.
- **Mission:** Dedicated division system owning its bot placement, capability contracts, specialist workforce, workflows, tools, benchmarks, lineage, and operational evidence.
- **Inputs:** Assigned bot profiles, capability records, task requests, division policies, and cross-division dependencies.
- **Outputs:** Division-owned capability plans, task routing, evidence records, workforce status, and dashboard health.
- **Control and measures:** Enforce least privilege, owner/reviewer assignment, cross-division handoff contracts, lifecycle lineage, and no-orphan rules; measure placement confidence, capability coverage, reliability, and benchmark results.
- **Acceptance gate:** Reconcile division identity, assign accountable owner, map bots and capabilities, define interfaces, add tests/benchmarks, and expose status before implementation promotion.
### DIV-09 — DreamAutomation

- **Subsystem ID:** `division_dreamautomation`
- **Registry identity:** `masterbot-65-registry.json` entry 9.
- **Reconciliation status:** `present_in_45_division_sources`.
- **Mission:** Dedicated division system owning its bot placement, capability contracts, specialist workforce, workflows, tools, benchmarks, lineage, and operational evidence.
- **Inputs:** Assigned bot profiles, capability records, task requests, division policies, and cross-division dependencies.
- **Outputs:** Division-owned capability plans, task routing, evidence records, workforce status, and dashboard health.
- **Control and measures:** Enforce least privilege, owner/reviewer assignment, cross-division handoff contracts, lifecycle lineage, and no-orphan rules; measure placement confidence, capability coverage, reliability, and benchmark results.
- **Acceptance gate:** Reconcile division identity, assign accountable owner, map bots and capabilities, define interfaces, add tests/benchmarks, and expose status before implementation promotion.
### DIV-10 — DreamEmpire

- **Subsystem ID:** `division_dreamempire`
- **Registry identity:** `masterbot-65-registry.json` entry 10.
- **Reconciliation status:** `present_in_45_division_sources`.
- **Mission:** Dedicated division system owning its bot placement, capability contracts, specialist workforce, workflows, tools, benchmarks, lineage, and operational evidence.
- **Inputs:** Assigned bot profiles, capability records, task requests, division policies, and cross-division dependencies.
- **Outputs:** Division-owned capability plans, task routing, evidence records, workforce status, and dashboard health.
- **Control and measures:** Enforce least privilege, owner/reviewer assignment, cross-division handoff contracts, lifecycle lineage, and no-orphan rules; measure placement confidence, capability coverage, reliability, and benchmark results.
- **Acceptance gate:** Reconcile division identity, assign accountable owner, map bots and capabilities, define interfaces, add tests/benchmarks, and expose status before implementation promotion.
### DIV-11 — DreamContent

- **Subsystem ID:** `division_dreamcontent`
- **Registry identity:** `masterbot-65-registry.json` entry 11.
- **Reconciliation status:** `present_in_45_division_sources`.
- **Mission:** Dedicated division system owning its bot placement, capability contracts, specialist workforce, workflows, tools, benchmarks, lineage, and operational evidence.
- **Inputs:** Assigned bot profiles, capability records, task requests, division policies, and cross-division dependencies.
- **Outputs:** Division-owned capability plans, task routing, evidence records, workforce status, and dashboard health.
- **Control and measures:** Enforce least privilege, owner/reviewer assignment, cross-division handoff contracts, lifecycle lineage, and no-orphan rules; measure placement confidence, capability coverage, reliability, and benchmark results.
- **Acceptance gate:** Reconcile division identity, assign accountable owner, map bots and capabilities, define interfaces, add tests/benchmarks, and expose status before implementation promotion.
### DIV-12 — DreamTrade

- **Subsystem ID:** `division_dreamtrade`
- **Registry identity:** `masterbot-65-registry.json` entry 12.
- **Reconciliation status:** `present_in_45_division_sources`.
- **Mission:** Dedicated division system owning its bot placement, capability contracts, specialist workforce, workflows, tools, benchmarks, lineage, and operational evidence.
- **Inputs:** Assigned bot profiles, capability records, task requests, division policies, and cross-division dependencies.
- **Outputs:** Division-owned capability plans, task routing, evidence records, workforce status, and dashboard health.
- **Control and measures:** Enforce least privilege, owner/reviewer assignment, cross-division handoff contracts, lifecycle lineage, and no-orphan rules; measure placement confidence, capability coverage, reliability, and benchmark results.
- **Acceptance gate:** Reconcile division identity, assign accountable owner, map bots and capabilities, define interfaces, add tests/benchmarks, and expose status before implementation promotion.
### DIV-13 — DreamFlow

- **Subsystem ID:** `division_dreamflow`
- **Registry identity:** `masterbot-65-registry.json` entry 13.
- **Reconciliation status:** `present_in_45_division_sources`.
- **Mission:** Dedicated division system owning its bot placement, capability contracts, specialist workforce, workflows, tools, benchmarks, lineage, and operational evidence.
- **Inputs:** Assigned bot profiles, capability records, task requests, division policies, and cross-division dependencies.
- **Outputs:** Division-owned capability plans, task routing, evidence records, workforce status, and dashboard health.
- **Control and measures:** Enforce least privilege, owner/reviewer assignment, cross-division handoff contracts, lifecycle lineage, and no-orphan rules; measure placement confidence, capability coverage, reliability, and benchmark results.
- **Acceptance gate:** Reconcile division identity, assign accountable owner, map bots and capabilities, define interfaces, add tests/benchmarks, and expose status before implementation promotion.
### DIV-14 — DreamMarket

- **Subsystem ID:** `division_dreammarket`
- **Registry identity:** `masterbot-65-registry.json` entry 14.
- **Reconciliation status:** `present_in_45_division_sources`.
- **Mission:** Dedicated division system owning its bot placement, capability contracts, specialist workforce, workflows, tools, benchmarks, lineage, and operational evidence.
- **Inputs:** Assigned bot profiles, capability records, task requests, division policies, and cross-division dependencies.
- **Outputs:** Division-owned capability plans, task routing, evidence records, workforce status, and dashboard health.
- **Control and measures:** Enforce least privilege, owner/reviewer assignment, cross-division handoff contracts, lifecycle lineage, and no-orphan rules; measure placement confidence, capability coverage, reliability, and benchmark results.
- **Acceptance gate:** Reconcile division identity, assign accountable owner, map bots and capabilities, define interfaces, add tests/benchmarks, and expose status before implementation promotion.
### DIV-15 — CommandCore

- **Subsystem ID:** `division_commandcore`
- **Registry identity:** `masterbot-65-registry.json` entry 15.
- **Reconciliation status:** `present_in_45_division_sources`.
- **Mission:** Dedicated division system owning its bot placement, capability contracts, specialist workforce, workflows, tools, benchmarks, lineage, and operational evidence.
- **Inputs:** Assigned bot profiles, capability records, task requests, division policies, and cross-division dependencies.
- **Outputs:** Division-owned capability plans, task routing, evidence records, workforce status, and dashboard health.
- **Control and measures:** Enforce least privilege, owner/reviewer assignment, cross-division handoff contracts, lifecycle lineage, and no-orphan rules; measure placement confidence, capability coverage, reliability, and benchmark results.
- **Acceptance gate:** Reconcile division identity, assign accountable owner, map bots and capabilities, define interfaces, add tests/benchmarks, and expose status before implementation promotion.
### DIV-16 — GameTitan

- **Subsystem ID:** `division_gametitan`
- **Registry identity:** `masterbot-65-registry.json` entry 16.
- **Reconciliation status:** `present_in_45_division_sources`.
- **Mission:** Dedicated division system owning its bot placement, capability contracts, specialist workforce, workflows, tools, benchmarks, lineage, and operational evidence.
- **Inputs:** Assigned bot profiles, capability records, task requests, division policies, and cross-division dependencies.
- **Outputs:** Division-owned capability plans, task routing, evidence records, workforce status, and dashboard health.
- **Control and measures:** Enforce least privilege, owner/reviewer assignment, cross-division handoff contracts, lifecycle lineage, and no-orphan rules; measure placement confidence, capability coverage, reliability, and benchmark results.
- **Acceptance gate:** Reconcile division identity, assign accountable owner, map bots and capabilities, define interfaces, add tests/benchmarks, and expose status before implementation promotion.
### DIV-17 — DreamInfluence

- **Subsystem ID:** `division_dreaminfluence`
- **Registry identity:** `masterbot-65-registry.json` entry 17.
- **Reconciliation status:** `present_in_45_division_sources`.
- **Mission:** Dedicated division system owning its bot placement, capability contracts, specialist workforce, workflows, tools, benchmarks, lineage, and operational evidence.
- **Inputs:** Assigned bot profiles, capability records, task requests, division policies, and cross-division dependencies.
- **Outputs:** Division-owned capability plans, task routing, evidence records, workforce status, and dashboard health.
- **Control and measures:** Enforce least privilege, owner/reviewer assignment, cross-division handoff contracts, lifecycle lineage, and no-orphan rules; measure placement confidence, capability coverage, reliability, and benchmark results.
- **Acceptance gate:** Reconcile division identity, assign accountable owner, map bots and capabilities, define interfaces, add tests/benchmarks, and expose status before implementation promotion.
### DIV-18 — DreamDecision

- **Subsystem ID:** `division_dreamdecision`
- **Registry identity:** `masterbot-65-registry.json` entry 18.
- **Reconciliation status:** `present_in_45_division_sources`.
- **Mission:** Dedicated division system owning its bot placement, capability contracts, specialist workforce, workflows, tools, benchmarks, lineage, and operational evidence.
- **Inputs:** Assigned bot profiles, capability records, task requests, division policies, and cross-division dependencies.
- **Outputs:** Division-owned capability plans, task routing, evidence records, workforce status, and dashboard health.
- **Control and measures:** Enforce least privilege, owner/reviewer assignment, cross-division handoff contracts, lifecycle lineage, and no-orphan rules; measure placement confidence, capability coverage, reliability, and benchmark results.
- **Acceptance gate:** Reconcile division identity, assign accountable owner, map bots and capabilities, define interfaces, add tests/benchmarks, and expose status before implementation promotion.
### DIV-19 — DreamOps

- **Subsystem ID:** `division_dreamops`
- **Registry identity:** `masterbot-65-registry.json` entry 19.
- **Reconciliation status:** `present_in_45_division_sources`.
- **Mission:** Dedicated division system owning its bot placement, capability contracts, specialist workforce, workflows, tools, benchmarks, lineage, and operational evidence.
- **Inputs:** Assigned bot profiles, capability records, task requests, division policies, and cross-division dependencies.
- **Outputs:** Division-owned capability plans, task routing, evidence records, workforce status, and dashboard health.
- **Control and measures:** Enforce least privilege, owner/reviewer assignment, cross-division handoff contracts, lifecycle lineage, and no-orphan rules; measure placement confidence, capability coverage, reliability, and benchmark results.
- **Acceptance gate:** Reconcile division identity, assign accountable owner, map bots and capabilities, define interfaces, add tests/benchmarks, and expose status before implementation promotion.
### DIV-20 — DreamPlanetary

- **Subsystem ID:** `division_dreamplanetary`
- **Registry identity:** `masterbot-65-registry.json` entry 20.
- **Reconciliation status:** `present_in_45_division_sources`.
- **Mission:** Dedicated division system owning its bot placement, capability contracts, specialist workforce, workflows, tools, benchmarks, lineage, and operational evidence.
- **Inputs:** Assigned bot profiles, capability records, task requests, division policies, and cross-division dependencies.
- **Outputs:** Division-owned capability plans, task routing, evidence records, workforce status, and dashboard health.
- **Control and measures:** Enforce least privilege, owner/reviewer assignment, cross-division handoff contracts, lifecycle lineage, and no-orphan rules; measure placement confidence, capability coverage, reliability, and benchmark results.
- **Acceptance gate:** Reconcile division identity, assign accountable owner, map bots and capabilities, define interfaces, add tests/benchmarks, and expose status before implementation promotion.
### DIV-21 — DreamEntFinance

- **Subsystem ID:** `division_dreamentfinance`
- **Registry identity:** `masterbot-65-registry.json` entry 21.
- **Reconciliation status:** `present_in_45_division_sources`.
- **Mission:** Dedicated division system owning its bot placement, capability contracts, specialist workforce, workflows, tools, benchmarks, lineage, and operational evidence.
- **Inputs:** Assigned bot profiles, capability records, task requests, division policies, and cross-division dependencies.
- **Outputs:** Division-owned capability plans, task routing, evidence records, workforce status, and dashboard health.
- **Control and measures:** Enforce least privilege, owner/reviewer assignment, cross-division handoff contracts, lifecycle lineage, and no-orphan rules; measure placement confidence, capability coverage, reliability, and benchmark results.
- **Acceptance gate:** Reconcile division identity, assign accountable owner, map bots and capabilities, define interfaces, add tests/benchmarks, and expose status before implementation promotion.
### DIV-22 — DreamCustIntel

- **Subsystem ID:** `division_dreamcustintel`
- **Registry identity:** `masterbot-65-registry.json` entry 22.
- **Reconciliation status:** `present_in_45_division_sources`.
- **Mission:** Dedicated division system owning its bot placement, capability contracts, specialist workforce, workflows, tools, benchmarks, lineage, and operational evidence.
- **Inputs:** Assigned bot profiles, capability records, task requests, division policies, and cross-division dependencies.
- **Outputs:** Division-owned capability plans, task routing, evidence records, workforce status, and dashboard health.
- **Control and measures:** Enforce least privilege, owner/reviewer assignment, cross-division handoff contracts, lifecycle lineage, and no-orphan rules; measure placement confidence, capability coverage, reliability, and benchmark results.
- **Acceptance gate:** Reconcile division identity, assign accountable owner, map bots and capabilities, define interfaces, add tests/benchmarks, and expose status before implementation promotion.
### DIV-23 — DreamLegal

- **Subsystem ID:** `division_dreamlegal`
- **Registry identity:** `masterbot-65-registry.json` entry 23.
- **Reconciliation status:** `present_in_45_division_sources`.
- **Mission:** Dedicated division system owning its bot placement, capability contracts, specialist workforce, workflows, tools, benchmarks, lineage, and operational evidence.
- **Inputs:** Assigned bot profiles, capability records, task requests, division policies, and cross-division dependencies.
- **Outputs:** Division-owned capability plans, task routing, evidence records, workforce status, and dashboard health.
- **Control and measures:** Enforce least privilege, owner/reviewer assignment, cross-division handoff contracts, lifecycle lineage, and no-orphan rules; measure placement confidence, capability coverage, reliability, and benchmark results.
- **Acceptance gate:** Reconcile division identity, assign accountable owner, map bots and capabilities, define interfaces, add tests/benchmarks, and expose status before implementation promotion.
### DIV-24 — DreamCyber

- **Subsystem ID:** `division_dreamcyber`
- **Registry identity:** `masterbot-65-registry.json` entry 24.
- **Reconciliation status:** `present_in_45_division_sources`.
- **Mission:** Dedicated division system owning its bot placement, capability contracts, specialist workforce, workflows, tools, benchmarks, lineage, and operational evidence.
- **Inputs:** Assigned bot profiles, capability records, task requests, division policies, and cross-division dependencies.
- **Outputs:** Division-owned capability plans, task routing, evidence records, workforce status, and dashboard health.
- **Control and measures:** Enforce least privilege, owner/reviewer assignment, cross-division handoff contracts, lifecycle lineage, and no-orphan rules; measure placement confidence, capability coverage, reliability, and benchmark results.
- **Acceptance gate:** Reconcile division identity, assign accountable owner, map bots and capabilities, define interfaces, add tests/benchmarks, and expose status before implementation promotion.
### DIV-25 — DreamHealth

- **Subsystem ID:** `division_dreamhealth`
- **Registry identity:** `masterbot-65-registry.json` entry 25.
- **Reconciliation status:** `present_in_45_division_sources`.
- **Mission:** Dedicated division system owning its bot placement, capability contracts, specialist workforce, workflows, tools, benchmarks, lineage, and operational evidence.
- **Inputs:** Assigned bot profiles, capability records, task requests, division policies, and cross-division dependencies.
- **Outputs:** Division-owned capability plans, task routing, evidence records, workforce status, and dashboard health.
- **Control and measures:** Enforce least privilege, owner/reviewer assignment, cross-division handoff contracts, lifecycle lineage, and no-orphan rules; measure placement confidence, capability coverage, reliability, and benchmark results.
- **Acceptance gate:** Reconcile division identity, assign accountable owner, map bots and capabilities, define interfaces, add tests/benchmarks, and expose status before implementation promotion.
### DIV-26 — DreamEducation

- **Subsystem ID:** `division_dreameducation`
- **Registry identity:** `masterbot-65-registry.json` entry 26.
- **Reconciliation status:** `present_in_45_division_sources`.
- **Mission:** Dedicated division system owning its bot placement, capability contracts, specialist workforce, workflows, tools, benchmarks, lineage, and operational evidence.
- **Inputs:** Assigned bot profiles, capability records, task requests, division policies, and cross-division dependencies.
- **Outputs:** Division-owned capability plans, task routing, evidence records, workforce status, and dashboard health.
- **Control and measures:** Enforce least privilege, owner/reviewer assignment, cross-division handoff contracts, lifecycle lineage, and no-orphan rules; measure placement confidence, capability coverage, reliability, and benchmark results.
- **Acceptance gate:** Reconcile division identity, assign accountable owner, map bots and capabilities, define interfaces, add tests/benchmarks, and expose status before implementation promotion.
### DIV-27 — DreamConstruction

- **Subsystem ID:** `division_dreamconstruction`
- **Registry identity:** `masterbot-65-registry.json` entry 27.
- **Reconciliation status:** `present_in_45_division_sources`.
- **Mission:** Dedicated division system owning its bot placement, capability contracts, specialist workforce, workflows, tools, benchmarks, lineage, and operational evidence.
- **Inputs:** Assigned bot profiles, capability records, task requests, division policies, and cross-division dependencies.
- **Outputs:** Division-owned capability plans, task routing, evidence records, workforce status, and dashboard health.
- **Control and measures:** Enforce least privilege, owner/reviewer assignment, cross-division handoff contracts, lifecycle lineage, and no-orphan rules; measure placement confidence, capability coverage, reliability, and benchmark results.
- **Acceptance gate:** Reconcile division identity, assign accountable owner, map bots and capabilities, define interfaces, add tests/benchmarks, and expose status before implementation promotion.
### DIV-28 — DreamTransport

- **Subsystem ID:** `division_dreamtransport`
- **Registry identity:** `masterbot-65-registry.json` entry 28.
- **Reconciliation status:** `present_in_45_division_sources`.
- **Mission:** Dedicated division system owning its bot placement, capability contracts, specialist workforce, workflows, tools, benchmarks, lineage, and operational evidence.
- **Inputs:** Assigned bot profiles, capability records, task requests, division policies, and cross-division dependencies.
- **Outputs:** Division-owned capability plans, task routing, evidence records, workforce status, and dashboard health.
- **Control and measures:** Enforce least privilege, owner/reviewer assignment, cross-division handoff contracts, lifecycle lineage, and no-orphan rules; measure placement confidence, capability coverage, reliability, and benchmark results.
- **Acceptance gate:** Reconcile division identity, assign accountable owner, map bots and capabilities, define interfaces, add tests/benchmarks, and expose status before implementation promotion.
### DIV-29 — DreamFood

- **Subsystem ID:** `division_dreamfood`
- **Registry identity:** `masterbot-65-registry.json` entry 29.
- **Reconciliation status:** `present_in_45_division_sources`.
- **Mission:** Dedicated division system owning its bot placement, capability contracts, specialist workforce, workflows, tools, benchmarks, lineage, and operational evidence.
- **Inputs:** Assigned bot profiles, capability records, task requests, division policies, and cross-division dependencies.
- **Outputs:** Division-owned capability plans, task routing, evidence records, workforce status, and dashboard health.
- **Control and measures:** Enforce least privilege, owner/reviewer assignment, cross-division handoff contracts, lifecycle lineage, and no-orphan rules; measure placement confidence, capability coverage, reliability, and benchmark results.
- **Acceptance gate:** Reconcile division identity, assign accountable owner, map bots and capabilities, define interfaces, add tests/benchmarks, and expose status before implementation promotion.
### DIV-30 — DreamScience

- **Subsystem ID:** `division_dreamscience`
- **Registry identity:** `masterbot-65-registry.json` entry 30.
- **Reconciliation status:** `present_in_45_division_sources`.
- **Mission:** Dedicated division system owning its bot placement, capability contracts, specialist workforce, workflows, tools, benchmarks, lineage, and operational evidence.
- **Inputs:** Assigned bot profiles, capability records, task requests, division policies, and cross-division dependencies.
- **Outputs:** Division-owned capability plans, task routing, evidence records, workforce status, and dashboard health.
- **Control and measures:** Enforce least privilege, owner/reviewer assignment, cross-division handoff contracts, lifecycle lineage, and no-orphan rules; measure placement confidence, capability coverage, reliability, and benchmark results.
- **Acceptance gate:** Reconcile division identity, assign accountable owner, map bots and capabilities, define interfaces, add tests/benchmarks, and expose status before implementation promotion.
### DIV-31 — DreamArts

- **Subsystem ID:** `division_dreamarts`
- **Registry identity:** `masterbot-65-registry.json` entry 31.
- **Reconciliation status:** `present_in_45_division_sources`.
- **Mission:** Dedicated division system owning its bot placement, capability contracts, specialist workforce, workflows, tools, benchmarks, lineage, and operational evidence.
- **Inputs:** Assigned bot profiles, capability records, task requests, division policies, and cross-division dependencies.
- **Outputs:** Division-owned capability plans, task routing, evidence records, workforce status, and dashboard health.
- **Control and measures:** Enforce least privilege, owner/reviewer assignment, cross-division handoff contracts, lifecycle lineage, and no-orphan rules; measure placement confidence, capability coverage, reliability, and benchmark results.
- **Acceptance gate:** Reconcile division identity, assign accountable owner, map bots and capabilities, define interfaces, add tests/benchmarks, and expose status before implementation promotion.
### DIV-32 — DreamProtection

- **Subsystem ID:** `division_dreamprotection`
- **Registry identity:** `masterbot-65-registry.json` entry 32.
- **Reconciliation status:** `present_in_45_division_sources`.
- **Mission:** Dedicated division system owning its bot placement, capability contracts, specialist workforce, workflows, tools, benchmarks, lineage, and operational evidence.
- **Inputs:** Assigned bot profiles, capability records, task requests, division policies, and cross-division dependencies.
- **Outputs:** Division-owned capability plans, task routing, evidence records, workforce status, and dashboard health.
- **Control and measures:** Enforce least privilege, owner/reviewer assignment, cross-division handoff contracts, lifecycle lineage, and no-orphan rules; measure placement confidence, capability coverage, reliability, and benchmark results.
- **Acceptance gate:** Reconcile division identity, assign accountable owner, map bots and capabilities, define interfaces, add tests/benchmarks, and expose status before implementation promotion.
### DIV-33 — DreamAgriculture

- **Subsystem ID:** `division_dreamagriculture`
- **Registry identity:** `masterbot-65-registry.json` entry 33.
- **Reconciliation status:** `present_in_45_division_sources`.
- **Mission:** Dedicated division system owning its bot placement, capability contracts, specialist workforce, workflows, tools, benchmarks, lineage, and operational evidence.
- **Inputs:** Assigned bot profiles, capability records, task requests, division policies, and cross-division dependencies.
- **Outputs:** Division-owned capability plans, task routing, evidence records, workforce status, and dashboard health.
- **Control and measures:** Enforce least privilege, owner/reviewer assignment, cross-division handoff contracts, lifecycle lineage, and no-orphan rules; measure placement confidence, capability coverage, reliability, and benchmark results.
- **Acceptance gate:** Reconcile division identity, assign accountable owner, map bots and capabilities, define interfaces, add tests/benchmarks, and expose status before implementation promotion.
### DIV-34 — DreamMaintenance

- **Subsystem ID:** `division_dreammaintenance`
- **Registry identity:** `masterbot-65-registry.json` entry 34.
- **Reconciliation status:** `present_in_45_division_sources`.
- **Mission:** Dedicated division system owning its bot placement, capability contracts, specialist workforce, workflows, tools, benchmarks, lineage, and operational evidence.
- **Inputs:** Assigned bot profiles, capability records, task requests, division policies, and cross-division dependencies.
- **Outputs:** Division-owned capability plans, task routing, evidence records, workforce status, and dashboard health.
- **Control and measures:** Enforce least privilege, owner/reviewer assignment, cross-division handoff contracts, lifecycle lineage, and no-orphan rules; measure placement confidence, capability coverage, reliability, and benchmark results.
- **Acceptance gate:** Reconcile division identity, assign accountable owner, map bots and capabilities, define interfaces, add tests/benchmarks, and expose status before implementation promotion.
### DIV-35 — DreamProduction

- **Subsystem ID:** `division_dreamproduction`
- **Registry identity:** `masterbot-65-registry.json` entry 35.
- **Reconciliation status:** `present_in_45_division_sources`.
- **Mission:** Dedicated division system owning its bot placement, capability contracts, specialist workforce, workflows, tools, benchmarks, lineage, and operational evidence.
- **Inputs:** Assigned bot profiles, capability records, task requests, division policies, and cross-division dependencies.
- **Outputs:** Division-owned capability plans, task routing, evidence records, workforce status, and dashboard health.
- **Control and measures:** Enforce least privilege, owner/reviewer assignment, cross-division handoff contracts, lifecycle lineage, and no-orphan rules; measure placement confidence, capability coverage, reliability, and benchmark results.
- **Acceptance gate:** Reconcile division identity, assign accountable owner, map bots and capabilities, define interfaces, add tests/benchmarks, and expose status before implementation promotion.
### DIV-36 — DreamSocial

- **Subsystem ID:** `division_dreamsocial`
- **Registry identity:** `masterbot-65-registry.json` entry 36.
- **Reconciliation status:** `present_in_45_division_sources`.
- **Mission:** Dedicated division system owning its bot placement, capability contracts, specialist workforce, workflows, tools, benchmarks, lineage, and operational evidence.
- **Inputs:** Assigned bot profiles, capability records, task requests, division policies, and cross-division dependencies.
- **Outputs:** Division-owned capability plans, task routing, evidence records, workforce status, and dashboard health.
- **Control and measures:** Enforce least privilege, owner/reviewer assignment, cross-division handoff contracts, lifecycle lineage, and no-orphan rules; measure placement confidence, capability coverage, reliability, and benchmark results.
- **Acceptance gate:** Reconcile division identity, assign accountable owner, map bots and capabilities, define interfaces, add tests/benchmarks, and expose status before implementation promotion.
### DIV-37 — DreamAdmin

- **Subsystem ID:** `division_dreamadmin`
- **Registry identity:** `masterbot-65-registry.json` entry 37.
- **Reconciliation status:** `present_in_45_division_sources`.
- **Mission:** Dedicated division system owning its bot placement, capability contracts, specialist workforce, workflows, tools, benchmarks, lineage, and operational evidence.
- **Inputs:** Assigned bot profiles, capability records, task requests, division policies, and cross-division dependencies.
- **Outputs:** Division-owned capability plans, task routing, evidence records, workforce status, and dashboard health.
- **Control and measures:** Enforce least privilege, owner/reviewer assignment, cross-division handoff contracts, lifecycle lineage, and no-orphan rules; measure placement confidence, capability coverage, reliability, and benchmark results.
- **Acceptance gate:** Reconcile division identity, assign accountable owner, map bots and capabilities, define interfaces, add tests/benchmarks, and expose status before implementation promotion.
### DIV-38 — DreamCrypto

- **Subsystem ID:** `division_dreamcrypto`
- **Registry identity:** `masterbot-65-registry.json` entry 38.
- **Reconciliation status:** `present_in_45_division_sources`.
- **Mission:** Dedicated division system owning its bot placement, capability contracts, specialist workforce, workflows, tools, benchmarks, lineage, and operational evidence.
- **Inputs:** Assigned bot profiles, capability records, task requests, division policies, and cross-division dependencies.
- **Outputs:** Division-owned capability plans, task routing, evidence records, workforce status, and dashboard health.
- **Control and measures:** Enforce least privilege, owner/reviewer assignment, cross-division handoff contracts, lifecycle lineage, and no-orphan rules; measure placement confidence, capability coverage, reliability, and benchmark results.
- **Acceptance gate:** Reconcile division identity, assign accountable owner, map bots and capabilities, define interfaces, add tests/benchmarks, and expose status before implementation promotion.
### DIV-39 — DreamPayments

- **Subsystem ID:** `division_dreampayments`
- **Registry identity:** `masterbot-65-registry.json` entry 39.
- **Reconciliation status:** `present_in_45_division_sources`.
- **Mission:** Dedicated division system owning its bot placement, capability contracts, specialist workforce, workflows, tools, benchmarks, lineage, and operational evidence.
- **Inputs:** Assigned bot profiles, capability records, task requests, division policies, and cross-division dependencies.
- **Outputs:** Division-owned capability plans, task routing, evidence records, workforce status, and dashboard health.
- **Control and measures:** Enforce least privilege, owner/reviewer assignment, cross-division handoff contracts, lifecycle lineage, and no-orphan rules; measure placement confidence, capability coverage, reliability, and benchmark results.
- **Acceptance gate:** Reconcile division identity, assign accountable owner, map bots and capabilities, define interfaces, add tests/benchmarks, and expose status before implementation promotion.
### DIV-40 — DreamBizLaunch

- **Subsystem ID:** `division_dreambizlaunch`
- **Registry identity:** `masterbot-65-registry.json` entry 40.
- **Reconciliation status:** `present_in_45_division_sources`.
- **Mission:** Dedicated division system owning its bot placement, capability contracts, specialist workforce, workflows, tools, benchmarks, lineage, and operational evidence.
- **Inputs:** Assigned bot profiles, capability records, task requests, division policies, and cross-division dependencies.
- **Outputs:** Division-owned capability plans, task routing, evidence records, workforce status, and dashboard health.
- **Control and measures:** Enforce least privilege, owner/reviewer assignment, cross-division handoff contracts, lifecycle lineage, and no-orphan rules; measure placement confidence, capability coverage, reliability, and benchmark results.
- **Acceptance gate:** Reconcile division identity, assign accountable owner, map bots and capabilities, define interfaces, add tests/benchmarks, and expose status before implementation promotion.
### DIV-41 — DreamCodeLab

- **Subsystem ID:** `division_dreamcodelab`
- **Registry identity:** `masterbot-65-registry.json` entry 41.
- **Reconciliation status:** `present_in_45_division_sources`.
- **Mission:** Dedicated division system owning its bot placement, capability contracts, specialist workforce, workflows, tools, benchmarks, lineage, and operational evidence.
- **Inputs:** Assigned bot profiles, capability records, task requests, division policies, and cross-division dependencies.
- **Outputs:** Division-owned capability plans, task routing, evidence records, workforce status, and dashboard health.
- **Control and measures:** Enforce least privilege, owner/reviewer assignment, cross-division handoff contracts, lifecycle lineage, and no-orphan rules; measure placement confidence, capability coverage, reliability, and benchmark results.
- **Acceptance gate:** Reconcile division identity, assign accountable owner, map bots and capabilities, define interfaces, add tests/benchmarks, and expose status before implementation promotion.
### DIV-42 — DreamLoans

- **Subsystem ID:** `division_dreamloans`
- **Registry identity:** `masterbot-65-registry.json` entry 42.
- **Reconciliation status:** `present_in_45_division_sources`.
- **Mission:** Dedicated division system owning its bot placement, capability contracts, specialist workforce, workflows, tools, benchmarks, lineage, and operational evidence.
- **Inputs:** Assigned bot profiles, capability records, task requests, division policies, and cross-division dependencies.
- **Outputs:** Division-owned capability plans, task routing, evidence records, workforce status, and dashboard health.
- **Control and measures:** Enforce least privilege, owner/reviewer assignment, cross-division handoff contracts, lifecycle lineage, and no-orphan rules; measure placement confidence, capability coverage, reliability, and benchmark results.
- **Acceptance gate:** Reconcile division identity, assign accountable owner, map bots and capabilities, define interfaces, add tests/benchmarks, and expose status before implementation promotion.
### DIV-43 — DreamPersonalCare

- **Subsystem ID:** `division_dreampersonalcare`
- **Registry identity:** `masterbot-65-registry.json` entry 43.
- **Reconciliation status:** `present_in_45_division_sources`.
- **Mission:** Dedicated division system owning its bot placement, capability contracts, specialist workforce, workflows, tools, benchmarks, lineage, and operational evidence.
- **Inputs:** Assigned bot profiles, capability records, task requests, division policies, and cross-division dependencies.
- **Outputs:** Division-owned capability plans, task routing, evidence records, workforce status, and dashboard health.
- **Control and measures:** Enforce least privilege, owner/reviewer assignment, cross-division handoff contracts, lifecycle lineage, and no-orphan rules; measure placement confidence, capability coverage, reliability, and benchmark results.
- **Acceptance gate:** Reconcile division identity, assign accountable owner, map bots and capabilities, define interfaces, add tests/benchmarks, and expose status before implementation promotion.
### DIV-44 — DreamMilitary

- **Subsystem ID:** `division_dreammilitary`
- **Registry identity:** `masterbot-65-registry.json` entry 44.
- **Reconciliation status:** `present_in_45_division_sources`.
- **Mission:** Dedicated division system owning its bot placement, capability contracts, specialist workforce, workflows, tools, benchmarks, lineage, and operational evidence.
- **Inputs:** Assigned bot profiles, capability records, task requests, division policies, and cross-division dependencies.
- **Outputs:** Division-owned capability plans, task routing, evidence records, workforce status, and dashboard health.
- **Control and measures:** Enforce least privilege, owner/reviewer assignment, cross-division handoff contracts, lifecycle lineage, and no-orphan rules; measure placement confidence, capability coverage, reliability, and benchmark results.
- **Acceptance gate:** Reconcile division identity, assign accountable owner, map bots and capabilities, define interfaces, add tests/benchmarks, and expose status before implementation promotion.
### DIV-45 — DreamAgents

- **Subsystem ID:** `division_dreamagents`
- **Registry identity:** `masterbot-65-registry.json` entry 45.
- **Reconciliation status:** `present_in_45_division_sources`.
- **Mission:** Dedicated division system owning its bot placement, capability contracts, specialist workforce, workflows, tools, benchmarks, lineage, and operational evidence.
- **Inputs:** Assigned bot profiles, capability records, task requests, division policies, and cross-division dependencies.
- **Outputs:** Division-owned capability plans, task routing, evidence records, workforce status, and dashboard health.
- **Control and measures:** Enforce least privilege, owner/reviewer assignment, cross-division handoff contracts, lifecycle lineage, and no-orphan rules; measure placement confidence, capability coverage, reliability, and benchmark results.
- **Acceptance gate:** Reconcile division identity, assign accountable owner, map bots and capabilities, define interfaces, add tests/benchmarks, and expose status before implementation promotion.
### DIV-46 — DreamResearch

- **Subsystem ID:** `division_dreamresearch`
- **Registry identity:** `masterbot-65-registry.json` entry 46.
- **Reconciliation status:** `present_in_65_registry_not_in_45_audit`.
- **Mission:** Dedicated division system owning its bot placement, capability contracts, specialist workforce, workflows, tools, benchmarks, lineage, and operational evidence.
- **Inputs:** Assigned bot profiles, capability records, task requests, division policies, and cross-division dependencies.
- **Outputs:** Division-owned capability plans, task routing, evidence records, workforce status, and dashboard health.
- **Control and measures:** Enforce least privilege, owner/reviewer assignment, cross-division handoff contracts, lifecycle lineage, and no-orphan rules; measure placement confidence, capability coverage, reliability, and benchmark results.
- **Acceptance gate:** Reconcile division identity, assign accountable owner, map bots and capabilities, define interfaces, add tests/benchmarks, and expose status before implementation promotion.
### DIV-47 — DreamBenchmark

- **Subsystem ID:** `division_dreambenchmark`
- **Registry identity:** `masterbot-65-registry.json` entry 47.
- **Reconciliation status:** `present_in_65_registry_not_in_45_audit`.
- **Mission:** Dedicated division system owning its bot placement, capability contracts, specialist workforce, workflows, tools, benchmarks, lineage, and operational evidence.
- **Inputs:** Assigned bot profiles, capability records, task requests, division policies, and cross-division dependencies.
- **Outputs:** Division-owned capability plans, task routing, evidence records, workforce status, and dashboard health.
- **Control and measures:** Enforce least privilege, owner/reviewer assignment, cross-division handoff contracts, lifecycle lineage, and no-orphan rules; measure placement confidence, capability coverage, reliability, and benchmark results.
- **Acceptance gate:** Reconcile division identity, assign accountable owner, map bots and capabilities, define interfaces, add tests/benchmarks, and expose status before implementation promotion.
### DIV-48 — DreamKnowledge

- **Subsystem ID:** `division_dreamknowledge`
- **Registry identity:** `masterbot-65-registry.json` entry 48.
- **Reconciliation status:** `present_in_65_registry_not_in_45_audit`.
- **Mission:** Dedicated division system owning its bot placement, capability contracts, specialist workforce, workflows, tools, benchmarks, lineage, and operational evidence.
- **Inputs:** Assigned bot profiles, capability records, task requests, division policies, and cross-division dependencies.
- **Outputs:** Division-owned capability plans, task routing, evidence records, workforce status, and dashboard health.
- **Control and measures:** Enforce least privilege, owner/reviewer assignment, cross-division handoff contracts, lifecycle lineage, and no-orphan rules; measure placement confidence, capability coverage, reliability, and benchmark results.
- **Acceptance gate:** Reconcile division identity, assign accountable owner, map bots and capabilities, define interfaces, add tests/benchmarks, and expose status before implementation promotion.
### DIV-49 — DreamEvolution

- **Subsystem ID:** `division_dreamevolution`
- **Registry identity:** `masterbot-65-registry.json` entry 49.
- **Reconciliation status:** `present_in_65_registry_not_in_45_audit`.
- **Mission:** Dedicated division system owning its bot placement, capability contracts, specialist workforce, workflows, tools, benchmarks, lineage, and operational evidence.
- **Inputs:** Assigned bot profiles, capability records, task requests, division policies, and cross-division dependencies.
- **Outputs:** Division-owned capability plans, task routing, evidence records, workforce status, and dashboard health.
- **Control and measures:** Enforce least privilege, owner/reviewer assignment, cross-division handoff contracts, lifecycle lineage, and no-orphan rules; measure placement confidence, capability coverage, reliability, and benchmark results.
- **Acceptance gate:** Reconcile division identity, assign accountable owner, map bots and capabilities, define interfaces, add tests/benchmarks, and expose status before implementation promotion.
### DIV-50 — DreamIntegration

- **Subsystem ID:** `division_dreamintegration`
- **Registry identity:** `masterbot-65-registry.json` entry 50.
- **Reconciliation status:** `present_in_65_registry_not_in_45_audit`.
- **Mission:** Dedicated division system owning its bot placement, capability contracts, specialist workforce, workflows, tools, benchmarks, lineage, and operational evidence.
- **Inputs:** Assigned bot profiles, capability records, task requests, division policies, and cross-division dependencies.
- **Outputs:** Division-owned capability plans, task routing, evidence records, workforce status, and dashboard health.
- **Control and measures:** Enforce least privilege, owner/reviewer assignment, cross-division handoff contracts, lifecycle lineage, and no-orphan rules; measure placement confidence, capability coverage, reliability, and benchmark results.
- **Acceptance gate:** Reconcile division identity, assign accountable owner, map bots and capabilities, define interfaces, add tests/benchmarks, and expose status before implementation promotion.
### DIV-51 — DreamReason

- **Subsystem ID:** `division_dreamreason`
- **Registry identity:** `masterbot-65-registry.json` entry 51.
- **Reconciliation status:** `present_in_65_registry_not_in_45_audit`.
- **Mission:** Dedicated division system owning its bot placement, capability contracts, specialist workforce, workflows, tools, benchmarks, lineage, and operational evidence.
- **Inputs:** Assigned bot profiles, capability records, task requests, division policies, and cross-division dependencies.
- **Outputs:** Division-owned capability plans, task routing, evidence records, workforce status, and dashboard health.
- **Control and measures:** Enforce least privilege, owner/reviewer assignment, cross-division handoff contracts, lifecycle lineage, and no-orphan rules; measure placement confidence, capability coverage, reliability, and benchmark results.
- **Acceptance gate:** Reconcile division identity, assign accountable owner, map bots and capabilities, define interfaces, add tests/benchmarks, and expose status before implementation promotion.
### DIV-52 — DreamWorld

- **Subsystem ID:** `division_dreamworld`
- **Registry identity:** `masterbot-65-registry.json` entry 52.
- **Reconciliation status:** `present_in_65_registry_not_in_45_audit`.
- **Mission:** Dedicated division system owning its bot placement, capability contracts, specialist workforce, workflows, tools, benchmarks, lineage, and operational evidence.
- **Inputs:** Assigned bot profiles, capability records, task requests, division policies, and cross-division dependencies.
- **Outputs:** Division-owned capability plans, task routing, evidence records, workforce status, and dashboard health.
- **Control and measures:** Enforce least privilege, owner/reviewer assignment, cross-division handoff contracts, lifecycle lineage, and no-orphan rules; measure placement confidence, capability coverage, reliability, and benchmark results.
- **Acceptance gate:** Reconcile division identity, assign accountable owner, map bots and capabilities, define interfaces, add tests/benchmarks, and expose status before implementation promotion.
### DIV-53 — DreamVision

- **Subsystem ID:** `division_dreamvision`
- **Registry identity:** `masterbot-65-registry.json` entry 53.
- **Reconciliation status:** `present_in_65_registry_not_in_45_audit`.
- **Mission:** Dedicated division system owning its bot placement, capability contracts, specialist workforce, workflows, tools, benchmarks, lineage, and operational evidence.
- **Inputs:** Assigned bot profiles, capability records, task requests, division policies, and cross-division dependencies.
- **Outputs:** Division-owned capability plans, task routing, evidence records, workforce status, and dashboard health.
- **Control and measures:** Enforce least privilege, owner/reviewer assignment, cross-division handoff contracts, lifecycle lineage, and no-orphan rules; measure placement confidence, capability coverage, reliability, and benchmark results.
- **Acceptance gate:** Reconcile division identity, assign accountable owner, map bots and capabilities, define interfaces, add tests/benchmarks, and expose status before implementation promotion.
### DIV-54 — DreamVoice

- **Subsystem ID:** `division_dreamvoice`
- **Registry identity:** `masterbot-65-registry.json` entry 54.
- **Reconciliation status:** `present_in_65_registry_not_in_45_audit`.
- **Mission:** Dedicated division system owning its bot placement, capability contracts, specialist workforce, workflows, tools, benchmarks, lineage, and operational evidence.
- **Inputs:** Assigned bot profiles, capability records, task requests, division policies, and cross-division dependencies.
- **Outputs:** Division-owned capability plans, task routing, evidence records, workforce status, and dashboard health.
- **Control and measures:** Enforce least privilege, owner/reviewer assignment, cross-division handoff contracts, lifecycle lineage, and no-orphan rules; measure placement confidence, capability coverage, reliability, and benchmark results.
- **Acceptance gate:** Reconcile division identity, assign accountable owner, map bots and capabilities, define interfaces, add tests/benchmarks, and expose status before implementation promotion.
### DIV-55 — DreamHuman

- **Subsystem ID:** `division_dreamhuman`
- **Registry identity:** `masterbot-65-registry.json` entry 55.
- **Reconciliation status:** `present_in_65_registry_not_in_45_audit`.
- **Mission:** Dedicated division system owning its bot placement, capability contracts, specialist workforce, workflows, tools, benchmarks, lineage, and operational evidence.
- **Inputs:** Assigned bot profiles, capability records, task requests, division policies, and cross-division dependencies.
- **Outputs:** Division-owned capability plans, task routing, evidence records, workforce status, and dashboard health.
- **Control and measures:** Enforce least privilege, owner/reviewer assignment, cross-division handoff contracts, lifecycle lineage, and no-orphan rules; measure placement confidence, capability coverage, reliability, and benchmark results.
- **Acceptance gate:** Reconcile division identity, assign accountable owner, map bots and capabilities, define interfaces, add tests/benchmarks, and expose status before implementation promotion.
### DIV-56 — DreamSecurity

- **Subsystem ID:** `division_dreamsecurity`
- **Registry identity:** `masterbot-65-registry.json` entry 56.
- **Reconciliation status:** `present_in_65_registry_not_in_45_audit`.
- **Mission:** Dedicated division system owning its bot placement, capability contracts, specialist workforce, workflows, tools, benchmarks, lineage, and operational evidence.
- **Inputs:** Assigned bot profiles, capability records, task requests, division policies, and cross-division dependencies.
- **Outputs:** Division-owned capability plans, task routing, evidence records, workforce status, and dashboard health.
- **Control and measures:** Enforce least privilege, owner/reviewer assignment, cross-division handoff contracts, lifecycle lineage, and no-orphan rules; measure placement confidence, capability coverage, reliability, and benchmark results.
- **Acceptance gate:** Reconcile division identity, assign accountable owner, map bots and capabilities, define interfaces, add tests/benchmarks, and expose status before implementation promotion.
### DIV-57 — DreamProduct

- **Subsystem ID:** `division_dreamproduct`
- **Registry identity:** `masterbot-65-registry.json` entry 57.
- **Reconciliation status:** `present_in_65_registry_not_in_45_audit`.
- **Mission:** Dedicated division system owning its bot placement, capability contracts, specialist workforce, workflows, tools, benchmarks, lineage, and operational evidence.
- **Inputs:** Assigned bot profiles, capability records, task requests, division policies, and cross-division dependencies.
- **Outputs:** Division-owned capability plans, task routing, evidence records, workforce status, and dashboard health.
- **Control and measures:** Enforce least privilege, owner/reviewer assignment, cross-division handoff contracts, lifecycle lineage, and no-orphan rules; measure placement confidence, capability coverage, reliability, and benchmark results.
- **Acceptance gate:** Reconcile division identity, assign accountable owner, map bots and capabilities, define interfaces, add tests/benchmarks, and expose status before implementation promotion.
### DIV-58 — DreamOperations

- **Subsystem ID:** `division_dreamoperations`
- **Registry identity:** `masterbot-65-registry.json` entry 58.
- **Reconciliation status:** `present_in_65_registry_not_in_45_audit`.
- **Mission:** Dedicated division system owning its bot placement, capability contracts, specialist workforce, workflows, tools, benchmarks, lineage, and operational evidence.
- **Inputs:** Assigned bot profiles, capability records, task requests, division policies, and cross-division dependencies.
- **Outputs:** Division-owned capability plans, task routing, evidence records, workforce status, and dashboard health.
- **Control and measures:** Enforce least privilege, owner/reviewer assignment, cross-division handoff contracts, lifecycle lineage, and no-orphan rules; measure placement confidence, capability coverage, reliability, and benchmark results.
- **Acceptance gate:** Reconcile division identity, assign accountable owner, map bots and capabilities, define interfaces, add tests/benchmarks, and expose status before implementation promotion.
### DIV-59 — DreamStrategy

- **Subsystem ID:** `division_dreamstrategy`
- **Registry identity:** `masterbot-65-registry.json` entry 59.
- **Reconciliation status:** `present_in_65_registry_not_in_45_audit`.
- **Mission:** Dedicated division system owning its bot placement, capability contracts, specialist workforce, workflows, tools, benchmarks, lineage, and operational evidence.
- **Inputs:** Assigned bot profiles, capability records, task requests, division policies, and cross-division dependencies.
- **Outputs:** Division-owned capability plans, task routing, evidence records, workforce status, and dashboard health.
- **Control and measures:** Enforce least privilege, owner/reviewer assignment, cross-division handoff contracts, lifecycle lineage, and no-orphan rules; measure placement confidence, capability coverage, reliability, and benchmark results.
- **Acceptance gate:** Reconcile division identity, assign accountable owner, map bots and capabilities, define interfaces, add tests/benchmarks, and expose status before implementation promotion.
### DIV-60 — DreamExperiment

- **Subsystem ID:** `division_dreamexperiment`
- **Registry identity:** `masterbot-65-registry.json` entry 60.
- **Reconciliation status:** `present_in_65_registry_not_in_45_audit`.
- **Mission:** Dedicated division system owning its bot placement, capability contracts, specialist workforce, workflows, tools, benchmarks, lineage, and operational evidence.
- **Inputs:** Assigned bot profiles, capability records, task requests, division policies, and cross-division dependencies.
- **Outputs:** Division-owned capability plans, task routing, evidence records, workforce status, and dashboard health.
- **Control and measures:** Enforce least privilege, owner/reviewer assignment, cross-division handoff contracts, lifecycle lineage, and no-orphan rules; measure placement confidence, capability coverage, reliability, and benchmark results.
- **Acceptance gate:** Reconcile division identity, assign accountable owner, map bots and capabilities, define interfaces, add tests/benchmarks, and expose status before implementation promotion.
### DIV-61 — DreamSimulation

- **Subsystem ID:** `division_dreamsimulation`
- **Registry identity:** `masterbot-65-registry.json` entry 61.
- **Reconciliation status:** `present_in_65_registry_not_in_45_audit`.
- **Mission:** Dedicated division system owning its bot placement, capability contracts, specialist workforce, workflows, tools, benchmarks, lineage, and operational evidence.
- **Inputs:** Assigned bot profiles, capability records, task requests, division policies, and cross-division dependencies.
- **Outputs:** Division-owned capability plans, task routing, evidence records, workforce status, and dashboard health.
- **Control and measures:** Enforce least privilege, owner/reviewer assignment, cross-division handoff contracts, lifecycle lineage, and no-orphan rules; measure placement confidence, capability coverage, reliability, and benchmark results.
- **Acceptance gate:** Reconcile division identity, assign accountable owner, map bots and capabilities, define interfaces, add tests/benchmarks, and expose status before implementation promotion.
### DIV-62 — DreamDiscovery

- **Subsystem ID:** `division_dreamdiscovery`
- **Registry identity:** `masterbot-65-registry.json` entry 62.
- **Reconciliation status:** `present_in_65_registry_not_in_45_audit`.
- **Mission:** Dedicated division system owning its bot placement, capability contracts, specialist workforce, workflows, tools, benchmarks, lineage, and operational evidence.
- **Inputs:** Assigned bot profiles, capability records, task requests, division policies, and cross-division dependencies.
- **Outputs:** Division-owned capability plans, task routing, evidence records, workforce status, and dashboard health.
- **Control and measures:** Enforce least privilege, owner/reviewer assignment, cross-division handoff contracts, lifecycle lineage, and no-orphan rules; measure placement confidence, capability coverage, reliability, and benchmark results.
- **Acceptance gate:** Reconcile division identity, assign accountable owner, map bots and capabilities, define interfaces, add tests/benchmarks, and expose status before implementation promotion.
### DIV-63 — DreamQuality

- **Subsystem ID:** `division_dreamquality`
- **Registry identity:** `masterbot-65-registry.json` entry 63.
- **Reconciliation status:** `present_in_65_registry_not_in_45_audit`.
- **Mission:** Dedicated division system owning its bot placement, capability contracts, specialist workforce, workflows, tools, benchmarks, lineage, and operational evidence.
- **Inputs:** Assigned bot profiles, capability records, task requests, division policies, and cross-division dependencies.
- **Outputs:** Division-owned capability plans, task routing, evidence records, workforce status, and dashboard health.
- **Control and measures:** Enforce least privilege, owner/reviewer assignment, cross-division handoff contracts, lifecycle lineage, and no-orphan rules; measure placement confidence, capability coverage, reliability, and benchmark results.
- **Acceptance gate:** Reconcile division identity, assign accountable owner, map bots and capabilities, define interfaces, add tests/benchmarks, and expose status before implementation promotion.
### DIV-64 — DreamResource

- **Subsystem ID:** `division_dreamresource`
- **Registry identity:** `masterbot-65-registry.json` entry 64.
- **Reconciliation status:** `present_in_65_registry_not_in_45_audit`.
- **Mission:** Dedicated division system owning its bot placement, capability contracts, specialist workforce, workflows, tools, benchmarks, lineage, and operational evidence.
- **Inputs:** Assigned bot profiles, capability records, task requests, division policies, and cross-division dependencies.
- **Outputs:** Division-owned capability plans, task routing, evidence records, workforce status, and dashboard health.
- **Control and measures:** Enforce least privilege, owner/reviewer assignment, cross-division handoff contracts, lifecycle lineage, and no-orphan rules; measure placement confidence, capability coverage, reliability, and benchmark results.
- **Acceptance gate:** Reconcile division identity, assign accountable owner, map bots and capabilities, define interfaces, add tests/benchmarks, and expose status before implementation promotion.
### DIV-65 — DreamFuture

- **Subsystem ID:** `division_dreamfuture`
- **Registry identity:** `masterbot-65-registry.json` entry 65.
- **Reconciliation status:** `present_in_65_registry_not_in_45_audit`.
- **Mission:** Dedicated division system owning its bot placement, capability contracts, specialist workforce, workflows, tools, benchmarks, lineage, and operational evidence.
- **Inputs:** Assigned bot profiles, capability records, task requests, division policies, and cross-division dependencies.
- **Outputs:** Division-owned capability plans, task routing, evidence records, workforce status, and dashboard health.
- **Control and measures:** Enforce least privilege, owner/reviewer assignment, cross-division handoff contracts, lifecycle lineage, and no-orphan rules; measure placement confidence, capability coverage, reliability, and benchmark results.
- **Acceptance gate:** Reconcile division identity, assign accountable owner, map bots and capabilities, define interfaces, add tests/benchmarks, and expose status before implementation promotion.


## 11.1 Division reconciliation gate

Before any division count is declared canonical, compare the 45-entry placement audit, the 46-division legacy-lineage description, the 65-entry master registry, the bot manifest/capability registry, and the current generated division catalog. Preserve all historical names and mappings. Record explicit aliases, merged identities, retired divisions, or unresolved candidates with evidence and owner approval. Never delete a division or reassign its bots solely to make counts agree.

## 12. Current category-system inventory (derived snapshot)

The primary registry's current system total and per-source counts are computed from the source registries at validation time. The displayed sections are a snapshot, not a permanent inventory or fixed architecture ceiling.

A companion taxonomy registry adds individually specified systems across the additional taxonomy groups discovered in source registries, including opportunity-resource categories, web-source domains, universal capability domains, software capability categories, model-matrix dimensions, learning and bootcamp stages, government-service domains, tools, skills, vibe-coding categories, and technology-discovery sources. A third task taxonomy registry separately covers human-AI task actions, domains, contexts, modalities, execution environments, quality dimensions, business/personal scenarios, and Markdown implementation-gap states.

- **Primary category systems:** computed from the current primary registry.
- **Additional taxonomy systems:** computed from the current additional registry.
- **Task and Markdown taxonomy systems:** computed from the task taxonomy registry.
- **Combined documented category systems:** derived from all three current registries.
- **Dedicated documentation sections:** generated from current source categories; no fixed count or ceiling.

Division inventories in older README, rebuild, audit, and lineage documents disagree. The validator now compares the current master registry with the current placement audit and computes the unmatched records dynamically; legacy file names and historical counts are not treated as permanent limits.

These totals cover the inspected source files and taxonomy definitions, not every possible repository-wide resource, bot, integration, or sibling-repository asset. Continue expanding the inventory as additional authoritative sources are discovered.


## 13. GitHub Pages category-system dashboard

The category-system inventory is exposed through `website/category-systems.html` and `website/category-systems.js`. The dashboard loads the primary, additional, and task/Markdown taxonomy registries and presents the combined current inventory with group filters, search, individual expandable records, source links, and lifecycle/verification states. The published data mirrors are `website/data/category-system-registry.json`, `website/data/additional-taxonomy-system-registry.json`, and `website/data/task-taxonomy-system-registry.json`.

The command `npm run buddy:category-systems` runs all three registry validators and the open-vocabulary vibe-coding taxonomy validator. Each registry is checked against its source catalogs, documentation sections, and published Pages mirror. Counts are recomputed from the source catalogs. The dashboard is a read-only visibility surface; it does not grant runtime permissions or imply that catalogued systems are implemented.


## 14. Additional taxonomy registry (open and extensible)

The companion file `config/buddy/additional-taxonomy-system-registry.json` and its detailed section-by-section documentation in `docs/BUDDY_ADDITIONAL_TAXONOMY_SYSTEMS.md` preserve the additional category systems currently discovered across the source taxonomies. Their source registries remain distinct; no aliasing or merging is inferred from similar names.


## 15. Living AI/technology discovery and Markdown gap closure

The repository now has a source-driven AI and technology radar at `website/technology-radar.html`. Its extensible source registry is `config/buddy/technology-discovery-policy.json`; `tools/refresh_buddy_technology_radar.py` refreshes RSS, research, public model/space APIs, GitHub repository search, and remote-work listings into an append-only, timestamped catalog. Counts and facets are derived from the current records. Source failures preserve the last good records, and all discoveries remain unverified leads until checked. The radar prioritizes vibe coding, coding agents, AI app builders, home businesses, remote work, freelancing, creator businesses, digital products, e-commerce, sales/marketing, agents, model infrastructure, robotics, and security/governance. Its scheduled workflow runs after merge to the default branch; source refreshes do not purchase services, contact employers, submit applications, or promise earnings.

The Markdown-to-implementation gap audit scans every tracked Markdown file, maps linked paths to implementation/tests/workflows/configuration, and highlights missing or untested references. Its dashboard is `website/markdown-gap-audit.html`; its policy is `config/buddy/markdown-implementation-gap-policy.json`. A code or test reference is not proof of a passing test. Actual execution, benchmark, regression, and production evidence remain separate gates.

Both inventories are open-vocabulary and versioned. No tool, model, provider, category, task, document, or reference count is a permanent ceiling. Historical records remain traceable; stale entries are marked rather than silently deleted.


## 16. Task and Markdown taxonomy systems

The third machine-readable catalog, `config/buddy/task-taxonomy-system-registry.json`, contains separate systems for the human-AI task sandbox and Markdown implementation-gap policy. Its individual sections are in `docs/BUDDY_TASK_AND_MARKDOWN_TAXONOMY_SYSTEMS.md`, and its GitHub Pages mirror is `website/data/task-taxonomy-system-registry.json`. The dashboard combines this catalog with the primary and additional taxonomy registries. These systems remain catalogued specifications until their individual interfaces, owners, tests, and evidence exist.
