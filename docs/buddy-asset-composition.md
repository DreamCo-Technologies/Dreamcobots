# Buddy Asset Composition

Buddy can build a proposed capability from verified digital assets without executing it.

A composition records the task, selected assets, transitive dependencies, estimated utility, estimated risk, lifecycle warnings, and a `simulation_only` flag.

This is the bridge between the asset graph and future digital-twin/simulation infrastructure:

`task -> capability search -> candidate assets -> dependency closure -> composition -> simulation -> decision engine -> policy -> approval -> execution`

The composition engine intentionally has no external side effects. A future executor must enforce authorization separately.
