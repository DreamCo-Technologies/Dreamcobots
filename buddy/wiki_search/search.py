"""Configurable PostgreSQL BM25 + pgvector search, fused with weighted RRF.

No implicit embedding API calls; caller supplies a 384-dimensional vector.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import isfinite

@dataclass(frozen=True)
class SearchOptions:
    collection: str = "wikipedia"
    limit: int = 10
    candidate_limit: int = 100
    keyword_weight: float = 1.0
    semantic_weight: float = 1.0
    rrf_k: int = 60

    def validate(self) -> None:
        if not self.collection or len(self.collection) > 100:
            raise ValueError("Invalid collection")
        if not (1 <= self.limit <= 100 and self.limit <= self.candidate_limit <= 1000):
            raise ValueError("Invalid result limits")
        if self.rrf_k < 1:
            raise ValueError("rrf_k must be positive")
        if any(not isfinite(x) or x < 0 for x in (self.keyword_weight, self.semantic_weight)):
            raise ValueError("Invalid weights")
        if self.keyword_weight + self.semantic_weight <= 0:
            raise ValueError("At least one search mode is required")

SQL = """
WITH keyword AS (
 SELECT id, row_number() OVER (ORDER BY search_text <@> %(query)s, id) AS rank
 FROM (SELECT id, search_text FROM buddy_knowledge
       WHERE collection = %(collection)s
       ORDER BY search_text <@> %(query)s LIMIT %(candidate_limit)s) AS hits
),
semantic AS (
 SELECT id, row_number() OVER (ORDER BY distance, id) AS rank
 FROM (SELECT id, embedding <=> %(embedding)s::vector AS distance
       FROM buddy_knowledge WHERE collection = %(collection)s AND embedding IS NOT NULL
       ORDER BY embedding <=> %(embedding)s::vector LIMIT %(candidate_limit)s) AS hits
),
fused AS (
 SELECT COALESCE(k.id,s.id) AS id,
        COALESCE(%(keyword_weight)s / (%(rrf_k)s + k.rank),0) +
        COALESCE(%(semantic_weight)s / (%(rrf_k)s + s.rank),0) AS score,
        k.rank AS keyword_rank, s.rank AS semantic_rank
 FROM keyword k FULL OUTER JOIN semantic s ON k.id=s.id
)
SELECT d.external_id,d.title,d.body,d.source_url,d.license,d.language,
       fused.score,fused.keyword_rank,fused.semantic_rank
FROM fused JOIN buddy_knowledge d ON d.id=fused.id
ORDER BY fused.score DESC, d.id LIMIT %(limit)s
"""

# BM25-only query avoids requiring a vector from the caller.
KEYWORD_SQL = """
SELECT external_id,title,body,source_url,license,language,
       search_text <@> %(query)s AS keyword_score
FROM buddy_knowledge WHERE collection=%(collection)s
ORDER BY search_text <@> %(query)s, id LIMIT %(limit)s
"""

def search(connection, query: str, *, embedding=None, options: SearchOptions = SearchOptions()):
    """Return cited rows; connection is a psycopg connection provided by the host."""
    options.validate()
    if not isinstance(query, str) or not query.strip() or len(query) > 500:
        raise ValueError("Invalid query")
    if embedding is not None:
        if len(embedding) != 384 or any(not isfinite(float(v)) for v in embedding):
            raise ValueError("Expected finite 384-dimensional embedding")
    if embedding is None and options.keyword_weight == 0:
        raise ValueError("Semantic-only mode requires embedding")
    params = vars(options).copy()
    params["query"] = query
    params["embedding"] = None if embedding is None else "[" + ",".join(str(float(v)) for v in embedding) + "]"
    with connection.cursor() as cursor:
        cursor.execute(SQL if embedding is not None and options.semantic_weight > 0 else KEYWORD_SQL, params)
        cols = [col.name for col in cursor.description]
        return [dict(zip(cols, row)) for row in cursor.fetchall()]
