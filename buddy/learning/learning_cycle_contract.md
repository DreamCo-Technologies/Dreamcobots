# Buddy Learning Cycle Contract

This contract defines what counts as a real learning cycle.

1. **Observe** — capture a benchmark, issue, CI recovery, tool outcome, external-model assist, or approved correction.
2. **Baseline** — preserve the original result before intervention.
3. **Intervene** — apply a bounded change, retrieval strategy, prompt/tool strategy, adapter, or registered trainer.
4. **Verify** — rerun the same capability with independent evidence.
5. **Regression** — run related previously-passing tests.
6. **Hold-out** — evaluate on data not used by the intervention.
7. **Safety** — confirm the change does not introduce prohibited behavior or secret leakage.
8. **Promote** — only verified improvements become mastered capabilities.
9. **Record** — store evidence, provenance, cost, latency, external assistance, and the capability delta.
10. **Reuse** — make the verified lesson available to future tasks.

## External models

The original DreamCo model catalog remains intact. OpenRouter and other providers are complementary teachers/specialists/fallbacks. Their successful outputs are evidence for capability acquisition, not proof that Buddy has mastered the capability.

## Efficiency target

Minimize external inference over time by increasing verified native solve rate, reusing successful lessons, deduplicating learning work, caching deterministic artifacts, and routing only to the smallest sufficient capability.

## Failure behavior

If evidence is incomplete, mark the result `unverified` rather than green. If a regression or safety gate fails, do not promote. Preserve the failed attempt as learning evidence and create a follow-up regression candidate.
