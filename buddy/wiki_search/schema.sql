-- Buddy Wikipedia hybrid search. PostgreSQL 17 + pg_textsearch + pgvector.
-- Extensions must be installed by an authorized database administrator.
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_textsearch;
CREATE TABLE IF NOT EXISTS buddy_knowledge (
 id BIGSERIAL PRIMARY KEY,
 collection TEXT NOT NULL DEFAULT 'wikipedia',
 external_id TEXT NOT NULL,
 title TEXT NOT NULL,
 body TEXT NOT NULL,
 source_url TEXT NOT NULL,
 license TEXT NOT NULL,
 language TEXT NOT NULL DEFAULT 'en',
 search_text TEXT GENERATED ALWAYS AS (title || ' ' || body) STORED,
 embedding vector(384),
 updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
 UNIQUE(collection, external_id)
);
CREATE INDEX IF NOT EXISTS buddy_knowledge_collection_idx ON buddy_knowledge(collection);
CREATE INDEX IF NOT EXISTS buddy_knowledge_bm25_idx ON buddy_knowledge USING bm25(search_text) WITH (text_config='english');
CREATE INDEX IF NOT EXISTS buddy_knowledge_vector_idx ON buddy_knowledge USING hnsw(embedding vector_cosine_ops);
