# FreeCodeCamp transcript rights and weekly Buddy test coverage

## Current status

The checked-in FreeCodeCamp metadata catalog currently contains 1,740 video entries and is marked **partial**. The authorized transcript manifest is empty. Therefore, the current state is:

- Authorized transcript files registered: 0
- Permission requests required for cataloged videos: 1,740
- Transcript downloads or caption scraping performed: none
- Weekly Buddy transcript tests evidenced: 0
- Weekly coverage status: blocked until the source catalog is complete, transcripts are authorized, and actual Buddy test evidence is recorded

## Rights-gated intake

Public YouTube metadata and public captions do not by themselves grant permission to download, store, redistribute, use for study, evaluate, or train a model on transcript text. Each transcript entry must identify the exact video URL, rightsholder permission or applicable license evidence, the local transcript file, and its SHA-256 hash.

Study permission, weekly evaluation permission, and model-training permission are separate fields. Training is not enabled by study or evaluation permission. The default policy blocks automatic caption scraping, automatic transcript downloads, and automatic model training.

Authorized transcript files must be placed under data/freecodecamp/authorized-transcripts/ and referenced from config/authorized-transcripts/manifest.json. The validator rejects path traversal, source mismatches, missing files, hash mismatches, and missing rights evidence.

## Weekly Buddy test evidence

config/authorized-transcripts/weekly-test-evidence.json records externally generated Buddy test evidence. Each record must identify the video, Buddy model and version, test suite, run ID, evaluation permission reference, timestamp, PASS status, and result SHA-256.

The weekly workflow audits that every transcript with verified weekly-evaluation permission has a passing test record from the last seven days. Missing, stale, failed, or mismatched evidence is blocked.

**Important limitation:** the audit validates submitted evidence; it does not execute Buddy or create model inference results. A real Buddy evaluation runner/model endpoint must be connected before the workflow can report complete weekly testing. The current empty manifest therefore correctly reports zero tested transcripts, not success.

## Outputs

The weekly workflow uploads transcript-intake-queue.json, weekly-buddy-test-audit.json, and summary.json.

The queue is a rights-request and intake plan, not a transcript downloader.
