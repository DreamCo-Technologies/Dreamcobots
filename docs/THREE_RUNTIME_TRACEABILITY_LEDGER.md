# DreamCo three-runtime traceability ledger

Snapshot: 2026-11-23 local time (GitHub API timestamps may be 2026-11-24 UTC). This is a point-in-time inventory, not a claim that the listed work is complete.

## Runtime candidates

| Candidate | Repository | Canonical responsibility | Current evidence | Remaining gate |
|---|---|---|---|---|
| Python reference | `DreamCo-Technologies/Dreamcobots` | Buddy orchestration, division registry, provider policy, data, tokenizers, training, evaluation, benchmark definitions and release evidence | Main repository; multiple Python contract and training PRs merged | Complete remaining PR reconciliation; verify live DB/storage/queue/compute integrations; run actual approved tokenizer/weight training; private holdout and release gates |
| Apple C | `ireanjordan24/dreamcobots` | Portable native runtime and later Apple Silicon execution adapter | `core-c/` CMake project, public header, source, C tests and `.github/workflows/dreamco-c-runtime.yml`; C workflow has successful runs on `main` and `feat/dreamco-c-runtime-foundation`; an earlier run failed on both OS matrix jobs | Reconcile branch/main history; investigate old Build failure; add shared contract fixtures, runtime implementation and benchmark evidence only after Python completion |
| Apple Swift | `ireanjordan24/dreamcobots` | Existing macOS UI/provider/orchestration candidate | `dreamco/ContentView.swift`, `dreamco/OpenRouterService.swift`, `dreamco/dreamcoApp.swift`, Xcode project, unit tests and UI tests exist | Preserve app and provider path; add a dedicated Xcode build/test workflow and shared task/provider contract conformance after Python completion |

## Python-first work reconciliation

| PR | Scope | Snapshot status | Traceability / next action |
|---|---|---|---|
| #18157 | Private holdout benchmarking | Merged | Verify benchmark artifacts and holdout isolation on current main; a merge alone is not a completed benchmark campaign |
| #18161 | Per-division PostgreSQL catalog identities | Merged | `buddy/datasets/postgres_catalog.py`, `tests/test_buddy_postgres_catalog.py`; verify real DSNs, grants, schema isolation and integration evidence |
| #18168 | Buddy Bootcamp curriculum for all 65 divisions | Merged | Verify curriculum coverage and that each learning path is backed by approved data/resources, not just catalog entries |
| #18169 | Release-gate-compatible training evidence | Merged | Verify evidence is emitted by real training jobs and binds exact code/data/model/checkpoint revisions |
| #18170 | Canonical per-division model identities | Merged | Verify identities are backed by actual checkpoints/tokenizers and execution evidence; specification-only models are not trained models |
| #18158 | Model-provider data classification and output-use policy | Open | Review `buddy/models/provider_runtime.py`, `config/buddy-model-serving-policy.json`, tests and generated artifacts. Verify provider-specific classification ceilings, model allowlists, output-training permission semantics, request audit evidence and fail-closed behavior. Reconcile stale base before merge |
| #18159 | S3 object storage health and backup/restore evidence | Open | Review `buddy/storage/object_store.py`, tests and workflow. Test credential-chain behavior, encryption/versioning/retention, isolated healthcheck prefix, backup/restore integrity and real service evidence. Mocks do not prove live S3 connectivity. Reconcile stale base before merge |
| #18167 | Five-minute planning versus actual training | Open | Verify the scheduler cannot claim training from planning events; real worker execution must produce job IDs, resource allocation, checkpoints, logs and benchmark evidence. Reconcile stale base before merge |

## Apple repository workflow evidence

