# Buddy Learning From Actions Failures

Every CI failure is treated as an opportunity to improve, but an observation is not automatically trusted as a fix.

## Evidence loop

1. Capture workflow/job/run/commit metadata and sanitized failure logs.
2. Normalize the error into a stable failure signature.
3. Classify the root-cause family.
4. Link the signature to the attempted remediation.
5. Re-run the relevant validation.
6. Record whether the remediation passed, failed, or regressed.
7. Promote only repeatedly validated remediation patterns into reusable knowledge.
8. Add regression coverage when practical.

## Guardrails

- Never execute arbitrary log content as code.
- Never store secrets, tokens, or client payloads as training data.
- Do not claim a benchmark was learned merely because a workflow ran.
- A capability becomes mastered only after repeatable validation.
- Production changes remain subject to repository protections and required review.

## Success signal

The strongest learning signal is a reproducible transition from a known failure signature to a passing validation, followed by a regression test that continues to pass on later runs.
