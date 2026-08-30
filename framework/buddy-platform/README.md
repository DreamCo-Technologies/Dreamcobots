# Buddy Platform Foundation

This package is the executable foundation for the approved DreamCo/Buddy direction. It intentionally implements deterministic contracts and orchestration boundaries first; production integrations (databases, game engines, identity, cloud execution, payments and external security scanners) must be connected behind these interfaces and independently verified.

## Modules

- `types.ts` — shared domain contracts.
- `learning.ts` — courses, objectives, assessments and mastery planning.
- `teacher-studio.ts` — natural-language teacher request to game/course specification.
- `trust-lab.ts` — model evaluation plans and evidence records.
- `model-council.ts` — 500-model specialization, weighted review and quorum decisions.
- `security.ts` — authorization-first security assessment lifecycle.
- `game-benchmark.ts` — progressive complex-game capability benchmark.
- `build-pipeline.ts` — plan/generate/test/review/PR/CI/deploy lifecycle with explicit gates.

No module performs an external attack, deploy, payment, secret access, or unrestricted self-modification.