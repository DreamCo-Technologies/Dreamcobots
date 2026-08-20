# Buddy Universal Source Learning Architecture

## Goal

Give Buddy one efficient learning pipeline for books, movies, videos, websites, papers, databases, datasets, repositories and courses without pretending that reading or indexing equals learning.

## Fast path

`Discover → Verify → Fingerprint → Extract → Normalize → Chunk → Index → Retrieve → Synthesize → Practice → Sandbox → Benchmark → Remediate → Retest → Promote`

## Source adapters

- **Books:** ISBNdb, Google Books, publisher catalogs, library metadata, MIT Press and open-license repositories.
- **Courses:** MIT OpenCourseWare, MIT Open Learning Library and other openly licensed course systems.
- **Websites:** sitemap/RSS/API-first discovery, respectful crawling, robots/terms checks and change detection.
- **Papers:** DOI/metadata providers, institutional repositories and open-access indexes.
- **Databases:** schema inspection, table statistics, sampling and provenance-aware query adapters.
- **Repositories:** README/docs/code/tests/issues/releases/CI metadata with repository permission boundaries.
- **Video/movies:** metadata → transcript/captions → scene/shot sampling → OCR/vision/audio extraction → timestamped evidence. Do not ingest or redistribute copyrighted video without permission.
- **Audio:** transcript → speaker/segment metadata → acoustic features where needed.
- **Images/PDFs:** OCR + layout/table/chart extraction while retaining page/region provenance.

## Efficiency rules

1. **Metadata first.** Never download a huge asset before deciding whether it can improve a known capability gap.
2. **Deduplicate globally.** Content fingerprints prevent repeated ingestion across URLs, editions and mirrors.
3. **Cache immutable evidence.** Reuse verified extraction instead of reprocessing unchanged sources.
4. **Incremental updates.** Reprocess only changed pages, chapters, scenes or database partitions.
5. **Hierarchical retrieval.** Source → section → chunk → evidence span; retrieve narrowly before expanding context.
6. **Hybrid retrieval.** Combine lexical, semantic and structured filters; rerank before synthesis.
7. **Adaptive chunking.** Preserve headings, code blocks, equations, tables, scenes and database rows instead of using one fixed splitter for every modality.
8. **Evidence budgets.** Spend compute on the smallest evidence set that can answer or teach the target capability.
9. **Active learning.** Select the next source based on the highest expected benchmark improvement per unit cost/time.
10. **Failure-directed study.** A failed benchmark changes the curriculum; successful material is not repeatedly consumed without evidence of need.
11. **Parallel specialists.** Extraction, retrieval, pedagogy, coding, testing and benchmark evaluation can run as separate bounded agents.
12. **Mastery gating.** Promotion requires repeatable quality, correctness, speed, safety and regression evidence.

## Copyright and access

Store provenance and license metadata with every learning object. Use official APIs, open licenses, public metadata and user-authorized content. For copyrighted books and movies, retain metadata and permitted excerpts/references rather than copying entire works without authorization.

MIT OCW explicitly allows downloading and remixing OCW material under its stated Creative Commons terms, while noting that some course readings are proprietary and are not supplied by OCW. citeturn0search0turn0search3

## Benchmark loop

For every capability:

`gap → source ranking → study slice → generated practice → sandbox → benchmark → failure taxonomy → targeted remediation → retest → regression test → evidence record`

A source can improve a model's knowledge retrieval without changing the underlying model weights. Buddy should track **knowledge availability**, **task performance**, and **model training** as separate states.

## Recommended architecture

- Source registry
- Provenance/license registry
- Content fingerprint store
- Object/document store
- Hybrid search index
- Knowledge graph
- Learning planner
- Practice generator
- Sandbox runner
- Benchmark runner
- Failure/remediation engine
- Mastery ledger
- Regression suite
- Cost/latency tracker
- Human approval layer

The first implementation is `tools/buddy_source_learning_engine.py`, which provides deterministic source IDs, source ranking, deduplication, chunking and benchmark-oriented study plans.
