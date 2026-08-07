# DreamCo Rebuild V2

Branch: `buddy-rebuild-v2`

## Purpose

Rebuild DreamCo/Buddy as one canonical, testable, governed system. Every bot, division, provider, organization, benchmark, connector, workflow, UI claim, and revenue feature must resolve to executable code, tested adapter evidence, or an explicit planned/unverified state.

## Non-negotiable architecture rules

1. One canonical bot contract drives every bot surface.
2. One canonical division registry drives all 45 divisions.
3. One capability graph maps bots -> capabilities -> tools -> adapters -> benchmarks -> evidence.
4. No capability is marked active from marketing copy alone.
5. Every external action has scope, approval, budget, audit receipt, and stop controls.
6. Every provider/model claim carries source, verification date, exact version/model id when applicable, and evidence state.
7. `EXISTING 500`, `ALLIANCE`, and future lists are source sets, not entity types.
8. Entity types are separate: model developer, inference platform, AI app, agent platform, data infrastructure, developer platform, business SaaS, university, nonprofit, government/public institution, standards body, research lab, hardware/compute provider, and DreamCo-native capability.
9. All 1,051 bot profiles must pass the same validation contract.
10. No `god mode`, `infinite memory`, `all languages`, `any app`, `zero human intervention`, or similar claim is considered verified without bounded, reproducible evidence.

## Capability evidence states

- `declared` — profile/catalog claim only.
- `official_verified` — verified against official documentation.
- `adapter_verified` — a configured adapter has passed connection/contract tests.
- `sandbox_tested` — reproducible sandbox task completed.
- `live_tested` — authenticated live test completed under explicit run approval.
- `production_certified` — release gates passed with evidence.
- `deprecated` — capability or integration is no longer current.
- `blocked` — known policy/security/technical blocker.

## Canonical bot contract

Every bot should resolve to these fields:

- identity: slug, display name, division, category, tier, version
- mission
- user jobs
- declared capabilities
- certified capabilities
- tools
- adapters
- model requirements
- data categories
- permissions
- autonomy ceiling
- operational modes
- budget policy
- side-effect policy
- evidence requirements
- benchmark suites
- runtime binding
- memory policy
- dependencies
- failure modes
- recovery behavior
- security controls
- professional-review requirements
- revenue model
- target users
- pricing metadata
- status
- last verified at

## Rebuild order

### Phase 1 — Core truth layer

- Bot contract v2
- Division registry v2
- Capability graph
- Organization/entity taxonomy
- Evidence ledger
- Benchmark registry
- Connector registry
- Permission and approval contract
- Cost/budget contract
- Audit receipt contract

### Phase 2 — CommandCore

Rebuild all 13 CommandCore bots first because every other division depends on them. Replace unverifiable claims with bounded capabilities and connect each bot to runtime/tests.

### Phase 3 — 45 divisions / 1,051 bots

For each division: normalize every bot, deduplicate overlapping roles, preserve distinct user jobs, attach capabilities/adapters/tests, and generate division scorecards.

### Phase 4 — Runtime

Turn catalog-only capabilities into real bounded executors. Separate planner, router, tool executor, connector executor, benchmark runner, memory service, evidence service, policy service, and audit service.

### Phase 5 — UI

Every UI badge must come from evidence. Pages should distinguish declared, configured, sandbox-tested, live-tested, and production-certified states.

### Phase 6 — Benchmark/competition engine

Compare DreamCo against providers, applications, infrastructure companies, alliance members, open-source projects, and research institutions only on relevant dimensions.

## Organization benchmark taxonomy

### Source sets

- `existing_500`
- `alliance`
- `official_provider_catalog`
- `open_source_watch`
- `dreamco_native`
- future snapshots

### Entity types

- foundation_model_developer
- model_inference_platform
- ai_application
- agent_framework_platform
- data_ai_infrastructure
- developer_platform
- business_saas
- hardware_compute
- research_lab
- university
- nonprofit
- government_public
- standards_body
- open_source_project
- dreamco_native

### Benchmark dimensions

- task quality
- reasoning
- coding
- research
- tool use
- orchestration
- data analysis
- image
- video
- speech/audio/music
- multilingual
- education
- science
- health support
- finance support
- legal support
- sales/CRM
- operations
- defensive security
- infrastructure
- evaluation/governance
- latency
- reliability
- recovery
- price
- privacy
- local/offline availability
- API quality
- integration surface
- evidence quality
- accessibility
- user experience

## 20 user-need suites

