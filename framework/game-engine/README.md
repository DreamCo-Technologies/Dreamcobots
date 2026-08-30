# Ultimate Game-Building Engine

Architecture foundation for Buddy's general-purpose game and simulation builder.

`Natural language -> Intent compiler -> Game Design IR -> Generation -> Validation -> Runtime -> Persistence/Networking -> Client/Editor`

The engine is designed for progressively larger games rather than template-only demos.

## Core capabilities

- Chunked/streamed worlds and persistent world state
- Procedural generation
- NPC/agent simulation and model-routed intelligence
- Multiplayer-ready server-authoritative state
- Quests, jobs, inventories and economies
- User-created towns, cities, buildings and interiors
- Historical worlds with provenance
- Educational objectives, assessments and teacher tooling
- Asset provenance/versioning
- Automated playtesting
- Security/performance gates
- PR/CI generation workflow
- Versioned rollback

## 500-model NPC architecture

The 500-model council is a specialist training/evaluation pool. Runtime worlds use lightweight NPC policies/agents and route expensive model inference only when needed, allowing large NPC populations without requiring one heavyweight model process per character.

NPCs have role, skills, goals, personality, scoped memory, tools, safety policy, model policy, observation/action contracts, inference budgets and deterministic fallback paths. Cross-user NPC memory is isolated by default.

## Design IR

`design-ir.ts` is the machine-readable boundary between Buddy generation and the runtime. It is engine-neutral so multiple runtimes can be evaluated behind the same contract.

## World streaming

`world-streaming.ts` provides deterministic chunk identity and validation for load/unload policies. Production work must add authoritative storage, interest management, streaming transport, asset caching and recovery.

## Benchmark ladder

1. Small playable game
2. 3D environment
3. NPC simulation
4. Educational game
5. Construction/interior editing
6. Persistent economy
7. Multiplayer prototype
8. Persistent world
9. Streaming open world
10. Full educational simulation

Every level requires reproducible build, runtime, security and regression evidence before being marked complete.

## Safety

Security testing is authorization-first. Generated games must not attack third-party systems. Model self-improvement remains sandboxed, evaluated and reversible. Secrets are excluded from prompts, logs and NPC memory by default.
