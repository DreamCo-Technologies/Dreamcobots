# Stage 02 Curriculum Factory

## Scope

The factory assembles deterministic study-guide draft artifacts from independently authored lesson fields. It does not call an LLM, download media, fetch transcripts, execute learner code, or publish courses.

## Rights boundary

The factory calls the existing Stage 01 `evaluate_source(..., purpose="fact_extraction")` policy gate for the exact catalog record. The catalog record must include a verified item-level license tag and SHA-256 fingerprint. The current FreeCodeCamp registry is `FACT_EXTRACTION_ONLY`: this can permit carefully bounded fact extraction when item-level evidence exists, but it does not grant transcript extraction or commercial training rights. Missing or unknown item-level evidence fails closed.

Every output remains a draft. Commercial release is explicitly false. Owner review and separate commercial rights evidence are still required before publication.

## Originality screen

The factory uses eight-token n-gram candidate containment with a default threshold below 4%. It requires a non-empty reference set and quarantines drafts that meet or exceed the threshold. This is a heuristic similarity screen, not proof of originality, non-infringement, or legal clearance. Human review remains mandatory.

## Artifacts

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