1. Conversation, writing, planning, everyday support
2. Code generation, review, debugging, testing, deployment
3. Source discovery, synthesis, literature review, evidence tracking
4. Tool-using agents, orchestration, workflows, task completion
5. Data preparation, analysis, forecasting, visualization
6. Image generation, editing, design, visual understanding
7. Video generation, editing, animation, production planning
8. Speech, transcription, voice, music, audio production
9. Translation, localization, language access, regional models
10. Tutoring, curriculum, practice, assessment, learning tools
11. Scientific discovery, simulation, reproducibility, domain models
12. Health education, clinical preparation, research, operations
13. Financial analysis, budgeting, risk education, operations
14. Legal information, document preparation, research, review support
15. Research, content, qualification, coaching, campaigns
16. Support, service, CRM assistance, customer intelligence
17. Automation, administration, supply chains, productivity
18. Defensive testing, monitoring, governance, incident readiness
19. Compute, chips, serving, storage, networking, observability
20. Evaluation, red teaming, provenance, policy, responsible AI

## 100 benchmark and upgrade additions

1. Live provider capability verification
2. Exact model-id discovery
3. Provider version drift detection
4. API availability tracking
5. SDK availability tracking
6. Pricing freshness tracking
7. License freshness tracking
8. Terms-change tracking
9. Model retirement detection
10. New-model discovery
11. Coding correctness benchmark
12. Repository-understanding benchmark
13. Debugging benchmark
14. Test-generation benchmark
15. Refactor benchmark
16. Security-fix benchmark
17. Deployment benchmark
18. Long-context benchmark
19. Structured-output benchmark
20. Tool-use benchmark
21. Multi-agent orchestration benchmark
22. Recovery-from-tool-failure benchmark
23. Planning benchmark
24. Constraint-following benchmark
25. Approval-gate benchmark
26. Cost-control benchmark
27. Token-efficiency benchmark
28. Latency benchmark
29. Throughput benchmark
30. Reliability benchmark
31. Hallucination benchmark
32. Citation-validity benchmark
33. Source-quality benchmark
34. Evidence-completeness benchmark
35. Freshness benchmark
36. Research synthesis benchmark
37. RAG benchmark
38. Retrieval precision benchmark
39. Retrieval recall benchmark
40. Memory correctness benchmark
41. Memory privacy benchmark
42. Data-analysis benchmark
43. SQL benchmark
44. Spreadsheet benchmark
45. Forecasting benchmark
46. Visualization benchmark
47. Image-generation benchmark
48. Image-editing benchmark
49. Visual-understanding benchmark
50. OCR/document benchmark
51. Video-generation benchmark
52. Video-editing benchmark
53. Animation benchmark
54. Speech-to-text benchmark
55. Text-to-speech benchmark
56. Voice-quality benchmark
57. Music-generation benchmark
58. Audio-editing benchmark
59. Translation benchmark
60. Localization benchmark
61. Regional-language benchmark
62. Tutoring benchmark
63. Assessment benchmark
64. Scientific-reasoning benchmark
65. Reproducibility benchmark
66. Simulation benchmark
67. Health-information grounding benchmark
68. Clinical-workflow support benchmark
69. Financial-analysis benchmark
70. Budgeting benchmark
71. Payment-operations benchmark
72. Legal-research benchmark
73. Document-review benchmark
74. Professional-handoff benchmark
75. Sales-research benchmark
76. Lead-qualification benchmark
77. CRM-workflow benchmark
78. Customer-support benchmark
79. Automation benchmark
80. Administration benchmark
81. Supply-chain workflow benchmark
82. Defensive-security benchmark
83. Dependency-security benchmark
84. Provenance benchmark
85. SBOM benchmark
86. Red-team resistance benchmark
87. Policy-governance benchmark
88. Compute-performance benchmark
89. Serving-cost benchmark
90. Storage/retrieval benchmark
91. Observability benchmark
92. Accessibility benchmark
93. UX benchmark
94. Connector-quality benchmark
95. API-design benchmark
96. Local/offline benchmark
97. Privacy benchmark
98. DreamCo-vs-competitor user-job benchmark
99. Division scorecard benchmark
100. Bot production-certification benchmark

## Benchmark run safety contract

Each run records:

- selected entities
- selected user needs
- fixture count
- concurrency
- maximum spend
- network access approval
- paid-test approval
- provider credentials by opaque reference only
- exact model/version ids
- run start/end timestamps
- test artifacts
- raw metrics
- normalized metrics
- failures
- retries
- external actions taken
- spend used
- evidence receipts

A run must stop automatically at the budget cap, permission boundary, security failure, or owner stop signal.

## DreamCo benchmark principle

DreamCo should not win because DreamCo wrote the benchmark. Fixtures, scoring rules, weights, and evidence must be visible and reproducible. DreamCo receives the same penalties for missing adapters, unverified claims, failures, latency, cost, and poor user-job completion as every outside system.

## Immediate rebuild priorities

1. Normalize CommandCore.
2. Introduce capability evidence states in the bot registry.
3. Split organization `source_set` from `entity_type`.
4. Add benchmark dimensions above to the organization intelligence registry.
5. Connect every benchmark result to a signed evidence record.
6. Generate a gap report across all 1,051 bots.
7. Generate duplicate-capability and duplicate-role reports.
8. Replace unsupported capability text with declared/planned state.
9. Add runtime bindings for top revenue/user-value bots first.
10. Make production certification—not profile existence—the definition of an active capability.
