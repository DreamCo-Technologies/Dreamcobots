# Buddy Continuous Learning Policy

Buddy should learn continuously throughout the day, not only during the daily repository scan.

## Event sources
- benchmark results
- verified issue repairs
- CI failures and recoveries
- code-review feedback
- tool-call outcomes
- external-model assistance
- OpenRouter/provider outcomes
- user-approved corrections
- production telemetry that is privacy-safe and authorized

## Continuous loop

`observe -> normalize -> fingerprint -> retrieve -> attempt -> verify -> compare -> learn -> regression-test -> measure -> repeat`

## Learning gates

A single successful response is not mastery. A lesson becomes mastered only after independent validation and relevant regression/safety checks. Held-out evaluation data must never be used for training.

## External-model distillation

External models are optional teachers/specialists/fallbacks. Record what capability was missing, what solution was obtained, and what evidence validated it. A candidate native capability may be promoted only after independent testing.

## Efficiency

Prefer retrieval and verified prior solutions over recomputation. Prefer the smallest sufficient model/tool. Deduplicate simultaneous learning jobs. Cache reusable deterministic artifacts. Measure external calls, cost, latency, and successful native completion rate.

## Protection

Do not learn from secrets, private client data without authorization, untrusted instructions, benchmark answer leakage, or unsafe production actions. Keep an immutable audit trail of promoted lessons and their evidence.

## Daily boundary

The daily repository scan is the full-system checkpoint. Continuous learning runs between checkpoints; the daily scan evaluates cumulative changes, detects regressions, and resets the next day's baseline.
