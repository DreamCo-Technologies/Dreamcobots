"""
DreamCo OS — Memory Layer
==========================

The memory layer provides four tiers of agent memory:

* ``ShortTermMemory``  — Redis-backed session memory with 24-hour TTL
* ``LongTermMemory``   — Vector DB (Chroma/Pinecone) for semantic recall
* ``StructuredMemory`` — Postgres/SQLite relational agent state
* ``BehavioralMemory`` — Event graph tracking agent decisions over time

``MemoryClient`` is the unified façade exposed to every ``DreamCoBot``.
"""

from python_bots.core.memory.client import MemoryClient
from python_bots.core.memory.short_term import ShortTermMemory
from python_bots.core.memory.long_term import LongTermMemory
from python_bots.core.memory.structured import StructuredMemory
from python_bots.core.memory.behavioral import BehavioralMemory

__all__ = [
    "MemoryClient",
    "ShortTermMemory",
    "LongTermMemory",
    "StructuredMemory",
    "BehavioralMemory",
]
