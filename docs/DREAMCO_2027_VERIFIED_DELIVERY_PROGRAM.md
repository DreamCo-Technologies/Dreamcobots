# DreamCo 2027 — Massive Verified Delivery Program

**Status:** proposed execution targets, not completed features. **Start:** 2026-10-22. **Horizon:** 2027-10-22.

## North star

Build a dependable, accessible, user-owned Buddy AI operating platform that executes authorized tasks, learns from independently evaluated work, teaches through original Buddy Bootcamp curricula, helps users create and improve compatible AI models, and earns sustainable revenue from demonstrably useful products.

This document extends rather than replaces `docs/MASTER_PLAN.md` and `docs/DREAMCO_MASTER_PLAN.md`. The machine-readable program is `config/dreamco-verified-goals-2027.json`: **10 workstreams × 10 explicit targets = 100 proposed capability outcomes**. These 100 are not claimed implemented, tested, or mastered.

## Measurable one-year outcomes

| Measure | Target | Counting rule |
| --- | ---: | --- |
| Independently verified capabilities | 100 | Unique capability ID with passing reproducible acceptance evidence, exact revision and reviewed result |
| Production-certified specialist capabilities | 25 | Above, plus authorization, deployment, monitoring, recovery and release certification |
| Bootcamp courses | 10 | Original lessons, source citations, runnable exercise, assessment and accessibility check |
| Operational commercial products | 3 | Working customer journey, support, billing safety, tested delivery and cost tracking |
| Products with paying customers | 1 | Actual consented payment and delivered customer value, not a simulated sale |
| Independently passed coding evaluations | 25 | Held-out tasks across languages and frameworks, with clean execution receipts |

These are stretch targets, conditional on resources and engineering progress. Do not treat a target as a forecast or success claim.

## Delivery lanes and acceptance

1. **Foundation (P0):** reproduce historical security findings on current `main`; secure any unauthenticated sensitive routes; pass required CI, dependency, secret and deployment gates; verify auth denial and rollback.
2. **Truth & Pages (P0):** publish public-safe capability evidence with exact revision, source, timestamp, test/benchmark status, connection state, blocked reason and last verified time. Mark absent or stale evidence unknown.
3. **Learning (P1):** track permitted source inventory, actual ingest receipts, executed drills, held-out evaluations and reproducible improvements; never claim to have studied all code.
4. **Bootcamp (P1):** ten complete, original, attributed, beginner-friendly courses with runnable exercises and scored assessments; no unlicensed course reproduction.
5. **Models (P1):** baseline model routing and optional supervised open-weight experiments with data/model rights, cost limits, independent benchmarks and rollback.
6. **Fleet (P1):** preserve existing bot IDs and definitions; certify bounded capabilities using shared runtime, permission and test contracts; do not equate profiles with live bots.
7. **Products (P1):** choose three narrowly scoped user problems and verify onboarding, delivery, support, privacy, subscription safety and unit economics before expansion.
8. **Creative (P2):** release bounded original media/game workflows with editable exports, rights controls, real rendering evidence and measured costs.
9. **Devices (P2):** device/app adapters report exactly what they can do; require scoped permission, visible progress, stop/revoke and real-device tests before claiming support.
10. **Operations (P0/P1):** monitor cost, latency, success rate, security, regressions and recovery. Prefer smallest safe shared repair over hundreds of duplicated bots.

## Milestone gates

- **Day 30:** Current-revision security triage and release blockers documented; confirmed P0 issues fixed or transparently blocked; initial reproducible baseline.
- **Day 60:** Pages evidence dashboard tied to build/deploy artifacts; mobile verification; stale/unknown states visible.
- **Day 90:** 10 complete Bootcamp courses assessed, with source permissions and independent tests.
- **Day 120:** 25 passed independent coding evaluations; failures and dependencies visible.
- **Day 180:** Three operational, narrowly scoped products with tested delivery and billing flows; do not count planned products.
- **Day 270:** 25 individually production-certified specialist capabilities.
- **Day 365:** 100 distinct independently verified capabilities and at least one paying product.

## Required evidence packet for every capability

```json
{
  "capability_id": "learning-01",
  "state": "planned",
  "implementation_revision": null,
  "owner": null,
  "runtime_binding": null,
  "tests": [],
  "independent_benchmarks": [],
  "security_and_rights_review": null,
  "live_connection_probe": null,
  "production_receipt": null,
  "last_verified_at": null,
  "blocker": "Implementation and independent verification not established"
}
```

Promotion requires executable implementation, passing positive/negative/recovery tests, exact revision, reproducible benchmark and review. Live external capabilities additionally require authenticated adapter probes and environment evidence. Production requires deployment, observability, rollback and authorization gates. Model-assisted completion must be labeled model-assisted rather than native Buddy mastery.

## Immediate work queue

1. Refresh historical `reports/P0_PLAN_GAP_QUEUE.md` against current code before editing security controls. Prioritize GitHub workflow dispatch, GitHub push/sync and billing authorization; never publish exploitable secrets.
2. Run required CI and classify failures by code, infrastructure, credentials and historical/stale report; do not turn green by disabling tests.
3. Complete the draft Buddy Pages evidence dashboard PR #15259, including real deploy integration and navigation; prevent static report counts from masquerading as live results.
4. Implement one end-to-end Buddy task receipt: approved action → tool execution → output → independent test → Pages evidence.
5. Prove one complete Bootcamp module and one held-out coding evaluation before expanding to ten or twenty-five.
6. Select one low-cost customer workflow, measure actual successful delivery and cost, then generalize shared infrastructure.
7. Reconcile historical 37-plan crosswalk, 100-idea roadmap and current evidence without overwriting original source plans.

## Governance and tracking

The 100 targets in the JSON registry begin as `planned_target`; the initial verified count is **unknown until audited**, not automatically zero. Dashboards must derive status from evidence, not from this file's target list. Review every 30 days and reprioritize based on measured user value, security risk and cost. Never silently promote targets because their deadlines arrive.

## Source hierarchy

Canonical: `docs/MASTER_PLAN.md`, `docs/DREAMCO_MASTER_PLAN.md`. Production: `docs/PRODUCTION_READINESS_MASTER_PLAN.md`, `docs/DREAMCO_DELIVERY_PLAN.md`. Long term: `docs/BUDDY_LONG_TERM_SUCCESS_PATH.md`. Historical snapshots: `reports/MASTER_ROADMAP_CROSSWALK.md`, `reports/P0_PLAN_GAP_QUEUE.md`, `reports/GOALS_TO_PRODUCTION_GATES.md`. Historical findings require current-revision revalidation.
