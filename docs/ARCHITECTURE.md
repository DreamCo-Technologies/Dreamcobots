# DreamCo Architecture Standard

> Engineering rule: **preserve capability, simplify runtime.**

## 1. Architecture goals

DreamCo is a governed platform, not a pile of independent bots. The architecture prioritizes modularity, composability, observability, testability, secure defaults, reversibility, commercial measurement, and predictable engineering conventions.

## 2. Canonical hierarchy

```text
Platform
├── Command / control plane
│   ├── routing
│   ├── policy
│   ├── approvals
│   ├── scheduling
│   ├── observability
│   └── audit
├── Cluster Superbots
│   └── domain coordination
├── Division Superbots
│   └── capability modules
│       ├── domain logic
│       ├── tool adapters
│       ├── connector adapters
│       ├── workflows
│       ├── benchmarks
│       └── evidence
├── Shared platform
│   ├── contracts
│   ├── identity
│   ├── memory
│   ├── model routing
│   ├── data access
│   ├── billing
│   └── telemetry
└── Product surfaces
    ├── web
    ├── APIs
    ├── dashboards
    └── automation interfaces
```

## 3. Division Superbot contract

Every division Superbot owns one domain boundary and exposes identity, mission, user jobs, normalized capabilities, tools, connectors, policies, dependencies, workflows, benchmarks, evidence, observability, commercial metadata, migration provenance, and lifecycle status.

The existing `shared/bot-contract-v2.ts` remains the low-level contract. Division Superbot metadata extends it rather than replacing it.

## 4. Capability design

A capability is the smallest independently testable business/technical outcome. Name capabilities after outcomes, not implementation details.

Good: `money.deals.price_drop_detection`

Bad: `dealBot2`

Each capability receives an ID, owner division, mission, inputs, outputs, tools, connectors, policy requirements, failure modes, benchmark IDs, evidence state, version, and provenance.

## 5. Runtime rule

A capability module does **not** automatically receive its own worker process. The default is a shared governed worker selected by the Division Superbot. A dedicated worker requires a documented isolation, security, runtime, performance, connector-lifecycle, or other engineering justification.

## 6. Professional repository layout

```text
config/
  superbot-consolidation-v1.json
  superbot-contract.schema.json
  divisions/<division>.json
contracts/capabilities/<capability>.json
workflows/<domain>/
server/runtime/
server/adapters/
server/policies/
shared/contracts/
shared/types/
shared/schemas/
memory/policies/
memory/migrations/
tools/inventory/
tools/generators/
tools/validation/
benchmarks/<domain>/
tests/unit/
tests/integration/
tests/contract/
tests/e2e/
reports/architecture/
reports/certification/
reports/migration/
docs/adr/
docs/architecture/
docs/operations/
docs/product/
```

Existing paths may remain during migration. New code should follow this structure where practical; moving files only for aesthetics is discouraged when it creates risk.

## 7. Separation of concerns

- Contracts define what a capability promises.
- Runtime decides how it executes.
- Adapters communicate with external systems.
- Policies decide what actions are permitted.
- Workflows coordinate capabilities.
- Benchmarks measure quality.
- Reports describe observed state and never become hidden runtime configuration.
- Product surfaces consume APIs/contracts instead of embedding domain logic.

## 8. Money architecture

Money capabilities must distinguish: `opportunity detected → verified → eligible → user action → provider confirmation → realized revenue/savings`.

Estimated value is never treated as realized revenue.

## 9. Security architecture

Secrets never belong in capability definitions, bot JSON, documentation, generated reports, or source control. Every external-write capability declares action, scope, approval requirement, maximum spend if applicable, audit receipt, rollback/recovery behavior, and responsible connector.

## 10. Migration architecture

Legacy bots are preserved as provenance records and compatibility aliases until parity is proven.

Lifecycle:

`discovered → classified → assigned → normalized → contract-merged → route-migrated → tested → certified → deprecated-alias → removable`

No file is deleted because it merely looks redundant. Removal requires capability, dependency, route, policy, evidence, consumer, and recovery parity.

## 11. Pull-request quality bar

Every change should answer: what changed; which Superbot owns it; which contract changed; which tests prove it; which dependencies changed; which routes changed; whether a new runtime was created and why; whether external side effects exist; how outcomes/revenue are measured; and how to roll back.

## 12. Definition of done

A user request must be traceable through:

`UI/API → command routing → cluster → division Superbot → capability → adapter/tool → evidence → outcome → audit/telemetry`

without encountering competing duplicate implementations.
