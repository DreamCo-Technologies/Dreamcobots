# DreamCo Master Plan

Last consolidated: 2026-08-08

## Purpose

This is the canonical human-readable plan for DreamCo. It organizes repository notes, plans, updates, reports, issue-style documents, and generated architecture into one execution order without deleting useful history.

## North Star

Buddy is the user-facing AI operating layer. Specialist bots, models, builders, benchmarks, libraries, data packages, creator systems, device integrations, and business systems work behind Buddy through shared canonical infrastructure.

The platform should optimize for verified user outcomes, user-owned data, clean code, easy upgrades, shared improvements, measurable benchmarks, and truthful capability status.

## Canonical execution order

### Phase 0 — Truth and repository hygiene
1. Inventory Markdown, text notes, pasted update files, generated reports, issue files, and architecture documents.
2. Classify each document as canonical, active plan, generated report, historical note, implementation guide, or archive candidate.
3. Do not delete history automatically.
4. Merge duplicated active plans into canonical documents and leave references from historical files.
5. Keep README focused on what the repository is and how to run it; keep roadmap/architecture detail here or in specialized docs.
6. Require implementation evidence before marking plans complete.

### Phase 1 — Make Buddy work reliably
1. Verify Buddy routing, chat, local bridge, core APIs, mobile/PWA, permissions, recovery, and observability.
2. Fix release-blocking bugs and failing required tests.
3. Remove or consolidate duplicate runtime owners.
4. Ensure clean upgrade, backup, migration, rollback, and restore paths.
5. Keep external writes behind authenticated adapters and approval rules.

### Phase 2 — Shared fleet architecture
1. Every canonical bot inherits verified shared improvements.
2. Shared routing, memory, testing, security, audio/media analysis, observability, builder strategy, performance, and data infrastructure are upgraded once and reused.
3. Bot-specific forks are last resort; prefer configuration, policy, plugins, adapters, or domain extensions.
4. Shared changes trigger impact-based parallel retesting.

### Phase 3 — Benchmarks and competition
1. Every bot/capability gets measurable benchmarks.
2. Discover up to the top 30 legitimate current competitors/substitutes per capability where the market supports it.
3. Compare open-source and vibe-coding alternatives with identical fixtures.
4. Convert measured gaps into parallel builder lanes.
5. Reward verified gap closure, not code volume.
6. Promote winning reusable improvements into shared fleet infrastructure.

### Phase 4 — Coding mastery
1. Benchmark coding bots against major global technology job families.
2. Enforce clean-code, tests, security, zero known release-blocking bugs, easy upgrades, migrations, and rollback.
3. Build open-source library mastery through executable skill cards and exact-version knowledge.
4. Train low-level systems knowledge from binary and memory through C, C++, assembly, compilers, OS internals, embedded systems, performance, and secure native code.
5. Convert reusable coding knowledge into Universal Training Library packages.

### Phase 5 — Universal Training Library
1. Organize every package by category, subcategory, difficulty, job role, domain, platform, training use, version, license, and provenance.
2. Every package includes usage instructions, minimal/advanced examples, bot-training recipe, data-package recipe, evaluation, troubleshooting, performance guidance, upgrade, rollback, security, and licensing notes.
3. Support prompt/policy customization, retrieval skills, SFT, LoRA/QLoRA, preference optimization, continued pretraining, distillation, and advanced from-scratch research.
4. Prefer the least expensive verified training method that meets the goal.
5. Keep packages composable and portable rather than building one enormous dataset.

### Phase 6 — Data Discovery and package economy
1. Data Discovery Bot searches lawful public/open/licensed/user-authorized sources.
2. Score rights clarity, relevance, quality, provenance, freshness, coverage, usability, benchmark value, commercial potential, and updateability.
3. Separate private-use permission from redistribution/commercial permission.
4. Build data cards, provenance manifests, training recipes, evaluation packs, contamination checks, deduplication reports, and update recipes.
5. Books, movies, scripts, manuals, courses, and media can be included only when rights permit; otherwise use reference/curriculum manifests.
6. Sell only packages and derivatives DreamCo or the user has the rights to commercialize.

### Phase 7 — Models and model training
1. Maintain a shared international open-weight model study program.
2. Study Chinese and other international model families using public model cards, papers, licenses, repositories, and reproducible trials.
3. Record exact revisions, quantizations, hardware fit, latency, memory, cost, privacy, quality, strengths, weaknesses, and best-fit tasks.
4. Route by verified task fit rather than brand.
5. Let users train their own compatible bots/models through the Training Studio with baseline evaluation, checkpointing, post-training comparison, packaging, export, and rollback.

### Phase 8 — Creator and media businesses
1. Creator Platform Hub handles podcasts, streamers, content creators, and platform-specific make/post preparation.
2. Music Creator and Music Career Studio support songs, beats, albums, performance coaching, user-authorized media, original avatars, videos, release packs, and trend benchmarking.
3. Hollywood Career Studio coordinates acting, hosting, creator, music, modeling, writing, directing, producing, streaming, and filmmaking career workflows without promising fame.
4. Acting/personality systems remain transparent that Buddy is AI.
5. Media workflows enforce rights, consent, provenance, and publishing approvals.

### Phase 9 — User-owned data and Collection Vault
1. Keep user-selected data local-first where practical.
2. Collection Vault organizes files, photos, videos, audio, charts, notes, links, app exports, creator assets, business records, and Buddy outputs.
3. Add encrypted persistence, search, previews, duplicate detection, semantic indexing, backup/restore, migration, and optional user-selected sync.
4. Cross-app access is deny-by-default and permission-scoped.

### Phase 10 — Business graduation
1. Specialist bots progress from prototype to internal tool to DreamCo service to marketplace offering to independent SaaS/enterprise product when justified.
2. Graduation depends on verified user value, clean operations, benchmark strength, legal/rights fit, supportability, pricing evidence, and reliable deployment.
3. Reusable improvements return to shared infrastructure even when a specialist becomes a product.

## Definition of done for any major feature
A feature is complete only when its canonical implementation exists, required tests pass, benchmark target passes or a documented exception exists, guardrails still pass, permissions/privacy/rights/cost boundaries remain intact, documentation is updated, rollback/recovery exists where relevant, no unnecessary duplicate implementation was introduced, and evidence is linked.

## Documentation roles
- `README.md` — repository identity, quick start, current verified capabilities.
- `docs/MASTER_PLAN.md` — canonical execution plan and sequencing.
- `docs/NOTES_ORGANIZATION.md` — documentation taxonomy and consolidation rules.
- `reports/*.md` — generated or dated evidence/reports; never silently treated as current architecture.
- `config/*.json` — machine-readable canonical programs/contracts.
- `tools/*` — generators, validators, scanners, benchmarks, migration and verification tooling.
- `.agents/memory/MEMORY.md` — agent memory/context, not the canonical roadmap.
- `attached_assets/` and pasted text — source/history to review and consolidate, not active truth by default.

## Immediate priorities
1. Run the documentation inventory tool and review duplicate/obsolete Markdown groups.
2. Verify the current Buddy runtime end-to-end on phone and desktop.
3. Generate the shared-fleet adoption map and close duplicate-owner gaps.
4. Run consolidated guardrail validation and parallel benchmark-gap planning.
5. Measure actual benchmark gaps before launching builder repairs.
6. Wire Data Discovery, Universal Training Library, model-study, and low-level coding tracks into executable runtime/UI paths.
7. Keep the repository shippable while expanding capability: small reviewed changes, tests, migration safety, and evidence first.
