# Buddy Agent Selection Score

Buddy should choose agents per step using evidence rather than a fixed agent list.

## Selection inputs

For every candidate agent/tool/model, evaluate:

- task-skill match
- benchmark performance on the exact task family
- recent reliability
- correctness
- speed/latency
- tool availability
- repository familiarity
- context requirements
- cost/resource budget
- safety/permission requirements
- integration compatibility
- recent failure/regression history

## Routing score

The orchestrator should produce an auditable ranking and select the highest-evidence candidate that satisfies hard constraints. Exact weights may vary by task.

Hard constraints should be checked first (required capability, permissions, compatibility, safety). Soft ranking follows with quality/correctness, reliability, speed, cost and other task-relevant evidence.

## Per-step selection

Do not choose one model/agent for an entire job merely because it was selected at the beginning. Re-evaluate at meaningful task boundaries when the next step has different requirements.

Example:

`planner → repository explorer → architect → coder → test engineer → security reviewer → performance reviewer → release engineer`

A small task may use only one specialist. A complex task may use many.

## Verification

Record:

- candidates considered
- selected agent
- reason
- evidence used
- task result
- fallback used, if any
- benchmark impact

This lets Buddy learn which agents are actually best for each class of work.

## Guardrail

A higher score is a recommendation, not permission. Consequential actions still follow user approval and repository policy.
