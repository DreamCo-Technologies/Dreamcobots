# Massive Improvement Suggestions — DreamCo-Technologies/Dreamcobots

Prioritized, concrete suggestions based on repository structure: 1,051 bot profiles, heavy Actions surface, Buddy governance, website + client/server, and CI-generated issue flood.

---

## P0 — Stop the bleeding (this week)

1. **Run Intelligent Issue Cleaner** hourly until CI issue backlog is under control
2. **Change Actions Failure Sweep** so it does not open a new issue per run ID; only upsert root-cause keys
3. **Disable or throttle** workflows that fail on every PR and re-open duplicate issues
4. **Concurrency groups** on all high-frequency workflows (`cancel-in-progress: true` where safe)
5. **Single required CI gate** (typecheck + unit) vs many optional noisy jobs
6. **Pin Actions** to known-good major versions; avoid surprise breaks
7. **Secrets audit**: ensure no tokens in client bundles or committed `.env`
8. **Document the truth rule** on the main README: profiles ≠ live runtimes
9. **Run** `tools/ensure_bots_production_ready.py` once and commit profile gaps
10. **Freeze new bot spam**: no new profiles without required fields + markdown

## P1 — Fleet data quality (1–2 weeks)

11. Enforce `required_bot_fields` in CI (`slug`, `displayName`, `category`, `description`, `capabilities`, `status`)
12. Fail CI when division `total` ≠ `bots.length`
13. Fail CI on duplicate slugs
14. Generate `bots/<slug>.md` for every App_bots entry
15. Add `systemPrompt` + `sample_test_prompt` to every profile
16. Standardize tier vocabulary (`free|pro|enterprise|elite`)
17. Category taxonomy doc + validator
18. Division placement audit → reviewed moves only (no blind auto-move)
19. Deduplicate near-identical capability lists (template + overrides)
20. Mark recovered/original bots with `source: recovered` metadata
21. Export a machine-readable fleet manifest for Buddy routing
22. Search index rebuild on every catalog change
23. Prospectus pages only show bots with complete profiles
24. Archive experimental bots to `original-bots/` instead of deleting
25. Quarterly fleet prune: inactive + no evidence → `status: archived`

## P2 — Buddy becomes the real product

26. Wire xAI/Grok API behind server-side key (never browser)
27. Streaming chat UI with bot hand-off chips
28. Routing confidence score + "why this bot" explanation
29. Multi-intent split (one message → multiple specialists)
30. Session memory + optional long-term memory vault
31. Ingest chat exports from `chats/` or user uploads
32. Approval modal for publish / spend / outreach / prod write
33. Action log (last 50–500 events) with filters
34. Sandbox-default tool execution
35. Evaluation set: 100 golden user jobs with expected bot routes
36. Regression test: routing accuracy ≥ target
37. Operator "30 questions" linked to real prompts
38. Voice-style short commands (`deal:`, `build:`, `write:`)
39. Buddy Success Center profile (non-sensitive) in local storage
40. Clear blocked/owner-action states in UI when verification can't finish

## P3 — CI & engineering system

41. Collapse overlapping benchmark workflows into one matrix
42. Separate `schedule` jobs from `pull_request` required checks
43. Artifact uploads only on failure (save storage)
44. Central `workflow_call` reusable workflows
45. `paths` filters so docs-only PRs skip heavy jobs
46. Dependabot/Renovate for npm + Actions
47. CodeQL + dependency review kept; noise tuned
48. Flaky test quarantine with expiry dates
49. "Repair issue" template that demands first failing step
50. Auto-close root-cause issues only after green verification on same workflow
51. Branch protection: require 1 green gate + up-to-date
52. CODEOWNERS for `App_bots/`, `server/`, `.github/workflows/`
53. Pre-commit or CI prettier/eslint for TS
54. Python tooling pinned in requirements files
55. Nix/devcontainer parity documented

## P4 — Website & command center

56. One nav model shared by `website/` and `client/`
57. Live dashboard data from API, not only static JSON
58. Bot page: capabilities, tasks, learning, benchmarks tabs
59. Division explorer with counts and search
60. Deals calculators behind clear "estimates only" labels
61. Settings page for connection profiles (no raw secrets)
62. Debug page only in non-prod or behind auth
63. Performance: code-split large fleet JSON
64. CDN caching headers for static assets
65. Public status page for API health
66. Accessibility audit (keyboard, contrast, labels)
67. i18n readiness if global users matter
68. Analytics with privacy-friendly defaults
69. SEO metadata for bot prospectus pages
70. Offline-friendly static fallbacks

