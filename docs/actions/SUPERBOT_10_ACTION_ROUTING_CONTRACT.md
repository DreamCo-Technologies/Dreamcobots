# Superbot → Actions 10-Action Routing Contract

## Objective

Expose all DreamCo superbots through the same ten Actions-page controls. Superbots are execution/orchestration domains; they do not create additional top-level UI buttons.

## Routing matrix

| Action | Superbot responsibility |
|---|---|
| `full_system_audit` | enumerate superbot registry, capabilities, dependencies, health and ownership |
| `reasoning_health_check` | exercise each superbot's supported reasoning families and verification paths |
| `connectivity_audit` | verify registry → router → superbot → capability → result → telemetry connectivity |
| `run_capability_batch` | execute bounded tests through the appropriate superbot |
| `failure_injection` | safely exercise superbot fault/recovery behavior in sandbox/test environments |
| `auto_diagnose` | correlate superbot errors, traces, dependencies and failure classes |
| `regression_sweep` | replay contracts and previously repaired superbot behavior |
| `benchmark_buddy` | benchmark superbot outcomes and aggregate them into Buddy metrics |
| `self_healing_check` | validate proposed repairs/recovery plans before promotion |
| `production_readiness` | aggregate superbot health, security, tests, risk, authorization and rollback evidence |

## Superbot contract

Every superbot registered with Buddy should expose:

- `superbot_id`
- `display_name`
- `domain`
- `capability_ids`
- `supported_actions`
- `dependencies`
- `input_schema`
- `output_schema`
- `health_check`
- `verification_strategy`
- `benchmark_suite`
- `telemetry_hooks`
- `failure_classes`
- `environment_policy`
- `authorization_policy`
- `rollback_strategy`
- `version`

## Health states

`DISCOVERED` → `REGISTERED` → `ROUTABLE` → `TESTABLE` → `OBSERVABLE` → `VERIFIED` → `PROMOTED`.

A superbot must not be reported as healthy merely because its registry entry exists.

## Result envelope

Every route returns a common structured result containing:

- request ID
- action ID
- superbot ID
- capability IDs used
- status
- evidence
- confidence
- uncertainty
- risk
- failures
- root-cause candidates
- verification results
- telemetry references
- repair candidates
- rollback information
- timestamp/version

## Reliability invariant

No superbot may bypass the existing verification, governance, observability, and authorization layers. The ten Actions are stable facades; internal routing may evolve without changing the Actions-page contract.
