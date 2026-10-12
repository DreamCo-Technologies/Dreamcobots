# Data Package Product Plan

**Repo:** DreamCo-Technologies/Dreamcobots  
**Generated:** 2026-09-21T16:13:56-05:00 (CDT / America/Chicago)  
**Restored:** 2026-10-02 by Grok-Data-Package-Merchant (owner of `plan-data-package`) from a verbatim read taken 2026-09-21; the original lived only as an untracked file on the shared box and was lost. Section 8 status notes added on restore.  
**Truth boundary:** Planning + inventory only. Does **not** flip `production_ready`, claim live marketplace sales, claim O*NET®/HF mastery, or authorize copying third-party copyrighted books/datasets for resale. Prefer completing existing Buddy learning / open-model / capability-package paths over parallel empires.

**Machine-readable sibling:** `reports/data-package-product.json`  
**Related:** `reports/ONET_MASTERY_TRACK.md`, `reports/HUGGINGFACE_MASTERY_TRACK.md`, `reports/MODEL_ACCESS_PRODUCT_PLAN.md`

---

## 1. Product north star

Sell **DATA PACKAGES** as a DreamCo product SKU family:

1. Buddy (and humans) study topics from **many points of view**.
2. Synthesize an **original DreamCo perspective** (analogy: read many books → write your own).
3. Store that synthesis as **owned DreamCo data** for reuse and lawful sale.
4. Ship only packages that pass a **provenance + license gate** (public domain, U.S. government / O*NET® terms, open licenses allowing commercial reuse, and original DreamCo-generated synthesis).

**Hard no:** designing a system to strip copyright from third-party books/datasets and resell them. Reference-only manifests + original exercises are OK when redistribution of the source is forbidden.

---

## 2. What already exists (evidence)

| Area | Artifact | State |
| --- | --- | --- |
| Knowledge rewrite / originality | `docs/training-methodology/DREAMCO_KNOWLEDGE_REWRITE_STANDARD.md` | Spec — multi-source → original DreamCo assets + book analogy |
| Multi-perspective policy | `buddy/learning/multi_perspective_policy.json` | Policy — 15 perspectives + `synthesize_pattern` pipeline |
| Open-code synthesizer stub | `buddy/learning/open_code_perspective.py` | **Stub** — returns research plan dict; no package store |
| Study evidence schema | `buddy/learning/study_data_schema.json` | Schema — license notes + training buckets + privacy |
| Dataset product standard | `config/dataset_product_standard.json` | Lifecycle + release artifacts + commercial honesty |
| Maximal testing program | `config/data-package-maximal-testing-program.json` | Broad QA families incl. provenance_and_rights |
| Provenance schema | `config/evidence_provenance_schema.json` | Required fields; source_type includes `onet`, `dreamco_generated` |
| Training ownership policy | `config/buddy-training-data-provenance-policy.json` | Ownership classes; block unknown from commercial packages |
| Candidate scoring | `tools/score_data_package_candidate.py` + `config/data-discovery-bot-program.json` | Triage CLI; hard-fails stolen/redistribution-forbidden |
| Dataset scorecard | `config/dataset_evaluation_scorecard.json` | 0–100 dims; commercial tiers prototype→premium |
| Capability package schema | `capabilities/capability_package.schema.json` | Capability bundles (not sellable dataset SKUs yet) |
| Capability marketplace config | `config/buddy_capability_package_marketplace.json` + `docs/capability-package-marketplace.md` | Capability install/bootcamp; knowledge_policy lawful only |
| Bootcamp gain package | `docs/BUDDY_SANDBOX_BOOTCAMP_DATA_PACKAGE.md` + `config/buddy-sandbox-bootcamp-package.json` | Internal gains package (not customer SKU) |
| O*NET® specs | `config/onet-sandbox-dataset-spec.json`, `config/onet-priority-curriculum.json`, `config/buddy_github_onet_codecademy_benchmark_system.json` | Curriculum/sandbox contracts |
| O*NET® ingest tool | `tools/build_universal_work_ai_catalog.py` | Downloads O*NET® 30.3 Excel zip by default; writes catalog. DP-ONET overrides this with `--onet-zip-url` pointing at 31.0 (see the O*NET® pin note in §8); the default is unchanged for other users |
| O*NET® consumers | `tools/build_ontology_snapshot.py`, `tools/build_universal_capability_benchmark.py`, `tools/build_maximum_sandbox_matrix.py` | Expect generated catalog |
| Generated O*NET® catalog | `config/generated/universal-work-ai-catalog.json` | **Missing** (tool not run / not committed) |
| User data package planner | `server/data-rights-policy.ts` → `createDataPackagePlan` | Consent-gated **plan only**; blocks sensitive/third-party PII |
| API templates | `GET /api/data-packages`, `POST /api/buddy/data/package-plan` in `server/routes.ts` | Templates; `populatedDatasetCount: 0`; no sale |
| Monetization bot profile | `bots/data-monetization.md` | Profile; **Production ready: False** |
| HF study packs (adjacent) | `tools/build_hf_*_packages.py`, `reports/HUGGINGFACE_MASTERY_TRACK.md` | `study_packs/` not materialized |

