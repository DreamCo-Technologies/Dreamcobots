# Stage 02 Curriculum Factory

## Scope

The factory assembles deterministic study-guide draft artifacts from independently authored lesson fields. It does not call an LLM, download media, fetch transcripts, execute learner code, or publish courses.

## Rights boundary

The factory calls the existing Stage 01 `evaluate_source(..., purpose="fact_extraction")` policy gate for the exact catalog record. The catalog record must include an approved item-level license tag, HTTPS evidence URL, repository-relative evidence snapshot path, SHA-256 matching the snapshot bytes, reviewer ID, and review timestamp. Stage 01 rejects path traversal, snapshots outside the repository, missing files, and hash mismatches. Catalog synchronization never fills these review fields automatically; new items remain `needs_human` and blocked until an owner reviews the exact item. The current FreeCodeCamp registry is `FACT_EXTRACTION_ONLY`: approved fact extraction does not grant transcript extraction or commercial training rights. Missing or unknown item-level evidence fails closed.

Every output remains a draft. Commercial release is explicitly false. Owner review and separate commercial rights evidence are still required before publication.

## Originality screen

The factory uses eight-token n-gram candidate containment with a default threshold below 4%. It requires a non-empty reference set and quarantines drafts that meet or exceed the threshold. This is a heuristic similarity screen, not proof of originality, non-infringement, or legal clearance. Human review remains mandatory.

## Artifacts

The catalog fingerprint recorded in provenance is a SHA-256 of the catalog metadata record, not a hash of the video or transcript. No media bytes are fetched or represented as verified content hashes.

Each run writes three separate JSON files:
- `<guide_id>.guide.json`: learner-facing schema only.
- `<guide_id>.provenance.json`: source identifiers, source record digest, policy decision, and media/transcript boundary.
- `<guide_id>.quality.json`: validation and originality evidence plus explicit review gates.

Writes refuse to overwrite existing files. The three artifacts are rolled back if a write fails partway through.

## Local validation

```sh
python -m unittest tests.test_curriculum_factory -v
```

No training eligibility, course approval, transcript permission, or commercial publication is inferred from a successful unit test.
