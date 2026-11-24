# Weekly Buddy transcript evaluation

## Requirement

Every transcript in the canonical, rights-approved transcript manifest must receive at least one real Buddy evaluation during every ISO week. The weekly target is **100% coverage**, not a sample.

## Source and rights boundary

- The canonical input is `config/authorized-transcripts/manifest.json`.
- Each entry must identify the transcript, its SHA-256 digest, source URL, division coverage, and a non-empty rights evidence reference.
- A public video URL, catalog entry, or publicly viewable caption is not permission to ingest, retain, redistribute, or train on a transcript.
- Transcript evaluation permission and model-training permission are separate. Evaluation must not silently enable training.
- Do not fetch or create transcript text as part of metadata discovery. Only evaluate transcript files already admitted through the approved manifest.

## Required evaluation evidence

Each real evaluation must record transcript ID and digest, Buddy model ID and version, evaluation-suite version, UTC start/end timestamps, result (passed/failed/error), numeric score, workflow run ID, and rights evidence reference. The digest must match the approved manifest so changed transcripts become due again.

## Honest status reporting

The weekly workflow can build a due-work report from the manifest and ledger. It must never mark a transcript tested merely because it was discovered, queued, parsed, or checked by a schema validator. A missing transcript manifest or unconfigured Buddy inference adapter is reported as blocked, not passed. The integration must fail closed until a real evaluator is registered.

## Current integration state

The freeCodeCamp catalog is metadata-only. It does not provide transcript text, and no transcript corpus or real Buddy transcript-evaluation adapter is currently registered by this change. Therefore this policy establishes the weekly acceptance contract; it does not claim that transcript evaluations have already run.
