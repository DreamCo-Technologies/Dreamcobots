"""Governed digital-asset registry for Buddy.

Assets are first-class objects: discoverable, versioned, attributable and
connected to capabilities. Secret material is represented only by references.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
from typing import Dict, Iterable, List, Optional


ASSET_TYPES = (
    "agent", "bot", "skill", "tool", "api", "connector", "model", "dataset",
    "prompt", "workflow", "code", "repository", "document", "knowledge",
    "template", "schema", "configuration", "infrastructure", "benchmark",
    "experiment", "policy", "media", "image", "audio", "video", "font",
    "package", "container", "plugin", "report", "dashboard", "secret_reference",
)


@dataclass
class DigitalAsset:
    asset_id: str
    name: str
    asset_type: str
    description: str = ""
    version: str = "0.1.0"
    source_uri: Optional[str] = None
    content_hash: Optional[str] = None
    owner: Optional[str] = None
    license: Optional[str] = None
    provenance: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    capabilities: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    lifecycle: str = "discovered"
    utility_score: float = 0.0
    trust_score: float = 0.0
    risk_score: float = 0.0
    secret_ref_only: bool = False
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class DigitalAssetRegistry:
    """In-memory registry suitable for tests and as a persistence adapter contract."""

    def __init__(self) -> None:
        self._assets: Dict[str, DigitalAsset] = {}

    @staticmethod
    def fingerprint(content: bytes) -> str:
        return "sha256:" + sha256(content).hexdigest()

    def register(self, asset: DigitalAsset) -> DigitalAsset:
        if asset.asset_type not in ASSET_TYPES:
            raise ValueError(f"unsupported asset type: {asset.asset_type}")
        if asset.secret_ref_only and asset.asset_type != "secret_reference":
            raise ValueError("secret_ref_only assets must use secret_reference type")
        self._assets[asset.asset_id] = asset
        return asset

    def get(self, asset_id: str) -> Optional[DigitalAsset]:
        return self._assets.get(asset_id)

    def search(self, query: str = "", asset_type: Optional[str] = None, tag: Optional[str] = None) -> List[DigitalAsset]:
        needle = query.lower().strip()
        result = []
        for asset in self._assets.values():
            haystack = " ".join([asset.name, asset.description, *asset.tags, *asset.capabilities]).lower()
            if needle and needle not in haystack:
                continue
            if asset_type and asset.asset_type != asset_type:
                continue
            if tag and tag not in asset.tags:
                continue
            result.append(asset)
        return sorted(result, key=lambda item: (-item.utility_score, item.name))

    def capability_assets(self, capability: str) -> List[DigitalAsset]:
        return self.search(asset_type=None, query=capability)

    def manifest(self) -> List[dict]:
        return [asdict(asset) for asset in sorted(self._assets.values(), key=lambda item: item.asset_id)]

    def dependencies_of(self, asset_id: str) -> Iterable[DigitalAsset]:
        asset = self.get(asset_id)
        if not asset:
            return ()
        return tuple(self._assets[dep] for dep in asset.dependencies if dep in self._assets)
