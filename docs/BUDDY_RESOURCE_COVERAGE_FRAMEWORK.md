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

The inspected study-resource set contains 94 rows and the following 70 distinct category labels. Keep the original labels in source data; normalize only in derived indexes so no category is silently lost.

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
- all 94 study-resource rows represented, preserving all 70 distinct labels;
- all 20 AI model categories represented;
- every new research item tagged to at least one category and one Buddy capability or explicit “monitor only” disposition.

**Current limitation:** this document records the categories observed in the inspected source files. It does not claim that every repository, every Markdown file, every division, every bot, every external resource, or every sibling-repository asset has already been audited. Expand the crosswalk as those authoritative inventories are inspected.
