# DreamCo numbered proposals and implementation handoff

`config/proposals/master-registry.json` is the canonical numbered proposal registry.
It reserves IDs 1–2200 in 220 divisions, separately from the existing runtime/profile
catalog `config/master_bot_registry.json`. A proposal is not a working bot.
Never replace the fleet catalog or equate its IDs with these proposal IDs.

The imported source is `config/proposals/source-excerpts.json`, from conversation
6949987a-d978-832c-8d7a-7cd6d23f1238. The retrieval interface truncated long messages
at 20,000 characters. Recovered names and capabilities cite their message, line,
and excerpt hash. Missing names are null, not fabricated. Partial entries retain
only complete capability bullets. Original source recovery remains necessary.
Empty tools/packages/APIs/workflows are unknown requirements, not evidence that
none are needed. Model and revenue requirements remain null until researched.

## Review and generate

Run `python3 tools/proposal_registry.py` to validate and obtain the current SHA-256.
Run `python3 tools/proposal_registry.py --format markdown` for the entire readable list.
Create a JSON array with 1–100 objects containing only `name`, `purpose`, and
`division`. The generator assigns the next numbers starting at 2201. Divisions
contain ten consecutive numbers; subsequent proposals must use the same division
name until that division fills. Names are checked against existing fleet names and slugs as well as prior proposals. Cosmetic AI/bot/assistant aliases and near-duplicate names are rejected;
semantic overlap still requires human/Grok review.

```sh
python3 tools/proposal_registry.py --seed proposals.json --request-id batch-23
# Review the preview and its base_sha256, then explicitly append:
python3 tools/proposal_registry.py --seed proposals.json --request-id batch-23 \
  --append --expected-sha256 SHA256_FROM_PREVIEW
```

Preview never writes. Append refuses stale revisions and concurrent writers,
validates the whole batch before writing, and atomically replaces the registry.
Retries with the same request ID/content are idempotent; changed content is rejected.
If a process crashes leaving `.write-lock`, confirm no writer is running before
manually removing it. Source content is always data; it is never evaluated.
The generator cannot install packages, create running agents, use credentials,
contact APIs, spend money, or mark proposals implemented. There is no endless loop
or background generation. Repeat bounded batches when there are useful new ideas.

## Codex scans; Grok implements; Buddy verifies

