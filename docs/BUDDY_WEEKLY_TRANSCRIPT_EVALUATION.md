# Buddy weekly transcript evaluation

Buddy's weekly transcript requirement is an evaluation-coverage contract, not permission to download or ingest course material.

## Eligibility

A catalog record enters the weekly evaluation queue only when all of these are true:

- The exact transcript is marked `rights_cleared_and_ingested`.
- The rights decision is `rights_cleared`.
- An immutable, valid SHA-256 digest is recorded.
- `transcript_evaluation_authorized` is explicitly true.

All other records remain visible in the blocked list with a reason. Public video metadata, public captions, or a video URL do not establish transcript rights.

## Execution boundary

The builder creates a plan only. It does not fetch media, scrape captions, ingest transcript text, execute Buddy evaluations, or train model weights. The output contains transcript identifiers and hashes, not transcript contents. A separate approved evaluator must consume the plan and record execution evidence before any transcript can be reported as tested.

## Weekly cadence

Each eligible transcript is scheduled once in the Monday-to-Sunday window. The plan includes comprehension, grounded question answering, factual consistency, citation/provenance, and retention/transfer evaluation categories. This schedule does not claim that any evaluation has run.

## Commands

```bash
python tools/build_buddy_weekly_transcript_evaluation_plan.py \
  --catalog config/generated/freecodecamp-youtube-catalog.json \
  --output artifacts/buddy-dataset-hub/weekly-transcript-evaluation-plan.json
python -m unittest tests.test_buddy_transcript_evaluation_scheduler -v
```
