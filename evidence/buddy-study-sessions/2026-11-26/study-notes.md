# Buddy tokenizer study notes — 2026-11-26

## Scope

This session studied only first-party DreamCo instructional material and used the repository's original synthetic CI corpus. The external-reference section in the course guide was excluded. No third-party videos, transcripts, captions, datasets, gated content, credentials, or paid services were used.

## Original lesson summary

A tokenizer turns text into a sequence of units that a downstream model can consume. A reliable pipeline makes each transformation explicit: preserve the raw input, decide whether normalization is permitted, establish pre-tokenization boundaries, segment into bytes or subwords, map units into a vocabulary, and decode when exact reconstruction is required.

The repository's byte-level BPE trainer starts with all 256 byte values. It counts adjacent byte-token pairs, chooses the most frequent pair, breaks ties deterministically, merges occurrences from left to right, and records each merge. Encoding starts from UTF-8 bytes and applies the recorded merges in order. Decoding concatenates the resulting byte strings and decodes UTF-8. Because every byte value exists in the base vocabulary, valid UTF-8 input can be represented without an unknown byte token.

Unicode normalization is not harmless cleanup. NFC can compose code points, and NFKC can fold compatibility characters such as full-width letters or ligatures. The current trainer does not normalize, which preserves exact input in the round-trip tests. It also does not provide source offsets, a separate numeric token-ID table, pre-tokenization, special-token registration, or model-checkpoint compatibility.

Vocabulary size is a measured trade-off. More merges can reduce token count, but a larger vocabulary increases downstream embedding-table requirements and can change model compatibility. A candidate should be chosen on validation data, then evaluated once on a separate holdout. The holdout must not participate in fitting or vocabulary selection.

Corpus acceptance is fail-closed: require a unique source ID, local path confinement, explicit rights and training permission, privacy review, non-sensitive and non-holdout declarations, an allowed source type, a rights-evidence reference, exact SHA-256, and valid UTF-8. Study permission, derivative permission, evaluation permission, and model-weight training permission remain distinct.

A tokenizer artifact is not a neural model checkpoint. This run trained a tokenizer on the synthetic CI corpus only; it did not change Buddy's model weights, perform distillation, or certify any division as mastered.

## Worked BPE example

For the synthetic string `banana bandana banana`, the highest-frequency adjacent pair is `an` (6 occurrences). The trainer records the merge as bytes `61` + `6e` → `616e`, then repeats the deterministic merge process until the configured vocabulary size or no pair occurs at least twice.

## Practical results

- The exact repository trainer was executed against the synthetic CI manifest.
- A validation sweep compared vocabulary sizes 256, 320, 384 and 512.
- Vocabulary size 384 was retained as a conservative smoke candidate: 128 merges and 602 validation tokens across 90 validation words, compared with 753 tokens for the 256-byte baseline.
- A fresh 12-example synthetic holdout was created after selection and evaluated once: 12/12 exact round trips.
- Invalid UTF-8 was rejected; the rights, path, hash, holdout and explicit-confirmation gates were exercised.
- The local regression suite passed 10/10 tests after the CI path-scope fix was prepared.

## Lesson completion boundaries

- `tok-03`, `tok-04`, `tok-06`: completed for the BPE/byte-coverage/rights-gate scope exercised here.
- `tok-01`, `tok-02`, `tok-05`, `tok-11`, `tok-12`: partially completed; offset maps, reversible normalization metadata, embedding-cost analysis, representative per-language evaluation, and rollback restore remain open.
- `tok-07`, `tok-08`, `tok-09`, `tok-10`: blocked; the specified third-party tokenizer libraries were not installed or used, special-token/chat-template support is absent, and no model checkpoint compatibility runner is available.

## Assessment and truth boundary

The active-recall score was 16/16 and the selected-lane transfer tasks scored 12/12. These are self-checked ChatGPT study-proxy answers, not outputs from a Buddy model inference session. Buddy model inference was not available in this run. No mastery claim is made.