**Verdict:** Strong **policy + planning** layer; weak **executable synthesizer → owned store → sellable SKU** path. No production marketplace listing with real datasets.

---

## 3. Proposed SKUs (sellable package types)

Prefer packages whose payload is **DreamCo-original synthesis + lawfully redistributable source extracts** (e.g. O*NET® fields under their published terms + attribution), not wholesale third-party corpora.

| SKU id | Name | Primary contents | Allowed source classes | Customer use |
| --- | --- | --- | --- | --- |
| `DP-ONET-OCC-SYN` (internal id) | DreamCo Occupation Synthesis Pack (built with O*NET® 31.0 data) | DreamCo task→capability maps, practice tasks, rubrics, occupation cards; pinned O*NET® version + attribution | `us_gov_onet`, `dreamco_original_synthesis` | Train/eval bots on occupational tasks |
| `DP-ONET-SKILL-GRAPH` | Skills & Work-Activities Graph Pack | Normalized skill/knowledge/ability/work-activity graphs + DreamCo transfer tasks | same | Capability routing / curriculum |
| `DP-MULTI-VIEW-LESSON` | Multi-View Lesson Pack | Original lessons (human + machine layers per rewrite standard) from ≥N independent perspectives | `public_domain`, `open_commercial`, `dreamco_original_synthesis`; reference-only for restricted sources | Courseware / RAG / student adapters |
| `DP-BENCH-HOLDOUT` | Benchmark & Holdout Pack | Original evaluation tasks + rubrics derived from concepts (not copied proprietary quizzes) | `dreamco_original_synthesis` (+ attributed open fixtures) | Eval / contamination-safe holdouts |
| `DP-BOOTCAMP-GAIN` | Sandbox Gain Library (internal→paid later) | Verified gains, strategies, failure recoveries (no secrets) | `dreamco_experiment`, `dreamco_original_synthesis` | Fleet improvement; later B2B |
| `DP-HF-STUDY` | HF Capability Study Pack (metadata + evals) | Pins + evals + DreamCo cards; **weights only if license allows** | `open_commercial` HF licenses; else metadata/eval only | Aligns with HF mastery track; not “all of HF” |
| `DP-DOMAIN-SYN` | Domain Synthesis Pack (per division) | Division-specific original notes/tasks (coding, gov services, creative, etc.) | Allowed sources + synthesis only | Vertical SKUs |

**Display name (2026-10-05 CT):** Irean Jordan approved option A from `reports/DATA_PACKAGE_LICENSE_QA_REVIEW.md` §1.4, so the buyer-facing name of `DP-ONET-OCC-SYN` is "DreamCo Occupation Synthesis Pack (built with O*NET® 31.0 data)". The SKU id `DP-ONET-OCC-SYN` is internal only; a buyer-facing id is decided before any listing. Other SKU names that put O*NET® first (for example `DP-ONET-SKILL-GRAPH`) need the same treatment before they are shown to buyers.

**Non-SKU / blocked:** full copyrighted book dumps, Codecademy lesson text copies, proprietary course HTML, user PII, credentials, scraped paywalled content.

Pricing (planning only — no live Stripe SKUs claimed): preview free sample → Standard / Professional / Premium tiers per `dataset_evaluation_scorecard.json` minimum scores (75 / 85 / 92) after release gates.

---

## 4. Multi-view → original DreamCo perspective pipeline

Reuse existing policy; complete the missing executable middle.

