# Automatic New-Bot Division Routing

## Goal

Every new bot added to DreamCo should automatically be classified into the correct one of the 46 canonical divisions and registered under that division's Superbot. Creating a new bot must not create an orphan or bypass the capability registry.

## Required intake

A new bot should declare, when possible:

- `name`
- `purpose`
- `primary_domain`
- `capabilities`
- `tools`
- `inputs`
- `outputs`
- `dependencies`
- `risk_level`
- `expected_outcomes`

If metadata is missing, the classifier may infer candidates from repository structure and source content, but the result must retain confidence/evidence.

## Routing pipeline

```text
NEW BOT / BOT UPDATE
        ↓
INTAKE
        ↓
DUPLICATE / CAPABILITY SEARCH
        ↓
DOMAIN CLASSIFICATION
        ↓
46-DIVISION MATCH
        ↓
SUPERBOT ASSIGNMENT
        ↓
CAPABILITY REGISTRATION
        ↓
DEPENDENCY / POLICY CHECK
        ↓
TEST + HEALTH CHECK
        ↓
AVAILABLE TO BUDDY
```

## Classification strategy

Use multiple signals:

1. explicit declared domain;
2. directory/location metadata;
3. bot name and description;
4. capabilities and tools;
5. imported modules/dependencies;
6. workflow targets;
7. existing capability similarity;
8. division-specific evaluation/tests.

No single weak signal should silently determine an ambiguous assignment.

## Duplicate prevention

Before registering a new bot, search for an equivalent capability. If an equivalent exists, prefer:

- extending the existing worker;
- composing existing capabilities;
- versioning the capability;
- creating an alias;

rather than creating another duplicate bot.

## Ambiguous routing

If confidence is below the configured threshold, register the bot as `unresolved` and create a classification review item. It remains visible and cannot silently disappear into an arbitrary division.

## Reclassification

A bot can move divisions when evidence changes. Preserve historical assignments and migration lineage.

## Buddy integration

Once registered, Buddy should discover the bot through the capability registry rather than requiring hard-coded knowledge of the bot's file path.
