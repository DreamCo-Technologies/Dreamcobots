# Buddy Database Routing Contract

**Status:** Policy decision engine and synthetic-fixture tests added; no live source is connected by this change.

## Current repository evidence

- The application database uses PostgreSQL through node-postgres and Drizzle in server/db.ts; DATABASE_URL is required, but this run did not inspect secret values or test the host connection.
- Buddy's dataset catalog uses a local SQLite database through buddy/datasets/hub.py. The default path is .dreamco/dataset-hub/catalog.sqlite3; the live file was not inspected.
- buddy/datasets/database_sources.py supports explicitly authorized, read-only SQLite and optional PostgreSQL snapshots. It is not a general-purpose router.
- config/rag-backend-catalog.json lists local, FAISS, Chroma, Qdrant, Weaviate, Milvus, pgvector, and Pinecone options. Listing a backend is not connection evidence.
- package.json contains pg and Drizzle dependencies. This scan did not find @supabase/supabase-js or firebase-admin; Firebase specialist documentation is not a connected Firestore integration.

The source registry records these distinctions. Unknown health, residency, latency, freshness, backup/restore, and credential state remain unknown. No credentials or connection strings are stored.

## Routing contract

A request is eligible only when all of these are satisfied:

1. The source lifecycle is CONNECTED, TESTED, or PRODUCTION.
2. The connector status is CONNECTED and health is HEALTHY.
3. The source explicitly permits the requested operation and data type.
4. Its classification ceiling covers the requested data sensitivity.
5. Its query capability, freshness, consistency, latency, cost tier, and residency region satisfy the request.
6. The decision is deterministic under the declared priority order.

A source in DISCOVERED, DOCUMENTED, or CONFIGURED state is not routable. Unknown values fail closed.

## Write safety

Writes additionally require an explicit approval ID, idempotency key, source-side allowlisting of that approval, enabled writes, idempotency support, and transaction support. Automatic write failover is disabled. The router returns a decision only; it never opens a connection, executes SQL, changes data, or performs a migration.

Read failover candidates are returned only when the caller explicitly permits failover and declares the operation idempotent. The router does not execute the failover.

## Synthetic lab

Run:

```bash
python -m unittest tests.test_buddy_database_router tests.test_buddy_database_sources
```

The fixtures prove deterministic source selection, permission and residency filtering, freshness/consistency/cost/latency checks, disconnected-source rejection, write approval/idempotency gates, read-only failover policy, and secret-field rejection.

## Not yet implemented

- Live health probes and authenticated connector tests.
- Production source-of-truth ownership and schema/version registry.
- PostgreSQL transaction and isolation integration tests.
- Supabase, Firebase, vector-store, object-store, warehouse, and search-engine adapters.
- Cache invalidation, retry budgets, connection pooling, load/failover tests, backup/restore drills, encryption/key management, retention, and disaster recovery.
- Runtime integration with Buddy's task router.

No live database was contacted. The new route engine is EXECUTABLE against synthetic fixtures, not CONNECTED, VERIFIED against live infrastructure, or PRODUCTION.
