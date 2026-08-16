# Bot → Capability Migration

## Why this exists

DreamCo has bots that may contain hundreds of useful behaviors. Converting a bot into one capability would lose information. The migration must therefore be **lossless first, consolidating second**.

## Rule

> Never throw away a bot's details because we believe another capability already covers them.

A bot can become a **capability bundle** containing dozens or hundreds of atomic capabilities.

## Preservation model

For every bot we preserve:

- identity and aliases
- original location
- division
- purpose
- every documented capability
- sub-capabilities
- workflows
- tasks
- tools
- model dependencies
- API/integration dependencies
- inputs and outputs
- prompts/policies where permitted
- knowledge domains
- memory requirements
- permissions
- strengths
- limitations
- failure modes
- recovery strategies
- benchmarks
- regression tests
- performance/cost/reliability evidence
- provenance and licensing metadata
- relationships to other bots
- migration history

## Capability extraction

Extraction occurs in four passes:

### Pass 1 — Inventory

Capture everything the bot claims or contains.

### Pass 2 — Normalize

Convert names into canonical capability IDs without deleting the original wording or source path.

### Pass 3 — Verify

Separate **documented**, **implemented**, **tested**, and **mastered** capabilities.

### Pass 4 — Compose

Allow capabilities to be shared by multiple bots and composed into Buddy/Superbot workflows.

## Evidence levels

| Level | Meaning |
|---|---|
| Documented | Capability is described somewhere in the repository. |
| Implemented | Code exists that appears to provide it. |
| Tested | Automated tests demonstrate it. |
| Independent | Capability works without teacher intervention on registered tasks. |
| Mastered | Capability passes benchmark, holdout, transfer, and regression criteria. |

This prevents a bot containing 300 claimed capabilities from being incorrectly treated as a bot with 300 proven capabilities.

## Migration safety

- Keep the original bot record.
- Keep original paths and hashes when available.
- Never delete capabilities solely because they look duplicated.
- Mark duplicates as relationships such as `equivalent_to`, `extends`, `depends_on`, or `conflicts_with`.
- Retire only after migration evidence exists.
- Keep retired records queryable for historical reconstruction.

## Target architecture

```text
Bot
 ├── Capability A
 ├── Capability B
 ├── Capability C
 ├── ...
 └── Capability N

Capability
 ├── Tasks
 ├── Tools
 ├── Models
 ├── Dependencies
 ├── Benchmarks
 ├── Tests
 ├── Evidence
 └── Improvement history
```

Buddy can then assemble capabilities dynamically instead of treating the original bot boundary as the permanent architecture.
