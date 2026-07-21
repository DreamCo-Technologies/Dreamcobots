# Old Repository Difference Archive

This folder preserves old DreamCo repository files that were present in an earlier branch but were not active in the current recovery branch.

## What Is Here

- Older docs, reports, examples, scripts, config files, and workflow definitions.
- Historical dashboard planning and capability material.
- Reference code that can be promoted back into the live app after review.

## What Is Elsewhere

The old Python app-category bot files are preserved separately in:

`original-bots/app-category-python/App_bots/`

They are not restored directly into the live `App_bots/` folder because the active repository already uses that path for the 45 division bot JSON profiles.

## Promotion Policy

Treat this archive as source recovery material, not automatically active production code.

Before moving anything from this folder into the live app:

- Check for stale dependencies and imports.
- Run syntax, type, and build checks.
- Confirm no old workflow creates unexpected cost or GitHub Actions usage.
- Keep paid, publishing, outreach, payment, and likeness actions behind owner approval.
- Update Buddy's registry or Actions page only after the restored feature is tested.
