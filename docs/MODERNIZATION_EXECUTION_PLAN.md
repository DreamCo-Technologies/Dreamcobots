# DreamCo Modernization + Benchmark Execution Plan

This plan incorporates the owner-approved modernization roadmap into the existing evidence-driven Buddy benchmark program.

## Operating mode

- Work only on the review branch until explicitly approved for promotion.
- Prefer small, reviewable commits.
- Group related work into logical pull requests.
- Run independent discovery and verification in parallel where safe.
- Serialize shared-state changes and dependency-sensitive migrations.
- Never fabricate passing tests, coverage, builds, benchmarks, or release assets.
- Preserve canonical capabilities and existing data.
- Do not weaken tests to obtain a pass.
- Do not change secrets or credentials.
- Do not make paid model/API calls.
- Do not deploy production or contact external parties.
- Destructive deletion requires evidence that a duplicate is safe to remove and owner approval at the applicable promotion gate.

## Execution order

### Track A — Health and inventory

1. Full repository inventory.
2. Duplicate and obsolete-folder report.
3. README/setup/requirements audit.
4. Naming/import compatibility analysis.
5. Existing Actions and Pages contract audit.

### Track B — Framework

1. Compare the requested framework components against existing canonical implementations.
2. Reuse existing systems instead of creating parallel duplicates.
3. Add missing configuration, logging, metrics, plugin management, event bus and lifecycle hooks only where gaps are verified.
4. Add focused tests for each shared component.

### Track C — Plugin platform and bot generator

1. Map existing plugin/bot registration mechanisms.
2. Identify duplicate discovery systems.
3. Establish one canonical registration contract where safe.
4. Build `tools/create_bot.py` only after checking existing generators.
5. Generate fixture bots and verify generated artifacts.

### Track D — Quality and CI

1. Inventory current test/lint/type-check tooling.
2. Repair broken configuration before adding duplicate tooling.
3. Add missing checks incrementally.
4. Run targeted checks first, then broader suites.
5. Upload machine-readable evidence to Actions.

### Track E — Releases and applications

1. Determine existing supported application targets.
2. Add release packaging only for targets that can be reproducibly built in the repository.
3. Verify artifacts rather than claiming that installers exist.
4. Connect release metadata to Pages.

### Track F — Security and governance

1. Audit existing Dependabot, CodeQL and secret-scanning configuration.
2. Avoid duplicating existing security workflows.
3. Add missing repository policy files.
4. Provide branch-protection recommendations when settings cannot safely be changed by code.

### Track G — Benchmark integration

Every modernization change is evaluated for its impact on the benchmark graph:

`baseline → root cause → smallest shared repair → targeted test → benchmark → dependent-suite retest → before/after evidence → rollback/fallback`

A modernization task can improve many benchmarks at once when it fixes a shared dependency. Those dependent suites should be retested rather than individually patched.

## Pull-request structure

The requested logical PR sequence is preserved:

1. Repository cleanup
2. Framework
3. Plugin architecture
4. CI/CD
5. Documentation
6. Release system
7. Application packaging

If repository reality shows that a requested PR would mix unrelated changes or create a conflict, split it into smaller reviewable PRs rather than forcing the requested grouping.

## Final report requirements

`REPORT.md` must distinguish:

- verified complete;
- partially complete;
- blocked;
- not started;
- known regressions;
- test evidence;
- benchmark evidence;
- changed files;
- remaining owner actions.

No item is marked complete merely because the code or configuration was created.
