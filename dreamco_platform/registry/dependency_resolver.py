from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Dict, Iterable, List


@dataclass
class BotRegistryEntry:
    bot_id: str
    dependencies: List[str] = field(default_factory=list)


class DependencyResolver:
    def __init__(self, entries: Iterable[BotRegistryEntry]) -> None:
        self.entries = {entry.bot_id: entry for entry in entries}

    def resolve_order(self, bot_ids: List[str]) -> List[str]:
        graph = defaultdict(list)
        indegree = defaultdict(int)
        for bot_id in bot_ids:
            entry = self.entries.get(bot_id)
            if entry is None:
                raise KeyError(f"Missing dependency definition for {bot_id}")
            indegree.setdefault(bot_id, 0)
            for dependency in entry.dependencies:
                if dependency not in self.entries:
                    raise KeyError(f"Missing dependency: {dependency}")
                graph[dependency].append(bot_id)
                indegree[bot_id] += 1
        queue = deque([bot for bot, degree in indegree.items() if degree == 0])
        order = []
        while queue:
            current = queue.popleft()
            order.append(current)
            for child in graph[current]:
                indegree[child] -= 1
                if indegree[child] == 0:
                    queue.append(child)
        if len(order) != len(indegree):
            raise ValueError("Circular dependency detected")
        return order

    def export_dot(self) -> str:
        lines = ["digraph bots {"]
        for entry in self.entries.values():
            if not entry.dependencies:
                lines.append(f'  "{entry.bot_id}";')
            for dependency in entry.dependencies:
                lines.append(f'  "{dependency}" -> "{entry.bot_id}";')
        lines.append("}")
        return "\n".join(lines)

    def dependency_map(self) -> Dict[str, List[str]]:
        return {bot_id: list(entry.dependencies) for bot_id, entry in self.entries.items()}

    def missing_for(self, bot_id: str) -> List[str]:
        entry = self.entries[bot_id]
        return [dependency for dependency in entry.dependencies if dependency not in self.entries]
