# Markdown-to-Implementation Gap Audit

Generated: 2026-11-24T04:51:19Z

This is a live inventory of Git-tracked Markdown requirements and their linked repository paths. Counts are computed from the current Git tree; no document, claim, or reference count is a fixed ceiling.

## Current derived summary

- Markdown documents scanned: 1663
- Actionable claim lines detected: 11851
- Documents with missing path references: 109
- Documents without implementation references: 1580
- Documents with implementation references but no test references: 67
- Documents with inventory count claims: 108
- Inventory count claims requiring review: 378

## Fixed-count claims requiring review

- .agents/memory/MEMORY.md:1 — - [Tool-belt upgrade pattern](tool-belt-upgrade.md) — shared/tool-belt.ts is injected into ALL 1,051+ bot prompts; upgrading it is the highest-leverage single-file change in the empire.
- .agents/memory/ai-cost-optimization.md:35 — **Why:** The system has 1,051 bots all using the same OpenAI integration; unbounded history + expensive models would balloon costs fast. All savings compound across every user session.
- .agents/memory/tool-belt-upgrade.md:3 — description: shared/tool-belt.ts is injected into every bot's system prompt via buildEnhancedSystemPrompt(); upgrading it simultaneously upgrades all 1,051+ bots.
- ARCHITECTURE.md:7 — The goal is not to make 1,000 bots independently clever. The goal is to build **shared intelligence once and reuse it everywhere**.
- README.md:111 — The Model Benchmark Lab audits 200 targets across 12 capability suites: 100 curated catalog records plus 100 task-specific discovery lanes that refresh exact model IDs from official provider catalogs. Catalog checks run locally. Live quality, latency, and cost scores remain empty
- README.md:111 — The Model Benchmark Lab audits 200 targets across 12 capability suites: 100 curated catalog records plus 100 task-specific discovery lanes that refresh exact model IDs from official provider catalogs. Catalog checks run locally. Live quality, latency, and cost scores remain empty
- SYSTEM_ARCHITECTURE.md:4 — DreamCo Empire OS is a 6-layer autonomous wealth-generation system orchestrating over 875+ AI bots across 45 divisions (including the new DreamAgents autonomous agent division). Its primary purpose is revenue generation through a SaaS model, covering a vast array of job categorie
- SYSTEM_ARCHITECTURE.md:19 — - **Modular Design**: The system is structured into 45 divisions, each comprising multiple specialized AI bots, allowing for scalability and clear separation of concerns.
- SYSTEM_ARCHITECTURE.md:31 — - Dedicated pages for Dashboard, Divisions, Bots, Autonomy, Chat (with Plan/Build/Execute/Teach mode selector), Ecosystem, Orchestration, Marketplace (with Plugins tab), Formulas, Deals, Debug, Learning Matrix, AI Leaders (Top 100 AI companies), AI Models Hub (100 models with fre
- SYSTEM_ARCHITECTURE.md:32 — - **Universal Tool Belt** (`shared/tool-belt.ts`): Runtime-injected system prompt enhancement giving all 857 bots entrepreneurship tools, AI safety principles, mode-specific instructions, and Top 100 AI companies context. Uses `buildEnhancedSystemPrompt()` to compose final prompt
- SYSTEM_ARCHITECTURE.md:39 — - `server/seed-bots.ts` — 884 original DreamCo bots across all 45 divisions
- SYSTEM_ARCHITECTURE.md:40 — - `server/seed-github-bots.ts` — 67 bots merged from github.com/DreamCo-Technologies/Dreamcobots (App_bots + specialty bots from bots/ directory)
- SYSTEM_ARCHITECTURE.md:43 — - **Buddy Bot** (`slug: buddy-bot`, `server/seed-buddy-bot.ts`) — Elite CommandCore master coding brain. System prompt covers 500+ libraries across every language, framework, and tool in existence. All 1,051 bots are wired to route coding tasks through Buddy. Always upserted on s
- bots/resource-eligibility-bot.md:1 — # 211 Resource Eligibility Bot
- bots/resource-eligibility-bot.md:43 — You are 211 Resource Eligibility Bot, a specialized AI bot in the DreamCo Empire OS DreamPersonalCare division. Helps individuals find and qualify for local social services, benefits programs, housing assistance, and emergency resources. Core capabilities: Local resource database
- bots/resource-eligibility-bot.md:47 — Test every declared capability for 211 Resource Eligibility Bot in sandbox mode: Local resource database; Eligibility screening; Application guidance; Benefits gap analysis; Housing assistance finder; Food assistance locator; Mental health resource referral; Crisis intervention r
- buddy/openrouter/README.md:13 — OpenRouter currently advertises 500+ models and 80+ providers, with provider routing and model fallback support. OpenRouter also supports provider controls such as data-collection restrictions and ZDR where available.
- buddy/openrouter/README.md:13 — OpenRouter currently advertises 500+ models and 80+ providers, with provider routing and model fallback support. OpenRouter also supports provider controls such as data-collection restrictions and ZDR where available.
- buddy/openrouter/README.md:22 — -> DreamCo 500+ model catalog
- data/dreamco_knowledge/assets/_candidates/edu_cs_11.0701/v3/README.md:60 — - Quotes: all 6,102 generated items quote their O*NET 31.0 task verbatim (0 mismatches) with the correct SOC/Task ID pair.
- data/dreamco_knowledge/assets/_candidates/edu_cs_11.0701/v4/README.md:38 — ## 2–3. Merchant changes (untracked; diff against `<workspace>/edu-v3-scratch/*.before.*`)
- data/dreamco_knowledge/packages/DP-ONET-OCC-SYN/0.0.2/sample/occupation_cards.md:7 — ## 11-3012.00 Administrative Services Managers
- data/dreamco_knowledge/packages/DP-ONET-OCC-SYN/0.0.2/sample/occupation_cards.md:14 — ## 11-3051.01 Quality Control Systems Managers
- data/dreamco_knowledge/packages/DP-ONET-OCC-SYN/0.0.2/sample/occupation_cards.md:21 — ## 13-1071.00 Human Resources Specialists
- data/dreamco_knowledge/packages/DP-ONET-OCC-SYN/0.0.2/sample/occupation_cards.md:28 — ## 13-1081.01 Logistics Engineers
- data/dreamco_knowledge/packages/DP-ONET-OCC-SYN/0.0.2/sample/occupation_cards.md:35 — ## 15-2041.00 Statisticians
- data/dreamco_knowledge/packages/DP-ONET-OCC-SYN/0.0.2/sample/occupation_cards.md:42 — ## 15-2051.02 Clinical Data Managers
- data/dreamco_knowledge/packages/DP-ONET-OCC-SYN/0.0.2/sample/occupation_cards.md:49 — ## 17-1011.00 Architects, Except Landscape and Naval
- data/dreamco_knowledge/packages/DP-ONET-OCC-SYN/0.0.2/sample/occupation_cards.md:56 — ## 17-2141.01 Fuel Cell Engineers
- data/dreamco_knowledge/packages/DP-ONET-OCC-SYN/0.0.2/sample/occupation_cards.md:63 — ## 19-3039.02 Neuropsychologists
- data/dreamco_knowledge/packages/DP-ONET-OCC-SYN/0.0.2/sample/occupation_cards.md:70 — ## 19-4099.01 Quality Control Analysts
- data/dreamco_knowledge/packages/DP-ONET-OCC-SYN/0.0.2/sample/occupation_cards.md:77 — ## 21-1013.00 Marriage and Family Therapists
- data/dreamco_knowledge/packages/DP-ONET-OCC-SYN/0.0.2/sample/occupation_cards.md:84 — ## 21-1022.00 Healthcare Social Workers
- data/dreamco_knowledge/packages/DP-ONET-OCC-SYN/0.0.2/sample/occupation_cards.md:91 — ## 23-1012.00 Judicial Law Clerks
- data/dreamco_knowledge/packages/DP-ONET-OCC-SYN/0.0.2/sample/occupation_cards.md:98 — ## 23-1021.00 Administrative Law Judges, Adjudicators, and Hearing Officers
- data/dreamco_knowledge/packages/DP-ONET-OCC-SYN/0.0.2/sample/occupation_cards.md:105 — ## 25-1082.00 Library Science Teachers, Postsecondary
- data/dreamco_knowledge/packages/DP-ONET-OCC-SYN/0.0.2/sample/occupation_cards.md:112 — ## 25-1111.00 Criminal Justice and Law Enforcement Teachers, Postsecondary
- data/dreamco_knowledge/packages/DP-ONET-OCC-SYN/0.0.2/sample/occupation_cards.md:119 — ## 27-1012.00 Craft Artists
- data/dreamco_knowledge/packages/DP-ONET-OCC-SYN/0.0.2/sample/occupation_cards.md:126 — ## 27-3023.00 News Analysts, Reporters, and Journalists
- data/dreamco_knowledge/packages/DP-ONET-OCC-SYN/0.0.2/sample/occupation_cards.md:133 — ## 29-2053.00 Psychiatric Technicians
- data/dreamco_knowledge/packages/DP-ONET-OCC-SYN/0.0.2/sample/occupation_cards.md:140 — ## 29-2091.00 Orthotists and Prosthetists
- data/dreamco_knowledge/packages/DP-ONET-OCC-SYN/0.0.2/sample/occupation_cards.md:147 — ## 31-9092.00 Medical Assistants
- data/dreamco_knowledge/packages/DP-ONET-OCC-SYN/0.0.2/sample/occupation_cards.md:154 — ## 31-9099.02 Endoscopy Technicians
- data/dreamco_knowledge/packages/DP-ONET-OCC-SYN/0.0.2/sample/occupation_cards.md:161 — ## 33-3011.00 Bailiffs
- data/dreamco_knowledge/packages/DP-ONET-OCC-SYN/0.0.2/sample/occupation_cards.md:168 — ## 33-9092.00 Lifeguards, Ski Patrol, and Other Recreational Protective Service Workers
- data/dreamco_knowledge/packages/DP-ONET-OCC-SYN/0.0.2/sample/occupation_cards.md:175 — ## 35-2015.00 Cooks, Short Order
- data/dreamco_knowledge/packages/DP-ONET-OCC-SYN/0.0.2/sample/occupation_cards.md:182 — ## 35-3023.00 Fast Food and Counter Workers
- data/dreamco_knowledge/packages/DP-ONET-OCC-SYN/0.0.2/sample/occupation_cards.md:189 — ## 37-2021.00 Pest Control Workers
- data/dreamco_knowledge/packages/DP-ONET-OCC-SYN/0.0.2/sample/occupation_cards.md:196 — ## 37-3012.00 Pesticide Handlers, Sprayers, and Applicators, Vegetation
- data/dreamco_knowledge/packages/DP-ONET-OCC-SYN/0.0.2/sample/occupation_cards.md:203 — ## 39-3021.00 Motion Picture Projectionists
- data/dreamco_knowledge/packages/DP-ONET-OCC-SYN/0.0.2/sample/occupation_cards.md:210 — ## 39-3091.00 Amusement and Recreation Attendants
- data/dreamco_knowledge/packages/DP-ONET-OCC-SYN/0.0.2/sample/occupation_cards.md:217 — ## 41-9031.00 Sales Engineers
- data/dreamco_knowledge/packages/DP-ONET-OCC-SYN/0.0.2/sample/occupation_cards.md:224 — ## 41-9041.00 Telemarketers
- data/dreamco_knowledge/packages/DP-ONET-OCC-SYN/0.0.2/sample/occupation_cards.md:231 — ## 43-5053.00 Postal Service Mail Sorters, Processors, and Processing Machine Operators
- data/dreamco_knowledge/packages/DP-ONET-OCC-SYN/0.0.2/sample/occupation_cards.md:238 — ## 43-5061.00 Production, Planning, and Expediting Clerks
- data/dreamco_knowledge/packages/DP-ONET-OCC-SYN/0.0.2/sample/occupation_cards.md:245 — ## 45-1011.00 First-Line Supervisors of Farming, Fishing, and Forestry Workers
- data/dreamco_knowledge/packages/DP-ONET-OCC-SYN/0.0.2/sample/occupation_cards.md:252 — ## 45-2093.00 Farmworkers, Farm, Ranch, and Aquacultural Animals
- data/dreamco_knowledge/packages/DP-ONET-OCC-SYN/0.0.2/sample/occupation_cards.md:259 — ## 47-2121.00 Glaziers
- data/dreamco_knowledge/packages/DP-ONET-OCC-SYN/0.0.2/sample/occupation_cards.md:266 — ## 47-5023.00 Earth Drillers, Except Oil and Gas
- data/dreamco_knowledge/packages/DP-ONET-OCC-SYN/0.0.2/sample/occupation_cards.md:273 — ## 49-3042.00 Mobile Heavy Equipment Mechanics, Except Engines
- data/dreamco_knowledge/packages/DP-ONET-OCC-SYN/0.0.2/sample/occupation_cards.md:280 — ## 49-9098.00 Helpers--Installation, Maintenance, and Repair Workers
- data/dreamco_knowledge/packages/DP-ONET-OCC-SYN/0.0.2/sample/occupation_cards.md:287 — ## 51-6041.00 Shoe and Leather Workers and Repairers
- data/dreamco_knowledge/packages/DP-ONET-OCC-SYN/0.0.2/sample/occupation_cards.md:294 — ## 51-9195.00 Molders, Shapers, and Casters, Except Metal and Plastic
- data/dreamco_knowledge/packages/DP-ONET-OCC-SYN/0.0.2/sample/occupation_cards.md:301 — ## 53-3032.00 Heavy and Tractor-Trailer Truck Drivers
- data/dreamco_knowledge/packages/DP-ONET-OCC-SYN/0.0.2/sample/occupation_cards.md:308 — ## 53-6031.00 Automotive and Watercraft Service Attendants
- docs/BUDDY_1000_SOURCE_BOT_TRAINING_GROUND.md:34 — Buddy must not treat all 1000 sources equally. At task time it ranks sources using:
- docs/BUDDY_1000_SOURCE_BOT_TRAINING_GROUND.md:79 — - Do not use 1000 sources for a problem that only needs two authoritative sources.
- docs/BUDDY_14_DAY_MODEL_GROWTH_PLAN.md:5 — **Not a promise:** frontier GPT-5 capability, a production-ready 25M model, or a full DreamCo fleet certification cannot be guaranteed by a date. Completion is evidence-gated.
- docs/BUDDY_24H_GAP_CLOSURE.md:9 — - Target throughput: 1,000 source-learning jobs per week.
- docs/BUDDY_65_MASTERBOT_OPERATING_SYSTEM.md:10 — - **65 Division MasterBots** — domain owners. The 65-division registry in the product/repository is the source of truth for names and ownership; this document does not invent replacement division names.
- docs/BUDDY_ACTIONS_ENGINE.md:5 — Make the Actions page the operational command center for Buddy: a goal-driven execution system that plans, previews, executes, verifies, observes, recovers and learns from work across the 46 Division Superbots, capability registry, device fabric and external tools.
- docs/BUDDY_ACTIONS_UNIFIED_OPERATING_SYSTEM.md:9 — - all 45 divisions
- docs/BUDDY_ADDITIONAL_TAXONOMY_SYSTEMS.md:9029 — ## 211 Source Priority
- docs/BUDDY_ADDITIONAL_TAXONOMY_SYSTEMS.md:9035 — - **Mission:** Dedicated 211 source priority subsystem for "official federal/state/local/tribal/territorial agency sources".
- docs/BUDDY_ADDITIONAL_TAXONOMY_SYSTEMS.md:9052 — - **Mission:** Dedicated 211 source priority subsystem for "USA.gov and official benefit/service directories".
- docs/BUDDY_ADDITIONAL_TAXONOMY_SYSTEMS.md:9069 — - **Mission:** Dedicated 211 source priority subsystem for "authorized 211/local community-resource directories".
- docs/BUDDY_ADDITIONAL_TAXONOMY_SYSTEMS.md:9086 — - **Mission:** Dedicated 211 source priority subsystem for "official agency APIs/data feeds".
- docs/BUDDY_ADDITIONAL_TAXONOMY_SYSTEMS.md:9103 — - **Mission:** Dedicated 211 source priority subsystem for "verified nonprofit/service-provider sources".
- docs/BUDDY_AUTOMATIC_BOT_ONBOARDING.md:55 — The classifier compares the bot against the canonical 46 divisions and existing capabilities. A high-confidence match is assigned automatically. Ambiguous matches become review items while remaining visible.
- docs/BUDDY_BOOTCAMP_AND_TRUST_FRAMEWORK.md:45 — The 500 model slots form a diverse review team rather than a single unquestioning agent. Roles include monitoring, training, evaluation, building, security, alignment, research, product, documentation, and red-team review.
- docs/BUDDY_GITHUB_COMPETITOR_MASTER_PLAN.md:171 — This repository already contains substantial infrastructure for the direction, including Buddy success/governance systems, benchmark tracking, model progress tooling, local repository integration, self-repair tooling, and dedicated Buddy pages. The generated success program curre
- docs/BUDDY_GITHUB_COMPETITOR_MASTER_PLAN.md:171 — This repository already contains substantial infrastructure for the direction, including Buddy success/governance systems, benchmark tracking, model progress tooling, local repository integration, self-repair tooling, and dedicated Buddy pages. The generated success program curre
- docs/BUDDY_PLATFORM_READINESS_SCORECARD.md:96 — All 18 categories in `docs/BUDDY_GITHUB_COMPETITOR_MASTER_PLAN.md` have current evidence.
- docs/BUDDY_REPOSITORY_REPAIR_DATASETS_BENCHMARKS_AND_DISTILLATION.md:58 — These are routing defaults, not a claim that the whole 65-to-45 division mapping is finalized.
- docs/BUDDY_RESOURCE_COVERAGE_FRAMEWORK.md:454 — The inspected `AI_MODEL_CATEGORIES` list has 20 categories:
- docs/BUDDY_RESOURCE_COVERAGE_FRAMEWORK.md:543 — - all 23 resource-registry IDs represented;
- docs/BUDDY_RESOURCE_COVERAGE_FRAMEWORK.md:1521 — ## 8.2 Category isolation and collaboration rules
- docs/BUDDY_RESOURCE_COVERAGE_FRAMEWORK.md:5531 — ## 11.1 Division reconciliation gate
- docs/BUDDY_RESOURCE_MAP.md:29 — ## Top 15 resources for Buddy (ranked)
- docs/BUDDY_RESOURCE_MAP.md:38 — | 6 | `study_packs` | study_packs/ (12 capability packs with sources, evals, SFT/DPO recipes) | Curated per-capability curricula and eval sets (instruct, code, reason, tools, research, safety, embed, rerank, vision, speech, translate, summarize). | **needs_owner_decision** | - |
- docs/BUDDY_RESOURCE_MAP.md:41 — | 9 | `github_actions` | GitHub Actions on Dreamcobots (146 workflows registered, GitHub-hosted runners, 0 self-hosted) | Scheduled and dispatchable compute for checks, catalogs, benchmarks and Pages builds. GITHUB_TOKEN is available to every workflow. | **connected** | - |
- docs/BUDDY_RESOURCE_MAP.md:53 — | - | `github_discussions` | GitHub Discussions on Dreamcobots (enabled, 6 categories, 0 threads) | A possible public Q&A and feedback channel for Buddy users and evals. | **needs_owner_decision** | - |
- docs/BUDDY_RESOURCE_MAP.md:73 — ## Grok teammate lanes (box-local roster, about 112 bots)
- docs/BUDDY_USER_TESTING_CATALOG.md:19 — | 45 divisions | Repository coverage exists | READY-USER | Test one primary workflow per division |
- docs/BUDDY_VIBE_CODING_REVERSE_ENGINEERING_DISTILLATION_AND_TRAINING.md:58 — The 65 MasterBot registry and 45-domain taxonomy must be reconciled using an authoritative crosswalk. Until then, do not invent ownership or claim all 45 divisions have a verified mapping.
- docs/CONVERSATION_SYSTEM_INTEGRATION_SPEC.md:41 — ## 8. 65 division dashboards
- docs/DREAMCO_BUDDY_MASTER_CODEX_DIRECTIVE.md:215 — One benchmark workflow succeeding does NOT prove all 500 models were benchmarked.
- docs/DREAMCO_BUDDY_MASTER_CODEX_DIRECTIVE.md:475 — Do NOT manually create 1,000 pages.
- docs/DREAMCO_BUDDY_MASTER_CODEX_DIRECTIVE.md:509 — The project historically had 45 divisions and later expanded to approximately 65.
- docs/DREAMCO_BUDDY_MASTER_CODEX_DIRECTIVE.md:1320 — DreamCo wants to track approximately 500 models and AI companies.
- docs/DREAMCO_BUDDY_MASTER_CODEX_DIRECTIVE.md:1372 — Do not report "500 models updated" unless 500 unique records were actually processed.
- docs/DREAMCO_BUDDY_MASTER_CODEX_DIRECTIVE.md:1432 — The project historically contained approximately 1,051 bots across 45 divisions and later expanded toward 65 divisions.
- docs/DREAMCO_BUDDY_MASTER_CODEX_DIRECTIVE.md:1432 — The project historically contained approximately 1,051 bots across 45 divisions and later expanded toward 65 divisions.
- docs/DREAMCO_BUDDY_MASTER_CODEX_DIRECTIVE.md:1432 — The project historically contained approximately 1,051 bots across 45 divisions and later expanded toward 65 divisions.
- docs/DREAMCO_BUDDY_MASTER_CODEX_DIRECTIVE.md:3727 — 500 models
- docs/DREAMCO_BUDDY_MASTER_CODEX_DIRECTIVE.md:3733 — 1,000 resources
- docs/DREAMCO_BUDDY_MASTER_CODEX_DIRECTIVE.md:6957 — simple task → 1 model
- docs/DREAMCO_DELIVERY_PLAN.md:35 — The canonical registry has 1,051 profiles. Fifty additional growth profiles now have separate catalog entries and shared sandbox task routes. Their original descriptions, capability lists and source files remain preserved. The 262 historical source records include these 50 and th
- docs/DREAMCO_DIVISION_MODEL_COMPETITIVENESS.md:50 — This PR adds the policy and a deterministic fleet-profile builder. It does not train 65 models, provision GPUs, create provider credentials, or prove model competitiveness. The first execution target is to generate all 65 model profiles, then reconcile the authoritative 45-domain
- docs/DREAMCO_DIVISION_MODEL_COMPETITIVENESS.md:50 — This PR adds the policy and a deterministic fleet-profile builder. It does not train 65 models, provision GPUs, create provider credentials, or prove model competitiveness. The first execution target is to generate all 65 model profiles, then reconcile the authoritative 45-domain
- docs/DREAMCO_MASTERY_CONTINUITY_SYSTEM.md:92 — The new engine connects all 65 registry entries to logical lanes, goal routing, dependency metadata, shared regression execution, the existing lane planner, benchmark execution, and evidence artifacts. It does **not** yet implement every domain capability, execute every historica
- docs/DREAMCO_MASTER_ROADMAP_2026.md:26 — ### 1–15 Workflow Organization & Dashboard
- docs/DREAMCO_MASTER_ROADMAP_2026.md:26 — ### 1–15 Workflow Organization & Dashboard
- docs/DREAMCO_MASTER_ROADMAP_2026.md:44 — ### 16–30 CI/CD & Deployment
- docs/DREAMCO_MASTER_ROADMAP_2026.md:62 — ### 31–50 Intelligence & Learning
- docs/DREAMCO_MASTER_ROADMAP_2026.md:85 — ### 51–65 Revenue & Governance
- docs/DREAMCO_MASTER_ROADMAP_2026.md:103 — ### 66–80 Community, Observability & DevEx
- docs/DREAMCO_MASTER_ROADMAP_2026.md:121 — ### 81–95 Advanced Innovation
- docs/DREAMCO_MASTER_ROADMAP_2026.md:139 — ### 96–100 Transformative
- docs/DREAMCO_REBUILD_V2.md:12 — 2. One canonical division registry drives all 45 divisions.
- docs/DREAMCO_REBUILD_V2.md:19 — 9. All 1,051 bot profiles must pass the same validation contract.
- docs/DREAMCO_REBUILD_V2.md:85 — ### Phase 3 — 45 divisions / 1,051 bots
- docs/DREAMCO_REBUILD_V2.md:85 — ### Phase 3 — 45 divisions / 1,051 bots
- docs/DREAMCO_REBUILD_V2.md:327 — 6. Generate a gap report across all 1,051 bots.
- docs/FLEET_ONE_WEEK_BUILD_PLAN.md:3 — Source of truth: `config/bots/build-queue.json` (checked by `tests/test_build_queue.py`). Starting point is the audit in #13731: 1232 bots (1213 TESTED, 19 SPEC_ONLY), all 55 App_bots divisions TESTED by the division smoke, 200 Pages (189 working, 10 stub, 1 broken), 105 workflow
- docs/FLEET_ONE_WEEK_BUILD_PLAN.md:3 — Source of truth: `config/bots/build-queue.json` (checked by `tests/test_build_queue.py`). Starting point is the audit in #13731: 1232 bots (1213 TESTED, 19 SPEC_ONLY), all 55 App_bots divisions TESTED by the division smoke, 200 Pages (189 working, 10 stub, 1 broken), 105 workflow
- docs/FLEET_ONE_WEEK_BUILD_PLAN.md:3 — Source of truth: `config/bots/build-queue.json` (checked by `tests/test_build_queue.py`). Starting point is the audit in #13731: 1232 bots (1213 TESTED, 19 SPEC_ONLY), all 55 App_bots divisions TESTED by the division smoke, 200 Pages (189 working, 10 stub, 1 broken), 105 workflow
- docs/GAIN_PRODUCTION_PIPELINE_PLAN.md:8 — 1101 bots, 56 divisions, `production_ready_true: 0`.
- docs/GAIN_PRODUCTION_PIPELINE_PLAN.md:8 — 1101 bots, 56 divisions, `production_ready_true: 0`.
- docs/GROK_CAPABILITIES_FOR_DREAMCO.md:162 — 118. Pretend 1,051 bots are all fully implemented runtimes
- docs/HUGGINGFACE_MASTERY_PLAN.md:48 — For each pack below, pick **3 datasets + 2 models + 1 eval suite**. Not 300.
- docs/LEGACY_BOT_LINEAGE_AND_DIVISION_MAP.md:5 — Preserve every historical DreamCo bot as an accounted-for capability, worker, alias, retired implementation or unresolved item while consolidating the runtime architecture around 46 Division Superbots and Buddy.
- docs/LEGACY_BOT_LINEAGE_AND_DIVISION_MAP.md:12 — └── 46 Division Superbots
- docs/LEGACY_BOT_LINEAGE_AND_DIVISION_MAP.md:86 — - all 46 divisions;
- docs/NEXT_100_OWNER_UPGRADES.md:45 — 29. Add a large-task-list virtualized UI that can display 100,000 tasks without freezing.
- docs/PR_INTEGRATION_LEDGER_2026-08-12.md:69 — **Decision:** rebuild against current `main`. This overlaps the older #446 Pages proposal, but #476 is the newer and more comprehensive implementation.
- docs/REPOSITORY_IMPROVEMENT_SUGGESTIONS.md:3 — Prioritized, concrete suggestions based on repository structure: 1,051 bot profiles, heavy Actions surface, Buddy governance, website + client/server, and CI-generated issue flood.
- docs/REPOSITORY_IMPROVEMENT_SUGGESTIONS.md:169 — 128. 10 division sandbox packs with evidence
- docs/REPOSITORY_OWNER_GUIDE.md:33 — The existing system map declares 1,051 specialist records across 45 divisions and a completion queue of 232. These are generated repository declarations, not independently verified production counts. Use the [build readiness page](https://dreamco-technologies.github.io/Dreamcobot
- docs/REPOSITORY_OWNER_GUIDE.md:43 — 7. **Some documentation and generated snapshots lag behind source.** The README previously described 26 pages although the baseline had 94. Prefer regenerated inventories and the actual files over old counts.
- docs/SUPERBOT_MIGRATION_PLAN.md:4 — Stop expanding standalone bots. The repository already reports **1,051 catalog profiles across 45 divisions**. The architecture will now make **every division a Superbot** while preserving all specialist bots as capability modules.
- docs/SUPERBOT_MIGRATION_PLAN.md:15 — └── 45 Division Superbots
- docs/SUPERBOT_MIGRATION_PLAN.md:24 — ### 45 Division Superbots
- docs/SUPERBOT_MIGRATION_PLAN.md:110 — - 45 Division Superbots are canonical.
- docs/UNIVERSAL_BOT_RUNTIME_CONTRACT.md:8 — DreamCo has ~1,120 bot profiles (`bots/*.md`, `App_bots/<Division>.json`,
- docs/UNIVERSAL_BOT_RUNTIME_CONTRACT.md:21 — | 3 | capabilities | ≥1 bot-specific capability. Tier packaging (“Advanced analytics dashboard”, “Priority email support”, “API access”…) is dropped and counted in `tier_features_dropped` |
- docs/UNMERGEABLE_PR_RECONCILIATION_2026-08-12.md:53 — Preserves the core #476 Pages capability of routing browser `/api`, `/ws`, and `/socket` traffic to a configured HTTPS/WSS backend while leaving normal local development behavior unchanged.
- docs/VIBE_CODING_CATEGORY_MAP.md:44 — ## 31–40: XR, simulation, infrastructure, data and productivity
- docs/VIBE_CODING_CATEGORY_MAP.md:57 — ## 41–50: Civic, professional, industrial and physical-world systems
- docs/adr/0001-superbot-operating-model.md:8 — DreamCo has grown into a large ecosystem of divisions, bot profiles, workflows, tools, experiments, notes and product surfaces. The repository's README currently describes 1,051+ bot profiles across 45 divisions, while the owner has identified additional bot material outside the 
- docs/adr/0001-superbot-operating-model.md:8 — DreamCo has grown into a large ecosystem of divisions, bot profiles, workflows, tools, experiments, notes and product surfaces. The repository's README currently describes 1,051+ bot profiles across 45 divisions, while the owner has identified additional bot material outside the 
- docs/architecture/PROPRIETARY_DIVISION_MODEL_PROGRAM.md:64 — B. Pilot 3 divisions with distinct modalities/domains; prove reproducible small-model fine-tuning and independent deployment.
- docs/benchmarks/BENCHMARKS_801_1000.md:181 — - **977 agent recovery benchmark** — recovery from failed tasks.
- docs/benchmarks/BENCHMARKS_801_1000.md:182 — - **978 agent planning benchmark** — long-horizon execution.
- docs/benchmarks/BENCHMARKS_801_1000.md:187 — - **983 skill-tree benchmark** — capability organization.
- docs/benchmarks/BENCHMARKS_801_1000.md:189 — - **985 source-discovery benchmark** — source ranking.
- docs/benchmarks/BENCHMARKS_801_1000.md:192 — - **988 capability-generation benchmark** — building missing tools.
- docs/benchmarks/BENCHMARKS_801_1000.md:195 — - **991 task-decomposition benchmark** — turning goals into plans.
- docs/benchmarks/BENCHMARKS_801_1000.md:196 — - **992 tool-selection benchmark** — selecting the best tool.
- docs/benchmarks/BENCHMARKS_801_1000.md:198 — - **994 model-routing benchmark** — selecting the model for the task.
- docs/dreamco-lite/DREAMCO_LITE_MVP.md:9 — - **2 bots**
- docs/dreampayments_benchmark.md:12 — ## 30 capability scorecard
- docs/engineering/DREAMCO_PROJECT_CHAT_CORPUS.md:23 — | LIB-MD-001 | `Pasted markdown.md` | `file_00000000ec84822fa5494193f142c5c9` | Read; 644 lines. Historical conversation transcript covering learning techniques, thinking strategies, repository organization, ChatGPT/GitHub integrations, GitLab/AWS/Ansible/Terraform/Kubernetes/Gra
- docs/engineering/PR_RECONCILIATION_LEDGER.md:75 — - Useful work: proposes caller identity checks on 14 model routes, plan-policy enforcement, allowlist-only model selection, owner-only discovery, paid-use approval, and UI fallback/sign-in notices with tests.
- docs/top-200-ideas-set-02.md:5 — ## 201–225 Systems & architecture
- docs/top-200-ideas-set-02.md:5 — ## 201–225 Systems & architecture
- docs/top-200-ideas-set-02.md:32 — ## 226–250 Memory & cognition
- docs/top-200-ideas-set-02.md:59 — ## 251–275 Planning & optimization
- docs/top-200-ideas-set-02.md:86 — ## 276–300 Simulation & digital twins
- docs/top-200-ideas-set-02.md:113 — ## 301–325 Data intelligence
- docs/top-200-ideas-set-02.md:140 — ## 326–350 AI/model intelligence
- docs/top-200-ideas-set-02.md:167 — ## 351–375 Knowledge & reasoning
- docs/top-200-ideas-set-02.md:194 — ## 376–400 Agent operations
- docs/top-200-ideas-set-02.md:194 — ## 376–400 Agent operations
- eval/edu_benchmark/README.md:40 — 4. **Benchmark Gap Planner has no data.** `benchmark-scores.json` is absent on main (404 @5ba09f2). Every scheduled "green" run (e.g. 37065929919, 37032509096 on 2026-10-02) reports 65/65 divisions as `RUN_BENCHMARKS` / "no measured evidence". Green means the job ran; no gaps wer
- original-bots/README.md:10 — | `autonomous-income-network/` | All 200 original Autonomous Income Bots (8 categories) |
- original-bots/README.md:13 — ## 🤖 Autonomous Income Bot Network (200 Bots)
- original-bots/autonomous-income-network/category-8-services-global.md:37 — - **200 bots** across 8 income categories
- reports/BOT_CALCULATORS.md:21 — - `car_flip`: 1 bots
- reports/BOT_CALCULATORS.md:22 — - `cash_flow`: 55 bots
- reports/BOT_CALCULATORS.md:23 — - `commerce_margin`: 20 bots
- reports/BOT_CALCULATORS.md:24 — - `creative_project`: 66 bots
- reports/BOT_CALCULATORS.md:25 — - `learning_outcomes`: 62 bots
- reports/BOT_CALCULATORS.md:26 — - `operations_efficiency`: 110 bots
- reports/BOT_CALCULATORS.md:27 — - `project_estimate`: 39 bots
- reports/BOT_CALCULATORS.md:28 — - `real_estate_flip`: 25 bots
- reports/BOT_CALCULATORS.md:29 — - `research_value`: 30 bots
- reports/BOT_CALCULATORS.md:30 — - `risk_reduction`: 246 bots
- reports/BOT_CALCULATORS.md:31 — - `sales_funnel`: 112 bots
- reports/BOT_CALCULATORS.md:32 — - `software_unit_economics`: 250 bots
- reports/BOT_CALCULATORS.md:33 — - `subscription`: 35 bots
- reports/BOT_PRODUCTION_READINESS.md:31 — - **CommandCore**: 13 bots (App_bots/CommandCore.json)
- reports/BOT_PRODUCTION_READINESS.md:32 — - **DreamAIInfra**: 25 bots (App_bots/DreamAIInfra.json)
- reports/BOT_PRODUCTION_READINESS.md:33 — - **DreamAdmin**: 21 bots (App_bots/DreamAdmin.json)
- reports/BOT_PRODUCTION_READINESS.md:34 — - **DreamAffiliate**: 5 bots (App_bots/DreamAffiliate.json)
- reports/BOT_PRODUCTION_READINESS.md:35 — - **DreamAgency**: 5 bots (App_bots/DreamAgency.json)
- reports/BOT_PRODUCTION_READINESS.md:36 — - **DreamAgents**: 20 bots (App_bots/DreamAgents.json)
- reports/BOT_PRODUCTION_READINESS.md:37 — - **DreamAgriculture**: 20 bots (App_bots/DreamAgriculture.json)
- reports/BOT_PRODUCTION_READINESS.md:38 — - **DreamArts**: 18 bots (App_bots/DreamArts.json)
- reports/BOT_PRODUCTION_READINESS.md:39 — - **DreamAutomation**: 21 bots (App_bots/DreamAutomation.json)
- reports/BOT_PRODUCTION_READINESS.md:40 — - **DreamBizLaunch**: 21 bots (App_bots/DreamBizLaunch.json)
- reports/BOT_PRODUCTION_READINESS.md:41 — - **DreamCodeLab**: 146 bots (App_bots/DreamCodeLab.json)
- reports/BOT_PRODUCTION_READINESS.md:42 — - **DreamConstruction**: 19 bots (App_bots/DreamConstruction.json)
- reports/BOT_PRODUCTION_READINESS.md:43 — - **DreamContent**: 16 bots (App_bots/DreamContent.json)
- reports/BOT_PRODUCTION_READINESS.md:44 — - **DreamCrypto**: 20 bots (App_bots/DreamCrypto.json)
- reports/BOT_PRODUCTION_READINESS.md:45 — - **DreamCustIntel**: 25 bots (App_bots/DreamCustIntel.json)
- reports/BOT_PRODUCTION_READINESS.md:46 — - **DreamCyber**: 25 bots (App_bots/DreamCyber.json)
- reports/BOT_PRODUCTION_READINESS.md:47 — - **DreamData**: 16 bots (App_bots/DreamData.json)
- reports/BOT_PRODUCTION_READINESS.md:48 — - **DreamDecision**: 25 bots (App_bots/DreamDecision.json)
- reports/BOT_PRODUCTION_READINESS.md:49 — - **DreamEducation**: 20 bots (App_bots/DreamEducation.json)
- reports/BOT_PRODUCTION_READINESS.md:50 — - **DreamEmpire**: 5 bots (App_bots/DreamEmpire.json)
- reports/BOT_PRODUCTION_READINESS.md:51 — - **DreamEntFinance**: 25 bots (App_bots/DreamEntFinance.json)
- reports/BOT_PRODUCTION_READINESS.md:52 — - **DreamFinance**: 25 bots (App_bots/DreamFinance.json)
- reports/BOT_PRODUCTION_READINESS.md:53 — - **DreamFlow**: 5 bots (App_bots/DreamFlow.json)
- reports/BOT_PRODUCTION_READINESS.md:54 — - **DreamFood**: 20 bots (App_bots/DreamFood.json)
- reports/BOT_PRODUCTION_READINESS.md:55 — - **DreamFoundry**: 5 bots (App_bots/DreamFoundry.json)
- reports/BOT_PRODUCTION_READINESS.md:56 — - **DreamFranchise**: 5 bots (App_bots/DreamFranchise.json)
- reports/BOT_PRODUCTION_READINESS.md:57 — - **DreamGlobal**: 16 bots (App_bots/DreamGlobal.json)
- reports/BOT_PRODUCTION_READINESS.md:58 — - **DreamHealth**: 20 bots (App_bots/DreamHealth.json)
- reports/BOT_PRODUCTION_READINESS.md:59 — - **DreamInfluence**: 25 bots (App_bots/DreamInfluence.json)
- reports/BOT_PRODUCTION_READINESS.md:60 — - **DreamIntegrations**: 5 bots (App_bots/DreamIntegrations.json)
- reports/BOT_PRODUCTION_READINESS.md:61 — - **DreamLegal**: 25 bots (App_bots/DreamLegal.json)
- reports/BOT_PRODUCTION_READINESS.md:62 — - **DreamLicensing**: 5 bots (App_bots/DreamLicensing.json)
- reports/BOT_PRODUCTION_READINESS.md:63 — - **DreamLoans**: 23 bots (App_bots/DreamLoans.json)
- reports/BOT_PRODUCTION_READINESS.md:64 — - **DreamMaintenance**: 21 bots (App_bots/DreamMaintenance.json)
- reports/BOT_PRODUCTION_READINESS.md:65 — - **DreamMarket**: 5 bots (App_bots/DreamMarket.json)
- reports/BOT_PRODUCTION_READINESS.md:66 — - **DreamMilitary**: 20 bots (App_bots/DreamMilitary.json)
- reports/BOT_PRODUCTION_READINESS.md:67 — - **DreamOps**: 26 bots (App_bots/DreamOps.json)
- reports/BOT_PRODUCTION_READINESS.md:68 — - **DreamPayments**: 23 bots (App_bots/DreamPayments.json)
- reports/BOT_PRODUCTION_READINESS.md:69 — - **DreamPersonalCare**: 30 bots (App_bots/DreamPersonalCare.json)
- reports/BOT_PRODUCTION_READINESS.md:70 — - **DreamPlanetary**: 25 bots (App_bots/DreamPlanetary.json)
- reports/BOT_PRODUCTION_READINESS.md:71 — - **DreamProServices**: 25 bots (App_bots/DreamProServices.json)
- reports/BOT_PRODUCTION_READINESS.md:72 — - **DreamProduction**: 20 bots (App_bots/DreamProduction.json)
- reports/BOT_PRODUCTION_READINESS.md:73 — - **DreamProtection**: 20 bots (App_bots/DreamProtection.json)
- reports/BOT_PRODUCTION_READINESS.md:74 — - **DreamRealEstate**: 25 bots (App_bots/DreamRealEstate.json)
- reports/BOT_PRODUCTION_READINESS.md:75 — - **DreamRetail**: 26 bots (App_bots/DreamRetail.json)
- reports/BOT_PRODUCTION_READINESS.md:76 — - **DreamRobotics**: 5 bots (App_bots/DreamRobotics.json)
- reports/BOT_PRODUCTION_READINESS.md:77 — - **DreamSaaS**: 5 bots (App_bots/DreamSaaS.json)
- reports/BOT_PRODUCTION_READINESS.md:78 — - **DreamSalesPro**: 37 bots (App_bots/DreamSalesPro.json)
- reports/BOT_PRODUCTION_READINESS.md:79 — - **DreamScience**: 20 bots (App_bots/DreamScience.json)
- reports/BOT_PRODUCTION_READINESS.md:80 — - **DreamSocial**: 33 bots (App_bots/DreamSocial.json)
- reports/BOT_PRODUCTION_READINESS.md:81 — - **DreamStreaming**: 5 bots (App_bots/DreamStreaming.json)
- reports/BOT_PRODUCTION_READINESS.md:82 — - **DreamTrade**: 12 bots (App_bots/DreamTrade.json)
- reports/BOT_PRODUCTION_READINESS.md:83 — - **DreamTransport**: 19 bots (App_bots/DreamTransport.json)
- reports/BOT_PRODUCTION_READINESS.md:84 — - **DreamTravel**: 5 bots (App_bots/DreamTravel.json)
- reports/BOT_PRODUCTION_READINESS.md:85 — - **GameTitan**: 4 bots (App_bots/GameTitan.json)
- reports/BOT_PRODUCTION_READINESS.md:86 — - **MasterbotProfilesExcluded**: 0 bots (App_bots/masterbots-46-65.json)
- reports/BUDDY_BENCHMARK_INDEX.md:19 — - **Daily division contract benchmarks** (45 divisions): `local_contract_runner_ready_live_competitors_required`
- reports/BUDDY_LOCAL_OWNER_AND_MODEL_LAB.md:10 — - The generated benchmark catalog contains 200 targets across 94 providers, 24 categories, and 12 evaluation suites. The second 100 are official-catalog discovery lanes, not invented model records or live scores.
- reports/BUDDY_LOCAL_OWNER_AND_MODEL_LAB.md:10 — - The generated benchmark catalog contains 200 targets across 94 providers, 24 categories, and 12 evaluation suites. The second 100 are official-catalog discovery lanes, not invented model records or live scores.
- reports/BUDDY_RESOURCE_LIST.md:35 — - 1,101 bot files in bots.
- reports/CAPABILITY_WORKBENCH_VALIDATION.md:12 — - Refreshed page audit: 224 pages, 216 wired, one partial, seven server-dependent
- reports/CERTIFY_FIRST_ORDER.md:17 — | 6 | `plan-prod-readiness-master` (PRC) | Grok-PRC-Certifier | partial | 0/1101 bots `production_ready`; PRC 0 verified / 16 partial / 3 unknown | No newer PRC count found on main | Proof of every PRC item: 0 are verified, 16 are partial and 3 are unknown. The roadmap's Definiti
- reports/CERTIFY_FIRST_ORDER.md:20 — | 9 | `plan-universal-sandbox-programs` (Universal sandbox) | Grok-Universal-Sandbox-Director | partial | 0/1101 `sandbox_test_defined` | **New since snapshot:** `5ba09f2ea` (2026-10-02 12:09 CDT) added `benchmarks/resource_mastery/{sandbox.py,test_sandbox.py}`, and `7ce5b6a2e` (
- reports/CERTIFY_FIRST_ORDER.md:75 — The full cron list is in `/home/box/roadmap/_crons.json` (55 schedules across 90 workflow files on main; all 90 parse with PyYAML).
- reports/CHAT_VS_REPO_TRUTH.md:16 — - Beginner Buddy engine exists; the full 200 skill records are not all committed.
- reports/DAILY_APPROVAL_LIST.md:34 — - #8925 Pages mirrors: Goals, desks, sources, learn, devices, OS
- reports/DATA_PACKAGE_LICENSE_QA_REVIEW.md:63 — | S21 | NCES CIP 2020 resources (CIP–SOC crosswalk) | https://nces.ed.gov/ipeds/cipcode/resources.aspx?y=56 | 2026-10-05 (file: https://nces.ed.gov/ipeds/cipcode/Files/CIP2020_SOC2018_Crosswalk.xlsx, HTTP 200) |
- reports/DATA_PACKAGE_WEEK1_EVIDENCE.md:125 — - `python3 tools/build_universal_work_ai_catalog.py` ran in the worktree: **ok**, about 15 s, 1,016 occupations, 18,796 tasks, 26,683,062 bytes.
- reports/DATA_PACKAGE_WEEK1_EVIDENCE.md:129 — - **31.0 compatibility:** a scratch run in `/tmp` of the unmodified tool against `db_31_0_excel.zip` (sha256 `c63ad00a…1b04`) worked: 1,016 occupations, 18,838 tasks.
- reports/FLEET_MASSIVE_UPDATE_2026-10-03.md:11 — - **PRs:** 50 owner PRs since 09-20: 45 open, 4 merged (#9173, #11988, #12057, #12059; none delivered by a Grok bot), 1 closed. Only **#9576** is fully green and MERGEABLE/CLEAN. #9575 is mergeable but has 20 non-passing checks, so it is **not** green. CONFLICTING: #8847, #8925, 
- reports/FLEET_MASSIVE_UPDATE_2026-10-03.md:12 — - **Main CI:** 31/41 workflows green on their latest run. Three of the reds come from one line in `website/work-desk.html` (see action 1).
- reports/FLEET_MASSIVE_UPDATE_2026-10-03.md:20 — | Security / API auth | 15 | **7.4%** (2/27) | Mutating + sensitive HTTP routes (P0 class) that carry an inbound auth guard. Rescan of main @95178f3 with Grok-Prod-API-Surface's scan_routes.py (regex extended to recognize billingOwnerAuthorized): 247 routes, 156 mutating, 27 muta
- reports/FLEET_MASSIVE_UPDATE_2026-10-03.md:21 — | Fleet bots production_ready | 15 | **0.0%** (0/1101) | config/generated/bot-production-readiness.json on main: stats.bots=1101, production_ready_true=0. That file lists 56 division records; the owner's count is 55. | — |
- reports/FLEET_MASSIVE_UPDATE_2026-10-03.md:28 — | Edu curriculum | 5 | **0.0%** (0/11) | One first deliverable per Edu bot (11 bots) landed on main: 0. | 54.5% (6/11) — If #12436, #12441, #12922, #13183, #13188 and #13187 merge. |
- reports/FLEET_MASSIVE_UPDATE_2026-10-03.md:29 — | Repo self-running automation | 5 | **37.5%** (9/24) | 12 bot-job families in reports/REPO_AUTONOMOUS_SYSTEMS_PLAN.md × 2: (a) has a cron schedule on main, 9/12 verified by grepping .github/workflows (missing: Bootcamp = dispatch only, Pages = no cron, O*NET = no workflow); (b) 
- reports/FLEET_MASSIVE_UPDATE_2026-10-03.md:36 — 1. #9573 is now the isolated CI fix and is being updated live (last push 10-03 9:39 AM CT, 30 files). It rephrases the website/work-desk.html sentence that trips the public-site preflight, adds the Gap Closure noop lane, drops the drizzle-kit esm-loader override, and regenerates 
- reports/FLEET_MASSIVE_UPDATE_2026-10-03.md:41 — 6. Review the 18 PRs opened 10-03 9:22–9:36 AM CT (#13177–#13194). They carry the local work of 24 bots. PR-specific failures to fix first: #13180 smoke; #13181 smoke; #13185 audit; #13188 smoke; #13190 Buddy quick verification. #13194 should fix the Grok Owner Systems workflow, 
- reports/FLEET_MASSIVE_UPDATE_2026-10-03.md:42 — 7. Unblock the 23 bots that still have local-only work and no PR: HF-Diffusers, HF-Mastery-Coach, HF-Safetensors-License, HF-Tokenizers, Buddy-Capability-Packager, Buddy-Debug-Arena, Buddy-Logic-Reasoner, Buddy-RCA-Trainer, Buddy-ToolUse-Arena, OS-Agents-ProcTable, Prod-API-Surfa
- reports/FLEET_MASSIVE_UPDATE_2026-10-03.md:43 — 8. Workflow volume: open a PR for origin branch ops/workflow-schedule-demotions (8 schedule-demotion commits, no PR yet) and set a consolidation target. Main has 91 workflow files, 56 of them scheduled, and about 47% of runs were cancelled on 09-28.
- reports/FLEET_MASSIVE_UPDATE_2026-10-03.md:51 — ### HF swarm — 21 bots (8 complete, 6 in progress, 2 blocked, 5 no output)
- reports/FLEET_MASSIVE_UPDATE_2026-10-03.md:71 — | <a name="bot-grok-hf-studypack-builder"></a>**Grok-HF-StudyPack-Builder** | Own materializing study_packs/ from HUGGINGFACE_MASTERY_TRACK — Day-1 packs on disk. | Materialized 12 capability packs (study_packs/pack.*) and modified tools/build_hf_capability_packs.py with tests. A
- reports/FLEET_MASSIVE_UPDATE_2026-10-03.md:77 — ### Buddy frontier sets — 30 bots (5 complete, 9 in progress, 7 blocked, 9 no output)
- reports/FLEET_MASSIVE_UPDATE_2026-10-03.md:112 — ### Buddy OS — 10 bots (2 complete, 2 in progress, 3 blocked, 3 no output)
- reports/FLEET_MASSIVE_UPDATE_2026-10-03.md:127 — ### Prod connectivity — 10 bots (4 complete, 4 in progress, 2 blocked, 0 no output)
- reports/FLEET_MASSIVE_UPDATE_2026-10-03.md:140 — | <a name="bot-grok-prod-resource-graph"></a>**Grok-Prod-Resource-Graph** | Own resource graph: every catalogued resource→owner bot→Pages→workflow→evidence. Close disconnected nodes. | Resource graph: 1051 bots. 8 named on Pages, 26 with per-bot evidence, 0 fully connected. Box: 
- reports/FLEET_MASSIVE_UPDATE_2026-10-03.md:140 — | <a name="bot-grok-prod-resource-graph"></a>**Grok-Prod-Resource-Graph** | Own resource graph: every catalogued resource→owner bot→Pages→workflow→evidence. Close disconnected nodes. | Resource graph: 1051 bots. 8 named on Pages, 26 with per-bot evidence, 0 fully connected. Box: 
- reports/FLEET_MASSIVE_UPDATE_2026-10-03.md:142 — ### Edu — 11 bots (4 complete, 3 in progress, 1 blocked, 3 no output)
- reports/FLEET_MASSIVE_UPDATE_2026-10-03.md:158 — ### Plan owners — 29 bots (9 complete, 7 in progress, 8 blocked, 5 no output)
- reports/FLEET_MASSIVE_UPDATE_2026-10-03.md:163 — | <a name="bot-grok-65-masterbot-os-lead"></a>**Grok-65-MasterBot-OS-Lead** | Own plan-65-masterbot-os. 65 MasterBot OS production readiness — runtime, routing, cert evidence per MasterBot. | 65 MasterBot OS readiness audit: 65 divisions, 102/102 routable, 5 tests pass. No per-Ma
- reports/FLEET_MASSIVE_UPDATE_2026-10-03.md:167 — | <a name="bot-grok-division-production-gates"></a>**Grok-Division-Production-Gates** | Own plan-division-production-gates. Per-division production gates across 55 divisions; pack readiness with evidence. | Division gate scorecard: 0 verified, 135 partial, 405 missing, plus a div
- reports/FLEET_MASSIVE_UPDATE_2026-10-03.md:169 — | <a name="bot-grok-eng-gap-closure-pilot"></a>**Grok-Eng-Gap-Closure-Pilot** | Own plan-eng-gap-closure. Engineering gap-closure pilot for CI/System Watch/Gap Closure; keep main green with evidence. | #9573 was re-cut into the isolated fix the owner asked for on 09-27, and it is
- reports/FLEET_MASSIVE_UPDATE_2026-10-03.md:170 — | <a name="bot-grok-fleet-gap-closer"></a>**Grok-Fleet-Gap-Closer** | Own plan-fleet-gap-closure. Scan 1101 bots / 55 divisions for missing code/tools vs declared roles; close capability gaps evidence-first; no deletes unless… | Read-only fleet gap baseline: 1100/1101 bots have n
- reports/FLEET_MASSIVE_UPDATE_2026-10-03.md:170 — | <a name="bot-grok-fleet-gap-closer"></a>**Grok-Fleet-Gap-Closer** | Own plan-fleet-gap-closure. Scan 1101 bots / 55 divisions for missing code/tools vs declared roles; close capability gaps evidence-first; no deletes unless… | Read-only fleet gap baseline: 1100/1101 bots have n
- reports/FLEET_MASSIVE_UPDATE_2026-10-03.md:170 — | <a name="bot-grok-fleet-gap-closer"></a>**Grok-Fleet-Gap-Closer** | Own plan-fleet-gap-closure. Scan 1101 bots / 55 divisions for missing code/tools vs declared roles; close capability gaps evidence-first; no deletes unless… | Read-only fleet gap baseline: 1100/1101 bots have n
- reports/FLEET_MASSIVE_UPDATE_2026-10-03.md:179 — | <a name="bot-grok-model-access-product-owner"></a>**Grok-Model-Access-Product-Owner** | Own plan-model-access. Ship Path A (owner 500), B (HF/GitHub open-weight), C (paid ultimate), D (Buddy selector allowlist-only). Stripe stub over parallel… | PR #13176 (draft, 10-03): 14 mod
- reports/FLEET_MASSIVE_UPDATE_2026-10-03.md:182 — | <a name="bot-grok-onet-ingest-lead"></a>**Grok-ONET-Ingest-Lead** | Own plan-onet-mastery. O*NET ingest→catalog→ontology→benchmark→provenance; ops mastery in days; sellable DP-ONET SKUs only behind license gate. | O*NET 30.3 ingest: 1,016 occupations, 18,796 tasks, sanity pass,
- reports/FLEET_MASSIVE_UPDATE_2026-10-03.md:257 — - **Detail:** Failing: Code Trust Gate, Command Center Data Contract, DreamCo 500-Model Benchmark System, DreamCo Core Health, Full System Certification, Grok Owner Systems, Parallel Benchmark Gap Builders, Production Readiness Evidence, Repository Test Matrix, Run Everything Now
- reports/FLEET_MASSIVE_UPDATE_2026-10-03.md:265 — - **Projected:** 29.6% — If #13176 merges: its branch guards 6/27 P0-class routes (14 model routes total), plus the 2 billing routes already on main. Estimate.
- reports/FLEET_MASSIVE_UPDATE_2026-10-03.md:269 — - **Basis:** config/generated/bot-production-readiness.json on main: stats.bots=1101, production_ready_true=0. That file lists 56 division records; the owner's count is 55.
- reports/FLEET_MASSIVE_UPDATE_2026-10-03.md:271 — - **Detail:** Root cause (Fleet-Gap-Closer): 1100/1101 bots have no dedicated code; testCapability is self-referential; GovernedSandboxExecutor always returns blocked.
- reports/FLEET_MASSIVE_UPDATE_2026-10-03.md:314 — - **Basis:** One first deliverable per Edu bot (11 bots) landed on main: 0.
- reports/FLEET_MASSIVE_UPDATE_2026-10-03.md:321 — - **Basis:** 12 bot-job families in reports/REPO_AUTONOMOUS_SYSTEMS_PLAN.md × 2: (a) has a cron schedule on main, 9/12 verified by grepping .github/workflows (missing: Bootcamp = dispatch only, Pages = no cron, O*NET = no workflow); (b) the plan's gap is closed, 0/12.
- reports/FLEET_MASSIVE_UPDATE_2026-10-03.md:329 — - **Detail:** Raw counts: 91 workflow files, 56 with a schedule. Branch ops/workflow-schedule-demotions has 8 'demote … off the collision' commits and no PR. Actions volume on 09-28 was about 2,500 runs per 24h, roughly 47% cancelled.
- reports/FLEET_MASSIVE_UPDATE_2026-10-03.md:335 — 3. Local-only work: may the 23 bots in action 8 open PRs without a per-bot chat approval? *(asked by / unblocks: HF-Diffusers, HF-Mastery-Coach, HF-Safetensors-License, HF-Tokenizers, Buddy-Capability-Packager, Buddy-Debug-Arena, Buddy-Logic-Reasoner, Buddy-RCA-Trainer, Buddy-Too
- reports/GOALS_TO_PRODUCTION_GATES.md:18 — - `config/generated/bot-production-readiness.json` correctly shows `production_ready_true: 0` across 1,101 bots. Good.
- reports/GOALS_TO_PRODUCTION_GATES.md:26 — | 3 Capability Genome | PARTIAL | P1 | capability registry, capability validation, integration evidence |  |
- reports/GOALS_TO_PRODUCTION_GATES.md:27 — | 4 Model research | PARTIAL | P1 | model registry, official-source provenance, execution adapter evidence |  |
- reports/GOALS_TO_PRODUCTION_GATES.md:33 — | 8 Resource optimization | PARTIAL | P1 | resource measurements, hardware profile, regression thresholds |  |
- reports/GOALS_TO_PRODUCTION_GATES.md:38 — | 11 Source ingestion | PARTIAL | P1 | provenance, freshness, refresh failure handling |  |
- reports/HF_DAY1_EVIDENCE_PACKET.md:27 — - `study_packs/hub/DAY1_NOTES.md` (on main; a different, untracked version is in `/workspace/Dreamcobots`): Day-1 topic "License, provenance, and exact checkpoint inventory". Covers `revision=` pins, model cards, license metadata, gated repos, safetensors vs pickle. Inventory: 23
- reports/HF_DAY1_EVIDENCE_PACKET.md:28 — - `study_packs/nlp-tasks/README.md` (uncommitted): 5 tasks (classification, ner, qa, summarization, translation), 24 drills total. Stdlib scorer only, no weights.
- reports/HF_DAY1_EVIDENCE_PACKET.md:40 — | R5 | nlp-tasks harness self-test (recorded) | `study_packs/nlp-tasks/evidence/harness-selftest-2026-09-28.json` (uncommitted) | `ok: true`, all 5 tasks gold_mean 1.0 / wrong_mean 0.0. Kind: `harness_selftest_not_model_eval` |
- reports/HF_DAY1_EVIDENCE_PACKET.md:41 — | R6 | nlp-tasks self-test (re-run 2026-10-02) | `python3 study_packs/nlp-tasks/drill_runner.py --selftest` (stdout only) | `ok: True`, all 5 tasks ok |
- reports/HF_DAY1_EVIDENCE_PACKET.md:53 — - **F2 main's Day-1 audit, "inventory" drill**: `passed: false`. The same ids are classified differently here. Mistral-Large-Instruct is counted as `gated` (code 401), gpt-oss-... as `not_a_model_id`, and gated totals 7 (6 models + 1 dataset). The two audits disagree on 5-vs-6 ga
- reports/HF_DAY1_EVIDENCE_PACKET.md:63 — - "Hub drills 4/5 passed; drill_05: 5 gated, 2 missing": **verified** against PR #12444 evidence files (R1, R2). It is **not on main**. Main's own audit says 4/5 but 7 gated (6 models) / 0 missing (F2).
- reports/HF_REPEAT_RUNS_DAY1.md:19 — | nlp-tasks harness self-test | ok=true, 5/5 tasks gold_mean=1.0 | ok=true, 5/5 tasks gold_mean=1.0; pytest 4 passed | **MATCH** | `study_packs/nlp-tasks/evidence/harness_selftest_run1.json` | `study_packs/nlp-tasks/evidence/harness_selftest_run2.json` |
- reports/HF_REPEAT_RUNS_DAY1.md:19 — | nlp-tasks harness self-test | ok=true, 5/5 tasks gold_mean=1.0 | ok=true, 5/5 tasks gold_mean=1.0; pytest 4 passed | **MATCH** | `study_packs/nlp-tasks/evidence/harness_selftest_run1.json` | `study_packs/nlp-tasks/evidence/harness_selftest_run2.json` |
- reports/HF_REPEAT_RUNS_DAY1.md:32 — - Run 1 source: original `harness-selftest-2026-09-28.json` (also on main); wrapped into `harness_selftest_run1.json`.
- reports/MASTER_ROADMAP_CROSSWALK.md:31 — | 6 | `plan-prod-readiness-master` | Grok-PRC-Certifier | partial | 0/1101 bots production_ready; PRC 0 verified / 16 partial / 3 unknown |
- reports/P0_PLAN_GAP_QUEUE.md:21 — | 6 | `ci.main.operate_red` | Main is red: **Grok Owner Systems / `operate`** has failed every scheduled run since at least Sep 27 (15 consecutive failures, none succeeded). Today: runs 36969676112 (12:36 AM CT, `fc4493bf`), 37021917463 (9:43 AM CT, `fc4493bf`), 37062479583 (3:44
- reports/P0_PLAN_GAP_QUEUE.md:26 — | 11 | `fleet.production_ready_zero` | 0/1101 bots `production_ready=true` (56 divisions; report generated Sep 27, 7:02 AM CT, apply mode, 1101 profiles updated). Filled profiles aren't runtime proof. | `reports/BOT_PRODUCTION_READINESS.md` on 5ba09f2 | Grok-Prod-Cert-Gate | Defi
- reports/P0_PLAN_GAP_QUEUE.md:26 — | 11 | `fleet.production_ready_zero` | 0/1101 bots `production_ready=true` (56 divisions; report generated Sep 27, 7:02 AM CT, apply mode, 1101 profiles updated). Filled profiles aren't runtime proof. | `reports/BOT_PRODUCTION_READINESS.md` on 5ba09f2 | Grok-Prod-Cert-Gate | Defi
- reports/branch-health-daily.md:112 — - #14849 fix(ci): regenerate pages feature audit for 223 pages (was 205) — `needs_human`: Conflicts. Conflict team may update-from-main or open a resolution PR.
- reports/branch-health-daily.md:115 — - #8925 Pages mirrors: Goals, desks, sources, learn, devices, OS — `needs_human`: Conflicts. Conflict team may update-from-main or open a resolution PR.
- reports/branch-health-daily.md:116 — - #14397 pages: link eight orphaned product pages in nav and sitemap — `needs_human`: Conflicts. Conflict team may update-from-main or open a resolution PR.
- study_packs/career_pathways/README.md:10 — - `practice_tasks_authored.json`: 162 practice tasks for the 27 authored majors. Each cites an O*NET 31.0 Task ID and O*NET-SOC code and has an original-wording paraphrase of the task's intent, an occupation-specific scenario prompt, a 3-criterion rubric for that scenario, and a 
- study_packs/career_pathways/README.md:35 — - Practice tasks reference an O*NET 31.0 Task ID and O*NET-SOC code. O*NET task text is not reproduced: tests check that no run of 5 or more words from any O*NET 31.0 task statement, Job Zone reference text, or occupation description appears in the authored fields or in the plan 
- study_packs/career_pathways/README.md:35 — - Practice tasks reference an O*NET 31.0 Task ID and O*NET-SOC code. O*NET task text is not reproduced: tests check that no run of 5 or more words from any O*NET 31.0 task statement, Job Zone reference text, or occupation description appears in the authored fields or in the plan 
- study_packs/career_pathways/docs/DATA_DICTIONARY.md:151 — | `tasks[].onet_task_id` | O*NET 31.0 Task ID (integer) from Task Statements; resolves to a task of onet_soc_code. |
- study_packs/career_pathways/docs/DATA_DICTIONARY.md:330 — | `practice_tasks[].onet_task_id` | O*NET 31.0 Task ID (integer) from Task Statements; resolves to a task of onet_soc_code. |
- study_packs/career_pathways/study_plans/03.0104_environmental_science.md:73 — ## Practice tasks (DreamCo-original scenario prompts tied to O*NET 31.0 task IDs)
- study_packs/career_pathways/study_plans/03.0104_environmental_science.md:75 — Authorship: DreamCo-original, authored by Grok-Edu-Career-Pathways (AI), not human-reviewed. Each item cites an O*NET 31.0 task by ID and occupation code; the work-activity line is a DreamCo paraphrase in original wording (the O*NET task statement itself is on the linked O*NET On
- study_packs/career_pathways/study_plans/09.0101_speech_communication_and_rhetoric.md:70 — ## Practice tasks (DreamCo-original scenario prompts tied to O*NET 31.0 task IDs)
- study_packs/career_pathways/study_plans/09.0101_speech_communication_and_rhetoric.md:72 — Authorship: DreamCo-original, authored by Grok-Edu-Career-Pathways (AI), not human-reviewed. Each item cites an O*NET 31.0 task by ID and occupation code; the work-activity line is a DreamCo paraphrase in original wording (the O*NET task statement itself is on the linked O*NET On
- study_packs/career_pathways/study_plans/11.0401_information_science_studies.md:81 — ## Practice tasks (DreamCo-original scenario prompts tied to O*NET 31.0 task IDs)
- study_packs/career_pathways/study_plans/11.0401_information_science_studies.md:83 — Authorship: DreamCo-original, authored by Grok-Edu-Career-Pathways (AI), not human-reviewed. Each item cites an O*NET 31.0 task by ID and occupation code; the work-activity line is a DreamCo paraphrase in original wording (the O*NET task statement itself is on the linked O*NET On
- study_packs/career_pathways/study_plans/11.0701_computer_science.md:89 — ## Practice tasks (DreamCo-original scenario prompts tied to O*NET 31.0 task IDs)
- study_packs/career_pathways/study_plans/11.0701_computer_science.md:91 — Authorship: DreamCo-original, authored by Grok-Edu-Career-Pathways (AI), not human-reviewed. Each item cites an O*NET 31.0 task by ID and occupation code; the work-activity line is a DreamCo paraphrase in original wording (the O*NET task statement itself is on the linked O*NET On
- study_packs/career_pathways/study_plans/13.1202_elementary_education_and_teaching.md:60 — ## Practice tasks (DreamCo-original scenario prompts tied to O*NET 31.0 task IDs)
- study_packs/career_pathways/study_plans/13.1202_elementary_education_and_teaching.md:62 — Authorship: DreamCo-original, authored by Grok-Edu-Career-Pathways (AI), not human-reviewed. Each item cites an O*NET 31.0 task by ID and occupation code; the work-activity line is a DreamCo paraphrase in original wording (the O*NET task statement itself is on the linked O*NET On
- study_packs/career_pathways/study_plans/14.0801_civil_engineering_general.md:68 — ## Practice tasks (DreamCo-original scenario prompts tied to O*NET 31.0 task IDs)
- study_packs/career_pathways/study_plans/14.0801_civil_engineering_general.md:70 — Authorship: DreamCo-original, authored by Grok-Edu-Career-Pathways (AI), not human-reviewed. Each item cites an O*NET 31.0 task by ID and occupation code; the work-activity line is a DreamCo paraphrase in original wording (the O*NET task statement itself is on the linked O*NET On
- study_packs/career_pathways/study_plans/14.0901_computer_engineering_general.md:72 — ## Practice tasks (DreamCo-original scenario prompts tied to O*NET 31.0 task IDs)
- study_packs/career_pathways/study_plans/14.0901_computer_engineering_general.md:74 — Authorship: DreamCo-original, authored by Grok-Edu-Career-Pathways (AI), not human-reviewed. Each item cites an O*NET 31.0 task by ID and occupation code; the work-activity line is a DreamCo paraphrase in original wording (the O*NET task statement itself is on the linked O*NET On
- study_packs/career_pathways/study_plans/14.1001_electrical_and_electronics_engineering.md:69 — ## Practice tasks (DreamCo-original scenario prompts tied to O*NET 31.0 task IDs)
- study_packs/career_pathways/study_plans/14.1001_electrical_and_electronics_engineering.md:71 — Authorship: DreamCo-original, authored by Grok-Edu-Career-Pathways (AI), not human-reviewed. Each item cites an O*NET 31.0 task by ID and occupation code; the work-activity line is a DreamCo paraphrase in original wording (the O*NET task statement itself is on the linked O*NET On
- study_packs/career_pathways/study_plans/14.1901_mechanical_engineering.md:69 — ## Practice tasks (DreamCo-original scenario prompts tied to O*NET 31.0 task IDs)
- study_packs/career_pathways/study_plans/14.1901_mechanical_engineering.md:71 — Authorship: DreamCo-original, authored by Grok-Edu-Career-Pathways (AI), not human-reviewed. Each item cites an O*NET 31.0 task by ID and occupation code; the work-activity line is a DreamCo paraphrase in original wording (the O*NET task statement itself is on the linked O*NET On
- study_packs/career_pathways/study_plans/23.0101_english_language_and_literature_general.md:65 — ## Practice tasks (DreamCo-original scenario prompts tied to O*NET 31.0 task IDs)
- study_packs/career_pathways/study_plans/23.0101_english_language_and_literature_general.md:67 — Authorship: DreamCo-original, authored by Grok-Edu-Career-Pathways (AI), not human-reviewed. Each item cites an O*NET 31.0 task by ID and occupation code; the work-activity line is a DreamCo paraphrase in original wording (the O*NET task statement itself is on the linked O*NET On
- study_packs/career_pathways/study_plans/26.0101_biology_biological_sciences_general.md:79 — ## Practice tasks (DreamCo-original scenario prompts tied to O*NET 31.0 task IDs)
- study_packs/career_pathways/study_plans/26.0101_biology_biological_sciences_general.md:81 — Authorship: DreamCo-original, authored by Grok-Edu-Career-Pathways (AI), not human-reviewed. Each item cites an O*NET 31.0 task by ID and occupation code; the work-activity line is a DreamCo paraphrase in original wording (the O*NET task statement itself is on the linked O*NET On
- study_packs/career_pathways/study_plans/27.0101_mathematics_general.md:77 — ## Practice tasks (DreamCo-original scenario prompts tied to O*NET 31.0 task IDs)
- study_packs/career_pathways/study_plans/27.0101_mathematics_general.md:79 — Authorship: DreamCo-original, authored by Grok-Edu-Career-Pathways (AI), not human-reviewed. Each item cites an O*NET 31.0 task by ID and occupation code; the work-activity line is a DreamCo paraphrase in original wording (the O*NET task statement itself is on the linked O*NET On
- study_packs/career_pathways/study_plans/27.0501_statistics_general.md:75 — ## Practice tasks (DreamCo-original scenario prompts tied to O*NET 31.0 task IDs)
- study_packs/career_pathways/study_plans/27.0501_statistics_general.md:77 — Authorship: DreamCo-original, authored by Grok-Edu-Career-Pathways (AI), not human-reviewed. Each item cites an O*NET 31.0 task by ID and occupation code; the work-activity line is a DreamCo paraphrase in original wording (the O*NET task statement itself is on the linked O*NET On
- study_packs/career_pathways/study_plans/40.0501_chemistry_general.md:73 — ## Practice tasks (DreamCo-original scenario prompts tied to O*NET 31.0 task IDs)
- study_packs/career_pathways/study_plans/40.0501_chemistry_general.md:75 — Authorship: DreamCo-original, authored by Grok-Edu-Career-Pathways (AI), not human-reviewed. Each item cites an O*NET 31.0 task by ID and occupation code; the work-activity line is a DreamCo paraphrase in original wording (the O*NET task statement itself is on the linked O*NET On
- study_packs/career_pathways/study_plans/40.0801_physics_general.md:67 — ## Practice tasks (DreamCo-original scenario prompts tied to O*NET 31.0 task IDs)
- study_packs/career_pathways/study_plans/40.0801_physics_general.md:69 — Authorship: DreamCo-original, authored by Grok-Edu-Career-Pathways (AI), not human-reviewed. Each item cites an O*NET 31.0 task by ID and occupation code; the work-activity line is a DreamCo paraphrase in original wording (the O*NET task statement itself is on the linked O*NET On
- study_packs/career_pathways/study_plans/42.0101_psychology_general.md:69 — ## Practice tasks (DreamCo-original scenario prompts tied to O*NET 31.0 task IDs)
- study_packs/career_pathways/study_plans/42.0101_psychology_general.md:71 — Authorship: DreamCo-original, authored by Grok-Edu-Career-Pathways (AI), not human-reviewed. Each item cites an O*NET 31.0 task by ID and occupation code; the work-activity line is a DreamCo paraphrase in original wording (the O*NET task statement itself is on the linked O*NET On
- study_packs/career_pathways/study_plans/43.0104_criminal_justice_safety_studies.md:65 — ## Practice tasks (DreamCo-original scenario prompts tied to O*NET 31.0 task IDs)
- study_packs/career_pathways/study_plans/43.0104_criminal_justice_safety_studies.md:67 — Authorship: DreamCo-original, authored by Grok-Edu-Career-Pathways (AI), not human-reviewed. Each item cites an O*NET 31.0 task by ID and occupation code; the work-activity line is a DreamCo paraphrase in original wording (the O*NET task statement itself is on the linked O*NET On
- study_packs/career_pathways/study_plans/44.0701_social_work.md:70 — ## Practice tasks (DreamCo-original scenario prompts tied to O*NET 31.0 task IDs)
- study_packs/career_pathways/study_plans/44.0701_social_work.md:72 — Authorship: DreamCo-original, authored by Grok-Edu-Career-Pathways (AI), not human-reviewed. Each item cites an O*NET 31.0 task by ID and occupation code; the work-activity line is a DreamCo paraphrase in original wording (the O*NET task statement itself is on the linked O*NET On
- study_packs/career_pathways/study_plans/45.0601_economics_general.md:75 — ## Practice tasks (DreamCo-original scenario prompts tied to O*NET 31.0 task IDs)
- study_packs/career_pathways/study_plans/45.0601_economics_general.md:77 — Authorship: DreamCo-original, authored by Grok-Edu-Career-Pathways (AI), not human-reviewed. Each item cites an O*NET 31.0 task by ID and occupation code; the work-activity line is a DreamCo paraphrase in original wording (the O*NET task statement itself is on the linked O*NET On
- study_packs/career_pathways/study_plans/45.1001_political_science_and_government_general.md:72 — ## Practice tasks (DreamCo-original scenario prompts tied to O*NET 31.0 task IDs)
- study_packs/career_pathways/study_plans/45.1001_political_science_and_government_general.md:74 — Authorship: DreamCo-original, authored by Grok-Edu-Career-Pathways (AI), not human-reviewed. Each item cites an O*NET 31.0 task by ID and occupation code; the work-activity line is a DreamCo paraphrase in original wording (the O*NET task statement itself is on the linked O*NET On
- study_packs/career_pathways/study_plans/50.0409_graphic_design.md:69 — ## Practice tasks (DreamCo-original scenario prompts tied to O*NET 31.0 task IDs)
- study_packs/career_pathways/study_plans/50.0409_graphic_design.md:71 — Authorship: DreamCo-original, authored by Grok-Edu-Career-Pathways (AI), not human-reviewed. Each item cites an O*NET 31.0 task by ID and occupation code; the work-activity line is a DreamCo paraphrase in original wording (the O*NET task statement itself is on the linked O*NET On
- study_packs/career_pathways/study_plans/51.2001_pharmacy.md:62 — ## Practice tasks (DreamCo-original scenario prompts tied to O*NET 31.0 task IDs)
- study_packs/career_pathways/study_plans/51.2001_pharmacy.md:64 — Authorship: DreamCo-original, authored by Grok-Edu-Career-Pathways (AI), not human-reviewed. Each item cites an O*NET 31.0 task by ID and occupation code; the work-activity line is a DreamCo paraphrase in original wording (the O*NET task statement itself is on the linked O*NET On
- study_packs/career_pathways/study_plans/51.3801_registered_nursing_registered_nurse.md:66 — ## Practice tasks (DreamCo-original scenario prompts tied to O*NET 31.0 task IDs)
- study_packs/career_pathways/study_plans/51.3801_registered_nursing_registered_nurse.md:68 — Authorship: DreamCo-original, authored by Grok-Edu-Career-Pathways (AI), not human-reviewed. Each item cites an O*NET 31.0 task by ID and occupation code; the work-activity line is a DreamCo paraphrase in original wording (the O*NET task statement itself is on the linked O*NET On
- study_packs/career_pathways/study_plans/52.0201_business_administration_and_management_general.md:106 — ## Practice tasks (DreamCo-original scenario prompts tied to O*NET 31.0 task IDs)
- study_packs/career_pathways/study_plans/52.0201_business_administration_and_management_general.md:108 — Authorship: DreamCo-original, authored by Grok-Edu-Career-Pathways (AI), not human-reviewed. Each item cites an O*NET 31.0 task by ID and occupation code; the work-activity line is a DreamCo paraphrase in original wording (the O*NET task statement itself is on the linked O*NET On
- study_packs/career_pathways/study_plans/52.0301_accounting.md:69 — ## Practice tasks (DreamCo-original scenario prompts tied to O*NET 31.0 task IDs)
- study_packs/career_pathways/study_plans/52.0301_accounting.md:71 — Authorship: DreamCo-original, authored by Grok-Edu-Career-Pathways (AI), not human-reviewed. Each item cites an O*NET 31.0 task by ID and occupation code; the work-activity line is a DreamCo paraphrase in original wording (the O*NET task statement itself is on the linked O*NET On
- study_packs/career_pathways/study_plans/52.0801_finance_general.md:79 — ## Practice tasks (DreamCo-original scenario prompts tied to O*NET 31.0 task IDs)
- study_packs/career_pathways/study_plans/52.0801_finance_general.md:81 — Authorship: DreamCo-original, authored by Grok-Edu-Career-Pathways (AI), not human-reviewed. Each item cites an O*NET 31.0 task by ID and occupation code; the work-activity line is a DreamCo paraphrase in original wording (the O*NET task statement itself is on the linked O*NET On
- study_packs/career_pathways/study_plans/52.1401_marketing_marketing_management_general.md:69 — ## Practice tasks (DreamCo-original scenario prompts tied to O*NET 31.0 task IDs)
- study_packs/career_pathways/study_plans/52.1401_marketing_marketing_management_general.md:71 — Authorship: DreamCo-original, authored by Grok-Edu-Career-Pathways (AI), not human-reviewed. Each item cites an O*NET 31.0 task by ID and occupation code; the work-activity line is a DreamCo paraphrase in original wording (the O*NET task statement itself is on the linked O*NET On
- study_packs/hub/DAY1_DRILL_NOTES.md:25 — Unique totals: **23 model ids, 8 dataset ids.** `tools/build_hf_capability_packs.py` merges both configs into
- study_packs/hub/drills/DRILLS.md:33 — | 5 | `drill_05_inventory_audit.py` | all 23 model ids + 8 dataset ids | exists, gated, license, latest sha, last_modified, pipeline_tag, base_model, rename detection. Writes `../evidence/drill_05_inventory_audit.json`. Exits 1 if any model id is missing | none (metadata API) |
- study_packs/trl/_sources/docs_HUGGINGFACE_MASTERY_PLAN.md:48 — For each pack below, pick **3 datasets + 2 models + 1 eval suite**. Not 300.

These are candidate count claims, not automatically incorrect values. Convert live inventory counts to generated values or label historical snapshots with their source and review date.

## Gap inventory

### .agents/memory/MEMORY.md

- Status: implementation_reference_missing
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### .agents/memory/ai-cost-optimization.md

- Status: implementation_reference_missing
- Actionable claim lines: 2
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### .agents/memory/browser-cache-fix.md

- Status: test_reference_missing
- Actionable claim lines: 0
- Implementation paths: client/public/sw.js
- Test paths: None detected
- Missing paths: None detected
- Next action: Add focused tests and acceptance evidence for the referenced implementation.
- Execution verified: No; run-specific evidence is required.

### .agents/memory/buddy-auth.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### .agents/memory/buddy-feature-routes.md

- Status: implementation_reference_missing
- Actionable claim lines: 3
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### .agents/memory/codelabs-bot-icon.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### .agents/memory/express-vite-route-order.md

- Status: test_reference_missing
- Actionable claim lines: 1
- Implementation paths: server/routes.ts, server/vite.ts
- Test paths: None detected
- Missing paths: None detected
- Next action: Add focused tests and acceptance evidence for the referenced implementation.
- Execution verified: No; run-specific evidence is required.

### .agents/memory/github-push.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### .agents/memory/service-worker-blank-page.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### .agents/memory/stripe-status.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### .agents/memory/tool-belt-upgrade.md

- Status: implementation_reference_missing
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### .github/ISSUE_TEMPLATE/thing-to-fix.md

- Status: implementation_reference_missing
- Actionable claim lines: 2
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### .github/PULL_REQUEST_TEMPLATE.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### .github/agents/buddy-debugger.agent.md

- Status: broken_path_references
- Actionable claim lines: 10
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: github/workflows/buddy-actions-test-lab.yml, tmp/dreamco-verification/latest.json
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### .github/agents/china-us-tech-manufacturing-scout.agent.md

- Status: implementation_reference_missing
- Actionable claim lines: 3
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### .github/agents/easy-updater.agent.md

- Status: implementation_reference_missing
- Actionable claim lines: 3
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### .github/agents/grok-actions-operator.agent.md

- Status: implementation_reference_missing
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### .github/agents/grok-buddy-bridge.agent.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### .github/agents/grok-fleet-debugger.agent.md

- Status: implementation_reference_missing
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### .github/agents/grok-legacy-placer.agent.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### .github/agents/grok-md-compiler.agent.md

- Status: implementation_reference_missing
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### .github/agents/grok-pr-pilot.agent.md

- Status: implementation_reference_missing
- Actionable claim lines: 2
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### .github/agents/grok-repo-scanner.agent.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### .github/agents/grok-research.agent.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### .github/agents/grok-safety-gate.agent.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### .github/agents/grok-systems-builder.agent.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### .github/agents/manufacturer-marketplace-bot.agent.md

- Status: implementation_reference_missing
- Actionable claim lines: 3
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### .github/agents/notes-to-code-builder.agent.md

- Status: broken_path_references
- Actionable claim lines: 4
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: config/generated/notes-to-code-backlog.json
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### .github/agents/trusted-code-reviewer.agent.md

- Status: implementation_reference_missing
- Actionable claim lines: 5
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### .github/copilot-instructions.md

- Status: test_reference_missing
- Actionable claim lines: 10
- Implementation paths: tools/audit_actions_health.py, tools/buddy_local_repository.py
- Test paths: None detected
- Missing paths: None detected
- Next action: Add focused tests and acceptance evidence for the referenced implementation.
- Execution verified: No; run-specific evidence is required.

### .github/pull_request_template.md

- Status: implementation_reference_missing
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### AGENTS.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### ARCHITECTURE.md

- Status: implementation_reference_missing
- Actionable claim lines: 11
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### CONSOLIDATION.md

- Status: implementation_reference_missing
- Actionable claim lines: 9
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### CONTRIBUTING.md

- Status: implementation_reference_missing
- Actionable claim lines: 3
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### DreamPayments/README.md

- Status: implementation_reference_missing
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### DreamPayments/SECURITY.md

- Status: implementation_reference_missing
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### EASY_UPDATE.md

- Status: implementation_reference_missing
- Actionable claim lines: 9
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### README.md

- Status: test_reference_missing
- Actionable claim lines: 8
- Implementation paths: website/actions.html, website/autonomy.html, website/bootcamp-wrappers.html, website/bots.html, website/buddy.html, website/build.html, website/category-systems.html, website/chat-sync.html, website/devices.html, website/divisions.html, website/goals.html, website/hf-bootcamp.html, website/hub.html, website/learn-hf.html, website/learn.html, website/markdown-gap-audit.html, website/marketplace.html, website/models.html, website/open-model-lab.html, website/os.html, website/own-bootcamp.html, website/recover.html, website/sources.html, website/technology-radar.html, website/test-center.html, website/work.html
- Test paths: None detected
- Missing paths: None detected
- Next action: Add focused tests and acceptance evidence for the referenced implementation.
- Execution verified: No; run-specific evidence is required.

### SECURITY.md

- Status: implementation_reference_missing
- Actionable claim lines: 2
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### START_HERE.md

- Status: test_reference_missing
- Actionable claim lines: 0
- Implementation paths: buddy/easy_github/buddy_easy_github.py
- Test paths: None detected
- Missing paths: None detected
- Next action: Add focused tests and acceptance evidence for the referenced implementation.
- Execution verified: No; run-specific evidence is required.

### SYSTEM_ARCHITECTURE.md

- Status: test_reference_missing
- Actionable claim lines: 2
- Implementation paths: client/index.html, client/public/manifest.json, client/public/sw.js, client/src/main.tsx, server/routes.ts, server/seed-bots.ts, server/seed-buddy-bot.ts, server/seed-codelabs.ts, server/seed-github-bots.ts, shared/schema.ts, shared/tool-belt.ts
- Test paths: None detected
- Missing paths: None detected
- Next action: Add focused tests and acceptance evidence for the referenced implementation.
- Execution verified: No; run-specific evidence is required.

### benchmarks/README.md

- Status: implementation_reference_missing
- Actionable claim lines: 2
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### benchmarks/america_gov/README.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### benchmarks/hf_model_ranker/README.md

- Status: implementation_reference_missing
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### benchmarks/resource_mastery/README.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### benchmarks/source_adapter_contract.md

- Status: implementation_reference_missing
- Actionable claim lines: 4
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### benchmarks/source_discovery_policy.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/3d-asset-mgr.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/5s-audit-tool.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/ab-testing-bot.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/accelerator-prep.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/access-control-mgr.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/accessibility-auditor.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/ach-processor.md

- Status: implementation_reference_missing
- Actionable claim lines: 8
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/ad-copy.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/adaptive-learning.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/admin-analytics-elite.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/adversarial-ai-defense.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/advocacy-scorer.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/advocacy-tracker.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/affiliate-marketing.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/after-action-review.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/ag-analytics-elite.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/agentgpt-browser.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/ai-governance-hub.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/ai-pair-prog.md

- Status: implementation_reference_missing
- Actionable claim lines: 8
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/ai-security-scanner.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/ai-self-learner.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/alarm-monitoring.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/algo-trading.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/analytics-hub.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/animation-pipeline.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/api-designer.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/api-integration-hub.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/api-map.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/api-monetization.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/app-perf-monitor.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/app-store-optimizer.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/apple-google-pay.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/appliance-repair.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/appointment-setter.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/approval-workflow.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/aquaculture-mgr.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/arbitrage-finder.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/art-portfolio.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/assembly-line.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/assessment-builder.md

- Status: implementation_reference_missing
- Actionable claim lines: 8
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/asset-perf-scorer.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/attack-surface-reducer.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/attendance-tracker.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/audience-notes.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/auth-matrix.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/auto-defense-deploy.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/auto-failover-ops.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/auto-loan.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/auto-patch-mgr.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/auto-recommender.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/auto-scaler.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/auto-scaling-tasks.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/autogen-agent.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/autogpt-agent.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/automation-gap-detector.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/autonomous-fleet.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/awards-decorations.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/babyagi-agent.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/barber-booking.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/bartender-ai.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/beam-agent.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/beauty-school.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/behavioral-anomaly-alert.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/benchmark-runner.md

- Status: implementation_reference_missing
- Actionable claim lines: 8
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/beta-tester-bot.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/bi-dashboard.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/bill-reminder.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/bim-coordinator.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/blindspot-detector.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/blockchain-analytics.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/blog-writer.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/blueprint-analyzer.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/bond-income.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/books-app-bot.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/bottleneck-predictor.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/brand-builder.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/brand-guidelines.md

- Status: implementation_reference_missing
- Actionable claim lines: 8
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/brand-impersonation.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/brand-perception-monitor.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/brand-perception-steer.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/brand-protector.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/brand-trust-monitor.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/brand-voice.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/btc-wallet.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/buddy-bot.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/buddy-code-replicator.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/buddy-library-indexer.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/buddy-self-teacher.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/buddy-tool-builder.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/budget-allocation-ai.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/budget-realloc-ai.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/budget-trip.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/building-automation.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/business-card-scanner.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/business-loan.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/business-plan-gen.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/cac-optimizer.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/campaign-alignment-opt.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/campaign-controller.md

- Status: implementation_reference_missing
- Actionable claim lines: 8
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/campaign-roi-analyzer.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/campaign-roi.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/capacity-planner.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/capex-opex-engine.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/capital-alloc-ai.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/capital-alloc-optimizer.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/capital-sustainability.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/captcha-handler.md

- Status: implementation_reference_missing
- Actionable claim lines: 8
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/case-manager.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/case-study.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/cashback-tracker.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/cashflow-stress-test.md

- Status: implementation_reference_missing
- Actionable claim lines: 8
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/catalog-manager.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/catering-coordinator.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/change-manager.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/change-order-mgr.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/channel-planner.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/chargeback-mgr.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/chatbot-builder.md

- Status: implementation_reference_missing
- Actionable claim lines: 8
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/chemical-inventory.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/chronic-care-mgr.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/churn-mitigation.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/churn-predictor-bot.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/citation-formatter.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/class-scheduler.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/classroom-behavior.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/client-billing.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/client-intake-care.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/client-portal.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/client-satisfaction.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/client-success.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/clinical-decision.md

- Status: implementation_reference_missing
- Actionable claim lines: 10
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/clinical-trial-mgr.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/cloud-scaler.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/clv-anomaly-detector.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/clv-predictor.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/cmms-analytics-elite.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/cnc-optimizer.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/code-architect.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/code-reader.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/code-review-ai.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/cohort-segmentation.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/cold-chain-monitor.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/cold-email-engine.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/college-readiness.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/color-palette.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/commercial-scanner.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/commodity-trader.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/comms-coordinator.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/community-health-elite.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/competitive-benchmark.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/competitive-intel.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/competitor-monitor.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/competitor-narrative.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/compliance-auditor.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/compliance-automation.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/compliance-kpi-monitor.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/compliance-mfg.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/compliance-scanner.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/compliance-trend-forecast.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/component-library.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/concrete-mix-ai.md

- Status: implementation_reference_missing
- Actionable claim lines: 8
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/consequence-simulator.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/construction-analytics-elite.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/construction-budget.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/construction-estimator.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/consulting-proposal.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/container-mgr.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/content-analytics.md

- Status: implementation_reference_missing
- Actionable claim lines: 8
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/content-calendar.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/contingency-planner.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/continuous-task-opt.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/contract-admin.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/contract-lifecycle.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/contract-loophole.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/contract-manager.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/contractual-risk-sim.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/conversion-funnel.md

- Status: implementation_reference_missing
- Actionable claim lines: 8
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/coordinated-attack-sim.md

- Status: implementation_reference_missing
- Actionable claim lines: 8
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/copywriting-ai.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/cosmetology-license.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/cost-consolidation.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/cost-reduction-engine.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/coupon-aggregator.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/coze-agent.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/crane-operations.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/crash-reporter-bot.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/creative-analytics-elite.md

- Status: implementation_reference_missing
- Actionable claim lines: 8
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/creative-brief-gen.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/creative-tester.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/creative-writer.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/credentialing-ai.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/credit-optimizer.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/credit-underwriter.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/crewai-agent.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/crisis-hotline.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/crisis-management.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/crm-exporter.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/cro-engine.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/crop-planner.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/cross-border-ma.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/cross-border-pay.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/cross-border-payments.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/cross-border-task-opt.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/cross-chain-bridge.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/cross-continent-redundancy.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/cross-dept-harmonizer.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/cross-entity-governance.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/cross-industry-influence.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/cross-jurisdiction-compliance.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/cross-region-deploy.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/cross-sell-engine.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/cross-team-efficiency.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/cross-tenant-correlation.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/crowd-management.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/crypto-compliance.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/crypto-fund-mgr.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/crypto-news.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/crypto-security.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/crypto-staking.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/crypto-tax.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/crypto-trading.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/cultural-intel.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/currency-hedging.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/curriculum-mapper.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/customer-data.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/customer-discovery.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/customer-segmentation.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/customs-clearance.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/customs-tariffs.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/cyber-physical.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/cyberattack-predictor.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/cybersecurity-mil.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/daily-report-gen.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/dairy-manager.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/dao-governance.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/dark-web-monitor.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/data-analysis-sci.md

- Status: implementation_reference_missing
- Actionable claim lines: 8
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/data-catalog.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/data-cleaner.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/data-governance.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/data-lake.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/data-monetization.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/data-quality-engine.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/data-quality.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/data-scientist.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/data-sync.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/data-warehouse.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/db-designer.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/deal-intelligence.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/debt-payoff.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/debug-detective.md

- Status: implementation_reference_missing
- Actionable claim lines: 8
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/decision-confidence.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/decision-validator.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/deep-link-mgr.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/deep-research-agent.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/defense-analytics-elite.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/defi-yield.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/deliverability-mgr.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/deliverable-tracker.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/delivery-board.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/delivery-integration.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/delivery-rating.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/demand-fluctuation.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/demand-forecaster.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/demand-planner.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/deployment-checklist.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/deployment-manager.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/deployment-mgr.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/derivatives-strategy.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/devin-agent.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/devops-analytics-elite.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/digital-franchise.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/disability-services.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/disaster-recovery.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/disaster-response-coord.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/disaster-sim-multi-region.md

- Status: implementation_reference_missing
- Actionable claim lines: 8
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/disclosure-checker.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/discount-dominator.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/dispatch-center.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/dispute-detector.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/distressed-asset.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/district-analytics-elite.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/dividend-investor.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/docs-generator.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/document-manager.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/document-processor.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/donation-tracker.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/dr-simulation.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/dreambot.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/drift-detector.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/driver-compliance.md

- Status: implementation_reference_missing
- Actionable claim lines: 8
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/driver-training-ai.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/drone-scouting.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/drone-security.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/dropshipping-engine.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/drug-discovery-ai.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/dynamic-pricing.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/edtech-evaluator.md

- Status: implementation_reference_missing
- Actionable claim lines: 8
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/education-app-bot.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/ehr-migration.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/elder-care.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/electrical-inspector.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/elevator-maint.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/email-automation.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/email-newsletter.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/embedded-finance.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/emergency-dispatch.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/emergency-triage.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/emerging-pattern-detector.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/emerging-trend-detector.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/empire-monitor.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/employee-directory.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/energy-auditor.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/energy-optimizer.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/enrollment-forecast.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/enterprise-ethics-score.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/enterprise-policy-auto.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/entertainment-app-bot.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/equipment-account.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/equipment-tracker.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/esg-optimizer.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/etf-rotator.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/eth-defi.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/ethics-violation-detector.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/etl-pipeline.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/eval-card.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/event-production.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/exchange-1031.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/executive-protection.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/expense-anomaly-ai.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/expense-reporter.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/experiment-tracker.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/export-docs.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/facilities-request.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/fairness-auditor.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/farm-accounting.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/farm-safety-check.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/feature-adoption.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/feature-flag-mgr.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/feature-flag.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/feature-store.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/feedback-sentiment.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/fertilizer-calc.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/field-log.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/finance-app-bot.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/financial-dashboard-gen.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/financial-impact-sim.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/financial-kpi-auto.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/financial-literacy.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/financial-resilience-index.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/financial-scenario-modeler.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/finetune-orchestrator.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/fire-investigation.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/fire-safety-ai.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/fire-sprinkler.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/fitness-military.md

- Status: implementation_reference_missing
- Actionable claim lines: 8
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/fitness-trainer.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/fleet-admin.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/fleet-tracker.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/font-manager.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/food-analytics-elite.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/food-bank-ops.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/food-cost-ctrl.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/food-drink-app-bot.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/food-inventory.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/food-truck-ops.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/foreclosure-finder.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/forex-trader.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/form-automation.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/franchise-compliance.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/franchise-launcher.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/franchise-ops.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/franchise-packager.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/fraud-detection-pay.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/fraud-ring-detector.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/fraud-shield.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/freebie-finder.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/freight-broker.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/fuel-optimizer.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/funding-finder.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/funnel-optimizer.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/fx-arbitrage.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/game-ai-player.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/game-analytics.md

- Status: implementation_reference_missing
- Actionable claim lines: 8
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/game-coach.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/games-app-bot.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/gamification-engine.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/gaming-titan.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/gas-tracker.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/generator-monitor.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/genomics-pipeline.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/geo-load-sim.md

- Status: implementation_reference_missing
- Actionable claim lines: 8
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/geo-perf-analytics.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/geo-resiliency-index.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/geospatial.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/ghost-kitchen.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/git-workflow.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/global-availability.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/global-bot-network.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/global-compliance.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/global-influence-index.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/global-ip.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/global-outage-estimator.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/global-redundancy-alert.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/global-supply-chain.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/go-to-market.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/god-mode-bot.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/gov-contract-bot.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/governance-anomaly.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/governance-dashboard.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/gpt-engineer-agent.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/grain-marketing.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/grant-finder.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/grant-tracker-social.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/grant-writer-edu.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/grant-writer-sci.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/graphic-design-mgr.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/greenhouse-controller.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/guard-scheduling.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/hair-color-formula.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/harvest-planner.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/health-analytics-elite.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/health-compliance.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/health-fitness-app-bot.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/health-inspection.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/hedge-fund-strategy.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/hft-market-maker.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/home-buyer-bot.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/home-maint-checklist.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/hotel-room-service.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/housing-services.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/hr-onboarding.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/hustle-finder-bot.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/hvac-diagnostic.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/hyper-resilient-defense.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/hyper-resilient-mode.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/icp-builder.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/idea-validator.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/idempotency-check.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/idle-time-minimizer.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/iep-manager.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/illustration-mgr.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/immersive-xr.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/immigrant-services.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/import-export.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/improvement-engine.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/in-app-purchase-opt.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/incident-reporter.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/incident-response-auto.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/influence-gap-detector.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/influence-mapping.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/influence-network-opt.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/influencer-bot.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/influencer-engagement.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/influencer-outreach.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/infra-risk-map.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/insider-threat-ai.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/insurance-fraud.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/insurance-shopper.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/integration-runbook.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/intelligence-analyst.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/intermodal-coordinator.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/international-sla.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/intl-franchise.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/intl-hr.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/intl-tax.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/intrusion-anomaly.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/inventory-forecaster.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/inventory-manager.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/inventory-mfg.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/investigation-mgr.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/investment-opp-scorer.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/investor-report-empire.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/investor-reporting.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/invoice-processor.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/ip-monitor.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/ip-valuator.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/irrigation-ai.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/it-service-desk.md

- Status: implementation_reference_missing
- Actionable claim lines: 8
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/itinerary-builder.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/job-application-bot.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/journey-bottleneck.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/json-formatter.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/k9-unit-tracker.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/kids-family-app-bot.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/kitchen-order.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/knowledge-base.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lab-equipment-mgr.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lab-notebook.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lab-results-tracker.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lab-safety-training.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/land-bank.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/landing-page-ai.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/landscaping-mgr.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/langchain-agent.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/last-mile-ai.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/latency-anomaly.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/latency-optimizer.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lead-scraper.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lead-validator.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lean-six-sigma.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lease-analyzer.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lease-optimizer.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/legal-audit-reports.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/legal-contract-lifecycle.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/legal-money-bot.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/legal-risk-scorer.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/legal-scenario-sim.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lending-platform.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lesson-planner.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-angular.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-anthropic.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-astro.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-aws.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-axios.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-azure.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-bun.md

- Status: implementation_reference_missing
- Actionable claim lines: 8
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-celery.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-cloudflare.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-cypress.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-date-fns.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-deno.md

- Status: implementation_reference_missing
- Actionable claim lines: 8
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-docker.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-drizzle.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-elasticsearch.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-electron.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-elysiajs.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-esbuild.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-ethers.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-express.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-fastify.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-firebase.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-flutter.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-framer-motion.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-gcp.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-github-actions.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-godot.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-golang.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-hono.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-huggingface.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-java-spring.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-javascript-es.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-jest.md

- Status: implementation_reference_missing
- Actionable claim lines: 9
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-jetpack-compose.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-kotlin-multiplatform.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-kotlin.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-kubernetes.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-langchain.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-llamaindex.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-lodash.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-matplotlib.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-mongoose.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-nestjs.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-nextjs.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-ngrx.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-numpy.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-nuxt.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-ollama.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-openai-sdk.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-opencv.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-pandas.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-parcel.md

- Status: implementation_reference_missing
- Actionable claim lines: 8
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-phaserjs.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-php-laravel.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-planetscale.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-playwright.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-polars.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-postgresql.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-prisma.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-pydantic.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-python-django.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-python-fastapi.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-python-flask.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-pytorch.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-qwik.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-react-native.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-react-query.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-react.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-reanimated.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-redis.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-redux.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-ruby-rails.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-rust.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-rxjs.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-scikit-learn.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-shadcn.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-solidity.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-solidjs.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-sqlalchemy.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-sqlite.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-stable-diffusion.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-storybook.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-streamlit.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-supabase.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-svelte.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-swiftui.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-tailwind.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-tauri.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-tensorflow.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-terraform.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-threejs.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-trpc.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-typescript.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-unity.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-vercel-ai.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-vercel.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-vite.md

- Status: implementation_reference_missing
- Actionable claim lines: 9
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-vitest.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-vue.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-web3-storage.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-webpack.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-websockets.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-zod.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lib-zustand.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/license-chooser.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lifestyle-app-bot.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/listing-optimizer.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/literature-review.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/litigation-exposure-ai.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/livestock-tracker.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/llc-formation.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/llm-cost-optimizer.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lms-integrator.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/load-calculator.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/loan-finder.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/loan-servicing.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lobbying-detector.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/localization-i18n.md

- Status: implementation_reference_missing
- Actionable claim lines: 8
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/localization.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/logistics-military.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/logistics-router.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/long-cycle-roi-sim.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/long-horizon-predictor.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/lora-plan.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/loyalty-impact-sim.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/loyalty-program.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/loyalty-rewards.md

- Status: implementation_reference_missing
- Actionable claim lines: 8
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/ma-advisory.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/mail-room.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/maintenance-mfg.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/manus-agent.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/mariner-agent.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/market-anomaly.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/market-entry.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/market-intel-dashboard.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/market-intel.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/market-maker.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/market-opp-scorer.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/market-price-alert.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/market-research-biz.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/market-sentiment.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/marketplace-hub.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/marketplace-manager.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/marketplace-sync.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/massage-therapist.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/med-spa-mgr.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/medical-app-bot.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/medical-billing.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/medical-device-tracker.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/medical-readiness.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/meeting-notes.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/meeting-scheduler.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/membership-mgr-care.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/memory-vault.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/mental-health-screen.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/mentorship-platform.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/menu-engineer.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/merchant-onboarding.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/messaging-impact-ai.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/metagpt-agent.md

- Status: implementation_reference_missing
- Actionable claim lines: 8
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/mfg-analytics-elite.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/micro-segment-cluster.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/microscopy-ai.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/milestone-tracker.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/mining-monitor.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/mitigation-recommender.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/ml-cicd.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/mobile-pay.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/model-card.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/model-lifecycle.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/model-routing-engine.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/monetization-optimizer.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/monorepo-mgr.md

- Status: implementation_reference_missing
- Actionable claim lines: 9
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/mortgage-advisor.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/mos-career-planner.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/multi-channel-outreach.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/multi-currency-optimizer.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/multi-entity-cashflow.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/multi-entity-policy.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/multi-layer-defense.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/multi-market-alignment.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/multi-obj-optimizer.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/multi-process-coord.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/multi-region-cost-opt.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/multi-region-recovery.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/multi-scenario-forecast.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/multi-tenant-scaler.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/multi-tz-scheduler.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/multi-var-decision.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/multichannel-amplifier.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/multichannel-customer.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/multifamily-acquisition.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/music-app-bot.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/music-production.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/mvp-planner.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/narrative-disruption-sim.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/narrative-prioritizer.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/nav-app-bot.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/network-attack-sim.md

- Status: implementation_reference_missing
- Actionable claim lines: 9
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/networking-mgr.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/news-app-bot.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/nft-portfolio.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/nlp-analytics.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/nonprofit-mgr.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/notification-engine.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/nurse-scheduler.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/nutrition-planner.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/objection-handler-ai.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/oee-tracker.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/offer-researcher.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/office-supplies.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/offline-pack.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/onboarding-funnel-bot.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/openagents-web3.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/operations-setup.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/operator-agent.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/opinion-leadership-map.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/opinion-shift-predictor.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/opportunity-risk-scorer.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/ops-commander.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/options-trader.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/orchestration-engine.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/outcome-clustering.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/outreach-coordinator.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/painting-estimator.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/parent-comm-hub.md

- Status: implementation_reference_missing
- Actionable claim lines: 8
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/partner-tracker.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/partnership-dev.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/partnership-leverage.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/partnership-manager.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/parts-list.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/patent-research.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/patient-engagement.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/patient-intake-ai.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/payment-analytics-elite.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/payment-gateway-bot.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/payment-gateway.md

- Status: implementation_reference_missing
- Actionable claim lines: 8
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/payment-reconciliation.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/payout-reconciler.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/payroll-processor.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/pci-compliance.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/peer-review-ai.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/penny-stock.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/perf-per-dollar.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/perf-profiler.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/permit-tracker.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/perplexity-agent.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/personal-care-analytics-elite.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/personalization-engine.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/pest-control-mgr.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/pest-disease-scout.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/pharmacy-inventory.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/photo-video-app-bot.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/photography-workflow.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/pipeline-manager.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/pitch-craft-ai.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/pitch-deck.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/pivot-detector.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/planetary-risk-engine.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/platform-eng.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/playbook-writer.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/plumbing-estimator.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/podcast-producer.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/policy-deviation-alerts.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/policy-manager.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/pool-maintenance.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/portfolio-rebalancer.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/pos-analytics.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/pos-integrator.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/pos-terminal.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/ppe-tracker.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/pr-impact-sim.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/pr-press.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/precision-ag.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/predictive-analytics.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/predictive-engagement.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/predictive-maintenance.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/predictive-modeler.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/premiere-checklist.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/preventive-maint.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/price-tracker.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/print-mgr.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/privacy-compliance.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/probability-ranker.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/process-control.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/process-lifecycle.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/process-miner.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/process-redundancy-eliminator.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/procurement-auto.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/product-description.md

- Status: implementation_reference_missing
- Actionable claim lines: 8
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/product-market-fit.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/product-photo.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/production-agency.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/production-scheduler.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/productivity-app-bot.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/professional-dev.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/profit-center-tracker.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/profit-per-feature.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/profitability-anomaly.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/project-management.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/project-scheduler.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/prompt-engineer.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/property-liquidity.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/property-mgmt.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/property-risk-sim.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/property-value.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/protocol-builder.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/proxy-rotator.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/pt-calculator.md

- Status: implementation_reference_missing
- Actionable claim lines: 8
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/punch-list-app.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/push-notification-mgr.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/qa-assurance.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/quality-control.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/quality-inspector.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/quant-backtester.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/quantum-ai-bot.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/radiology-ai.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/rag-index.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/rank-insignia-guide.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/re-crowdfunding.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/re-investment.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/re-rebalancer.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/readiness-tracker.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/reading-level-ai.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/rebate-tracker.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/receipt-scanner.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/reception-bot.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/recipe-scaler.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/recruitment-military.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/recurring-task-optimizer.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/reentry-program.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/reference-app-bot.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/referral-program-mgr.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/regex-builder.md

- Status: implementation_reference_missing
- Actionable claim lines: 8
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/regional-anomaly-cluster.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/regional-downtime-alert.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/regulatory-change-auto.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/regulatory-reporter.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/reit-predictor.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/relevance-agent.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/renewal-calendar.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/rental-cashflow-bot.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/report-automation.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/reputation-attack-monitor.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/research-analyst.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/research-analytics-elite.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/research-bot.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/research-compliance.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/research-data-mgr.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/reservation-ai.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/resilience-scorer.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/resource-alloc-optimizer.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/resource-directory.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/resource-eligibility-bot.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/resource-forecaster.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/resource-scheduler.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/resume-builder-bot.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/retail-product-mgr.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/retainer-model.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/retention-risk-ai.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/returns-optimizer.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/revenue-continuity.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/revenue-engine.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/revenue-impact-prioritizer.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/revenue-journey-optimizer.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/revenue-leakage-alert.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/revenue-max-engine.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/revenue-model.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/revenue-optimizer.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/revenue-per-cohort.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/revenue-per-task.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/review-collector-bot.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/review-manager.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/rewards-maximizer.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/rfi-tracker.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/risk-escalation-predictor.md

- Status: implementation_reference_missing
- Actionable claim lines: 8
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/risk-legal-recommender.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/risk-manager.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/risk-monitor.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/risk-scenario-modeler.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/robo-advisor.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/robot-task-spec.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/rogue-bot-isolator.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/roi-per-client.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/roofing-estimator.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/route-optimizer.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/royalty-modeler.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/royalty-split.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/rpa-bot.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/rumor-validation.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/saas-builder.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/saas-churn.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/saas-onboarding.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/saas-package-bot.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/saas-pricing.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/saas-status-page.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/safety-checklist.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/safety-compliance-const.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/safety-envelope.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/safety-mfg.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/sales-performance.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/salon-scheduler.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/sample-tracker.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/savings-analytics-elite.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/scaling-playbook.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/scenario-comparison.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/scheduling-bot.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/school-safety-ai.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/scope-manager.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/scope-writer.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/scrap-tracker.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/script-coach.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/seasonal-planner.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/security-compliance.md

- Status: implementation_reference_missing
- Actionable claim lines: 8
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/security-patrol.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/security-posture.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/security-scanner.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/self-debug-engine.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/sentiment-drift-detector.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/sentiment-manipulation-alert.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/seo-optimizer.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/session-tracker-bot.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/shift-handover.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/shipment-visibility.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/shipping-dock.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/shipping-optimizer.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/shopify-bot.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/shopping-app-bot.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/sim-scenario.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/site-logistics.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/skincare-routine.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/sku-rights.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/sla-compliance-tracker.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/sla-monitor.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/smart-building-ai.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/smart-building-elite.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/smart-building.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/smart-factory.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/social-commerce.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/social-content.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/social-impact-elite.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/social-net-app-bot.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/social-scheduler.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/social-sharing-bot.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/soil-analyzer.md

- Status: implementation_reference_missing
- Actionable claim lines: 8
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/sow-generator.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/spa-manager.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/space-ai-bot.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/split-pay-calc.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/sports-app-bot.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/staff-scheduler-food.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/staffing-plan.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/stakeholder-impact.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/stakeholder-risk-mitigator.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/staking-mgr.md

- Status: implementation_reference_missing
- Actionable claim lines: 8
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/startup-analytics-elite.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/startup-costs.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/stock-asset-finder.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/stock-trading-bot.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/strategic-revenue-proj.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/strategic-timing.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/strategy-planner.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/streaming-engine.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/stripe-billing.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/student-analytics.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/student-loan.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/subcontractor-mgr.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/subscription-billing.md

- Status: implementation_reference_missing
- Actionable claim lines: 8
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/subscription-box.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/subscription-lifecycle-mgr.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/subscription-lifecycle.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/substance-abuse.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/substitute-mgr.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/succession-planner.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/superagi-agent.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/supplier-manager.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/supply-chain-ag.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/supply-chain-mfg.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/supply-chain-optimizer.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/supreme-compliance.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/surgical-scheduler.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/surveillance-analytics.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/sustainability-food.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/swarm-agent.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/syndication-mgr.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/tactical-strategic-tradeoff.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/takedown-draft.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/talent-matcher.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/task-acceleration.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/task-delegation-ai.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/task-dependency-mgr.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/task-impact-scorer.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/task-reliability-opt.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/task-scheduler.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/tax-incentive-finder.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/tax-lien.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/tax-optimizer.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/telehealth-assistant.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/terminal-deploy.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/territory-planner.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/test-generator.md

- Status: implementation_reference_missing
- Actionable claim lines: 10
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/therapy-notes-ai.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/thesis-writing-ai.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/threat-assessment.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/threat-intel-integrator.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/threat-prioritizer.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/threejs-addons.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/threejs-animation.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/threejs-audio.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/threejs-cameras.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/threejs-core.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/threejs-extras.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/threejs-geometries.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/threejs-global.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/threejs-helpers.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/threejs-lights.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/threejs-loaders.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/threejs-materials.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/threejs-math.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/threejs-nodes.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/threejs-objects.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/threejs-renderers.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/threejs-scenes.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/threejs-textures.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/threejs-tsl.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/throughput-maximizer.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/thumbnail-brief.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/time-attendance.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/time-tracker.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/tip-calculator.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/tip-processing.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/tms-integrator.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/token-billing.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/token-launch.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/tool-inventory.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/toolbox-talks.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/track-chooser.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/trade-compliance-engine.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/trade-finance.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/trade-master.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/tradeoff-analyzer.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/trading-bot-mgr.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/traffic-spike-predictor.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/trailer-tracker.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/training-cert.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/training-matrix.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/training-simulator.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/transition-assist.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/transport-analytics-elite.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/travel-agency.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/travel-app-bot.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/travel-coordinator.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/treasury-analyzer.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/tutoring-matcher.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/uptime-probability.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/urban-heatmap.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/user-feedback-aggregator.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/user-retention-engine.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/user-segmentation-bot.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/utilities-app-bot.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/utilization-optimizer.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/vaccine-tracker.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/vector-db-optimizer.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/vehicle-maintenance.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/vendor-compare.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/vendor-manager.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/venture-dealflow.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/venture-studio.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/vertical-farm.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/vfx-supervisor.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/video-editor-ai.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/video-script.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/visa-checklist.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/visual-merch.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/visual-planner.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/volunteer-mgr.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/vuln-propagation.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/warehouse-manager.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/warehouse-ops.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/warehouse-robot.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/wargame-simulator.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/weather-app-bot.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/weather-farming.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/weather-impact.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/web-scraper.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/webhook-tester.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/website-builder.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/wellness-coach.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/wellness-retreat.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/whale-tracker.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/white-label-saas.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/whitelabel-empire.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/whitelabel-publisher.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/whitepaper-ebook.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/wholesale-manager.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/wholesale-trade-bot.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/wine-sommelier.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/work-order-mgr.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/workflow-anomaly-alerts.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/workflow-bottleneck.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/workflow-builder.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/workflow-harmonizer.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/workflow-team-builder.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/workout-timer.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/workplace-experience.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/yield-farmer.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/yoga-studio.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/youth-program.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/zero-day-alert.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### bots/zoning-compliance.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### buddy/autonomy/README.md

- Status: implementation_reference_missing
- Actionable claim lines: 4
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### buddy/autonomy/pr_backlog_recovery_plan.md

- Status: implementation_reference_missing
- Actionable claim lines: 2
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### buddy/bench/GOALS.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### buddy/bootcamp/README.md

- Status: implementation_reference_missing
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### buddy/easy_github/FOR_ANY_REPOSITORY.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### buddy/easy_github/MAP.md

- Status: implementation_reference_missing
- Actionable claim lines: 2
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### buddy/easy_github/SAY_THIS.md

- Status: implementation_reference_missing
- Actionable claim lines: 2
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### buddy/easy_github/START_HERE.md

- Status: implementation_reference_missing
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### buddy/easy_github/WORDS.md

- Status: implementation_reference_missing
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### buddy/frontier/FRONTIER_BUILD_PLAN.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### buddy/frontier/README.md

- Status: implementation_reference_missing
- Actionable claim lines: 2
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### buddy/frontier/evaluation_matrix.md

- Status: implementation_reference_missing
- Actionable claim lines: 10
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### buddy/learning/DEPENDENCY_REDUCTION.md

- Status: implementation_reference_missing
- Actionable claim lines: 3
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### buddy/learning/DEPENDENCY_REDUCTION_CHECKLIST.md

- Status: implementation_reference_missing
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### buddy/learning/LEARNING_FROM_FAILURES.md

- Status: implementation_reference_missing
- Actionable claim lines: 2
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### buddy/learning/LEARNING_METRICS.md

- Status: implementation_reference_missing
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### buddy/learning/MODEL_CARD.md

- Status: test_reference_missing
- Actionable claim lines: 0
- Implementation paths: buddy/easy_github/skills_00.json
- Test paths: None detected
- Missing paths: None detected
- Next action: Add focused tests and acceptance evidence for the referenced implementation.
- Execution verified: No; run-specific evidence is required.

### buddy/learning/README.md

- Status: implementation_reference_missing
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### buddy/learning/REASONING_AND_LEARNING.md

- Status: implementation_reference_missing
- Actionable claim lines: 3
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### buddy/learning/continuous_learning_policy.md

- Status: implementation_reference_missing
- Actionable claim lines: 3
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### buddy/learning/learning_cycle_contract.md

- Status: implementation_reference_missing
- Actionable claim lines: 2
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### buddy/memory/README.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### buddy/openrouter/OPENROUTER_INTEGRATION.md

- Status: implementation_reference_missing
- Actionable claim lines: 4
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### buddy/openrouter/README.md

- Status: implementation_reference_missing
- Actionable claim lines: 4
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### buddy_os/README.md

- Status: broken_path_references
- Actionable claim lines: 5
- Implementation paths: buddy_os/integration/runtime_map.yaml, dreamco_platform/automation/task_runner.py, server/buddy-model-policy.ts, server/fleet-runtime.ts, tools/buddy_cli.py, tools/buddy_local_bridge.py
- Test paths: tests/test_buddy_os_contracts.py
- Missing paths: github/workflows/buddy-actions-test-lab.yml, github/workflows/buddy-os-contracts.yml, github/workflows/dreamco-control-center.yml
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### capabilities/BUDDY_CAPABILITIES_CATALOG.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### capabilities/BUDDY_CAPABILITY_CATALOG.md

- Status: implementation_reference_missing
- Actionable claim lines: 13
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### capabilities/media_cloning/README.md

- Status: implementation_reference_missing
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### client/requirements.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### config/repository_scan_update_pr_scope.md

- Status: implementation_reference_missing
- Actionable claim lines: 2
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### config/repository_scan_update_pr_scope_final.md

- Status: implementation_reference_missing
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### data/dreamco_knowledge/assets/_candidates/edu_cs_11.0701/README.md

- Status: implementation_reference_missing
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### data/dreamco_knowledge/assets/_candidates/edu_cs_11.0701/v2/README.md

- Status: broken_path_references
- Actionable claim lines: 5
- Implementation paths: tools/score_data_package_candidate.py
- Test paths: None detected
- Missing paths: data/dreamco_knowledge/evidence/<kind>/<asset_id>/<YYYYMMDD>-<NN>.json
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### data/dreamco_knowledge/assets/_candidates/edu_cs_11.0701/v3/README.md

- Status: broken_path_references
- Actionable claim lines: 8
- Implementation paths: tools/license_provenance_gate.py, tools/score_data_package_candidate.py
- Test paths: tests/test_license_provenance_gate.py
- Missing paths: authored/target_overrides.json, data/practice_tasks.json, projections/*.candidate.json, verification/diversity_report.json, verification/leakage_report.json, verification/regression_and_evidence_check.json
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### data/dreamco_knowledge/assets/_candidates/edu_cs_11.0701/v4/README.md

- Status: broken_path_references
- Actionable claim lines: 14
- Implementation paths: tools/license_provenance_gate.py, tools/minimal_json_schema.py, tools/score_data_package_candidate.py
- Test paths: tests/test_license_provenance_gate.py
- Missing paths: data/practice_tasks.json, docs/data_dictionary.json, repo>/<evidence_root>/<kind>/<asset_id>/<run>.json, repo_root>/<evidence_root>/<kind>/<asset_id>/<run>.json, tests/test_build.py, verification/gate_all_1044_summary.json, verification/leakage_report_v4.json, verification/license_gate_cs_without_repo_root.json, verification/license_gate_generated_sample_14.4802.json
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### data/dreamco_knowledge/assets/_candidates/edu_cs_11.0701/v5/README.md

- Status: broken_path_references
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: authored/*.json, data/practice_tasks.json, evidence_root>/holdout/edu-cs-11.0701/<run>.json
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### data/dreamco_knowledge/packages/DP-ONET-OCC-SYN/0.0.1/ATTRIBUTION.md

- Status: implementation_reference_missing
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### data/dreamco_knowledge/packages/DP-ONET-OCC-SYN/0.0.1/MODIFICATIONS.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### data/dreamco_knowledge/packages/DP-ONET-OCC-SYN/0.0.1/data_dictionary.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### data/dreamco_knowledge/packages/DP-ONET-OCC-SYN/0.0.1/dataset_card.md

- Status: test_reference_missing
- Actionable claim lines: 2
- Implementation paths: tools/build_universal_work_ai_catalog.py, tools/license_provenance_gate.py
- Test paths: None detected
- Missing paths: None detected
- Next action: Add focused tests and acceptance evidence for the referenced implementation.
- Execution verified: No; run-specific evidence is required.

### data/dreamco_knowledge/packages/DP-ONET-OCC-SYN/0.0.2/ATTRIBUTION.md

- Status: implementation_reference_missing
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### data/dreamco_knowledge/packages/DP-ONET-OCC-SYN/0.0.2/MODIFICATIONS.md

- Status: test_reference_missing
- Actionable claim lines: 1
- Implementation paths: tools/build_dp_onet_occ_syn_sample.py
- Test paths: None detected
- Missing paths: None detected
- Next action: Add focused tests and acceptance evidence for the referenced implementation.
- Execution verified: No; run-specific evidence is required.

### data/dreamco_knowledge/packages/DP-ONET-OCC-SYN/0.0.2/data_dictionary.md

- Status: test_reference_missing
- Actionable claim lines: 1
- Implementation paths: tools/build_dp_onet_occ_syn_sample.py
- Test paths: None detected
- Missing paths: None detected
- Next action: Add focused tests and acceptance evidence for the referenced implementation.
- Execution verified: No; run-specific evidence is required.

### data/dreamco_knowledge/packages/DP-ONET-OCC-SYN/0.0.2/dataset_card.md

- Status: test_reference_missing
- Actionable claim lines: 1
- Implementation paths: tools/score_data_package_dataset.py
- Test paths: None detected
- Missing paths: None detected
- Next action: Add focused tests and acceptance evidence for the referenced implementation.
- Execution verified: No; run-specific evidence is required.

### data/dreamco_knowledge/packages/DP-ONET-OCC-SYN/0.0.2/sample/occupation_cards.md

- Status: implementation_reference_missing
- Actionable claim lines: 30
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### database/migrations/README_DIVISION_DATASET_CATALOG.md

- Status: test_reference_missing
- Actionable claim lines: 9
- Implementation paths: buddy/datasets/postgres_catalog.py
- Test paths: None detected
- Missing paths: None detected
- Next action: Add focused tests and acceptance evidence for the referenced implementation.
- Execution verified: No; run-specific evidence is required.

### docs/500_MODEL_RESEARCH.md

- Status: implementation_reference_missing
- Actionable claim lines: 2
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/ACTIONS_CONTROL_PLANE.md

- Status: implementation_reference_missing
- Actionable claim lines: 2
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/ACTIONS_RECOVERY_AND_BENCHMARK_DASHBOARD.md

- Status: implementation_reference_missing
- Actionable claim lines: 10
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/ACTIONS_RECOVERY_BUTTONS.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/AGI_CAPABILITY_ARCHITECTURE.md

- Status: implementation_reference_missing
- Actionable claim lines: 11
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/AI_ADVANCEMENT_MUSIC_VIDEO.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/AI_RESEARCH_OBSERVATORY.md

- Status: implementation_reference_missing
- Actionable claim lines: 2
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/ARCHITECTURE.md

- Status: implementation_reference_missing
- Actionable claim lines: 4
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/BENCHMARK_DRIVEN_CAPABILITY_ENGINE.md

- Status: implementation_reference_missing
- Actionable claim lines: 2
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/BENCHMARK_EVIDENCE_LIFECYCLE.md

- Status: implementation_reference_missing
- Actionable claim lines: 4
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/BOT_PRODUCTION_READINESS.md

- Status: implementation_reference_missing
- Actionable claim lines: 3
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/BOT_TO_CAPABILITY_MIGRATION.md

- Status: implementation_reference_missing
- Actionable claim lines: 3
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_1000_SOURCE_BOOTCAMP.md

- Status: implementation_reference_missing
- Actionable claim lines: 4
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_1000_SOURCE_BOT_TRAINING_GROUND.md

- Status: implementation_reference_missing
- Actionable claim lines: 12
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_14_DAY_MODEL_GROWTH_PLAN.md

- Status: test_reference_missing
- Actionable claim lines: 9
- Implementation paths: buddy/gpt_baseline/tiny_gpt.py, tools/run_buddy_gpt_baseline.py
- Test paths: None detected
- Missing paths: None detected
- Next action: Add focused tests and acceptance evidence for the referenced implementation.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_24H_GAP_CLOSURE.md

- Status: implementation_reference_missing
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_65_MASTERBOT_OPERATING_SYSTEM.md

- Status: implementation_reference_missing
- Actionable claim lines: 19
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_ACTIONS_ACCEPTANCE_TESTS.md

- Status: implementation_reference_missing
- Actionable claim lines: 9
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_ACTIONS_AGI_EXPERIENCE.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_ACTIONS_BUTTON_CONTRACT.md

- Status: test_reference_missing
- Actionable claim lines: 14
- Implementation paths: website/actions.html
- Test paths: None detected
- Missing paths: None detected
- Next action: Add focused tests and acceptance evidence for the referenced implementation.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_ACTIONS_ENGINE.md

- Status: implementation_reference_missing
- Actionable claim lines: 10
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_ACTIONS_EXECUTION_MATRIX.md

- Status: implementation_reference_missing
- Actionable claim lines: 15
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_ACTIONS_MASTER_ROADMAP.md

- Status: implementation_reference_missing
- Actionable claim lines: 18
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_ACTIONS_OS.md

- Status: implementation_reference_missing
- Actionable claim lines: 12
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_ACTIONS_UNIFIED_OPERATING_SYSTEM.md

- Status: implementation_reference_missing
- Actionable claim lines: 3
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_ACTION_MEMORY_AND_CONTEXT.md

- Status: implementation_reference_missing
- Actionable claim lines: 4
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_ADDITIONAL_TAXONOMY_SYSTEMS.md

- Status: test_reference_missing
- Actionable claim lines: 746
- Implementation paths: website/category-systems.html, website/data/additional-taxonomy-system-registry.json
- Test paths: None detected
- Missing paths: None detected
- Next action: Add focused tests and acceptance evidence for the referenced implementation.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_AGI_STYLE_REPAIR_ARCHITECTURE.md

- Status: implementation_reference_missing
- Actionable claim lines: 15
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_AUTOMATIC_BOT_ONBOARDING.md

- Status: implementation_reference_missing
- Actionable claim lines: 4
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_AUTONOMY_LEVELS_AND_GATES.md

- Status: implementation_reference_missing
- Actionable claim lines: 2
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_BENCHMARKS_101_200.md

- Status: implementation_reference_missing
- Actionable claim lines: 3
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_BENCHMARKS_201_250.md

- Status: implementation_reference_missing
- Actionable claim lines: 4
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_BENCHMARK_OBSTACLE_PLAYBOOK.md

- Status: implementation_reference_missing
- Actionable claim lines: 11
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_BOOTCAMP_AND_TRUST_FRAMEWORK.md

- Status: implementation_reference_missing
- Actionable claim lines: 11
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_BOOTCAMP_SANDBOX_SPEC.md

- Status: implementation_reference_missing
- Actionable claim lines: 18
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_BOT_BOOTCAMP.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_BUILD_RUNTIME.md

- Status: implementation_reference_missing
- Actionable claim lines: 5
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_CAPABILITY_BENCHMARK_REGISTRY.md

- Status: implementation_reference_missing
- Actionable claim lines: 5
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_CAPABILITY_GRAPH_V2.md

- Status: implementation_reference_missing
- Actionable claim lines: 3
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_CI_REPAIR_DATASETS_DATABASES_BENCHMARKS_AND_DISTILLATION.md

- Status: broken_path_references
- Actionable claim lines: 10
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: github/workflows/buddy-ci-safe-repair.yml, github/workflows/buddy-failure-learning-regression.yml
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_CONTINUOUS_LEARNING_OPERATING_MODEL.md

- Status: test_reference_missing
- Actionable claim lines: 2
- Implementation paths: tools/buddy_masterbot_training_lane.py
- Test paths: None detected
- Missing paths: None detected
- Next action: Add focused tests and acceptance evidence for the referenced implementation.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_CONTROL_PLANE.md

- Status: broken_path_references
- Actionable claim lines: 14
- Implementation paths: tools/buddy_control_plane.py, website/buddy-control.html, website/data/buddy-control-status.json
- Test paths: tests/test_buddy_control_plane.py
- Missing paths: github/workflows/buddy-command-router.yml
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_DATABASE_ROUTING_CONTRACT.md

- Status: implementation_reference_missing
- Actionable claim lines: 2
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_DATASET_HUB_AND_UNKNOWN_PROBLEM_ROUTER.md

- Status: implementation_reference_missing
- Actionable claim lines: 8
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_DATASET_HUB_RUNTIME_IMPLEMENTATION.md

- Status: implementation_reference_missing
- Actionable claim lines: 18
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_DEVICE_FABRIC.md

- Status: implementation_reference_missing
- Actionable claim lines: 9
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_DEVICE_INTELLIGENCE.md

- Status: implementation_reference_missing
- Actionable claim lines: 8
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_DISTILL_CONTRACT.md

- Status: broken_path_references
- Actionable claim lines: 0
- Implementation paths: tools/check_buddy_distill_gate.py
- Test paths: tests/test_check_buddy_distill_gate.py
- Missing paths: github/workflows/buddy-distill-gate.yml
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_DREAMCO_MASTER_VISION.md

- Status: implementation_reference_missing
- Actionable claim lines: 36
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_ENDGAME_ARCHITECTURE.md

- Status: implementation_reference_missing
- Actionable claim lines: 8
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_F0_EVIDENCE_PACKET.md

- Status: implementation_reference_missing
- Actionable claim lines: 2
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_F0_PATHS_TO_CREATE.md

- Status: implementation_reference_missing
- Actionable claim lines: 2
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_FAILURE_DETECTION_RECOVERY_LEARNING.md

- Status: test_reference_missing
- Actionable claim lines: 13
- Implementation paths: tools/buddy_failure_learning.py
- Test paths: None detected
- Missing paths: None detected
- Next action: Add focused tests and acceptance evidence for the referenced implementation.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_FRONTIER_EVALUATION_HARNESS.md

- Status: implementation_reference_missing
- Actionable claim lines: 3
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_FRONTIER_PROMOTION_CHECKLIST.md

- Status: broken_path_references
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: config/buddy/approved-models-allowlist.json, evidence/frontier/<suite>.bundle.json
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_GAIN_TO_PRODUCTION_PIPELINE.md

- Status: implementation_reference_missing
- Actionable claim lines: 5
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_GITHUB_COMPETITOR_MASTER_PLAN.md

- Status: implementation_reference_missing
- Actionable claim lines: 16
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_GITHUB_TRANSITION_CONTRACT.md

- Status: implementation_reference_missing
- Actionable claim lines: 2
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_GOVERNANCE_STATUS.md

- Status: implementation_reference_missing
- Actionable claim lines: 5
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_GOVERNED_EXPERIMENT_SANDBOX.md

- Status: implementation_reference_missing
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_GPT_STYLE_MODEL_BOOTCAMP.md

- Status: implementation_and_test_paths_referenced_not_verified
- Actionable claim lines: 19
- Implementation paths: buddy/bootcamp/buddy_bootcamp.yaml, buddy/gpt_baseline/tiny_gpt.py, buddy/learning/study_methods.py, tools/bootcamp_lesson_planner.py, tools/run_buddy_gpt_baseline.py
- Test paths: tests/test_buddy_gpt_baseline.py
- Missing paths: None detected
- Next action: Run the linked tests and attach CI, benchmark, regression, and runtime evidence before promotion.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_GREEN_BY_TONIGHT_RUNBOOK.md

- Status: implementation_reference_missing
- Actionable claim lines: 10
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_HF_PACKAGES.md

- Status: broken_path_references
- Actionable claim lines: 0
- Implementation paths: website/data/buddy-hf-packages.json
- Test paths: None detected
- Missing paths: github/workflows/sync-to-huggingface.yml
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_LAPTOP_APP_TESTING.md

- Status: implementation_reference_missing
- Actionable claim lines: 5
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_LAPTOP_CLI_20_OPTIONS.md

- Status: implementation_reference_missing
- Actionable claim lines: 4
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_LONG_TERM_SUCCESS_PATH.md

- Status: implementation_reference_missing
- Actionable claim lines: 5
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_MARKDOWN_TO_IMPLEMENTATION_GAP_POLICY.md

- Status: test_reference_missing
- Actionable claim lines: 7
- Implementation paths: tools/audit_markdown_implementation_gaps.py, website/data/markdown-implementation-gap-audit.json, website/markdown-gap-audit.html
- Test paths: None detected
- Missing paths: None detected
- Next action: Add focused tests and acceptance evidence for the referenced implementation.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_OBSERVED_CAPABILITY_RUNTIME.md

- Status: test_reference_missing
- Actionable claim lines: 5
- Implementation paths: buddy/capabilities/runtime.py, buddy/store/own_model.py, server/open-model-lab-policy.ts, shared/model-provider-sources.ts, tools/check_buddy_distill_gate.py
- Test paths: None detected
- Missing paths: None detected
- Next action: Add focused tests and acceptance evidence for the referenced implementation.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_PERSONAL_MEMORY_SHARED_LEARNING_AND_PERSONALITY.md

- Status: implementation_reference_missing
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_PLATFORM_READINESS_SCORECARD.md

- Status: implementation_reference_missing
- Actionable claim lines: 15
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_REPAIR_EVENT_SCHEMA.md

- Status: implementation_reference_missing
- Actionable claim lines: 3
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_REPAIR_INTELLIGENCE_SCORECARD.md

- Status: implementation_reference_missing
- Actionable claim lines: 5
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_REPAIR_ORCHESTRATOR_IMPLEMENTATION_PLAN.md

- Status: broken_path_references
- Actionable claim lines: 10
- Implementation paths: tools/buddy_failure_learning.py
- Test paths: tests/test_buddy_failure_learning.py
- Missing paths: github/workflows/buddy-failure-learning.yml
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_REPAIR_ORCHESTRATOR_SPEC.md

- Status: implementation_reference_missing
- Actionable claim lines: 11
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_REPOSITORY_REPAIR_DATASETS_BENCHMARKS_AND_DISTILLATION.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_RESOURCE_COVERAGE_FRAMEWORK.md

- Status: broken_path_references
- Actionable claim lines: 530
- Implementation paths: shared/ai-models.ts, tools/refresh_buddy_technology_radar.py, website/category-systems.html, website/category-systems.js, website/data/additional-taxonomy-system-registry.json, website/data/category-system-registry.json, website/data/task-taxonomy-system-registry.json, website/markdown-gap-audit.html, website/technology-radar.html
- Test paths: tests/test_buddy_category_system_registry.py
- Missing paths: config/buddy-study-resources-*.json
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_RESOURCE_MAP.md

- Status: broken_path_references
- Actionable claim lines: 8
- Implementation paths: tools/generate_resource_connection_catalog.py, website/data/buddy-resource-connection-catalog.json
- Test paths: None detected
- Missing paths: /config/buddy/resource-registry.json
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_SANDBOX_BOOTCAMP_DATA_PACKAGE.md

- Status: implementation_reference_missing
- Actionable claim lines: 9
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_TASK_AND_MARKDOWN_TAXONOMY_SYSTEMS.md

- Status: test_reference_missing
- Actionable claim lines: 10
- Implementation paths: website/category-systems.html, website/data/task-taxonomy-system-registry.json
- Test paths: None detected
- Missing paths: None detected
- Next action: Add focused tests and acceptance evidence for the referenced implementation.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_THREE_QUEUE_OPERATING_MODEL.md

- Status: implementation_reference_missing
- Actionable claim lines: 16
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_TINY_GPT_BASELINE_MODEL_CARD.md

- Status: implementation_reference_missing
- Actionable claim lines: 2
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_TOOL_SKILL_CATALOG.md

- Status: implementation_reference_missing
- Actionable claim lines: 10
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_UNIVERSAL_CREATION_ENGINE.md

- Status: implementation_reference_missing
- Actionable claim lines: 11
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_UNIVERSAL_LEARNING_AND_MASTERY_LOOP.md

- Status: implementation_reference_missing
- Actionable claim lines: 4
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_UNIVERSAL_LEARNING_ENGINE.md

- Status: implementation_reference_missing
- Actionable claim lines: 17
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_USER_DATA_OWNERSHIP_AND_SUBSCRIPTION_CONTROL.md

- Status: implementation_and_test_paths_referenced_not_verified
- Actionable claim lines: 6
- Implementation paths: server/connection-policy.ts, server/data-rights-policy.ts, server/user-control-center-policy.ts, shared/personal-buddy-training-contract.ts
- Test paths: tests/task-and-data-policy.test.ts
- Missing paths: None detected
- Next action: Run the linked tests and attach CI, benchmark, regression, and runtime evidence before promotion.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_USER_TESTING_CATALOG.md

- Status: implementation_reference_missing
- Actionable claim lines: 24
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_VIBE_CODING_CONTRACT.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_VIBE_CODING_REVERSE_ENGINEERING_DISTILLATION_AND_TRAINING.md

- Status: implementation_reference_missing
- Actionable claim lines: 16
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_WEB_LEARNING_FABRIC.md

- Status: implementation_reference_missing
- Actionable claim lines: 4
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_WEB_SOURCE_CONNECTION.md

- Status: implementation_reference_missing
- Actionable claim lines: 4
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/BUDDY_WEIGHT_OWNERSHIP.md

- Status: implementation_reference_missing
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/CAPABILITY_BENCHMARK_LADDER.md

- Status: implementation_reference_missing
- Actionable claim lines: 2
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/CAPABILITY_FIRST_DEVELOPER_GUIDE.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/CAPABILITY_GENOME_EXPERIMENT_ENGINE.md

- Status: implementation_reference_missing
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/CHAT_HISTORY_2026-08-28.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/CHAT_PRODUCTION_WORKLOG.md

- Status: broken_path_references
- Actionable claim lines: 7
- Implementation paths: tools/production_readiness_gate.py
- Test paths: None detected
- Missing paths: github/workflows/production-readiness.yml
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### docs/CODERABBIT_PARITY_MATRIX.md

- Status: implementation_reference_missing
- Actionable claim lines: 28
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/CODING_CAPABILITY_BENCHMARK_LAB.md

- Status: implementation_reference_missing
- Actionable claim lines: 5
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/CONSOLIDATED_PR_INTEGRATION_MANIFEST.md

- Status: test_reference_missing
- Actionable claim lines: 5
- Implementation paths: client/src/pages/ActionsPage.tsx
- Test paths: None detected
- Missing paths: None detected
- Next action: Add focused tests and acceptance evidence for the referenced implementation.
- Execution verified: No; run-specific evidence is required.

### docs/CONTINUOUS_INNOVATION_AND_LIBRARY_SPECIALISTS.md

- Status: implementation_reference_missing
- Actionable claim lines: 10
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/CONVERSATION_SYSTEM_INTEGRATION_SPEC.md

- Status: implementation_reference_missing
- Actionable claim lines: 10
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/CUSTOMER_PRODUCTION_RUNBOOK.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/DEFINITION_OF_DONE.md

- Status: implementation_reference_missing
- Actionable claim lines: 2
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/DEFINITION_OF_READY.md

- Status: implementation_reference_missing
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/DEPLOYMENT_COST_POLICY.md

- Status: implementation_reference_missing
- Actionable claim lines: 3
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/DEVELOPER_ONRAMP.md

- Status: test_reference_missing
- Actionable claim lines: 9
- Implementation paths: tools/audit_actions_health.py
- Test paths: None detected
- Missing paths: None detected
- Next action: Add focused tests and acceptance evidence for the referenced implementation.
- Execution verified: No; run-specific evidence is required.

### docs/DREAMCO_2027_VERIFIED_DELIVERY_PROGRAM.md

- Status: implementation_reference_missing
- Actionable claim lines: 14
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/DREAMCO_BEGINNER_FIRST_PRODUCT_EXPERIENCE.md

- Status: implementation_reference_missing
- Actionable claim lines: 14
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/DREAMCO_BUDDY_MASTER_CODEX_DIRECTIVE.md

- Status: broken_path_references
- Actionable claim lines: 380
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: command-center/data/master-build-status.json, framework/base_bot.py, framework/global_ai_sources_flow.py, global_learning_system/learning_loop.py, integrations/auth.py, integrations/base.py, integrations/errors.py, integrations/health.py, integrations/policies.py, integrations/registry.py, tools/auto_recovery.py, tools/check_bot_framework.py, tools/generate_bot_skeleton.py
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### docs/DREAMCO_BUILD_YOUR_OWN_AI_FLAGSHIP.md

- Status: implementation_reference_missing
- Actionable claim lines: 16
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/DREAMCO_CHAT_CONTEXT_2026-08-11.md

- Status: implementation_reference_missing
- Actionable claim lines: 24
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/DREAMCO_CREATIVE_AI_FRONTIER_GOALS.md

- Status: implementation_reference_missing
- Actionable claim lines: 3
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/DREAMCO_DELIVERY_PLAN.md

- Status: test_reference_missing
- Actionable claim lines: 17
- Implementation paths: tools/chat_implementation_audit.py
- Test paths: None detected
- Missing paths: None detected
- Next action: Add focused tests and acceptance evidence for the referenced implementation.
- Execution verified: No; run-specific evidence is required.

### docs/DREAMCO_DIVISION_MODEL_COMPETITIVENESS.md

- Status: implementation_reference_missing
- Actionable claim lines: 4
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/DREAMCO_DIVISION_MODEL_EVIDENCE_GATE.md

- Status: implementation_reference_missing
- Actionable claim lines: 9
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/DREAMCO_DIVISION_SCHEMA_PROVISIONING.md

- Status: implementation_reference_missing
- Actionable claim lines: 4
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/DREAMCO_ENGINEERING_OPERATING_SYSTEM.md

- Status: test_reference_missing
- Actionable claim lines: 3
- Implementation paths: tools/build_runtime_sync_plan.py, tools/recover_legacy_bots.py, tools/run_everything_now.py
- Test paths: None detected
- Missing paths: None detected
- Next action: Add focused tests and acceptance evidence for the referenced implementation.
- Execution verified: No; run-specific evidence is required.

### docs/DREAMCO_FLAGSHIP_GO_TO_MARKET.md

- Status: implementation_reference_missing
- Actionable claim lines: 24
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/DREAMCO_GLOBAL_RECONCILIATION.md

- Status: broken_path_references
- Actionable claim lines: 7
- Implementation paths: tools/dreamco_global_reconciliation.py
- Test paths: None detected
- Missing paths: github/workflows/dreamco-global-reconciliation.yml
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### docs/DREAMCO_GOVERNED_DATASET_INGESTION.md

- Status: test_reference_missing
- Actionable claim lines: 7
- Implementation paths: buddy/datasets/license_policy.py
- Test paths: None detected
- Missing paths: None detected
- Next action: Add focused tests and acceptance evidence for the referenced implementation.
- Execution verified: No; run-specific evidence is required.

### docs/DREAMCO_MASTERY_CONTINUITY_SYSTEM.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/DREAMCO_MASTER_PLAN.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/DREAMCO_MASTER_ROADMAP_2026.md

- Status: broken_path_references
- Actionable claim lines: 10
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: framework/global_ai_sources_flow.py
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### docs/DREAMCO_OBJECT_STORAGE_EVIDENCE.md

- Status: implementation_reference_missing
- Actionable claim lines: 9
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/DREAMCO_POSTGRES_DIVISION_PROBE.md

- Status: implementation_reference_missing
- Actionable claim lines: 2
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/DREAMCO_REBUILD_V2.md

- Status: implementation_reference_missing
- Actionable claim lines: 18
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/DREAMCO_REVENUE_OPERATING_GUIDE.md

- Status: broken_path_references
- Actionable claim lines: 11
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: money/affiliate_engine.js, money/lead_seller.js, workflows/crypto.json, workflows/fiverr.json, workflows/grants.json, workflows/legal_money.json, workflows/real_estate.json
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### docs/ENGINEERING_CONVENTIONS.md

- Status: implementation_reference_missing
- Actionable claim lines: 9
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/FLEET_ONE_WEEK_BUILD_PLAN.md

- Status: broken_path_references
- Actionable claim lines: 4
- Implementation paths: None detected
- Test paths: tests/test_build_queue.py
- Missing paths: config/bots/run-policy-overrides.json
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### docs/FREE_FIRST_LEARNING_POLICY.md

- Status: implementation_reference_missing
- Actionable claim lines: 2
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/FRONTIER_CLAIM_TRUST_GATES.md

- Status: broken_path_references
- Actionable claim lines: 4
- Implementation paths: tools/check_frontier_claim_trust_gates.py, tools/verify_frontier_evidence.py
- Test paths: None detected
- Missing paths: config/generated/sandbox-24h-tick.json, github/workflows/deploy-buddy-pages.yml, github/workflows/frontier-claim-trust-gate.yml
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### docs/FRONTIER_EVIDENCE_PLAN_2026.md

- Status: test_reference_missing
- Actionable claim lines: 6
- Implementation paths: tools/verify_frontier_evidence.py
- Test paths: None detected
- Missing paths: None detected
- Next action: Add focused tests and acceptance evidence for the referenced implementation.
- Execution verified: No; run-specific evidence is required.

### docs/FRONTIER_SUPERBOT_LOOP.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/GAIN_PRODUCTION_PIPELINE_PLAN.md

- Status: implementation_reference_missing
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/GEOMETRIC_REASONING.md

- Status: implementation_reference_missing
- Actionable claim lines: 3
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/GITHUB_FIRST_PERSONAL_AI_SETUP.md

- Status: implementation_reference_missing
- Actionable claim lines: 16
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/GITHUB_MODEL_REPOSITORY.md

- Status: broken_path_references
- Actionable claim lines: 17
- Implementation paths: tools/buddy_local_repository.py
- Test paths: None detected
- Missing paths: github/dependabot.yml, github/workflows/codeql.yml, github/workflows/dependency-review.yml
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### docs/GITHUB_PAGES_UNIVERSE_LINK_PLAN.md

- Status: broken_path_references
- Actionable claim lines: 7
- Implementation paths: website/actions.html, website/autonomy.html, website/bots.html, website/hf-bootcamp.html, website/learn-hf.html, website/models.html, website/nav.js, website/os.html, website/own-bootcamp.html
- Test paths: None detected
- Missing paths: github/workflows/deploy-buddy-pages.yml, github/workflows/pages.yml, website/<page>.html
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### docs/GLOBAL_AI_SOURCES_FLOW_SPEC.md

- Status: broken_path_references
- Actionable claim lines: 9
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: framework/global_ai_sources_flow.py
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### docs/GLOBAL_GOVERNMENT_IMPROVEMENT_PROGRAM.md

- Status: implementation_reference_missing
- Actionable claim lines: 4
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/GREENKEEPER_AUTOBUILDER.md

- Status: implementation_reference_missing
- Actionable claim lines: 5
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/GROK_CAPABILITIES_FOR_DREAMCO.md

- Status: broken_path_references
- Actionable claim lines: 12
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: App_bots/*.json
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### docs/GROK_TEACHES_BUDDY_SYLLABUS_v0.md

- Status: test_reference_missing
- Actionable claim lines: 3
- Implementation paths: buddy/bootcamp/buddy_bootcamp.yaml, tools/bootcamp_lesson_planner.py
- Test paths: None detected
- Missing paths: None detected
- Next action: Add focused tests and acceptance evidence for the referenced implementation.
- Execution verified: No; run-specific evidence is required.

### docs/HUGGINGFACE_MASTERY_PLAN.md

- Status: broken_path_references
- Actionable claim lines: 3
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: config/generated/hf-hub-literacy-checklist.json
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### docs/LAPTOP_VR_ARCHITECTURE.md

- Status: implementation_reference_missing
- Actionable claim lines: 4
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/LEGACY_BOT_LINEAGE_AND_DIVISION_MAP.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/LOCAL_BACKEND.md

- Status: implementation_reference_missing
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/LOCAL_BUDDY_MODEL_BLUEPRINT.md

- Status: implementation_reference_missing
- Actionable claim lines: 4
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/MASTERBOT_45_DOMAIN_CROSSWALK.md

- Status: test_reference_missing
- Actionable claim lines: 0
- Implementation paths: shared/division-production-contract.ts
- Test paths: None detected
- Missing paths: None detected
- Next action: Add focused tests and acceptance evidence for the referenced implementation.
- Execution verified: No; run-specific evidence is required.

### docs/MASTER_PLAN.md

- Status: broken_path_references
- Actionable claim lines: 9
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: config/*.json
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### docs/MEDIA_GAME_CAPABILITY_ROADMAP.md

- Status: implementation_reference_missing
- Actionable claim lines: 11
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/MODEL_LAB_BENCHMARK_SCHEMA.md

- Status: implementation_reference_missing
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/MODEL_LAB_FOR_USERS.md

- Status: implementation_reference_missing
- Actionable claim lines: 2
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/MODEL_PROSPECTUS_AND_COMPARISON_PLAN.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/MODERNIZATION_EXECUTION_PLAN.md

- Status: broken_path_references
- Actionable claim lines: 11
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: tools/create_bot.py
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### docs/NEW_BOT_AUTO_ROUTING.md

- Status: implementation_reference_missing
- Actionable claim lines: 8
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/NEXT_100_DEEP_REPO_UPGRADES.md

- Status: implementation_reference_missing
- Actionable claim lines: 12
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/NEXT_100_OWNER_UPGRADES.md

- Status: implementation_reference_missing
- Actionable claim lines: 20
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/NOTES_ORGANIZATION.md

- Status: implementation_reference_missing
- Actionable claim lines: 9
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/OPEN_SOURCE_ADVANCEMENT_PROGRAM.md

- Status: implementation_reference_missing
- Actionable claim lines: 4
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/PAGES_COPY_PASTE.md

- Status: implementation_reference_missing
- Actionable claim lines: 2
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/PASS_ALL_500_BENCHMARKS.md

- Status: test_reference_missing
- Actionable claim lines: 1
- Implementation paths: shared/model-benchmark-targets.ts, tools/check_buddy_model_benchmarks.mjs
- Test paths: None detected
- Missing paths: None detected
- Next action: Add focused tests and acceptance evidence for the referenced implementation.
- Execution verified: No; run-specific evidence is required.

### docs/PRODUCTION_GREENKEEPER.md

- Status: implementation_reference_missing
- Actionable claim lines: 3
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/PRODUCTION_PUSH_GUIDE.md

- Status: implementation_reference_missing
- Actionable claim lines: 5
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/PRODUCTION_READINESS_MASTER_PLAN.md

- Status: implementation_reference_missing
- Actionable claim lines: 2
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/PRODUCT_ENGINEERING_STANDARD.md

- Status: implementation_reference_missing
- Actionable claim lines: 8
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/PR_INTEGRATION_LEDGER_2026-08-12.md

- Status: broken_path_references
- Actionable claim lines: 8
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: framework/global_ai_sources_flow.py
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### docs/PR_REBUILD_PROCESS.md

- Status: implementation_reference_missing
- Actionable claim lines: 2
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/PR_REVIEW_CODERABBIT_PARITY.md

- Status: implementation_reference_missing
- Actionable claim lines: 15
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/PR_REVIEW_DECISION_PROTOCOL.md

- Status: implementation_reference_missing
- Actionable claim lines: 8
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/PUBLIC_GITHUB_PAGES_MASTER_DASHBOARD.md

- Status: implementation_reference_missing
- Actionable claim lines: 14
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/READINESS_GATE_PLAN.md

- Status: implementation_reference_missing
- Actionable claim lines: 2
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/REASONING_EFFICIENCY_AND_AI_COURSE_SYSTEM.md

- Status: implementation_reference_missing
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/REPOSITORY_CAPABILITY_INTEGRATION_MATRIX.md

- Status: implementation_reference_missing
- Actionable claim lines: 5
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/REPOSITORY_GOVERNANCE.md

- Status: implementation_reference_missing
- Actionable claim lines: 10
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/REPOSITORY_HEALTH_REPAIR_RUNBOOK.md

- Status: implementation_reference_missing
- Actionable claim lines: 3
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/REPOSITORY_IMPROVEMENT_SUGGESTIONS.md

- Status: test_reference_missing
- Actionable claim lines: 10
- Implementation paths: tools/ensure_bots_production_ready.py
- Test paths: None detected
- Missing paths: None detected
- Next action: Add focused tests and acceptance evidence for the referenced implementation.
- Execution verified: No; run-specific evidence is required.

### docs/REPOSITORY_OWNER_GUIDE.md

- Status: implementation_reference_missing
- Actionable claim lines: 10
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/STARTUP_FACTORY.md

- Status: implementation_reference_missing
- Actionable claim lines: 9
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/SUPERBOT_AGENT_ECONOMY.md

- Status: implementation_reference_missing
- Actionable claim lines: 4
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/SUPERBOT_COGNITIVE_MATURITY_MODEL.md

- Status: implementation_reference_missing
- Actionable claim lines: 2
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/SUPERBOT_META_ORCHESTRATOR.md

- Status: implementation_reference_missing
- Actionable claim lines: 4
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/SUPERBOT_MIGRATION_CHECKLIST.md

- Status: implementation_reference_missing
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/SUPERBOT_MIGRATION_PLAN.md

- Status: implementation_reference_missing
- Actionable claim lines: 4
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/SUPERBOT_REBUILD_BLUEPRINT.md

- Status: implementation_reference_missing
- Actionable claim lines: 3
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/SUPERBOT_SELF_DISCOVERY_SYSTEM.md

- Status: implementation_reference_missing
- Actionable claim lines: 5
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/SUPERBOT_SIMULATION_LAB.md

- Status: implementation_reference_missing
- Actionable claim lines: 3
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/SUPERBOT_WORLD_MODEL.md

- Status: implementation_reference_missing
- Actionable claim lines: 4
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/UNIFIED_500_MODEL_BENCHMARK_OPERATING_PLAN.md

- Status: broken_path_references
- Actionable claim lines: 5
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: github/workflows/dreamco-unified-system.yml
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### docs/UNIVERSAL_BOT_RUNTIME_CONTRACT.md

- Status: broken_path_references
- Actionable claim lines: 8
- Implementation paths: buddy_os/governance/approval_policy.yaml, buddy_os/governance/release_readiness.yaml, server/seed-bots.ts, tools/fleet_runtime_audit.py, tools/generate_bot_manifests.py, website/data/fleet-runtime-status.json
- Test paths: tests/test_fleet_runtime_executor.py
- Missing paths: /config/bots/bot-manifests.generated.json, /config/bots/bot-runtime-contract.schema.json, App_bots/<Division>.json, evidence/fleet-runtime/<slug>.json
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### docs/UNIVERSAL_CAPABILITY_ARCHITECTURE.md

- Status: implementation_reference_missing
- Actionable claim lines: 3
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/UNMERGEABLE_PR_RECONCILIATION_2026-08-12.md

- Status: broken_path_references
- Actionable claim lines: 4
- Implementation paths: client/src/lib/runtimeBackend.ts
- Test paths: None detected
- Missing paths: framework/global_ai_sources_flow.py
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### docs/US_OPEN_MODEL_FOUNDRY.md

- Status: implementation_reference_missing
- Actionable claim lines: 5
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/US_WEIGHT_SYSTEM.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/VIBE_CODING_CATEGORY_MAP.md

- Status: implementation_reference_missing
- Actionable claim lines: 12
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/VOICE_CLONING_PLAN.md

- Status: test_reference_missing
- Actionable claim lines: 2
- Implementation paths: buddy/media/voice.py
- Test paths: None detected
- Missing paths: None detected
- Next action: Add focused tests and acceptance evidence for the referenced implementation.
- Execution verified: No; run-specific evidence is required.

### docs/adr/0001-superbot-operating-model.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/architecture/DREAMCO_DIVISION_RESOURCE_READINESS.md

- Status: test_reference_missing
- Actionable claim lines: 5
- Implementation paths: buddy/resources/division_resource_router.py
- Test paths: None detected
- Missing paths: None detected
- Next action: Add focused tests and acceptance evidence for the referenced implementation.
- Execution verified: No; run-specific evidence is required.

### docs/architecture/DREAMCO_FIRST_PARTY_MODEL_FACTORY_AND_BUDDY_BOOTCAMP.md

- Status: implementation_reference_missing
- Actionable claim lines: 17
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/architecture/DREAMCO_HUGGINGFACE_DIVISION_TAXONOMY.md

- Status: implementation_reference_missing
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/architecture/PROPRIETARY_DIVISION_MODEL_PROGRAM.md

- Status: implementation_reference_missing
- Actionable claim lines: 19
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/benchmark-candidate-selection.md

- Status: implementation_reference_missing
- Actionable claim lines: 3
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/benchmark-command-center-contract.md

- Status: implementation_reference_missing
- Actionable claim lines: 3
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/benchmark-dataset-factory.md

- Status: implementation_reference_missing
- Actionable claim lines: 2
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/benchmark-evolution-loop.md

- Status: implementation_reference_missing
- Actionable claim lines: 3
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/benchmark-orchestrator.md

- Status: implementation_reference_missing
- Actionable claim lines: 4
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/benchmarks/BENCHMARKS_801_1000.md

- Status: implementation_reference_missing
- Actionable claim lines: 2
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/benchmarks/BUDDY_UNIVERSAL_1000.md

- Status: implementation_reference_missing
- Actionable claim lines: 8
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/buddy-asset-composition.md

- Status: implementation_reference_missing
- Actionable claim lines: 2
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/buddy-decision-engine.md

- Status: implementation_reference_missing
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/buddy-mathematical-intelligence.md

- Status: implementation_reference_missing
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/buddy-multimodal-trainer/GATES.md

- Status: test_reference_missing
- Actionable claim lines: 3
- Implementation paths: buddy/media/consent.py
- Test paths: None detected
- Missing paths: None detected
- Next action: Add focused tests and acceptance evidence for the referenced implementation.
- Execution verified: No; run-specific evidence is required.

### docs/buddy-multimodal-trainer/NEXT_STEPS.md

- Status: implementation_and_test_paths_referenced_not_verified
- Actionable claim lines: 0
- Implementation paths: buddy/media/sellability_gate.py
- Test paths: tests/test_sellability_gate.py
- Missing paths: None detected
- Next action: Run the linked tests and attach CI, benchmark, regression, and runtime evidence before promotion.
- Execution verified: No; run-specific evidence is required.

### docs/buddy-multimodal-trainer/SCOPE_MAP.md

- Status: implementation_reference_missing
- Actionable claim lines: 2
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/buddy-vibe-coding-game-engine.md

- Status: implementation_reference_missing
- Actionable claim lines: 3
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/buddy-vibe-game-engine.md

- Status: implementation_reference_missing
- Actionable claim lines: 3
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/capabilities/BATCH_13_2401_2600.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/capabilities/BATCH_14_2601_2800.md

- Status: implementation_reference_missing
- Actionable claim lines: 8
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/capabilities/BATCH_15_2801_3000.md

- Status: implementation_reference_missing
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/capability-package-marketplace.md

- Status: implementation_reference_missing
- Actionable claim lines: 4
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/digital-asset-strategy.md

- Status: implementation_reference_missing
- Actionable claim lines: 2
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/dreamco-lite/DREAMCO_LITE_MVP.md

- Status: implementation_reference_missing
- Actionable claim lines: 8
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/dreamco-lite/PROOF_MODE.md

- Status: implementation_reference_missing
- Actionable claim lines: 5
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/dreamco-lite/UPGRADE_LADDER.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/dreampayments_benchmark.md

- Status: implementation_reference_missing
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/engineering/DREAMCO_PROJECT_CHAT_CORPUS.md

- Status: implementation_reference_missing
- Actionable claim lines: 13
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/engineering/PR_RECONCILIATION_LEDGER.md

- Status: broken_path_references
- Actionable claim lines: 16
- Implementation paths: None detected
- Test paths: tests/test_buddy_resource_registry.py
- Missing paths: buddy/bootcamp/training_methods_hub.py, github/workflows/buddy-training-methods-hub.yml, github/workflows/command-center-index.yml, github/workflows/keep-green.yml, tests/test_buddy_training_methods_hub.py
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### docs/hf/HF_PIN_MATRIX.md

- Status: implementation_reference_missing
- Actionable claim lines: 2
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/index.md

- Status: implementation_reference_missing
- Actionable claim lines: 2
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/k12/K12_CURRICULUM_MAP_README.md

- Status: implementation_reference_missing
- Actionable claim lines: 2
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/local-command-center.md

- Status: implementation_reference_missing
- Actionable claim lines: 2
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/media-to-game-mastery.md

- Status: implementation_reference_missing
- Actionable claim lines: 4
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/multimodal-learning-fabric.md

- Status: implementation_reference_missing
- Actionable claim lines: 4
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/nvidia-video-mastery-bot.md

- Status: implementation_reference_missing
- Actionable claim lines: 2
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/plans/plan-study-skills-os.md

- Status: broken_path_references
- Actionable claim lines: 0
- Implementation paths: buddy/learning/learning_strategies_catalog.json, buddy/learning/study_methods.py
- Test paths: tests/test_buddy_srs_sm2.py
- Missing paths: tests/test_sm2.py
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### docs/product/DREAMCO_DATASET_STUDIO_AND_MARKETPLACE.md

- Status: implementation_reference_missing
- Actionable claim lines: 12
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/product/DREAMCO_MODEL_STUDIO_AND_MARKETPLACE.md

- Status: test_reference_missing
- Actionable claim lines: 20
- Implementation paths: buddy_os/actions/model_marketplace_contract.yaml
- Test paths: None detected
- Missing paths: None detected
- Next action: Add focused tests and acceptance evidence for the referenced implementation.
- Execution verified: No; run-specific evidence is required.

### docs/public_development/BUDDY_PUBLIC_DEVELOPMENT.md

- Status: implementation_reference_missing
- Actionable claim lines: 13
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/real_estate/BUDDY_REAL_ESTATE_DEVELOPMENT.md

- Status: implementation_reference_missing
- Actionable claim lines: 13
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/reality-simulation-engine.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/repository-scan-update-pr.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/repository-scan-update-standard-v2.md

- Status: implementation_reference_missing
- Actionable claim lines: 2
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/repository-scan-update-standard.md

- Status: implementation_reference_missing
- Actionable claim lines: 4
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/subject-ai-productivity-mastery.md

- Status: implementation_reference_missing
- Actionable claim lines: 3
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/system/PLUGIN_REGISTRY.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/system/SHARED_SYSTEM_PROMPT.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/top-200-ideas-set-02.md

- Status: implementation_reference_missing
- Actionable claim lines: 2
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/training-methodology/BUDDY_BOOTCAMP_1000_SITE_CURRICULUM.md

- Status: implementation_reference_missing
- Actionable claim lines: 4
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/training-methodology/DACL_CUSTOMER_OFFER.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/training-methodology/DACL_EVALUATION_PROTOCOL.md

- Status: implementation_reference_missing
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/training-methodology/DREAMCO_ADAPTIVE_LEARNING.md

- Status: implementation_reference_missing
- Actionable claim lines: 3
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/training-methodology/DREAMCO_KNOWLEDGE_REWRITE_STANDARD.md

- Status: implementation_reference_missing
- Actionable claim lines: 5
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/universal-benchmark-and-sandbox-blueprint.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/universal-benchmark-scanner.md

- Status: implementation_reference_missing
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/universal-education-engine.md

- Status: implementation_reference_missing
- Actionable claim lines: 2
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/video-benchmark-mastery.md

- Status: implementation_reference_missing
- Actionable claim lines: 2
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/video-intelligence.md

- Status: implementation_reference_missing
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/video-knowledge-quality-gates.md

- Status: implementation_reference_missing
- Actionable claim lines: 2
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/video-learning-worker-architecture.md

- Status: implementation_reference_missing
- Actionable claim lines: 2
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/world-model-benchmark-teachers.md

- Status: implementation_reference_missing
- Actionable claim lines: 2
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### docs/world-model-candidate-discovery.md

- Status: implementation_reference_missing
- Actionable claim lines: 2
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### eval/edu_benchmark/ALIGNMENT_NOTES.md

- Status: broken_path_references
- Actionable claim lines: 8
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: frontier/F0.packet.json
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### eval/edu_benchmark/README.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### eval/edu_benchmark/SET7_COURSE_MASTERY_FLOORS_AND_HOLDOUT_POLICY.md

- Status: implementation_reference_missing
- Actionable claim lines: 9
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### eval/edu_mastery_scorecards/docs/EVIDENCE_CARD_SPEC.md

- Status: broken_path_references
- Actionable claim lines: 3
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: gate/cert_gate.py, schema/course_evidence_card.schema.json
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### evidence/frontier/f0/README.md

- Status: broken_path_references
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: packets/f0-*.json
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### evidence/ledger/README.md

- Status: implementation_reference_missing
- Actionable claim lines: 8
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### evidence/plan-business-productivity-programs/manufacturing-productivity/EVIDENCE.md

- Status: implementation_and_test_paths_referenced_not_verified
- Actionable claim lines: 7
- Implementation paths: tools/build_manufacturing_productivity_benchmarks.py
- Test paths: tests/test_autonomous_business_and_deployment.py, tests/test_business_manufacturing_productivity_program.py
- Missing paths: None detected
- Next action: Run the linked tests and attach CI, benchmark, regression, and runtime evidence before promotion.
- Execution verified: No; run-specific evidence is required.

### framework/buddy-platform/README.md

- Status: implementation_reference_missing
- Actionable claim lines: 3
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### framework/game-engine/README.md

- Status: implementation_reference_missing
- Actionable claim lines: 3
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### governance/dreamco-chat-sources/README.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### huggingface/dreamco-router/README.md

- Status: broken_path_references
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: github/workflows/sync-to-huggingface.yml
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### integration/three-month-merge-audit-20261106.md

- Status: implementation_reference_missing
- Actionable claim lines: 5
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### money/BUDDY_HUSTLE_ENGINE.md

- Status: implementation_reference_missing
- Actionable claim lines: 3
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### money_os/README.md

- Status: broken_path_references
- Actionable claim lines: 2
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: automation/workflows.json, config/bot_registry.json, data/opportunity_sources.json
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### money_os/docs/bot-definition-of-done.md

- Status: implementation_reference_missing
- Actionable claim lines: 2
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### money_os/docs/conversation-requirements.md

- Status: implementation_reference_missing
- Actionable claim lines: 4
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### money_os/docs/launch.md

- Status: implementation_reference_missing
- Actionable claim lines: 2
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### money_os/docs/repository-audit-and-revenue-expansion.md

- Status: implementation_reference_missing
- Actionable claim lines: 3
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### money_os/frontend/README.md

- Status: implementation_reference_missing
- Actionable claim lines: 2
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### original-bots/README.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### original-bots/autonomous-income-network/category-1-digital-saas.md

- Status: implementation_reference_missing
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### original-bots/autonomous-income-network/category-2-finance-trading.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### original-bots/autonomous-income-network/category-3-ecommerce-retail.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### original-bots/autonomous-income-network/category-4-media-content.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### original-bots/autonomous-income-network/category-5-ai-robotics.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### original-bots/autonomous-income-network/category-6-franchising-licensing.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### original-bots/autonomous-income-network/category-7-ecommerce-automation.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### original-bots/autonomous-income-network/category-8-services-global.md

- Status: implementation_reference_missing
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### original-bots/systems/ai-leaps-robot-bot.md

- Status: implementation_reference_missing
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### original-bots/systems/api-automation-bot.md

- Status: implementation_reference_missing
- Actionable claim lines: 3
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### original-bots/systems/consulting-agency-bot.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### original-bots/systems/contracts-legal-bot.md

- Status: implementation_reference_missing
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### original-bots/systems/crypto-mining-bot.md

- Status: implementation_reference_missing
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### original-bots/systems/drop-shipping-bot.md

- Status: implementation_reference_missing
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### original-bots/systems/import-export-bot.md

- Status: implementation_reference_missing
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### original-bots/systems/master-bot-system.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### original-bots/systems/penny-stock-trading-bot.md

- Status: implementation_reference_missing
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### original-bots/systems/saas-automation-bot.md

- Status: implementation_reference_missing
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### original-bots/systems/schools-coaching-bot.md

- Status: implementation_reference_missing
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### original-bots/systems/youtube-streaming-bot.md

- Status: implementation_reference_missing
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### plans/OER_LICENSE_GATE_v1.md

- Status: implementation_reference_missing
- Actionable claim lines: 5
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### plans/plan-media-game-mastery.md

- Status: broken_path_references
- Actionable claim lines: 8
- Implementation paths: buddy/frontier/plan_status.py, buddy/media/consent.py, buddy/media/core.py, buddy/media/provenance.py, dreamco_platform/games/harness.py, tools/buddy_source_selector.py, tools/dreamco_file_converter.py, tools/video_evidence_validator.py, tools/video_package_compiler.py, tools/video_scan_fast.py, tools/video_scan_manifest.py, website/data/plan-status.json
- Test paths: tests/test_buddy_game_lab.py
- Missing paths: config/buddy_video_*.json, schemas/source_provenance_record.schema.json, tools/validate_source_provenance.py
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### reports/ACTIONS_LIVE_HEALTH.md

- Status: broken_path_references
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: github/workflows/all-bot-sandbox-campaign.yml, github/workflows/auto-merge-intake.yml, github/workflows/benchmark-mastery-distillation.yml, github/workflows/buddy-bootcamp-resource-categories.yml, github/workflows/buddy-custom-training-rewards.yml, github/workflows/buddy-daily-capability-gap-lab.yml, github/workflows/buddy-evidence-acquisition-tests.yml, github/workflows/buddy-failure-learning.yml, github/workflows/buddy-inhouse-capability-certification.yml, github/workflows/buddy-learning-runtime-integration.yml, github/workflows/buddy-navigation-bootcamp.yml, github/workflows/buddy-preventive-site-audit.yml, github/workflows/buddy-production-evidence-preflight.yml, github/workflows/buddy-provider-learning-libraries.yml, github/workflows/buddy-recovery-systems.yml, github/workflows/buddy-safe-repair.yml, github/workflows/buddy-self-build.yml, github/workflows/buddy-task-store-tests.yml, github/workflows/buddy-teacher-coverage-audit.yml, github/workflows/buddy-training-methods-hub.yml, github/workflows/buddy-training-taxonomy.yml, github/workflows/ci-automation.yml, github/workflows/ci.yml, github/workflows/codex-scan-only.yml, github/workflows/compatibility-repair-apply.yml, github/workflows/consolidated-evidence.yml, github/workflows/dependency-security-repair.yml, github/workflows/dreamco-build.yml, github/workflows/dreamco-five-minute-status-monitor.yml
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### reports/AI_ORGANIZATION_INTELLIGENCE.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### reports/AUTONOMOUS_WORKLIST.md

- Status: implementation_reference_missing
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### reports/BOT_ACCOUNTING_PLACEMENT_AUDIT.md

- Status: implementation_reference_missing
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### reports/BOT_CALCULATORS.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### reports/BOT_DIVISION_PLACEMENT_AUDIT.md

- Status: implementation_reference_missing
- Actionable claim lines: 4
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### reports/BOT_FLEET_E2E.md

- Status: test_reference_missing
- Actionable claim lines: 1
- Implementation paths: website/data/bot-fleet-e2e.json
- Test paths: None detected
- Missing paths: None detected
- Next action: Add focused tests and acceptance evidence for the referenced implementation.
- Execution verified: No; run-specific evidence is required.

### reports/BOT_FLEET_PROSPECTUS.md

- Status: implementation_reference_missing
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### reports/BOT_PRODUCTION_READINESS.md

- Status: implementation_reference_missing
- Actionable claim lines: 2
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### reports/BRANCH_PLAN_READINESS.md

- Status: broken_path_references
- Actionable claim lines: 10
- Implementation paths: tools/branch_health_daily.py, website/buddy.html, website/connections.html, website/desks.css, website/index.html, website/nav.js, website/wiring.html
- Test paths: None detected
- Missing paths: github/workflows/pages.yml
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### reports/BUDDY_BENCHMARK_INDEX.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### reports/BUDDY_DISTRIBUTION_CATALOG.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### reports/BUDDY_FLEET_QUALITY_PROGRAM.md

- Status: implementation_reference_missing
- Actionable claim lines: 3
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### reports/BUDDY_LOCAL_OWNER_AND_MODEL_LAB.md

- Status: implementation_reference_missing
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### reports/BUDDY_MULTIMODAL_STUDIO.md

- Status: implementation_reference_missing
- Actionable claim lines: 3
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### reports/BUDDY_OS_SHELL.md

- Status: test_reference_missing
- Actionable claim lines: 0
- Implementation paths: website/os-observability.js
- Test paths: None detected
- Missing paths: None detected
- Next action: Add focused tests and acceptance evidence for the referenced implementation.
- Execution verified: No; run-specific evidence is required.

### reports/BUDDY_PLATFORM_EXPANSION.md

- Status: implementation_reference_missing
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### reports/BUDDY_RESOURCE_LIST.md

- Status: implementation_reference_missing
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### reports/BUDDY_SUCCESS_PROGRAM.md

- Status: implementation_reference_missing
- Actionable claim lines: 2
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### reports/BUDDY_USER_TESTING_CATALOG.md

- Status: implementation_reference_missing
- Actionable claim lines: 13
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### reports/BUDDY_WEBSITE_BUILD_SYNC.md

- Status: test_reference_missing
- Actionable claim lines: 2
- Implementation paths: website/buddy-site-sync.js, website/data/buddy-site-status.json
- Test paths: None detected
- Missing paths: None detected
- Next action: Add focused tests and acceptance evidence for the referenced implementation.
- Execution verified: No; run-specific evidence is required.

### reports/BUILD_LIST.md

- Status: implementation_reference_missing
- Actionable claim lines: 2
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### reports/BUILD_PLAN.md

- Status: implementation_reference_missing
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### reports/CAPABILITY_WORKBENCH_VALIDATION.md

- Status: test_reference_missing
- Actionable claim lines: 5
- Implementation paths: website/capability-workbench.html
- Test paths: None detected
- Missing paths: None detected
- Next action: Add focused tests and acceptance evidence for the referenced implementation.
- Execution verified: No; run-specific evidence is required.

### reports/CERTIFY_FIRST_ORDER.md

- Status: broken_path_references
- Actionable claim lines: 10
- Implementation paths: buddy/bootcamp/buddy_bootcamp.yaml, buddy/learning/bootcamp.py, buddy_os/actions/paid_model_access_and_resource_import.yaml, tools/audit_repository_connections.py, tools/build_hf_capability_packs.py, tools/build_universal_work_ai_catalog.py, tools/connect_repository_pages.py, tools/score_data_package_candidate.py
- Test paths: None detected
- Missing paths: /home/box/roadmap/_crons.json, /home/box/roadmap/coverage_snapshot.json, benchmarks/america_gov/{sandbox.py,test_sandbox.py,catalog.json, benchmarks/resource_mastery/{sandbox.py,test_sandbox.py, config/generated/repository-system-connections.json, github/workflows/buddy-sandbox-bootcamp.yml, github/workflows/engineering-gap-closure.yml, github/workflows/grok-twins-hf-study.yml, github/workflows/pages.yml, github/workflows/repository-scan-update.yml, github/workflows/self-working-system.yml, study_packs/hub/{DAY1_NOTES.md,day1_audit.py,evidence/day1-inventory.json,evidence/drills.json, tools/check_bot_framework.py
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### reports/CHAT_VS_REPO_TRUTH.md

- Status: test_reference_missing
- Actionable claim lines: 2
- Implementation paths: buddy/memory/places.json, website/chat-data.js
- Test paths: None detected
- Missing paths: None detected
- Next action: Add focused tests and acceptance evidence for the referenced implementation.
- Execution verified: No; run-specific evidence is required.

### reports/DAILY_APPROVAL_LIST.md

- Status: implementation_reference_missing
- Actionable claim lines: 4
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### reports/DAILY_BOT_STUDY_SCAN.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### reports/DAILY_LEARNING.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### reports/DAILY_PRODUCTION_SCAN.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### reports/DATA_PACKAGE_LICENSE_QA_REVIEW.md

- Status: implementation_and_test_paths_referenced_not_verified
- Actionable claim lines: 27
- Implementation paths: server/routes.ts, tools/build_dp_onet_occ_syn_sample.py, tools/minimal_json_schema.py, tools/score_data_package_dataset.py
- Test paths: tests/test_license_provenance_gate.py, tests/test_score_data_package_dataset.py
- Missing paths: None detected
- Next action: Run the linked tests and attach CI, benchmark, regression, and runtime evidence before promotion.
- Execution verified: No; run-specific evidence is required.

### reports/DATA_PACKAGE_PRODUCT_PLAN.md

- Status: broken_path_references
- Actionable claim lines: 17
- Implementation paths: buddy/learning/multi_perspective_policy.json, buddy/learning/open_code_perspective.py, buddy/learning/study_data_schema.json, server/data-rights-policy.ts, server/routes.ts, tools/build_maximum_sandbox_matrix.py, tools/build_ontology_snapshot.py, tools/build_universal_capability_benchmark.py, tools/build_universal_work_ai_catalog.py, tools/score_data_package_candidate.py
- Test paths: None detected
- Missing paths: config/generated/universal-work-ai-catalog.json, tools/build_hf_*_packages.py
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### reports/DATA_PACKAGE_WEEK1_EVIDENCE.md

- Status: broken_path_references
- Actionable claim lines: 7
- Implementation paths: buddy/learning/multi_perspective_policy.json, tools/build_sellable_data_package.py, tools/license_provenance_gate.py, tools/minimal_json_schema.py, tools/score_data_package_candidate.py
- Test paths: tests/test_license_provenance_gate.py
- Missing paths: as_is/candidate.json, as_is/license_gate.json, buddy/learning/multi_view_synthesizer.py, buddy/learning/sellable_package_schema.json, config/generated/universal-work-ai-catalog.json, templates/license_gate.json
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### reports/DREAMCO_SEARCH_INDEX.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### reports/FLEET_MASSIVE_UPDATE_2026-10-03.md

- Status: broken_path_references
- Actionable claim lines: 41
- Implementation paths: website/fleet-status.html, website/nav.js, website/work-desk.html
- Test paths: None detected
- Missing paths: /website/fleet-status.html
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### reports/FLEET_RUNTIME_AUDIT.md

- Status: test_reference_missing
- Actionable claim lines: 4
- Implementation paths: buddy/fleet_runtime/divisions.py, buddy/fleet_runtime/fixtures.py, tools/fleet_runtime_audit.py, tools/generate_bot_manifests.py
- Test paths: None detected
- Missing paths: None detected
- Next action: Add focused tests and acceptance evidence for the referenced implementation.
- Execution verified: No; run-specific evidence is required.

### reports/FREE_ACTIONS.md

- Status: implementation_reference_missing
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### reports/GOALS_TO_PRODUCTION_GATES.md

- Status: broken_path_references
- Actionable claim lines: 4
- Implementation paths: None detected
- Test paths: tests/test_buddy_media.py
- Missing paths: buddy/media/{connectors,core,image,memory_guard,voice}.py
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### reports/GROK_CHAT_SESSION_SNAPSHOT.md

- Status: test_reference_missing
- Actionable claim lines: 1
- Implementation paths: buddy/learning/learning_strategies_catalog.json, buddy/learning/reasoning_and_learning_registry.py, buddy/learning/reasoning_techniques_catalog.json, tools/ensure_bots_production_ready.py
- Test paths: None detected
- Missing paths: None detected
- Next action: Add focused tests and acceptance evidence for the referenced implementation.
- Execution verified: No; run-specific evidence is required.

### reports/GROK_HELP_AND_SUGGESTIONS_INDEX.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### reports/HF_DAY1_EVIDENCE_PACKET.md

- Status: implementation_reference_missing
- Actionable claim lines: 5
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### reports/HF_REPEAT_RUNS_DAY1.md

- Status: implementation_reference_missing
- Actionable claim lines: 3
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### reports/HF_TOMORROW_SWARM_STATUS.md

- Status: broken_path_references
- Actionable claim lines: 6
- Implementation paths: tools/buddy_scan_hubs.py, tools/build_hf_capability_packs.py, tools/build_hf_download_packages.py
- Test paths: None detected
- Missing paths: /workspace/hf-license-audit/hub_license_audit.json, drills/drill_03_gated_probe.py, nlp-tasks-build/gen.py, study_packs/multimodal/evidence/run_<ts>.json, study_packs/nlp-tasks/*/sources.json, study_packs/nlp-tasks/classification/evidence/run_nlp-cls-sst2-20261013-r1.json, study_packs/transformers/evidence/run_<ts>.json, tools/download_hf_package.sh
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### reports/HUGGINGFACE_CAPABILITY_PACKS.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### reports/ISSUES_KERNEL_TRIAGE_2026-09-28.md

- Status: implementation_reference_missing
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### reports/MASSIVE_GOAL_LIST.md

- Status: implementation_reference_missing
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### reports/MASTER_ROADMAP_CROSSWALK.md

- Status: implementation_reference_missing
- Actionable claim lines: 4
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### reports/OS_OBSERVABILITY.md

- Status: test_reference_missing
- Actionable claim lines: 1
- Implementation paths: website/actions.html, website/data/os-observability-metrics.json, website/os-observability.js, website/os.html
- Test paths: None detected
- Missing paths: None detected
- Next action: Add focused tests and acceptance evidence for the referenced implementation.
- Execution verified: No; run-specific evidence is required.

### reports/P0_PLAN_GAP_QUEUE.md

- Status: broken_path_references
- Actionable claim lines: 9
- Implementation paths: server/index.ts, server/routes.ts, tools/build_customer_model_plan.py, tools/check_frontier_claim_trust_gates.py, tools/run_weight_balancer.py, website/actions.html
- Test paths: None detected
- Missing paths: config/generated/grok-owner-systems.json, evidence/api_scan_main_5ba09f2.json, github/workflows/grok-owner-systems.yml, server/**/*.ts
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### reports/PAGES_FEATURE_AUDIT.md

- Status: test_reference_missing
- Actionable claim lines: 0
- Implementation paths: tools/audit_pages_features.py
- Test paths: None detected
- Missing paths: None detected
- Next action: Add focused tests and acceptance evidence for the referenced implementation.
- Execution verified: No; run-specific evidence is required.

### reports/PLAN_SHELF.md

- Status: implementation_reference_missing
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### reports/PRODUCTION_CERT_GATE.md

- Status: broken_path_references
- Actionable claim lines: 6
- Implementation paths: tools/check_frontier_claim_trust_gates.py, tools/ensure_bots_production_ready.py, tools/run_24h_sandbox_soak.py
- Test paths: None detected
- Missing paths: config/generated/sandbox-24h-tick.json, github/workflows/buddy-24h-sandbox-soak.yml
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### reports/PRODUCTION_EVIDENCE_LEDGER.md

- Status: implementation_reference_missing
- Actionable claim lines: 5
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### reports/PRODUCTION_READINESS_OFFLOAD.md

- Status: broken_path_references
- Actionable claim lines: 5
- Implementation paths: tools/grok_run_owner_systems.py
- Test paths: None detected
- Missing paths: github/dependabot.yml, github/workflows/actions-failure-watch.yml
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### reports/PRODUCTION_READINESS_REPORT.md

- Status: test_reference_missing
- Actionable claim lines: 1
- Implementation paths: server/index.ts, server/observability.ts, server/openaiConfig.ts, server/stripeClient.ts, server/webhookHandlers.ts
- Test paths: None detected
- Missing paths: None detected
- Next action: Add focused tests and acceptance evidence for the referenced implementation.
- Execution verified: No; run-specific evidence is required.

### reports/PRODUCTION_SCAN.md

- Status: implementation_reference_missing
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### reports/PROD_CONNECTIVITY_SCAN.md

- Status: test_reference_missing
- Actionable claim lines: 0
- Implementation paths: website/actions.html
- Test paths: None detected
- Missing paths: None detected
- Next action: Add focused tests and acceptance evidence for the referenced implementation.
- Execution verified: No; run-specific evidence is required.

### reports/PROD_RESOURCE_CONNECTION_QUEUE.md

- Status: broken_path_references
- Actionable claim lines: 8
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: config/path-d-buddy-selector-allowlist.json, github/workflows/pages.yml, shared/os-event-bus-contract.ts, website/agents.html, website/bootcamp.html, website/buddy-os-bus.js, website/data-packages.html, website/frontier.html, website/issues.html, website/packages.html, website/pulls.html
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### reports/PROFESSIONAL_BOOTCAMP.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### reports/REPO_AUTONOMOUS_SYSTEMS_PLAN.md

- Status: test_reference_missing
- Actionable claim lines: 2
- Implementation paths: tools/audit_repository_connections.py, tools/build_hf_capability_packs.py, tools/build_universal_work_ai_catalog.py
- Test paths: None detected
- Missing paths: None detected
- Next action: Add focused tests and acceptance evidence for the referenced implementation.
- Execution verified: No; run-specific evidence is required.

### reports/UNMERGED_PR_VAULT.md

- Status: implementation_reference_missing
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### reports/branch-health-daily.md

- Status: implementation_reference_missing
- Actionable claim lines: 4
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### schemas/benchmarks/capability.schema.md

- Status: implementation_reference_missing
- Actionable claim lines: 4
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### scoring-criteria.md

- Status: implementation_reference_missing
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### settings/README.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### study_packs/DAY1_INVENTORY.md

- Status: broken_path_references
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: study_packs/*/sources.json
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### study_packs/README.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### study_packs/accelerate/CARD.md

- Status: broken_path_references
- Actionable claim lines: 2
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: scripts/smoke_offload.py
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### study_packs/accelerate/lessons/01_device_maps.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### study_packs/accelerate/lessons/02_offload.md

- Status: implementation_reference_missing
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### study_packs/accelerate/lessons/03_multi_gpu.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### study_packs/career_pathways/README.md

- Status: broken_path_references
- Actionable claim lines: 24
- Implementation paths: tools/license_provenance_gate.py
- Test paths: None detected
- Missing paths: authored/coverage_rules.json, authored/outline_topics.json, authored/release_changes.json, authored/target_overrides.json, data/dreamco_knowledge/evidence/regression/<asset_id>/<YYYYMMDD>-<NN>.json, data/majors_selected.json, data/practice_tasks.json, docs/data_dictionary.json, docs/make_data_dictionary.py, evidence/GENERATED_MANIFEST.json, evidence/holdout_kit/REVEALED_KEY.json, evidence/holdout_kit/VERIFIED_SHAS.json, evidence/scorer_input_cs_selfassessed.json, evidence_root>/<kind>/<asset_id>/<run>.json
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### study_packs/career_pathways/docs/DATA_DICTIONARY.md

- Status: broken_path_references
- Actionable claim lines: 50
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: data/dreamco_knowledge/evidence/holdout/<asset_id>/<run>.json, data/dreamco_knowledge/evidence/holdout/<asset_id>/<run>.results.json, data/dreamco_knowledge/evidence/regression/<asset_id>/<run>.json, data/dreamco_knowledge/evidence/regression/<asset_id>/<run>.results.json, data/majors_selected.json, data/practice_tasks.json, docs/data_dictionary.json, docs/make_data_dictionary.py, evidence/GENERATED_MANIFEST.json, evidence/holdout_kit/REVEALED_KEY.json, evidence/holdout_kit/VERIFIED_SHAS.json, evidence/holdout_kit/items.json, study_plans/<stem>/asset.json, study_plans/<stem>/candidate.json, study_plans/<stem>/license_gate.json, study_plans/<stem>/plan.json, study_plans/<stem>/provenance.json
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### study_packs/career_pathways/evidence/holdout_kit/README.md

- Status: broken_path_references
- Actionable claim lines: 20
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: data/practice_tasks.json
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### study_packs/career_pathways/evidence/holdout_kit/items.md

- Status: implementation_reference_missing
- Actionable claim lines: 21
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### study_packs/career_pathways/raw/SOURCES.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### study_packs/career_pathways/study_plans/03.0104_environmental_science.md

- Status: broken_path_references
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: data/practice_tasks.json, study_plans/03.0104_environmental_science/license_gate.json, study_plans/03.0104_environmental_science/provenance.json
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### study_packs/career_pathways/study_plans/09.0101_speech_communication_and_rhetoric.md

- Status: broken_path_references
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: data/practice_tasks.json, study_plans/09.0101_speech_communication_and_rhetoric/license_gate.json, study_plans/09.0101_speech_communication_and_rhetoric/provenance.json
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### study_packs/career_pathways/study_plans/11.0401_information_science_studies.md

- Status: broken_path_references
- Actionable claim lines: 17
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: data/practice_tasks.json, study_plans/11.0401_information_science_studies/license_gate.json, study_plans/11.0401_information_science_studies/provenance.json
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### study_packs/career_pathways/study_plans/11.0701_computer_science.md

- Status: broken_path_references
- Actionable claim lines: 22
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: data/practice_tasks.json, study_plans/11.0701_computer_science/license_gate.json, study_plans/11.0701_computer_science/provenance.json
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### study_packs/career_pathways/study_plans/13.1202_elementary_education_and_teaching.md

- Status: broken_path_references
- Actionable claim lines: 9
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: data/practice_tasks.json, study_plans/13.1202_elementary_education_and_teaching/license_gate.json, study_plans/13.1202_elementary_education_and_teaching/provenance.json
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### study_packs/career_pathways/study_plans/14.0801_civil_engineering_general.md

- Status: broken_path_references
- Actionable claim lines: 8
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: data/practice_tasks.json, study_plans/14.0801_civil_engineering_general/license_gate.json, study_plans/14.0801_civil_engineering_general/provenance.json
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### study_packs/career_pathways/study_plans/14.0901_computer_engineering_general.md

- Status: broken_path_references
- Actionable claim lines: 13
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: data/practice_tasks.json, study_plans/14.0901_computer_engineering_general/license_gate.json, study_plans/14.0901_computer_engineering_general/provenance.json
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### study_packs/career_pathways/study_plans/14.1001_electrical_and_electronics_engineering.md

- Status: broken_path_references
- Actionable claim lines: 11
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: data/practice_tasks.json, study_plans/14.1001_electrical_and_electronics_engineering/license_gate.json, study_plans/14.1001_electrical_and_electronics_engineering/provenance.json
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### study_packs/career_pathways/study_plans/14.1901_mechanical_engineering.md

- Status: broken_path_references
- Actionable claim lines: 17
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: data/practice_tasks.json, study_plans/14.1901_mechanical_engineering/license_gate.json, study_plans/14.1901_mechanical_engineering/provenance.json
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### study_packs/career_pathways/study_plans/23.0101_english_language_and_literature_general.md

- Status: broken_path_references
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: data/practice_tasks.json, study_plans/23.0101_english_language_and_literature_general/license_gate.json, study_plans/23.0101_english_language_and_literature_general/provenance.json
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### study_packs/career_pathways/study_plans/26.0101_biology_biological_sciences_general.md

- Status: broken_path_references
- Actionable claim lines: 5
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: data/practice_tasks.json, study_plans/26.0101_biology_biological_sciences_general/license_gate.json, study_plans/26.0101_biology_biological_sciences_general/provenance.json
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### study_packs/career_pathways/study_plans/27.0101_mathematics_general.md

- Status: broken_path_references
- Actionable claim lines: 10
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: data/practice_tasks.json, study_plans/27.0101_mathematics_general/license_gate.json, study_plans/27.0101_mathematics_general/provenance.json
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### study_packs/career_pathways/study_plans/27.0501_statistics_general.md

- Status: broken_path_references
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: data/practice_tasks.json, study_plans/27.0501_statistics_general/license_gate.json, study_plans/27.0501_statistics_general/provenance.json
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### study_packs/career_pathways/study_plans/40.0501_chemistry_general.md

- Status: broken_path_references
- Actionable claim lines: 9
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: data/practice_tasks.json, study_plans/40.0501_chemistry_general/license_gate.json, study_plans/40.0501_chemistry_general/provenance.json
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### study_packs/career_pathways/study_plans/40.0801_physics_general.md

- Status: broken_path_references
- Actionable claim lines: 8
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: data/practice_tasks.json, study_plans/40.0801_physics_general/license_gate.json, study_plans/40.0801_physics_general/provenance.json
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### study_packs/career_pathways/study_plans/42.0101_psychology_general.md

- Status: broken_path_references
- Actionable claim lines: 4
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: data/practice_tasks.json, study_plans/42.0101_psychology_general/license_gate.json, study_plans/42.0101_psychology_general/provenance.json
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### study_packs/career_pathways/study_plans/43.0104_criminal_justice_safety_studies.md

- Status: broken_path_references
- Actionable claim lines: 5
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: data/practice_tasks.json, study_plans/43.0104_criminal_justice_safety_studies/license_gate.json, study_plans/43.0104_criminal_justice_safety_studies/provenance.json
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### study_packs/career_pathways/study_plans/44.0701_social_work.md

- Status: broken_path_references
- Actionable claim lines: 9
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: data/practice_tasks.json, study_plans/44.0701_social_work/license_gate.json, study_plans/44.0701_social_work/provenance.json
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### study_packs/career_pathways/study_plans/45.0601_economics_general.md

- Status: broken_path_references
- Actionable claim lines: 8
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: data/practice_tasks.json, study_plans/45.0601_economics_general/license_gate.json, study_plans/45.0601_economics_general/provenance.json
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### study_packs/career_pathways/study_plans/45.1001_political_science_and_government_general.md

- Status: broken_path_references
- Actionable claim lines: 5
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: data/practice_tasks.json, study_plans/45.1001_political_science_and_government_general/license_gate.json, study_plans/45.1001_political_science_and_government_general/provenance.json
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### study_packs/career_pathways/study_plans/50.0409_graphic_design.md

- Status: broken_path_references
- Actionable claim lines: 11
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: data/practice_tasks.json, study_plans/50.0409_graphic_design/license_gate.json, study_plans/50.0409_graphic_design/provenance.json
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### study_packs/career_pathways/study_plans/51.2001_pharmacy.md

- Status: broken_path_references
- Actionable claim lines: 4
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: data/practice_tasks.json, study_plans/51.2001_pharmacy/license_gate.json, study_plans/51.2001_pharmacy/provenance.json
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### study_packs/career_pathways/study_plans/51.3801_registered_nursing_registered_nurse.md

- Status: broken_path_references
- Actionable claim lines: 10
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: data/practice_tasks.json, study_plans/51.3801_registered_nursing_registered_nurse/license_gate.json, study_plans/51.3801_registered_nursing_registered_nurse/provenance.json
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### study_packs/career_pathways/study_plans/52.0201_business_administration_and_management_general.md

- Status: broken_path_references
- Actionable claim lines: 8
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: data/practice_tasks.json, study_plans/52.0201_business_administration_and_management_general/license_gate.json, study_plans/52.0201_business_administration_and_management_general/provenance.json
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### study_packs/career_pathways/study_plans/52.0301_accounting.md

- Status: broken_path_references
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: data/practice_tasks.json, study_plans/52.0301_accounting/license_gate.json, study_plans/52.0301_accounting/provenance.json
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### study_packs/career_pathways/study_plans/52.0801_finance_general.md

- Status: broken_path_references
- Actionable claim lines: 5
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: data/practice_tasks.json, study_plans/52.0801_finance_general/license_gate.json, study_plans/52.0801_finance_general/provenance.json
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### study_packs/career_pathways/study_plans/52.1401_marketing_marketing_management_general.md

- Status: broken_path_references
- Actionable claim lines: 9
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: data/practice_tasks.json, study_plans/52.1401_marketing_marketing_management_general/license_gate.json, study_plans/52.1401_marketing_marketing_management_general/provenance.json
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### study_packs/datasets/CARD.md

- Status: test_reference_missing
- Actionable claim lines: 4
- Implementation paths: tools/build_hf_capability_packs.py
- Test paths: None detected
- Missing paths: None detected
- Next action: Add focused tests and acceptance evidence for the referenced implementation.
- Execution verified: No; run-specific evidence is required.

### study_packs/datasets/evidence/README.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### study_packs/datasets/lessons/01_load_dataset/README.md

- Status: implementation_reference_missing
- Actionable claim lines: 3
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### study_packs/datasets/lessons/02_map/README.md

- Status: implementation_reference_missing
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### study_packs/datasets/lessons/03_streaming/README.md

- Status: implementation_reference_missing
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### study_packs/evaluate/CARD.md

- Status: test_reference_missing
- Actionable claim lines: 1
- Implementation paths: buddy/bench/scorecard.py, buddy/learning/bootcamp.py, tools/build_hf_capability_packs.py
- Test paths: None detected
- Missing paths: None detected
- Next action: Add focused tests and acceptance evidence for the referenced implementation.
- Execution verified: No; run-specific evidence is required.

### study_packs/evaluate/evidence/2026-09-28_fallback_parity.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### study_packs/evaluate/evidence/README.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### study_packs/evaluate/lessons/01_metric_basics/README.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### study_packs/evaluate/lessons/02_buddy_bench_scoring/README.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### study_packs/hub/DAY1_DRILL_NOTES.md

- Status: broken_path_references
- Actionable claim lines: 3
- Implementation paths: tools/build_hf_capability_packs.py, tools/build_hf_download_packages.py
- Test paths: None detected
- Missing paths: evidence/drill_05_inventory_audit.json, snapshots/169d4a43…/config.json, study_packs/<pack>/sources.json, study_packs/hf_packages/<pack>/package.json
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### study_packs/hub/DAY1_NOTES.md

- Status: implementation_reference_missing
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### study_packs/hub/README.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### study_packs/hub/drills/DRILLS.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### study_packs/multimodal/README.md

- Status: broken_path_references
- Actionable claim lines: 1
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: evidence/latest.json, evidence/run_20260928T225217.json, recipes/av_trainer_handoff.yaml
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### study_packs/nlp-tasks/README.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### study_packs/nlp-tasks/classification/CARD.md

- Status: broken_path_references
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: /drill_runner.py
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### study_packs/nlp-tasks/ner/CARD.md

- Status: broken_path_references
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: /drill_runner.py
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### study_packs/nlp-tasks/qa/CARD.md

- Status: broken_path_references
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: /drill_runner.py
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### study_packs/nlp-tasks/summarization/CARD.md

- Status: broken_path_references
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: /drill_runner.py
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### study_packs/nlp-tasks/translation/CARD.md

- Status: broken_path_references
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: /drill_runner.py
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### study_packs/pack.code/CARD.md

- Status: broken_path_references
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: recipes/dpo.yaml, recipes/sft.yaml
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### study_packs/pack.embed/CARD.md

- Status: broken_path_references
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: recipes/dpo.yaml, recipes/sft.yaml
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### study_packs/pack.instruct/CARD.md

- Status: broken_path_references
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: recipes/dpo.yaml, recipes/sft.yaml
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### study_packs/pack.reason/CARD.md

- Status: broken_path_references
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: recipes/dpo.yaml, recipes/sft.yaml
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### study_packs/pack.rerank/CARD.md

- Status: broken_path_references
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: recipes/dpo.yaml, recipes/sft.yaml
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### study_packs/pack.research/CARD.md

- Status: broken_path_references
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: recipes/dpo.yaml, recipes/sft.yaml
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### study_packs/pack.safety/CARD.md

- Status: broken_path_references
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: recipes/dpo.yaml, recipes/sft.yaml
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### study_packs/pack.speech/CARD.md

- Status: broken_path_references
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: recipes/dpo.yaml, recipes/sft.yaml
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### study_packs/pack.summarize/CARD.md

- Status: broken_path_references
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: recipes/dpo.yaml, recipes/sft.yaml
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### study_packs/pack.tools/CARD.md

- Status: broken_path_references
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: recipes/dpo.yaml, recipes/sft.yaml
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### study_packs/pack.translate/CARD.md

- Status: broken_path_references
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: recipes/dpo.yaml, recipes/sft.yaml
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### study_packs/pack.vision/CARD.md

- Status: broken_path_references
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: recipes/dpo.yaml, recipes/sft.yaml
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### study_packs/transformers/CARD.md

- Status: broken_path_references
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: drills/run_drills.py
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### study_packs/transformers/drills/README.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### study_packs/trl/README.md

- Status: broken_path_references
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: recipes/dpo.yaml, recipes/grpo.yaml, recipes/sft.yaml, scripts/train_*.py
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### study_packs/trl/_sources/AGENTS.md

- Status: implementation_reference_missing
- Actionable claim lines: 7
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### study_packs/trl/_sources/bots_lib-huggingface.md

- Status: implementation_reference_missing
- Actionable claim lines: 6
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

### study_packs/trl/_sources/docs_HUGGINGFACE_MASTERY_PLAN.md

- Status: broken_path_references
- Actionable claim lines: 3
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: config/generated/hf-hub-literacy-checklist.json
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### study_packs/trl/eval_plan.md

- Status: broken_path_references
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: study_packs/trl/scorecards/<pack_id>/<date>.json
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### systems/README.md

- Status: broken_path_references
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: App_bots/*.json
- Next action: Repair or explicitly supersede the missing repository path references.
- Execution verified: No; run-specific evidence is required.

### tools/issue_cleaner/README.md

- Status: reference_only
- Actionable claim lines: 0
- Implementation paths: None detected
- Test paths: None detected
- Missing paths: None detected
- Next action: Find or build the implementation, or record why the requirement is intentionally documentation-only.
- Execution verified: No; run-specific evidence is required.

## Truth boundary

This report maps documentation references to repository paths. It does not prove that code implements the full requirement, that tests pass, or that a feature is production-ready.
