# NVIDIA Video Mastery Bot

## Purpose

This bot studies publicly documented NVIDIA Cosmos/DreamDojo video-data workflows and authorized datasets as engineering references. It does not bypass access controls or indiscriminately scrape copyrighted video.

NVIDIA's current Cosmos documentation describes a Dataset Search stack for ingesting, indexing, searching, and curating multimodal data, including text-to-video, video-to-video, and embedding-based search. NVIDIA's Cosmos 3 technical report also describes scene-change detection, canonical re-encoding, embeddings, and deduplication as parts of large-scale video processing.

## Fast scanning architecture

`inventory → metadata → scene changes → adaptive sampling → speech/OCR/action sampling → captions → embeddings → duplicate detection → quality filtering → temporal index → JSONL/Parquet/SQLite`

The expensive models are not run uniformly across every frame. A cheap first pass identifies where deeper analysis is valuable, then targeted analysis is run only where needed. Results are cached and checkpointed so a long scan can resume after interruption.

## AI-readable learning format

Each observation becomes a stable record with:

- source and license
- content hash
- video/clip ID
- start/end timestamp
- observed event
- entities
- actions
- audio events
- OCR/text
- evidence references
- confidence
- benchmark result
- explicit `unknown` when evidence is insufficient

The learning record can be exported as JSON, JSONL, Parquet, SQLite, and human-readable Markdown.

## What Buddy learns

Buddy should convert the observations into original capability records:

`concept → evidence → procedure → preconditions → actions → expected effect → failure modes → verification → benchmark → transfer case`

This makes the result useful to AI systems without requiring the original video to be repeatedly processed.

## Important correction on the “400 hours” claim

We should **not hard-code 400 hours as if it were the size of one universal NVIDIA dataset**. NVIDIA's public materials describe different datasets and much larger corpora across Cosmos projects. For example, a 2025 NVIDIA presentation described about 20 million hours of videos for Cosmos pretraining, while current Cosmos documentation describes specific benchmark and training datasets separately. Exact quantities must therefore be attached to a named dataset/version and source.

## DreamCo benchmark

The bot benchmarks temporal accuracy, event accuracy, grounding, retrieval, OCR, speech, audio-visual reasoning, long-video efficiency, deduplication, confidence calibration, hallucination resistance, and recovery.

NVIDIA technology remains an optional accelerator/reference lane. DreamCo's structured data and benchmark contracts remain portable so Buddy can operate without NVIDIA infrastructure.
