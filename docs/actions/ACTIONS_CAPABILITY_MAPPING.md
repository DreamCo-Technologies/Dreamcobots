# Capability-to-Actions Mapping

All capability families use the ten Actions-page facades. This mapping prevents UI explosion while retaining full internal routing.

| Action | Primary capability families |
|---|---|
| `full_system_audit` | all registries, ontology, dependencies, repository, infrastructure, bots, workflows |
| `reasoning_health_check` | logical, symbolic, mathematical, geometric, causal, probabilistic, temporal, spatial, multimodal, scientific, meta-reasoning |
| `connectivity_audit` | capability graph, routing, dependencies, APIs, tools, workflows, observability |
| `run_capability_batch` | any bounded capability/test/benchmark selection |
| `failure_injection` | reliability, recovery, fault simulation, chaos/sandbox testing |
| `auto_diagnose` | telemetry, traces, logs, failure classification, root-cause analysis, dependency analysis |
| `regression_sweep` | tests, contracts, benchmarks, historical failures, previously repaired behavior |
| `benchmark_buddy` | reasoning, coding, geometry, science, planning, memory, multimodal and domain benchmarks |
| `self_healing_check` | repair planning, patch verification, sandbox validation, rollback, recovery |
| `production_readiness` | governance, security, reliability, performance, observability, authorization, rollback |

## Required routing metadata

Each registered capability should declare:
- stable capability ID
- family
- supported action facades
- handler/module
- dependencies
- required inputs
- outputs/schema
- verification method
- benchmark(s)
- telemetry hooks
- failure classifications
- environment restrictions
- authorization level
- rollback strategy when mutable

## Status vocabulary

`CATALOGED` -> `REGISTERED` -> `ROUTABLE` -> `EXECUTABLE/TESTABLE` -> `OBSERVABLE` -> `VERIFIED` -> `PROMOTED`.

A capability cannot be represented as `WORKING` solely because its name exists in a catalog.
