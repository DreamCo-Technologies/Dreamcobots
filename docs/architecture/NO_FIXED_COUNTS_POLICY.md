# No Fixed Counts Policy

DreamCo's bot, module, capability, worker, and superbot architecture is resource-driven.

## Policy

- Counts are telemetry, never ceilings.
- Do not add hard-coded maximum fleet sizes.
- Do not require a fixed number of modules per superbot.
- Do not require a fixed number of superbots per domain.
- Do not make the Actions UI grow with fleet size.
- Capacity is constrained by real resources and authorization, not arbitrary counters.

## Runtime behavior

Discovery registers available modules. The allocator selects verified resources based on capability fit, health, cost, latency, concurrency, policy, and available compute. Buddy composes or reuses superbots as needed.

The 10 Actions remain stable control-plane facades regardless of fleet size.

## Testing invariant

CI should fail when production code introduces an arbitrary fleet ceiling or treats a historical inventory count as a maximum.
