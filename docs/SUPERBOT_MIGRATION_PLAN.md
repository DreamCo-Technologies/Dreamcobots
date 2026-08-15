# DreamCo Superbot Migration Plan

## Decision
Stop expanding standalone bots. The repository already reports **1,051 catalog profiles across 45 divisions**. The architecture will now make **every division a Superbot** while preserving all specialist bots as capability modules.

This produces **45 canonical Division Superbots**, coordinated by **12 Cluster Superbots**. The 1,051+ existing bot identities are not discarded; they become capabilities, workflows, tools, plans, notes, tests, routes and compatibility aliases owned by one Division Superbot.

## Target architecture

```text
Dream Command / Cluster layer
        │
        ├── 12 Cluster Superbots
        │
        └── 45 Division Superbots
                 │
                 └── all legacy bots → capability modules
```

### 12 Cluster Superbots

Command, AI Infrastructure, Engineering, Business, Money, Commerce, Real Assets, Finance & Risk, Sales & Growth, Content & Media, People & Services, Security & Governance.

### 45 Division Superbots

CommandCore, DreamAdmin, DreamAgents, DreamAIInfra, DreamAutomation, DreamCodeLab, DreamOps, DreamFlow, DreamBizLaunch, DreamEmpire, DreamGlobal, DreamAgriculture, DreamConstruction, DreamMaintenance, DreamRealEstate, DreamTransport, DreamProduction, DreamMarket, DreamRetail, DreamFinance, DreamEntFinance, DreamLoans, DreamPayments, DreamTrade, DreamSalesPro, DreamCustIntel, DreamInfluence, DreamSocial, DreamContent, DreamArts, GameTitan, DreamEducation, DreamHealth, DreamPersonalCare, DreamFood, DreamProServices, DreamLegal, DreamCyber, DreamProtection, DreamMilitary, DreamDecision, DreamData, DreamScience, DreamCrypto, DreamPlanetary.

The authoritative mapping is `config/superbot-consolidation-v1.json`.

## What happens to existing bots

Every old bot, agent, worker, scout, planner, manager, optimizer and duplicate profile is classified as one of:

- capability module
- workflow module
- tool adapter
- connector adapter
- compatibility alias
- test/evidence module
- supporting documentation/knowledge
- unique capability awaiting migration
- invalid/unused artifact requiring review

Example:

`algo-trading` → `DreamTrade Superbot → trading → algorithmic-trading`

`home_buyer_bot` → `DreamRealEstate Superbot → home-buying`

`dealBot` → `DreamFinance/Money capability → price-drop-deals`

`receiptBot` → `DreamFinance/Money capability → receipt-reward-match`

`couponBot` → `DreamRetail Superbot → coupon-stacking`

`debugger` → `DreamCodeLab Superbot → debugging`

The old identifiers remain routable until all consumers are migrated.

## Entire-repository accounting

This is broader than a bot scan. The new `tools/build_superbot_repository_inventory.py` recursively inventories the repository and records every eligible file's:

- path
- SHA-256 provenance hash
- division when discoverable
- proposed Superbot owner
- assignment method
- bot identity signal
- review requirement

It covers application code, bot definitions, legacy sources, configs, workflows, tests, website files, docs, memory, assets, generated artifacts and supporting files, while excluding only dependency/build/cache directories.

The inventory is produced as `config/generated/superbot-repository-inventory.json` and `reports/SUPERBOT_REPOSITORY_INVENTORY.md`.

## Migration gates

No mass deletion is performed simply because two filenames look similar.

A legacy artifact may be removed only after:

1. Complete repository inventory.
2. Capability parity.
3. Dependency parity.
4. Route/API/UI parity.
5. Permission parity.
6. Memory-policy parity.
7. Observability parity.
8. Revenue-attribution parity.
9. Sandbox certification.
10. Full E2E/regression pass.
11. Code Trust pass.
12. Duplicate-runtime check.
13. Rollback manifest recorded.

## Runtime rule

`shared/bot-contract-v2.ts` remains the canonical capability contract. `server/fleet-runtime.ts` remains the governed runtime boundary. Legacy bot slugs resolve to `division_superbot + capability` instead of creating separate worker processes.

Cluster Superbots coordinate Division Superbots; they do not copy or duplicate their capabilities.

## New-bot freeze

A new request does **not** create another bot by default.

It must first be added as a capability to the appropriate Division Superbot. A separate runtime is allowed only when the capability has a proven isolation, security, performance, connector, or lifecycle requirement that cannot be satisfied as a module.

## Definition of success

- 45 Division Superbots are canonical.
- 12 Cluster Superbots coordinate them.
- All existing bot identities remain accounted for.
- All useful plans, tools, capabilities, goals and notes have an owner.
- Existing routes continue working through aliases.
- Capability tests remain green.
- No permissions broaden during consolidation.
- No duplicate schedulers or external-write paths are introduced.
- Revenue workflows preserve attribution and reconciliation.
- The repository becomes smaller in runtime complexity even if historical provenance is retained.
- Future growth happens through capability modules, not bot proliferation.
