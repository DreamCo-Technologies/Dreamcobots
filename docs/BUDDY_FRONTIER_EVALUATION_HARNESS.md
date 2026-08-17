# Buddy Frontier Evaluation Harness

## Purpose

Measure whether Buddy is actually improving across reasoning, execution, reliability and governance instead of equating more automation with intelligence.

## Evaluation dimensions

- goal understanding;
- planning quality;
- tool selection;
- capability routing;
- multi-step execution;
- verification accuracy;
- recovery quality;
- latency;
- resource cost;
- factual reliability;
- provenance quality;
- permission correctness;
- safety/governance compliance;
- cross-division transfer;
- regression resistance;
- human decision quality;
- measurable task outcomes.

## Evaluation loop

```text
TASK SET
 ↓
BASELINE
 ↓
RUN CANDIDATE
 ↓
COLLECT TRACE + EVIDENCE
 ↓
SCORE
 ↓
COMPARE
 ↓
FAILURE ANALYSIS
 ↓
BOOTCAMP GAIN
 ↓
REPLAY / REGRESSION
```

## Test classes

1. deterministic unit tests;
2. integration tests;
3. sandbox scenarios;
4. adversarial/error-recovery scenarios;
5. long-horizon missions;
6. cross-division capability-transfer tests;
7. device-routing tests;
8. governance boundary tests;
9. production shadow evaluations;
10. canary evaluations.

## Score design

Do not reduce all behavior to one intelligence score. Maintain a vector of measurements and expose tradeoffs such as quality vs latency, autonomy vs approval burden, and capability vs risk.

## Golden tasks

Maintain a versioned set of representative tasks with expected outcomes and acceptable ranges. When a task changes, preserve the prior version for historical comparison.

## Regression gate

A new capability should not be promoted solely because it improves one benchmark. Check critical regressions, governance violations and reliability degradation before promotion.

## Evidence

Every score should link to the task version, run, trace, artifacts, model/tool configuration and source lineage needed to reproduce the result.
