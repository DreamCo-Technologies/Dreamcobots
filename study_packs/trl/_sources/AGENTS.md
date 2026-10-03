# DreamCo Agent Instructions

These instructions apply to coding agents working anywhere in this repository unless a nearer `AGENTS.md` overrides them.

## Evidence-first debugging

1. When a GitHub Actions check is failing, inspect the Actions run/job logs and available artifacts before changing code.
2. Prefer the `Buddy Actions Test Lab` as the owner-facing manual verification entry point.
3. Reproduce the smallest relevant failure before broad edits.
4. Search for the canonical owner and related tests/config/generators before implementing a fix.
5. Fix root causes. Never make CI green by deleting tests, weakening assertions, suppressing meaningful errors, reducing safety thresholds, or silently skipping required work.
6. Add or strengthen a regression test when a genuine defect is repaired.
7. Run focused verification first, then the relevant Buddy suite, then broader repository verification when the change has wide impact.

## Canonical verification

- `npx tsx tools/run_universal_verification.ts --quick` — fast gate.
- `npx tsx tools/run_universal_verification.ts` — merge-level verification.
- `npx tsx tools/run_universal_verification.ts --full` — broad/full verification.
- `npm run test:governed` — governed application, policy, bot, UI, and Python tests.
- `npm run test:repository` — broad repository verification.
- `npm run buddy:fleet:e2e` — fleet execution-profile verification.
- `npm run buddy:site:check` — public Buddy website verification.

## Generated artifacts

Generated files are evidence derived from canonical source. If a generated file is stale, run its canonical generator and fix the source/generator when necessary. Do not hand-edit generated evidence just to satisfy a check.

## Shared fleet rule

Before adding bot-specific infrastructure, determine whether the capability belongs in shared Buddy/fleet infrastructure. Prefer one canonical reusable implementation with per-bot configuration over many copies.

## Capability truth

A configuration, Markdown plan, generated catalog, or declared capability is not proof that a runtime capability is operational. Use executable test, integration, deployment, or runtime evidence for operational claims.

## Safety, permissions, and external effects

Keep external network access, paid services, real outreach, publishing, account changes, financial actions, production writes, and destructive operations behind repository permission/approval gates. Tests should use local, synthetic, mock, staging, or provider-sandbox fixtures whenever possible.

## Agent handoff

For CI/debugging tasks, use the repository custom agent `.github/agents/buddy-debugger.agent.md` when available. Preserve the failing command, root cause, focused fix, verification evidence, and residual risk in the task/PR summary.
