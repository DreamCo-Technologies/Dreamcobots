# DreamCo owner guide

This guide explains what exists in `DreamCo-Technologies/Dreamcobots`, where to find it, and what still needs configuration or proof. The organization is a directory over existing files; moving source folders would risk breaking imports and automation.

## Start with these links

- [Public Buddy site](https://dreamco-technologies.github.io/Dreamcobots/)
- [Searchable website and documentation directory](https://dreamco-technologies.github.io/Dreamcobots/repository-guide.html)
- [Repository system map](https://dreamco-technologies.github.io/Dreamcobots/system-map.html)
- [Setup center](https://dreamco-technologies.github.io/Dreamcobots/setup-center.html)
- [Live Actions results](https://github.com/DreamCo-Technologies/Dreamcobots/actions)

## What you have

The September 22, 2026 baseline at commit `03cf046ed57de9bbf3fc118daf87de6903c6d9eb` contains **3,420 tracked paths, 94 top-level HTML website pages, 226 files under tests, and 214 under tools**. This guide adds another website page. Counts are inventory, not a count of functioning products. The generated directory refreshes its page list from the actual files.

| Area | What is there | What that proves |
| --- | --- | --- |
| `website/` | Public HTML, styles, scripts, generated catalogs and browser interfaces | A static site implementation exists; each feature still needs appropriate testing |
| `client/` | React application frontend | Application source exists; it is separate from the static Pages site |
| `server/` | Express backend and service code | Backend source exists; Pages does not run it |
| `shared/` | Types, policies, routing and shared contracts | Reusable code exists |
| `App_bots/`, `bots/`, `original-bots/` | Specialist catalogs, profiles, and legacy material | Named specialists exist; not every profile is a running agent |
| `buddy/`, `buddy_os/`, `dreamco_platform/`, `framework/` | Shared runtime, orchestration, learning and platform modules | Implementation files exist; runtime coverage varies |
| `config/`, `schemas/` | Configuration, contracts, and generated evidence | Declared settings and snapshots exist; these are not account authorization |
| `tools/`, `scripts/`, `script/` | Generators, checks, command-line and build tooling | Automation code exists; inspect results of actual runs |
| `tests/`, `benchmarks/`, `evidence/`, `reports/` | Tests and recorded results | Evidence exists; check scope, timestamp and revision before relying on it |
| `.github/workflows/` | CI, scheduled jobs, checks, and deployment workflows | Workflow definitions exist; live status is in Actions |
| `docs/`, `command-center/` | Plans, documentation, ownership maps and generated status | Context and navigation exist; plans are not shipped features |
| `DreamPayments/`, `money/`, `money_os/` | Payment and money-related source/configuration | Not proof of live checkout, payouts or revenue |
| `attached_assets/` | Assets already committed to this repository | Not an automatically synchronized copy of the ChatGPT project |

The existing system map declares 1,051 specialist records across 45 divisions and a completion queue of 232. These are generated repository declarations, not independently verified production counts. Use the [build readiness page](https://dreamco-technologies.github.io/Dreamcobots/build.html) and current tests for the specific feature you need.

## What is missing or not established

1. **Automatic ChatGPT-project synchronization is not established.** Conversations, project uploads and GitHub are separate stores. Only actual repository files appear in the public directory. Project attachments have not been exhaustively retrieved or compared, so no claim is made that all Dreamco project material is already in GitHub.
2. **A live backend connection is not established by this audit.** Server source and deployment configuration exist, but a current authenticated deployment, working database, and end-to-end provider connection were not verified. Static Pages cannot execute the Express server, private API calls, or background workers.
3. **Production operation of all bots is not established.** Catalogs, policies, tests and generated capability records do not mean every specialist is continuously running or trained.
4. **Live payments, customer delivery and revenue were not verified.** Use provider sandbox tests and explicit deployment evidence before declaring these operational.
5. **Pages has two publishers.** `pages.yml` builds `docs/` with Jekyll and overlays `website/`. `deploy-buddy-pages.yml` publishes `website/` alone. They use different concurrency groups and can replace each other's artifacts. Both now regenerate the owner directory, but consolidation requires verifying the documentation coverage and deployment preflights first.
6. **A filename collision exists on common Mac filesystems.** `.github/PULL_REQUEST_TEMPLATE.md` and `.github/pull_request_template.md` differ only by case. Both exist in Git; a default Mac checkout cannot represent both independently. Choose a canonical template in a separate reviewed cleanup.
7. **Some documentation and generated snapshots lag behind source.** The README previously described 26 pages although the baseline had 94. Prefer regenerated inventories and the actual files over old counts.

## How the Pages connection works

`Repository source → generators and checks → website/ → GitHub Pages`

The new directory links every discovered HTML page to its website URL and its GitHub source. It also links all scanned top-level source folders and Markdown documentation under `docs/`. These links work under the `/Dreamcobots/` project prefix because website links are relative.

Backend code, tests and documentation outside `website/` open in GitHub. They are not copied into the public artifact or disguised as browser functionality. Private conversations, credentials and project uploads are not included in this change.

Both existing Pages workflows rebuild the directory before publishing. To refresh it locally:

```sh
python3 tools/generate_repository_guide.py
python3 tools/generate_repository_guide.py --check
```

The generator reuses `tools/generate_dreamco_repository_master_map.py` for discovery and exclusions. Edit the generator for layout/text changes; do not hand-edit `website/repository-guide.html`.

## Practical order for the remaining work

1. Review the directory, owner guide, and website navigation changes, then merge through the normal repository checks.
2. Confirm the Pages deployment for the merged revision and open `repository-guide.html` on the live site.
3. Consolidate the two publishers after deciding whether rendered documentation must remain part of the Pages artifact.
4. Inventory the ChatGPT project uploads separately; compare approved materials against GitHub by content before importing anything public.
5. Pick one useful backend-backed feature, configure its service and provider access, and verify it end to end. Record the exact evidence instead of marking the entire fleet live.

GitHub documents Pages as [static site hosting](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages).
