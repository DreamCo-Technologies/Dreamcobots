# Buddy Capability Graph v2

The Capability Graph is DreamCo's persistent map of what a bot can do, what it still needs to learn, which sources teach it, which tests prove it, and what failures cause regression.

## Core loop

`goal -> capability graph -> gap ranking -> source selection -> study guide -> practice -> sandbox -> benchmark -> remediation -> transfer -> mastery -> regression monitoring`

## Why this matters

The 1000-source program should not become a giant prompt or a giant knowledge dump. The graph turns source material into reusable training assets and connects them to measurable capabilities.

## Evidence model

A capability can have evidence from:

- independent tasks
- debugging tasks
- novel transfer tasks
- multi-capability integration
- long-horizon tasks
- regression suites
- source provenance
- safety verification

A bot does not receive a permanent mastery label simply because a model produced a convincing explanation.

## Targeted learning

When a bot fails, Buddy identifies the smallest capability/subskill responsible. It then selects the highest-value teacher sources, generates targeted remediation, creates a novel sandbox task, and retests only the affected dimensions before running broader regression checks.

This prevents the expensive pattern of retraining an entire bot for one missing skill.

## Customer isolation

Customer curricula should live in separate namespaces. Customer data must not silently become training material for another customer's bot. Shared DreamCo training assets can only be promoted through the governed/common knowledge path.

## Model independence

The graph stores capability evidence independently from the model that generated it. A model provider can therefore be replaced without losing the curriculum, tests, source mappings, mastery records, or customer training plans.