```text
SOURCES (many perspectives)
  official docs | OSS | papers | exercises | case studies | security/perf reviews |
  O*NET® data | public domain | open commercial | failure cases | cross-model results
        ↓
COLLECT + NORMALIZE CLAIMS   (multi_perspective_policy.pattern_pipeline)
        ↓
LICENSE / PROVENANCE GATE    (evidence_provenance + training-data-provenance-policy)
  allow_commercial_redistribution? → yes / no / reference_only
        ↓
SYNTHESIZE ORIGINAL ASSET    (Knowledge Rewrite Standard layers)
  human lesson + machine skill objects + practice + transfer tasks
  DreamCo analysis: agree / reject / improve / still-need-test
        ↓
VALIDATE                     (sandbox → benchmark → holdout → regression)
        ↓
STORE AS OWNED DREAMCO DATA  (knowledge store partitions + provenance ledger)
        ↓
PACKAGE BUILD                (dataset_product_standard release artifacts)
        ↓
SELLABLE GATE                (scorecard + maximal testing + hard fails)
        ↓
LIST / LICENSE / FULFILL     (capability marketplace + data-monetization path)
```

**Book analogy (canonical):** research many works → learn → write **your own** expression and analysis (`DREAMCO_KNOWLEDGE_REWRITE_STANDARD.md`).

---

## 5. Storage schema (owned DreamCo knowledge store)

Extend conventions already in-repo; do not invent a second library.

### 5.1 Recommended layout (under existing trees)

```text
data/dreamco_knowledge/                 # owned synthesis + packages (gitignored bulky blobs OK)
  assets/{asset_id}/
    asset.json                          # machine layer + provenance
    lesson.md                           # human layer
    tasks.jsonl
    provenance.json                     # evidence_provenance.v1
    license_gate.json                   # pass/fail + basis
  packages/{sku_id}/{version}/
    manifest.json                       # sellable package manifest
    LICENSE
    dataset_card.md
    provenance_manifest.json
    license_manifest.json
    quality_report.json
    benchmark_report.json
    sample/
buddy/learning/                         # code + policies (already)
config/generated/                       # O*NET® catalog, package indexes
capabilities/                           # capability package schema (extend or sibling)
```

### 5.2 Core records (fields to implement)

**Synthesis asset** (extends `study_data_schema` + rewrite standard):

