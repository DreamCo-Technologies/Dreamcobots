# Dynamic Resource-Scaled Fleet Rules

## Non-negotiable architecture rules

1. No fixed maximum number of bots, modules, superbot instances, capabilities, workers, or agents.
2. Numeric counts shown in dashboards are observations, not limits.
3. The historical 1,051 bot set is treated as discovered/reusable module inventory, not a permanent fleet size.
4. Capability counts such as 3,000 are catalog milestones, not ceilings.
5. New resources may be admitted through discovery and registration when authorized.
6. Resource pressure may trigger scale-out, queueing, consolidation, degradation, or scale-down.
7. The router chooses implementations based on capability, health, cost, latency, policy, and available resources.
8. Multiple instances of the same module are permitted when workload and resources justify them.
9. Equivalent modules may be consolidated when consolidation improves reliability or efficiency.
10. Retired modules remain represented in provenance/history but are not active capacity.

## Resource model

The fleet allocator should consider:

- CPU
- GPU/NPU/accelerator capacity
- memory
- storage
- network bandwidth
- model/provider quotas
- API rate limits
- concurrency
- latency budgets
- task priority
- cost budgets
- energy constraints where measurable
- security/authorization boundaries
- environment availability

## Superbot composition

Superbots are not necessarily static. Buddy may compose a superbot from verified modules at request time or maintain reusable compositions when that is more efficient.

A composition should record the exact module versions and capability routes used so the result is reproducible and auditable.

## Actions integration

The ten Actions remain stable:

1. full_system_audit
2. reasoning_health_check
3. connectivity_audit
4. run_capability_batch
5. failure_injection
6. auto_diagnose
7. regression_sweep
8. benchmark_buddy
9. self_healing_check
10. production_readiness

All dynamic fleet changes are observable through these Actions. No additional button is required when fleet capacity changes.

## Growth model

```text
Demand
  + Available Resources
  + Verified Capability Supply
  + Policy
  + Reliability
        ↓
 Dynamic Allocator
        ↓
 Instances / Modules / Superbot Compositions
        ↓
 Buddy Router
        ↓
 Ten Actions
```

## Failure isolation

A failed instance should be quarantined where practical. The allocator may route work to another verified instance or composition. A persistent module failure becomes a diagnostic/repair item rather than a reason to falsify fleet health.

## Measurement

Report both capacity and utilization. Examples:

`active_instances`, `idle_instances`, `queued_tasks`, `available_compute`, `verified_modules`, `degraded_modules`, `quarantined_instances`, `superbot_compositions`.

None of these fields defines a maximum.
