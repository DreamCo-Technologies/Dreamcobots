# Buddy Actions — 10-Action Unified Control Plane

Goal: expose the entire capability catalog through exactly 10 stable Actions-page entry points. Capabilities remain internal, composable routes rather than thousands of UI buttons.

## The ten actions

1. `full_system_audit` — inventory capabilities, bots, workflows, dependencies, routes, health, and ownership.
2. `reasoning_health_check` — exercise reasoning families, verification, calibration, and model/provider health.
3. `connectivity_audit` — prove each capability has a discoverable registry entry, router path, handler, dependency set, and observable result path.
4. `run_capability_batch` — execute a bounded test/benchmark batch selected from the capability registry.
5. `failure_injection` — safely simulate controlled failures in non-production/test environments and verify detection/recovery.
6. `auto_diagnose` — classify failures, correlate telemetry, identify probable root causes, and produce repair candidates.
7. `regression_sweep` — run previously passing contracts plus targeted regression suites and compare against baselines.
8. `benchmark_buddy` — measure accuracy, calibration, latency, reliability, coverage, and task-specific benchmark outcomes.
9. `self_healing_check` — validate repair/recovery plans in sandbox, verify changes, and report whether promotion is safe.
10. `production_readiness` — aggregate test, benchmark, security, dependency, risk, authorization, observability, and rollback evidence into a readiness decision.

## Common contract

Every action accepts a request ID, optional capability selectors, environment, dry-run/sandbox mode, authorization context, and budget/time limits. Every action returns a structured envelope containing status, evidence, confidence, uncertainty, risk, failures, root-cause candidates, telemetry references, verification results, and next actions.

## Routing contract

```text
Actions Page
  -> Action Registry
  -> Buddy Router
  -> Capability Registry / Graph
  -> selected capability chain
  -> verification + observability
  -> structured result
  -> Actions timeline
```

## Safety rules

- Default execution mode is read-only, dry-run, or sandbox where possible.
- Production side effects require explicit authorization and applicable policy gates.
- Failure injection must never target production by default.
- Self-healing must verify a proposed repair before promotion.
- Every state transition must be observable and attributable to a request ID.
- Failed verification blocks promotion.
- Rollback information must be retained for mutable operations.

## Capability coverage

The ten actions are facades over the full capability graph, including capability batches 1–3000. New capabilities should register against an action category and should not require a new top-level Actions-page button unless a genuine control-plane category is introduced.

## Reliability target

A capability is considered connected only when discovery, routing, execution/test handling, result serialization, telemetry, verification, and regression coverage are all present. Catalog presence alone is not connection proof.
