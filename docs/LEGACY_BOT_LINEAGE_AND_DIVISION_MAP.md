# Legacy Bot Lineage and Division Map

## Goal

Preserve every historical DreamCo bot as an accounted-for capability, worker, alias, retired implementation or unresolved item while consolidating the runtime architecture around 46 Division Superbots and Buddy.

## Canonical hierarchy

```text
Buddy
└── Meta-Orchestrator
    └── 46 Division Superbots
        └── Capability Registry
            └── Legacy Bot Workers / Implementations
```

## No orphan rule

Every discovered legacy bot must receive exactly one primary lifecycle state:

- `active-worker`
- `capability-provider`
- `merged-into-superbot`
- `alias`
- `deprecated`
- `quarantined`
- `unresolved`

Every bot must also have a primary division assignment, even if the assignment is `unresolved` pending review.

## Preserve lineage

Merging must never erase historical identity. The registry should retain:

- legacy bot ID/name;
- original path;
- original division if known;
- canonical division;
- canonical Superbot;
- extracted capabilities;
- tools/integrations;
- workflows;
- dependencies;
- status;
- replacement capability ID;
- migration evidence;
- tests/evaluation evidence;
- last observed commit/version.

## Assignment pipeline

```text
SCAN REPOSITORY
 ↓
INVENTORY EVERY BOT
 ↓
NORMALIZE IDENTITY
 ↓
EXTRACT CAPABILITIES
 ↓
DETECT DUPLICATES
 ↓
CLASSIFY DOMAIN
 ↓
ASSIGN DIVISION
 ↓
MAP TO SUPERBOT
 ↓
PRESERVE LINEAGE
 ↓
MIGRATE / WRAP / RETAIN
 ↓
VERIFY PARITY
 ↓
UPDATE REGISTRY
```

## Confidence

Division assignment should include confidence and evidence. Automated classification may propose assignments, but ambiguous bots remain visible as `unresolved` rather than silently disappearing.

## UI requirement

Buddy's administration/engineering view should be able to show:

- all 46 divisions;
- every known historical bot under its mapped division;
- current lifecycle state;
- replacement Superbot capability;
- dependencies;
- health/evaluation status;
- lineage back to original files.

The user-facing product does not need to expose every implementation detail; the engineering/admin view should.

## Consolidation rule

Do not delete a legacy implementation solely because a Superbot exists. Require capability parity, tests, dependency migration, observability and rollback evidence before removal.
