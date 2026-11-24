# Buddy Database and Dataset Engineering Track

## Purpose

Teach Buddy to design and evaluate production-grade data architecture and route tasks to the correct permitted data source. The track is a curriculum and documentation exercise; it does not connect to DreamCo production databases or authorize ingestion.

The machine-readable track is `specialized_study_tracks[database-and-dataset-engineering]` in `config/buddy-study-resources-1101-1200-expansion.json`. It references existing catalog resources and additional official documentation gateways.

## Ten-lesson sequence

1. **Relational modeling and normalization** — design synthetic multi-tenant schemas, keys, constraints and migration tests.
2. **Transactions, isolation and concurrency** — test commit/rollback, isolation anomalies, locking and idempotent retries.
3. **Indexes, query plans and performance** — compare scans and indexes; capture EXPLAIN plans, latency and row counts.
4. **Database technology selection** — compare PostgreSQL, SQLite, Supabase, Firestore, Redis, DuckDB and Iceberg.
5. **Buddy data-source routing** — route synthetic reads by freshness, consistency, sensitivity, permission, latency and cost; reject unapproved writes.
6. **Hybrid keyword and vector retrieval** — prototype PostgreSQL full-text plus pgvector/Qdrant/OpenSearch with citations and ACL filters.
7. **Dataset discovery and rights review** — catalog metadata-only candidates with source, license, privacy, quality and intended-use fields.
8. **Dataset quality, splits and contamination** — test schema, deduplication, imbalance, leakage and isolated holdouts on synthetic fixtures.
9. **Data lineage and reproducible experiments** — link dataset hashes, transformations, splits, tokenizer/model versions, run IDs and evaluation.
10. **Routing and governance capstone** — test source-of-truth, failover, permissions, backup/restore and lineage using synthetic fixtures.

## Routing decision contract

For every source, record provider, engine, environment, owner, purpose, schema/version, classification, permitted operations, freshness, retention, residency, credential status (status only), health, cost tier, backup/restore evidence and lifecycle state.

Buddy's routing policy must evaluate:
- task and data type;
- source-of-truth and read/write permission;
- freshness, consistency and transaction requirements;
- query capability, latency, throughput and availability;
- privacy, sensitivity, residency and retention;
- cost and fallback behavior.

Writes must target only an approved writable source. Retries must be idempotent; cache invalidation and audit lineage must be explicit. Vector retrieval must retain keyword fallback and provenance/ACL filtering.

## Dataset governance

Discovery is metadata-first. For every candidate capture canonical name, URL, publisher, task/domain, format, size/splits, language, license/terms, consent/rights, provenance, collection date, update cadence, PII risk, contamination, quality limitations, intended/allowed use, preprocessing, deduplication and evaluation relevance.

Unknown rights are **BLOCKED** from training. A dataset card or public URL is not permission to ingest. Train/validation/test splits must be separated; holdout evaluation data stays isolated. Every training record must link dataset version/hash, transformation code, split IDs, tokenizer, teacher/student model versions, hyperparameters, compute, run ID, checkpoint hash and evaluation suite.

## Study sources

- [PostgreSQL documentation](https://www.postgresql.org/docs/current/)
- [SQLite documentation](https://www.sqlite.org/docs.html)
- [Supabase documentation](https://supabase.com/docs)
- [Firebase documentation](https://firebase.google.com/docs)
- [Redis documentation](https://redis.io/docs/latest/)
- [DuckDB documentation](https://duckdb.org/docs/stable/)
- [Apache Iceberg documentation](https://iceberg.apache.org/docs/latest/)
- [PostgreSQL full-text search](https://www.postgresql.org/docs/current/textsearch.html)
- [pgvector](https://github.com/pgvector/pgvector)
- [Qdrant documentation](https://qdrant.tech/documentation/)
- [OpenSearch documentation](https://docs.opensearch.org/latest/)
- [Hugging Face dataset cards](https://huggingface.co/docs/hub/datasets-cards)
- [UCI Machine Learning Repository](https://archive.ics.uci.edu/)
- [OpenML](https://www.openml.org/)
- [Stanford CS245: Principles of Data-Intensive Systems](https://web.stanford.edu/class/cs245/)

## Safety boundaries

- Synthetic fixtures are allowed for labs.
- Production database access, live writes and production migrations are disabled.
- Bulk dataset downloads and private/paid dataset ingestion are disabled.
- Model-weight training is not authorized by this study track.
- Per-dataset license and terms review is required; unknown rights remain BLOCKED.
- No secrets, connection strings or credential values may appear in logs or artifacts.

## Completion evidence

A lesson is complete only after an original artifact, deterministic test output, source citations, reviewer approval and a recorded rubric result. A catalog entry or generated plan is not proof that Buddy has learned the material.

**Current status:** CURRICULUM_DEFINED_REFERENCE_ONLY. No production database was connected, no dataset was downloaded, no model weights were trained, and Buddy has not completed this track.
