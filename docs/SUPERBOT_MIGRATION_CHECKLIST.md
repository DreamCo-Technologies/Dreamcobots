# Superbot Migration Checklist

Use this checklist for every Division Superbot. The migration is complete only when all required gates are green.

## Discovery

- [ ] Division identity confirmed.
- [ ] All known bot profiles inventoried.
- [ ] All non-bot files with domain ownership identified.
- [ ] Plans, goals and notes collected.
- [ ] Workflows and schedules identified.
- [ ] Tools and connectors identified.
- [ ] UI/API routes identified.
- [ ] Tests and benchmarks identified.
- [ ] Dependencies identified.

## Normalization

- [ ] Duplicate capability names merged.
- [ ] Canonical capability IDs assigned.
- [ ] Capability contracts created.
- [ ] Legacy names recorded as aliases.
- [ ] Provenance recorded for every absorbed artifact.
- [ ] Canonical implementation selected.

## Runtime

- [ ] Division Superbot has one canonical runtime binding.
- [ ] Routing resolves `division + capability`.
- [ ] Legacy routes resolve through compatibility aliases.
- [ ] No duplicate scheduler exists.
- [ ] No duplicate external-write path exists.
- [ ] Failure/recovery behavior is defined.

## Security

- [ ] Permissions reviewed.
- [ ] External writes disabled by default.
- [ ] High-impact actions require fresh approval.
- [ ] Spending limits are explicit.
- [ ] Secrets are externalized.
- [ ] Audit receipt is available.

## Quality

- [ ] Contract tests pass.
- [ ] Unit tests pass.
- [ ] Integration tests pass where applicable.
- [ ] Sandbox side-effect tests pass.
- [ ] E2E routes pass.
- [ ] Observability checks pass.
- [ ] Code Trust passes.

## Commercial

- [ ] Revenue/savings opportunity model defined where applicable.
- [ ] Estimated value separated from realized value.
- [ ] Attribution event defined.
- [ ] Outcome/revenue reconciliation defined.

## Retirement

- [ ] Legacy capability is represented in canonical module.
- [ ] All consumers migrated.
- [ ] Compatibility alias verified.
- [ ] Rollback manifest recorded.
- [ ] Duplicate implementation marked deprecated.
- [ ] Removal approved only after parity.
