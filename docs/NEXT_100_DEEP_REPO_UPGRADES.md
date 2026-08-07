# DreamCo / Buddy — Second 100 Deep-Repository Upgrades

These upgrades intentionally avoid duplicating the first owner-level 100. They focus on consolidation, migration, runtime depth, observability, testing, economics, and product coherence revealed by the repository structure and current contracts.

## 1. Legacy consolidation and migration
1. Build an automated legacy-folder mapper that classifies every top-level bot/system folder as canonical, migrate, archive, or delete-candidate.
2. Create a migration registry for `Business_bots`, `Marketing_bots`, `Occupational_bots`, `Side_Hustle_bots`, `python_bots`, `java_bots`, and similar parallel bot trees.
3. Deduplicate bot identities across old JSON catalogs, seed files, generated registries, and specialized directories.
4. Add canonical slug redirects so old bot IDs continue resolving after migration.
5. Add duplicate-capability clustering to identify bots that should merge or specialize.
6. Add duplicate-user-job clustering to reduce near-identical bots.
7. Add legacy-file ownership metadata: canonical replacement, migration status, and last consumer.
8. Add an archive gate that proves no runtime imports reference a legacy module before removal.
9. Generate a repo-wide orphan-file report for files not imported, generated, tested, or served.
10. Generate a repo-wide dead-route report for server/API routes never called by clients or tests.

## 2. Bot fleet normalization depth
11. Convert every bot profile into `dreamco.bot_contract.v2` through a deterministic migration tool.
12. Add per-bot semantic versioning independent from the global app version.
13. Add capability aliases so differently worded capabilities map to one canonical capability ID.
14. Add standardized user-job IDs so benchmarks aggregate across divisions.
15. Add standardized industry and profession taxonomy for all bots.
16. Add a bot inheritance system for shared category defaults without duplicating JSON.
17. Add bot mixins for common capabilities such as research, sales, document work, scheduling, and analytics.
18. Add capability prerequisites so a bot cannot certify advanced abilities without foundational ones.
19. Add capability deprecation and replacement paths per bot.
20. Add machine-generated per-bot changelogs showing capability, adapter, benchmark, and policy changes.

## 3. Runtime execution depth
21. Introduce an explicit planner/executor split with typed handoff objects.
22. Add a tool-selection policy layer that scores tool fit, cost, latency, privacy, and evidence quality.
23. Add execution leases so two workers cannot perform the same side effect simultaneously.
24. Add distributed locks for shared resources such as deployments, payments, files, and external accounts.
25. Add idempotency storage for every external-write adapter.
26. Add compensation/rollback workflows for reversible multi-step transactions.
27. Add partial-success semantics so projects can finish useful work even when one dependency fails.
28. Add task checkpoint snapshots for long-running agent plans.
29. Add bounded recursive planning depth and cycle detection.
30. Add runtime circuit breakers for failing providers, tools, or connectors.

## 4. Agent quality and orchestration
31. Replace competitor-inspired agent descriptions with DreamCo-native behavioral specifications.
32. Add agent handoff benchmarks measuring context loss between specialists.
33. Add delegation-quality benchmarks measuring whether Buddy chooses the right specialist.
34. Add team-size optimization so Buddy does not spawn unnecessary agents.
35. Add adversarial-agent tests for conflicting recommendations within a team.
36. Add consensus-vs-expert-selection policies rather than always averaging agent opinions.
37. Add escalation policies for low-confidence agent outputs.
38. Add agent-role memory scopes so one specialist cannot automatically read unrelated project data.
39. Add per-agent token/time/cost budgets within a larger project budget.
40. Add orchestration replay so failed team runs can be inspected step-by-step.

## 5. Adapter and integration engineering
41. Define one adapter interface for auth, capabilities, health, read, write, rate limits, audit receipts, and revocation.
42. Add adapter contract tests that every provider must pass before registration.
43. Add rate-limit discovery and adaptive throttling per provider.
44. Add provider-specific retry classification rather than generic retry-on-error.
45. Add token/credential rotation health checks.
46. Add connection-expiration forecasting so users are warned before integrations break.
47. Add sandbox-vs-production credential separation for every write-capable connector.
48. Add adapter capability diffing when a provider changes its API.
49. Add fallback adapter chains for interchangeable services.
50. Add integration chaos tests that intentionally simulate timeout, 429, auth failure, malformed data, and provider outage.

