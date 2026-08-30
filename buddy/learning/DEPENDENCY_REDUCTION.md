# Buddy Dependency Reduction Plan

Buddy should become increasingly capable without requiring the external model/bot fleet for routine capabilities. This is a capability-replacement program, not a deletion program.

## Lifecycle

1. Keep the original DreamCo model catalog and specialist bots available.
2. Use external models as teachers, evaluators, or fallbacks where appropriate.
3. Capture benchmark failures and successful solutions as sanitized evidence.
4. Implement a native capability.
5. Require repeated native passes, holdout validation, and regression protection.
6. Track native solve rate against comparable benchmark cohorts.
7. Only after evidence-backed parity may routing prefer the native implementation.
8. Retain the external fallback until operational evidence supports retiring it.

## Guardrail

A lower external-call count is not sufficient evidence of learning. Capability quality must remain stable or improve on held-out and regression tests.
