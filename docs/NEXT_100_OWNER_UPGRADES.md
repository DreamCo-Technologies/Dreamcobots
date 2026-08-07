# DreamCo / Buddy — Next 100 Owner-Level Upgrades

This plan treats DreamCo as one product and one AI workforce platform. It is based on the current `buddy-rebuild-v2` architecture, the repository inventory, the active rebuild contracts, the bot catalogs, the test matrix, the public-site deployment path, and the product direction established for Buddy.

## North-star rule

Buddy should accept a legitimate user goal, assemble the right specialist team, discover the resources and tools needed, execute authorized work, explain risk and cost, measure results, learn from outcomes, and leave the user in control of data and permissions.

## A. Canonical runtime and truth layer

1. Build one `BotRuntimeV2` executor that consumes `bot-contract-v2` for every bot instead of category-specific ad hoc execution.
2. Generate normalized V2 records for all bot-source JSON files and reject incomplete records in CI.
3. Add a canonical division registry and make every UI/catalog route read from it.
4. Build the capability graph: bot -> user job -> capability -> tool -> adapter -> permission -> benchmark -> evidence.
5. Add an evidence ledger with immutable run receipts and evidence hashes.
6. Separate `declared`, `configured`, `tested`, and `certified` capability counts everywhere in the product.
7. Add runtime-binding coverage as a first-class bot score.
8. Add connector-binding coverage as a first-class bot score.
9. Add benchmark-coverage percentage to every bot.
10. Add a production certification gate that is required before a bot is labeled production-ready.

## B. Universal goal and role engine

11. Add a universal goal classifier that routes user goals before choosing bots.
12. Add automatic specialist-team assembly for each goal.
13. Add Role Packs for common professions and industries.
14. Add task-frequency-based role suggestions.
15. Add a user-editable role builder for custom jobs.
16. Add per-role default dashboards and action buttons.
17. Add per-role KPI definitions and success metrics.
18. Add per-role benchmark suites.
19. Add per-role learning curricula.
20. Add role-to-role handoff and escalation rules.

## C. Scalable autonomous task execution

21. Implement a durable queue backed by a real persistence layer rather than UI/process memory.
22. Add queue partitions by user, tenant, project, bot, and risk class.
23. Add dependency-aware DAG execution for multi-step projects.
24. Add retry policies with idempotency keys for external side effects.
25. Add dead-letter queues for tasks that repeatedly fail.
26. Add remote workers for heavy/background work.
27. Add device-aware scheduling using CPU, memory, thermal, battery, and network state.
28. Add pause/resume/cancel-all controls at user, project, bot, and company levels.
29. Add a large-task-list virtualized UI that can display 100,000 tasks without freezing.
30. Add task checkpointing so long projects survive device/app restarts.

## D. Background and device execution

31. Implement background-performance preferences across supported native clients.
32. Add explicit Maximum Mode for users who authorize high battery/data usage.
33. Add server fallback when mobile OS background execution is suspended.
34. Add paired-device work distribution so laptop/desktop can take heavy tasks from phone.
35. Add local-network device discovery only after owner enrollment/approval.
36. Add Bluetooth-device capability discovery behind explicit permissions.
37. Add per-device action scopes and capability cards.
38. Add a "Hey Buddy, check in" roll-call experience for authorized devices.
39. Add device health telemetry to the user-visible Trust Center.
40. Add an immediate global kill switch for all device actions.

## E. Local-first ownership and data control

41. Implement a local encrypted Buddy Vault as the default personal data store where practical.
42. Add portable Buddy export/import packages for settings, workflows, personality, memory, and agent definitions.
43. Add selectable storage targets: local-only, user cloud, self-hosted, enterprise, optional DreamCo cloud.
44. Add per-data-category storage location controls.
45. Add a data lineage view showing where every memory or fact came from.
46. Add a Data Finder that searches all user-authorized local and connected sources.
47. Add one-click revoke/re-index controls for each data source.
48. Add a privacy-safe memory deletion workflow with index rebuild.
49. Add company/personal workspace isolation with separate keys and retention policies.
50. Add backup health, restore tests, and recovery scoring.

## F. Easy Coder / repository intelligence

51. Turn Easy Coder into a complete Describe -> Build -> Test -> Diff -> Push -> PR -> Deploy flow.
52. Add a beginner Git/GitHub mode that translates every Git action into plain English.
53. Add repository architecture graph generation.
54. Add repository-wide symbol/dependency search and impact analysis.
55. Add automatic relevant-test selection before push.
56. Add generated-code provenance and license tracking.
57. Add open-source pattern search that returns ideas and tradeoffs instead of blindly copying code.
58. Add framework/library benchmark cards for each supported ecosystem.
59. Add per-library capability labs showing what open source can build with that library.
60. Add innovation proposals that suggest useful extensions for open-source libraries and user projects.

