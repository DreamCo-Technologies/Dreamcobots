# Buddy Automatic Bot Onboarding

## Objective

Make new DreamCo bots immediately discoverable by Buddy while preserving the 46-division architecture and preventing duplicate or orphan implementations.

## Lifecycle

```text
CREATE / UPDATE BOT
        ↓
DISCOVER METADATA
        ↓
IDENTITY + LINEAGE
        ↓
DUPLICATE CHECK
        ↓
CLASSIFY DIVISION
        ↓
ASSIGN SUPERBOT
        ↓
REGISTER CAPABILITIES
        ↓
RUN POLICY / SECURITY / TESTS
        ↓
HEALTH CHECK
        ↓
PUBLISH TO CAPABILITY REGISTRY
        ↓
BUDDY DISCOVERS IT
```

## New-bot contract

A bot should expose machine-readable metadata whenever practical:

```yaml
name: example_bot
purpose: concise purpose
primary_domain: division-domain
capabilities:
  - capability.id
inputs: []
outputs: []
tools: []
dependencies: []
risk_level: low
owner: division
```

The platform may infer missing metadata, but inferred values retain confidence and evidence.

## Automatic placement

The classifier compares the bot against the canonical 46 divisions and existing capabilities. A high-confidence match is assigned automatically. Ambiguous matches become review items while remaining visible.

## Buddy visibility

Buddy should discover bots through the registry rather than scanning arbitrary paths at runtime. The registry becomes the source of truth for available capabilities.

## Updates

Changes to a bot trigger re-evaluation when they alter purpose, tools, dependencies, permissions, interfaces or capabilities. Historical assignments remain in lineage records.

## Reliability

New bots enter a measured lifecycle rather than immediately becoming trusted:

`candidate → validated → active → degraded → quarantined → recovered/retired`

## Consolidation

If a new bot duplicates an existing capability, the system should recommend extension/composition rather than adding another standalone capability.