- C workflow: `.github/workflows/dreamco-c-runtime.yml`.
- Successful run on Apple repository `main`: [run 45334180626](https://github.com/ireanjordan24/dreamcobots/actions/runs/45334180626).
- Successful run on `feat/dreamco-c-runtime-foundation`: [run 45333790023](https://github.com/ireanjordan24/dreamcobots/actions/runs/45333790023).
- Earlier failed C matrix run: [run 45333715060](https://github.com/ireanjordan24/dreamcobots/actions/runs/45333715060); both Ubuntu and macOS Build steps failed. Preserve and diagnose this evidence; later success does not erase the failure.
- The inspected C workflow builds/tests CMake on Ubuntu and macOS. It does not establish Swift compilation or Xcode UI-test execution.
- The private Apple repository has no open PRs in the inspected query. Its default branch is `main`; inspect branch history and submodule pins before any synchronization.

## Shared three-runtime release gates

1. Python remains the source of truth for task packets, division/model identities, provider policy, dataset rights/manifests, tokenizer/model artifacts, benchmark cases and release evidence.
2. Complete and verify Python services, approved tokenizer/weight training, private holdout, regression/safety tests, backup/restore and release gates before promoting either Apple candidate.
3. Freeze versioned JSON schemas and conformance fixtures.
4. Keep C and Swift as separate candidates with independent builds/tests and a shared task/provider interface.
5. Compare only parity-controlled workloads: same task packet, model/tokenizer revisions, prompts, tool permissions, data splits, benchmark version and gates. Record hardware/OS/compiler/runtime/environment. Separate incomparable hardware cohorts.
6. Select the best eligible implementation per task only after capability, rights, privacy, safety, quality and reproducibility hard gates. Keep fallback and rollback evidence.
7. Do not infer training from scheduled jobs, model quality from parameter count, or performance from language choice.

## Operational truth and safety boundaries

- A merged PR means its code is in the target branch; it does not prove live external services, training, model quality, or production readiness.
- A green C build does not prove a complete inference runtime; a Swift UI test does not prove model inference parity.
- No Mac runner execution is claimed by this ledger. Use it only when runner registration and actual job execution are observable.
- Do not commit credentials or raw private ChatGPT conversations. Export only explicitly approved requirements and decisions.
- Do not rewrite history, delete old branches, bulk-update the submodule, cancel productive workflows, enable Cloudflare, or weaken macOS security controls.

## Complete open-PR metadata inventory (2026-11-23 snapshot)

The following entries were returned by GitHub's open-PR search for the canonical repository. This is a **metadata inventory only**: each item remains unreviewed for code overlap, dependency ordering, branch divergence, tests, security, and merge disposition unless its detailed review appears above. Do not merge from this list alone.

| PR | Title | Review disposition |
|---:|---|---|
| [#18173](https://github.com/DreamCo-Technologies/Dreamcobots/pull/18173) | Preserve Python, Apple C, and Apple Swift as three competing runtimes | Review pending |
| [#18130](https://github.com/DreamCo-Technologies/Dreamcobots/pull/18130) | feat(buddy): connect full bot fleet to divisions, learning and revenue plans | Review pending |
| [#17855](https://github.com/DreamCo-Technologies/Dreamcobots/pull/17855) | fix(ci): repair verified repository workflow failures | Review pending |
| [#17794](https://github.com/DreamCo-Technologies/Dreamcobots/pull/17794) | fix(training): validate provenance metadata outside PII text scan | Review pending |
| [#17783](https://github.com/DreamCo-Technologies/Dreamcobots/pull/17783) | Add reproducible Buddy tiny GPT baseline and Bootcamp evidence | Review pending |
| [#17766](https://github.com/DreamCo-Technologies/Dreamcobots/pull/17766) | feat(buddy): connect verified CI repairs to dataset event pipeline | Review pending |
| [#17499](https://github.com/DreamCo-Technologies/Dreamcobots/pull/17499) | Add always-on production readiness master list and routing inventory | Review pending |
| [#17497](https://github.com/DreamCo-Technologies/Dreamcobots/pull/17497) | fix(learning): require execution provenance before promotion | Review pending |
| [#17173](https://github.com/DreamCo-Technologies/Dreamcobots/pull/17173) | docs: add independent DreamCo conversation checklists and master registry | Review pending |
| [#16913](https://github.com/DreamCo-Technologies/Dreamcobots/pull/16913) | Add five-minute read-only repository health audit | Review pending |
| [#17170](https://github.com/DreamCo-Technologies/Dreamcobots/pull/17170) | audit: inventory every Markdown requirement and add Pages checklist | Review pending |
| [#8847](https://github.com/DreamCo-Technologies/Dreamcobots/pull/8847) | Build the DreamCo inventions hub, specialist intakes and live Actions | Review pending |
| [#16911](https://github.com/DreamCo-Technologies/Dreamcobots/pull/16911) | Add Hugging Face and Ollama training academy for Buddy Bootcamp | Review pending |
| [#15406](https://github.com/DreamCo-Technologies/Dreamcobots/pull/15406) | Fix Keep Green invalid Pages index without truncating file inventory | Review pending |
| [#13176](https://github.com/DreamCo-Technologies/Dreamcobots/pull/13176) | Gate model routes on caller identity; make Buddy model selection allowlist-only (plan-model-access Path D) | Review pending |
| [#13889](https://github.com/DreamCo-Technologies/Dreamcobots/pull/13889) | Connect existing bots to the proposal registry and add bounded fleet verification | Review pending |
| [#15122](https://github.com/DreamCo-Technologies/Dreamcobots/pull/15122) | Add fail-closed Buddy Master Teacher evidence gate | Review pending |
| [#15185](https://github.com/DreamCo-Technologies/Dreamcobots/pull/15185) | Add Buddy production evidence preflight across Pages, Bootcamp and dependencies | Review pending |
| [#15189](https://github.com/DreamCo-Technologies/Dreamcobots/pull/15189) | feat: persistent user-scoped Buddy task state and audit trail | Review pending |
| [#15253](https://github.com/DreamCo-Technologies/Dreamcobots/pull/15253) | Buddy: opt-in evidence learning and verified capability acquisition | Review pending |
| [#15255](https://github.com/DreamCo-Technologies/Dreamcobots/pull/15255) | Buddy Training Hub: free and paid compute, tokenization and weight-training catalog | Review pending |
| [#15256](https://github.com/DreamCo-Technologies/Dreamcobots/pull/15256) | Buddy Bootcamp: searchable AI training taxonomy and lesson templates | Review pending |
| [#15257](https://github.com/DreamCo-Technologies/Dreamcobots/pull/15257) | Buddy Bootcamp: categorize 12 training resources with searchable learning paths | Review pending |
| [#15258](https://github.com/DreamCo-Technologies/Dreamcobots/pull/15258) | Buddy Bootcamp: 12 official provider-specific learning libraries and searchable catalog | Review pending |
| [#15262](https://github.com/DreamCo-Technologies/Dreamcobots/pull/15262) | Daily Buddy capability tests, dedup candidates, frontier gaps and training plans | Review pending |
| [#15342](https://github.com/DreamCo-Technologies/Dreamcobots/pull/15342) | Document Buddy benchmark coverage gaps | Review pending |
| [#15436](https://github.com/DreamCo-Technologies/Dreamcobots/pull/15436) | Add read-only Buddy division/model benchmark coverage auditor | Review pending |
| [#15487](https://github.com/DreamCo-Technologies/Dreamcobots/pull/15487) | Safety: make Intelligent Issue Cleaner read-only and preserve CI failures | Review pending |
| [#16912](https://github.com/DreamCo-Technologies/Dreamcobots/pull/16912) | Build Buddy Dataset Profile Builder and governed learning manifests | Review pending |
| [#16757](https://github.com/DreamCo-Technologies/Dreamcobots/pull/16757) | Connect Buddy resources, research, benchmarks, and learning diagnostics | Review pending |
| [#13278](https://github.com/DreamCo-Technologies/Dreamcobots/pull/13278) | Bundle safe unmerged work: bot slugs, control plane, F0, deps | Review pending |
| [#13901](https://github.com/DreamCo-Technologies/Dreamcobots/pull/13901) | Add human-reviewed capability evaluation and approval console | Review pending |
| [#14014](https://github.com/DreamCo-Technologies/Dreamcobots/pull/14014) | Consolidate Buddy runtime, training workbench and fail-closed evidence controls | Review pending |
| [#13195](https://github.com/DreamCo-Technologies/Dreamcobots/pull/13195) | security(api): require auth on /api with small public allowlist (DRAFT for owner review) | Review pending |
| [#14397](https://github.com/DreamCo-Technologies/Dreamcobots/pull/14397) | pages: link eight orphaned product pages in nav and sitemap | Review pending |
| [#14668](https://github.com/DreamCo-Technologies/Dreamcobots/pull/14668) | fix(ci): Evidence gate runs the existing Buddy OS unittest | Review pending |
| [#14849](https://github.com/DreamCo-Technologies/Dreamcobots/pull/14849) | fix(ci): regenerate pages feature audit for 223 pages (was 205) | Review pending |
| [#15261](https://github.com/DreamCo-Technologies/Dreamcobots/pull/15261) | Buddy in-house capability certification lab and 365-day measurable goals | Review pending |
| [#15186](https://github.com/DreamCo-Technologies/Dreamcobots/pull/15186) | Buddy user-configurable training points and rewards | Review pending |
| [#15187](https://github.com/DreamCo-Technologies/Dreamcobots/pull/15187) | Expose existing capability workbench across DreamCo Pages and document truth gates | Review pending |
| [#14603](https://github.com/DreamCo-Technologies/Dreamcobots/pull/14603) | evidence(hf): SST-2 Day-1 dual runs (acc 0.91055, claimable false) | Review pending |
| [#12431](https://github.com/DreamCo-Technologies/Dreamcobots/pull/12431) | Fix Buddy Sandbox Bootcamp curriculum validation | Review pending |
| [#12082](https://github.com/DreamCo-Technologies/Dreamcobots/pull/12082) | Add personal Buddy setup and learning evidence; fix full-fleet certification | Review pending |
| [#8925](https://github.com/DreamCo-Technologies/Dreamcobots/pull/8925) | Pages mirrors: Goals, desks, sources, learn, devices, OS | Review pending |
| [#8701](https://github.com/DreamCo-Technologies/Dreamcobots/pull/8701) | Recovery systems: eight lanes, one incident bus | Review pending |
| [#8702](https://github.com/DreamCo-Technologies/Dreamcobots/pull/8702) | Build readiness + self-build/self-fix for every repository part | Review pending |
| [#3682](https://github.com/DreamCo-Technologies/Dreamcobots/pull/3682) | feat: 65 MasterBot training OS, Bootcamp, Sandbox, and 24/7 gap lanes | Review pending |
| [#3684](https://github.com/DreamCo-Technologies/Dreamcobots/pull/3684) | feat: safely add 20 MasterBots to homepage architecture | Review pending |
| [#5123](https://github.com/DreamCo-Technologies/Dreamcobots/pull/5123) | feat: publish DreamCo AI research portal and control-plane updates | Review pending |
| [#7973](https://github.com/DreamCo-Technologies/Dreamcobots/pull/7973) | feat: Grok twin router + Build Updates Now pipeline | Review pending |
| [#1961](https://github.com/DreamCo-Technologies/Dreamcobots/pull/1961) | feat: standardize Buddy repository scan update reporting | Review pending |
| [#830](https://github.com/DreamCo-Technologies/Dreamcobots/pull/830) | Buddy frontier growth + universal navigation platform | Review pending |
| [#730](https://github.com/DreamCo-Technologies/Dreamcobots/pull/730) | DreamPayments + Buddy: merchant-first processing, O*NET bootcamp and evidence-driven agents | Review pending |
| [#682](https://github.com/DreamCo-Technologies/Dreamcobots/pull/682) | Add evidence-based model benchmark scorecard | Review pending |
| [#476](https://github.com/DreamCo-Technologies/Dreamcobots/pull/476) | Publish every user-facing page on GitHub Pages and attach backend | Review pending |
| [#474](https://github.com/DreamCo-Technologies/Dreamcobots/pull/474) | Repair Actions control center behavior and status truth | Review pending |
| [#469](https://github.com/DreamCo-Technologies/Dreamcobots/pull/469) | Add DreamCo intelligence, continuous expansion, and 100-update research gate | Review pending |
| [#467](https://github.com/DreamCo-Technologies/Dreamcobots/pull/467) | Expand Buddy universal benchmarks, revenue, workforce, government and sandbox systems | Review pending |
| [#928](https://github.com/DreamCo-Technologies/Dreamcobots/pull/928) | feat: add DreamCo Money OS revenue integration | Review pending |

Inventory count: 62 open PRs returned; 8 PR numbers already referenced in this ledger; 59 additional open PRs listed here. Refresh this inventory before every reconciliation pass because PR state changes over time.
