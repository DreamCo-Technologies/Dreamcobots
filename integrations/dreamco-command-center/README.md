# DreamCo Command Center Integration

Source repository: `DreamCo-Technologies/DreamCo-Command-Center`
Destination repository: `DreamCo-Technologies/Dreamcobots`

This folder is the staging area for merging the Replit-built DreamCo Command Center into the main Dreamcobots repository without breaking the existing bot platform.

## What is being combined

- Replit workspace configuration: `.replit`, `.npmrc`, `pnpm-workspace.yaml`, root TypeScript config, and scripts.
- Command Center API: Express/TypeScript API server with auth, bots, Buddy, dashboard, earnings, GitHub, memory, media, quantum, sources, Stripe, and vibe routes.
- DreamCo dashboard app: Vite/React dashboard with actions, bots, Buddy, business, capabilities, dashboard, divisions, GitHub, memory, pricing, revenue, system, studio, vibe, and related UI components.
- Shared libraries: API client, API spec, Zod schemas, database schema package, and Replit auth web helper.
- Bot contract system: manifest schema, validation workflows, copilot instructions, and starter bot manifests.
- Replit attached assets and master build directives.

## Merge stages

1. Inventory and preserve the Replit source map in the main repo.
2. Copy source modules into this integration folder in safe chunks.
3. Promote stable bot manifests and schemas into the main `bots/` framework.
4. Wire the Command Center dashboard as a runnable app without disrupting the existing static build.
5. Connect API routes to the existing Dreamcobots automation, audit, and bot framework scripts.
6. Add CI checks for the imported workspace, then remove duplicate/generated cache files.

## Build safety notes

The command-center source uses `pnpm` and TypeScript workspaces. The main Dreamcobots repository currently uses Node scripts, Express, Jest, ESLint, and a static `public` build. The integration should stay isolated until its package scripts pass independently.

Do not overwrite root `package.json`, workflows, or existing bot folders until the imported app has its own green build path.
