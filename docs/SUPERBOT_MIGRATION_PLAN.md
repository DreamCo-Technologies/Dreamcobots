# DreamCo Superbot Migration Plan

## Decision
Stop expanding the number of standalone bots. The repository already has **1,051 catalog profiles across 45 divisions**, with 1,051 governed runtime instances and **zero separate standalone processes** according to the repository's fleet prospectus. The E2E certification reports 1,051/1,051 sandbox-certified profiles and 8,408/8,408 capability contracts passing, while live external flows remain intentionally unverified until providers are configured and approved.

That means the next optimization is consolidation, not bot creation.

## Target architecture

The target is approximately **12 governed Superbots**. Specialist bots become capability modules, skills, route aliases, test packets, and commercial profiles inside those Superbots.

### 1. Command Superbot
Routing, planning, scheduling, analytics, approvals, audit, fleet health, failure escalation.

### 2. AI Infrastructure Superbot
Models, memory, learning, evaluation, model selection, AI infrastructure.

### 3. Engineering Superbot
Coding, debugging, testing, software, APIs, architecture, automation, DevOps.

### 4. Business Superbot
Business launch, consulting, proposals, operations, B2B workflows.

### 5. Money Superbot
Money OS, deal discovery, price drops, coupon/receipt matching, settlements, grants, savings, lead monetization, revenue attribution.

### 6. Commerce Superbot
Retail, marketplaces, ecommerce, sourcing, dropshipping, digital products.

### 7. Real Assets Superbot
Real estate, construction, maintenance, transportation, equipment and property intelligence.

### 8. Finance & Risk Superbot
Finance, lending, payments, insurance routing, trading, portfolio analytics and risk controls.

### 9. Sales & Growth Superbot
Sales, lead generation, CRM, customer intelligence, social growth, influence and referrals.

### 10. Content & Media Superbot
Content, arts, video, audio, creator workflows, social media and gaming.

### 11. People & Services Superbot
Education, jobs, health, personal care, food and professional services.

### 12. Security & Governance Superbot
Cybersecurity, legal workflows, protection, compliance, governance and regulated-domain safeguards.

## Critical preservation rule
Do **not** simply delete the 1,051 profiles. Preserve every useful capability and route as a module. Old slugs become compatibility aliases that resolve to a Superbot capability.

Example:

`algo-trading` -> `finance_risk.trading.algo`
`home_buyer_bot` -> `real_assets.real_estate.home_buying`
`dealBot` -> `money.deals.price_drop`
`receiptBot` -> `money.receipts.reward_match`
`couponBot` -> `money.deals.coupon_stack`
`debugger` -> `engineering.debugging`

The user still experiences the same capability; internally there is one governed worker instead of a separate worker for every specialist.

## Migration sequence

### Phase 0 — Freeze
- No new standalone bot profiles unless they are explicitly approved as a new capability module.
- New ideas go into a capability backlog, not `bots/` or `App_bots/` as another worker.

### Phase 1 — Inventory
For every profile/file, extract:
- slug
- division
- capabilities
- tools
- connectors
- dependencies
- runtime route
- permissions
- tests
- revenue model
- UI route
- workflow references
- duplicate/similar capability signatures

### Phase 2 — Cluster
Group profiles by capability similarity and assign one Superbot owner.

### Phase 3 — Contract merge
Merge capability declarations, dependencies, permissions and tests into the Superbot contract. Use `shared/bot-contract-v2.ts` as the canonical contract; it already supports capability evidence, dependencies, permissions, autonomy ceilings, memory policy, commercial metadata and readiness evaluation.

### Phase 4 — Runtime merge
Use the existing governed `FleetRuntimeRegistry` as the execution boundary. The current runtime already performs capability-aware routing and sandbox certification. Extend it so aliases resolve to Superbot + capability rather than spawning another worker.

### Phase 5 — Compatibility
Keep old URLs, bot slugs and UI identifiers working through aliases until every consumer is migrated.

### Phase 6 — Delete duplicates
Only after E2E parity is proven should duplicate runtime/config files be removed. Keep a migration manifest so rollback is possible.

## Definition of success
The consolidation is successful when:

- Fewer worker runtimes exist.
- Every previous user-facing capability remains routable.
- Capability tests remain green.
- Permissions do not broaden during consolidation.
- Revenue workflows still attribute revenue correctly.
- Website/API routes continue working.
- Memory and observability remain intact.
- No duplicate scheduler or external-write path exists.
- New capability requests add modules to an existing Superbot instead of new bots.

## Important finding
The repository already contains the beginnings of this architecture: `shared/bot-contract-v2.ts` defines capability evidence and readiness, `server/fleet-runtime.ts` provides governed capability routing, and `tools/run_bot_fleet_e2e.ts` certifies the fleet. The consolidation should strengthen those existing systems rather than introduce another competing orchestrator.
