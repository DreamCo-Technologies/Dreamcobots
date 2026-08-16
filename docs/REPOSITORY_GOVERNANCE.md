# Repository Governance

## Canonical ownership

Every major capability should have one canonical implementation owner, one contract, and one verification path.

Before adding code, search for an existing implementation. If one exists, improve it unless there is a documented architectural reason to replace it.

## Naming

Use descriptive names that communicate responsibility:

- `framework/` for reusable behavior
- `tools/` for deterministic repository operations
- `config/` for policy and registry data
- `tests/` for verification
- `docs/` for human guidance
- `server/` and `client/` for application runtime

Avoid names such as `new`, `final`, `ultimate`, `v2-final`, or `misc` for permanent systems.

## Generated artifacts

Generated artifacts should include enough metadata to identify their source generator and schema version. Never hand-edit generated output when a generator exists.

## Dependency policy

Prefer an existing dependency already used by the repository. New dependencies require a clear benefit, license compatibility, maintenance assessment, and a test that exercises the intended use.

## CI policy

Workflows should have one clear responsibility. A workflow should:

- fail loudly when its prerequisites are missing
- expose useful logs
- use bounded retries
- avoid infinite loops
- avoid duplicate work already owned by another workflow
- preserve artifacts needed for diagnosis

Scheduled autonomy must be bounded by time, cost, permissions, and concurrency limits.

## AI capability policy

A model response, catalog entry, or configuration record is not evidence of a working capability. Capabilities require executable tests and, where appropriate, independent benchmark or holdout evidence.

## Security and data policy

Secrets belong in approved secret stores. Do not commit credentials. External sources are research inputs and must retain provenance and applicable rights metadata. Commercial packages require a publication gate.

## Review checklist

Before merging, reviewers should ask:

- Is this the canonical owner?
- Is there a regression test?
- Is the change observable?
- Can it be rolled back?
- Does it introduce duplicated logic?
- Does it create an unnecessary new dependency?
- Does it weaken an existing security or governance control?
- Does the documentation explain the new boundary?

## Architectural quality bar

The repository should become more understandable after every substantial change. Refactor adjacent duplication when practical, but keep changes focused enough that reviewers can verify them.
