"""PostgreSQL metadata adapter for per-division dataset catalogs.

This adapter stores manifests only; dataset bytes remain in the existing
content-addressed object store until a separately approved object-store adapter
is configured. It never creates schemas/tables or applies migrations.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime, timezone
from typing import Any, Callable

SCHEMA_PATTERN = re.compile(r"^dreamco_division_([0-9]{3})$")
HASH_PATTERN = re.compile(r"^[0-9a-f]{64}$")


class PostgresCatalogError(RuntimeError):
    """A PostgreSQL catalog operation could not be safely completed."""


def division_schema(masterbot_id: int) -> str:
    if isinstance(masterbot_id, bool) or not isinstance(masterbot_id, int) or not 1 <= masterbot_id <= 65:
        raise PostgresCatalogError("masterbot_id must be a canonical integer from 1 through 65")
    return f"dreamco_division_{masterbot_id:03d}"


def _validate_manifest(manifest: dict[str, Any], masterbot_id: int) -> dict[str, Any]:
    if not isinstance(manifest, dict):
        raise PostgresCatalogError("dataset manifest must be an object")
    required = ("dataset_id", "version", "name", "owner", "license", "license_url",
                "source_url", "data_plane", "rights_status")
    if any(not str(manifest.get(key, "")).strip() for key in required):
        raise PostgresCatalogError("dataset manifest is missing required identity or rights fields")
    if not re.fullmatch(r"[A-Za-z0-9._-]{3,100}", str(manifest["dataset_id"])):
        raise PostgresCatalogError("dataset_id contains unsupported characters")
    if isinstance(manifest["version"], bool) or not isinstance(manifest["version"], int) or manifest["version"] < 1:
        raise PostgresCatalogError("dataset version must be a positive integer")
    if manifest.get("primary_masterbot_id") not in (None, masterbot_id):
        raise PostgresCatalogError("dataset primary owner does not match target division")
    digest = manifest.get("content_sha256")
    if digest is not None and not HASH_PATTERN.fullmatch(str(digest)):
        raise PostgresCatalogError("content_sha256 must be a lowercase SHA-256 digest")
    if manifest.get("holdout") and manifest.get("data_plane") != "evaluation_only_holdout":
        raise PostgresCatalogError("holdout datasets must use the evaluation-only data plane")
    if manifest.get("training_approved") is True:
        if manifest.get("rights_status") != "VERIFIED":
            raise PostgresCatalogError("training-approved manifests require verified rights")
        if manifest.get("data_plane") not in {"dreamco_owned_training", "licensed_training", "user_contributed_opt_in_training"}:
            raise PostgresCatalogError("training-approved manifest uses a non-training data plane")
        if not str(manifest.get("rights_evidence", "")).strip():
            raise PostgresCatalogError("training-approved manifests require a rights evidence reference")
    return {key: value for key, value in manifest.items()
            if key not in {"content", "raw_data", "token", "authorization", "password", "dsn"}}


class PostgresDatasetCatalog:
    """Persist dataset manifest metadata in one isolated MasterBot schema.

    The required table is installed by a separately reviewed migration.
    No DDL is issued by this adapter.
    """

    def __init__(self, dsn: str | None = None, connect: Callable[..., Any] | None = None):
        self.dsn = dsn or os.environ.get("DREAMCO_POSTGRES_DSN") or os.environ.get("DATABASE_URL")
        if not self.dsn:
            raise PostgresCatalogError("DREAMCO_POSTGRES_DSN or DATABASE_URL is required")
        if connect is None:
            try:
                import psycopg
            except ImportError as exc:
                raise PostgresCatalogError("Install psycopg to use the PostgreSQL catalog") from exc
            connect = psycopg.connect
        self._connect = connect

    def register(self, masterbot_id: int, manifest: dict[str, Any]) -> dict[str, Any]:
        schema = division_schema(masterbot_id)
        safe = _validate_manifest(manifest, masterbot_id)
        serialized = json.dumps(safe, sort_keys=True, ensure_ascii=False)
        manifest_hash = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        created_at = str(safe.get("created_at") or datetime.now(timezone.utc).isoformat())
        sql = f'''INSERT INTO "{schema}".dataset_catalog
            (dataset_id, version, masterbot_id, manifest, manifest_sha256, content_sha256, created_at)
            VALUES (%s, %s, %s, %s::jsonb, %s, %s, %s)
            ON CONFLICT (dataset_id, version) DO UPDATE SET
              manifest = EXCLUDED.manifest,
              manifest_sha256 = EXCLUDED.manifest_sha256,
              content_sha256 = EXCLUDED.content_sha256
            WHERE "{schema}".dataset_catalog.manifest_sha256 = EXCLUDED.manifest_sha256
            RETURNING dataset_id, version, manifest_sha256'''
        try:
            with self._connect(self.dsn, connect_timeout=5) as connection:
                with connection.cursor() as cursor:
                    cursor.execute(sql, (safe["dataset_id"], safe["version"], masterbot_id,
                                         serialized, manifest_hash, safe.get("content_sha256"), created_at))
                    row = cursor.fetchone()
                    if row is None:
                        raise PostgresCatalogError("immutable dataset version conflict: existing manifest hash differs")
        except PostgresCatalogError:
            raise
        except Exception as exc:
            # Database exceptions can contain connection strings or sensitive SQL values.
            raise PostgresCatalogError(f"PostgreSQL dataset catalog write failed ({type(exc).__name__})") from exc
        return {"status": "PERSISTED", "masterbot_id": masterbot_id, "schema": schema,
                "dataset_id": str(row[0]), "version": int(row[1]), "manifest_sha256": str(row[2]),
                "credentials_emitted": False}

    def get(self, masterbot_id: int, dataset_id: str, version: int) -> dict[str, Any] | None:
        schema = division_schema(masterbot_id)
        if not re.fullmatch(r"[A-Za-z0-9._-]{3,100}", str(dataset_id)):
            raise PostgresCatalogError("invalid dataset_id")
        if isinstance(version, bool) or not isinstance(version, int) or version < 1:
            raise PostgresCatalogError("version must be a positive integer")
        try:
            with self._connect(self.dsn, connect_timeout=5) as connection:
                with connection.cursor() as cursor:
                    cursor.execute(f'''SELECT manifest, manifest_sha256 FROM "{schema}".dataset_catalog
                        WHERE dataset_id = %s AND version = %s''', (dataset_id, version))
                    row = cursor.fetchone()
        except Exception as exc:
            raise PostgresCatalogError(f"PostgreSQL dataset catalog read failed ({type(exc).__name__})") from exc
        if row is None:
            return None
        payload = row[0] if isinstance(row[0], dict) else json.loads(row[0])
        digest = hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
        if digest != row[1]:
            raise PostgresCatalogError("stored dataset manifest hash verification failed")
        return payload
