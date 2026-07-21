# DreamCo Repository Consolidation Board

Main destination: `DreamCo-Technologies/Dreamcobots`

The goal is to make `Dreamcobots` the only active source of truth. Other repositories become source imports, archive references, or are retired after their useful systems are merged.

## Repositories discovered

| Repository | Role | Status | Import plan |
| --- | --- | --- | --- |
| `DreamCo-Technologies/Dreamcobots` | Main destination | Active | Keep root stable; add integrations, scans, dashboards, CI |
| `DreamCo-Technologies/DreamCo-Command-Center` | DreamCo command center source | Stage 1 inventoried | Import dashboard, API, DB, contracts, assets, scripts in chunks |
| `DreamCo-Technologies/Dreamco` | Small side repo | Pending inventory | Inspect, preserve useful files, then retire if duplicate |
| `ireanjordan24/Dreamcobots-Grok-Revolutionary` | Personal prototype source | Pending import | Bring Stage 1 Actions page concepts and docs into main repo |

## Consolidation stages

### Stage 1: Control plane

- Add integration folder and inventory.
- Add missing-file scanner.
- Add bot tracking and learning spec.
- Add dashboard specification.
- Add 100-resource AI map.

### Stage 2: Contract and schema import

- Import `dreamcobots-contract/` from Command Center.
- Import DB schemas from `lib/db/src/schema/`.
- Import OpenAPI spec from `lib/api-spec/openapi.yaml`.
- Normalize all bot manifests against one schema.

### Stage 3: Dashboard import

- Import Command Center dashboard into `apps/command-center/` or `integrations/dreamco-command-center/source/artifacts/dreamco-dashboard/`.
- Keep app isolated until its package build passes.
- Connect Actions, Agents, Bots, Dashboard, Memory, Workflows, Resources, and Commands pages.

### Stage 4: API import

- Import API server routes and libraries.
- Connect bot indexer, source indexer, Buddy routes, memory routes, and dashboard routes.
- Add auth and command permission checks before exposing write actions.

### Stage 5: Bot repair

- Run `npm run scan:missing`.
- Generate `reports/bot-health-report.md`.
- Create one issue per broken bot or one PR per bot family.
- Add missing README, manifest/profile, run command, examples, and tests.

### Stage 6: GitHub dashboard automation

- Add GitHub Actions for missing-file scan, bot framework check, agent audit, tests, and dashboard report publishing.
- Add labels and issue templates for bot modes, risk, missing files, learning stages, and workflow blockers.

### Stage 7: Retirement

- After files are merged and validated, mark side repos as archived or read-only.
- Add archive notes pointing back to `Dreamcobots`.

## Do not overwrite

- Root `package.json` until a migration branch proves the package manager plan.
- Existing `.github/workflows/` without checking current CI.
- Existing `bots/`, `python_bots/`, `java_bots/`, or `empire-os/` files without comparing behavior.
- Secrets, environment files, or production deploy settings.

## Next concrete import chunk

1. `dreamcobots-contract/README.md`
2. `dreamcobots-contract/bot.manifest.schema.json`
3. `dreamcobots-contract/bots/*/bot.manifest.json`
4. `lib/db/src/schema/*.ts`
5. `lib/api-spec/openapi.yaml`
6. `artifacts/dreamco-dashboard/src/pages/actions.tsx`
7. `artifacts/dreamco-dashboard/src/pages/bots.tsx`
8. `artifacts/dreamco-dashboard/src/pages/dashboard.tsx`
9. `artifacts/api-server/src/routes/bots.ts`
10. `artifacts/api-server/src/routes/buddy.ts`
