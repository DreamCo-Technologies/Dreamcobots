# Buddy AGI-Style Repair Architecture

## Purpose

Make Buddy's repair system behave like a highly capable general problem-solving system: it should reason across the repository, form hypotheses, test them, use tools deliberately, learn from outcomes, and know when it does not know.

**Important:** this architecture does not claim that Buddy is AGI. "AGI-style" describes the engineering behaviors we want to reproduce and measure.

## Core loop

```text
OBSERVE
  -> BUILD WORLD MODEL
  -> IDENTIFY GOAL / CONSTRAINTS
  -> GENERATE HYPOTHESES
  -> RANK HYPOTHESES
  -> CHOOSE LOWEST-RISK INFORMATION-GAINING ACTION
  -> SANDBOX / REPRODUCE
  -> ACT
  -> MEASURE
  -> UPDATE BELIEFS
  -> VERIFY
  -> GENERALIZE
  -> STORE LESSON
  -> PLAN NEXT ACTION
```

## 1. Persistent system model

Buddy maintains a machine-readable graph of:

- repositories/files/modules;
- workflows/jobs/actions;
- Issues/Actions/Agents;
- dependencies and integrations;
- tests and benchmarks;
- deployments/environments;
- capabilities and owners;
- known failures and repair history;
- evidence freshness;
- user-approved constraints.

The model is evidence-backed. Unknown relationships remain unknown rather than invented.

## 2. Goal decomposition

Convert a broad request such as **"make everything green"** into measurable subgoals:

`goal -> capabilities -> dependencies -> tests -> repairs -> verification gates`

Each subgoal gets a definition of done and a dependency-aware priority.

## 3. Hypothesis engine

For each failure, Buddy should maintain multiple plausible causes when evidence is ambiguous.

Example:

```text
Failure: workflow cannot start

H1: missing dependency       0.42
H2: runtime mismatch         0.31
H3: permission/config issue  0.19
H4: transient service issue  0.08
```

Probabilities are working estimates, not facts. New evidence updates the ranking.

## 4. Active diagnosis

Do not run every possible test blindly.

Choose the next safe action that is expected to reduce uncertainty most while minimizing:

- risk;
- cost;
- runtime;
- blast radius;
- user disruption.

## 5. Multi-agent debate

Specialists can independently analyze the same incident:

- architecture;
- security;
- testing;
- performance;
- reliability;
- product/user experience;
- domain specialist.

The Council compares evidence, disagreements and confidence. A vote is not a substitute for executable proof.

## 6. Repair planning

Repairs are generated as small, reversible steps:

1. reproduce;
2. isolate;
3. patch;
4. targeted test;
5. dependent regression test;
6. broader certification;
7. canary if required;
8. verify;
9. record lesson.

## 7. Tool selection

Buddy selects tools based on task requirements rather than agent identity.

Examples:

- repository search for code relationships;
- workflow evidence for CI failures;
- sandbox for risky execution;
- benchmarks for capability claims;
- browser smoke tests for user-facing behavior;
- security scanners for trust gates.

## 8. Memory with provenance

Every learned repair pattern records:

- original evidence;
- environment/version;
- action taken;
- result;
- confidence;
- regression outcome;
- source incident;
- expiration/revalidation condition.

A lesson is not promoted to a reusable strategy solely because one repair succeeded.

## 9. Transfer learning across failures

When a new failure resembles historical incidents, Buddy can propose a known strategy but must verify applicability before applying it.

```text
similarity -> retrieve strategy -> check prerequisites -> reproduce -> apply -> verify
```

## 10. Self-evaluation

After each repair Buddy asks:

- Did the original goal pass?
- Did the fix introduce regressions?
- Did cost/runtime improve or worsen?
- Is the strategy reusable?
- Was confidence calibrated?
- What evidence was missing?

## 11. Uncertainty and humility

Buddy must have an explicit **I don't know** state.

Low-confidence or conflicting evidence triggers:

`more evidence -> specialist review -> Council -> human escalation`

Never manufacture certainty to make the dashboard green.

## 12. Safety boundaries

AGI-style behavior must not become unrestricted autonomy.

Consequential actions require policy gates appropriate to risk. Never:

- expose secrets;
- destroy user work without authorization;
- disable security gates to pass certification;
- alter tests solely to hide regressions;
- silently deploy high-risk changes;
- train on data without required user authorization.

## 13. Intelligence scorecard

Measure the repair system itself:

- first-pass diagnosis accuracy;
- root-cause accuracy;
- repair success rate;
- regression rate;
- time to verified repair;
- unnecessary-action rate;
- cost per successful repair;
- uncertainty calibration;
- transfer success rate;
- human escalation rate;
- recurrence rate after repair.

## 14. End state

The goal is not a bot that simply says **"I fixed it."**

The goal is a system that can explain:

> **What is wrong → what I believe is causing it → what evidence supports that belief → what I tried → why I chose that action → what changed → what passed → what failed → what I learned → what I recommend next.**

That is the standard for Buddy's AGI-style repair system.
