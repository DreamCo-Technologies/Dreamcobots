"""Portable manifests and compatibility checks for Buddy digital assets."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass(frozen=True)
class AssetManifest:
    asset_id: str
    name: str
    version: str
    asset_type: str
    capabilities: List[str] = field(default_factory=list)
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    runtime: Optional[str] = None
    license: Optional[str] = None
    provenance: List[str] = field(default_factory=list)
    integrity_hash: Optional[str] = None
    permissions: List[str] = field(default_factory=list)

    def compatible_with(self, required_inputs: List[str], required_outputs: List[str]) -> bool:
        return set(required_inputs).issubset(self.inputs) and set(required_outputs).issubset(self.outputs)

    def export(self) -> Dict[str, object]:
        return {
            "asset_id": self.asset_id, "name": self.name, "version": self.version,
            "asset_type": self.asset_type, "capabilities": self.capabilities,
            "inputs": self.inputs, "outputs": self.outputs,
            "dependencies": self.dependencies, "runtime": self.runtime,
            "license": self.license, "provenance": self.provenance,
            "integrity_hash": self.integrity_hash, "permissions": self.permissions,
        }
