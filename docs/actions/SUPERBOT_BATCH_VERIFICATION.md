# Superbot Batch Verification

Every 200-capability batch is validated through the ten Actions rather than receiving new UI controls.

## Required gates

1. **Discovery** — capability and superbot are found in the registry.
2. **Routing** — the Actions router resolves the correct superbot and capability chain.
3. **Contract** — inputs/outputs satisfy the registered schema.
4. **Execution/Test** — bounded execution or deterministic test succeeds in the appropriate environment.
5. **Observability** — logs, metrics and traces are attributable to a request ID.
6. **Verification** — result is independently checked where applicable.
7. **Failure handling** — expected failures are classified and recovery behavior is exercised.
8. **Regression** — existing contracts remain green.
9. **Benchmark** — quality/latency/reliability metrics are captured.
10. **Promotion** — only verified results can be promoted.

## Status model

`UNTESTED`, `DISCOVERED`, `REGISTERED`, `ROUTABLE`, `TESTABLE`, `OBSERVABLE`, `VERIFIED`, `PROMOTED`, `BLOCKED`, `FAILED`.

## Batch accounting

For each 200-capability batch, the Actions page should report counts for every status and list the highest-priority blockers. This lets Buddy work through the catalog systematically without claiming that catalog entries are functioning implementations.

## Safety

Failure injection and self-healing tests run in sandbox/test environments by default. Production changes require the repository's existing governance and authorization gates.
