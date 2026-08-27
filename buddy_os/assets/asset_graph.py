"""Dependency/capability graph for registered Buddy digital assets."""
from __future__ import annotations

from collections import defaultdict, deque
from typing import Dict, Iterable, List, Set, Tuple

from .digital_asset_registry import DigitalAssetRegistry


class AssetGraph:
    def __init__(self, registry: DigitalAssetRegistry) -> None:
        self.registry = registry

    def edges(self) -> List[Tuple[str, str, str]]:
        result = []
        for asset in self.registry.manifest():
            for dependency in asset["dependencies"]:
                result.append((asset["asset_id"], dependency, "depends_on"))
            for capability in asset["capabilities"]:
                result.append((asset["asset_id"], capability, "provides"))
        return result

    def dependency_closure(self, asset_id: str) -> Set[str]:
        seen: Set[str] = set()
        queue = deque([asset_id])
        while queue:
            current = queue.popleft()
            asset = self.registry.get(current)
            if not asset:
                continue
            for dependency in asset.dependencies:
                if dependency not in seen:
                    seen.add(dependency)
                    queue.append(dependency)
        return seen

    def capability_index(self) -> Dict[str, List[str]]:
        index: Dict[str, List[str]] = defaultdict(list)
        for asset in self.registry.manifest():
            for capability in asset["capabilities"]:
                index[capability].append(asset["asset_id"])
        return {key: sorted(value) for key, value in sorted(index.items())}
