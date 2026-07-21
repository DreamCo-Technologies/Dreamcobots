# DreamCo App Foundry

DreamCo App Foundry is the own-code-first layer for building, testing, packaging, hosting, and deploying client projects from this repository.

The rule is simple: DreamCo code is the source of truth. External platforms can host, process payments, send email, or run a container, but they are adapters. Buddy and the repo remain the builder of record.

## Build Lanes

- Games: design docs, playable prototypes, levels, scoring, controls, saves, and deploy bundles.
- Websites: client sites, portals, landing pages, documentation hubs, and product showcases.
- Apps: screen maps, data models, API contracts, local-first storage, tests, and rollback plans.
- School courses: outlines, lesson modules, quizzes, rubrics, teacher notes, and student-safe media plans.
- Simulations: scenario models, variables, deterministic engines, charts, and replayable results.
- Dashboards: command centers, bot dashboards, prospectus pages, KPI trackers, and alerts.
- Creative media: scripts, storyboards, asset manifests, consent ledgers, and export plans.
- Business bots: tool contracts, APIs, webhooks, workflows, sandbox tests, and approval packets.

## Hosting Path

Static-first projects can preview through GitHub Pages, Hostinger, or any static host. Backend apps stay in sandbox/mock mode until production secrets, auth, monitoring, and rollback gates are configured.

Runtime apps move through:

1. Local laptop sandbox.
2. Static preview where possible.
3. Managed Node or container host after approval.
4. Production deployment only after rollback and owner approval.

## Gates

- Generated code must build.
- JSON, Python, and JavaScript syntax checks must pass.
- Each project needs a sandbox test packet.
- Each sandbox needs a workflow generator.
- API contracts need mocked sandbox tests.
- Secrets must not be committed.
- Local-first storage policy applies by default.
- Media needs rights and consent review.
- Money movement, outreach, production deploys, and credential changes require owner approval.

## Reports

Generate the dashboard report with:

```bash
npm run report:app-foundry
```

Check that the committed report is current with:

```bash
npm run check:app-foundry
```
