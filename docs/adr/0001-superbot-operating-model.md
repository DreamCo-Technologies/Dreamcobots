# ADR 0001 — Superbot Operating Model

- Status: Accepted for consolidation branch
- Date: 2026-08-15

## Context

DreamCo has grown into a large ecosystem of divisions, bot profiles, workflows, tools, experiments, notes and product surfaces. The repository's README currently describes 1,051+ bot profiles across 45 divisions, while the owner has identified additional bot material outside the headline count. Continuing to add standalone bots would increase duplicated routing, tests, configuration and operational burden.

## Decision

Every division becomes a canonical **Division Superbot**. Existing specialist bots are migrated into capability modules, workflow modules, tool/connector adapters, evidence records, documentation, or compatibility aliases.

A smaller set of **Cluster Superbots** coordinates related Division Superbots. Cluster Superbots do not duplicate division capabilities.

The governed runtime remains the execution boundary. A capability only receives a dedicated runtime when engineering requirements justify it.

## Non-goals

- Do not delete history merely to make the tree smaller.
- Do not change external behavior without a migration/compatibility path.
- Do not treat a profile count as proof of production capability.
- Do not add another competing orchestration framework.

## Consequences

### Positive
- One canonical implementation per capability.
- Easier testing and observability.
- Clear ownership of tools and workflows.
- Smaller runtime surface.
- Legacy routes can remain compatible.
- Engineers can understand domain boundaries.

### Trade-offs
- Migration requires careful dependency and route analysis.
- Some legacy capabilities will need normalization before merging.
- The repository may temporarily contain old and new representations during migration.

## Migration gate

A legacy implementation can be removed only after capability, dependency, route, permission, observability, revenue-attribution, sandbox/E2E, and rollback parity is demonstrated.
