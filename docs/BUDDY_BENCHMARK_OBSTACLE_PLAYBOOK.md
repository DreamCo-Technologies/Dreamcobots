# Buddy Benchmark Obstacle Playbook

## Purpose

Make benchmark failure useful. A failed benchmark should automatically become a diagnosis and learning opportunity rather than a dead end.

## Failure-to-learning loop

```text
BENCHMARK FAIL
   ↓
CLUSTER ERRORS
   ↓
IDENTIFY SKILL GAP
   ↓
CLASSIFY OBSTACLE
   ↓
GENERATE LEARNING OPTIONS
   ↓
SELECT LOWEST-COST HIGH-VALUE EXPERIMENT
   ↓
PRACTICE
   ↓
RETEST
   ↓
REGRESSION
   ↓
TRANSFER TEST
   ↓
PROMOTE / ITERATE / ESCALATE
```

## Obstacle taxonomy

### Knowledge gap
Buddy lacks necessary factual/procedural information.

Possible response: retrieve trusted sources, build structured knowledge, create targeted practice.

### Reasoning gap
Buddy has relevant information but reaches the wrong conclusion.

Possible response: create contrastive examples, decomposition tasks, counterexample tests and independent verification.

### Planning gap
Buddy understands the task but chooses poor steps.

Possible response: compare plans, score expected risk/information gain, simulate before acting.

### Tool-use gap
Buddy chooses or uses tools poorly.

Possible response: tool-selection experiments, tool documentation retrieval, sandbox practice and outcome tracking.

### Context gap
Solution works in one environment but fails in another.

Possible response: add environment-aware tests and explicit prerequisites.

### Implementation gap
The reasoning is correct but code/execution is wrong.

Possible response: minimal reproduction, targeted coding exercise, patch, regression suite.

### Data-quality gap
Learning material is noisy, stale, duplicated or contradictory.

Possible response: provenance scoring, deduplication, corroboration and source refresh.

### Evaluation gap
The benchmark does not measure the intended capability correctly.

Possible response: audit benchmark validity; never simply lower the threshold to pass.

### Generalization gap
Buddy passes familiar examples but fails novel variants.

Possible response: holdout examples, adversarial variants, distribution shifts and transfer tests.

### Safety gap
A proposed solution works but violates policy or creates unacceptable risk.

Possible response: reject, isolate, redesign and add a safety regression.

## Example: bug repair

```text
CI failure
 -> compare current vs known-good
 -> reproduce minimal failure
 -> inspect dependency/runtime evidence
 -> form 3 candidate causes
 -> run cheapest discriminating test
 -> eliminate two hypotheses
 -> patch smallest affected component
 -> run original test
 -> run dependent tests
 -> run security check
 -> benchmark affected capability
 -> store validated repair pattern
```

## Example: benchmark failure

If a coding benchmark falls below target:

1. cluster failures by concept;
2. distinguish syntax, API knowledge, planning and reasoning errors;
3. retrieve relevant permitted documentation;
4. generate exercises focused on the weakest cluster;
5. include unseen variants;
6. practice in sandbox;
7. retest;
8. regression-test previously strong skills;
9. transfer-test on a new task;
10. only then update the skill score.

## Strategy selection

Each candidate learning intervention can be evaluated on:

`expected improvement / (cost + risk + time)`

This is a planning heuristic, not a claim of guaranteed optimization.

## Stopping rules

Buddy should stop experimenting when:

- the benchmark passes with sufficient margin;
- transfer tests pass;
- regression tests remain healthy;
- additional experiments have low expected value;
- budget/time limits are reached;
- safety uncertainty remains unresolved.

At that point it should report the remaining uncertainty instead of endlessly changing itself.

## Best-system principle

The strongest learner is not the one that consumes the most data. It is the one that can determine:

**what it needs to learn, why it failed, which evidence matters, what experiment will discriminate between explanations, how to practice, whether improvement generalizes, and when it is safe to remember the lesson.**
