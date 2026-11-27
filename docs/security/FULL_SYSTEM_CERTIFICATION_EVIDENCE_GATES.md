# Full-system certification evidence gate corrections

The full-system receipt must not turn missing evidence into a pass.

This change tightens two checks:

- Runtime connection evidence must have a coherent declared count, unique connection IDs, a matching runtime-verified count, and a probe reference plus timestamp for every `runtime_verified` record. It still allows the core system to be certified with explicitly unverified external connections, but the final fully-connected claim remains false until all declared connections have evidence.
- Work-platform benchmark coverage requires a generated, non-empty backlog whose recorded case count matches the actual case array. A missing work catalog is a blocker, not a successful benchmark state.

The PR workflow now runs full-system certification when these gate definitions, tests, and supporting evidence builders change.

## What this does not prove

A passing certification workflow is commit- and environment-specific. It does not mean every integration is connected or every user workflow is production-safe. Live credentials, production deployment, recovery, observability, user acceptance and external provider probes still require actual evidence.
