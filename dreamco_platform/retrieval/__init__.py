"""
DreamCo Platform — Retrieval Layer
=====================================

Pluggable backend adapters for the Memory + Retrieval Layer (Layer 6):

    Model Router
          ↓
    Memory + Retrieval Layer   ← this package
    ├── RedisStore        (hot cache / session memory)
    ├── PineconeStore     (vector similarity search)
    ├── ElasticStore      (full-text + hybrid search)
    └── SQLStore          (structured relational facts)
          ↓
    Execution Layer

All adapters share the ``RetrievalBackend`` abstract interface so the
``RetrievalLayer`` can transparently dispatch reads/writes across backends.
"""

from dreamco_platform.retrieval.base import RetrievalBackend, RetrievalRecord  # noqa: F401
from dreamco_platform.retrieval.redis_store import RedisStore  # noqa: F401
from dreamco_platform.retrieval.pinecone_store import PineconeStore  # noqa: F401
from dreamco_platform.retrieval.elastic_store import ElasticStore  # noqa: F401
from dreamco_platform.retrieval.sql_store import SQLStore  # noqa: F401
from dreamco_platform.retrieval.retrieval_layer import RetrievalLayer  # noqa: F401

__all__ = [
    "RetrievalBackend",
    "RetrievalRecord",
    "RedisStore",
    "PineconeStore",
    "ElasticStore",
    "SQLStore",
    "RetrievalLayer",
]
