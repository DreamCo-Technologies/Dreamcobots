# Buddy Autonomy Levels and Gates

## Purpose

Give Buddy a measurable path from assistant to increasingly capable engineering automation without granting unrestricted control.

## Levels

### A0 — Observe
Reads evidence and reports status.

Allowed: read-only repository/workflow/monitoring evidence.

Gate to A1: accurate status mapping and no false-green findings.

### A1 — Diagnose
Forms hypotheses and selects safe diagnostic tests.

Allowed: bounded read-only diagnostics and sandbox reproduction.

Gate to A2: diagnosis accuracy and confidence calibration meet configured thresholds.

### A2 — Repair Low Risk
Applies reversible, low-blast-radius repairs through approved runners.

Gate: repair success, regression rate and rollback readiness.

### A3 — Coordinated Repair
Coordinates multiple specialists and verification paths.

Gate: reliable cross-system incident handling and correct escalation.

### A4 — Gated Production Automation
Can execute defined production changes when policy permits.

Gate: security, approval, canary, monitoring and rollback controls.

### A5 — Adaptive Engineering
Can propose improvements to its own repair strategies and optimize tool/model routing from measured outcomes.

Gate: sustained improvements without unacceptable safety, reliability, cost or user-impact regressions.

## Universal gates

Every level preserves:

- least privilege;
- audit trail;
- evidence-backed status;
- bounded retries;
- rollback where applicable;
- user-data protection;
- secret protection;
- Council/human escalation for high-risk ambiguity.

## Promotion evidence

Promotion requires measured evidence from representative tasks, not a single successful demo.

Track:

- diagnosis accuracy;
- repair success;
- regression rate;
- time to verified repair;
- cost;
- unnecessary actions;
- escalation quality;
- security incidents;
- recurrence.

## Emergency stop

Any high-confidence safety violation, repeated destructive behavior, secret exposure, unexplained production change, or loss of auditability forces a downgrade to the safest previously certified level until reviewed.

## UI representation

The Actions page should show:

`Buddy autonomy: A1 — Diagnose`

along with:

- what Buddy can do;
- what it cannot do;
- what evidence earned the level;
- what is required for the next level.

The level is a capability contract, not a marketing claim about intelligence.