## 6. Testing and verification quality
51. Split the giant governed test command into parallel suites with explicit ownership and failure summaries.
52. Add mutation testing to verify tests actually catch logic changes.
53. Add property-based testing for schemas, routing, queues, budgets, and permissions.
54. Add snapshot compatibility tests for generated registries.
55. Add cross-platform browser tests for every public Buddy page.
56. Add mobile viewport and low-memory browser test profiles.
57. Add accessibility automation for keyboard, screen reader semantics, contrast, and focus order.
58. Add API fuzz tests for all Zod-validated endpoints.
59. Add migration tests proving old stored data upgrades safely to new contracts.
60. Add release-candidate soak tests running realistic multi-hour task workloads.

## 7. Observability and reliability
61. Add one correlation ID spanning UI request, Buddy router, agents, adapters, queue tasks, and audit receipt.
62. Add distributed tracing around all model, connector, database, and worker calls.
63. Add per-bot SLOs for availability, latency, completion rate, and recovery time.
64. Add error-budget policies that automatically reduce autonomy for unstable capabilities.
65. Add provider health dashboards with latency, error, cost, and rate-limit trends.
66. Add queue health dashboards with wait time, throughput, retries, dead letters, and bottlenecks.
67. Add user-visible incident status for capabilities that are degraded or unavailable.
68. Add automatic regression detection against each bot's previous benchmark baseline.
69. Add anomaly detection for sudden spend, latency, error, or output-quality changes.
70. Add structured postmortem generation from failed production runs.

## 8. Cost and economic intelligence
71. Add per-task expected-cost estimation before execution.
72. Add actual-vs-estimated cost tracking by bot, model, connector, and workflow.
73. Add a cost-per-successful-user-job metric.
74. Add model-routing optimization using quality-per-dollar rather than raw model rank.
75. Add connector-cost optimization using free/local alternatives when quality remains acceptable.
76. Add enterprise cost-center and department allocation.
77. Add customer-level profitability analytics for DreamCo itself.
78. Add feature-level infrastructure cost attribution.
79. Add cost regression gates in CI for benchmark workloads.
80. Add workload simulations showing the cheapest safe architecture at 100, 1K, 10K, 100K, and 1M users.

## 9. Product coherence and UX
81. Build a single capability search that indexes bots, roles, actions, pages, connectors, and templates.
82. Add one universal command palette for navigating and launching any Buddy action.
83. Add contextual progress views for long-running projects instead of generic loading states.
84. Add a universal project object shared by coding, business, creator, sales, and research workspaces.
85. Add cross-workspace project history so users do not lose context when switching modes.
86. Add explain-this-button metadata to every significant UI control.
87. Add evidence badges beside capability claims directly in the UI.
88. Add explicit unavailable/configuration-required states instead of hiding unsupported actions.
89. Add a first-run capability discovery experience based on the user's actual goals.
90. Add saved workspace layouts for individuals, teams, and industries.

## 10. Enterprise and ecosystem scale
91. Add tenant-level policy inheritance with organization -> department -> team -> role -> user precedence.
92. Add policy simulation so admins can see what a rule change would block before publishing it.
93. Add delegated administration with scoped admin roles instead of one all-powerful admin.
94. Add enterprise audit export formats for common SIEM/data-lake pipelines.
95. Add organization-wide bot certification dashboards showing which AI workers are allowed for which departments.
96. Add private enterprise skill packs that can be versioned, tested, and rolled back.
97. Add a DreamCo extension SDK so third parties can build adapters, skills, role packs, and UI modules against stable contracts.
98. Add extension signing, provenance, permission manifests, and sandbox review before installation.
99. Add a compatibility matrix that shows which DreamCo versions support each adapter, skill, model, and enterprise pack.
100. Add an automated release train that promotes only tested, benchmarked, migration-safe, cost-reviewed, policy-reviewed changes from development -> sandbox -> canary -> production.

## Deep-repo principle
The second wave is about turning DreamCo from many powerful parallel systems into one coherent, observable, migratable, testable platform. New features should not create another isolated subsystem unless they plug into the canonical contracts, runtime, project model, permissions, audit path, and benchmark system.
