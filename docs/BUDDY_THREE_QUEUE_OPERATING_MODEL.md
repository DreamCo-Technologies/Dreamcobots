# Buddy Three-Queue Operating Model

## Purpose

Keep Buddy's three core operational sections organized while using one shared reliability engine:

1. **Issues** — product bugs, feature requests, user reports, technical debt.
2. **Actions** — CI/CD workflow and automation failures.
3. **Agents** — Buddy/agent execution failures, tool failures, model failures and behavioral regressions.

The three queues remain visibly separate for humans, but share the same underlying incident lifecycle, evidence model, priority system, repair engine and Council gates.

## One control plane, three clear views

```text
                    BUDDY CONTROL PLANE
                           |
          +----------------+----------------+
          |                |                |
       ISSUES           ACTIONS          AGENTS
          |                |                |
          +----------------+----------------+
                           |
                Unified Repair Engine
                           |
       Intake -> Dedup -> Classify -> Reproduce
          -> Repair -> Test -> Council -> Deploy
          -> Verify -> Monitor -> Close/Reopen
```

## Section contracts

### 1. Issues

Use for human-facing work and product/system problems.

Required fields:
- issue_id
- title
- source
- severity
- priority
- component
- owner
- status
- duplicate_group
- reproduction
- related_action_runs
- related_agent_runs
- linked_changes
- council_status
- verification_evidence
- next_action

Statuses:
`new -> triaged -> queued -> reproducing -> building -> testing -> council -> ready -> deployed -> verified -> closed`

Failure/regression transition:
`closed -> reopened -> triaged`

### 2. Actions

Use for automation and CI/CD failures.

Required fields:
- run_id
- workflow
- job
- step
- commit
- branch
- failure_fingerprint
- first_seen
- last_seen
- occurrence_count
- related_issues
- attempted_repairs
- current_status
- verification_evidence

Statuses:
`detected -> grouped -> triaged -> reproducing -> repairing -> testing -> verified -> monitoring -> resolved`

A transient retry is **not** a repair. The failure must be reproduced or otherwise explained and regression-protected before resolution.

### 3. Agents

Use for agent execution health and AI behavior.

Required fields:
- agent_run_id
- agent_name
- task_class
- model_route
- tool_chain
- failure_class
- confidence
- latency
- cost_metadata
- related_issues
- related_action_runs
- attempted_repairs
- council_status
- outcome

Failure classes:
`model -> tool -> code -> data -> policy -> permission -> environment -> integration -> unknown`

Statuses:
`started -> running -> evaluating -> retryable -> repairing -> council -> escalated -> verified -> learned`

## Shared priority

Priority should consider:

`security > data loss > production outage > widespread regression > repeated automation failure > user blocker > correctness defect > performance > developer experience > enhancement`

Tie breakers:
1. affected users
2. recurrence
3. blast radius
4. dependency centrality
5. age
6. repair confidence
7. cost

## Deduplication

The system must link related records instead of creating parallel work.

Examples:

- one failing Action creates or links to one canonical incident;
- five agents reporting the same integration failure share one incident;
- multiple user issues with the same root cause form a duplicate group;
- one repair can resolve every linked record when verification proves the root cause was shared.

## Council integration

The Council receives the same evidence package regardless of queue:

- reproduction evidence
- proposed change
- tests
- regression tests
- security findings
- architecture impact
- performance impact
- compliance impact
- cost impact
- rollback plan
- confidence

No agent can mark its own production change as certified.

## User experience

The UI should keep the three sections visually distinct:

### Issues
**What needs to be fixed or built?**

### Actions
**What automation failed?**

### Agents
**What did Buddy or an agent fail to accomplish?**

A shared **Health** view may summarize all three, but it must preserve the source category and allow drilling back to the canonical record.

## Automatic organization rules

- newest failures enter the correct queue automatically;
- severity and ownership are assigned deterministically where possible;
- duplicates are linked;
- stale records are surfaced;
- blocked records explain exactly what is blocking them;
- closed records reopen on verified regression;
- completed records retain evidence;
- unresolved records remain visible;
- no queue is allowed to silently discard failures.

## Anti-bot-sprawl rule

Do not create a new bot for every failure type. Prefer shared services:

- Unified Intake
- Incident Fingerprinting
- Priority Engine
- Reproduction Engine
- Repair Engine
- Test/Regression Engine
- Council Gateway
- Deployment Gate
- Verification Engine
- Learning/Knowledge Engine

Specialized agents can plug into these services without becoming separate uncontrolled systems.

## Beginner mode

Beginners should never need to understand the three internal queues. Buddy can show:

**Needs attention**

with a plain-language explanation and one recommended action.

Advanced mode exposes Issues, Actions and Agents separately with logs, traces, diffs and technical controls.

## Required dashboard metrics

- open Issues
- failing Actions
- unhealthy Agents
- critical incidents
- auto-repair success rate
- regression rate
- human escalations
- mean time to detect
- mean time to repair
- mean time to recover
- repeated failure rate
- Council rejection rate
- unresolved blockers
- stale records

## Definition of done

A failure can enter through any of the three sections and receive the same quality of treatment: detection, classification, deduplication, reproduction, safe repair, testing, Council review when required, deployment, verification, monitoring, and evidence-backed closure.
