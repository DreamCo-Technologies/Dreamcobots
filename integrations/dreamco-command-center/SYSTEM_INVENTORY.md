# DreamCo Command Center Systems Inventory

Generated from `DreamCo-Technologies/DreamCo-Command-Center` on main.

## Source totals

- Total files discovered: 328
- Import candidates after skipping TypeScript build cache files: 325
- Skipped generated cache files: 3 `*.tsbuildinfo`
- Approximate source size: 2.3 MB

## Top-level source areas

| Area | Purpose |
| --- | --- |
| `artifacts/api-server/` | TypeScript API server for command-center systems |
| `artifacts/dreamco-dashboard/` | Main React/Vite Command Center dashboard app |
| `artifacts/mockup-sandbox/` | Replit mockup preview sandbox |
| `attached_assets/` | Replit prompt/build directive assets |
| `dreamcobots-contract/` | Bot manifest schema, validation workflows, and starter bot contracts |
| `lib/api-client-react/` | Generated React API client |
| `lib/api-spec/` | OpenAPI contract and Orval config |
| `lib/api-zod/` | Generated Zod/API types |
| `lib/db/` | Drizzle database package and schemas |
| `lib/replit-auth-web/` | Replit auth web helper |
| `scripts/` | Sync and post-merge scripts |

## API systems to import

- `auth`
- `biometric`
- `bots`
- `buddy`
- `buddyCapabilities`
- `copilot`
- `dashboard`
- `earnings`
- `github`
- `health`
- `media`
- `memory`
- `quantum`
- `snapshots`
- `sources`
- `stripe`
- `stripeWebhook`
- `vibe`

## Dashboard pages to preserve

- `actions`
- `ai-leaders`
- `autonomy`
- `bots`
- `buddy`
- `business`
- `capabilities`
- `consent`
- `copilot`
- `costs`
- `crypto`
- `dashboard`
- `deals`
- `divisions`
- `ecosystem`
- `formulas`
- `github`
- `learning-matrix`
- `loans`
- `marketplace`
- `memory`
- `pricing`
- `quantum`
- `revenue`
- `sources`
- `studio`
- `system`
- `time-capsule`
- `vibe`

## Bot contract manifests discovered

- `ai_enablement_hub`
- `auto_client_hunter`
- `company_lookup`
- `elite_scraper`
- `god_mode_autocloser`
- `payment_autocollector`

## Database schemas to merge

- `agent_capabilities`
- `agent_inheritance`
- `agents`
- `ai_sources`
- `auth`
- `biometric_consent`
- `bot_manifest`
- `bot_runs`
- `buddy_notes`
- `capabilities`
- `divisions`
- `events`
- `media_jobs`
- `quantum_providers`
- `snapshots`
- `vibe`
- `workflows`

## Next import chunk

The next safe chunk should copy these first because they define how every other module connects:

1. `dreamcobots-contract/`
2. `lib/db/src/schema/`
3. `lib/api-spec/openapi.yaml`
4. `artifacts/api-server/src/routes/bots.ts`
5. `artifacts/api-server/src/routes/buddy.ts`
6. `artifacts/dreamco-dashboard/src/pages/actions.tsx`
7. `artifacts/dreamco-dashboard/src/pages/bots.tsx`
8. `artifacts/dreamco-dashboard/src/pages/dashboard.tsx`