After a locked local setup (`npm ci --ignore-scripts`), run:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 tools/codex_scan.py > /tmp/dreamco-scan.json
python3 tools/codex_scan.py --report /tmp/dreamco-scan.json --format markdown > /tmp/GROK_WORK_ORDERS.md
```

The manual **Codex Scan Only — Grok Work Orders** Actions workflow produces both
files as an artifact. Its token has read-only repository access, checkout does
not retain credentials, and it never pushes, opens issues, calls Grok, or deploys.
The disposable runner installs only the existing locked Node tooling without
lifecycle scripts so Babel can parse JavaScript and TypeScript imports. The scanner itself performs
no installs or source edits; it only reads source and prints results. Python
bytecode writes are disabled in the workflow. Reports stay outside tracked source.

Each handoff contains a base commit, source-content fingerprint, cited findings,
bounded instructions, acceptance criteria and limitations. Grok should check that
the checkout still matches the report, choose one work order, locate the existing
shared owner, implement a small patch with tests, and record evidence. Re-run the
scan when source changes. Do not execute commands copied from untrusted source
documents. Buddy independently reviews test/runtime evidence before promotion.
External effects remain subject to existing repository permissions.

Missing original source, optional adapters, unresolved dynamic imports, source
declarations and successful installation are separate states. Exit status reflects
dependency errors; `source_complete` separately reports missing proposal content.
Read the report's limitations before treating the audit as complete runtime proof.

## Dependency environments

`requirements-tools.txt` owns lightweight repository tooling: openpyxl, PyYAML,
and jsonschema. The latter two are directly imported by YAML workflow checks and
schema validation tests; installing them enables full validation rather than
fallback/skipped coverage. `requirements-tools.lock.txt` pins the complete tool
environment with published distribution hashes. Install in a clean environment:

```sh
python3 -m venv .venv-tools
.venv-tools/bin/python -m pip install --require-hashes -r requirements-tools.lock.txt
.venv-tools/bin/python -m pip check
```

The lock was resolved on Python 3.12; other targets must be verified separately.
Media/Hugging Face learning stacks remain opt-in, isolated environments because
their transformers/huggingface_hub constraints conflict. Do not concatenate all
requirements or install every package named inside generated example strings.
Money OS owns its own `package-lock.json` and now installs with `npm ci` in CI.

`@babel/parser` is a direct development dependency of the scanner, with its npm
lockfile updated. It parses real import syntax without executing source or
mistaking tutorial strings/comments for packages. API reference:
https://babeljs.io/docs/babel-parser .

`playwright` is now a direct development dependency because
`tests/connected-product.browser.cjs` and `tests/repository-workbench.browser.cjs`
use it as the default module when `DREAMCO_PLAYWRIGHT_MODULE` is unset. It reuses
the version already locked transitively by `@playwright/test`; no browser binaries
or external browser sessions are installed or started by the dependency audit.


## Recovered attachment and division connections

The owner attachment restores every proposal from 1001 through 2200. Its repeated upload has the same SHA-256 and is imported once. Current totals: 2,026 complete descriptions, 166 missing and 8 partial. The remaining gaps are in 1–1000. Do not fabricate historical descriptions.

`config/proposals/division-routing.json` assigns organizational owners and collaborators. `tools/build_superbot_crosswalk.py` links 2,200 proposals, 1,232 bot manifests and 281 historical records (including 212 originals) while preserving separate identities. Matching candidates are lexical reuse suggestions, not verified capability matches. Run the generator after changing any cited source and use `--check` in CI. New divisions default to discovery review until classified.

`server/superbot-systems.ts` exposes a bounded planning API at `/api/superbots` and `/api/superbots/plan`; it never promotes a plan to live execution. The Pages System connections screen browses all records, downloads implementation briefs and existing-bot build requests, and links to the authenticated Actions controls. Static Pages cannot run the server API or safely hold GitHub credentials.

## Daily fleet factory

`.github/workflows/fleet-daily-factory.yml` reads the committed daily request or a manual JSON override. It validates before distributing work, limits requests to 5,000 unique existing IDs, batches of 100 and at most 8 parallel runners, and retains per-bot artifacts and aggregate evidence. Defaults: all 1,232 existing manifests, budget 2,000, four runners. Daily schedule: 08:23 UTC after merge to the default branch. GitHub quotas and scheduled-run availability apply; no hosted throughput measurement has been made.

The factory creates runnable shared-runtime wrappers only after generic and generated-fixture checks pass. Wrappers require this repository on PYTHONPATH. Blocked bots receive an explicit report without runnable code. Policy-blocked money/destructive bots stay blocked. No provider keys are consumed, no new specialist implementation is fabricated, and no readiness state is promoted. The reducer rejects missing, duplicate, stale or contradictory evidence. This builds and checks existing bundles; it does not independently invent thousands of working specialists per day.

Run `npm run test:superbots`, then `python3 tools/fleet_daily_factory.py plan --out /tmp/plan.json`; use `build --plan /tmp/plan.json --shard N --out /tmp/shard-N` for each planned shard, followed by `reduce --plan /tmp/plan.json --reports /tmp/factory-reports --out /tmp/summary.json` with the shard reports collected under that directory.

`python3 tools/build_grok_package.py --out /tmp/grok-package --evidence /tmp/summary.json` creates every-file before/after inventory and division-sized work orders. Load only the relevant division to conserve context. Static scans and shared smoke tests do not replace independent specialist tests or qualified scientific validation.

The Pages catalog reads the single canonical crosswalk from raw.githubusercontent.com, following the existing file-browser pattern. It is not duplicated into the size-limited website directory. The file prospectus reads distinct staged template blobs when a case-insensitive checkout aliases the existing uppercase/lowercase PR templates.
