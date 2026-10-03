# Readiness gate plan

A gate is green only when the check ran on the current revision and produced evidence. A document, a listed file, or a sandbox receipt is not certification.

## Release gate

`python3 tools/production_readiness_gate.py --strict` is the code gate. It passes when release-blocking runtime checks pass. It still reports `external_config_required` until the host has:

- `DATABASE_URL`
- `STRIPE_WEBHOOK_SECRET`
- a Stripe secret key and publishable key
- `OWNER_BILLING_TOKEN`
- an OpenAI key if those routes stay enabled

Host secrets are not committed. GitHub Pages must be set to GitHub Actions before the Pages workflow can publish.

## Voice gate

Consent hash, reference length, memory budget, watermark, then three verified passes. See `docs/VOICE_CLONING_PLAN.md`. No pass is recorded from a missing model.

## Study gate

A bot study task marked done is a local lesson. Production mastery still requires a repeated native pass, a private holdout, and a regression check.

## What is still missing

- Live smoke tests on the host with the secrets above.
- Pages source switched to GitHub Actions.
- Hugging Face study packs are not mastered. Open pull requests were not merged by this scan.
- Distillation from Grok outputs stays closed until xAI terms allow it.
- O*NET zip files and third-party course dumps stay out of the public repo.
- Hidden holdouts stay private.
- Workflow count is still far above the consolidation target. Colliding cron minutes should be staggered after one workflow in each group is proven to cover the others.

## Decisions

- Merge `main` into `#9573`. Do not rebase.
- Open the operate-check fix and the API sign-in lockdown as a draft.
- Open the data-package gate. Do not commit the O*NET zip.
- Keep the XTTS install commented out.
