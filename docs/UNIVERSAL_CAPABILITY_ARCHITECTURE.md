# Universal Capability Architecture

DreamCo's long-term architecture is capability-first and domain-complete.

## Principle

Do not create a new bot merely because a new skill is discovered. First determine whether the skill belongs in an existing canonical capability. A bot or agent should be a composition of capabilities, tools, memory, policy, and execution strategy.

## Domain coverage

The universal taxonomy spans software, research, science, business, creative media, games, robotics, manufacturing, education, government services, accessibility, safety, governance, open source, commerce, and other practical human workflows.

## Capability record

Every important capability should eventually have:

- stable ID
- domain(s)
- description
- originating bot/agent records
- implementation reference
- inputs/outputs
- tools
- dependencies
- benchmark suite
- 0-100 score
- dimension scores
- confidence
- baseline
- target
- gap
- trend
- holdout/transfer results
- regression status
- limitations
- provenance
- security policy
- improvement history

## Composition

```text
User goal
   ↓
Task decomposition
   ↓
Capability selection
   ↓
Tool/model selection
   ↓
Agent composition
   ↓
Sandbox execution
   ↓
Benchmark + holdout + transfer
   ↓
Regression verification
   ↓
Result
   ↓
Evidence + learning
```

## Open-source objective

The architecture should make it easy for contributors to add a capability, prove it with tests and benchmarks, document it, and make it reusable across many agents. Improvements should propagate through shared implementations instead of requiring dozens of bot-specific rewrites.

## Completeness objective

The taxonomy is deliberately broad but not considered complete. Missing domains are expected to be discovered through repository audits, user requests, benchmark gaps, industry research, and developer contributions.
