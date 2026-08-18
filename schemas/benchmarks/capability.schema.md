# Buddy Capability Registry

This is the canonical machine-readable design contract for all 1,000 benchmark targets.

## Registry rules
1. IDs are stable and never reused.
2. A target is a learning source, benchmark, or capability family until validated by execution evidence.
3. Every target must declare prerequisites, learning objectives, tasks, validation, sandbox requirements, remediation, and mastery criteria before it can be promoted.
4. External sources are adapters. Cached/offline packages remain usable when an upstream source is unavailable.
5. Free/local/open execution is the default. Paid routes require explicit authorization.
6. Repository operations are authorization-scoped and sandboxed.

## Required capability record
```yaml
id: stable.capability.id
benchmark_id: 1-1000
category: capability-family
source_ids: []
prerequisites: []
learning_objectives: []
task_ids: []
sandbox_profile: default
mastery:
  threshold: 0.9
  repeated_passes: 3
validation:
  objective: true
  regression: true
  provenance: true
  security: true
  accessibility: true
cost:
  free_first: true
  paid_authorization_required: true
status: discovered
```

## Status promotion
`discovered -> learned -> practiced -> mastered -> production_proven`

No status promotion may occur solely because a model claims success. Evidence must be stored.

## Capability families
- academic knowledge
- software engineering
- repository engineering
- AI/ML
- data
- cloud/infrastructure
- cybersecurity
- government services
- business operations
- finance
- entrepreneurship
- sales/marketing
- human productivity
- education
- science/math
- medicine education
- construction/architecture
- media/books/video
- 3D/design
- games/simulation
- robotics
- autonomous agents
- evaluation/benchmarking
- observability
- security/quality
- deployment
- self-improvement

## Universal task routing
A new task is routed through: understand -> decompose -> identify capabilities -> detect gaps -> research -> select authorized tools -> sandbox -> execute -> validate -> recover -> measure -> explain -> store capability -> regression.

## Evidence requirements
Each benchmark result should preserve task input hash, benchmark version, capability versions, model/provider route, cost, duration, human interventions, test results, source provenance, failure taxonomy, remediation actions and final score.
