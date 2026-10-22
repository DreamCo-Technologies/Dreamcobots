# Buddy customizable Wikipedia search bot (review implementation)

Inspired by the freeCodeCamp PostgreSQL hybrid-search course; independently authored.

## Setup
- PostgreSQL 17+ with `pg_textsearch` and `pgvector` installed and enabled.
- Authorized operator runs `schema.sql` in a dedicated database.
- Host application installs `psycopg[binary]` and supplies a connection to `search.search`.
- Ingest Wikipedia only from authorized dumps or official APIs while respecting licenses, attribution and rate limits.
- To enable semantic search, supply locally generated 384-dimensional embeddings using a licensed embedding model. Model/version must remain consistent across query and document vectors.
- `SearchOptions` controls collection, candidate pool, top K, keyword and semantic weights and RRF constant.
- Without embeddings, keyword BM25 search works. No paid API required.
- No live database, Wikipedia dump, UI or production API is provisioned by these files.

## Boundaries
Wikipedia is not authoritative for every subject. Show source URL and license, identify gaps and verify sensitive claims independently.
For multi-user data, implement authenticated collection authorization and row-level security **before** allowing private collections; collection filtering alone is not access control.
Do not expose raw DB credentials in browser code. Benchmark retrieval recall and latency with independent holdouts before promotion.
