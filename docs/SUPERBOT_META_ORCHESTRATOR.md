# Superbot Meta-Orchestrator

## Purpose

Coordinate Division Superbots when a goal crosses multiple domains. The meta-orchestrator is a coordinator, not a replacement for domain ownership.

## Goal decomposition

```text
USER GOAL
  ↓
INTENT + CONSTRAINTS
  ↓
CAPABILITY GRAPH
  ↓
DIVISION ROUTING
  ↓
PARALLEL / SEQUENTIAL PLAN
  ↓
EXECUTION
  ↓
CROSS-DIVISION VERIFICATION
  ↓
SYNTHESIS
  ↓
OUTCOME
```

## Capability graph

Represent a complex goal as nodes and dependencies:

- goal;
- subgoal;
- capability;
- tool;
- data source;
- policy gate;
- verification step;
- expected outcome.

The graph allows independent work to run in parallel and dependent work to wait for prerequisites.

## Collective intelligence

Superbots should be able to:

- ask another division for a capability;
- challenge an assumption;
- request verification;
- provide evidence;
- negotiate task ownership;
- merge compatible plans;
- escalate unresolved conflicts.

## Disagreement protocol

When Superbots disagree:

1. identify the exact claim or decision;
2. expose evidence and provenance;
3. compare confidence and source quality;
4. run a targeted verification task if possible;
5. apply domain policy;
6. escalate when the conflict remains material.

A majority vote is not proof of correctness.

## Resource optimization

The orchestrator should select plans based on:

- expected outcome quality;
- latency;
- cost;
- reliability;
- required permissions;
- reversibility;
- evidence quality.

## Safety

The orchestrator cannot increase a child capability's permissions. Policy evaluation remains authoritative at the point of side effect.

## Learning

After a completed multi-division task, store:

- plan;
- participating capabilities;
- tool selections;
- failures/recoveries;
- verification results;
- outcome;
- user feedback;
- cost/latency;
- reusable strategy.

Successful patterns become candidates for future planning only after validation.
