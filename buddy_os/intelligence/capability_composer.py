"""Compose compatible asset capabilities into a governed workflow descriptor."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

from buddy_os.assets.digital_asset_registry import DigitalAsset


@dataclass(frozen=True)
class CompositeCapability:
    capability_id: str
    name: str
    asset_ids: List[str]
    capabilities: List[str]
    dependencies: List[str]


class CapabilityComposer:
    def compose(self, capability_id: str, name: str, assets: Iterable[DigitalAsset]) -> CompositeCapability:
        selected = list(assets)
        if not selected:
            raise ValueError("at least one asset is required")
        capabilities: List[str] = []
        dependencies: List[str] = []
        for asset in selected:
            capabilities.extend(x for x in asset.capabilities if x not in capabilities)
            dependencies.extend(x for x in asset.dependencies if x not in dependencies)
        return CompositeCapability(capability_id, name, [a.asset_id for a in selected], capabilities, dependencies)