- `asset_id`, `title`, `capability_ids`, `perspectives_used[]`, `source_refs[]` (pinned)
- `ownership_class` ∈ training-data-provenance ownership_classes
- `commercial_redistribution_allowed`, `attribution_required`, `share_alike_required`
- `human_layer`, `machine_layer`, `dreamco_analysis`
- `validation`: sandbox / benchmark / holdout / regression evidence ids
  - Implemented as `validation_evidence_ids` with the four lists. Each id is `<kind>:<asset_id>:<YYYYMMDD>-<NN>`. Its kind must equal the list key, and its asset_id must equal the record's. The id resolves to `<repo_root>/<evidence_root>/<kind>/<asset_id>/<YYYYMMDD>-<NN>.json`.
  - Optional `evidence_root` is a repo-relative POSIX directory, default `data/dreamco_knowledge/evidence`. It may not have a leading `/`, `..` segments, or backslashes.
  - The file must be a `config/evidence_provenance_schema.json` record with `evidence_id` equal to the id, plus `split`, `n_items`, `metric`, `score`, `threshold`, and `passed`.
  - `tools/license_provenance_gate.py` resolves every id. Use `--repo-root` to point it at another tree. The resolved path must stay inside the repo root.
  - A malformed or unresolvable id fails `synthesis_asset_record` at sale scope, capping the outcome at approved_for_private_use. Only resolved records with `passed: true` count toward the minimum. A record that resolves but has `passed` false or any other non-true value is listed in the check reasons (`<id> resolved but passed is not true`) and does not count. That alone does not fail the check. If too few records pass, the check fails at sale scope, never as a rights failure. A record with no `passed` field is non-conforming and fails as a missing field.
  - Holdout records (kind `holdout`) are human-graded and produced on a shared box, so the producer's own scorer and verifier cannot be the trust boundary. Remote verification is mandatory for sale (`holdout_verification.required_for_sale: true`): if the asset relies on any holdout record with `passed: true` (whether or not it is needed to reach `min_validation_evidence_ids`), then without `--verify-holdout-remote`, or when verification fails, `synthesis_asset_record` fails at sale scope with the reason `holdout evidence not remotely verified; required for sale` and the outcome is capped at approved_for_private_use (never a rights failure). Holdout records with `passed` not true are not relied on, and regression, sandbox and benchmark records count exactly as before. With `--verify-holdout-remote`, the gate verifies each counting holdout record itself (config `config/license_provenance_gate.json#holdout_verification`: canonical remote `https://github.com/DreamCo-Technologies/Dreamcobots`, allowed branches `main` and `edu-career-pathways/majors-onet-study-plans`). It never imports or runs the producer's `verify_holdout.py`. It runs `/usr/bin/git` (root-owned, never looked up on PATH) in an environment built from scratch: empty HOME/XDG, `GIT_CONFIG_NOSYSTEM=1`, `GIT_CONFIG_GLOBAL=/dev/null`, no proxy variables, `protocol.file.allow=never`, and only https allowed. It runs `ls-remote` on the canonical URL and does a full fetch of the allowed tips (blobs included, not blobless) into a fresh temporary bare repository. It then requires all of these:
    - `grading_commit` is an ancestor of the record's allowed branch tip.
    - Optional signer check, off by default. `required_signer_fingerprints` (empty) and `ssh_allowed_signers_file` (empty) are placeholders until the grader registers a key. When either is set, `grading_commit` **and** the commit that introduced the `GRADING_FINAL.txt` bytes present at `grading_commit` (if that is a different commit) must each carry a good, valid signature from a listed signer, checked with `git verify-commit` in the sanitized git environment. OpenPGP: `/usr/bin/gpg` in a fresh GNUPGHOME holding only the armored keys in `signer_public_keys` (default `config/holdout_signer_keys.asc`, not yet created), and the signing or primary key fingerprint (40 hex) must be listed. SSH: `/usr/bin/ssh-keygen` with `gpg.ssh.allowedSignersFile` set to `ssh_allowed_signers_file` (the principal must match, `namespaces="git"`), or to a temporary file holding only the signing key when its `SHA256:…` fingerprint is listed. A signed later commit therefore cannot cover an unsigned sheet and declaration. Tests use throwaway SSH and GPG keys in temporary directories.
    - `REVEALED_KEY.json` is absent at `grading_commit` and in every ancestor (merges included). Across **all** allowed branches it is touched by exactly one non-merge commit (the reveal), a strict descendant of `grading_commit`, and it is never modified, removed or re-added. The key's bytes are never committed under any other path or on any other allowed branch outside the reveal and its descendants (`git log -m --find-object`). The revealed key must carry a hex nonce (a key without one is rejected), and that nonce may appear only in the reveal and its descendants: `git log -m --no-renames -S<nonce>` over every allowed tip must list no other commit, so a reformatted or relocated copy of the key committed before grading, or on another allowed branch, fails. This closes N1 from the af8b2a3 recheck (parity with the producer's `key_nonce_only_in_reveal_and_descendants`). Copies that change the nonce string (re-cased, base64, split, compressed) and key text outside committed files (commit messages, notes, tags, unmerged refs) remain residual. This means nobody can grade after the key is public. The all-branch and any-path rules were stricter than the producer's verifier at dde106b.
    - `grading_sheet.csv` and `GRADING_FINAL.txt` are byte-identical at every commit from `grading_commit` to the reveal (an edit and revert fails), and the record and results file are unchanged after the reveal.
    - Every results file, record and `FINALIZED.txt` for this key commitment, in any commit reachable from any allowed branch (files deleted later included), names this `grading_commit`: a kit is scored once.
    - Optional pinned SHAs (`expected_shas`, `expected_shas_file` in the producer's `VERIFIED_SHAS.json` format, kept outside their repository; `require_expected_shas` false by default): when a pin exists, `grading_commit` and the reveal commit must be identical and the pinned `remote_tip_sha` must still be reachable from the branch tip, so a force-push that rewrites history fails.
    - sha256(sheet) = `sheet_sha256`, sha256(`REVEALED_KEY.json`) = `key_sha256` (recomputed from the revealed key, including its nonce and seed), and items match the commitment.
    - The record equals the committed record, and `integrity_hash` matches the committed results file.
    - Score, baseline_score, n_items and passed match DreamCo's own implementation of the published pass rule. That rule is: kit-level detection ≥ 0.8, false alarms ≤ 0.2 and mean gap ≥ 1.0; per asset, ≥ 4 items of both kinds, asset detection ≥ 0.8, false alarms ≤ 0.2, agreement ≥ 0.8 and strictly above baseline, and no full-strength item judged incorrect.
  - Any mismatch or network failure is a sale-scope gap (cap approved_for_private_use, never a rights failure), and the record does not count. Tests stand in a local bare repository for the remote only through a test-only argument that never counts the record and always caps the outcome.
  - Build, hash, and pytest checks are integrity evidence, not validation.
- `integrity_hash`, `created_at`, `generator_version`

**Sellable package manifest** (align `dataset_product_standard.required_release_artifacts`):

- `sku_id`, `version`, `package_type`, `contents_digest`
- `included_asset_ids[]`, `excluded_reference_only_sources[]`
- `license_gate_status`: `pass` | `fail` | `reference_only_bundle`
- `scorecard_score`, `commercial_tier`, `known_limitations`
- `sales_channel`, `stripe_price_id` (optional, unset until wired)

### 5.3 Files to complete (stubs already exist) vs propose

| Action | Path |
| --- | --- |
| **Complete** | `buddy/learning/open_code_perspective.py` — expand `synthesize_pattern` → write asset draft + provenance |
| **Complete** | `buddy/learning/multi_perspective_policy.json` — add `sellable_output_contract` + allowed ownership classes |
| **Complete** | `buddy/learning/study_data_schema.json` — add `ownership_class`, `sellable_eligible` |
| **Complete** | `tools/score_data_package_candidate.py` — emit gate report consumed by package builder |
| **Complete** | `server/data-rights-policy.ts` + routes — keep plan-only until store + gate exist |
| **Propose (same conventions)** | `buddy/learning/multi_view_synthesizer.py` — orchestrates perspectives → rewrite layers → store |
| **Propose** | `buddy/learning/sellable_package_schema.json` — SKU manifest schema |
| **Propose** | `schemas/data_package.manifest.schema.json` — JSON Schema for CI validation |
| **Propose** | `tools/build_sellable_data_package.py` — assemble release artifacts; refuse on gate fail |
| **Propose** | `tools/license_provenance_gate.py` — shared gate used by O*NET® + HF + synthesis |
| **Propose** | `config/generated/data-package-catalog.json` — index of SKUs (empty pins OK) |
| **Run existing** | `python3 tools/build_universal_work_ai_catalog.py` → `config/generated/universal-work-ai-catalog.json` |

Do **not** create a separate `data_empire/` or parallel buddy learning tree.

---

## 6. Legal / provenance gate (plain language)

Before a SKU can be marked **sellable**:

1. **Know the source.** Every included byte traces to a pinned source or a DreamCo-generated asset with generation inputs recorded.
2. **Classify ownership.** Use `buddy-training-data-provenance-policy.json` classes. “We read it” ≠ “we own it.”
3. **Check commercial + redistribution.** Sellable requires explicit allowance (public domain, U.S. gov / O*NET® terms with attribution, open license that permits commercial reuse, or DreamCo-original). If redistribution forbidden → **reference_only** (citations + original exercises only).
4. **No copyright stripping.** Do not copy substantial protected chapters, videos, or proprietary datasets into the package.
5. **No sensitive personal data.** Align `createDataPackagePlan` blocks (minors, credentials, third-party PII, messages).
6. **Pass tests.** Provenance/rights family in maximal testing + scorecard release gates; hard fails from Data Discovery Bot scoring.
7. **Honest marketing.** Describe tested use cases, version, limitations — never “universal best dataset.”

Gate outcomes: `approved_for_sale` | `approved_for_private_use` | `reference_only` | `blocked`.

---

## 7. Sales path (honest, incremental)

| Stage | Mechanism | Evidence today |
| --- | --- | --- |
| Discover | Data Discovery Bot candidates | `config/data-discovery-bot-program.json` |
| Plan (user-owned) | `POST /api/buddy/data/package-plan` | Plan only; no listing |
| Templates | `GET /api/data-packages` | `populatedDatasetCount: 0` |
| Capability install | Capability package marketplace config | Bootcamp stages designed |
| Monetization profile | `bots/data-monetization.md` | Not production-ready |
| Checkout (future) | Stripe paths used by model packs (`client` AIModelsPage) | Reuse pattern; do not claim data SKUs live |
| Fulfillment (future) | Versioned tarball / signed manifest + license card | Not built |

**Week-1 sales truth:** sell **samples / waitlist / plan manifests**, not claimed live dataset inventory.

---

## 8. MVP — Week 1 (by ~2026-09-28 CT)

Numbered, evidence-backed, no `production_ready` flips:

1. Run O*NET® catalog generator (online or document offline blocker); commit or gitignore policy for `config/generated/universal-work-ai-catalog.json`.
2. Add `tools/license_provenance_gate.py` stub: input candidate → output `pass|fail|reference_only` using ownership classes + commercial/redistribution flags.
3. Add `buddy/learning/multi_view_synthesizer.py` stub that reads `multi_perspective_policy.json`, calls extended `synthesize_pattern`, writes one **sandbox** asset under `data/dreamco_knowledge/assets/_mvp_demo/` with provenance.
4. Define one SKU stub `DP-ONET-OCC-SYN` v0.0.1 manifest (empty payload OK) + license gate must run.
5. Wire `score_data_package_candidate.py` example candidate JSON for O*NET®-derived synthesis (rights_basis = O*NET® data + dreamco_original).
6. Document in package README: blocked categories + book analogy + hard no on copyright stripping.
7. Align naming with capability marketplace + dataset product standard (no new product brand).
8. Evidence packet: `reports/DATA_PACKAGE_WEEK1_EVIDENCE.md` listing files touched, gate results, zero false “for sale” claims.

**Status on restore (2026-10-02 CT):** items 1 (catalog generates; 30.3 pin, 31.0 verified compatible; commit-vs-gitignore decision still open), 2, 4, and 5 are done on branch `feat/data-package-gate-skeleton`, with the gate's real outcome on an O*NET®-derived study plan sample (`reference_only` as-is, `approved_for_private_use` once provenance files were added). Item 3 (multi-view synthesizer) is not started. The week slipped about a week.

**O*NET® pin for DP-ONET (2026-10-03 CT):**
- DP-ONET-OCC-SYN 0.0.1 pins **O*NET® 31.0**:
  - `db_31_0_excel.zip`, sha256 `c63ad00a8e45f3d3ef8e1529fcf8864d2279f2dfcb98737436818f5664781b04`
  - `db_31_0_csv.zip`, sha256 `55033fc68b4c13ec23e7f74dc6378660f6e854e75d55d6e333ae0a761d3987cd`
  - Both are under `https://www.onetcenter.org/dl_files/database/`. The crosswalk xlsx pin is in the package `provenance_manifest.json`.
- The per-file pins in the edu_cs_11.0701 asset `provenance.json` match the files inside the CSV zip.
- The fleet ingest tool keeps its 30.3 default, so no other user changes. DP-ONET overrides it with `--onet-zip-url https://www.onetcenter.org/dl_files/database/db_31_0_excel.zip`, the less invasive option.
- The tool reads only Occupation Data and Task Statements, so it works with 31.0 unchanged.
- 31.0 replaces the single Skills file with **Essential Skills** (2.A.*) and **Transferable Skills** (2.B.*). There is no `skills.csv` or `Skills.xlsx`, so skill-based assets must name which file they use.

---

## 9. Realistic timeline (product path)

| Window | Outcome |
| --- | --- |
| Week 1 | Gate + synthesizer stub + 1 SKU manifest; O*NET® catalog generated |
| Weeks 2–4 | First internal package with sample records; scorecard ≥ prototype; no live charge |
| Oct 2026 | Private beta: 1–2 SKUs (O*NET® synthesis + multi-view lesson) behind owner approval |
| Nov–Dec 2026 | Paid fulfillment stub (Stripe price + download of gated zip) **only after** release gates green |
| YE 2026 | Repeatable package factory for allowed sources; still no claim of “all knowledge licensed” |

See `reports/ONET_MASTERY_TRACK.md` for O*NET® days-to-ops-mastery and HF track for Hub reminder.

---

## 10. Top product risks

- Catalog configs look complete while **runtime store and gate** are missing → overclaim risk.
- Codecademy / proprietary course text must stay **lens only** (`buddy_github_onet_codecademy_benchmark_system.json` already says do not copy proprietary course text).
- HF packs may include weights only when license permits; default is metadata + DreamCo evals (`HUGGINGFACE_MASTERY_TRACK.md`).
