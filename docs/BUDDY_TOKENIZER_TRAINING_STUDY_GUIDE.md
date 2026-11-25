# Buddy Tokenizer Engineering and Training Course

**Owner lane:** Grok-HF-Tokenizers  
**Curriculum status:** Ready for study and sandbox exercises; actual tokenizer training remains approval-gated.  
**Audience:** All 55 canonical divisions and 65 MasterBot lanes through their relevant language-model, data, platform and evaluation prerequisites.

This course expands the existing tokenizer, local-model, Hugging Face, Transformers, and model-foundry guides. It is not a separate competing curriculum. The canonical machine-readable syllabus is `config/buddy-tokenizer-training-curriculum.json`.

## Course references

- [Hugging Face Tokenizers documentation](https://huggingface.co/docs/tokenizers) — implementation reference for normalization, pre-tokenization, models, trainers, decoders and post-processors.
- [Hugging Face NLP Course: Tokenizers](https://huggingface.co/learn/nlp-course/chapter6/1) — tokenizer concepts and hands-on learning.
- [freeCodeCamp — Train Your Own LLM](https://www.youtube.com/watch?v=9Ge0sMm65jo) — broader LLM course with BPE tokenization in the data/model training sequence.
- [SentencePiece](https://github.com/google/sentencepiece) — Unigram and BPE implementation reference.

These are link-only study references. Do not copy course chapters, download captions/media, redistribute course materials, or use their contents as model-training data without item-level rights evidence. Buddy should create original explanations, examples, labs, quizzes and rubrics.

## Learning path

| Lesson | Topic | Required practical evidence |
|---|---|---|
| 1 | Text-to-token pipeline | Round-trip and offset tests |
| 2 | Unicode and normalization | Documented reversible normalization behavior |
| 3 | BPE, WordPiece and Unigram | Small-vocabulary comparison |
| 4 | Byte-level coverage | UTF-8 edge-case fixtures |
| 5 | Vocabulary design | Vocabulary-size trade-off report |
| 6 | Corpus quality and rights | Authorized source manifest and isolated splits |
| 7 | Hugging Face Tokenizers | Reproducible local BPE/Unigram artifacts |
| 8 | SentencePiece | Pinned BPE/Unigram comparison |
| 9 | Special tokens and chat templates | Atomic special-token and role-validation tests |
| 10 | Tokenizer/model compatibility | Exact tokenizer/model revision match |
| 11 | Evaluation and fairness | Held-out, disaggregated scorecard |
| 12 | Release and operations | Hash-verified release candidate and rollback record |

## Hands-on labs

1. Build a minimal character/whitespace tokenizer to understand the complete encode/decode path.
2. Train byte-level BPE and Unigram tokenizers on an original synthetic corpus. Record the exact corpus hash, seed, library version and settings.
3. Compare multiple vocabulary sizes using fertility, compression, sequence expansion and embedding-table cost.
4. Test emoji, mixed scripts, code, rare names, punctuation, combining marks and long inputs.
5. Create Buddy's chat template with explicit system, user, assistant and tool roles. Require special tokens to map atomically and reject unsupported roles.
6. Bind a tokenizer revision to a model checkpoint and prove that mismatched vocabulary or special-token hashes fail closed.
7. Evaluate by language and domain on a source-isolated holdout. Report unknown-token rate, byte coverage, fertility and sequence expansion.
8. Package the tokenizer with a manifest, hashes, model compatibility record and rollback instructions.

## Core technical concepts

- **Normalization:** Unicode and whitespace handling must be explicit; normalization can change text and offsets.
- **Pre-tokenization:** Establishes boundaries or byte sequences before subword learning.
- **BPE:** Learns merge operations from frequent adjacent symbol pairs.
- **WordPiece:** Uses a likelihood-oriented vocabulary construction and continuation-token conventions.
- **Unigram:** Starts from a larger candidate vocabulary and prunes according to a probabilistic segmentation objective.
- **Byte-level tokenization:** Provides broad byte coverage, but does not guarantee good semantic segmentation or efficient sequence lengths.
- **Special tokens:** Must remain atomic, have stable IDs and be consistent with the model's chat template.
- **Tokenizer/model coupling:** Changing vocabulary or special-token IDs changes the model input/output interface and may require embedding changes and retraining or controlled adaptation.

## Evaluation scorecard

Track at minimum: exact round-trip rate, byte coverage, unknown-token rate, tokens per word, bytes per token, sequence-length expansion, vocabulary size, special-token atomicity, offset accuracy, per-language coverage and reproducibility.

Do not select a tokenizer solely because it has the largest vocabulary or lowest average token count. Report results separately for languages, scripts, code, domain terms and rare names.

## Training and release gates

- Only authorized first-party, public-domain, openly licensed or separately licensed text may enter tokenizer training. Public visibility is not training permission.
- Keep training, validation, test and private holdout data isolated by source; do not train on evaluation or holdout text.
- Preserve provenance, dataset/source hashes, tokenizer configuration, seed, library versions and exact artifact hashes.
- Pin the tokenizer revision, special-token map and chat template to the exact model/checkpoint.
- Run compatibility, regression, safety and held-out evaluation before promotion.
- No paid compute, background GPU execution or external data transfer without explicit compute and data authorization.
- A trained tokenizer artifact is not proof that Buddy's model weights were trained. Model training requires its own run manifest, checkpoints, hashes and evaluation evidence.

## Mastery standard

Buddy completes this track only after all 12 lesson assessments pass, tokenizer artifacts are reproducible, special-token and model-compatibility tests pass, and an independent held-out scorecard meets the configured floors. Reading, summarizing, cataloging or passing a curriculum-schema test alone does not count as mastery.
