# DreamCo Recovery Merge Report

Generated: 2026-07-20

## Recovery Branch

- Branch: `codex/recover-buddy-after-import`
- Base: `origin/main`
- Recovery source: `codex/bot-test-dashboard`

## What Was Restored

- `config/` source-of-truth registries, policies, generated catalogs, and bot governance configs.
- `tools/` generator, audit, storage, runner, registry, and recovery scripts.
- `reports/` generated evidence for Buddy, bot readiness, storage, Stripe, app categories, professional OS, and life-opportunity systems.
- `dreamco-control-tower/` Buddy Actions dashboard, backend report APIs, frontend tests, and command-center UI.

## What Was Preserved

- Current `origin/main` app shell, website, restored original bot JSON files, server, client, and attached assets.
- Current `App_bots/` division JSON files from main.
- Current TypeScript app `package.json` dependency stack, with DreamCo report scripts added instead of replacing it.

## Voice Fix

Buddy no longer depends on a paid external voice key for the default voice path.

- `POST /api/voice/clone` now returns a DreamCo local/browser text-to-speech packet when no external voice endpoint is configured.
- `GET /api/voice/voices` now exposes free local Buddy voice choices.
- External voice providers are optional and require `BUDDY_VOICE_API_KEY` plus `BUDDY_VOICE_TTS_URL`.
- Voice or likeness cloning remains consent-gated.

## Safety Notes

- This branch is additive and recovery-focused.
- No destructive reset was used.
- The recovered systems should be reviewed in a pull request before merging into `main`.