## G. Sales, lead generation, and growth teams

61. Generate a specialized sales team profile for every business-capable bot.
62. Generate ICPs and qualification rules per bot/category.
63. Add per-bot offer builders tied to measurable user outcomes.
64. Add per-bot ROI calculators and proof-point libraries.
65. Add compliant lead discovery across authorized/public business sources.
66. Add outreach-channel adapters with opt-out and platform-policy enforcement.
67. Add call/email/social role-play training for human reps.
68. Add rep scorecards, coaching plans, and trend tracking.
69. Add loss-reason and objection intelligence that feeds product improvement.
70. Add a scaling team to every bot: revenue, automation, partnerships, retention, cost, expansion, and analytics.

## H. Business OS and opportunity engine

71. Build a unified Start / Run / Grow Business workspace.
72. Add resource discovery for grants, loans, accelerators, competitions, and economic-development programs.
73. Add contract/RFP opportunity discovery and qualification.
74. Add supplier, vendor, insurance, payments, shipping, software, and operating-cost comparison workflows.
75. Add a Next Best Business Action engine driven by current company data and user goals.
76. Add business launch checklists by jurisdiction and industry with official-source links.
77. Add invention commercialization workflows: research, prototype, manufacturing, licensing, funding, launch.
78. Add business-health scorecards for revenue, cash flow, sales, retention, costs, operations, and risk.
79. Add expansion simulations for new products, locations, markets, and channels.
80. Add company-specific Buddy training from authorized SOPs, manuals, policies, and documents.

## I. Commerce, sourcing, import/export

81. Build Alibaba/supplier sourcing adapters and structured supplier verification workflows.
82. Build Amazon marketplace workflow adapters for listing, inventory, fulfillment, and analytics where API access allows.
83. Add landed-cost calculators with duties, freight, fees, returns, advertising, and fulfillment.
84. Add category-specific import/export compliance profiles with official-source freshness dates.
85. Add dropshipping agreement builders with legal-review handoff.
86. Add supplier scorecards using quality, price, lead time, MOQ, verification, and defect history.
87. Add product opportunity scoring by demand evidence, competition, margin, compliance, and return risk.
88. Add FBA/FBM/3PL/dropship scenario comparisons.
89. Add international sourcing and sales workflows per DreamCo bot category.
90. Add commerce learning loops that compare forecast margins with real post-sale outcomes.

## J. Personality, avatars, creator, and communication OS

91. Build Personality Studio UI from the personality contract and presets.
92. Add profession-themed robot avatars for every bot with per-bot outfit/tool/theme defaults.
93. Add company-branded avatar fleets and user customization controls.
94. Add original-character Actor Studio with appearance, voice, personality, wardrobe, and series memory.
95. Build Creator/Streamer Studio with scripts, thumbnails, clips, schedules, publishing, analytics, and sponsorship workflows.
96. Build end-to-end Movie/Series production workspaces with writer, director, editor, audio, music, marketing, and distribution teams.
97. Build DreamCo Connect: direct messages, channels, communities, team spaces, and AI-assisted collaboration.
98. Add meeting/video-call architecture with transcription, summaries, action items, screen sharing, and consent-aware recording.
99. Add contextual "I can help with..." suggestions to every bot and workspace, personalized from accepted/ignored suggestions.
100. Add an Owner Control Tower that shows fleet certification, runtime health, queue load, connector health, benchmark gaps, sales/growth opportunities, data locations, costs, risks, and the next highest-value upgrade.

## Release sequencing

### Wave 1 — Make the system true
1-10, 21-30, 51-56

### Wave 2 — Make it valuable
61-80

### Wave 3 — Make it connected
31-50, 81-90

### Wave 4 — Make it memorable and collaborative
91-100

## Definition of done for any upgrade

An upgrade is not complete because a file or button exists. It is complete when it has:

- canonical contract/schema
- runtime implementation
- required connector(s)
- permission policy
- failure/retry behavior
- user-visible state
- tests
- benchmark fixture(s)
- evidence record
- documentation
- cost/risk behavior
- production certification state

## Owner rule

Prioritize fewer certified capabilities over a larger number of unverified claims. Every new feature should either improve user goal completion, measurable business value, developer accessibility, user ownership/control, or platform reliability.
