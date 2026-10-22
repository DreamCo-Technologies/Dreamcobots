# Daily Capability Gap Lab

## Scope
Scheduled once per day via GitHub Actions, after the workflow lands on the default
branch. The workflow evaluates **all capabilities registered in the certification
manifest**, not every aspirational bot or code file in DreamCo. The first manifest
contains 12 capability families, with no executable test modules assigned yet.

Each run creates:
- Local test receipts and conservative capability status.
- Duplicate candidates from normalized domain + description fingerprints.
- Explicit gap-closure and training plans for each capability.
- Honest not-run markers for frontier comparisons, reverse engineering, and model training.

The lab does **not** scrape the world, reverse-engineer protected systems, call
paid frontier APIs, train weights, modify existing bots, delete duplicates, or
certify production automatically. Only authorized and licensed sources may be
studied; protected evaluation fixtures stay isolated from training data.

## Next implementation gates
1. Map canonical fleet registry IDs to the capability manifest without duplicate IDs.
2. Register sandbox-safe tests with pinned fixtures and dependency manifests.
3. Add test receipt storage and independent holdout benchmarks.
4. Add opt-in frontier adapters with identical tasks, cost limits and model revisions.
5. Add consented training recipes, legal source provenance and human review.
6. Integrate generated artifacts into the existing Pages publisher.
7. Publish daily freshness and missed-run alerts without claiming unrun tasks passed.

GitHub Pages is static: Actions artifacts are not automatically available there.
Use the Actions workflow page for actual daily run results until publication is wired.
