# Buddy Capability Lifecycle

Every major Buddy capability follows the same lifecycle so the system grows deliberately.

1. **Need** — define the user problem and success criteria.
2. **Plan** — choose specialist agents, tools, data and dependencies.
3. **Sandbox** — execute against safe fixtures or isolated resources.
4. **Measure** — score correctness, quality, latency, cost, safety and usability as applicable.
5. **Review** — compare against baseline and inspect failures.
6. **Promote** — only move forward when thresholds are met.
7. **Monitor** — continuously collect production evidence.
8. **Regress** — automatically detect degradation.
9. **Recover** — roll back or disable the affected capability when needed.
10. **Learn** — convert useful failures and successes into tests, documentation and training examples.

## Specialist routing

A task can use multiple specialist agents. Buddy should select agents based on the task's required capabilities rather than using the same agent for everything. The final coordinator must reconcile outputs, identify disagreement, and preserve evidence for the user.

## Promotion evidence

A capability promotion record should contain:

- benchmark name/version
- baseline
- model/agent configuration
- tool configuration
- test set identifier
- sample count
- correctness/quality score
- latency distribution
- cost where measurable
- safety results
- failures and known limitations
- reviewer/approval state
- rollback target

## No silent escalation

New permissions, spending authority, external communications, deployments, merges, device control or other consequential authority must not appear simply because a benchmark improved. Capability and authority are separate dimensions.
