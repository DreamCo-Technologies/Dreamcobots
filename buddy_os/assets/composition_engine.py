"""Safe composition and simulation planning for Buddy digital assets."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from .digital_asset_registry import DigitalAssetRegistry
from .asset_graph import AssetGraph


@dataclass(frozen=True)
class Composition:
    task: str
    asset_ids: List[str]
    dependencies: List[str]
    estimated_risk: float
    estimated_utility: float
    simulation_only: bool = True
    warnings: List[str] = field(default_factory=list)


class AssetCompositionEngine:
    def __init__(self, registry: DigitalAssetRegistry) -> None:
        self.registry = registry
        self.graph = AssetGraph(registry)

    def compose(self, task: str, asset_ids: List[str]) -> Composition:
        assets = [self.registry.get(asset_id) for asset_id in asset_ids]
        missing = [asset_id for asset_id, asset in zip(asset_ids, assets) if asset is None]
        if missing:
            raise ValueError(f"unknown assets: {', '.join(missing)}")

        dependencies = set()
        warnings = []
        utility = 0.0
        risk = 0.0
        for asset in assets:
            dependencies.update(self.graph.dependency_closure(asset.asset_id))
            utility += asset.utility_score
            risk += asset.risk_score
            if asset.lifecycle not in {"verified", "available"}:
                warnings.append(f"{asset.asset_id} is lifecycle={asset.lifecycle}")

        count = max(len(assets), 1)
        return Composition(
            task=task,
            asset_ids=list(asset_ids),
            dependencies=sorted(dependencies),
            estimated_risk=min(1.0, risk / count),
            estimated_utility=min(1.0, utility / count),
            warnings=warnings,
        )