## P5 — Runtime truth & benchmarks

71. Never display fabricated benchmark scores
72. Empty live scores until authenticated adapters return evidence
73. Per-run budget and approval for live model calls
74. Sandbox capability campaign with stored evidence packs
75. Competitor benchmarks only with dated sources
76. Model catalog refresh job with committed snapshots for offline CI
77. Capability contracts per division (bounded parallel checks)
78. Distinguish catalog claim vs executable instance vs standalone OS process
79. Telemetry schema for latency, cost, failure class
80. Weekly evidence freshness report

## P6 — Security, legal, trust

81. Threat model doc for Buddy local bridge
82. Explicit bans: credential stuffing, DoS, third-party attacks
83. Minors / sensitive trait targeting bans in data bots
84. License scan for third-party code
85. Data retention policy for memory vault
86. User deletion/correction path for stored preferences
87. Audit log immutability strategy
88. Role model: owner vs operator vs viewer
89. Enterprise SSO design notes (when needed)
90. Incident response runbook for leaked key

## P7 — Money features (honest)

91. Deal scoring weights documented and tunable
92. Historical win/loss calibration when data exists
93. Export deal summary PDF/CSV
94. CRM export adapters optional and approved
95. Clear separation of opportunity estimates vs confirmed revenue
96. Payment connectors only via DreamPayments governed paths
97. Cost controls on model spend
98. Usage metering design
99. Refund/dispute process notes for SaaS tiers
100. No "guaranteed income" marketing claims in product UI

## P8 — Content & growth

101. Brand voice one-pager for ContentBot
102. 2-week content calendar template
103. Approval checkpoints before publish
104. Template library for winning post formats
105. Multi-channel variants from one idea
106. Launch asset pack generator (governed)
107. Docs site search
108. Public changelog
109. Case studies only with real evidence
110. Community contribution path for bot profiles

## P9 — Scale & architecture

111. Prefer shared fleet runtime over per-bot microservices
112. Config-driven specialists, not copy-pasted code
113. Event bus for bot-to-bot handoffs (optional later)
114. Queue for long-running sandbox jobs
115. Multi-region only after single-region reliability
116. Feature flags for experimental divisions
117. Schema versioning for App_bots (`schema` field)
118. Migration tooling when profile shape changes
119. Hard limit on workflow count; archive unused YAML
120. Cost dashboard for Actions minutes

## P10 — Operator 1-day and 30-day plans

### 1-day focus
121. Green typecheck + build
122. Issue cleaner dry-run then apply
123. Production readiness apply for profiles
124. Buddy route + one live API reply (if key available)
125. Pages/website smoke test

### 30-day focus
126. CI noise under 50 open auto-issues
127. Routing eval harness live
128. 10 division sandbox packs with evidence
129. Deal + Content paths usable end-to-end in sandbox
130. Weekly readiness report automated

## P11 — Metrics that matter

131. Open issues (auto vs human)
132. Median time to close CI root-cause issues
133. % bots with complete profiles
134. % bots with sandbox evidence in last 30 days
135. Routing accuracy on golden set
136. CI minutes per week
137. Deploy success rate on main
138. p95 API latency
139. Model spend per day
140. User-job completion rate (when product has users)

## P12 — Anti-patterns to avoid

141. Opening an issue for every failed Actions run forever
142. Marking `production_ready: true` from markdown alone
143. Hand-editing generated evidence to pass CI
144. Deleting tests to go green
145. 1000 near-duplicate workflows
146. Secrets in frontend
147. Claiming live money actions without approval + adapter
148. Expanding bot count without quality bar
149. Building per-bot infrastructure when shared will do
150. Ignoring `AGENTS.md` evidence-first debugging rules

---

## Suggested implementation order (next 5 commits)

1. Failure Sweep: root-cause upsert only (stop issue flood at source)
2. Issue Cleaner: confirm hourly apply is green
3. `ensure_bots_production_ready.py` apply + report committed
4. CI: required field validator on `App_bots`
5. Buddy: server-side Grok route + UI stream (API key in secrets)

---

*Living document. Update as blockers clear. Honesty over hype.*
