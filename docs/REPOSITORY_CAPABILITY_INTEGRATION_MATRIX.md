# DreamCo Cross-Repository Capability Integration Matrix

## Purpose

Treat the DreamCo repositories as a capability portfolio rather than blindly merging unrelated histories. `DreamCo-Technologies/Dreamcobots` remains the canonical production/benchmark repository. Other repositories are capability sources and test labs.

## Sources scanned

- `DreamCo-Technologies/Dreamcobots` — canonical master; public; large production/benchmark system.
- `DreamCo-Technologies/DreamCo-Command-Center` — dashboard/API/control-plane source.
- `DreamCo-Technologies/Dreamco` — small bot-system integration/migration-safety prototype.
- `DreamCo-Technologies/Ai-bots` — very small template/logging repository; no substantial capability found yet.
- `DreamCo-Technologies/demo-repository` — private GitHub demo repository; excluded from automatic code promotion until inspected separately.
- `ireanjordan24/Dreamcobots-Grok-Revolutionary` — small React/Vite Empire HQ prototype with bot/action/analyzer/orchestrator concepts and devcontainer support.
- `ireanjordan24/dreamcobots` — Apple/Xcode SwiftUI + SwiftData application prototype and tests.
- `ireanjordan24/codespaces-react` — development workspace; requires deeper inspection before promotion.

## Initial capability comparison

| Capability | Master | Command Center | Dreamco | Grok | Laptop iOS | Action |
|---|---|---|---|---|---|---|
| Benchmark registry/runner | Strong | Partial | No | No | No | Keep master as source of truth |
| Benchmark gap planning | Strong | Partial | No | No | No | Keep master; connect Command Center |
| Bot fleet indexing | Partial/fragmented | Strong implementation | Partial | Prototype | No | Adapt Command Center indexer to master APIs; do not copy its workspace DB imports |
| Command-center UI | Strong/partial | Strong | No | Empire HQ prototype | No | Compare UX; port only validated components |
| Bot/action/analyzer/orchestrator UX | Partial | Strong/partial | No | Prototype | No | Benchmark and adapt into master client |
| GitHub integration | Strong | Strong client implementation | No | Actions-oriented prototype | No | Consolidate behind one master GitHub service |
| Media providers | Strong | Strong implementation | No | No | No | Compare provider coverage; add only missing providers |
| Auth/API middleware | Strong | Strong implementation | No | Devcontainer only | No | Keep master security model; borrow patterns only after review |
| Legal/policy controls | Strong | Strong implementation | No | No | No | Compare policy coverage; do not duplicate enforcement |
| Apple/iOS app | No/limited | No | No | No | Starter app | Add as dedicated Apple client target, not mixed into server code |
| Local Mac experimentation | Designed in docs/tools | No | No | Devcontainer | Strong potential | Use laptop as benchmark lab/self-hosted runner |
| Migration safety | Partial | Partial | Explicit prototype | No | No | Extract useful invariants into master migration tooling |

## Promotion rules

1. Never overwrite `main` with another repository.
2. Prefer capability-level integration over repository-level merging.
3. Preserve original repositories as rollback/reference sources.
4. Promote code only when it has a clear master integration point and tests.
5. Never copy secrets, credentials, personal Xcode workspace data, generated dependencies, or environment-specific state.
6. Every promoted capability must receive a benchmark/quality gate where measurable.
7. If two implementations provide the same capability, benchmark both and retain the better one.
8. Failed promotions become GitHub Issues with the source repository and candidate capability recorded.

## Immediate priorities

### P0 — Cross-repository auditor

Automatically inventory repositories, classify capabilities, detect duplicate implementations, and emit a promotion plan.

### P0 — Benchmark integration

Connect candidate capability changes to the existing Buddy benchmark registry, benchmark runner, obstacle playbook, and parallel gap planner.

### P1 — Command Center bridge

Adapt the Command Center's bot indexing and GitHub integration concepts to the master repository's own server/data model rather than importing `@workspace/*` dependencies.

### P1 — Apple client

Treat the laptop SwiftUI project as an Apple client prototype. Integrate API contracts and benchmark telemetry, not the starter Xcode user-data files.

### P2 — Grok/Empire HQ UX

Use the Grok repository's Empire HQ concepts as a UI experiment. Promote only components that provide measurable workflow or benchmark value over the existing client.
