from __future__ import annotations

from framework import GlobalAISourcesFlow  # noqa: F401

import hashlib
import hmac
import os
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any


def _utc_now() -> str:
    return datetime.utcnow().isoformat() + "Z"


@dataclass
class AssetRecord:
    asset_id: str
    owner: str
    lineage: list[str]
    originating_job: str
    provider: str
    media_format: str
    content_type: str
    bytes_size: int
    storage_path: str
    status: str
    created_at: str
    updated_at: str
    retention_days: int
    metadata: dict[str, Any] = field(default_factory=dict)
    delivery_url: str = ""
    expires_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "owner": self.owner,
            "lineage": self.lineage,
            "originating_job": self.originating_job,
            "provider": self.provider,
            "media_format": self.media_format,
            "content_type": self.content_type,
            "bytes_size": self.bytes_size,
            "storage_path": self.storage_path,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "retention_days": self.retention_days,
            "metadata": self.metadata,
            "delivery_url": self.delivery_url,
            "expires_at": self.expires_at,
        }


class AssetGraph:
    """Relationship-aware creative asset graph with lineage and provenance queries."""

    def __init__(self) -> None:
        self.nodes: dict[str, dict[str, Any]] = {}
        self.edges: list[dict[str, Any]] = []
        self.workflow_events: list[dict[str, Any]] = []

    def add_asset(self, asset: dict[str, Any]) -> None:
        asset_id = asset["asset_id"]
        node = dict(asset)
        node.setdefault("ownership", {"owner": asset.get("owner")})
        node.setdefault("provenance", {"originating_job": asset.get("originating_job"), "provider": asset.get("provider")})
        node.setdefault("usage", {"campaigns": [], "published_variants": []})
        node.setdefault("workflow_history", [])
        self.nodes[asset_id] = node
        self.workflow_events.append({"event": "asset_created", "asset_id": asset_id, "timestamp": _utc_now()})

    def add_relationship(
        self,
        *,
        source_asset_id: str,
        target_asset_id: str,
        relationship_type: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        edge = {
            "source_asset_id": source_asset_id,
            "target_asset_id": target_asset_id,
            "relationship_type": relationship_type,
            "metadata": metadata or {},
            "created_at": _utc_now(),
        }
        self.edges.append(edge)
        if target_asset_id in self.nodes:
            self.nodes[target_asset_id].setdefault("workflow_history", []).append(
                {"event": relationship_type, "source_asset_id": source_asset_id, "timestamp": edge["created_at"]}
            )

    def update_usage(self, asset_id: str, *, campaign_id: str | None = None, published_variant: str | None = None) -> None:
        node = self.nodes.get(asset_id)
        if not node:
            return
        usage = node.setdefault("usage", {"campaigns": [], "published_variants": []})
        if campaign_id and campaign_id not in usage["campaigns"]:
            usage["campaigns"].append(campaign_id)
        if published_variant and published_variant not in usage["published_variants"]:
            usage["published_variants"].append(published_variant)
        node.setdefault("workflow_history", []).append({"event": "usage_updated", "timestamp": _utc_now()})

    def get_ancestors(self, asset_id: str) -> list[str]:
        parents = [edge["source_asset_id"] for edge in self.edges if edge["target_asset_id"] == asset_id]
        ancestors: set[str] = set()
        stack = list(parents)
        while stack:
            current = stack.pop()
            if current in ancestors:
                continue
            ancestors.add(current)
            stack.extend([edge["source_asset_id"] for edge in self.edges if edge["target_asset_id"] == current])
        return list(ancestors)

    def get_descendants(self, asset_id: str) -> list[str]:
        children = [edge["target_asset_id"] for edge in self.edges if edge["source_asset_id"] == asset_id]
        descendants: set[str] = set()
        stack = list(children)
        while stack:
            current = stack.pop()
            if current in descendants:
                continue
            descendants.add(current)
            stack.extend([edge["target_asset_id"] for edge in self.edges if edge["source_asset_id"] == current])
        return list(descendants)

    def validate_consistency(self) -> dict[str, Any]:
        missing_nodes: list[dict[str, Any]] = []
        for edge in self.edges:
            if edge["source_asset_id"] not in self.nodes or edge["target_asset_id"] not in self.nodes:
                missing_nodes.append(edge)
        return {
            "valid": len(missing_nodes) == 0,
            "issues": missing_nodes,
            "node_count": len(self.nodes),
            "edge_count": len(self.edges),
        }

    def snapshot(self) -> dict[str, Any]:
        consistency = self.validate_consistency()
        return {
            "node_count": len(self.nodes),
            "edge_count": len(self.edges),
            "workflow_events": len(self.workflow_events),
            "consistency_valid": consistency["valid"],
            "consistency_issues": consistency["issues"],
        }


class LocalAssetStore:
    """Durable local object storage + in-memory registry with signed delivery URLs."""

    def __init__(self, root_dir: str | None = None, base_url: str | None = None, signing_secret: str | None = None) -> None:
        self.root_dir = Path(root_dir or os.getenv("DREAMCO_ARTIFACT_ROOT", "/tmp/dreamcobots_artifacts"))
        self.root_dir.mkdir(parents=True, exist_ok=True)
        self.base_url = base_url or os.getenv("DREAMCO_DELIVERY_BASE_URL", "https://media.dreamcobots.local/artifacts")
        self.signing_secret = (signing_secret or os.getenv("DREAMCO_SIGNING_SECRET", "dreamco-dev-signing-secret")).encode("utf-8")
        self.registry: dict[str, AssetRecord] = {}
        self.asset_graph = AssetGraph()

    def _sign(self, asset_id: str, expires_epoch: int) -> str:
        payload = f"{asset_id}:{expires_epoch}".encode("utf-8")
        return hmac.new(self.signing_secret, payload, hashlib.sha256).hexdigest()

    def persist(
        self,
        *,
        owner: str,
        originating_job: str,
        provider: str,
        media_format: str,
        content_type: str,
        content_bytes: bytes,
        metadata: dict[str, Any] | None = None,
        lineage: list[str] | None = None,
        retention_days: int = 30,
        ttl_seconds: int = 3600,
    ) -> AssetRecord:
        asset_id = f"asset_{uuid.uuid4().hex[:16]}"
        ext = media_format.lower().lstrip(".")
        path = self.root_dir / f"{asset_id}.{ext}"
        path.write_bytes(content_bytes)

        expires_epoch = int(time.time()) + ttl_seconds
        signature = self._sign(asset_id, expires_epoch)
        signed_url = f"{self.base_url}/{asset_id}.{ext}?exp={expires_epoch}&sig={signature}"

        now = _utc_now()
        record = AssetRecord(
            asset_id=asset_id,
            owner=owner,
            lineage=lineage or [],
            originating_job=originating_job,
            provider=provider,
            media_format=ext,
            content_type=content_type,
            bytes_size=len(content_bytes),
            storage_path=str(path),
            status="active",
            created_at=now,
            updated_at=now,
            retention_days=retention_days,
            metadata=metadata or {},
            delivery_url=signed_url,
            expires_at=(datetime.utcnow() + timedelta(seconds=ttl_seconds)).isoformat() + "Z",
        )
        self.registry[asset_id] = record
        self.asset_graph.add_asset(record.to_dict())
        for source_asset_id in lineage or []:
            self.asset_graph.add_relationship(
                source_asset_id=source_asset_id,
                target_asset_id=asset_id,
                relationship_type="derivative",
                metadata={"originating_job": originating_job},
            )
        self.asset_graph.workflow_events.append(
            {
                "event": "asset_persisted",
                "asset_id": asset_id,
                "owner": owner,
                "originating_job": originating_job,
                "timestamp": _utc_now(),
            }
        )
        return record

    def get(self, asset_id: str) -> AssetRecord | None:
        return self.registry.get(asset_id)

    def graph_snapshot(self) -> dict[str, Any]:
        return self.asset_graph.snapshot()

    def graph_context(self, asset_id: str) -> dict[str, Any]:
        node = self.asset_graph.nodes.get(asset_id, {})
        return {
            "asset_id": asset_id,
            "asset": node,
            "ancestors": self.asset_graph.get_ancestors(asset_id),
            "descendants": self.asset_graph.get_descendants(asset_id),
        }
