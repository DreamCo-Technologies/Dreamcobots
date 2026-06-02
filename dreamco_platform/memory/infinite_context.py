from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class ContextWindow:
    active_messages: List[str] = field(default_factory=list)
    compressed_history: List[str] = field(default_factory=list)
    total_tokens_managed: int = 0


class InfiniteContext:
    def __init__(self, token_limit: int = 200) -> None:
        self.token_limit = token_limit
        self.window = ContextWindow()

    def add_message(self, message: str) -> None:
        self.window.active_messages.append(message)
        self.window.total_tokens_managed += len(message.split())
        while self._active_tokens() > self.token_limit:
            self.compress_oldest()

    def retrieve_relevant(self, query: str) -> List[str]:
        query_terms = set(query.lower().split())
        scored = []
        for message in self.window.active_messages + self.window.compressed_history:
            overlap = len(query_terms & set(message.lower().split()))
            if overlap:
                scored.append((overlap, message))
        return [message for _, message in sorted(scored, reverse=True)[:5]]

    def compress_oldest(self) -> None:
        if not self.window.active_messages:
            return
        message = self.window.active_messages.pop(0)
        words = message.split()
        summary = ' '.join(words[: min(12, len(words))])
        self.window.compressed_history.append(summary)

    def _active_tokens(self) -> int:
        return sum(len(message.split()) for message in self.window.active_messages)

def context_health(self) -> dict:
    return {
        'active_messages': len(self.window.active_messages),
        'compressed_messages': len(self.window.compressed_history),
        'tokens_managed': self.window.total_tokens_managed,
    }


def restore_recent_summary(self) -> str | None:
    return self.window.compressed_history[-1] if self.window.compressed_history else None


InfiniteContext.context_health = context_health
InfiniteContext.restore_recent_summary = restore_recent_summary

def all_messages(self) -> List[str]:
    return list(self.window.compressed_history + self.window.active_messages)


InfiniteContext.all_messages = all_messages
