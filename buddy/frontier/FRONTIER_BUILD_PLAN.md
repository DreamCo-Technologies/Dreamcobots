# Buddy Frontier Build Plan

## Objective
Build a measurable path from today's orchestration-heavy system toward increasingly native frontier-level capability.

## Capability loop

1. Capture a baseline on a pinned evaluation version.
2. Run the task with the smallest sufficient native/external route.
3. Capture failures, traces, cost, latency, and external assistance.
4. Cluster failures by root cause.
5. Generate bounded learning jobs.
6. Apply a fix, training step, retrieval improvement, tool improvement, routing change, or architecture change.
7. Run the existing regression suite.
8. Run fresh/held-out evaluation tasks.
9. Promote only when held-out, regression, and safety gates pass.
10. Store the evidence and convert the solved failure into a reusable regression case.

## Development priorities

### Phase A — foundation reliability
- Eliminate dependency and syntax failures in CI.
- Make benchmark execution reproducible.
- Make learning/evaluation artifacts auditable.
- Establish private held-out task storage and access controls.

### Phase B — coding autonomy
- Repository indexing and architecture maps.
- Issue clustering and root-cause analysis.
- Sandboxed patch/test loops.
- Automatic regression generation.
- Safe PR generation and verification.

### Phase C — broad capability growth
- Reasoning and mathematics.
- Science/research.
- Tool use and long-horizon planning.
- Long-context memory.
- Multimodal routes where supported.
- Safety and robustness.

### Phase D — native capability migration
- Identify recurring external-model solutions.
- Reproduce the capability locally or in Buddy-native components where feasible.
- Compare native and teacher-assisted performance.
- Migrate only after held-out validation.
- Retain external providers as optional teachers/fallbacks.

### Phase E — frontier evidence
- Run controlled comparisons against strong baselines.
- Use fresh/private tasks to reduce contamination risk.
- Report confidence intervals/variance where applicable.
- Track capability, reliability, cost, latency, and external dependency together.

## Non-negotiable guardrails

- No training on held-out answers.
- No benchmark-specific hardcoding to manufacture scores.
- No disabling tests to increase throughput.
- No automatic destructive production actions from an unverified learning job.
- No secret credentials in learning artifacts.
- No deletion of the protected original DreamCo model catalog.
