# Pass-all plan for the 500-model benchmarks

Buddy already has **500 catalog targets** (`MODEL_BENCHMARK_TARGET_COUNT = 500`) and an operating plan in `docs/UNIFIED_500_MODEL_BENCHMARK_OPERATING_PLAN.md`. The index still says **live programs with evidence: 0**. Missing evidence is not a pass.

"Pass all 500" means: every target reaches a **terminal legal state** — `passed`, `not_applicable`, or `blocked` with a reason — not that Buddy secretly beat every frontier API for free.

## What "pass" is allowed to mean

| State | Allowed as done? | Meaning |
| --- | --- | --- |
| `passed` | yes | Same fixture, quality gate, safety gate |
| `not_applicable` | yes | Wrong modality (e.g. video model on text suite) |
| `blocked` | yes, if honest | Needs paid adapter / license / hardware |
| missing / `catalogued` only | **no** | Not a pass |
| `failed` | no | Goes to a study pack + retest |

Native Buddy mastery still requires `native` independence, not Grok taking the test for Buddy.

## Four waves (do not run 500 paid APIs in one Actions job)

### Wave A — catalog integrity (week 1)
- 500 names, sources, licenses still match `shared/model-benchmark-targets.ts`
- `tools/check_buddy_model_benchmarks.mjs` stays green
- Every target has a prospectus row

### Wave B — local / free fixtures (weeks 2–6)
Pass the suites that do **not** need paid APIs:
- repository contracts
- instruction / coding / tool fixtures on local or open-weight students
- safety refusals
- Buddy learning proof loop

Close gaps with `pack.instruct`, `pack.code`, `pack.tools`, `pack.safety` + LoRA, not by deleting tests.

### Wave C — hosted comparators (weeks 7–14, explicit budget)
Grok, OpenAI, Anthropic, Gemini, etc. only with an approved adapter and a dollar cap. Record `external_model_assisted` when the teacher helps. Do not mark those as Buddy-native mastery.

### Wave D — blocked-but-honest leftover
Whatever still needs a GPU, a gated HF repo, or a vendor contract stays `blocked` with a ticket. That is how you "finish 500" without lying.

## Shared-fix order (from the operating plan)

When many models fail the same suite, fix **one** thing:

1. Fixture / grader bug
2. Router / tool schema
3. RAG retrieval
4. Student LoRA on that capability pack
5. Only then a bigger student (`dream-work` → `dream-pro`)

Retest every dependent suite after a shared fix.

## Scoreboard

Track counts, not vibes:

- catalogued / ready / running / passed / failed / blocked / stale / n/a
- native pass rate vs external-assisted pass rate
- $ spent this wave
- stale after model-id change

Owner button: **DreamCo unified system** / 500-model workflow already named in the operating plan. Do not spawn 500 extra workflows.
