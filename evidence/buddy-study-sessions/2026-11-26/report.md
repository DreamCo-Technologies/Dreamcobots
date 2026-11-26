# Buddy bounded study session — 2026-11-26

**Session:** `buddy-study-2026-11-26-0802-ct`  
**Source commit:** [`dba9177b5423c2a1dfd7729ca888c00505b3399b`](https://github.com/DreamCo-Technologies/Dreamcobots/commit/dba9177b5423c2a1dfd7729ca888c00505b3399b)  
**Status:** bounded study executed; partial curriculum coverage; no mastery claim

## What was actually done

- Studied three first-party DreamCo documents: the tokenizer course guide, the byte-BPE trainer guide, and the universal learning/evidence guide. The external-reference section of the course guide was excluded.
- Extracted **22 original glossary entries**.
- Completed an **8-question active-recall self-check: 16/16 (100%)**.
- Completed **12 selected MasterBot transfer exercises: 12/12 (100%)**. These were authored and scored by the ChatGPT study proxy, not by Buddy model inference.
- Ran the repository's exact byte-level BPE trainer on the original synthetic CI corpus, using the rights-gated manifest and explicit confirmation flag.
- Compared vocabulary sizes 256, 320, 384 and 512 on a separate synthetic validation set. Selected 384 as a conservative smoke candidate; it is not a production optimum.
- Evaluated a newly created, independent synthetic holdout **once after selection**: **12/12 exact round trips**. Invalid UTF-8 was rejected.
- Ran the trainer regression suite plus new workflow-scope tests locally: **10 passed, 0 failed**.
- Repeated the same tokenizer run and obtained an identical output hash. The CLI refused to run when the explicit confirmation flag was omitted.

## Tokenizer result

| Measure | Result |
|---|---:|
| Source corpus | 3,155 bytes |
| Source SHA-256 | `8a81744f145294343b3091292d6f4a11d2a05e317cf8ee15a6825129ebaf278e` |
| Algorithm | deterministic byte-level BPE |
| Selected vocabulary | 384 tokens |
| Learned merges | 128 |
| Validation | 602 tokens / 90 words; exact round trips at all four tested sizes |
| Fresh holdout | 12 / 12 exact round trips |
| Final tokenizer SHA-256 | `759cf1c1e203cf6569d9bdf523c956bcfbf1db16cce5326da13783c37698b721` |
| Reproducibility | identical output hash on repeat |
| Model-weight training | **not executed** |
| Model checkpoint hash | none |

The synthetic corpus manifest marks this fixture as CI-only, non-production and not authorized for neural model-weight training. The run created a tokenizer artifact only.

## Division and lane coverage

The canonical registries were reconciled as **55 domain profiles** (45 core proposed owner mappings and 10 supplemental unresolved mappings) and **65 MasterBot lanes** (45 domain-owner lanes and 20 shared-platform lanes).

- **7/55 domain divisions** received a selected shared-foundation transfer activity; **48/55** are explicitly blocked for this run.
- **12/65 MasterBot lanes** received a selected shared-foundation transfer activity; **53/65** are explicitly blocked for this run.
- The 10 supplemental profiles remain owner-mapping unresolved. No ownership or route was changed.
- The shared course configuration declares a foundation mapping for all 55/65; that is not evidence that each division independently studied or mastered it.

See [`artifacts/division-coverage.json`](artifacts/division-coverage.json) for every division and lane, with its exact status and reason.

## Lesson status

- **Completed for the scope exercised:** `tok-03`, `tok-04`, `tok-06`
- **Partially completed:** `tok-01`, `tok-02`, `tok-05`, `tok-11`, `tok-12`
- **Blocked:** `tok-07`, `tok-08`, `tok-09`, `tok-10`

The blocked lessons require additional library support, special-token/chat-template implementation, or a real model checkpoint compatibility runner. Offset mapping, embedding-cost analysis, representative per-language evaluation and rollback restore remain open.

## Verified repository defect fixed in this branch

The byte-BPE test workflow did not trigger when files under `data/buddy-authorized-corpora/` changed, so a changed rights manifest or corpus could bypass the targeted regression suite. The branch adds that path to the workflow filter, adds a regression test, and runs both test modules. No trainer algorithm change was needed.

## Failures and remediation

1. An exploratory vocabulary sweep initially used a provisional holdout for model selection. That set was reclassified as validation, and a fresh holdout was generated and evaluated only after the 384 candidate was selected. The contaminated holdout was not used for training.
2. A first worked-example reporting snippet used `.decode()` on integer byte values. The reporting snippet was corrected; repository code was unaffected.
3. Python startup emitted an unrelated spreadsheet-runtime warmup warning. The unit-test process returned 0 and all 10 tests passed.

## Safety and limitations

- No external material, transcript, gated content, secrets, customer data, paid compute, network download, or model-weight training was used.
- The first-party seed lesson JSONL was not used: its records remain drafts with empty answers and row-level training permission not granted.
- The external video catalog was not used: its inventory is partial and item-level rights/derivative permissions were not verified.
- Buddy model inference was not available in this run. All active-recall and transfer answers are ChatGPT study-proxy outputs; they are not Buddy's independent responses.
- No division mastery, production readiness, model training, or deployment is claimed.

## Evidence artifacts

- [`session.json`](session.json) — versioned session manifest, source provenance, lesson activity records, hashes, scores, tests, failures and timestamps.
- [`study-notes.md`](study-notes.md) — original lesson summary and worked BPE example.
- [`artifacts/glossary.json`](artifacts/glossary.json) — 22 original glossary definitions.
- [`artifacts/active-recall.json`](artifacts/active-recall.json) — 8 questions, rubric and proxy score.
- [`artifacts/division-coverage.json`](artifacts/division-coverage.json) — all 55 domain divisions and 65 MasterBot lanes.
- [`artifacts/lane-transfer-activities.json`](artifacts/lane-transfer-activities.json) — the 12 selected lane-specific transfer tasks, answers, scores and evidence hashes.
- [`artifacts/tokenizer-training-run.json`](artifacts/tokenizer-training-run.json) — rights provenance, configuration and output hashes.
- [`artifacts/tokenizer-final-vocab-384.json`](artifacts/tokenizer-final-vocab-384.json) — final tokenizer artifact.
- [`artifacts/validation-fixture.jsonl`](artifacts/validation-fixture.jsonl) and [`artifacts/validation-sweep.json`](artifacts/validation-sweep.json) — validation-only vocabulary comparison and split remediation.
- [`artifacts/validation-sweep.json`](artifacts/validation-sweep.json) records output hashes for all four vocabulary runs; only the selected 384-token artifact is retained as a model file.
- [`artifacts/holdout-fixture.jsonl`](artifacts/holdout-fixture.jsonl) and [`artifacts/holdout-evaluation.json`](artifacts/holdout-evaluation.json) — fresh independent synthetic holdout and results.
- [`artifacts/sandbox-test-results.json`](artifacts/sandbox-test-results.json) — unit tests, negative checks, reproducibility and warnings.

All evidence is tied to source commit `dba9177b5423c2a1dfd7729ca888c00505b3399b`. PR CI must still complete on the evidence branch before the change is merge-ready.
