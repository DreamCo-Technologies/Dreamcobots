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

## Interactive command center

Open `buddy-command-center.html` or `dashboard.html` to use the repository workbench.

- **All files:** every Git-tracked path, including generated reports, legacy files, and both case-sensitive template names. The count grows as files are added; it is not capped at the original 3,420. Select a file to view its purpose, open GitHub, prepare a plan, or load an editable text preview. Credential-related files have metadata only in the workbench.
- **All pages:** every tracked website HTML page has a direct page link and file controls. All pages load the same repository navigation through shared scripts or a direct loader.
- **Bot portfolios:** all 1,051 registered bots resolve to their existing division prospectus. Mission, users, inputs, outputs, capabilities, limitations, readiness, and source evidence are visible. Download the portfolio or attach your own work-sample links in your notes. Source artifacts are not customer results.
- **My work plans:** save notes and personal progress in this browser and export them. Browser storage is not GitHub synchronization. Clearing browser storage removes these notes unless exported.
- **Explore info:** each section gets an exploration button. Turn on Explore info mode to click ordinary text, or select text and choose Explore selected text. Buddy receives the selected context only when you choose Explain with Buddy.

### What management means here

Reading the catalog, filtering, viewing portfolios, saving local plans, and downloading drafts work on static Pages. **Edit with GitHub** opens GitHub's authenticated editor, where repository permissions, commits, reviews, and deployment checks apply. File previews read the current public `main`; the deployed index may be older. No browser token is required or stored by this workbench.

This change does not implement an authenticated in-dashboard commit service, execute arbitrary code, run all bots, or make existing demo business features operational. Those require their own backend and verified adapters.

### Updating the connections

Run `python3 tools/connect_repository_pages.py` after generating new HTML, then `python3 tools/generate_command_center_data.py`. Stage new files before generating so Git's tracked-file index includes them. The publisher workflows regenerate these connections. `python3 -m unittest tests.test_repository_browser` verifies complete tracked-path coverage, all page loaders, and every registered bot prospectus.

Browser regression: serve `website/` on `127.0.0.1:8765` and run `node tests/repository-workbench.browser.cjs` with Playwright and Chromium installed. The test uses a mocked source response to verify that loaded code stays inert. It covers file preview/download, saved notes, bot portfolio download, filters, information mode, mobile width, shared page controls, and load-failure recovery.

## Historical bot reconciliation and project coverage

The portfolio interface now contains the 1,051 canonical profiles **plus 262 separately counted historical source records**: 200 income-network table entries, 12 archived major systems, and 50 additional Markdown bot profiles. All 1,101 Markdown bot files are accounted for: 1,051 link to canonical profiles and 50 appear as historical portfolios. Repeated historical names remain traceable records and are not added to the verified-runtime count. Original specification text and source categories are retained; aliases map older categories into existing divisions.

The Project coverage tab links safe feature families to existing source and names the gaps. A private local audit retrieved 48 conversations, 1,241 turns and 1,241 user-message records. One visible conversation could not be read because its conversation tree is corrupt; four content blocks were truncated by the access tool; four attachment references have no retrieved contents. The app listing is limited to 50 recent tasks, so this is not proof that every project conversation has been enumerated. A complete project export is required to close those source-coverage gaps. Raw chats, credentials and personal information are not published.

The branch-health public report generator now uses neutral display labels for legacy platform names and preserves source commit SHAs, PR references, health scores, counts and the original scan timestamp. Display labels are explicitly marked and must not be used as Git refs. This resolves the locally reproduced branding preflight failure without changing its rules or declaring failed checks passed.
