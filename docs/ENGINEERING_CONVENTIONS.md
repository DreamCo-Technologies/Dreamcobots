# DreamCo Engineering Conventions

## Naming

- Files: `kebab-case` where practical for new platform files; preserve established conventions inside existing domains.
- TypeScript symbols: `camelCase` functions/variables, `PascalCase` types/classes.
- Python: `snake_case`.
- Capability IDs: `domain.subdomain.outcome`.
- Stable IDs must not depend on display names.

## Ownership

Every production artifact has one owner:

`cluster → division → capability → implementation`.

If two implementations claim the same capability, one becomes canonical and the other becomes a migration candidate.

## Dependencies

Prefer dependency direction:

`product → orchestration → division → capability → adapter → infrastructure`.

Shared infrastructure must not import product-specific code.

## Tests

Each capability should have the smallest useful test pyramid:

1. schema/contract test;
2. unit behavior test;
3. adapter/integration test when an external dependency exists;
4. sandbox side-effect test;
5. E2E route test when user-facing.

## Configuration

Runtime configuration belongs in configuration/environment management, not hard-coded source. Secrets never enter Git.

## Observability

Important operations emit a stable correlation ID and enough structured metadata to answer:

- what happened;
- which Superbot/capability acted;
- what policy applied;
- what dependency was used;
- whether an external side effect occurred;
- what outcome was produced.

## Pull requests

Prefer small coherent migrations. A large structural migration is acceptable only when accompanied by generated inventories, explicit gates, tests, and rollback documentation.

## Refactoring

Do not rename or move code solely to make it prettier if that risks hidden consumers. First establish ownership and contract boundaries; then migrate with compatibility aliases.

## Bot/Superbot rule

Do not create a new standalone bot for a new idea. Add the idea to the capability backlog, assign it to a Division Superbot, and create a capability contract. Dedicated runtime is an exception requiring an engineering justification.
