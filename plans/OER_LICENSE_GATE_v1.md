# OER License Gate v1 — OpenStax / MIT OCW / general OER

**Owner:** Grok-Edu-OER-Ingest (SET 7)  
**Hard rule:** Never strip licenses for sale.  
**Aligned with:** `dreamco.buddy_training_data_provenance.v1`, LP-factory sellable gate, evidence provenance schema.

## Purpose

Ingest open courseware (OpenStax, MIT OCW, and other OER) with an immutable license/provenance record, then allow only license-compliant paths into:

1. **internal study / Bootcamp** (non-sale)
2. **attribution-preserving open remix** (free/open packages)
3. **sellable DreamCo-original synthesis** (marketplace SKUs)

Sellable products must not launder third-party expression under a DreamCo brand or strip required attribution/license notices.

## Source license facts (as of 2026-09-21)

### OpenStax
- **Per-title, never catalog-wide.** Many titles are **CC BY 4.0** (commercial reuse allowed with attribution). Some titles (e.g. Principles of Accounting) are **CC BY-NC-SA 4.0**.
- OpenStax help center also documents a general NC-SA framing — **always read the book's own preface / license line**.
- OpenStax **name, logo, and covers** are **not** under the CC license; do not reproduce marks without Rice University consent.
- Art/figures may have separate rights; reuse only when credit/limitations allow.

### MIT OpenCourseWare
- Default: **CC BY-NC-SA 4.0**.
- **Non-commercial:** may not sell, profit from, or commercialize OCW materials **or works derived from them**.
- Use vs user: a for-profit entity may use OCW for **internal** training if the use itself is not commercialization.
- Attribution + ShareAlike required for reuse/derivatives under the license.
- Fee-based commercial courses built on OCW materials are prohibited under MIT's NC guidance.

### Common OER / CC matrix (ingest classifier)

| License | Internal study | Open remix (free) | Sellable with verbatim excerpts | Sellable original synthesis* |
|---------|----------------|-------------------|---------------------------------|------------------------------|
| CC0 / public domain | allow | allow | allow | allow |
| CC BY | allow | allow + attribution | allow + attribution + license notice | allow (record concept provenance) |
| CC BY-SA | allow | allow + SA on derivatives | allow only if product license compatible with SA | allow if no substantial SA expression copied |
| CC BY-NC | allow | allow (non-commercial) | **deny** | allow only if **no substantial licensed expression** in SKU |
| CC BY-NC-SA | allow | allow + SA (non-commercial) | **deny** | allow only if **no substantial licensed expression** in SKU |
| unknown / missing | quarantine | deny | **deny** | **deny** until classified |

\*Original synthesis = DreamCo-authored expression of ideas/facts (not copyrightable as such), with provenance of *concepts studied*, zero (or de minimis fair-use — **not** the product strategy) copied wording/structure. Prefer full rewrite + human review over fair-use claims.

## Never-strip rule

For any redistributed OER excerpt or licensed derivative package:

1. Keep `license`, `license_url` / SPDX, and `attribution_text` on the asset and on every export manifest.
2. Never rewrite ownership to `dreamco_owned` merely because we ingested or learned from it.
3. Preserve NOTICE / credit lines; do not strip HTML/PDF license footers in archives labeled for redistribution.
4. Marketplace listings must surface license + attribution metadata (same spirit as Buddy marketplace provenance policy).

## Ingest metadata schema (`dreamco.oer_license_gate.v1`)

Required fields:

- `source_id` — stable id (e.g. `openstax:statistics:2e`, `mit-ocw:6.006`)
- `title`, `source_org` (`openstax` | `mit_ocw` | `other_oer`), `canonical_url`
- `license_spdx` or CC URI (e.g. `CC-BY-4.0`, `CC-BY-NC-SA-4.0`)
- `license_version`, `license_url`
- `commercial_ok` (bool), `derivatives_ok` (bool), `share_alike` (bool), `attribution_required` (bool)
- `attribution_text` (machine + human form)
- `marks_excluded` (bool — OpenStax marks, MIT marks, etc.)
- `retrieved_at`, `license_evidence_url` (preface/terms page snapshotted)
- `classifier_confidence` (`high` | `medium` | `low`)
- `review_status` (`auto_pass` | `needs_human` | `quarantine` | `blocked`)
- `provenance_hash` (hash of payload + license fields)
- `allowed_modes` — subset of `internal_study`, `open_remix`, `sellable_original_synthesis`, `sellable_verbatim_bundle`

Ownership class mapping (Buddy provenance):

- Verbatim OER store → `open_license_with_conditions` or `third_party_reference_only`
- DreamCo rewrite for sale → `synthetic_generated_by_dreamco` / `dreamco_owned` **only after** rewrite gate + human review; source inputs recorded in `transformation_history`
- Unknown → `unknown_do_not_publish`

## Pipeline stages

```
discover
  → license_classify (per-title; snapshot evidence URL)
  → quarantine_if_unknown_or_low_confidence
  → allow_list_modes (matrix above)
  → ingest_store (immutable provenance record)
  → synthesis_router
       ├─ internal_study
       ├─ open_remix (preserve license + SA)
       └─ sellable_path
            → originality_gate (no NC/SA expression leakage)
            → attribution_bundle (concept provenance only for NC sources)
            → sellable_export_gate (marketplace)
```

### Sellable export gate (fail closed)

Block export if any of:

- `commercial_ok == false` **and** SKU contains substantial licensed expression
- `review_status` in `quarantine` | `blocked` | `needs_human` (until cleared)
- missing `attribution_text` / `license_url` on any included third-party excerpt
- ShareAlike conflict across combined works without a compatible outbound license
- OpenStax/MIT **marks** included without separate permission
- ownership falsely labeled `dreamco_owned` for third-party text

## OpenStax / OCW operational defaults

| Source | Default classifier | Sellable default |
|--------|--------------------|------------------|
| OpenStax | **Must read title preface**; do not assume BY or NC-SA | Verbatim commercial only if title is CC BY (or commercial permission granted); NC titles → original synthesis only |
| MIT OCW | Assume **CC BY-NC-SA 4.0** unless page says otherwise | **No** verbatim or derived-expression SKUs; internal study OK; sellable = DreamCo-original only with concept provenance |
| Other OER | Classify from license URI; unknown → quarantine | Fail closed |

## Failure modes

| Condition | Action |
|-----------|--------|
| Unknown / conflicting license text | Quarantine; no sale; no open remix |
| NC source in commercial SKU with copied expression | Block; require rewrite or drop |
| SA derivative mixed with incompatible proprietary SKU license | Block combination |
| Attribution stripped in packaging | Block; regenerate with NOTICE |
| Marks (logos/covers) in product | Block without written consent |

## Proposed repo layout

```
plans/edu-oer-ingest/
  OER_LICENSE_GATE_v1.md          # this doc
  schemas/oer_license_gate.v1.json
  matrices/allow_deny.v1.json
```

Mirror under Empire HQ board when ready; do not push until SET owner asks.

## Open questions / risks

1. OpenStax catalog license drift (help center vs per-book preface) — require evidence snapshot per title.
2. "Original synthesis" detection — need similarity / human-review bar before sellable_ok.
3. Whether paid Buddy Bootcamp access that *mentions* OCW concepts counts as commercial derivative (MIT: use-based; internal OK; selling courses *based on OCW materials* is called out as prohibited — keep Bootcamp lessons DreamCo-authored).
4. Coordination with Data-Package-Merchant + LP-factory sellable gate for one shared export checklist.
