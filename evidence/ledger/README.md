# Production-readiness evidence ledger — entry shape (v0.1)

**Rule:** No `production_ready` without linked soak + CI + runtime proof. No vanity greens.

## Entry schema

Every ledger row is one **claim** bound to **artifacts** at a **SHA**, with mandatory **soak** (and CI + runtime) links. Incomplete rows cannot certify.

```json
{
  "entry_id": "el-<yyyyMMdd>-<shortslug>",
  "schema_version": "0.1",
  "status": "open | evidence_incomplete | evidence_complete | cert_pending | certified | rejected",
  "claim": {
    "kind": "production_ready",
    "subject_type": "bot | plan | division | package | runtime",
    "subject_id": "string",
    "subject_name": "string",
    "asserted_ready": false
  },
  "git": {
    "repo": "owner/name",
    "sha": "40-char commit",
    "ref": "branch or tag (optional)",
    "tree_url": "https://github.com/owner/name/tree/<sha>"
  },
  "artifacts": [
    {
      "role": "ci | soak | runtime | gate_doc | other",
      "name": "string",
      "uri": "https://... or repo path @ sha",
      "content_hash": "sha256:... (optional but preferred)",
      "recorded_at": "ISO-8601"
    }
  ],
  "ci": {
    "required": true,
    "run_url": "https://...",
    "workflow": "string",
    "conclusion": "success | failure | cancelled | skipped | unknown",
    "checks_green_only_if": "same SHA as git.sha; no rebased/main-only greens"
  },
  "soak": {
    "required": true,
    "run_id": "string",
    "uri": "https://... or path @ sha",
    "started_at": "ISO-8601",
    "ended_at": "ISO-8601",
    "duration_ok": true,
    "result": "pass | fail | inconclusive",
    "notes": "string"
  },
  "runtime": {
    "required": true,
    "proof_uri": "https://... or path @ sha",
    "environment": "sandbox | canary | prod-candidate",
    "observed_at": "ISO-8601",
    "result": "pass | fail | inconclusive"
  },
  "anti_vanity": {
    "no_manual_flip": true,
    "no_green_without_sha_match": true,
    "no_cert_if_any_required_link_missing": true,
    "rejected_reasons": []
  },
  "prc": {
    "certifier": "Grok-PRC-Certifier",
    "aligned_schema": "0.1",
    "decision": "pending | certify | deny",
    "decision_at": null,
    "decision_ref": null
  },
  "updated_at": "ISO-8601",
  "updated_by": "Grok-Prod-Evidence-Ledger"
}
```

## Certification gate (ledger → PRC)

PRC may flip `certified` **only if**:

1. `git.sha` is set and immutable for the claim
2. `ci.conclusion == success` **and** CI run is for that exact SHA
3. `soak.result == pass` with `uri` + duration evidence
4. `runtime.result == pass` with `proof_uri`
5. Every required `artifacts[].uri` resolves
6. `anti_vanity` checks all true; no skipped required fields

Otherwise status stays `evidence_incomplete` or `rejected`. **Never** set `claim.asserted_ready` or PRC `certify` on dashboard greens alone.

## Minimal example (incomplete — cannot certify)

```json
{
  "entry_id": "el-20260921-example-bot",
  "schema_version": "0.1",
  "status": "evidence_incomplete",
  "claim": {
    "kind": "production_ready",
    "subject_type": "bot",
    "subject_id": "example-bot",
    "subject_name": "Example Bot",
    "asserted_ready": false
  },
  "git": {
    "repo": "DreamCo-Technologies/Dreamcobots",
    "sha": null,
    "ref": null,
    "tree_url": null
  },
  "artifacts": [],
  "ci": { "required": true, "run_url": null, "workflow": null, "conclusion": "unknown", "checks_green_only_if": "same SHA as git.sha; no rebased/main-only greens" },
  "soak": { "required": true, "run_id": null, "uri": null, "started_at": null, "ended_at": null, "duration_ok": false, "result": "inconclusive", "notes": "missing" },
  "runtime": { "required": true, "proof_uri": null, "environment": "sandbox", "observed_at": null, "result": "inconclusive" },
  "anti_vanity": {
    "no_manual_flip": true,
    "no_green_without_sha_match": true,
    "no_cert_if_any_required_link_missing": true,
    "rejected_reasons": ["missing_sha", "missing_ci", "missing_soak", "missing_runtime"]
  },
  "prc": {
    "certifier": "Grok-PRC-Certifier",
    "aligned_schema": "0.1",
    "decision": "pending",
    "decision_at": null,
    "decision_ref": null
  },
  "updated_at": "2026-09-21T16:40:00-05:00",
  "updated_by": "Grok-Prod-Evidence-Ledger"
}
```

## Change control

- v0.1 draft for PRC alignment
- Ledger owner: Grok-Prod-Evidence-Ledger
- Cert decisions: Grok-PRC-Certifier only, against this shape
