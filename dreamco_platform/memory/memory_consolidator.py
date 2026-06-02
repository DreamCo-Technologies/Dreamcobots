from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Iterable, List


class ConsolidationStrategy(Enum):
    BY_TOPIC = 'by_topic'
    BY_BOT_TYPE = 'by_bot_type'
    BY_OUTCOME_TYPE = 'by_outcome_type'


@dataclass
class MemoryEntry:
    bot_id: str
    topic: str
    content: str
    importance: float
    outcome_type: str = 'general'
    bot_type: str = 'general'


@dataclass
class ConsolidatedMemory:
    key: str
    summary: str
    combined_weight: float
    source_count: int


class MemoryConsolidator:
    def consolidate(self, entries: Iterable[MemoryEntry], strategy: ConsolidationStrategy = ConsolidationStrategy.BY_TOPIC) -> List[ConsolidatedMemory]:
        buckets: Dict[str, list[MemoryEntry]] = defaultdict(list)
        for entry in entries:
            if strategy == ConsolidationStrategy.BY_TOPIC:
                key = entry.topic
            elif strategy == ConsolidationStrategy.BY_BOT_TYPE:
                key = entry.bot_type
            else:
                key = entry.outcome_type
            buckets[key].append(entry)
        consolidated = []
        for key, group in buckets.items():
            unique_sentences = []
            seen = set()
            total_weight = 0.0
            for entry in sorted(group, key=lambda item: item.importance, reverse=True):
                total_weight += entry.importance
                if entry.content not in seen:
                    seen.add(entry.content)
                    unique_sentences.append(entry.content)
            summary = ' '.join(unique_sentences[:3])
            consolidated.append(ConsolidatedMemory(key, summary, round(total_weight, 3), len(group)))
        return consolidated
