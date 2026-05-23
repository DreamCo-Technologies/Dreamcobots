from __future__ import annotations

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


class LocalAssetStore:
    """Durable local object storage + in-memory registry with signed delivery URLs."""

    def __init__(self, root_dir: str | None = None, base_url: str | None = None, signing_secret: str | None = None) -> None:
        self.root_dir = Path(root_dir or os.getenv("DREAMCO_ARTIFACT_ROOT", "/tmp/dreamcobots_artifacts"))
        self.root_dir.mkdir(parents=True, exist_ok=True)
        self.base_url = base_url or os.getenv("DREAMCO_DELIVERY_BASE_URL", "https://media.dreamcobots.local/artifacts")
        self.signing_secret = (signing_secret or os.getenv("DREAMCO_SIGNING_SECRET", "dreamco-dev-signing-secret")).encode("utf-8")
        self.registry: dict[str, AssetRecord] = {}

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
        return record

    def get(self, asset_id: str) -> AssetRecord | None:
        return self.registry.get(asset_id)
