# Buddy Frontier Competition Program

This program turns frontier competition into an engineering loop: establish a baseline, run fresh/held-out evaluations, identify capability gaps, train or improve the relevant subsystem, rerun validation, and retain regressions as permanent tests.

## Core principle

Buddy does not become frontier-competitive by having a large model/provider catalog. It becomes competitive by demonstrating strong performance on difficult tasks with increasing native capability, reliability, and efficiency.

## Capability flywheel

`baseline -> evaluate -> diagnose -> learn -> implement -> verify -> benchmark -> compare -> retain regression test -> repeat`

## Evidence required for every claimed improvement

- Evaluation task set and version.
- Baseline result.
- New result.
- Whether external models/tools were used.
- Compute/cost and latency measurements when available.
- Failure analysis.
- Regression result against previously mastered capabilities.

## Relationship to external models

The protected DreamCo model fleet and OpenRouter are teachers, specialists, comparison targets, and fallbacks. They remain available while Buddy learns. Successful external-assisted solutions can become candidates for Buddy-native implementation, but promotion requires independent validation.

## Real-world priority

Repository repair, issue resolution, CI recovery, coding, tool use, research, and long-horizon DreamCo tasks are first-class evaluations because they directly measure whether Buddy can improve the system that builds Buddy.
