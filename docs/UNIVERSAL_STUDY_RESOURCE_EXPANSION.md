# Universal Study Resource Expansion (1101–1200)

## Purpose

Expand the existing DreamCo study catalog without creating a parallel scheduler or bypassing existing governance. This seed adds 100 curated resource pointers. It is a metadata-first discovery catalog, not an ingestion manifest, training dataset, or proof of access.

## Existing architecture to reuse

- `config/buddy-study-resource-policy.json`
- `config/buddy-study-resources-001-100.json`
- `config/buddy-study-resources-1001-1100-must-have.json`
- `buddy/learning/study_resource_scheduler.py`
- `buddy/datasets/discovery_fleet.py`
- `buddy/datasets/license_policy.py`
- `docs/DREAMCO_GOVERNED_DATASET_INGESTION.md`
- `docs/BUDDY_WEB_LEARNING_FABRIC.md`

The new catalog deliberately does not alter existing IDs, existing resources, model catalogs, or division registries. Before merging, wire this file into the canonical resource loader and add schema/duplicate-ID/URL tests.

## Source families

The 100-ID range is reserved for an expansion batch. This first commit seeds 100 resources:

- FreeCodeCamp and YouTube metadata/transcript policy.
- Hugging Face, UCI, OpenML, Kaggle, Google Dataset Search, government and research dataset catalogs.
- Public corpora and knowledge graphs.
- Research indexes and paper discovery.
- Neural networks, transformers, GPU engineering, model evaluation and AI governance.
- Programming, databases, analytics, DevOps, cloud and security.
- Open university courses and hands-on software education.
- Tolkien scholarship, digital humanities, constructed-language research, comparative mythology, linguistics and literary archives.

## FreeCodeCamp and video learning workflow

1. Discover official FreeCodeCamp curriculum paths, certifications, lesson identifiers, source repository changes, video IDs, titles, channels, descriptions, publication dates, durations and category metadata.
2. Normalize and deduplicate by stable source identity, not display title or playlist position.
3. Preserve source URL, publisher/channel, retrieved-at timestamp, source revision/etag where available, content hash for locally supplied permitted files, and division/capability mapping.
4. Keep metadata discovery separate from transcript acquisition.
5. Obtain transcript text only through a permitted route: owner-provided export, creator-supplied file, a supported API request where the authenticated user has the required video-edit permission, or another explicit license/consent grant.
6. If transcript access is unavailable, retain metadata and a link, then generate an original study outline from authorized documentation; do not fabricate a transcript.
7. Run text quality checks (language, encoding, timestamps, duplication, truncation, speaker labels, ASR confidence where supplied) before evaluation.
8. Keep evaluation permission separate from training permission. A transcript approved for evaluation is not automatically approved for training.
9. Weekly Buddy evaluation records must identify exact Buddy model/version, transcript ID/hash, task prompt/version, expected rubric, evaluator version, sample size, score, uncertainty, failures and timestamp.
10. Only separately approved datasets can proceed to preprocessing or model training.

### YouTube API boundary

The YouTube Data API `captions.list` returns caption-track metadata, not caption text. The `captions.download` method requires OAuth and permission to edit the video. DreamCo must not bypass this restriction using scraping, downloader workarounds, cookies, or unofficial extraction.

Official references:
- https://developers.google.com/youtube/v3/docs/captions/list
- https://developers.google.com/youtube/v3/docs/captions/download
- https://developers.google.com/youtube/data/guides/implementation/captions

### FreeCodeCamp rights boundary

The current freeCodeCamp repository describes its software as BSD-3-Clause while separately identifying curriculum materials as copyrighted. Do not infer that all lessons, articles, videos, images, or third-party media share the software license.

Official source: https://github.com/freeCodeCamp/freeCodeCamp

## Dataset study workflow

For every candidate dataset, Buddy should inspect the dataset card, publisher, source URL, revision, schema, sample rows, splits, language, size, collection period, update cadence, license, terms, provenance, consent/rights, PII risk, sensitive attributes, known contamination, duplication, imbalance, quality limitations and intended use.

Quality gates:
- provenance and source integrity;
- license and file-level rights;
- consent and privacy;
- relevance and accuracy;
- completeness and duplication;
- imbalance and representativeness;
- toxicity/safety;
- benchmark contamination;
- train/validation/test leakage;
- reproducible version/hash and preprocessing lineage.

Unknown or conflicting rights are BLOCKED from training. Discovery, card inspection, sample inspection, approved download, preprocessing, training-ready status and actual use in a run must be distinct states.

## Tolkien study lane

Use the Tolkien-specific resources as a scholarly research lane, not a copyrighted-text ingestion lane. Study literary history, mythology, philology, comparative linguistics, constructed-language methodology, digital humanities, corpus annotation, maps and timelines through authorized sources.

Use the Digital Tolkien Project, Tolkien Estate resource links, Tolkien Society, peer-reviewed journals and university research guides as discovery gateways. Treat community databases as secondary references and verify claims against primary scholarship.

The machine-readable curriculum is `specialized_study_tracks[tolkien]` in `config/buddy-study-resources-1101-1200-expansion.json`. It contains eight lessons: philological context; historical linguistics; comparative mythology; narrative architecture; archival provenance; digital humanities; scholarly reception; and a cited capstone. Completion requires a learner-authored artifact, source citations, rights review and rubric evidence—not metadata discovery alone.

The track explicitly disables copyrighted primary-text ingestion, transcript/audiobook downloads, reproduction of protected invented languages or scripts, derivative generation using protected characters/settings/stories, and model-weight training. Unknown rights remain BLOCKED. See `docs/BUDDY_TOLKIEN_STUDY_TRACK.md` for the lesson plan and official rights references.

Do not bulk-copy Tolkien novels, appendices, maps, artwork, audio, journal articles, or proprietary language materials. Build original exercises and original worldbuilding tasks; cite sources and keep protected source passages out of training data absent explicit permission.

## Buddy student assignments

- Dataset lane: explain a dataset card and produce a rights/quality checklist without downloading data.
- Video lane: classify a metadata record and determine whether transcript access is actually authorized.
- Transcript lane: evaluate one explicitly approved sample and record the model/version/hash/evaluator evidence.
- Research lane: compare a primary source and a secondary source; identify unsupported claims.
- Tolkien lane: construct an original, non-infringing worldbuilding schema and demonstrate consistent language/culture/geography relationships.

## Acceptance criteria before merge

- JSON parses and contains unique IDs 1101–1200 with no collision against existing catalogs.
- Resource records have non-empty names, categories, HTTPS URLs, descriptions and study methods.
- Every record defaults to metadata-only discovery; no automatic downloads or training.
- YouTube transcript workflow explicitly enforces owner permission or another documented rights grant.
- FreeCodeCamp curriculum copyright is not conflated with the repository software license.
- Tolkien sources are marked with per-item rights review and no bulk text ingestion.
- Scheduler integration uses capability gaps and existing registry conventions.
- Tests cover malformed records, duplicate IDs, unknown rights, unauthorized transcript retrieval, and training/evaluation permission separation.
- No model weights, production data, paid compute, secrets, or live services are modified by this catalog PR.

## Current status

This PR adds catalog seed data and a design/acceptance specification only. It does not claim that resources have been fetched, read, downloaded, transcribed, approved, connected, or used for training. No model weights are changed.
